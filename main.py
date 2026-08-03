from groq import Groq
from config import *

client = Groq(api_key=API_KEY)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": "Hello!"
        }
    ],
    temperature=TEMPERATURE,
    max_completion_tokens=MAX_TOKENS,
)

print(response.choices[0].message.content)
