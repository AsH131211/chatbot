import io
import sys
import time
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
INVALIDATE_INTERVAL_S = 0.016

_CMDS = {"/exit", "/quit", "/clear", "/new", "/help"}

_lock = threading.Lock()
_msgs: list = []
_status_text: str = ""
_cancel = threading.Event()
_last_invalidate: float = 0.0

_THINK_FRAMES = ("◌", "◎", "●", "◎")
_think_idx = 0
_think_timer = None
_thinking_on = False

_CUR_FRAMES = ("█", "▌", "▏", " ", "▏", "▌")
_cur_char = "█"
_cur_idx = 0
_cur_timer = None
_cur_on = False


def _c(r, g, b):  return f"\033[38;2;{r};{g};{b}m"
def _bg(r, g, b): return f"\033[48;2;{r};{g};{b}m"
_R    = "\033[0m"
_DIM  = "\033[2m"
_BOLD = "\033[1m"
_BLUE = _c(74, 158, 255)
_GREY = _c(200, 200, 200)


def _size():
    try:
        from prompt_toolkit.application.current import get_app
        s = get_app().output.get_size()
        return s.rows, s.columns
    except Exception:
        return 24, 80


def _render_user(text: str, cols: int) -> str:
    max_w = max(20, int(cols * BUBBLE_RATIO))
    lines = []
    for para in text.splitlines():
        lines.extend(textwrap.wrap(para, width=max_w) or [""])
    bw = min(max_w, max((len(l) for l in lines), default=1))
    out = []
    label = "you"
    out.append(" " * max(0, cols - len(label) - 2) + f"{_DIM}{_GREY}{label}{_R}")
    for line in lines:
        cell = " " + line.ljust(bw) + " "
        pad = max(0, cols - len(cell) - 1)
        out.append(" " * pad + _c(200, 216, 240) + _bg(26, 47, 74) + cell + _R)
    out.append("")
    return "\n".join(out) + "\n"


def _render_jarvis_rich(text: str, cols: int) -> str:
    buf = io.StringIO()
    c = RC(file=buf, force_terminal=True, width=max(20, cols - 4), highlight=False)
    c.print(Text("jarvis", style="dim #4a9eff"))
    c.print(Markdown(text, code_theme="nord"))
    c.print()
    return buf.getvalue()


def _render_jarvis_plain(text: str, cols: int) -> str:
    width = max(20, cols - 4)
    rows, _ = _size()
    avail = max(4, rows - 4)
    wrapped: list[str] = []
    for para in text.splitlines():
        wrapped.extend(textwrap.wrap(para, width=width) or [""])
    if len(wrapped) > avail - 1:
        wrapped = wrapped[-(avail - 1):]
    cursor = _c(74, 158, 255) + _cur_char + _R
    if wrapped:
        wrapped[-1] += cursor
    else:
        wrapped = [cursor]
    return f"{_DIM}{_BLUE}jarvis{_R}\n" + "\n".join(wrapped) + "\n\n"


def _render_divider(cols: int) -> str:
    return _c(28, 28, 28) + "─" * cols + _R + "\n\n"


def _get_rendered(msg: dict, cols: int) -> str:
    role = msg["role"]
    text = msg["text"]
    cache = msg.get("_cache")

    if role == "user":
        if cache and cache[0] == cols:
            return cache[1]
        rendered = _render_user(text, cols)
        msg["_cache"] = (cols, rendered)
        return rendered

    if role == "jarvis":
        if cache and cache[0] == cols:
            return cache[1]
        rendered = _render_jarvis_rich(text, cols) + _render_divider(cols)
        msg["_cache"] = (cols, rendered)
        return rendered

    if role == "jarvis_stream":
        return _render_jarvis_plain(text, cols)

    return text


def get_chat() -> ANSI:
    rows, cols = _size()
    avail = max(4, rows - 3)
    with _lock:
        msgs = list(_msgs)
        status = _status_text
    parts = [_get_rendered(m, cols) for m in msgs]
    if status:
        parts.append(f"\n  {_c(255,200,50)}{status}{_R}\n")
    lines = "".join(parts).split("\n")
    if len(lines) > avail:
        lines = lines[-avail:]
    return ANSI("\n".join(lines))


def get_header() -> ANSI:
    _, cols = _size()
    now = datetime.now().strftime("%H:%M")
    left = f"  {_BOLD}{_BLUE}jarvis{_R}  {_c(50,205,50)}●{_R}"
    left_plain = "  jarvis  ●"
    gap = max(0, cols - len(left_plain) - len(now) - 1)
    return ANSI(left + " " * gap + f"{_DIM}{now}{_R}")


def get_status() -> ANSI:
    with _lock:
        s = _status_text
    if s:
        return ANSI(f"  {_DIM}{s}{_R}")
    return ANSI(f"  {_DIM}ctrl-d quit  ·  ctrl-c cancel{_R}")


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
                _msgs[i].pop("_cache", None)
                return


def _invalidate(app: Application, force: bool = False):
    global _last_invalidate
    now = time.monotonic()
    if force or (now - _last_invalidate) >= INVALIDATE_INTERVAL_S:
        _last_invalidate = now
        app.invalidate()


