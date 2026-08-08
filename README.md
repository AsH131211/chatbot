# 🤖 J.A.R.V.I.S.

> **A lightweight terminal AI assistant built from scratch in Python — Just A Rather Very Intelligent System.**

Jarvis is a personal learning project that explores how modern AI assistants work under the hood. Every component is hand-crafted — from conversation management and persistent memory to provider routing, live web search, local LLM support, voice synthesis, and a full-screen terminal UI.

---

## ✨ Features

- 🖥️ **Full-screen TUI** — immersive, full-screen terminal shell built with `rich` + `prompt_toolkit`
- 💬 **Streaming chat** — tokens stream live into the TUI viewport as they're generated
- 🔊 **Voice synthesis** — sentence-by-sentence TTS via `pykokoro` (Kokoro), synced with the streaming response
- 🧠 **Persistent memory** — extracts and stores long-term facts about the user across sessions using Gemini
- 💾 **Persistent chat history** — conversation is saved and resumed automatically
- 🪟 **Sliding context window** — keeps the last 20 messages in context to stay within token limits
- 🔀 **Smart provider routing** — use `/rt` prefix to trigger live web search + local LLM answer
- 🌐 **Live web search** — queries SearXNG, fetches and scrapes full page content via `trafilatura` and `BeautifulSoup`
- 📍 **Location-aware search** — memory-injected location context improves local search results
- 🖥️ **Local LLM** — streams responses from Qwen3-8B via `llama-server` (OpenAI-compatible API)
- 🎭 **JARVIS personality** — responds as the composed, witty AI from Iron Man; addresses you as *"sir"*
- 🔐 **Secure API key handling** — keys loaded from environment variables only
- 🚀 **One-command launch** — `jarvis.sh` auto-creates the venv, installs deps, and starts the TUI

---

## 🚀 Demo

```text
┌──────────────────────────────────────────┐
│  jarvis ●                          19:49 │
├──────────────────────────────────────────┤
│                                          │
│   jarvis                                 │
│   Good evening, sir. All systems are     │
│   online and ready. How may I assist?    │
│                                 you      │
│           ╭─────────────────────────╮   │
│           │ /rt latest Linux kernel │   │
│           ╰─────────────────────────╯   │
│   jarvis                                 │
│   The latest stable Linux kernel is...  │
│                                          │
├──────────────────────────────────────────┤
│  ›  type here ...                        │
│  ctrl-d quit  ·  ctrl-c cancel           │
└──────────────────────────────────────────┘
```

---

## 📂 Project Structure

```text
jarvis/
│
├── main.py              # Minimal streaming REPL (no TUI)
├── jarvis.sh            # One-command launcher — auto-venv, deps, starts TUI
├── config.py            # Centralized config (models, API keys, URLs, flags)
├── assistant.py         # Assistant class — streaming, memory, voice sync
├── router.py            # Provider routing (/rt prefix → realtime search)
├── llm.py               # Core chat function — routes, fetches web context, dispatches
├── context.py           # Builds the full message context (system prompt + memory + history)
├── memory.py            # Persistent memory: load, save, and LLM-powered extraction
├── storage.py           # Chat history: atomic load/save to disk
│
├── UI/
│   └── tui.py           # Full-screen TUI — rich layout, streaming viewport, key bindings
│
├── voice/
│   ├── __init__.py      # Public API: preload, speak, wait
│   ├── tts.py           # TTS engine — pykokoro pipeline, background worker queue
│   ├── player.py        # Audio playback via pw-play
│   └── config.py        # Voice settings (voice name, speed, language, quality)
│
├── providers/
│   ├── local.py         # Local LLM provider (llama-server, streaming, OpenAI-compatible)
│   └── realtime.py      # Realtime provider — SearXNG search + page fetching
│
├── utils/
│   └── fetch.py         # Web page fetcher: trafilatura + BeautifulSoup fallback
│
├── chats/
│   └── default.json     # Persisted conversation history (auto-created)
│
├── memories/
│   └── default.json     # Persisted user memory facts (auto-created)
│
├── requirements.txt
└── README.md
```

---

## 🛠️ Installation

**Clone the repository**

```bash
git clone git@github.com:AsH131211/jarvis.git
cd jarvis
```

**Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Jarvis requires a Google Gemini API key for memory extraction.

```bash
export GEMINI_API="your_gemini_api_key"
```

