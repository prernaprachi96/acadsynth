"""
utils/ingestor.py
=================
Builds the searchable library from your PDFs.

  PDF  ->  text  ->  chunks of ~400 words  ->  vectors  ->  ChromaDB

The database is saved in the "chroma_db" folder next to app.py,
no matter which folder you start the app from.
"""

import hashlib
from collections import Counter
from pathlib import Path

import chromadb
import fitz  # PyMuPDF

from utils.embedder import embed_texts

CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db"
COLLECTION = "academic_sources"
CHUNK_OVERLAP = 80   # words shared between neighbouring chunks

_client = None


def get_collection():
    """Connect to ChromaDB (created automatically the first time)."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


# ── Reading and chunking ──────────────────────────────────────────────────────

def read_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF held in memory."""
    text = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text.append(page.get_text())
    return "\n".join(text)


def chunk_text(text: str, chunk_size: int = 400, overlap: int = CHUNK_OVERLAP) -> list:
    """Split text into overlapping chunks of about `chunk_size` words."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()
        if len(chunk) > 50:
            chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


# ── Adding a PDF ──────────────────────────────────────────────────────────────

def ingest_pdf(file_bytes: bytes, filename: str) -> dict:
    """
    Add one PDF to the library.
    Returns {"status": "ok", "chunks": n} or {"status": "error", "message": "..."}.
    Uploading the same file name again replaces the old copy.
    """
    try:
        text = read_pdf(file_bytes)
    except Exception as e:
        return {"status": "error",
                "message": f"This file could not be opened as a PDF ({e})."}

    if not text.strip():
        return {"status": "error",
                "message": "No text found. This PDF is probably a scan (images only)."}

    chunks = chunk_text(text)
    if not chunks:
        return {"status": "error", "message": "The PDF had too little text to use."}

    collection = get_collection()

    # Replace any older copy of the same file
    collection.delete(where={"source": filename})

    ids = [
        hashlib.md5(f"{filename}::{i}::{chunk[:50]}".encode()).hexdigest()
        for i, chunk in enumerate(chunks)
    ]
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embed_texts(chunks),
        metadatas=[{"source": filename, "chunk_index": i} for i in range(len(chunks))],
    )
    return {"status": "ok", "chunks": len(chunks), "source": filename}


# ── Looking at and cleaning the library ───────────────────────────────────────

def source_stats() -> dict:
    """{ "paper.pdf": 42, ... }  (file name -> number of chunks)"""
    result = get_collection().get(include=["metadatas"])
    metas = result.get("metadatas") or []
    return dict(sorted(Counter(m["source"] for m in metas).items()))


def read_source_text(filename: str, max_words: int = 10000) -> str:
    """The whole text of one PDF (chunks put back in order, overlap removed)."""
    res = get_collection().get(where={"source": filename},
                               include=["documents", "metadatas"])
    pairs = sorted(zip(res.get("metadatas") or [], res.get("documents") or []),
                   key=lambda p: p[0].get("chunk_index", 0))
    parts = []
    for i, (_, doc) in enumerate(pairs):
        words = doc.split()
        parts.append(" ".join(words if i == 0 else words[CHUNK_OVERLAP:]))
    return " ".join(" ".join(parts).split()[:max_words])


def list_sources() -> list:
    return list(source_stats().keys())


def source_count() -> int:
    return get_collection().count()


def delete_source(filename: str):
    get_collection().delete(where={"source": filename})


def clear_library():
    collection = get_collection()
    ids = collection.get()["ids"]
    if ids:
        collection.delete(ids=ids)
