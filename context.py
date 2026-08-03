def build_context(messages):

    context = [
        {
            "role": "system",
            "content": "You are Jarvis, a helpful AI assistant like the jarvis in ironman."
        }
    ]

    context.extend(messages[-20:])

    return context