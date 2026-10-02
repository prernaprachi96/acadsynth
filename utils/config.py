"""
utils/config.py
===============
Small helpers shared by every page:
  - where the Gemini API key comes from
  - which Gemini model to use
  - the choices shown in the dropdowns
"""
import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # also reads a .env file if you have one

DEFAULT_MODEL = "gemini-3.5-flash"

# Dropdown choices on the New query page
FORMAT_OPTIONS = {
    ".docx": "Word document (.docx)",
    ".pptx": "Slide deck (.pptx)",
    ".md":   "Markdown text (.md)",
}

# label shown to the user, number of passages to fetch per source type
DEPTH_OPTIONS = {
    "quick":    ("Quick (3 per source)", 3),
    "standard": ("Standard (6 per source)", 6),
    "deep":     ("Deep (10 per source)", 10),
}

STYLE_OPTIONS = ["Academic / formal", "Technical summary", "Plain language"]


def _settings() -> dict:
    return st.session_state.setdefault("settings", {})


def find_api_key():
    """
    Returns (key, where_it_came_from). Both are "" if no key is set.
    Order: typed in Settings page -> secrets.toml -> .env / environment.
    """
    typed = _settings().get("api_key", "").strip()
    if typed:
        return typed, "the Settings page"

    try:
        secret = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:
        secret = ""
    if secret:
        return secret, "secrets.toml"

    env = os.environ.get("GEMINI_API_KEY", "").strip()
    if env:
        return env, "your .env file"

    return "", ""


def get_api_key() -> str:
    return find_api_key()[0]


def get_model() -> str:
    return _settings().get("model") or DEFAULT_MODEL
