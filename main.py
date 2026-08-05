from llm import chat
from context import build_context
from storage import load_chat, save_chat
from memory import load_memory, save_memory, extract_memory


conversation = load_chat()
memory = load_memory()

print(" Jarvis is online.")
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

        chat_context = build_context(memory, conversation)
        reply = chat(chat_context)

        conversation.append({
            "role": "assistant",
            "content": reply
        })

        save_chat(conversation)

        try:
            memory = extract_memory(memory, conversation)
            save_memory(memory)

        except Exception as e:
            print(f"\n⚠ Memory update failed: {e}")

    except KeyboardInterrupt:
        print("\nShutting down...")
        break

    except Exception as e:
        print(f"\n❌ {e}")

        if conversation and conversation[-1]["role"] == "user":
            conversation.pop()