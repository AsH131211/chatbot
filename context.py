def build_context(memory, messages):
    facts = memory["facts"]

    context = [
        {
            "role": "system",
            "content": "You are Jarvis. just like in ironman.."
        }
    ]

    if facts:
        memory_text = "Known facts about the user:\n\n"
        for fact in facts:
            memory_text += f"- {fact}\n" 

        context.append({
            "role":"system",
            "content" : memory_text
        })

    context.extend(messages[-20:])
    return context 