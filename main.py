from providers import ask_llm

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

    try:
        reply = ask_llm(messages)

        print(f"\nJarvis: {reply}\n")

        messages.append({
            "role": "assistant",
            "content": reply
        })

    except Exception as e:
        print(f"Error: {e}")

        messages.pop()