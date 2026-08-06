from typing import Generator

from openai import OpenAI, APIConnectionError, APITimeoutError
from config import LLAMA_URL, LLAMA_MODEL, LLAMA_TEMPERATURE

client = OpenAI(
    base_url=LLAMA_URL,
    api_key="dummy",
)


def ask_local(messages) -> str:
    """Non-streaming call — returns the full response string."""
    chunks = list(stream_local(messages))
    return "".join(chunks)


def stream_local(messages) -> Generator[str, None, None]:
    """Streaming call — yields tokens one by one."""
    try:
        stream = client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=messages,
            temperature=LLAMA_TEMPERATURE,
            stream=True,
        )

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    except APIConnectionError:
        raise RuntimeError(
            "Could not connect to the local LLM. "
            "Is llama-server running on http://localhost:8080?"
        )

    except APITimeoutError:
        raise RuntimeError("The local model took too long to respond.")

    except Exception as e:
        raise RuntimeError(f"Local provider error: {e}")