import streamlit as st


def render():
    st.markdown("""
    <div class='page-title'>Research Pipeline</div>
    <div class='page-subtitle'>Submit a topic. Four agents retrieve, synthesise, and format a document for you.</div>
    """, unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    def stat(col, val, label):
        col.markdown(f"""
        <div class='paper-card' style='padding:1.2rem 1.4rem; margin-bottom:0'>
            <div class='stat-number'>{val}</div>
            <div class='stat-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

    stat(c1, "12",   "queries run")
    stat(c2, "47",   "sources retrieved")
    stat(c3, "8",    "documents saved")
    stat(c4, "3.4s", "avg. pipeline time")

    st.markdown("<div class='warm-divider'></div>", unsafe_allow_html=True)

    # ── How it works ──────────────────────────────────────────────────────────
    st.markdown("<div class='section-heading'>How the pipeline works</div>",
                unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.88rem; color:#8C6A4F; margin-bottom:1.2rem; font-weight:300'>
        Each query passes through four agents in sequence.
    </div>
    """, unsafe_allow_html=True)

    pipeline = [
        ("Orchestrator",
         "Reads your query. Decides the plan — which agents to call, in what order, with what parameters."),
        ("Researcher",
         "Searches a vector database of academic sources using RAG. Returns the most relevant excerpts, ranked by similarity."),
        ("Synthesizer",
         "Reads the retrieved excerpts and writes a formal, cited academic synthesis in your chosen style."),
        ("Formatter",
         "Takes the synthesis and exports it as a .docx, .pptx, or .md file, ready to submit or share."),
    ]

    for i, (name, desc) in enumerate(pipeline):
        connector = "" if i == len(pipeline) - 1 else """
        <div style='margin-left:14px; width:1px; height:16px; background:#EDD9BC'></div>
        """
        st.markdown(f"""
        <div style='display:flex; gap:16px; align-items:flex-start'>
            <div style='margin-top:3px'>
                <div style='width:28px; height:28px; border-radius:50%;
                            background:#FDE8D0; border:1.5px solid #E8873A;
                            display:flex; align-items:center; justify-content:center;
                            font-family:Lora,serif; font-size:0.78rem; color:#A0520A;
                            font-weight:600; flex-shrink:0'>{i+1}</div>
            </div>
            <div style='padding-bottom:4px'>
                <div style='font-family:Lora,serif; font-weight:600; font-size:0.97rem;
                            color:#2C1A0E; margin-bottom:3px'>{name}</div>
                <div style='font-size:0.86rem; color:#6B4F38; line-height:1.6;
                            font-weight:300'>{desc}</div>
            </div>
        </div>
        {connector}
        """, unsafe_allow_html=True)

    st.markdown("<div class='warm-divider'></div>", unsafe_allow_html=True)

    # ── Recent queries ─────────────────────────────────────────────────────────
    st.markdown("<div class='section-heading'>Recent queries</div>",
                unsafe_allow_html=True)

    recent = [
        ("Transformer attention mechanisms vs recurrence in NLP", ".docx", "2 mins ago"),
        ("RAG vs fine-tuning — when to use each approach",        ".pptx", "1 hour ago"),
        ("LangGraph state machines for multi-agent workflows",     ".md",   "3 hours ago"),
        ("Multi-agent coordination strategies in LLM systems",    ".docx", "Yesterday"),
    ]

    for query_text, fmt, when in recent:
        st.markdown(f"""
        <div class='paper-card-white' style='padding:0.9rem 1.2rem; margin-bottom:0.6rem;
             display:flex; justify-content:space-between; align-items:center'>
            <div>
                <span style='font-size:0.9rem; color:#2C1A0E'>{query_text}</span>
                <span class='tag tag-orange' style='margin-left:10px'>{fmt}</span>
            </div>
            <div style='display:flex; align-items:center; gap:10px; flex-shrink:0'>
                <span style='font-size:0.78rem; color:#B09070'>{when}</span>
                <span class='tag tag-green'>done</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.4rem'></div>", unsafe_allow_html=True)
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("Start a new query", type="primary", use_container_width=True):
            st.rerun()
