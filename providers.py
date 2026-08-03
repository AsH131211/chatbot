from google import genai
from google.api_core.exceptions import ResourceExhausted
from config import *

gemini_client = genai.Client(api_key=GEMINI_API)


def _stream_gemini(model, messages):
    
    prompt = ""
    for msg in messages:
        prompt += f"{msg['role']}: {msg['content']}\n"

    response = gemini_client.models.generate_content_stream(
        model=model,
        contents=prompt,
    )

    reply = ""
    for chunk in response:
        if chunk.text:
            reply += chunk.text
            print(chunk.text, end="", flush=True)

    print()
    return reply


def ask_gemini(messages):
    
    return _stream_gemini(MODEL2, messages)


def ask_gemini_fallback(messages):
    
    return _stream_gemini(MODEL1, messages)
