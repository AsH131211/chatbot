from groq import Groq
from config import *

client = Groq(api_key=API_KEY)

messages = [
    {
        "role": "system",
        "content": "You are Jarvis, a helpful AI assistant."
    }
]

print("Jarvis is online.")
print("Type /exit to quit.\n")

while True:

    prompt = input("> ").strip()

    
    if prompt.casefold() == "/exit":
        print("Shutting down...")
        break

   
    if not prompt:
        continue

   
    messages.append({
        "role": "user",
        "content": prompt
    })

    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_completion_tokens=MAX_TOKENS,
    )

    
    reply = response.choices[0].message.content

    print(f"\nJarvis: {reply}\n")

   
    messages.append({
        "role": "assistant",
        "content": reply
    })