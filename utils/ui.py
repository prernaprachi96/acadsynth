"""
utils/ui.py
===========
Tiny display helpers used by more than one page.
"""
import datetime


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
