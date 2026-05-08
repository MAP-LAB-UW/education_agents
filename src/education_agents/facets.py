"""Load and render facet maps for prompt construction."""

from __future__ import annotations

import json
from pathlib import Path

from .schemas import FacetMap

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "facets"


def load_facet_map(topic: str) -> FacetMap:
    path = DATA_DIR / f"{topic}.json"
    with open(path) as f:
        return FacetMap.model_validate(json.load(f))


def render_facet_map_for_prompt(facet_map: FacetMap) -> str:
    lines = [f"Topic: {facet_map.topic} | Course: {facet_map.course}\n"]

    goals = [f for f in facet_map.facets if f.type == "goal"]
    problematic = [f for f in facet_map.facets if f.type == "problematic"]

    lines.append("=== Goal facets (what students SHOULD understand) ===")
    for f in goals:
        lines.append(f"  {f.id}: {f.text}")

    lines.append("\n=== Problematic facets (common misconceptions) ===")
    for f in problematic:
        lines.append(f"  {f.id}: {f.text}")

    return "\n".join(lines)


def _is_image_example(example) -> bool:
    return "@'" in example.stem or any("@'" in o.text for o in example.options)


def render_examples_for_prompt(
    facet_map: FacetMap,
    exclude_image_examples: bool = True,
) -> str:
    examples = facet_map.examples
    if exclude_image_examples:
        examples = [ex for ex in examples if not _is_image_example(ex)]

    if not examples:
        return "(No text-based examples available.)"

    parts: list[str] = []
    for i, ex in enumerate(examples, 1):
        lines = [f"--- Example {i} ---"]
        lines.append(f"Format: {ex.response_format}")
        lines.append(f"Stem: {ex.stem}\n")
        lines.append("Options:")
        for opt in ex.options:
            correct_marker = "CORRECT" if opt.is_correct else "incorrect"
            lines.append(
                f"  {opt.id}. {opt.text}  "
                f"[facets: {', '.join(opt.facet_tags)}] ({correct_marker})"
            )
        parts.append("\n".join(lines))

    return "\n\n".join(parts)
