import threading
from typing import Generator

from context import build_context
from storage import load_chat, save_chat
from memory import load_memory, save_memory, extract_memory


class Assistant:
    def __init__(self):
        self.conversation = load_chat()
        self.memory = load_memory()
        # Serialise background commits so they don't interleave.
        self._commit_lock = threading.Lock()

    # ------------------------------------------------------------------ #
    #  Non-streaming (kept for compatibility / fallback)                  #
    # ------------------------------------------------------------------ #
    def ask(self, prompt: str) -> str:
        self.conversation.append({"role": "user", "content": prompt})
        chat_context = build_context(self.memory, self.conversation)
        from llm import chat
        reply = chat(chat_context)
        self._commit_async(reply)
        return reply

    # ------------------------------------------------------------------ #
    #  Streaming — yields tokens, commits when done                       #
    # ------------------------------------------------------------------ #
    def stream(self, prompt: str) -> Generator[str, None, None]:
        self.conversation.append({"role": "user", "content": prompt})
        chat_context = build_context(self.memory, self.conversation)

        from llm import stream_chat
        buf: list[str] = []
        for token in stream_chat(chat_context):
            buf.append(token)
            yield token

        # Fire-and-forget: persist conversation + update memory without
        # blocking the next user prompt.
        full_reply = "".join(buf)
        self._commit_async(full_reply)

    # ------------------------------------------------------------------ #
    #  Internal                                                           #
    # ------------------------------------------------------------------ #
    def _commit_async(self, reply: str):
        """Persist and update memory on a daemon thread."""
        t = threading.Thread(
            target=self._commit, args=(reply,), daemon=True
        )
        t.start()

    def _commit(self, reply: str):
        with self._commit_lock:
            self.conversation.append({"role": "assistant", "content": reply})
            save_chat(self.conversation)

            try:
                self.memory = extract_memory(self.memory, self.conversation)
                save_memory(self.memory)
            except Exception:
                pass
