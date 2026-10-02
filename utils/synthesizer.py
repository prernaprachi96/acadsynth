"""
utils/synthesizer.py
====================
The "writer" agent. Sends your question and the sources to Gemini
and gets back a cited, structured synthesis.

Uses the current `google-genai` package (the old `google-generativeai`
package is deprecated). If the chosen model is not available for your
key, it automatically tries another Flash model and tells you which.
"""

import re
import time

from utils.config import DEFAULT_MODEL, get_api_key, get_model


class SynthesisError(Exception):
    """A problem with a plain-English message that is safe to show the user."""


SYSTEM_PROMPT = """You are an academic research synthesizer for university-level work.

You are given source excerpts of two kinds: documents the user uploaded ([PDF Source n])
and web results ([Web Source n]).

Rules:
- Use only the provided excerpts. Do not invent facts or sources.
- Cite every claim with the label of its source, e.g. [PDF Source 1] or [Web Source 2].
- Paraphrase and combine ideas. Do not copy text word for word.
- If the question is general (for example "describe this" or "summarize"), describe the
  uploaded document itself: what it is, its purpose, and its main content.
- Start with "## Summary", then write 2 to 4 more sections. Every section starts with a
  markdown heading (## Heading) and has one or two flowing paragraphs (no bullet points).
- Content from the user's documents comes first. If web sources are provided, put the
  web-based material in its own section titled "## Additional context from the web".
  Use it only for background or checks that add to the document content, and keep it
  clearly separate. If no web sources are provided, do not add that section.
- If the sources do not contain enough information, say so clearly.
- Finish with "## References": a numbered list of the sources you cited, each with its
  label, title or file name, and URL if one was given.
"""

STYLE_INSTRUCTIONS = {
    "Academic / formal":
        "Use formal academic language and complete sentences.",
    "Technical summary":
        "Be concise and precise. Focus on technical details. Use direct language.",
    "Plain language":
        "Write simply so a non-expert can follow. Avoid jargon and explain technical terms.",
}


# ── Talking to Gemini ─────────────────────────────────────────────────────────

def _make_client(api_key: str):
    try:
        from google import genai
    except ImportError:
        raise SynthesisError(
            "The Gemini package is missing. In the terminal run: "
            "pip install -U google-genai"
        )
    return genai.Client(api_key=api_key)


def _is_busy(err: Exception) -> bool:
    low = str(err).lower()
    return any(w in low for w in ("503", "unavailable", "overloaded", "high demand"))


def _friendly(err: Exception) -> str:
    """Turn a raw Gemini error into something you can act on."""
    text = str(err)
    low = text.lower()
    detail = f"\n\nDetails from Gemini: {text[:250]}"
    if "api key" in low or "api_key" in low or "permission_denied" in low or "401" in low or "403" in low:
        return ("Gemini did not accept your API key. Open Settings, paste the key again "
                "(from aistudio.google.com/apikey), then press 'Check key and load models'." + detail)
    if "429" in low or "resource_exhausted" in low or "quota" in low:
        return ("You hit Gemini's free usage limit. Wait a minute and try again, "
                "or pick a different model in Settings." + detail)
    if _is_busy(err):
        return ("Gemini is overloaded right now, even after retrying other models. "
                "Wait a minute and press Create document again." + detail)
    if "timed out" in low or "connect" in low or "network" in low:
        return "Could not reach Gemini. Check your internet connection and try again." + detail
    return "Gemini returned an error." + detail


def _is_model_not_found(err: Exception) -> bool:
    low = str(err).lower()
    return "404" in low or "not_found" in low or "not found" in low


def list_models_with_client(client) -> list:
    """Model names that can write text, Flash models first."""
    names = []
    for m in client.models.list():
        actions = getattr(m, "supported_actions", None)
        if actions is not None and "generateContent" not in actions:
            continue
        names.append(m.name.replace("models/", ""))
    skip = ("image", "tts", "live", "audio", "embed", "robotics", "computer-use")
    names = [n for n in names if n.startswith("gemini") and not any(x in n for x in skip)]
    return sorted(set(names), key=lambda n: (("flash" not in n), n))


def list_models(api_key: str) -> list:
    """Used by the Settings page to show which models your key can use."""
    client = _make_client(api_key)
    try:
        return list_models_with_client(client)
    except Exception as e:
        raise SynthesisError(_friendly(e))


