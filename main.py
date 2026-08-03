from groq import Groq
from config import *

client = Groq(api_key=API_KEY)

messages=[
        {
            "role": "system",
            "content": "You are an AI assistant Jarvis."
        }
    ]  

while(True):

    prompt = input("> ")

    if prompt.lower() == "exit":
        print("shutting down...\n")
        break

    messages.append({
        "role": "user",
        "content": prompt
    })


    response = client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            max_completion_tokens=MAX_TOKENS,
            messages=messages)

    reply = response.choices[0].message.content


    print(reply)

    messages.append({
        "role": "assistant",
        "content": reply
    })