Get a free API key at [aistudio.google.com](https://aistudio.google.com).

---

## ▶️ Running Jarvis

**Recommended — one-command launcher:**

```bash
./jarvis.sh
```

**Or manually:**

```bash
python UI/tui.py
```

**Minimal streaming REPL (no TUI):**

```bash
python main.py
```

---

## ⌨️ TUI Commands

| Command | Behaviour |
|---------|----------|
| `/rt <query>` | Live web search → local model answers with fresh data |
| `/clear` | Clear the screen without resetting the session |
| `/new` | Fresh session (clears screen + conversation history) |
| `/help` | Show available commands |
| `/exit` or `/quit` | Quit Jarvis |
| `Ctrl-D` | Quit Jarvis |
| `Ctrl-C` | Cancel the current streaming response |
| `↑` / `↓` | Navigate input history |

---

## 🔀 Provider Routing

| Prefix | Behaviour |
|--------|-----------|
| *(none)* | Sent directly to the local Qwen3-8B model |
| `/rt ` | Searches the web via SearXNG, scrapes top results, and sends the live content as context to the local model |

---

## 🖥️ Local LLM Setup

```bash
llama-server --model Qwen3-8B-Q4_K_M.gguf --port 8080
```

Configured in [`config.py`](config.py):

```python
LLAMA_URL   = "http://localhost:8080/v1"
LLAMA_MODEL = "Qwen/Qwen3-8B-GGUF:Q4_K_M"
```

---

## 🌐 Web Search Setup (SearXNG)

```bash
docker run -d -p 8888:8080 searxng/searxng
```

Configured in [`config.py`](config.py):

```python
SEARXNG_URL = "http://127.0.0.1:8888"
```

---

## 🔊 Voice Setup

Voice is powered by [Kokoro](https://github.com/thewh1teagle/pykokoro) via `pykokoro`. Audio is played through PipeWire (`pw-play`).

Configure in [`voice/config.py`](voice/config.py):

```python
VOICE_NAME   = "bm_daniel"
MODEL_QUALITY = "q4"
LANGUAGE     = "en-gb"
SPEECH_SPEED = 1.0
VOICE_ENABLED = True
```

Kokoro models download automatically on first run. Playback requires `pipewire-pulse` or an equivalent PipeWire setup.

---

## 🧠 Memory System

After each turn, Jarvis uses `gemini-3.5-flash-lite` to extract and update long-term facts about the user. Memory is injected as a system message at the start of every context, so Jarvis always knows who it's talking to.

---

## 🧩 Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| TUI | `prompt_toolkit >= 3.0.0` + `rich >= 13.0.0` |
| Local LLM | Qwen3-8B via `llama-server` (OpenAI-compatible, streamed) |
| Memory Extraction | Google Gemini (`gemini-3.5-flash-lite`) |
| Voice TTS | `pykokoro` (Kokoro) + `soundfile` + `pw-play` |
| Web Search | SearXNG (self-hosted, local) |
| Web Scraping | `trafilatura` + `BeautifulSoup4` / `lxml` |
| HTTP | `requests` |

---

## 🗺️ Roadmap

### ✅ Version 0.1 — 0.5
- [x] Gemini API, REPL, conversation history, streaming, provider abstraction, context window, memory, local LLM, web search, JARVIS personality

### ✅ Version 1.0
- [x] Full-screen TUI, `Assistant` class, TUI commands, Ctrl-C cancel, input history, location-aware search, one-command launcher

### ✅ Version 1.1
- [x] Voice interface — sentence-synced TTS via Kokoro, background worker queue, preload on startup

### 🚀 Version 1.2+ (Planned)
- [ ] Named chat sessions
- [ ] Tool calling / function use
- [ ] Retrieval-Augmented Generation (RAG)

---

## 🎯 Project Goals

Topics being explored:

- Prompt Engineering & System Prompts
- Context & Memory Management
- Provider Abstraction & Routing
- Streaming LLM Responses
- Local LLM Integration (llama.cpp)
- Live Web Search & Content Extraction
- Terminal UI Design (TUI)
- Voice Synthesis & Audio Sync

---

## 🤝 Contributing

Contributions, ideas, and suggestions are always welcome. Feel free to open an issue or submit a pull request.

---

<div align="center">

### ⭐ If you found this project interesting, consider giving it a star!

**Built with ❤️, Python, and lots of curiosity.**

*Shinzou wo Sasageyo!*

</div>
