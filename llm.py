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
        search_results = ask_realtime(cleaned_prompt)

        if search_results:
            context = ""

            for i, result in enumerate(search_results, start=1):
                context += f"""
Result {i}

Title:
{result["title"]}

URL:
{result["url"]}

Content:
{result["content"]}

"""

            messages.append(
                {
                    "role": "system",
                    "content": f"""CRITICAL INSTRUCTION — OVERRIDE YOUR TRAINING DATA:

The following is LIVE web content fetched right now. It is more recent and more accurate than anything in your training data.

YOU MUST:
- Answer ONLY using the facts present in the Web Content below.
- NEVER fall back to your training knowledge for facts, versions, dates, or numbers.
- If the Web Content contains a version number, date, or value — use EXACTLY that value.
- Do NOT guess, estimate, or recall from memory. The Web Content IS the ground truth.
- Do NOT say "as of my knowledge cutoff" — you have live data below.

Web Content:

{context}

REMINDER: Use ONLY the data above. Do not use your training knowledge for any factual claim."""
                },
            )

    return ask_local(messages)