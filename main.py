from llm import chat
from context import build_context
from storage import load_chat , save_chat


conversation = load_chat()

print("🤖 Jarvis is online.")
print("Type /exit to quit.\n")

while True:

    prompt = input("> ").strip()

    if prompt.casefold() == "/exit":
        print("Shutting down...")
        break

    if not prompt:
        continue

    conversation.append({
        "role": "user",
        "content": prompt
    })

    

    try:
        print("Jarvis: ", end="", flush=True)

        chat_context = build_context(conversation)

        reply = chat(chat_context)

        conversation.append({
            "role": "assistant",
            "content": reply
        })

        save_chat(conversation)

    except Exception as e:
        print(f"\nError: {e}")

        conversation.pop()