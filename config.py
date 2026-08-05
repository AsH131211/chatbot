import os
GEMINI_API = os.environ["GEMINI_API"]

MEM_MODEL = "gemini-3.5-flash-lite"
TEMPERATURE = 0.5
MAX_TOKENS = 1024


LLAMA_URL = "http://localhost:8080/v1"
LLAMA_MODEL = "Qwen/Qwen3-8B-GGUF:Q4_K_M"
LLAMA_TEMPERATURE = 0.6

SEARXNG_URL = "http://127.0.0.1:8888"

ALLOW_LOCAL_FALLBACK = True