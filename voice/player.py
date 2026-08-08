import subprocess
from pathlib import Path


def play(audio_file: Path) -> None:
    subprocess.run(
        ["pw-play", str(audio_file)],
        check=True,
    )