def _generate(client, model: str, prompt: str, system: str = None) -> str:
    from google.genai import types
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system or SYSTEM_PROMPT,
            temperature=0.3,
        ),
    )
    text = (response.text or "").strip()
    if not text:
        raise SynthesisError(
            "Gemini sent back an empty answer (a safety filter may have blocked it). "
            "Try rewording your question."
        )
    return text


# ── Planning the web search ───────────────────────────────────────────────────

PLANNER_SYSTEM = "You write short web search queries. Output only the queries, one per line."


def plan_web_queries(question: str, excerpt: str) -> list:
    """
    Ask Gemini what to look up on the web to add background to the user's PDFs.
    Returns up to 3 short queries, or [] if Gemini cannot be reached
    (the caller then falls back to a simpler search).
    """
    api_key = get_api_key()
    if not api_key:
        return []

    prompt = (
        f'A student uploaded a document and asked: "{question}"\n\n'
        f"Excerpt of the document:\n{excerpt[:6000]}\n\n"
        "Write 2 or 3 short web search queries (at most 8 words each) that would find "
        "background or up-to-date information to help answer the question: for example "
        "explanations of technologies, concepts, organisations or standards mentioned in "
        "the document.\n"
        "Rules: never include personal names, email addresses, phone numbers or street "
        "addresses. No quotation marks. One query per line. Output only the queries."
    )

    try:
        client = _make_client(api_key)
        model = get_model() or DEFAULT_MODEL
        raw = ""
        for attempt in range(2):
            try:
                raw = _generate(client, model, prompt, system=PLANNER_SYSTEM)
                break
            except Exception as err:
                if _is_busy(err) and attempt == 0:
                    time.sleep(2)
                    continue
                return []
    except Exception:
        return []

    queries = []
    for line in raw.splitlines():
        q = re.sub(r"^[\s\-\*\d\.\)]+", "", line).strip().strip("\"'`")
        if 3 <= len(q) <= 120 and q.lower() not in [x.lower() for x in queries]:
            queries.append(q)
    return queries[:3]


# ── Main function ─────────────────────────────────────────────────────────────

def _candidate_models(client, chosen: str) -> list:
    """The chosen model first, then up to two other Flash models as backups."""
    candidates = [chosen]
    try:
        for name in list_models_with_client(client):
            if name not in candidates and "flash" in name and "lite" not in name:
                candidates.append(name)
            if len(candidates) >= 3:
                break
    except Exception:
        pass
    return candidates


def synthesize(query: str, sources_text: str, style: str = "Academic / formal"):
    """
    Returns (synthesis_text, model_used).
    Retries when Gemini is busy, then tries backup models.
    Raises SynthesisError with a clear message if everything fails.
    """
    api_key = get_api_key()
    if not api_key:
        raise SynthesisError("No Gemini API key found. Add it in Settings.")

    style_note = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["Academic / formal"])
    prompt = (
        f"Research question: {query}\n\n"
        f"Writing style: {style_note}\n\n"
        f"Sources:\n{sources_text}\n\n"
        "Write the synthesis now. Cite each source by its label."
    )

    client = _make_client(api_key)
    chosen = get_model() or DEFAULT_MODEL
    last_error = None

    for model in _candidate_models(client, chosen):
        for attempt in range(3):                 # up to 3 tries per model
            try:
                return _generate(client, model, prompt), model
            except SynthesisError:
                raise
            except Exception as err:
                last_error = err
                if _is_busy(err) and attempt < 2:
                    time.sleep(2 * (attempt + 1))   # wait 2s, then 4s, then retry
                    continue
                if _is_busy(err) or _is_model_not_found(err):
                    break                          # go to the next backup model
                raise SynthesisError(_friendly(err))   # key / quota / other: stop now

    if last_error is not None and _is_model_not_found(last_error):
        raise SynthesisError(
            f"The model '{chosen}' is not available for your key. "
            "Open Settings and press 'Check key and load models' to choose one that is."
            f"\n\nDetails from Gemini: {str(last_error)[:250]}"
        )
    raise SynthesisError(_friendly(last_error) if last_error else "Gemini did not respond.")
