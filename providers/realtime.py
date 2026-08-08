import json
import requests
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from config import SEARXNG_URL
from utils.fetch import fetch_url

_IST = ZoneInfo("Asia/Kolkata")

_TIME_KEYWORDS = (
    "time", "what time", "current time", "time now",
    "date", "today's date", "what date", "day today",
    "clock", "hour",
)

_ENGINES = "duckduckgo,google cse"


def _try_instant(query: str) -> str | None:
    if any(kw in query.lower() for kw in _TIME_KEYWORDS):
        now = datetime.now(_IST)
        return f"Current date and time: {now.strftime('%I:%M %p IST, %A %d %B %Y')}"
    return None


def ask_realtime(query: str, max_results: int = 3):
    try:
        instant = _try_instant(query)
        if instant:
            return [{"title": "Instant Answer", "url": "", "content": instant}]

        response = requests.get(
            f"{SEARXNG_URL}/search",
            params={"q": query, "format": "json", "engines": _ENGINES, "language": "en-IN"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        results = []

        for answer in data.get("answers", []):
            text = (answer.get("answer") if isinstance(answer, dict) else str(answer)).strip()
            if text:
                results.append({"title": "Instant Answer", "url": "", "content": text})

        for box in data.get("infoboxes", []):
            parts = [p for p in [box.get("infobox"), box.get("content")] if p]
            parts += [f"{a['label']}: {a['value']}" for a in box.get("attributes", []) if a.get("label") and a.get("value")]
            combined = "\n".join(parts).strip()
            if combined:
                results.append({"title": box.get("infobox", "Infobox"), "url": box.get("url", ""), "content": combined[:2000]})

        remaining = max(0, max_results - len(results))
        for r in data.get("results", [])[:remaining]:
            url = r.get("url", "")
            snippet = r.get("content", "").strip()
            try:
                article = fetch_url(url) if url else None
            except Exception:
                article = None
            content = (article or snippet)[:2000]
            if content:
                results.append({"title": r.get("title", ""), "url": url, "content": content})

        return results

    except requests.RequestException as e:
        raise RuntimeError(f"SearXNG request failed: {e}")
    except Exception as e:
        raise RuntimeError(f"SearXNG search failed: {e}")