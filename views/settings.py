"""views/settings.py - API key, model, and your PDF library."""
import streamlit as st

from utils.config import (DEFAULT_MODEL, find_api_key, is_local_mode, key_status,
                          shared_key_limit, shared_runs_left, using_shared_key)
from utils.ingestor import clear_library, delete_source, source_stats
from utils.synthesizer import SynthesisError, list_models
from utils.ui import storage_notice


def _label(text: str):
    st.markdown(f'<div class="eyebrow">{text}</div>', unsafe_allow_html=True)


def render():
    st.title("Settings")
    st.markdown('<p class="lead">Set up your Gemini key once, then manage your PDFs.</p>',
                unsafe_allow_html=True)

    settings = st.session_state.setdefault("settings", {})

    # ── 1. API key ───────────────────────────────────────────────────────────
    with st.container(border=True):
        _label("Required")
        st.subheader("Your Gemini key")

        key, source = find_api_key()
        status = key_status()
        if status == "ready":
            st.success(f"A key is ready to use (from {source}, ends in ...{key[-4:]}).")
        elif status == "own_needed":
            if shared_key_limit() == 0:
                st.warning("The app owner's key is not shared. Paste your own key below.")
            else:
                st.warning(f"You have used all {shared_key_limit()} free documents on the "
                           "owner's key. Paste your own key below to continue.")
        else:
            st.error("No key found yet. Follow the three steps below.")

        if status == "ready" and using_shared_key() and not is_local_mode():
            st.info(f"You are using the owner's shared key. {shared_runs_left()} of "
                    f"{shared_key_limit()} free documents left. "
                    "Paste your own key to remove this limit.")

        st.markdown("**How to get a free key**")
        st.markdown(
            "1. Open **aistudio.google.com/apikey** and sign in with your Google account.\n"
            "2. Press **Create API key** and copy the key.\n"
            "3. Paste it in the box below and press **Save key**."
        )
        new_key = st.text_input("Paste your key here", type="password", key="key_input")
        if st.button("Save key", type="primary", key="save_key"):
            if new_key.strip():
                settings["api_key"] = new_key.strip()
                settings.pop("models", None)
                st.rerun()
            else:
                st.warning("The box is empty. Paste your key first.")
        st.caption("The key is kept only while this browser tab is open. "
                   "On your own computer you can store it in .streamlit/secrets.toml.")

    # ── 2. Model ─────────────────────────────────────────────────────────────
    with st.container(border=True):
        _label("Optional")
        st.subheader("Writing model")
        st.write("The default works for most people. Change it only if you see "
                 "errors about usage limits.")
        if st.button("Check my key and load models", key="load_models", disabled=not key):
            with st.spinner("Asking Gemini which models your key can use..."):
                try:
                    settings["models"] = list_models(key)
                    st.success(f"Your key works. {len(settings['models'])} models are available.")
                except SynthesisError as err:
                    st.error(str(err))

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
        _label("Optional")
        st.subheader("Your PDF library")
        if storage_notice():
            st.caption(storage_notice())
        stats = source_stats()
        if not stats:
            st.write("No PDFs yet. Add them on the New query page.")
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
