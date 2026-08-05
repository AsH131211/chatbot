from router import choose_provider, Provider
from providers.local import ask_local
from providers.realtime import ask_realtime


def chat(messages):
    last_user = next(
        msg for msg in reversed(messages)
        if msg["role"] == "user"
    )

    provider, cleaned_prompt = choose_provider(last_user["content"])

    messages = messages.copy()

    for i in range(len(messages) - 1, -1, -1):
        if messages[i]["role"] == "user":
            messages[i] = {
                **messages[i],
                "content": cleaned_prompt,
            }
            break

    if provider == Provider.REALTIME:
        return ask_realtime(messages)

    try:
        return ask_local(messages)

    except RuntimeError as e:
        print(f"\n⚠️ {e}")
        print("⚠️ Falling back to realtime provider...\n")

        return ask_realtime(messages)