from llm import chat
from context import build_context

messages = []

print("🤖 Jarvis is online.")
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

    try:
        print("Jarvis: ", end="", flush=True)

        chat_context = build_context(messages)

        reply = chat(chat_context)

        messages.append({
            "role": "assistant",
            "content": reply
        })

    except Exception as e:
        print(f"\nError: {e}")

        messages.pop()