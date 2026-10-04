"""
utils/embedder.py
=================
Converts text into a list of numbers (a "vector") so the computer can
compare meaning instead of exact words.

  "neural network training"  ->  [0.23, -0.11, 0.87, ...]  (384 numbers)
  "deep learning process"    ->  [0.21, -0.09, 0.85, ...]  (similar numbers!)

Model: all-MiniLM-L6-v2. Runs on your laptop, free. It downloads once
(about 80 MB) the first time you add a PDF, then it is cached.
"""

_model = None


def get_model():
    """Load the embedding model the first time it is needed."""
    global _model
    if _model is None:
        # Imported here so the app starts fast and the heavy library only
        # loads when you actually add or search PDFs.
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_texts(texts: list) -> list:
    """Convert a list of texts into a list of vectors (used when adding PDFs)."""
    return get_model().encode(texts, batch_size=16, show_progress_bar=False).tolist()


def embed_query(query: str) -> list:
    """Convert one question into a vector (used when searching)."""
    return embed_texts([query])[0]
