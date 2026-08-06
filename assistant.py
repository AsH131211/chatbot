from typing import Generator

from context import build_context
from storage import load_chat, save_chat
from memory import load_memory, save_memory, extract_memory
from llm import chat, stream_chat


class Assistant:
    def __init__(self):
        self.conversation = load_chat()
        self.memory = load_memory()

    # ------------------------------------------------------------------ #
    #  Non-streaming (kept for compatibility / fallback)                  #
    # ------------------------------------------------------------------ #
    def ask(self, prompt: str) -> str:
        self.conversation.append({"role": "user", "content": prompt})
        chat_context = build_context(self.memory, self.conversation)
        reply = chat(chat_context)
        self._commit(reply)
        return reply

    # ------------------------------------------------------------------ #
    #  Streaming — yields tokens, commits when done                       #
    # ------------------------------------------------------------------ #
    def stream(self, prompt: str) -> Generator[str, None, None]:
        self.conversation.append({"role": "user", "content": prompt})
        chat_context = build_context(self.memory, self.conversation)

        full_reply = ""
        for token in stream_chat(chat_context):
            full_reply += token
            yield token

        self._commit(full_reply)

    # ------------------------------------------------------------------ #
    #  Internal                                                           #
    # ------------------------------------------------------------------ #
    def _commit(self, reply: str):
        """Persist conversation and update memory."""
        self.conversation.append({"role": "assistant", "content": reply})
        save_chat(self.conversation)

        try:
            self.memory = extract_memory(self.memory, self.conversation)
            save_memory(self.memory)
        except Exception:
            pass