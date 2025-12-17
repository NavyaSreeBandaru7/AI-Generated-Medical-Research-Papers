from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    index_dir: Path = Path("indexes/faiss_index")
    exports_dir: Path = Path("exports")

    # Chunking
    chunk_size: int = 1200
    chunk_overlap: int = 200

    # Retrieval
    k: int = 12
    fetch_k: int = 40
    search_type: str = "mmr"

    # Models
    embedding_model: str = "text-embedding-3-large"
    chat_model: str = "gpt-4.1-mini"
    temperature: float = 0.0

def settings() -> Settings:
    return Settings()
