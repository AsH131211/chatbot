from groq import Groq, RateLimitError
from google import genai
from config import *

groq_client = Groq(api_key=GROQ_API)
gemini_client = genai.Client(api_key=GEMINI_API)


def ask_groq(messages):

    try:
        response = groq_client.chat.completions.create(
            model=MODEL1,
            messages=messages,
            temperature=TEMPERATURE,
            max_completion_tokens=MAX_TOKENS,
        )

        return response.choices[0].message.content

    except RateLimitError:
        raise

    except Exception as e:
        raise e


def ask_gemini(messages):

    prompt = ""

    for msg in messages:
        prompt += f"{msg['role']}: {msg['content']}\n"

    response = gemini_client.models.generate_content(
        model=MODEL2,
        contents=prompt,
    )

    return response.text



def ask_llm(messages):
    try:
        return ask_groq(messages)

    except RateLimitError:
        print("\n[Groq rate limit reached. Switching to Gemini...]\n")
        return ask_gemini(messages)