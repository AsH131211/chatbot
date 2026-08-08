import json
from pathlib import Path

from google import genai
from config import GEMINI_API, MEM_MODEL

MEMORY_DIR = Path("memories")
MEMORY_FILE = MEMORY_DIR / "default.json"

_client = genai.Client(api_key=GEMINI_API)


def load_memory() -> dict:
    MEMORY_DIR.mkdir(exist_ok=True)
    if not MEMORY_FILE.exists():
        return {"facts": []}
    with open(MEMORY_FILE) as f:
        return json.load(f)


def save_memory(memory: dict) -> None:
    MEMORY_DIR.mkdir(exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


def extract_memory(memory: dict, conversation: list) -> dict:
    prompt = (
        "You are a memory extraction system.\n\n"
        f"Existing memory:\n\n{json.dumps(memory, indent=2)}\n\n"
        f"Recent conversation:\n\n{json.dumps(conversation, indent=2)}\n\n"
        "Update the memory using the conversation.\n\n"
        "Rules:\n"
        "- Keep only long-term useful facts.\n"
        "- Ignore greetings.\n"
        "- Ignore temporary plans.\n"
        "- Ignore assistant responses.\n"
        "- Merge duplicate facts.\n"
        "- Return ONLY valid JSON.\n\n"
        'Format:\n\n{"facts": ["Fact 1", "Fact 2"]}'
    )

    response = _client.models.generate_content(model=MEM_MODEL, contents=prompt)
    text = response.text.strip()

    if text.startswith("```"):
        text = text.split("```", 1)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]

    return json.loads(text)