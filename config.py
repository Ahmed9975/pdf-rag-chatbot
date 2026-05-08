from __future__ import annotations

import os

try:
    import torch
except Exception:  # pragma: no cover
    torch = None

APP_TITLE = "AI Study Assistant"
APP_SUBTITLE = "Chat normally, or analyze one or more uploaded PDFs with cleaner controls and a simpler workflow."

MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen3:8b")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "intfloat/multilingual-e5-large-instruct",
)

DEVICE = (
    os.getenv("EMBEDDING_DEVICE")
    or ("cuda" if torch is not None and torch.cuda.is_available() else "cpu")
)

INDEX_ROOT = os.getenv("FAISS_INDEX_ROOT", "faiss_indexes")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1024"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "128"))

DEFAULT_RETRIEVAL_K = int(os.getenv("DEFAULT_RETRIEVAL_K", "3"))
MULTI_FILE_K = int(os.getenv("MULTI_FILE_K", "2"))
MULTI_FILE_DETAILED_K = int(os.getenv("MULTI_FILE_DETAILED_K", "4"))
DETAILED_RELEVANT_K = int(os.getenv("DETAILED_RELEVANT_K", "12"))
DETAILED_OVERVIEW_CHUNKS = int(os.getenv("DETAILED_OVERVIEW_CHUNKS", "10"))
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "6"))

WELCOME_MESSAGE = """
## Welcome

- Chat normally even before uploading files.
- Upload one or more PDFs.
- Choose the active file from the sidebar.
- Switch between general chat, active PDF, or all PDFs.
- Turn on detailed mode for deeper explanations.

### Example prompts
- Explain OOP simply
- Summarize the active PDF
- Compare all files
- Explain this lecture step by step
""".strip()

QUICK_ACTIONS = [
    "Summarize the active PDF",
    "Explain this lecture step by step",
    "List uploaded files",
    "Compare all files",
]
