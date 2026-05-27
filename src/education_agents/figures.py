"""Execute generated figure code and capture output as base64 PNG."""

from __future__ import annotations

import base64
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from .schemas import Figure


def build_multimodal_content(text: str, figure_data: dict[str, str]) -> list[dict] | str:
    """Convert text with [FIGURE:id] placeholders into multimodal content blocks.

    Returns a plain string if there are no figure references, or a list of
    text/image_url content blocks suitable for litellm messages.
    """
    if not figure_data:
        return text

    parts: list[dict] = []
    last = 0
    for match in re.finditer(r"\[FIGURE:([^\]]+)\]", text):
        if match.start() > last:
            parts.append({"type": "text", "text": text[last:match.start()]})
        fig_id = match.group(1)
        b64 = figure_data.get(fig_id)
        if b64:
            parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}"},
            })
        else:
            parts.append({"type": "text", "text": match.group(0)})
        last = match.end()
    if last < len(text):
        parts.append({"type": "text", "text": text[last:]})

    if len(parts) == 1 and parts[0]["type"] == "text":
        return parts[0]["text"]
    return parts


def execute_figures(figures: list[Figure]) -> dict[str, str]:
    """Run each figure's Python code and return a mapping of id -> base64 PNG."""
    results: dict[str, str] = {}
    for fig in figures:
        data = _run_figure_code(fig)
        if data:
            results[fig.id] = data
    return results


def _run_figure_code(figure: Figure) -> str | None:
    """Execute a single figure's code in a subprocess, return base64 PNG or None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / f"{figure.id}.png"
        user_code = textwrap.dedent(figure.python_code)
        preamble = (
            "import matplotlib\n"
            "matplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n\n"
        )
        postamble = (
            f"\nplt.savefig({str(out_path)!r}, dpi=150, bbox_inches='tight',\n"
            f"            facecolor='white', edgecolor='none')\n"
            "plt.close('all')\n"
        )
        wrapper = preamble + user_code + postamble

        script_path = Path(tmpdir) / "run_figure.py"
        script_path.write_text(wrapper)

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=tmpdir,
        )

        if result.returncode != 0:
            print(f"[figures] {figure.id} failed: {result.stderr[:500]}")
            return None

        if not out_path.exists():
            print(f"[figures] {figure.id} produced no output file")
            return None

        return base64.b64encode(out_path.read_bytes()).decode("ascii")
