"""
storage.py — atomic JSON persistence for the conversation log.

Uses a write-to-temp-then-rename pattern so the chat file is never
left in a half-written state if the process is interrupted mid-save.
"""
import json
import os
import tempfile
from pathlib import Path

CHAT_DIR  = Path("chats")
CHAT_FILE = CHAT_DIR / "default.json"


def load_chat() -> list:
    CHAT_DIR.mkdir(exist_ok=True)
    if not CHAT_FILE.exists():
        return []
    with open(CHAT_FILE, "r") as fh:
        return json.load(fh)


def save_chat(conversation: list) -> None:
    CHAT_DIR.mkdir(exist_ok=True)
    # Write to a sibling temp file, then atomically replace.
    fd, tmp = tempfile.mkstemp(dir=CHAT_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(conversation, fh, indent=2)
        os.replace(tmp, CHAT_FILE)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
