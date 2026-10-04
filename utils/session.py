"""
utils/session.py
================
Decides WHO owns the files, so that visitors never see each other's data.

Two modes:

  Private mode (the default, used when the app is online)
    Every browser session gets its own PDF library and its own Results.
    Nothing is shared. If you refresh or reopen the page you start empty,
    and leftover files are deleted automatically after 24 hours.

  Local mode (only on your own computer)
    Switched on by putting   LOCAL_MODE = true   in .streamlit/secrets.toml
    Files are kept in the project folders chroma_db/ and outputs/ as before.
"""

import shutil
import tempfile
import time
import uuid
from pathlib import Path

import streamlit as st

from utils.config import is_local_mode

ROOT = Path(__file__).resolve().parent.parent
PRIVATE_BASE = Path(tempfile.gettempdir()) / "acadsynth"
STAMPS = PRIVATE_BASE / "sessions"       # one small file per visitor, marks "last active"
MAX_AGE_SECONDS = 24 * 3600              # delete a visitor's files after 24 hours
_last_cleanup = 0.0


def is_private() -> bool:
    return not is_local_mode()


def session_id() -> str:
    """A random id for this browser session."""
    if "sid" not in st.session_state:
        st.session_state["sid"] = uuid.uuid4().hex[:12]
    return st.session_state["sid"]


def chroma_dir() -> Path:
    return PRIVATE_BASE / "chroma" if is_private() else ROOT / "chroma_db"


def collection_name() -> str:
    return f"s_{session_id()}" if is_private() else "academic_sources"


def outputs_dir() -> Path:
    if is_private():
        return PRIVATE_BASE / "outputs" / session_id()
    return ROOT / "outputs"


def touch():
    """Mark this visitor as active (keeps their files alive)."""
    if not is_private():
        return
    STAMPS.mkdir(parents=True, exist_ok=True)
    (STAMPS / session_id()).touch()


def cleanup_old():
    """Delete the files of visitors who have been away for 24 hours. Runs at most every 30 min."""
    global _last_cleanup
    if not is_private() or time.time() - _last_cleanup < 1800:
        return
    _last_cleanup = time.time()
    if not STAMPS.exists():
        return

    for stamp in STAMPS.iterdir():
        try:
            if time.time() - stamp.stat().st_mtime < MAX_AGE_SECONDS:
                continue
            sid = stamp.name
            shutil.rmtree(PRIVATE_BASE / "outputs" / sid, ignore_errors=True)
            try:
                from utils.ingestor import get_client   # imported here to avoid a loop
                get_client().delete_collection(f"s_{sid}")
            except Exception:
                pass
            stamp.unlink(missing_ok=True)
        except Exception:
            continue
