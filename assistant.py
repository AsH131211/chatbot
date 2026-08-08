import threading
from typing import Generator

from voice import preload, speak, wait as voice_wait
from context import build_context
from storage import load_chat, save_chat
from memory import load_memory, save_memory, extract_memory


class Assistant:
    def __init__(self):
        self.conversation = load_chat()
        self.memory = load_memory()
        self._commit_lock = threading.Lock()
        preload()

    def ask(self, prompt: str) -> str:
        self.conversation.append({"role": "user", "content": prompt})
        from llm import chat
        reply = chat(build_context(self.memory, self.conversation))
        speak(reply)
        self._commit_async(reply)
        voice_wait()
        return reply

    def stream(self, prompt: str) -> Generator[str, None, None]:
        self.conversation.append({"role": "user", "content": prompt})
        from llm import stream_chat

        buf: list[str] = []
        sentence: str = ""

        for token in stream_chat(build_context(self.memory, self.conversation)):
            buf.append(token)
            sentence += token
            yield token
            stripped = sentence.rstrip()
            if stripped and stripped[-1] in ".!?":
                speak(stripped)
                sentence = ""

        if sentence.strip():
            speak(sentence.strip())

        self._commit_async("".join(buf))
        voice_wait()

    def _commit_async(self, reply: str) -> None:
        threading.Thread(target=self._commit, args=(reply,), daemon=True).start()

    def _commit(self, reply: str) -> None:
        with self._commit_lock:
            self.conversation.append({"role": "assistant", "content": reply})
            save_chat(self.conversation)
            try:
                self.memory = extract_memory(self.memory, self.conversation)
                save_memory(self.memory)
            except Exception:
                pass
