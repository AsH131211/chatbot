import requests

from config import SEARXNG_URL
from utils.fetch import fetch_url


def ask_realtime(query: str, max_results: int = 3):
    try:
        response = requests.get(
            f"{SEARXNG_URL}/search",
            params={
                "q": query,
                "format": "json",
                "language": "en",
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            return []

        search_results = []

        for result in results[:max_results]:
            url = result.get("url", "")
            article = fetch_url(url)

            if not article:
                article = result.get("content", "")

            search_results.append(
                {
                    "title": result.get("title", ""),
                    "url": url,
                    "content": article[:2000],
                }
            )

        return search_results

    except requests.RequestException as e:
        raise RuntimeError(f"SearXNG request failed: {e}")

    except Exception as e:
        raise RuntimeError(f"SearXNG search failed: {e}")