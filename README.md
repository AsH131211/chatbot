# 🤖 Jarvis

> **A lightweight terminal AI assistant built from scratch in Python — inspired by Iron Man's J.A.R.V.I.S.**

Jarvis is a personal learning project that explores how modern AI assistants like ChatGPT, Gemini, and Claude work under the hood. Every component is hand-crafted — from conversation management and persistent memory to provider routing and local LLM support.

---

## ✨ Features

- 💬 **Interactive terminal chatbot** — clean REPL-style interface
- 🧠 **Persistent memory** — extracts and stores long-term facts about the user across sessions
- 💾 **Persistent chat history** — conversation is saved and resumed automatically
- 🪟 **Sliding context window** — keeps the last 20 messages in context to stay within token limits
- 🔀 **Smart provider routing** — use `/rt` prefix to force the realtime (Gemini) provider
- 🖥️ **Local LLM support** — runs Qwen3-8B via `llama-server` (OpenAI-compatible API)
- ☁️ **Realtime provider** — Gemini streaming via Google GenAI SDK
- 🔄 **Automatic fallback** — falls back to Gemini if the local model is unavailable
- 🏗️ **Modular architecture** — clean separation of concerns across focused modules
- 🔐 **Secure API key handling** — keys loaded from environment variables only

---

## 🚀 Demo

```text
Jarvis is online.
Type /exit to quit.

> hello

Jarvis: Hello! How can I assist you today?

> /rt what's the latest news in AI?

Jarvis: [streams response from Gemini in realtime...]

> /exit

Shutting down...
```

---

## 📂 Project Structure

```text
jarvis/
│
├── main.py              # Entry point — REPL loop, orchestrates all modules
├── config.py            # Centralized config (models, API keys, URLs, flags)
├── router.py            # Provider routing logic (/rt prefix → realtime)
├── llm.py               # Core chat function — selects provider and dispatches
├── context.py           # Builds the full message context (system + memory + history)
├── memory.py            # Persistent memory: load, save, and LLM-powered extraction
├── storage.py           # Chat history: load and save conversation to disk
│
├── providers/
│   ├── local.py         # Local LLM provider (llama-server, OpenAI-compatible)
│   └── realtime.py      # Realtime provider (Gemini streaming)
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

> **Note:** Local LLM support also requires the `openai` Python package. Install it with:
> ```bash
> pip install openai
> ```

---

## 🔑 Environment Variables

Jarvis requires a Google Gemini API key to be set as an environment variable.

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

```bash
python main.py
```

Exit anytime with:

```text
/exit
```

---

## 🔀 Provider Routing

Jarvis uses a smart routing system to decide which LLM handles your message.

| Prefix | Provider | Model |
|--------|----------|-------|
| *(none)* | Local LLM (default) | Qwen3-8B via `llama-server` |
| `/rt ` | Realtime (Gemini) | `gemini-3.6-flash` |

**Example:**

```text
> tell me a joke           ← handled by local Qwen3 model
> /rt what is quantum computing?  ← handled by Gemini streaming
```

If the local model is unreachable (e.g., `llama-server` is not running), Jarvis automatically falls back to the Gemini provider.

---

## 🖥️ Local LLM Setup

Jarvis connects to a locally running `llama-server` instance via its OpenAI-compatible API.

**1. Install `llama.cpp`** and download the model:

```bash
# Example: download Qwen3-8B GGUF
# Then run the server
llama-server --model Qwen3-8B-Q4_K_M.gguf --port 8080
```

**2. Verify it's running:**

```bash
curl http://localhost:8080/v1/models
```

Jarvis will then automatically route non-prefixed queries to it.

Configured in [`config.py`](config.py):

```python
LLAMA_URL   = "http://localhost:8080/v1"
LLAMA_MODEL = "Qwen/Qwen3-8B-GGUF:Q4_K_M"
```

---

## 🧠 Memory System

After each turn, Jarvis uses a lightweight Gemini model (`gemini-3.5-flash-lite`) to extract and update long-term facts about the user from the conversation.

**Rules applied during extraction:**
- ✅ Keep only persistent, useful facts
- ❌ Ignore greetings, small talk, temporary plans
- 🔀 Merge duplicate or related facts
- 💾 Stored in `memories/default.json`

Memory is injected as a system message at the start of every context, so Jarvis always knows who it's talking to.

---

## 🧩 Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Realtime LLM | Google Gemini (`gemini-3.6-flash`) |
| Memory Extraction | Google Gemini (`gemini-3.5-flash-lite`) |
| Local LLM | Qwen3-8B via `llama-server` (OpenAI-compatible) |
| Google GenAI SDK | `google-genai >= 1.32.0` |

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
- [x] Automatic local → realtime fallback

### 🚀 Version 1.0 (Planned)
- [ ] Rich terminal UI (TUI)
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
