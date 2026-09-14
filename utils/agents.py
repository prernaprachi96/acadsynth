"""
utils/agents.py
All four agent functions. Currently return simulated output.
Replace each TODO with the real implementation.
"""
import time
import streamlit as st


def run_orchestrator(query, config):
    time.sleep(0.5)
    # TODO: replace with LangGraph/CrewAI graph.invoke(...)
    return f"Plan ready · agents: Researcher → Synthesizer → Formatter · top_k={config.get('depth','7').split()[2] if 'sources' not in config.get('depth','') else 7}"


def run_researcher(query, config):
    time.sleep(0.9)
    # TODO: replace with ChromaDB/Pinecone .query(query_texts=[query], n_results=top_k)
    return (
        f"Retrieved 7 sources for: \"{query[:55]}…\"\n\n"
        "Source 1 (0.91) — Vaswani et al., Attention Is All You Need\n"
        "Source 2 (0.87) — Lewis et al., Retrieval-Augmented Generation\n"
        "Source 3 (0.83) — Han et al., LLM Multi-Agent Systems\n"
        "… (4 more sources)"
    )


def run_synthesizer(query, sources, config):
    time.sleep(1.0)
    # TODO: replace with OpenAI/Anthropic chat.completions.create(...)
    return (
        f"The transformer architecture (Vaswani et al., 2017) introduced multi-head "
        f"self-attention as a replacement for recurrence, enabling full parallelism during "
        f"training and substantially improving performance on knowledge-intensive tasks. "
        f"Retrieval-augmented approaches (Lewis et al., 2020) further grounded generation "
        f"in dynamically fetched documents, reducing hallucinations. In multi-agent "
        f"frameworks (Han et al., 2024), separating retrieval, synthesis, and formatting "
        f"into specialist agents yields higher factual accuracy and adaptability across "
        f"diverse output requirements — directly addressing the goals of this pipeline."
    )


def run_formatter(synthesis, config):
    time.sleep(0.6)
    # TODO: replace with python-docx / python-pptx export
    return synthesis.encode("utf-8")


def run_step(agent_name, query, config):
    if agent_name == "Orchestrator":
        return run_orchestrator(query, config)
    elif agent_name == "Researcher":
        result = run_researcher(query, config)
        st.session_state["last_sources"] = result
        return result
    elif agent_name == "Synthesizer":
        sources = st.session_state.get("last_sources", "")
        result  = run_synthesizer(query, sources, config)
        st.session_state["last_synthesis"] = result
        return result
    elif agent_name == "Formatter":
        synthesis = st.session_state.get("last_synthesis", "")
        run_formatter(synthesis, config)
        fmt = config.get("format", ".docx").split(" ")[0]
        return f"Document exported as {fmt} and ready to download."
    return ""
