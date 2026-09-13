import streamlit as st

st.set_page_config(
    page_title="AcadSynth",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #FFFAF5;
    color: #2C1A0E;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #2C1A0E;
    border-right: none;
    padding-top: 0;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0;
}
[data-testid="stSidebar"] * {
    color: #F5DFC0 !important;
}
[data-testid="stSidebar"] .stRadio > label {
    display: none;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 2px;
    display: flex;
    flex-direction: column;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 10px 20px !important;
    border-radius: 0 !important;
    font-size: 0.9rem !important;
    font-family: 'DM Sans', sans-serif !important;
    cursor: pointer;
    transition: background 0.15s;
    border-left: 3px solid transparent !important;
    display: block;
    color: #C9A882 !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(232,135,58,0.12) !important;
    color: #F5DFC0 !important;
    border-left-color: #E8873A !important;
}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] input:checked + div + div,
[data-testid="stSidebar"] input[type="radio"]:checked ~ * {
    color: #F5DFC0 !important;
}

/* ── Main content area ── */
.main .block-container {
    padding: 2.5rem 3rem;
    max-width: 960px;
    background: #FFFAF5;
}

/* ── Page title style ── */
.page-title {
    font-family: 'Lora', serif;
    font-size: 2rem;
    font-weight: 600;
    color: #2C1A0E;
    line-height: 1.25;
    margin-bottom: 0.3rem;
}
.page-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.92rem;
    color: #8C6A4F;
    margin-bottom: 2rem;
    font-weight: 300;
}

/* ── Paper card ── */
.paper-card {
    background: #FDF3E7;
    border: 1px solid #EDD9BC;
    border-radius: 8px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
}
.paper-card-white {
    background: #ffffff;
    border: 1px solid #EDD9BC;
    border-radius: 8px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
}

/* ── Stat block ── */
.stat-number {
    font-family: 'Lora', serif;
    font-size: 2.4rem;
    font-weight: 600;
    color: #E8873A;
    line-height: 1;
}
.stat-label {
    font-size: 0.8rem;
    color: #8C6A4F;
    margin-top: 4px;
    font-weight: 400;
}

