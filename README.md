# 🤖 J.A.R.V.I.S.

> **A lightweight terminal AI assistant built from scratch in Python — Just A Rather Very Intelligent System.**

Jarvis is a personal learning project that explores how modern AI assistants work under the hood. Every component is hand-crafted — from conversation management and persistent memory to provider routing, live web search, local LLM support, and a full-screen terminal UI.

---

## ✨ Features

- 🖥️ **Full-screen TUI** — immersive, full-screen terminal shell built with `rich` + `prompt_toolkit`
- 💬 **Streaming chat** — tokens stream live into the TUI viewport as they're generated
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
│  jarvis ●                          19:49 │  ← header
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
├── main.py              # Minimal entry point — creates Assistant and runs a basic REPL
├── jarvis.sh            # One-command launcher — auto-venv, deps, starts TUI
├── config.py            # Centralized config (models, API keys, URLs, flags)
├── assistant.py         # Assistant class — wraps streaming, memory, and history
├── router.py            # Provider routing logic (/rt prefix → realtime search)
├── llm.py               # Core chat function — routes, fetches web context, dispatches
├── context.py           # Builds the full message context (system prompt + memory + history)
├── memory.py            # Persistent memory: load, save, and LLM-powered extraction
├── storage.py           # Chat history: load and save conversation to disk
│
├── UI/
│   └── tui.py           # Full-screen TUI — rich layout, streaming viewport, key bindings
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
```

```bash
# Bash / Zsh
source .venv/bin/activate

# Fish
source .venv/bin/activate.fish
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Jarvis requires a Google Gemini API key for memory extraction.

```bash
# Bash / Zsh — add to ~/.bashrc or ~/.zshrc
export GEMINI_API="your_gemini_api_key"

# Fish — persists across sessions
set -Ux GEMINI_API "your_gemini_api_key"
```

Verify it's set:

```bash
echo $GEMINI_API
```

Get a free API key at [aistudio.google.com](https://aistudio.google.com).

---

## ▶️ Running Jarvis

**Recommended — one-command launcher (auto-manages venv & deps):**

```bash
./jarvis.sh
```

**Or manually (with venv activated):**

```bash
python UI/tui.py
```

**Minimal REPL (no TUI):**

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

Jarvis uses a simple prefix-based routing system.

| Prefix | Behaviour |
|--------|-----------|
| *(none)* | Sent directly to the local Qwen3-8B model |
| `/rt ` | Searches the web via SearXNG, scrapes top results, and sends the live content as context to the local model |

**Example:**

```text
> tell me a joke                        ← local Qwen3 model only
> /rt latest stable Linux kernel?      ← live web search → local model answers with fresh data
```

---

## 🖥️ Local LLM Setup

Jarvis streams responses from a locally running `llama-server` instance.

**1. Install `llama.cpp` and start the server:**

```bash
llama-server --model Qwen3-8B-Q4_K_M.gguf --port 8080
```

**2. Verify it's running:**

```bash
curl http://localhost:8080/v1/models
```

Configured in [`config.py`](config.py):

```python
LLAMA_URL   = "http://localhost:8080/v1"
LLAMA_MODEL = "Qwen/Qwen3-8B-GGUF:Q4_K_M"
```

Tokens stream live into the TUI viewport — no spinner, just real-time text.

---

## 🌐 Web Search Setup (SearXNG)

The `/rt` prefix triggers a live web search using a locally running [SearXNG](https://github.com/searxng/searxng) instance.

**Run SearXNG with Docker:**

```bash
docker run -d -p 8888:8080 searxng/searxng
```

Configured in [`config.py`](config.py):

```python
SEARXNG_URL = "http://127.0.0.1:8888"
```

**How it works:**
1. Queries SearXNG for the top 3 results
2. Fetches each URL — extracts clean text via `trafilatura`, with `BeautifulSoup` as fallback
3. Enhances the query with the user's known location (from memory) for better local results
4. Injects the scraped content as a system message so the local model answers from live data

---

## 🧠 Memory System

After each turn, Jarvis uses a lightweight Gemini model (`gemini-3.5-flash-lite`) to extract and update long-term facts about the user.

**Rules applied during extraction:**
- ✅ Keep only persistent, useful facts
- ❌ Ignore greetings, small talk, temporary plans, assistant responses
- 🔀 Merge duplicate or related facts
- 💾 Stored in `memories/default.json`

Memory is injected as a system message at the start of every context, so Jarvis always knows who it's talking to. Location facts from memory are also used to improve web search relevance.

---

## 🧩 Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| TUI Framework | `prompt_toolkit >= 3.0.0` + `rich >= 13.0.0` |
| Local LLM | Qwen3-8B via `llama-server` (OpenAI-compatible, streamed) |
| Memory Extraction | Google Gemini (`gemini-3.5-flash-lite`) |
| Web Search | SearXNG (self-hosted, local) |
| Web Scraping | `trafilatura` + `BeautifulSoup4` / `lxml` |
| Google GenAI SDK | `google-genai >= 1.32.0` |
| HTTP | `requests` |

---

## 🗺️ Roadmap

### ✅ Version 0.1
- [x] Connect to Gemini API
- [x] Single-prompt chatbot

### ✅ Version 0.2
- [x] Interactive chatbot (REPL loop)
- [x] Conversation history
- [x] Modular codebase

### ✅ Version 0.3
- [x] Streaming responses
- [x] Provider abstraction layer

### ✅ Version 0.4
- [x] Context manager with sliding window
- [x] Persistent chat history (JSON)

### ✅ Version 0.5
- [x] Persistent memory system (LLM-powered extraction)
- [x] Local LLM provider (`llama-server` + Qwen3-8B)
- [x] Smart provider routing (`/rt` prefix)
- [x] Live web search (SearXNG + page scraping)
- [x] Live token streaming
- [x] JARVIS personality system prompt

### ✅ Version 1.0
- [x] Full-screen TUI (`rich` + `prompt_toolkit`)
- [x] `Assistant` class — clean streaming + memory API
- [x] TUI commands: `/clear`, `/new`, `/help`, `/exit`, `/quit`
- [x] Ctrl-C to cancel streaming response mid-generation
- [x] Input history navigation (↑ / ↓)
- [x] Location-aware web search (memory-injected context)
- [x] One-command launcher (`jarvis.sh`)

### 🚀 Version 1.1+ (Planned)
- [ ] Named chat sessions
- [ ] Tool calling / function use
- [ ] Retrieval-Augmented Generation (RAG)
- [ ] Voice interface

---

## 🎯 Project Goals

This project is being built to deeply understand how production AI assistants actually work.

Topics being explored:

- Prompt Engineering & System Prompts
- Context & Memory Management
- Provider Abstraction & Routing
- Streaming LLM Responses
- Local LLM Integration (llama.cpp)
- Live Web Search & Content Extraction
- Terminal UI Design (TUI)
- Tool Calling
- Retrieval-Augmented Generation (RAG)

---

## 🤝 Contributing

Contributions, ideas, and suggestions are always welcome.

Feel free to open an issue or submit a pull request.

---

<div align="center">

### ⭐ If you found this project interesting, consider giving it a star!

**Built with ❤️, Python, and lots of curiosity.**

*Shinzou wo Sasageyo!*

</div>
