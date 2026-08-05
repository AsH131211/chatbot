import sys
import threading
import itertools
import time

from openai import OpenAI, APIConnectionError, APITimeoutError
from config import LLAMA_URL, LLAMA_MODEL, LLAMA_TEMPERATURE

client = OpenAI(
    base_url=LLAMA_URL,
    api_key="dummy",
)


def _spinner(stop_event):
    frames = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    while not stop_event.is_set():
        sys.stderr.write(f"\r\033[2m{next(frames)} thinking...\033[0m")
        sys.stderr.flush()
        time.sleep(0.08)
    sys.stderr.write("\r\033[K")
    sys.stderr.flush()


def ask_local(messages):
    try:
        stop = threading.Event()
        spinner_thread = threading.Thread(target=_spinner, args=(stop,), daemon=True)
        spinner_thread.start()

        stream = client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=messages,
            temperature=LLAMA_TEMPERATURE,
            stream=True,
        )

        full_response = ""
        first_token = True
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                if first_token:
                    # Kill spinner as soon as first token arrives
                    stop.set()
                    spinner_thread.join()
                    first_token = False
                sys.stdout.write(delta)
                sys.stdout.flush()
                full_response += delta

        # Ensure spinner is stopped even if no tokens came
        if not stop.is_set():
            stop.set()
            spinner_thread.join()

        sys.stdout.write("\n")
        sys.stdout.flush()
        return full_response

    except APIConnectionError:
        raise RuntimeError(
            "Could not connect to the local LLM. "
            "Is llama-server running on http://localhost:8080?"
        )

    except APITimeoutError:
        raise RuntimeError("The local model took too long to respond.")

    except Exception as e:
        raise RuntimeError(f"Local provider error: {e}")