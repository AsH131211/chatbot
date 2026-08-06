#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"
PYTHON="$VENV/bin/python"
PIP="$VENV/bin/pip"
TUI="$SCRIPT_DIR/UI/tui.py"

if [[ ! -d "$VENV" ]]; then
    echo "  [!] No .venv found — creating one..."
    python3 -m venv "$VENV"
fi

if [[ ! -f "$VENV/.deps_installed" ]] || \
   [[ "$SCRIPT_DIR/requirements.txt" -nt "$VENV/.deps_installed" ]]; then
    echo "  [~] Installing dependencies..."
    "$PIP" install -q --upgrade pip
    "$PIP" install -q -r "$SCRIPT_DIR/requirements.txt"
    touch "$VENV/.deps_installed"
fi

cd "$SCRIPT_DIR"
exec "$PYTHON" "$TUI"
