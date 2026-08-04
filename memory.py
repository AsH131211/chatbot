import json
from pathlib import Path
from google import genai
from config import GEMINI_API, MEM_MODEL


MEMORY_DIR = Path("memories")
MEMORY_FILE = MEMORY_DIR / "default.json"


def load_memory():
    MEMORY_DIR.mkdir(exist_ok=True)

    if not MEMORY_FILE.exists():
        return {"facts": []}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory):
    MEMORY_DIR.mkdir(exist_ok=True)

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)



client = genai.Client(api_key=GEMINI_API)


def extract_memory(memory, conversation):
    prompt = f"""
You are a memory extraction system.

Existing memory:

{json.dumps(memory, indent=2)}

Recent conversation:

{json.dumps(conversation, indent=2)}

Update the memory using the conversation.

Rules:
- Keep only long-term useful facts.
- Ignore greetings.
- Ignore temporary plans.
- Ignore assistant responses.
- Merge duplicate facts.
- Return ONLY valid JSON.

Format:

{{
    "facts": [
        "Fact 1",
        "Fact 2"
    ]
}}
"""

    response = client.models.generate_content(
        model= MEM_MODEL,
        contents=prompt,
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.split("```", 1)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]

    return json.loads(text)
    