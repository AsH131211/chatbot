import requests
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from config import SEARXNG_URL
from utils.fetch import fetch_url

_IST = ZoneInfo("Asia/Kolkata")

# ── Instant local answers (no network) ───────────────────────────────────────

_TIME_KEYWORDS = (
    "time", "what time", "current time", "time now",
    "date", "today's date", "what date", "day today",
    "clock", "hour",
)


def _try_instant(query: str) -> str | None:
    q = query.lower()
    if any(kw in q for kw in _TIME_KEYWORDS):
        now = datetime.now(_IST)
        return f"Current date and time: {now.strftime('%I:%M %p IST, %A %d %B %Y')}"
    return None


# ── SearXNG search ────────────────────────────────────────────────────────────
# Only use engines confirmed working on this instance:
#   duckduckgo  — fast, good snippets, DDG instant answers
#   google cse  — Google Custom Search, good local results

_ENGINES = "duckduckgo,google cse"


def ask_realtime(query: str, max_results: int = 3):
    try:
        # Fast-path: answer without hitting the network
        instant = _try_instant(query)
        if instant:
            return [{"title": "Instant Answer", "url": "", "content": instant}]

        response = requests.get(
            f"{SEARXNG_URL}/search",
            params={
                "q":        query,
                "format":   "json",
                "engines":  _ENGINES,
                "language": "en-IN",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        search_results = []

        # 1. Instant answers (DDG quick facts)
        for answer in data.get("answers", []):
            text = (answer.get("answer") if isinstance(answer, dict) else str(answer)).strip()
            if text:
                search_results.append(
                    {"title": "Instant Answer", "url": "", "content": text}
                )

        # 2. Infoboxes (knowledge panels)
        for box in data.get("infoboxes", []):
            parts = []
            if box.get("infobox"):
                parts.append(box["infobox"])
            if box.get("content"):
                parts.append(box["content"])
            for attr in box.get("attributes", []):
                if attr.get("label") and attr.get("value"):
                    parts.append(f"{attr['label']}: {attr['value']}")
            combined = "\n".join(parts).strip()
            if combined:
                search_results.append(
                    {"title": box.get("infobox", "Infobox"),
                     "url":   box.get("url", ""),
                     "content": combined[:2000]}
                )

        # 3. Web results — use the search snippet directly (reliable), then
        #    optionally try to fetch the full page for richer content.
        remaining = max(0, max_results - len(search_results))
        for result in data.get("results", [])[:remaining]:
            url     = result.get("url", "")
            snippet = result.get("content", "").strip()

            # Attempt full-page fetch; fall back to snippet on any failure
            try:
                article = fetch_url(url) if url else None
            except Exception:
                article = None

            content = (article or snippet)[:2000]
            if content:
                search_results.append(
                    {"title": result.get("title", ""), "url": url, "content": content}
                )

        return search_results

    except requests.RequestException as e:
        raise RuntimeError(f"SearXNG request failed: {e}")

    except Exception as e:
        raise RuntimeError(f"SearXNG search failed: {e}")