/* ── Tags / badges ── */
.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-right: 6px;
    font-family: 'DM Sans', sans-serif;
}
.tag-orange { background: #FDE8D0; color: #A0520A; }
.tag-green  { background: #D9F5E5; color: #1A6640; }
.tag-gray   { background: #F0EAE3; color: #6B4F38; }
.tag-blue   { background: #DDE9F7; color: #1A4A82; }

/* ── Result output box ── */
.result-box {
    background: #ffffff;
    border: 1px solid #EDD9BC;
    border-left: 4px solid #E8873A;
    border-radius: 0 6px 6px 0;
    padding: 1.2rem 1.4rem;
    font-family: 'Lora', serif;
    font-size: 0.95rem;
    line-height: 1.8;
    color: #2C1A0E;
    white-space: pre-wrap;
}

/* ── Step indicator ── */
.step-line {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    font-size: 0.88rem;
    color: #8C6A4F;
    border-bottom: 1px solid #F0E8DC;
}
.step-line:last-child { border-bottom: none; }
.step-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-done    { background: #3DAA6C; }
.dot-running { background: #E8873A; }
.dot-wait    { background: #D4C4B5; }

/* ── Divider ── */
.warm-divider {
    border: none;
    border-top: 1px solid #EDD9BC;
    margin: 1.8rem 0;
}

/* ── Section heading inside page ── */
.section-heading {
    font-family: 'Lora', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #2C1A0E;
    margin-bottom: 0.6rem;
    margin-top: 1.4rem;
}

/* ── Input overrides ── */
.stTextArea textarea, .stTextInput input {
    background: #ffffff !important;
    border: 1px solid #D4B896 !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #2C1A0E !important;
    font-size: 0.92rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #E8873A !important;
    box-shadow: 0 0 0 2px rgba(232,135,58,0.15) !important;
}

.stSelectbox > div > div {
    background: #ffffff !important;
    border: 1px solid #D4B896 !important;
    border-radius: 6px !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: #E8873A !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.55rem 1.4rem !important;
    font-size: 0.9rem !important;
    transition: background 0.15s !important;
}
.stButton > button[kind="primary"]:hover {
    background: #C96E22 !important;
}
.stButton > button {
    border: 1px solid #D4B896 !important;
    background: #ffffff !important;
    color: #2C1A0E !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
.stButton > button:hover {
    background: #FDF3E7 !important;
    border-color: #E8873A !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: #FDF3E7 !important;
    border: 1px solid #D4B896 !important;
    color: #A0520A !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
}

/* ── Checkbox ── */
.stCheckbox label {
    font-family: 'DM Sans', sans-serif !important;
    color: #2C1A0E !important;
    font-size: 0.9rem !important;
}

/* ── Slider ── */
.stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
    background: #E8873A !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important;
    color: #2C1A0E !important;
    background: #FDF3E7 !important;
    border: 1px solid #EDD9BC !important;
    border-radius: 6px !important;
}
.streamlit-expanderContent {
    background: #ffffff !important;
    border: 1px solid #EDD9BC !important;
    border-top: none !important;
    border-radius: 0 0 6px 6px !important;
}

/* ── Caption / small text ── */
.stCaption {
    color: #8C6A4F !important;
    font-size: 0.8rem !important;
}

/* ── Success / info / warning ── */
.stSuccess {
    background: #D9F5E5 !important;
    border: 1px solid #A8DFC0 !important;
    color: #1A6640 !important;
    border-radius: 6px !important;
}
.stInfo {
    background: #FDF3E7 !important;
    border: 1px solid #EDD9BC !important;
    color: #6B4F38 !important;
    border-radius: 6px !important;
}
.stWarning {
    background: #FFF3CD !important;
    border-color: #F0C040 !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 28px 20px 20px 20px; border-bottom: 1px solid #3D2810;'>
        <div style='font-family: Lora, serif; font-size: 1.35rem; font-weight: 600;
                    color: #F5DFC0; letter-spacing: -0.3px;'>AcadSynth</div>
        <div style='font-size: 0.75rem; color: #7A5C44; margin-top: 4px;
                    font-family: DM Sans, sans-serif;'>Multi-Agent Research Pipeline</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    page = st.radio(
        "nav",
        ["Home", "New Query", "My Results", "Settings"],
        label_visibility="collapsed",
        format_func=lambda x: {
            "Home":       "  Overview",
            "New Query":  "  New Query",
            "My Results": "  Results",
            "Settings":   "  Settings",
        }[x]
    )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding: 0 20px; border-top: 1px solid #3D2810; padding-top: 20px;'>
        <div style='font-size: 0.72rem; color: #5A3E2B; margin-bottom: 10px;
                    font-family: DM Sans, sans-serif; text-transform: none; letter-spacing: 0;'>
            Agent status
        </div>
    """, unsafe_allow_html=True)

    for name, active in [("Orchestrator", True), ("Researcher", False),
                          ("Synthesizer", False), ("Formatter", False)]:
        dot = "#3DAA6C" if active else "#4A3020"
        label_color = "#C9A882" if active else "#5A3E2B"
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:8px; margin-bottom:7px'>
            <div style='width:7px; height:7px; border-radius:50%; background:{dot};
                        flex-shrink:0'></div>
            <span style='font-size:0.78rem; color:{label_color};
                         font-family: DM Sans, sans-serif'>{name}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='position:fixed; bottom:20px; left:0; width:230px; padding:0 20px;'>
        <div style='font-size:0.7rem; color:#3D2810; font-family: DM Sans, sans-serif;'>
            DSN4091 · Group 153
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Page routing ──────────────────────────────────────────────────────────────
if page == "Home":
    from pages import home
    home.render()
elif page == "New Query":
    from pages import query
    query.render()
elif page == "My Results":
    from pages import results
    results.render()
elif page == "Settings":
    from pages import settings
    settings.render()