def _stop_thinking():
    global _think_timer, _thinking_on
    _thinking_on = False
    if _think_timer:
        _think_timer.cancel()
        _think_timer = None


def _tick_thinking(app: Application):
    global _think_idx, _think_timer
    if not _thinking_on:
        return
    _set_status(f"{_THINK_FRAMES[_think_idx % len(_THINK_FRAMES)]}  thinking…")
    _invalidate(app, force=True)
    _think_idx += 1
    _think_timer = threading.Timer(0.28, _tick_thinking, args=(app,))
    _think_timer.daemon = True
    _think_timer.start()


def _start_thinking(app: Application):
    global _think_idx, _thinking_on
    _think_idx = 0
    _thinking_on = True
    _tick_thinking(app)


def _stop_cursor():
    global _cur_timer, _cur_on, _cur_char
    _cur_on = False
    _cur_char = ""
    if _cur_timer:
        _cur_timer.cancel()
        _cur_timer = None


def _tick_cursor(app: Application):
    global _cur_idx, _cur_char, _cur_timer
    if not _cur_on:
        return
    _cur_char = _CUR_FRAMES[_cur_idx % len(_CUR_FRAMES)]
    _cur_idx += 1
    _invalidate(app, force=True)
    _cur_timer = threading.Timer(0.11, _tick_cursor, args=(app,))
    _cur_timer.daemon = True
    _cur_timer.start()


def _start_cursor(app: Application):
    global _cur_idx, _cur_on, _cur_char
    _cur_idx = 0
    _cur_on = True
    _cur_char = _CUR_FRAMES[0]
    _tick_cursor(app)


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
    _invalidate(app, force=True)
    _start_thinking(app)

    buf = ""
    first = True
    try:
        for tok in jarvis.stream(text):
            if _cancel.is_set():
                break
            buf += tok
            if first:
                _stop_thinking()
                _set_status("")
                _add_msg("jarvis_stream", tok)
                _start_cursor(app)
                first = False
            else:
                _update_last_stream(buf)
            _invalidate(app)

    except Exception as e:
        _stop_thinking()
        _stop_cursor()
        _set_status("")
        _add_msg("raw", f"\n  {_c(220,80,80)}error:{_R} {_DIM}{_friendly_error(e)}{_R}\n\n")
        _invalidate(app, force=True)
        return

    _stop_thinking()
    _stop_cursor()
    _set_status("")
    if not first:
        _finalise_stream()
    _invalidate(app, force=True)


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
        _invalidate(app, force=True)
        return

    if verb == "/help":
        _add_msg("raw", (
            "\n"
            f"  {_BOLD}{_BLUE}commands{_R}\n"
            f"  {_DIM}{'─'*22}{_R}\n"
            f"  {_DIM}/clear    clear screen{_R}\n"
            f"  {_DIM}/new      fresh session{_R}\n"
            f"  {_DIM}/rt       realtime search  (/rt latest python){_R}\n"
            f"  {_DIM}/exit     quit{_R}\n\n"
        ))
        _invalidate(app, force=True)
        return

    _add_msg("raw", f"\n  {_c(255,200,50)}unknown:{_R} {text}  — try /help\n\n")
    _invalidate(app, force=True)


def build_app(jarvis: Assistant) -> Application:
    input_buf = Buffer(
        history=FileHistory(str(HISTORY_FILE)),
        auto_suggest=AutoSuggestFromHistory(),
        multiline=False,
        name="input",
    )

    kb = KeyBindings()

    @kb.add("enter")
    def _submit(event):
        text = input_buf.text.strip()
        input_buf.reset(append_to_history=True)
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

    layout = Layout(
        HSplit([
            Window(content=FormattedTextControl(get_header), height=1, style="class:header"),
            Window(content=FormattedTextControl(get_chat, focusable=False), wrap_lines=False, style="class:chat"),
            Window(height=1, char="─", style="class:sep"),
            VSplit([
                Window(content=FormattedTextControl(lambda: [("class:glyph", "  › ")]), width=5, height=1, style="class:pbar", dont_extend_height=True),
                Window(content=BufferControl(buffer=input_buf), height=1, style="class:pbar", dont_extend_height=True),
            ]),
            Window(content=FormattedTextControl(get_status), height=1, style="class:status"),
        ]),
        focused_element=Window(content=BufferControl(buffer=input_buf), height=1),
    )

    style = Style.from_dict({
        "header": "bg:#070707",
        "chat":   "bg:#070707",
        "sep":    "bg:#070707 #181818",
        "pbar":   "bg:#101010",
        "glyph":  "bg:#101010 #4a9eff bold",
        "status": "bg:#050505",
        "":       "#c8c8c8 bg:#070707",
    })

    return Application(
        layout=layout,
        key_bindings=kb,
        style=style,
        full_screen=True,
        mouse_support=True,
        refresh_interval=0.5,
    )


def main():
    jarvis = Assistant()
    build_app(jarvis).run()


if __name__ == "__main__":
    main()
