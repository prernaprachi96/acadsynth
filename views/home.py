"""views/home.py - the Overview page: what the app does and what to do first."""
import streamlit as st

from utils import nav
from utils.config import key_status
from utils.history import list_runs
from utils.ingestor import source_stats
from utils.ui import pretty_date

STEPS = [
    ("01", "Add your papers",
     "Upload PDF files. You can skip this and search only the web."),
    ("02", "Ask a question",
     "Type what you want to know and choose the file type you want."),
    ("03", "Download the result",
     "Get a Word, PowerPoint or Markdown file with every source listed."),
]


def render():
    st.title("AcadSynth")
    st.markdown(
        '<p class="lead">Turn your research papers into a cited summary. '
        "Add PDFs, ask a question, and download a finished document.</p>",
        unsafe_allow_html=True,
    )

    # ── The one thing to do next ─────────────────────────────────────────────
    status = key_status()
    if status == "ready":
        if st.button("Start a new query", type="primary", key="home_goto_query"):
            nav.go("query")
    else:
        if status == "missing":
            st.error("Before you start: add your Gemini key. "
                     "The app cannot write anything without it.")
        else:
            st.warning("Before you start: this app needs your own free Gemini key. "
                       "Add it in Settings.")
        if st.button("Add my key", type="primary", key="home_goto_settings"):
            nav.go("settings")

    # ── Three steps ──────────────────────────────────────────────────────────
    st.markdown('<div class="eyebrow">How it works</div>', unsafe_allow_html=True)
    for col, (num, title, text) in zip(st.columns(3), STEPS):
        with col.container(border=True):
            st.markdown(f'<div class="num">{num}</div>', unsafe_allow_html=True)
            st.markdown(f"**{title}**")
            st.write(text)

    # ── Setup status ─────────────────────────────────────────────────────────
    st.markdown('<div class="eyebrow">Your setup</div>', unsafe_allow_html=True)
    key_text = {"ready": "Ready", "own_needed": "Your own key is needed",
                "missing": "Not set"}[status]
    stats = source_stats()
    st.markdown(f"**Gemini key:** {key_text}")
    st.markdown("**PDF library:** " +
                (f"{len(stats)} PDF(s) added" if stats else "Empty (adding PDFs is optional)"))

    # ── The four agents ──────────────────────────────────────────────────────
    with st.expander("What happens when you press Create document"):
        st.markdown(
            "1. **Orchestrator** checks your setup and plans the run.\n"
            "2. **Researcher** finds the most relevant passages in your PDFs and on the web.\n"
            "3. **Synthesizer** writes a structured summary and cites every source.\n"
            "4. **Formatter** builds the file and saves it in Results."
        )

    # ── Recent documents ─────────────────────────────────────────────────────
    runs = list_runs()[:3]
    if runs:
        st.markdown('<div class="eyebrow">Recent documents</div>', unsafe_allow_html=True)
        for run in runs:
            st.markdown(f"**{run['query']}**  \n"
                        f"{pretty_date(run['created'])}, {run['format']}")
        if st.button("See all results", key="home_goto_results"):
            nav.go("results")
