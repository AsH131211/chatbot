from openai import OpenAI
from openai import APIConnectionError, APITimeoutError
from config import LLAMA_URL, LLAMA_MODEL, LLAMA_TEMPERATURE

client = OpenAI(
    base_url=LLAMA_URL,
    api_key="dummy",
)


def ask_local(messages):
    try:
        stream = client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=messages,
            temperature=LLAMA_TEMPERATURE,
            stream=True,
        )

        full_response = ""

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta.content

            if delta:
                print(delta, end="", flush=True)
                full_response += delta

        print()

        return full_response

    except APIConnectionError:
        raise RuntimeError(
            "Could not connect to the local LLM. "
            "Is llama-server running on http://localhost:8080?"
        )

    except APITimeoutError:
        raise RuntimeError(
            "The local model took too long to respond."
        )

    except Exception as e:
        raise RuntimeError(f"Local provider error: {e}")