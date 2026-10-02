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
from utils.researcher import NoPdfMatch, research
from utils.synthesizer import SynthesisError, synthesize

STEPS = [
    ("Orchestrator", "checking your setup and planning the run"),
    ("Researcher",   "finding sources in your PDFs and on the web"),
    ("Synthesizer",  "writing the synthesis with Gemini"),
    ("Formatter",    "building your document"),
]


class PipelineError(Exception):
    """A problem with a plain-English fix, safe to show directly."""


class PdfMismatch(PipelineError):
    """The question did not match the selected PDFs (shown as a warning)."""


def run_step(agent_name: str, query: str, config: dict, ctx: dict) -> str:
    """Run one agent. Returns a short sentence describing what it did."""

    if agent_name == "Orchestrator":
        if not find_api_key()[0]:
            raise PipelineError(
                "No Gemini API key yet. Open Settings, paste your key, and press Save key."
            )
        has_library = source_count() > 0
        if config["use_pdf"] and not has_library and not config["use_web"]:
            raise PipelineError(
                "You chose 'Only my PDFs' but your library is empty. Upload a PDF in step 1."
            )
        if config["use_pdf"] and has_library and not config["pdf_files"]:
            raise PipelineError(
                "No PDF is selected. In step 2, pick at least one PDF under 'PDFs to use', "
                "or choose 'Only the web'."
            )
        use_pdf = config["use_pdf"] and has_library
        where = []
        if use_pdf:
            where.append(f"{len(config['pdf_files'])} PDF(s)")
        if config["use_web"]:
            where.append("the web")
        return (f"Will use {' and '.join(where)}, then write in "
                f"'{config['style']}' style as a {config['format']} file.")

    if agent_name == "Researcher":
        use_pdf = config["use_pdf"] and bool(config["pdf_files"])
        try:
            result = research(query, top_k=config["top_k"], use_pdf=use_pdf,
                              use_web=config["use_web"], pdf_files=config["pdf_files"])
        except NoPdfMatch as err:
            raise PdfMismatch(
                f"Your question did not match anything in your PDF(s): {err}. "
                "Nothing was written, because the answer would not come from your documents. "
                "Try one of these: use words that appear in the PDF "
                "(for example 'What skills are listed in this resume?'), ask something general "
                "like 'Summarize this document', or choose 'Only the web' if the question "
                "is not about your PDFs."
            )
        if result["total"] == 0:
            hint = result["web_error"] or (
                "Try rewording the question or uploading a relevant PDF."
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
