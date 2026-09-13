import streamlit as st


def render():
    st.markdown("""
    <div class='page-title'>Settings</div>
    <div class='page-subtitle'>Configure your API keys, model, and output preferences.</div>
    """, unsafe_allow_html=True)

    # ── LLM ──────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-heading'>Language model</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='paper-card'>", unsafe_allow_html=True)

    provider = st.selectbox("Provider", ["OpenAI", "Anthropic", "Local (Ollama)"])

    if provider == "OpenAI":
        st.text_input("API key", type="password", placeholder="sk-…")
        st.selectbox("Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
    elif provider == "Anthropic":
        st.text_input("API key", type="password", placeholder="sk-ant-…")
        st.selectbox("Model", ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"])
    else:
        st.info("Make sure Ollama is running on http://localhost:11434")
        st.text_input("Model tag", value="llama3")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Vector DB ─────────────────────────────────────────────────────────────
    st.markdown("<div class='section-heading'>Vector database (RAG)</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='paper-card'>", unsafe_allow_html=True)

    vdb = st.selectbox("Backend", ["ChromaDB (local)", "Pinecone (cloud)"])
    if vdb == "ChromaDB (local)":
        st.text_input("Persist directory", value="./chroma_db")
        st.text_input("Collection name", value="academic_sources")
        st.caption("ChromaDB runs locally — no API key needed.")
    else:
        st.text_input("Pinecone API key", type="password")
        st.text_input("Environment", placeholder="us-east-1-aws")
        st.text_input("Index name", value="academic-synthesis")

    st.slider("Sources to retrieve (top-k)", 3, 20, 7)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Output ────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-heading'>Output</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='paper-card'>", unsafe_allow_html=True)
    st.text_input("Save files to", value="./outputs")
    c1, c2, c3 = st.columns(3)
    with c1: st.checkbox(".docx", value=True)
    with c2: st.checkbox(".pptx")
    with c3: st.checkbox(".md")
    st.markdown("</div>", unsafe_allow_html=True)

    save_col, _ = st.columns([1, 4])
    with save_col:
        if st.button("Save settings", type="primary", use_container_width=True):
            st.success("Settings saved for this session.")

    st.markdown("<div class='warm-divider'></div>", unsafe_allow_html=True)
    st.caption(
        "Store API keys in .streamlit/secrets.toml and access with st.secrets['KEY_NAME']. "
        "Never commit secrets to GitHub."
    )
