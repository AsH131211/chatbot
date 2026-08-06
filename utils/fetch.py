import requests
import trafilatura
from bs4 import BeautifulSoup, Tag
from typing import Optional

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 Chrome/138 Safari/537.36"
    )
}

_NOISE_TAGS = [
    "script", "style", "noscript", "iframe",
    "nav", "footer", "header", "aside",
    "form", "button", "input", "select", "textarea",
    "svg", "canvas",
]

_MIN_GOOD_LENGTH = 150


def _table_to_text(table: Tag) -> str:
    lines: list[str] = []
    caption = table.find("caption")
    if caption:
        lines.append(f"[{caption.get_text(separator=' ', strip=True)}]")
    for tr in table.find_all("tr"):
        cells = [
            td.get_text(separator=" ", strip=True)
            for td in tr.find_all(["th", "td"])
        ]
        if any(c for c in cells):
            lines.append(" | ".join(cells))
    return "\n".join(lines)


def _bs4_extract(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(_NOISE_TAGS):
        tag.decompose()

    parts: list[str] = []
    seen: set[str] = set()

    for el in soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "dt", "dd", "table"]
    ):
        name = el.name
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            text = el.get_text(separator=" ", strip=True)
            if text and text not in seen:
                seen.add(text)
                parts.append(f"\n## {text}")
        elif name == "table":
            text = _table_to_text(el)
            if text and text not in seen:
                seen.add(text)
                parts.append(text)
        elif name in ("p", "li", "dt", "dd"):
            text = el.get_text(separator=" ", strip=True)
            if len(text) > 25 and text not in seen:
                seen.add(text)
                parts.append(text)

    return "\n".join(parts).strip()


def _is_poor_extraction(text: str) -> bool:
    if not text or len(text) < _MIN_GOOD_LENGTH:
        return True
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return True
    lengths = sorted(len(ln) for ln in lines)
    median_len = lengths[len(lengths) // 2]
    if median_len < 20 and len(lines) < 10:
        return True
    return False


def fetch_url(url: str) -> str:
    try:
        response = requests.get(url, headers=_HEADERS, timeout=10)
        response.raise_for_status()
        html = response.text

        traf_text: Optional[str] = trafilatura.extract(
            html,
            include_links=False,
            include_images=False,
            include_tables=True,
            favor_precision=False,
            no_fallback=False,
        )

        if not _is_poor_extraction(traf_text or ""):
            return traf_text 

        bs_text = _bs4_extract(html)

        if bs_text and len(bs_text) >= len(traf_text or ""):
            return bs_text

        return traf_text or ""

    except Exception:
        return ""