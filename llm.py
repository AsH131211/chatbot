from typing import Generator

from router import choose_provider, Provider
from providers.local import ask_local, stream_local
from providers.realtime import ask_realtime


def _build_messages(messages, cleaned_prompt):
    messages = messages.copy()
    for i in range(len(messages) - 1, -1, -1):
        if messages[i]["role"] == "user":
            messages[i] = {**messages[i], "content": cleaned_prompt}
            break
    return messages


def _location_from_messages(messages) -> str:
    keywords = ("located in", "lives in", "from", "city", "town", "district", "state", "country", "region")
    for msg in messages:
        if msg.get("role") != "system":
            continue
        content = msg.get("content", "")
        if "known facts" not in content.lower():
            continue
        for line in content.splitlines():
            if any(kw in line.lower() for kw in keywords):
                return line.strip().lstrip("- ")
    return ""


def _inject_search_context(messages, cleaned_prompt):
    location = _location_from_messages(messages)
    query = f"{cleaned_prompt} {location}".strip() if location else cleaned_prompt

    results = ask_realtime(query)
    if not results:
        return messages

    context = "".join(
        f"\nResult {i}\n\nTitle:\n{r['title']}\n\nURL:\n{r['url']}\n\nContent:\n{r['content']}\n\n"
        for i, r in enumerate(results, 1)
    )

    messages.append({
        "role": "system",
        "content": (
            "CRITICAL INSTRUCTION — OVERRIDE YOUR TRAINING DATA:\n\n"
            "The following is LIVE web content fetched right now. It is more recent and more accurate than anything in your training data.\n\n"
            "YOU MUST:\n"
            "- Answer ONLY using the facts present in the Web Content below.\n"
            "- NEVER fall back to your training knowledge for facts, versions, dates, or numbers.\n"
            "- If the Web Content contains a version number, date, or value — use EXACTLY that value.\n"
            "- Do NOT guess, estimate, or recall from memory. The Web Content IS the ground truth.\n"
            "- Do NOT say \"as of my knowledge cutoff\" — you have live data below.\n\n"
            f"Web Content:\n\n{context}\n\n"
            "REMINDER: Use ONLY the data above. Do not use your training knowledge for any factual claim."
        ),
    })
    return messages


def _prepare(messages) -> tuple[list, Provider]:
    last_user = next(msg for msg in reversed(messages) if msg["role"] == "user")
    provider, cleaned_prompt = choose_provider(last_user["content"])
    messages = _build_messages(messages, cleaned_prompt)
    if provider == Provider.REALTIME:
        messages = _inject_search_context(messages, cleaned_prompt)
    return messages, provider


def chat(messages) -> str:
    messages, _ = _prepare(messages)
    return ask_local(messages)


def stream_chat(messages) -> Generator[str, None, None]:
    messages, _ = _prepare(messages)
    yield from stream_local(messages)