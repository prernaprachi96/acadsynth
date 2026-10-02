"""
utils/agents.py
===============
The four agents, run one after another by the New query page.

  1. Orchestrator - checks your setup and plans the run
  2. Researcher   - finds sources in your PDFs and on the web
  3. Synthesizer  - writes the cited synthesis with Gemini
  4. Formatter    - builds the file and saves it to Results

Each step shares a dictionary called `ctx` so the next step can use
the previous step's output. If something is wrong, a step raises
PipelineError with a message that tells you how to fix it.
"""

from utils.config import find_api_key
from utils.formatter import format_output
from utils.history import save_run
from utils.ingestor import source_count
from utils.researcher import research
from utils.synthesizer import SynthesisError, synthesize

STEPS = [
    ("Orchestrator", "checking your setup and planning the run"),
    ("Researcher",   "finding sources in your PDFs and on the web"),
    ("Synthesizer",  "writing the synthesis with Gemini"),
    ("Formatter",    "building your document"),
]


class PipelineError(Exception):
    """A problem with a plain-English fix, safe to show directly."""


def run_step(agent_name: str, query: str, config: dict, ctx: dict) -> str:
    """Run one agent. Returns a short sentence describing what it did."""

    if agent_name == "Orchestrator":
        if not find_api_key()[0]:
            raise PipelineError(
                "No Gemini API key yet. Open Settings, paste your key, and press Save key."
            )
        n_chunks = source_count()
        if n_chunks == 0 and not config["use_web"]:
            raise PipelineError(
                "There is nothing to search. Upload a PDF in step 1, "
                "or tick 'Also search the web' in step 2."
            )
        where = []
        if n_chunks:
            where.append("your PDFs")
        if config["use_web"]:
            where.append("the web")
        return (f"Will search {' and '.join(where)}, then write in "
                f"'{config['style']}' style as a {config['format']} file.")

    if agent_name == "Researcher":
        result = research(query, top_k=config["top_k"], use_web=config["use_web"])
        if result["total"] == 0:
            hint = result["web_error"] or (
                "Try rewording the question, uploading a relevant PDF, "
                "or ticking 'Also search the web'."
            )
            raise PipelineError(f"No usable sources were found. {hint}")
        ctx["research"] = result
        return result["summary"]

    if agent_name == "Synthesizer":
        try:
            text, model = synthesize(query, ctx["research"]["combined"], config["style"])
        except SynthesisError as err:
            raise PipelineError(str(err))
        ctx["synthesis"] = text
        ctx["model"] = model
        return f"Wrote {len(text.split())} words using {model}."

    if agent_name == "Formatter":
        file_bytes, filename, mime = format_output(query, ctx["synthesis"], config["format"])
        ctx["file"] = (file_bytes, filename, mime)
        ctx["run_id"] = save_run(
            query=query, config=config, synthesis=ctx["synthesis"],
            sources=ctx["research"]["sources"], file_bytes=file_bytes,
            filename=filename, mime=mime, model=ctx["model"],
        )
        return f"Saved {filename}. It is also in Results."

    raise PipelineError(f"Unknown step: {agent_name}")
