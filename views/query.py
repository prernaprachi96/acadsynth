"""views/query.py - the main page: add papers, ask a question, get a document."""
import streamlit as st

from utils import agents, nav
from utils.config import (DEPTH_OPTIONS, FORMAT_OPTIONS, SOURCE_HELP, SOURCE_MODES,
                          STYLE_OPTIONS, key_status)
from utils.ingestor import ingest_pdf, source_stats
from utils.ui import sources_markdown, storage_notice


def _label(text: str):
    st.markdown(f'<div class="eyebrow">{text}</div>', unsafe_allow_html=True)


def render():
    st.title("New query")
    st.markdown('<p class="lead">Follow the three steps below, from top to bottom.</p>',
                unsafe_allow_html=True)

    status = key_status()
    if status != "ready":
        if status == "missing":
            st.error("You need a Gemini key before you can create a document.")
        else:
            st.warning("You need your own free Gemini key before you can create a document.")
        if st.button("Go to Settings to add it", key="query_goto_settings"):
            nav.go("settings")

    # ── Step 1: PDFs ─────────────────────────────────────────────────────────
    with st.container(border=True):
        _label("Step 1 of 3, optional")
        st.subheader("Add your papers")
        st.write("Drop your PDF files below. Skip this step to search only the web.")
        files = st.file_uploader("PDF files", type=["pdf"], accept_multiple_files=True,
                                 label_visibility="collapsed")
        _handle_uploads(files or [])

        stats = source_stats()
        if stats:
            st.caption("In your library now: " + ", ".join(stats.keys()))
        else:
            st.caption("Your library is empty. PDF files only, up to 20 MB each.")
        if storage_notice():
            st.caption(storage_notice())

    # ── Step 2: question + options ───────────────────────────────────────────
    with st.container(border=True):
        _label("Step 2 of 3")
        st.subheader("Ask your question")
        st.write("Write your question in a full sentence, then choose where the answer "
                 "should come from.")
        with st.form("query_form", border=False):
            question = st.text_area(
                "Your question",
                placeholder="Example: What are the main findings of this paper?",
                height=110,
            )
            st.caption("Short requests such as 'Summarize this document' also work.")

            mode = st.radio(
                "Where should the answer come from?", list(SOURCE_MODES),
                format_func=SOURCE_MODES.get,
                captions=list(SOURCE_HELP.values()),
            )
            if stats:
                pdf_files = st.multiselect("Which PDFs to use", list(stats),
                                           default=list(stats))
            else:
                pdf_files = []

            fmt = st.selectbox("File type to create", list(FORMAT_OPTIONS),
                               format_func=FORMAT_OPTIONS.get)
            with st.expander("More options"):
                depth = st.selectbox(
                    "How much to read", list(DEPTH_OPTIONS), index=1,
                    format_func=lambda k: DEPTH_OPTIONS[k][0],
                    help="Up to this many passages from your PDFs and up to this many "
                         "results from the web.")
                style = st.selectbox("Writing style", STYLE_OPTIONS)

            submitted = st.form_submit_button("Create document", type="primary",
                                              disabled=(status != "ready"))

    # ── Step 3: result ───────────────────────────────────────────────────────
    with st.container(border=True):
        _label("Step 3 of 3")
        st.subheader("Your document")

        fresh = False
        if submitted:
            if len(question.strip()) < 3:
                st.warning("Write your question in step 2 first.")
                return
            config = {
                "format": fmt,
                "depth_label": DEPTH_OPTIONS[depth][0],
                "top_k": DEPTH_OPTIONS[depth][1],
                "style": style,
                "use_pdf": mode in ("both", "pdf"),
                "use_web": mode in ("both", "web"),
                "pdf_files": pdf_files,
            }
            if not _run(question.strip(), config):
                return  # the message is already on screen
            fresh = True

        run = st.session_state.get("last_run")
        if run:
            _show_run(run, fresh)
        else:
            st.write("Press **Create document** in step 2. It usually takes about a minute, "
                     "and your file will appear here.")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _handle_uploads(files):
    """Add each new PDF to the library once (not on every click)."""
    log = st.session_state.setdefault("ingest_log", {})
    for f in files:
        key = f"{f.name}:{f.size}"
        if key not in log:
            with st.spinner(f"Reading {f.name}. The first PDF also downloads a small "
                            "language model (about 80 MB)."):
                log[key] = ingest_pdf(f.getvalue(), f.name)
        res = log[key]
        if res["status"] == "ok":
            st.success(f"{f.name} was added ({res['chunks']} passages).")
            if res.get("truncated"):
                st.info(f"{f.name} is very long, so only its first {res['chunks']} "
                        "passages were added.")
        else:
            st.error(f"{f.name} could not be added. {res['message']}")


def _run(question: str, config: dict) -> bool:
    """Run the four agents. Returns True if a document was made."""
    ctx = {}
    with st.status("Working on your document...", expanded=True) as status:
        for name, description in agents.STEPS:
            st.markdown(f"**{name}**: {description}...")
            try:
                message = agents.run_step(name, question, config, ctx)
            except agents.PdfMismatch as err:
                status.update(label="Stopped: your question did not match your PDFs",
                              state="error", expanded=True)
                st.warning(str(err))
                return False
            except agents.PipelineError as err:
                status.update(label=f"Stopped at the {name} step", state="error", expanded=True)
                st.error(str(err))
                return False
            except Exception as err:  # anything unexpected
                status.update(label=f"Stopped at the {name} step", state="error", expanded=True)
                st.error(f"Something unexpected went wrong in the {name} step: {err}")
                return False
            st.markdown(f"Finished: {message}")
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


def _show_run(run: dict, fresh: bool):
    ext = run["filename"].rsplit(".", 1)[-1].upper()
    if fresh:
        st.success("Your document is ready. Download it below.")
    st.download_button(f"Download {ext} file", data=run["bytes"],
                       file_name=run["filename"], mime=run["mime"],
                       type="primary", key="download_last_run")
    st.caption("A copy is also saved on the Results page.")
    st.divider()
    st.markdown(run["synthesis"])
    with st.expander("Sources used"):
        st.markdown(sources_markdown(run["sources"]))
