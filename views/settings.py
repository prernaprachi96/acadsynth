"""views/settings.py - API key, model, and your PDF library."""
import streamlit as st

from utils.config import (DEFAULT_MODEL, find_api_key, is_local_mode, shared_key_limit,
                          shared_runs_left, using_shared_key)
from utils.ingestor import clear_library, delete_source, source_stats
from utils.synthesizer import SynthesisError, list_models
from utils.ui import storage_notice


def render():
    st.title("Settings")
    st.write("Set up Gemini once, then manage the PDFs in your library.")

    settings = st.session_state.setdefault("settings", {})

    # ── 1. API key ───────────────────────────────────────────────────────────
    with st.container(border=True):
        st.subheader("1. Gemini API key")
        key, source = find_api_key()
        if key:
            st.success(f"OK: a key is in use (from {source}, ends in ...{key[-4:]}).",
                       icon=":material/check_circle:")
        else:
            st.error("Problem: no key found yet.", icon=":material/error:")

        if using_shared_key() and not is_local_mode():
            if shared_key_limit() == 0:
                st.info("Note: the app owner's key is not shared. Paste your own key below.")
            else:
                st.info(f"Note: you are using the app owner's shared key. "
                        f"{shared_runs_left()} of {shared_key_limit()} free documents left. "
                        "Paste your own key below to remove this limit.")
        st.caption("Get a free key at aistudio.google.com/apikey. No credit card needed.")
        new_key = st.text_input("Paste your key here", type="password", key="key_input")
        if st.button("Save key", type="primary", key="save_key"):
            if new_key.strip():
                settings["api_key"] = new_key.strip()
                settings.pop("models", None)
                st.rerun()
            else:
                st.warning("Warning: the box is empty. Paste your key first.")
        st.caption("This only lasts until you close the browser tab. To keep it, add the line "
                   "GEMINI_API_KEY = \"your-key\" to the file .streamlit/secrets.toml.")

    # ── 2. Model ─────────────────────────────────────────────────────────────
    with st.container(border=True):
        st.subheader("2. Gemini model")
        if st.button("Check key and load models", key="load_models", disabled=not key):
            with st.spinner("Asking Gemini which models your key can use..."):
                try:
                    settings["models"] = list_models(key)
                    st.success(f"OK: your key works. {len(settings['models'])} models available.")
                except SynthesisError as err:
                    st.error(f"Problem: {err}")

        options = settings.get("models") or [DEFAULT_MODEL, "gemini-2.5-flash"]
        current = settings.get("model", DEFAULT_MODEL)
        if current not in options:
            options = [current] + options
        settings["model"] = st.selectbox("Model used for writing", options,
                                         index=options.index(current), key="model_select")
        st.caption("A 'flash' model is fast and works on the free plan. If the chosen model "
                   "is not available, the app tries another flash model and tells you which.")

    # ── 3. Library ───────────────────────────────────────────────────────────
    with st.container(border=True):
        st.subheader("3. Your PDF library")
        if storage_notice():
            st.caption(storage_notice())
        stats = source_stats()
        if not stats:
            st.info("Note: no PDFs yet. Add them on the New query page.", icon=":material/info:")
        else:
            st.caption(f"{len(stats)} PDF(s), {sum(stats.values())} passages in total.")
            for name, chunks in stats.items():
                left, right = st.columns([5, 1])
                left.markdown(f"**{name}**  \n{chunks} passages")
                if right.button("Remove", key=f"rm_{name}"):
                    delete_source(name)
                    st.session_state.pop("ingest_log", None)
                    st.rerun()

            st.divider()
            sure = st.checkbox("I want to remove all PDFs from the library", key="clear_sure")
            if st.button("Remove all PDFs", disabled=not sure, key="clear_all"):
                clear_library()
                st.session_state.pop("ingest_log", None)
                st.rerun()
