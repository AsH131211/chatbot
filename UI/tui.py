"""
J.A.R.V.I.S  ─  Full-screen terminal shell
============================================
Layout
  ┌──────────────────────────────────────────┐
  │  jarvis ●                          19:49 │  ← header (1 line)
  ├──────────────────────────────────────────┤
  │                                          │
  │   [chat messages scroll here]            │  ← scrollable viewport
  │                                          │
  ├──────────────────────────────────────────┤
  │  ›  type here ...                        │  ← fixed input bar (1 line)
  │  ctrl-d quit  ·  ctrl-c cancel           │  ← status bar (1 line)
  └──────────────────────────────────────────┘
"""

import io
import sys
import threading
import textwrap
from datetime import datetime
from pathlib import Path

from rich.console import Console as RC
from rich.markdown import Markdown
from rich.text import Text

from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from assistant import Assistant  # noqa: E402

HISTORY_FILE = ROOT / ".jarvis_history"
BUBBLE_RATIO = 0.52

# ── TUI commands (everything else is forwarded to the LLM) ──────────────────

_CMDS = {"/exit", "/quit", "/clear", "/new", "/help"}



# ── Global state (lock-protected) ─────────────────────────────────────────────

_lock = threading.Lock()

# Each entry: {"role": "user"|"jarvis"|"jarvis_stream"|"raw", "text": str}
_msgs: list[dict] = []
_status_text: str = ""
_cancel = threading.Event()

# ── ANSI colour helpers ───────────────────────────────────────────────────────

def _c(r, g, b):    return f"\033[38;2;{r};{g};{b}m"
def _bg(r, g, b):   return f"\033[48;2;{r};{g};{b}m"
_R  = "\033[0m"
_DIM = "\033[2m"
_BOLD = "\033[1m"
_CYAN = _c(0, 210, 255)
_BLUE = _c(74, 158, 255)
_GREY = _c(200, 200, 200)

# ── Terminal size ─────────────────────────────────────────────────────────────

def _size() -> tuple[int, int]:
    try:
        from prompt_toolkit.application.current import get_app
        s = get_app().output.get_size()
        return s.rows, s.columns
    except Exception:
        return 24, 80

# ── Renderers ─────────────────────────────────────────────────────────────────

def _render_user(text: str, cols: int) -> str:
    max_w = max(20, int(cols * BUBBLE_RATIO))
    lines: list[str] = []
    for para in text.splitlines():
        lines.extend(textwrap.wrap(para, width=max_w) or [""])
    bw = min(max_w, max((len(l) for l in lines), default=1))

    out: list[str] = []
    label = "you"
    out.append(" " * max(0, cols - len(label) - 2) + f"{_DIM}{_GREY}{label}{_R}")
    for line in lines:
        cell = " " + line.ljust(bw) + " "
        pad  = max(0, cols - len(cell) - 1)
        out.append(
            " " * pad
            + _c(200, 216, 240)
            + _bg(26, 47, 74)
            + cell
            + _R
        )
    out.append("")
    return "\n".join(out) + "\n"


def _render_jarvis(text: str, cols: int) -> str:
    buf = io.StringIO()
    c = RC(file=buf, force_terminal=True, width=max(20, cols - 4), highlight=False)
    c.print(Text("jarvis", style="dim #4a9eff"))
    c.print(Markdown(text, code_theme="nord"))
    c.print()
    return buf.getvalue()


def _render_divider(cols: int) -> str:
    return _c(28, 28, 28) + "─" * cols + _R + "\n\n"



# ── Chat viewport ─────────────────────────────────────────────────────────────

def get_chat() -> ANSI:
    rows, cols = _size()
    avail = max(4, rows - 3)   # header(1) + sep(1) + input(1) + status(1)

    with _lock:
        msgs   = list(_msgs)
        status = _status_text

    parts: list[str] = []
    for msg in msgs:
        role, text = msg["role"], msg["text"]
        if role == "user":
            parts.append(_render_user(text, cols))
        elif role in ("jarvis", "jarvis_stream"):
            parts.append(_render_jarvis(text, cols))
            if role == "jarvis":
                parts.append(_render_divider(cols))
        else:  # raw
            parts.append(text)

    if status:
        parts.append(f"\n  {_c(255,200,50)}{status}{_R}\n")

    content = "".join(parts)
    lines   = content.split("\n")

    # Always show the BOTTOM of the chat (latest messages)
    if len(lines) > avail:
        lines = lines[-avail:]

    return ANSI("\n".join(lines))


def get_header() -> ANSI:
    _, cols = _size()
    now   = datetime.now().strftime("%H:%M")
    left  = f"  {_BOLD}{_BLUE}jarvis{_R}  {_c(50,205,50)}●{_R}"
    right = f"{_DIM}{now}{_R}"
    left_plain  = "  jarvis  ●"
    right_plain = now
    gap = max(0, cols - len(left_plain) - len(right_plain) - 1)
    return ANSI(left + " " * gap + right)


def get_status() -> ANSI:
    with _lock:
        s = _status_text
    if s:
        return ANSI(f"  {_DIM}{s}{_R}")
    return ANSI(f"  {_DIM}ctrl-d quit  ·  ctrl-c cancel{_R}")

# ── State management ──────────────────────────────────────────────────────────

def _set_status(text: str):
    global _status_text
    with _lock:
        _status_text = text


def _add_msg(role: str, text: str):
    with _lock:
        _msgs.append({"role": role, "text": text})


def _update_last_stream(text: str):
    with _lock:
        for i in range(len(_msgs) - 1, -1, -1):
            if _msgs[i]["role"] == "jarvis_stream":
                _msgs[i]["text"] = text
                return


