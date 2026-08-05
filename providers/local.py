from openai import OpenAI
from openai import APIConnectionError, APITimeoutError
from config import LLAMA_URL, LLAMA_MODEL, LLAMA_TEMPERATURE

client = OpenAI(
    base_url=LLAMA_URL,
    api_key="dummy",
)


def ask_local(messages):
    try:
        response = client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=messages,
            temperature=LLAMA_TEMPERATURE,
        )

        return response.choices[0].message.content

    except APIConnectionError:
        raise RuntimeError(
            "Could not connect to the local LLM. "
            "Is llama-server running on http://localhost:8080 ?"
        )

    except APITimeoutError:
        raise RuntimeError(
            "The local model took too long to respond."
        )

    except Exception as e:
        raise RuntimeError(f"Local provider error: {e}")