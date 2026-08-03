from providers import ask_gemini, ask_gemini_fallback
from google.api_core.exceptions import ResourceExhausted


def chat(messages):
    try:
        return ask_gemini(messages)

    except ResourceExhausted:
        print("\n[Rate limit reached on 3.6 flash — switching to fallback 3.5 flash lite...]")
        return ask_gemini_fallback(messages)
