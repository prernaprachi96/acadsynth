"""
utils/ui.py
===========
Tiny display helpers used by more than one page.
"""
import datetime

from utils import session


def sources_markdown(sources: list) -> str:
    """Turn the list of sources into a readable markdown list."""
    if not sources:
        return "_No sources were recorded._"
    lines = []
    for s in sources:
        line = f"- **{s['label']}**: {s['title']}"
        if s.get("detail"):
            line += f" ({s['detail']})"
        if s.get("url"):
            line += f"  \n  {s['url']}"
        lines.append(line)
    return "\n".join(lines)


def pretty_date(iso: str) -> str:
    try:
        return datetime.datetime.fromisoformat(iso).strftime("%d %b %Y, %H:%M")
    except Exception:
        return iso


def storage_notice() -> str:
    """One sentence about where your files are kept ("" on your own computer)."""
    if session.is_private():
        return ("Private mode: your PDFs and documents can only be seen in this browser session. "
                "If you refresh or reopen the page, you start empty, and leftovers are deleted "
                "after 24 hours. Download what you want to keep.")
    return ""
