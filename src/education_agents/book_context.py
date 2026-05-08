"""Load book context for prompt augmentation."""

from __future__ import annotations

from pathlib import Path

BOOK_PATH = Path(__file__).resolve().parents[2] / "docs" / "edpsy490_ch_5.tex"


def load_book_context(mode: str, path: str | None = None) -> str | None:
    if mode == "none":
        return None

    if mode == "rag":
        raise NotImplementedError("RAG mode not implemented yet")

    if mode == "full_tex":
        p = Path(path) if path else BOOK_PATH
        return p.read_text()

    raise ValueError(f"Unknown book_context_mode: {mode!r}")
