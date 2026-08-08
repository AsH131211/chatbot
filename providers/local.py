from __future__ import annotations

import json
from typing import Generator

import requests

from config import LLAMA_URL, LLAMA_MODEL, LLAMA_TEMPERATURE


def stream_local(messages) -> Generator[str, None, None]:
    """Streaming call — yields tokens one by one, with minimal latency."""
    url = LLAMA_URL.rstrip("/") + "/chat/completions"
    payload = {
        "model":       LLAMA_MODEL,
        "messages":    messages,
        "temperature": LLAMA_TEMPERATURE,
        "stream":      True,
    }

    try:
        with requests.post(
            url,
            json=payload,
            headers={"Accept": "text/event-stream"},
            stream=True,
            timeout=(10, 120),   # (connect timeout, read timeout)
        ) as resp:
            resp.raise_for_status()

            for raw_line in resp.iter_lines(chunk_size=None):
                # iter_lines() yields bytes; decode to str.
                if isinstance(raw_line, bytes):
                    line = raw_line.decode("utf-8", errors="replace")
                else:
                    line = raw_line

                if not line.startswith("data:"):
                    continue

                data = line[5:].strip()
                if data == "[DONE]":
                    break

                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue

                choices = chunk.get("choices")
                if not choices:
                    continue

                delta = choices[0].get("delta", {}).get("content")
                if delta:
                    yield delta

    except requests.ConnectionError:
        raise RuntimeError(
            "Could not connect to the local LLM. "
            "Is llama-server running on http://localhost:8080?"
        )
    except requests.Timeout:
        raise RuntimeError("The local model took too long to respond.")
    except Exception as e:
        raise RuntimeError(f"Local provider error: {e}")


def ask_local(messages) -> str:
    """Non-streaming — returns the full response string."""
    return "".join(stream_local(messages))
