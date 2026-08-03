# 🤖 Jarvis

> **A lightweight terminal (for now) AI assistant built from scratch in Python.**

Jarvis is a personal learning project that explores how modern AI assistants like ChatGPT, Gemini, and Claude work behind the scenes. Instead of relying on frameworks, every component is built manually—from conversation handling to provider switching and (soon) memory management.

---

## ✨ Features

- 💬 Interactive terminal chatbot
- 🧠 Conversation history
- ⚡ Gemini 3.6 Flash as primary model
- 🔄 Automatic fallback to Gemini 3.5 Flash Lite when rate limit is hit
- 🏗️ Modular project structure
- 🔐 Secure API keys using environment variables
- 🖥️ Simple and lightweight CLI (for now ..)

---

## 🚀 Demo

```text
Jarvis is online.
Type /exit to quit.

> hello

Jarvis:
Hello! How can I help you today?

> write a binary search in python

Jarvis:
def binary_search(arr, target):
    ...
```

---

## 📂 Project Structure

```text
jarvis/
│
├── chats/             # Chat history (future)
├── config.py          # Configuration
├── main.py            # Main application
├── providers.py       # Gemini providers (primary + fallback)
├── requirements.txt
└── README.md
```

---

## 🛠️ Installation

Clone the repository

```bash
git clone git@github.com:AsH131211/jarvis.git
cd jarvis
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

### Fish

```fish
source .venv/bin/activate.fish
```

### Bash

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Fish Shell

```fish
set -Ux GEMINI_API "your_gemini_api_key"
```

Verify

```fish
echo $GEMINI_API
```

---

## ▶️ Running Jarvis

```bash
python main.py (Not fully built so for now ..)
```

Exit anytime with

```text
/exit
```

---

## 🧩 Tech Stack

- 🐍 Python
- 💎 Google Gemini API (`gemini-3.6-flash` + `gemini-3.5-flash-lite`)
- 🔧 Virtual Environment

---

## 🗺️ Roadmap

### ✅ Version 0.1
- [x] Connect to Gemini API
- [x] Single prompt chatbot

### ✅ Version 0.2
- [x] Interactive chatbot
- [x] Conversation history
- [x] Modular codebase

### ✅ Version 0.3
- [x] Dual Gemini model setup
- [x] Streaming responses
- [x] Automatic fallback (3.6 Flash → 3.5 Flash Lite on rate limit)

### 🚧 Version 0.4
- [x] Context Manager
- [x] Sliding context window
- [x] Persistent chat history

### 🚀 Version 1.0
- [ ] Memory Manager
- [ ] Rich terminal UI
- [ ] Chat sessions
- [ ] Command system
- [ ] Tool calling
- [ ] Local LLM (Ollama)

---

## 🎯 Project Goals

This project is being built to understand how production AI assistants actually work.

Topics covered include:

- Prompt Engineering
- Context Management
- Memory Systems
- Provider Abstraction
- Streaming Responses
- Tool Calling
- Retrieval-Augmented Generation (RAG)
- Local LLM Integration

---

## 🤝 Contributing

Contributions, ideas, and suggestions are always welcome.

Feel free to open an issue or submit a pull request.

---


<div align="center">

### ⭐ If you found this project interesting, consider giving it a star!

**Built with ❤️, Python, and lots of curiosity.**
**Shinzou wo Sasageyo!**

</div>
