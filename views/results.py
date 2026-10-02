"""views/results.py - every document you have made (read from the outputs folder)."""
import streamlit as st

from utils import nav
from utils.history import delete_run, list_runs, read_file
from utils.ui import pretty_date, sources_markdown


def render():
    st.title("Results")
    st.write("Every document you have created, newest first.")

    runs = list_runs()
    if not runs:
        st.info("Note: no documents yet. Create your first one on the New query page.",
                icon=":material/info:")
        if st.button("Go to New query", type="primary", key="results_goto_query"):
            nav.go("query")
        return

    col_s, col_f = st.columns([3, 1])
    search = col_s.text_input("Search your results", placeholder="Type a word from the question")
    formats = ["All types"] + sorted({r["format"] for r in runs})
    fmt = col_f.selectbox("Document type", formats)

    shown = [r for r in runs
             if (not search.strip() or search.lower() in r["query"].lower())
             and (fmt == "All types" or r["format"] == fmt)]

    if not shown:
        st.warning("Note: nothing matches. Clear the search or choose 'All types'.")
        return

    for run in shown:
        with st.expander(f"{run['query'][:100]}  ({pretty_date(run['created'])})"):
            st.caption(f"{run['format']} file, {run['depth']}, {run['style']}, "
                       f"about {run['words']} words, written by {run['model']}")

            try:
                data = read_file(run)
                st.download_button(f"Download {run['format']} file", data=data,
                                   file_name=run["filename"], mime=run["mime"],
                                   type="primary", key=f"dl_{run['id']}")
            except FileNotFoundError:
                st.warning("Problem: the document file is missing from the outputs folder.")

            st.markdown(run["synthesis"])
            st.markdown("**Sources used**")
            st.markdown(sources_markdown(run["sources"]))

            st.divider()
            _delete_controls(run["id"])


def _delete_controls(run_id: str):
    if st.session_state.get("confirm_delete") == run_id:
        st.warning("Warning: delete this result and its file? This cannot be undone.")
        yes, no = st.columns(2)
        if yes.button("Yes, delete", key=f"yes_{run_id}", type="primary"):
            delete_run(run_id)
            st.session_state.pop("confirm_delete", None)
            st.rerun()
        if no.button("Keep it", key=f"no_{run_id}"):
            st.session_state.pop("confirm_delete", None)
            st.rerun()
    elif st.button("Delete", key=f"del_{run_id}"):
        st.session_state["confirm_delete"] = run_id
        st.rerun()
