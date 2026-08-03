import json
from pathlib import Path

CHAT_DIR = Path("chats")
CHAT_FILE = CHAT_DIR / "default.json"

def load_chat():
    CHAT_DIR.mkdir(exist_ok=True)

    if not CHAT_FILE.exists():
        return[]


    with open(CHAT_FILE,"r") as file:
        return json.load(file)


def save_chat(conversation):
    CHAT_DIR.mkdir(exist_ok=True)

    with open(CHAT_FILE,"w") as file:
        json.dump(conversation,file, indent=4)

