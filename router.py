from enum import Enum


class Provider(Enum):
    LOCAL = "local"
    REALTIME = "realtime"


def choose_provider(prompt: str) -> tuple[Provider, str]:
    prompt = prompt.strip()
    if prompt.startswith("/rt "):
        return Provider.REALTIME, prompt[4:].strip()
    return Provider.LOCAL, prompt