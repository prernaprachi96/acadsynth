"""
utils/researcher.py
===================
Finds sources for a question from two places:

  1. Your uploaded PDFs (ChromaDB)
  2. The web (DuckDuckGo, free, no key)

How it works:
  - PDFs come first. A specific question searches the PDFs by meaning.
    A vague one ("describe this", "summarize") reads the whole PDF instead.
  - If the question matches nothing in your PDFs, it STOPS with a warning
    (NoPdfMatch) instead of quietly answering from the web.
  - The web is then searched using topics taken from your PDF content, so the
    final report can add background that the PDF itself does not explain.

Labels like "PDF Source 1" and "Web Source 2" are what Gemini cites, and the
same labels appear in the "Sources used" list.
"""

from utils.embedder import embed_query
from utils.ingestor import get_collection, read_source_text
from utils.synthesizer import plan_web_queries


class NoPdfMatch(Exception):
    """PDFs were selected but nothing in them matched the question."""


# ── Is the question too vague to search by meaning? ──────────────────────────

_VAGUE_WORDS = {"this", "these", "it", "document", "resume", "cv", "paper",
                "pdf", "file", "report"}
_VAGUE_STARTS = ("summar", "describe", "overview", "explain")


def is_vague(query: str) -> bool:
    """'describe this', 'summarize', 'what is this paper about' -> True"""
    words = [w.strip(".,?!;:()\"'").lower() for w in query.split()]
    words = [w for w in words if w]
    if len(words) <= 4:
        return True
    if len(words) <= 12:
        return any(w in _VAGUE_WORDS or w.startswith(_VAGUE_STARTS) for w in words)
    return False


# ── PDF search ───────────────────────────────────────────────────────────────

def search_local(query: str, top_k: int = 5, files: list = None,
                 min_score: float = 0.25) -> list:
    """Most relevant chunks from the chosen PDFs. score: 1.0 = perfect match."""
    collection = get_collection()
    where = {"source": {"$in": list(files)}} if files else None
    matching = len(collection.get(where=where)["ids"])
    if matching == 0:
        return []

    results = collection.query(
        query_embeddings=[embed_query(query)],
        n_results=min(top_k, matching),
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    for doc, meta, dist in zip(results["documents"][0],
                               results["metadatas"][0],
                               results["distances"][0]):
        score = round(1 - dist, 3)
        if score >= min_score:
            output.append({"text": doc,
                           "source": meta.get("source", "unknown PDF"),
                           "score": score, "whole": False})
    return output


# ── Web search ───────────────────────────────────────────────────────────────

def search_web(query: str, max_results: int = 5):
    """Search DuckDuckGo. Returns (results, error_message). "" means no error."""
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
                results.append({"text": text,
                                "title": r.get("title") or "Web result",
                                "url": r.get("href") or ""})
        return results, ""
    except Exception as e:
        return [], f"Web search failed ({e})."


# ── Main function ────────────────────────────────────────────────────────────

def research(query: str, top_k: int = 5, use_pdf: bool = True,
             use_web: bool = True, pdf_files: list = None) -> dict:
    """
    Returns:
      combined  - one text block with every source, for Gemini
      sources   - list for display: {label, title, detail, url}
      total     - how many usable sources were found
      web_error - "" or a message if web search failed
      queries   - the web searches that were run
      summary   - one plain sentence for the progress display
    Raises NoPdfMatch if PDFs were selected but nothing in them matched.
    """
    pdf_files = list(pdf_files or [])
    local, local_note = [], "not used"

    # 1. PDFs first
    if use_pdf and pdf_files:
        if is_vague(query):
            for name in pdf_files:
                text = read_source_text(name)
                if text.strip():
                    local.append({"text": text, "source": name,
                                  "score": None, "whole": True})
            local_note = f"read {len(local)} whole PDF(s)"
        else:
            local = search_local(query, top_k=top_k, files=pdf_files)
            local_note = f"{len(local)} matching passage(s)"
        if not local:
            raise NoPdfMatch(", ".join(pdf_files))

    # 2. Web, guided by what the PDFs are about
    web, web_error, queries, web_note = [], "", [], ""
    if use_web:
        if local:
            excerpt = " ".join(" ".join(r["text"].split()[:700]) for r in local[:3])
            queries = plan_web_queries(query, excerpt)
            if not queries:
                if not is_vague(query):
                    queries = [query]
                else:
                    web_note = " Web search skipped: could not decide what to search for."
        else:
            queries = [query]

        if queries:
            per_query = max(2, -(-top_k // len(queries)))   # round up
            seen = set()
            for q in queries:
                found, err = search_web(q, max_results=per_query)
                web_error = web_error or err
                for r in found:
                    key = r["url"] or r["title"]
                    if key not in seen:
                        seen.add(key)
                        web.append(r)
            web = web[: top_k + 2]

    # 3. Put everything together
    parts, sources = [], []

    if local:
        parts.append("=== FROM YOUR UPLOADED DOCUMENTS ===\n")
        for i, r in enumerate(local, 1):
            label = f"PDF Source {i}"
            if r["whole"]:
                parts.append(f"[{label} | {r['source']} | whole document]\n{r['text']}\n")
                detail = "whole document"
            else:
                parts.append(f"[{label} | {r['source']}]\n{r['text']}\n")
                detail = f"relevance {r['score']}"
            sources.append({"label": label, "title": r["source"],
                            "detail": detail, "url": ""})

    if web:
        parts.append("\n=== FROM WEB SEARCH ===\n")
        for i, r in enumerate(web, 1):
            label = f"Web Source {i}"
            parts.append(f"[{label} | {r['title']} | {r['url']}]\n{r['text']}\n")
            sources.append({"label": label, "title": r["title"],
                            "detail": "", "url": r["url"]})

    summary = f"PDFs: {local_note}. Web: {len(web)} result(s)."
    if queries:
        summary += " Searched for: " + "; ".join(queries) + "."
    summary += web_note
    if web_error:
        summary += f" {web_error}"

    return {
        "combined": "\n".join(parts),
        "sources": sources,
        "total": len(local) + len(web),
        "web_error": web_error,
        "queries": queries,
        "summary": summary,
    }
