"""
utils/synthesizer.py
====================
The "writer" agent. Sends your question and the sources to Gemini
and gets back a cited, structured synthesis.

Uses the current `google-genai` package (the old `google-generativeai`
package is deprecated). If the chosen model is not available for your
key, it automatically tries another Flash model and tells you which.
"""

from utils.config import DEFAULT_MODEL, get_api_key, get_model


class SynthesisError(Exception):
    """A problem with a plain-English message that is safe to show the user."""


SYSTEM_PROMPT = """You are an academic research synthesizer for university-level work.

Rules:
- Use only the provided source excerpts. Do not invent facts or sources.
- Cite every claim with the label of the source, e.g. [PDF Source 1] or [Web Source 2].
- Paraphrase and combine ideas. Do not copy text word for word.
- Structure the answer with 3 to 5 short sections. Start each section with a markdown
  heading (## Heading), e.g. Overview, Key findings, Open questions.
- Under each heading write one or two flowing paragraphs (no bullet points).
- If the sources do not contain enough information, say so clearly.
- Finish with a "## References" section: a numbered list of the sources you cited,
  each with its label, title or file name, and URL if one was given.
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


def _friendly(err: Exception) -> str:
    """Turn a raw Gemini error into something you can act on."""
    text = str(err)
    low = text.lower()
    if "api key" in low or "api_key" in low or "permission_denied" in low or "401" in low or "403" in low:
        return ("Gemini did not accept your API key. Open Settings, paste the key again "
                "(from aistudio.google.com/apikey), then press 'Check key and load models'.")
    if "429" in low or "resource_exhausted" in low or "quota" in low:
        return ("You hit Gemini's free usage limit. Wait a minute and try again, "
                "or pick a different model in Settings.")
    if "503" in low or "unavailable" in low or "overloaded" in low:
        return "Gemini is busy right now. Wait a moment and press Create document again."
    if "timed out" in low or "connect" in low or "network" in low:
        return "Could not reach Gemini. Check your internet connection and try again."
    return f"Gemini returned an error: {text[:300]}"


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


def _pick_fallback(client, tried: str):
    try:
        names = list_models_with_client(client)
    except Exception:
        return None
    for n in names:
        if n != tried and "flash" in n and "lite" not in n:
            return n
    return None


def _generate(client, model: str, prompt: str) -> str:
    from google.genai import types
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
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


# ── Main function ─────────────────────────────────────────────────────────────

def synthesize(query: str, sources_text: str, style: str = "Academic / formal"):
    """
    Returns (synthesis_text, model_used).
    Raises SynthesisError with a clear message if something goes wrong.
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
    model = get_model() or DEFAULT_MODEL

    try:
        return _generate(client, model, prompt), model
    except SynthesisError:
        raise
    except Exception as first_error:
        if _is_model_not_found(first_error):
            alt = _pick_fallback(client, model)
            if alt:
                try:
                    return _generate(client, alt, prompt), alt
                except SynthesisError:
                    raise
                except Exception as second_error:
                    raise SynthesisError(_friendly(second_error))
            raise SynthesisError(
                f"The model '{model}' is not available for your key. "
                "Open Settings and press 'Check key and load models' to choose one that is."
            )
        raise SynthesisError(_friendly(first_error))
