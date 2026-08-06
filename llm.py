from typing import Generator

from router import choose_provider, Provider
from providers.local import ask_local, stream_local
from providers.realtime import ask_realtime


def _build_messages(messages, cleaned_prompt):
    """Inject the cleaned prompt into the last user message."""
    messages = messages.copy()
    for i in range(len(messages) - 1, -1, -1):
        if messages[i]["role"] == "user":
            messages[i] = {**messages[i], "content": cleaned_prompt}
            break
    return messages


def _location_from_messages(messages) -> str:
    """
    Scan memory system messages for a location fact and return it as a
    short string (e.g. "Wayanad, Kerala, India") to append to search queries.
    Returns an empty string if nothing useful is found.
    """
    location_keywords = (
        "located in", "lives in", "from", "city", "town",
        "district", "state", "country", "region",
    )
    for msg in messages:
        if msg.get("role") != "system":
            continue
        content = msg.get("content", "")
        # Only look in the facts block written by memory.py
        if "known facts" not in content.lower():
            continue
        for line in content.splitlines():
            lower = line.lower()
            if any(kw in lower for kw in location_keywords):
                return line.strip().lstrip("- ")
    return ""


def _inject_search_context(messages, cleaned_prompt):
    """Run a realtime search and append results as a system message."""
    # Enhance the query with the user's known location (from memory) so that
    # searches like "weather now" return local rather than US results.
    location = _location_from_messages(messages)
    search_query = f"{cleaned_prompt} {location}".strip() if location else cleaned_prompt

    search_results = ask_realtime(search_query)
    if not search_results:
        return messages

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

REMINDER: Use ONLY the data above. Do not use your training knowledge for any factual claim.""",
        }
    )
    return messages


def _prepare(messages) -> tuple[list, Provider]:
    """Resolve provider, clean prompt, optionally inject search context."""
    last_user = next(
        msg for msg in reversed(messages) if msg["role"] == "user"
    )
    provider, cleaned_prompt = choose_provider(last_user["content"])
    messages = _build_messages(messages, cleaned_prompt)

    if provider == Provider.REALTIME:
        messages = _inject_search_context(messages, cleaned_prompt)

    return messages, provider


def chat(messages) -> str:
    """Non-streaming: return the full reply string."""
    messages, _ = _prepare(messages)
    return ask_local(messages)


def stream_chat(messages) -> Generator[str, None, None]:
    """Streaming: yield tokens as they arrive from the model."""
    messages, _ = _prepare(messages)
    yield from stream_local(messages)