def _finalise_stream():
    with _lock:
        for i in range(len(_msgs) - 1, -1, -1):
            if _msgs[i]["role"] == "jarvis_stream":
                _msgs[i]["role"] = "jarvis"
                return

# ── Chat thread ───────────────────────────────────────────────────────────────

def _friendly_error(e: Exception) -> str:
    msg = str(e)
    if "Connection refused" in msg and "8888" in msg:
        return "SearXNG is offline — start it first, then retry with /rt."
    if "Connection refused" in msg and "8080" in msg:
        return "Local LLM is offline — is llama-server running on port 8080?"
    if "Name resolution" in msg or "gaierror" in msg:
        return "DNS failure — no internet access from this machine."
    if "Timeout" in msg or "timed out" in msg:
        return "Request timed out."
    return msg


def _run_chat(text: str, app: Application, jarvis: Assistant):
    _cancel.clear()
    _add_msg("user", text)
    _set_status("◌  thinking…")
    app.invalidate()

    buf   = ""
    first = True
    try:
        for tok in jarvis.stream(text):
            if _cancel.is_set():
                break
            buf += tok
            if first:
                _set_status("")
                _add_msg("jarvis_stream", buf)
                first = False
            else:
                _update_last_stream(buf)
            app.invalidate()
    except Exception as e:
        friendly = _friendly_error(e)
        _set_status("")
        _add_msg("raw", f"\n  {_c(220,80,80)}error:{_R} {_DIM}{friendly}{_R}\n\n")
        app.invalidate()
        return

    _set_status("")
    if not first:
        _finalise_stream()
    app.invalidate()

# ── Command handler ───────────────────────────────────────────────────────────

def _run_command(text: str, app: Application, jarvis: Assistant):
    verb = text.strip().split()[0].lower()

    if verb in ("/exit", "/quit"):
        app.exit()
        return

    if verb in ("/clear", "/new"):
        with _lock:
            _msgs.clear()
        if verb == "/new":
            jarvis.conversation = []
        app.invalidate()
        return

    if verb == "/help":
        raw = (
            "\n"
            f"  {_BOLD}{_BLUE}commands{_R}\n"
            f"  {_DIM}{'─'*22}{_R}\n"
            f"  {_DIM}/clear    clear screen{_R}\n"
            f"  {_DIM}/new      fresh session{_R}\n"
            f"  {_DIM}/rt       realtime search  (/rt latest python){_R}\n"
            f"  {_DIM}/exit     quit{_R}\n\n"
        )
        _add_msg("raw", raw)
        app.invalidate()
        return

    _add_msg("raw", f"\n  {_c(255,200,50)}unknown:{_R} {text}  — try /help\n\n")
    app.invalidate()

# ── Application builder ───────────────────────────────────────────────────────

def build_app(jarvis: Assistant) -> Application:
    history   = FileHistory(str(HISTORY_FILE))
    input_buf = Buffer(
        history=history,
        auto_suggest=AutoSuggestFromHistory(),
        multiline=False,
        name="input",
    )

    kb = KeyBindings()

    @kb.add("enter")
    def _submit(event):
        text = input_buf.text.strip()
        input_buf.reset()
        if not text:
            return
        verb = text.split()[0].lower()
        fn = _run_command if verb in _CMDS else _run_chat
        threading.Thread(target=fn, args=(text, event.app, jarvis), daemon=True).start()

    @kb.add("c-d")
    def _quit(event):
        event.app.exit()

    @kb.add("c-c")
    def _cancel_stream(event):
        _cancel.set()

    @kb.add("up")
    def _hist_back(event):
        input_buf.history_backward(count=1)

    @kb.add("down")
    def _hist_fwd(event):
        input_buf.history_forward(count=1)

    # ── Layout ────────────────────────────────────────────────────────────────

    header_win = Window(
        content=FormattedTextControl(get_header),
        height=1,
        style="class:header",
    )
    chat_win = Window(
        content=FormattedTextControl(get_chat, focusable=False),
        wrap_lines=False,
        style="class:chat",
    )
    sep_win = Window(
        height=1,
        char="─",
        style="class:sep",
    )
    prompt_win = Window(
        content=FormattedTextControl(lambda: [("class:glyph", "  › ")]),
        width=5,
        height=1,
        style="class:pbar",
        dont_extend_height=True,
    )
    input_win = Window(
        content=BufferControl(
            buffer=input_buf,
        ),
        height=1,
        style="class:pbar",
        dont_extend_height=True,
    )
    status_win = Window(
        content=FormattedTextControl(get_status),
        height=1,
        style="class:status",
    )

    layout = Layout(
        HSplit([
            header_win,
            chat_win,
            sep_win,
            VSplit([prompt_win, input_win]),
            status_win,
        ]),
        focused_element=input_win,
    )

    style = Style.from_dict({
        "header":  "bg:#070707",
        "chat":    "bg:#070707",
        "sep":     "bg:#070707 #181818",
        "pbar":    "bg:#101010",
        "glyph":   "bg:#101010 #4a9eff bold",
        "status":  "bg:#050505",
        "":        "#c8c8c8 bg:#070707",
    })

    return Application(
        layout=layout,
        key_bindings=kb,
        style=style,
        full_screen=True,
        mouse_support=True,
        refresh_interval=0.5,
    )

# ── Entry ─────────────────────────────────────────────────────────────────────

def main():
    jarvis = Assistant()
    app = build_app(jarvis)
    app.run()


if __name__ == "__main__":
    main()