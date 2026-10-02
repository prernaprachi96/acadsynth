"""
utils/nav.py
============
Lets any page send the user to another page with one line:

    nav.go("query")

app.py fills PAGES at the start of every run.
"""
import streamlit as st

PAGES = {}


def go(key: str):
    st.switch_page(PAGES[key])
