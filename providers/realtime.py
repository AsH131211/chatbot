from google import genai
from config import (GEMINI_API, RT_MODEL,)
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


def ask_realtime(messages):
    try:
            return _stream_gemini(RTMODEL, messages)

    except Exception as e:
        raise RuntimeError(
            f"Realtime provider error: {e}"
        )
    


