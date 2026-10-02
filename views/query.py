"""views/query.py - the main page: add papers, ask a question, get a document."""
import streamlit as st

from utils import agents, nav
from utils.config import DEPTH_OPTIONS, FORMAT_OPTIONS, STYLE_OPTIONS, find_api_key
from utils.ingestor import ingest_pdf, source_stats
from utils.ui import sources_markdown


def render():
    st.title("New query")
    st.write("Three steps: add your papers (optional), ask your question, then download the document.")

    has_key = bool(find_api_key()[0])
    if not has_key:
        st.error("Add your Gemini API key first. Without it the app cannot write the document.",
                 icon=":material/error:")
        if st.button("Go to Settings", key="query_goto_settings"):
            nav.go("settings")

    # ── Step 1: PDFs ─────────────────────────────────────────────────────────
    with st.container(border=True):
        st.subheader("1. Add your papers (optional)")
        st.caption("PDF files only. They stay on this computer. "
                   "Skip this step if you only want a web search.")
        files = st.file_uploader("PDF files", type=["pdf"], accept_multiple_files=True,
                                 label_visibility="collapsed")
        _handle_uploads(files or [])

        stats = source_stats()
        if stats:
            st.caption("In your library now: " + ", ".join(stats.keys()))
        else:
            st.caption("Your library is empty.")

    # ── Step 2: question + options ───────────────────────────────────────────
    with st.container(border=True):
        st.subheader("2. Ask your question")
        with st.form("query_form", border=False):
            question = st.text_area(
                "Your research question",
                placeholder="Example: How do transformers handle long documents compared with recurrent networks?",
                height=120,
            )
            c1, c2, c3 = st.columns(3)
            fmt = c1.selectbox("Document type", list(FORMAT_OPTIONS),
                               format_func=FORMAT_OPTIONS.get)
            depth = c2.selectbox("How much to read", list(DEPTH_OPTIONS), index=1,
                                 format_func=lambda k: DEPTH_OPTIONS[k][0],
                                 help="'Per source' means up to this many passages from your "
                                      "PDFs and up to this many results from the web.")
            style = c3.selectbox("Writing style", STYLE_OPTIONS)
            use_web = st.checkbox("Also search the web", value=True,
                                  help="Adds web results next to your PDFs. Free, no key needed.")
            submitted = st.form_submit_button("Create document", type="primary",
                                              disabled=not has_key)

    # ── Step 3: result ───────────────────────────────────────────────────────
    with st.container(border=True):
        st.subheader("3. Your document")

        if submitted:
            if len(question.strip()) < 10:
                st.warning("Write your research question in step 2 first (at least a full sentence).")
                return
            config = {
                "format": fmt,
                "depth_label": DEPTH_OPTIONS[depth][0],
                "top_k": DEPTH_OPTIONS[depth][1],
                "style": style,
                "use_web": use_web,
            }
            if not _run(question.strip(), config):
                return  # the error is already on screen

        run = st.session_state.get("last_run")
        if run:
            _show_run(run)
        else:
            st.caption("Your document will appear here after you press Create document.")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _handle_uploads(files):
    """Add each new PDF to the library once (not on every click)."""
    log = st.session_state.setdefault("ingest_log", {})
    for f in files:
        key = f"{f.name}:{f.size}"
        if key not in log:
            with st.spinner(f"Reading {f.name}. The first PDF also downloads a small language model (about 80 MB)."):
                log[key] = ingest_pdf(f.getvalue(), f.name)
        res = log[key]
        if res["status"] == "ok":
            st.success(f"{f.name}: added {res['chunks']} passages to your library.")
        else:
            st.error(f"{f.name}: {res['message']}")


def _run(question: str, config: dict) -> bool:
    """Run the four agents. Returns True if a document was made."""
    ctx = {}
    with st.status("Working on your document...", expanded=True) as status:
        for name, description in agents.STEPS:
            st.markdown(f"**{name}**: {description}...")
            try:
                message = agents.run_step(name, question, config, ctx)
            except agents.PipelineError as err:
                status.update(label=f"Stopped at the {name} step", state="error", expanded=True)
                st.error(str(err))
                return False
            except Exception as err:  # anything unexpected
                status.update(label=f"Stopped at the {name} step", state="error", expanded=True)
                st.error(f"Something unexpected went wrong in the {name} step: {err}")
                return False
            st.markdown(f":material/check: {message}")
        status.update(label="Done. Your document is ready.", state="complete", expanded=False)

    data, filename, mime = ctx["file"]
    st.session_state["last_run"] = {
        "question": question,
        "synthesis": ctx["synthesis"],
        "sources": ctx["research"]["sources"],
        "bytes": data,
        "filename": filename,
        "mime": mime,
    }
    return True


def _show_run(run: dict):
    ext = run["filename"].rsplit(".", 1)[-1].upper()
    st.download_button(f"Download {ext} file", data=run["bytes"],
                       file_name=run["filename"], mime=run["mime"],
                       type="primary", key="download_last_run")
    st.caption("Also saved in Results, so you can come back to it later.")
    st.divider()
    st.markdown(run["synthesis"])
    with st.expander("Sources used"):
        st.markdown(sources_markdown(run["sources"]))
