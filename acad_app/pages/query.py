import streamlit as st
import time
from utils import agents


def render():
    st.markdown("""
    <div class='page-title'>New Query</div>
    <div class='page-subtitle'>Describe your research topic. Be specific — the more detail you give, the better the retrieval.</div>
    """, unsafe_allow_html=True)

    # ── Query form ────────────────────────────────────────────────────────────
    st.markdown("<div class='paper-card'>", unsafe_allow_html=True)

    query_text = st.text_area(
        "Research question or topic",
        placeholder="e.g. Compare transformer-based attention mechanisms with recurrent architectures for processing long documents in NLP tasks.",
        height=120,
        label_visibility="visible",
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        output_format = st.selectbox(
            "Output format",
            [".docx — Word document", ".pptx — Slide deck", ".md — Markdown"],
        )
    with col_b:
        depth = st.selectbox(
            "Research depth",
            ["Quick — 3 sources", "Standard — 7 sources", "Deep — 15+ sources"],
            index=1,
        )
    with col_c:
        style = st.selectbox(
            "Writing style",
            ["Academic / formal", "Technical summary", "Plain language"],
        )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    use_rag = st.checkbox(
        "Use RAG (retrieval-augmented generation)",
        value=True,
        help="Grounds the synthesis in retrieved source excerpts. Always recommended.",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    col_run, _ = st.columns([1, 4])
    with col_run:
        run = st.button("Run pipeline", type="primary", use_container_width=True)

    if not run:
        return

    if not query_text.strip():
        st.warning("Please enter a research topic before running.")
        return

    # ── Pipeline ──────────────────────────────────────────────────────────────
    st.markdown("<div class='warm-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-heading'>Pipeline running</div>", unsafe_allow_html=True)

    progress_ph = st.empty()
    steps = [
        ("Orchestrator", "Parsing query and building task plan"),
        ("Researcher",   "Querying vector store for relevant sources"),
        ("Synthesizer",  "Writing synthesis from retrieved excerpts"),
        ("Formatter",    "Exporting document in requested format"),
    ]
    done = []

    for i, (agent_name, desc) in enumerate(steps):
        with progress_ph.container():
            _draw_steps(steps, done, i)

        result = agents.run_step(agent_name, query_text, {
            "format": output_format,
            "depth":  depth,
            "style":  style,
            "rag":    use_rag,
        })
        done.append((agent_name, result))
        time.sleep(0.25)

    with progress_ph.container():
        _draw_steps(steps, done, len(steps))

    # ── Output ────────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.6rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-heading'>Synthesis</div>", unsafe_allow_html=True)

    synthesis = next((r for n, r in done if n == "Synthesizer"), "")
    fmt_short = output_format.split(" ")[0]

    st.markdown(f"<div class='result-box'>{synthesis}</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    dl_col, _ = st.columns([1, 4])
    with dl_col:
        st.download_button(
            label=f"Download {fmt_short}",
            data=synthesis.encode("utf-8"),
            file_name=f"synthesis{fmt_short.replace('.','_')}.txt",
            mime="text/plain",
        )
    st.caption("In the full pipeline this downloads the real formatted document.")


def _draw_steps(all_steps, done_list, current_idx):
    done_names = {n for n, _ in done_list}
    st.markdown("<div class='paper-card' style='padding:1rem 1.4rem'>",
                unsafe_allow_html=True)
    for j, (name, desc) in enumerate(all_steps):
        if name in done_names:
            dot_cls, text_color, label = "dot-done",    "#3DAA6C", f"{name} — done"
        elif j == current_idx:
            dot_cls, text_color, label = "dot-running", "#E8873A", f"{name} — {desc}…"
        else:
            dot_cls, text_color, label = "dot-wait",    "#B09070", f"{name} — waiting"

        st.markdown(f"""
        <div class='step-line'>
            <div class='step-dot {dot_cls}'></div>
            <span style='color:{text_color}; font-size:0.87rem'>{label}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
