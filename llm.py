from providers import ask_groq, ask_gemini
from groq import RateLimitError


def chat(messages):
    try:
        return ask_groq(messages)

    except RateLimitError:
        return ask_gemini(messages)