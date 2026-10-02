"""
utils/researcher.py
===================
Finds sources for a question from two places:

  1. Your uploaded PDFs (ChromaDB, searched by meaning)
  2. The web (DuckDuckGo, free, no key)

Everything is combined into one labelled text block for the Synthesizer.
The labels ("PDF Source 1", "Web Source 2") are what Gemini cites,
and the same labels are shown to you in the "Sources used" list.
"""

from utils.embedder import embed_query
from utils.ingestor import get_collection


def search_local(query: str, top_k: int = 5, min_score: float = 0.25) -> list:
    """Most relevant chunks from your PDFs. score: 1.0 = perfect match."""
    collection = get_collection()
    total = collection.count()
    if total == 0:
        return []

    results = collection.query(
        query_embeddings=[embed_query(query)],
        n_results=min(top_k, total),
        include=["documents", "metadatas", "distances"],
    )

    output = []
    for doc, meta, dist in zip(results["documents"][0],
                               results["metadatas"][0],
                               results["distances"][0]):
        score = round(1 - dist, 3)
        if score >= min_score:
            output.append({
                "text": doc,
                "source": meta.get("source", "unknown PDF"),
                "score": score,
            })
    return output


def search_web(query: str, max_results: int = 5):
    """
    Search DuckDuckGo. Returns (results, error_message).
    error_message is "" when everything worked.
    """
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS  # old package name
        except ImportError:
            return [], "Web search is not installed. Run: pip install ddgs"

    try:
        raw = DDGS().text(query[:300], max_results=max_results)
        results = []
        for r in raw or []:
            text = (r.get("body") or "").strip()
            if text:
                results.append({
                    "text": text,
                    "title": r.get("title") or "Web result",
                    "url": r.get("href") or "",
                })
        return results, ""
    except Exception as e:
        return [], f"Web search failed ({e})."


def research(query: str, top_k: int = 5, use_web: bool = True) -> dict:
    """
    Returns:
      combined   - one text block with every source, for Gemini
      sources    - list for display: {label, title, detail, url}
      total      - how many usable sources were found
      web_error  - "" or a message if web search failed
      summary    - one plain sentence for the progress display
    """
    local = search_local(query, top_k=top_k)
    web, web_error = search_web(query, max_results=top_k) if use_web else ([], "")

    parts, sources = [], []

    if local:
        parts.append("=== FROM YOUR UPLOADED DOCUMENTS ===\n")
        for i, r in enumerate(local, 1):
            label = f"PDF Source {i}"
            parts.append(f"[{label} | {r['source']}]\n{r['text']}\n")
            sources.append({"label": label, "title": r["source"],
                            "detail": f"relevance {r['score']}", "url": ""})

    if web:
        parts.append("\n=== FROM WEB SEARCH ===\n")
        for i, r in enumerate(web, 1):
            label = f"Web Source {i}"
            parts.append(f"[{label} | {r['title']} | {r['url']}]\n{r['text']}\n")
            sources.append({"label": label, "title": r["title"],
                            "detail": "", "url": r["url"]})

    summary = f"Found {len(local)} passage(s) in your PDFs and {len(web)} web result(s)."
    if web_error:
        summary += f" {web_error}"

    return {
        "combined": "\n".join(parts),
        "sources": sources,
        "total": len(local) + len(web),
        "web_error": web_error,
        "summary": summary,
    }
