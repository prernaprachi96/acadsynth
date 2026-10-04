"""
utils/history.py
================
Saves every finished run to disk so the Results page is real.

Each run gets its own folder inside the outputs folder:

    <outputs>/20261001-143205/
        meta.json        question, settings, synthesis text, sources
        <the document>   the .docx / .pptx / .md file

Which outputs folder is used comes from utils/session.py: your own
"outputs/" folder in local mode, or a private folder per visitor online.
"""

import datetime
import json
import re
import shutil

from utils import session

_ID_PATTERN = re.compile(r"^\d{8}-\d{6}(-\d+)?$")


def save_run(*, query, config, synthesis, sources, file_bytes, filename, mime, model) -> str:
    base = session.outputs_dir()
    base.mkdir(parents=True, exist_ok=True)

    now = datetime.datetime.now()
    run_id = now.strftime("%Y%m%d-%H%M%S")
    n = 1
    while (base / run_id).exists():
        run_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{n}"
        n += 1

    folder = base / run_id
    folder.mkdir()
    (folder / filename).write_bytes(file_bytes)

    meta = {
        "id": run_id,
        "created": now.isoformat(timespec="seconds"),
        "query": query,
        "format": config["format"],
        "depth": config["depth_label"],
        "style": config["style"],
        "used_web": config["use_web"],
        "model": model,
        "filename": filename,
        "mime": mime,
        "words": len(synthesis.split()),
        "synthesis": synthesis,
        "sources": sources,
    }
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
    return run_id


def list_runs() -> list:
    """All saved runs, newest first."""
    base = session.outputs_dir()
    if not base.exists():
        return []
    runs = []
    for folder in sorted(base.iterdir(), reverse=True):
        meta_file = folder / "meta.json"
        if folder.is_dir() and meta_file.exists():
            try:
                runs.append(json.loads(meta_file.read_text(encoding="utf-8")))
            except Exception:
                continue  # skip a damaged entry instead of crashing the page
    return runs


def read_file(run: dict) -> bytes:
    return (session.outputs_dir() / run["id"] / run["filename"]).read_bytes()


def delete_run(run_id: str):
    if not _ID_PATTERN.match(run_id):
        return
    shutil.rmtree(session.outputs_dir() / run_id, ignore_errors=True)
