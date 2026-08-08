import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from assistant import Assistant

jarvis = Assistant()
print("Jarvis is online.\n")

while True:
    try:
        prompt = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        break

    if not prompt:
        continue

    if prompt in ("/exit", "/quit"):
        break

    for token in jarvis.stream(prompt):
        print(token, end="", flush=True)
    print()