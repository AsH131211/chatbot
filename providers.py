from groq import Groq, RateLimitError
from google import genai
from config import *

groq_client = Groq(api_key=GROQ_API,max_retries=0)
gemini_client = genai.Client(api_key=GEMINI_API)


def ask_groq(messages):

    try:
        response = groq_client.chat.completions.create(
            model=MODEL1,
            messages=messages,
            temperature=TEMPERATURE,
            max_completion_tokens=MAX_TOKENS,
            stream = True,
        )

        reply = ""

        for chunk in response:
            piece = chunk.choices[0].delta.content

            if piece:
                reply += piece
                print(piece, end="", flush=True)

        print()

        return reply


        
    except RateLimitError:
        raise



def ask_gemini(messages):

    prompt = ""

    for msg in messages:
        prompt += f"{msg['role']}: {msg['content']}\n"

    response = gemini_client.models.generate_content_stream(
        model=MODEL2,
        contents=prompt,
    )

    reply = ""

    for chunk in response:
         if chunk.text:
            reply += chunk.text
            print(chunk.text, end="", flush=True)


    print()

    return reply


def ask_llm(messages):
    try:
        return ask_groq(messages)

    except RateLimitError:
        return ask_gemini(messages)