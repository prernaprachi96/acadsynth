"""
app.py  -  start the app with:   streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="AcadSynth",
    page_icon=":material/menu_book:",
    layout="wide",
)

from utils import nav, session             # noqa: E402
from utils.config import key_status        # noqa: E402
from views import home, query, results, settings  # noqa: E402

# ── Look and feel ────────────────────────────────────────────────────────────
# Black and white, with colour used ONLY for messages (green = success,
# red = error, amber = warning, blue = information).
# To change the fonts, edit the two names in the @import line and in the two
# font-family rules marked FONT BODY and FONT HEADINGS.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap');

    /* FONT BODY: IBM Plex Sans (falls back to Segoe UI / Calibri, the Office fonts) */
    html, body, .stApp, p, li, label, input, textarea, button, a, td, th, summary,
    [data-baseweb="select"], [data-baseweb="select"] div,
    [data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"] {
        font-family: 'IBM Plex Sans', 'Segoe UI', Calibri, Arial, sans-serif !important;
    }
    /* FONT HEADINGS: Playfair Display (falls back to Georgia) */
    h1, h2, h3, h4, .num {
        font-family: 'Playfair Display', Georgia, 'Times New Roman', serif !important;
        color: #000 !important; letter-spacing: -0.01em;
    }
    h1 { font-size: 3.1rem !important; font-weight: 700 !important; line-height: 1.1 !important; }
    h2 { font-size: 1.9rem !important; font-weight: 700 !important; }
    h3 { font-size: 1.5rem !important; font-weight: 600 !important; }
    /* keep the small built-in icons (arrows etc.) working */
    [data-testid="stIconMaterial"], .material-symbols-rounded, .material-icons {
        font-family: 'Material Symbols Rounded' !important;
    }

    /* Page */
    html, body, .stApp, [data-testid="stApp"] { background: #fff !important; color: #000 !important; }
    .block-container, [data-testid="stMainBlockContainer"] {
        max-width: 880px; padding-top: 3.5rem; line-height: 1.65; }
    footer { visibility: hidden; }

    /* Small helper styles used by the pages */
    .lead { font-size: 1.15rem; color: #1a1a1a; margin: 0.2rem 0 1.4rem 0; }
    .eyebrow { font-size: 0.74rem; letter-spacing: 0.16em; text-transform: uppercase;
               font-weight: 600; color: #1a1a1a; margin: 1.6rem 0 0.4rem 0; }
    .num { font-size: 2.4rem; font-weight: 600; line-height: 1; margin-bottom: 0.5rem; }

    /* Text that is easy to miss */
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {
        color: #262626 !important; opacity: 1 !important; }
    ::placeholder { color: #4a4a4a !important; opacity: 1 !important; }
    [data-testid="stMarkdownContainer"] a { color: #000 !important;
        text-decoration: underline; text-underline-offset: 3px; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #fff !important; border-right: 1px solid #000; }
    [data-testid="stSidebar"] * { color: #000 !important; }
    [data-testid="stSidebarNav"]::before {
        content: "AcadSynth"; display: block; padding: 1.4rem 1rem 0.6rem 1rem;
        font-family: 'Playfair Display', Georgia, serif; font-size: 1.7rem; font-weight: 700; }
    [data-testid="stSidebarNav"] a, [data-testid="stSidebarNavLink"] {
        text-decoration: none !important; border-radius: 2px !important; }
    [data-testid="stSidebarNavLink"][aria-current="page"],
    [data-testid="stSidebarNav"] a[aria-current="page"] { background: #000 !important; }
    [data-testid="stSidebarNavLink"][aria-current="page"] *,
    [data-testid="stSidebarNav"] a[aria-current="page"] * { color: #fff !important; }

    /* Cards, inputs, uploader, expanders */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #000 !important; border-radius: 2px !important;
        background: #fff !important; padding: 0.5rem 0.8rem; }
    textarea, input, [data-baseweb="select"] > div, [data-baseweb="textarea"], [data-baseweb="input"] {
        background: #fff !important; color: #000 !important;
        border: 1px solid #000 !important; border-radius: 2px !important; }
    [data-testid="stFileUploaderDropzone"] { background: #fff !important;
        border: 1px dashed #000 !important; border-radius: 2px !important; }
    [data-testid="stFileUploaderDropzone"] * { color: #000 !important; }
    [data-testid="stExpander"] { border: 1px solid #000 !important; border-radius: 2px !important;
        background: #fff !important; }
    [data-testid="stStatus"], [data-testid="stStatusWidget"] {
        border: 1px solid #000 !important; border-radius: 2px !important; background: #fff !important; }

    /* Messages: the only place where colour is used (colours come from config.toml) */
    [data-testid="stAlert"] { border-radius: 3px !important; }
    [data-testid="stAlert"] * { color: #000 !important; }
    [data-testid="stAlert"] svg { display: none !important; }   /* no icons */

    /* Buttons: main action = black with white text, the rest = white with black text */
    button[kind="primary"], [data-testid^="stBaseButton-primary"] {
        background: #000 !important; border: 1px solid #000 !important;
        border-radius: 2px !important; padding: 0.55rem 1.5rem !important;
        letter-spacing: 0.02em; }
    button[kind="primary"]:hover, [data-testid^="stBaseButton-primary"]:hover {
        background: #333 !important; }
    button[kind="primary"] *, [data-testid^="stBaseButton-primary"] * { color: #fff !important; }
    button[kind="secondary"], [data-testid^="stBaseButton-secondary"] {
        background: #fff !important; border: 1px solid #000 !important;
        border-radius: 2px !important; letter-spacing: 0.02em; }
    button[kind="secondary"] *, [data-testid^="stBaseButton-secondary"] * { color: #000 !important; }
    button:disabled { opacity: 0.4 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Pages (no icons) ─────────────────────────────────────────────────────────
nav.PAGES["home"]     = st.Page(home.render,     title="Overview",  url_path="overview", default=True)
nav.PAGES["query"]    = st.Page(query.render,    title="New query", url_path="new-query")
nav.PAGES["results"]  = st.Page(results.render,  title="Results",   url_path="results")
nav.PAGES["settings"] = st.Page(settings.render, title="Settings",  url_path="settings")

session.touch()          # keeps this visitor's files alive
session.cleanup_old()    # removes files of visitors gone for 24 hours

page = st.navigation(list(nav.PAGES.values()))

with st.sidebar:
    st.divider()
    status = key_status()
    if status == "ready":
        st.caption("Gemini key: ready")
    elif status == "own_needed":
        st.caption("Gemini key: add yours in Settings")
    else:
        st.caption("Gemini key: missing. Open Settings.")
    st.caption("DSN4091, Group 153")

page.run()
