from __future__ import annotations
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from .config import settings

def build_faiss_index(docs, api_key: str, out_dir: Path | None = None):
    s = settings()
    out_dir = out_dir or s.index_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    splitter = RecursiveCharacterTextSplitter(chunk_size=s.chunk_size, chunk_overlap=s.chunk_overlap)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model=s.embedding_model, api_key=api_key)
    vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(str(out_dir))
    return vs, chunks
