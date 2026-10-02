"""
app.py  -  start the app with:   streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="AcadSynth",
    page_icon=":material/menu_book:",
    layout="wide",
)

from utils import nav                      # noqa: E402
from utils.config import find_api_key      # noqa: E402
from views import home, query, results, settings  # noqa: E402

# Colours come from .streamlit/config.toml. This only adds a heading font
# and keeps the text column a comfortable reading width.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600;700&display=swap');
    h1, h2, h3 { font-family: 'Source Serif 4', Georgia, serif !important;
                 letter-spacing: -0.01em; }
    .block-container, [data-testid="stMainBlockContainer"] { max-width: 920px; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

nav.PAGES["home"]     = st.Page(home.render,     title="Overview",  icon=":material/home:",        url_path="overview", default=True)
nav.PAGES["query"]    = st.Page(query.render,    title="New query", icon=":material/edit_note:",   url_path="new-query")
nav.PAGES["results"]  = st.Page(results.render,  title="Results",   icon=":material/folder_open:", url_path="results")
nav.PAGES["settings"] = st.Page(settings.render, title="Settings",  icon=":material/settings:",    url_path="settings")

page = st.navigation(list(nav.PAGES.values()))

with st.sidebar:
    st.divider()
    if find_api_key()[0]:
        st.caption(":material/check_circle: Gemini key is set")
    else:
        st.caption(":material/warning: Gemini key missing. Add it in Settings.")
    st.caption("DSN4091, Group 153")

page.run()
