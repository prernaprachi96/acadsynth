"""views/home.py - the Overview page: what the app does and what to do first."""
import streamlit as st

from utils import nav
from utils.config import find_api_key
from utils.history import list_runs
from utils.ingestor import source_stats
from utils.ui import pretty_date


def render():
    st.title("AcadSynth")
    st.write(
        "Give it your research papers and a question. It finds the relevant passages, "
        "writes a cited summary, and gives you a Word, PowerPoint or Markdown file."
    )

    # ── Setup checklist (real status, not placeholders) ──────────────────────
    with st.container(border=True):
        st.subheader("Before you start")

        key, source = find_api_key()
        if key:
            st.success(f"OK: Gemini API key is set (from {source}).", icon=":material/check_circle:")
        else:
            st.error("Problem: Gemini API key is missing. The app cannot write anything without it.",
                     icon=":material/error:")
            if st.button("Add my key in Settings", key="home_goto_settings"):
                nav.go("settings")

        stats = source_stats()
        if stats:
            st.success(f"OK: {len(stats)} PDF(s) in your library.", icon=":material/check_circle:")
        else:
            st.info("Note: no PDFs uploaded yet. That is fine: without PDFs the app searches the web.",
                    icon=":material/info:")

    if st.button("Start a new query", type="primary", key="home_goto_query"):
        nav.go("query")

    # ── How it works ─────────────────────────────────────────────────────────
    st.subheader("What happens when you press Create document")
    st.markdown(
        "1. **Orchestrator** checks your setup and plans the run.\n"
        "2. **Researcher** finds the most relevant passages in your PDFs and on the web.\n"
        "3. **Synthesizer** writes a structured summary and cites every source.\n"
        "4. **Formatter** builds the file and saves it in Results."
    )

    # ── Recent documents (read from disk) ────────────────────────────────────
    st.subheader("Recent documents")
    runs = list_runs()[:3]
    if not runs:
        st.caption("Nothing yet. Your first document will show up here.")
        return

    for run in runs:
        st.markdown(f"**{run['query']}**  \n"
                    f"{pretty_date(run['created'])}, {run['format']}")
    if st.button("See all results", key="home_goto_results"):
        nav.go("results")
