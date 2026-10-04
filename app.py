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
from utils.config import find_api_key      # noqa: E402
from views import home, query, results, settings  # noqa: E402

# Colours come from .streamlit/config.toml. This CSS only makes sure that
# everything is pure black on white with clearly visible text.
st.markdown(
    """
    <style>
    h1, h2, h3 { font-family: Georgia, 'Times New Roman', serif !important;
                 letter-spacing: -0.01em; color: #000 !important; }
    .block-container, [data-testid="stMainBlockContainer"] { max-width: 920px; }
    footer { visibility: hidden; }

    /* Page and sidebar */
    html, body, .stApp, [data-testid="stApp"] { background: #fff !important; color: #000 !important; }
    [data-testid="stSidebar"] { background: #fff !important; border-right: 2px solid #000; }
    [data-testid="stSidebar"] * { color: #000 !important; }
    [data-testid="stSidebarNavLink"][aria-current="page"],
    [data-testid="stSidebarNav"] a[aria-current="page"] { background: #000 !important; }
    [data-testid="stSidebarNavLink"][aria-current="page"] *,
    [data-testid="stSidebarNav"] a[aria-current="page"] * { color: #fff !important; }

    /* Text that is easy to miss: captions, hints, placeholders */
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {
        color: #1a1a1a !important; opacity: 1 !important; }
    ::placeholder { color: #444 !important; opacity: 1 !important; }
    a { color: #000 !important; text-decoration: underline !important; }

    /* Cards, inputs, uploader */
    [data-testid="stVerticalBlockBorderWrapper"] { border: 1.5px solid #000 !important; background: #fff !important; }
    textarea, input, [data-baseweb="select"] > div, [data-baseweb="textarea"], [data-baseweb="input"] {
        background: #fff !important; color: #000 !important; border: 1.5px solid #000 !important; }
    [data-testid="stFileUploaderDropzone"] { background: #fff !important; border: 1.5px dashed #000 !important; }
    [data-testid="stFileUploaderDropzone"] * { color: #000 !important; }
    [data-testid="stExpander"] { border: 1.5px solid #000 !important; background: #fff !important; }
    [data-testid="stStatus"], [data-testid="stStatusWidget"] { border: 1.5px solid #000 !important; background: #fff !important; }

    /* Messages (success / error / warning / info): white box, black border, black text */
    [data-testid="stAlert"] { background: #fff !important; border: 2px solid #000 !important; }
    [data-testid="stAlertContainer"] { background: transparent !important; }
    [data-testid="stAlert"] * { color: #000 !important; }

    /* Buttons: main action = black with white text, others = white with black text */
    button[kind="primary"], [data-testid^="stBaseButton-primary"] {
        background: #000 !important; border: 2px solid #000 !important; }
    button[kind="primary"] *, [data-testid^="stBaseButton-primary"] * { color: #fff !important; }
    button[kind="secondary"], [data-testid^="stBaseButton-secondary"] {
        background: #fff !important; border: 2px solid #000 !important; }
    button[kind="secondary"] *, [data-testid^="stBaseButton-secondary"] * { color: #000 !important; }
    button:disabled { opacity: 0.45 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

nav.PAGES["home"]     = st.Page(home.render,     title="Overview",  icon=":material/home:",        url_path="overview", default=True)
nav.PAGES["query"]    = st.Page(query.render,    title="New query", icon=":material/edit_note:",   url_path="new-query")
nav.PAGES["results"]  = st.Page(results.render,  title="Results",   icon=":material/folder_open:", url_path="results")
nav.PAGES["settings"] = st.Page(settings.render, title="Settings",  icon=":material/settings:",    url_path="settings")

session.touch()          # keeps this visitor's files alive
session.cleanup_old()    # removes files of visitors gone for 24 hours

page = st.navigation(list(nav.PAGES.values()))

with st.sidebar:
    st.divider()
    if find_api_key()[0]:
        st.caption(":material/check_circle: Gemini key is set")
    else:
        st.caption(":material/warning: Gemini key missing. Add it in Settings.")
    st.caption("DSN4091, Group 153")

page.run()
