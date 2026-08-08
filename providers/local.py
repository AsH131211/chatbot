from __future__ import annotations

import json
from typing import Generator

import requests

from config import LLAMA_URL, LLAMA_MODEL, LLAMA_TEMPERATURE


def stream_local(messages) -> Generator[str, None, None]:
    url = LLAMA_URL.rstrip("/") + "/chat/completions"
    payload = {
        "model": LLAMA_MODEL,
        "messages": messages,
        "temperature": LLAMA_TEMPERATURE,
        "stream": True,
    }

    try:
        with requests.post(
            url,
            json=payload,
            headers={"Accept": "text/event-stream"},
            stream=True,
            timeout=(10, 120),
        ) as resp:
            resp.raise_for_status()

            for raw in resp.iter_lines(chunk_size=None):
                line = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw

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
        raise RuntimeError("Could not connect to llama-server on http://localhost:8080.")
    except requests.Timeout:
        raise RuntimeError("Local model timed out.")
    except Exception as e:
        raise RuntimeError(f"Local provider error: {e}")


def ask_local(messages) -> str:
    return "".join(stream_local(messages))
