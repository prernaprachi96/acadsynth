"""
utils/history.py
================
Saves every finished run to disk so the Results page is real.

Each run gets its own folder inside "outputs/" (next to app.py):

    outputs/20261001-143205/
        meta.json        question, settings, synthesis text, sources
        <the document>   the .docx / .pptx / .md file
"""

import datetime
import json
import re
import shutil
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
_ID_PATTERN = re.compile(r"^\d{8}-\d{6}(-\d+)?$")


def save_run(*, query, config, synthesis, sources, file_bytes, filename, mime, model) -> str:
    OUTPUT_DIR.mkdir(exist_ok=True)

    now = datetime.datetime.now()
    run_id = now.strftime("%Y%m%d-%H%M%S")
    n = 1
    while (OUTPUT_DIR / run_id).exists():
        run_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{n}"
        n += 1

    folder = OUTPUT_DIR / run_id
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
    if not OUTPUT_DIR.exists():
        return []
    runs = []
    for folder in sorted(OUTPUT_DIR.iterdir(), reverse=True):
        meta_file = folder / "meta.json"
        if folder.is_dir() and meta_file.exists():
            try:
                runs.append(json.loads(meta_file.read_text(encoding="utf-8")))
            except Exception:
                continue  # skip a damaged entry instead of crashing the page
    return runs


def read_file(run: dict) -> bytes:
    return (OUTPUT_DIR / run["id"] / run["filename"]).read_bytes()


def delete_run(run_id: str):
    if not _ID_PATTERN.match(run_id):
        return
    shutil.rmtree(OUTPUT_DIR / run_id, ignore_errors=True)
