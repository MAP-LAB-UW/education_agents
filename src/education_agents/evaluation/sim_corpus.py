"""Build a unified item corpus for the student simulator and group it by
misconception facet set.

Pulls items from two sources into one normalized shape (`SimItem`):
  - generated `RunArtifact` JSONs under outputs/* directories
  - expert `Example`s in a facet map (data/facets/<topic>.json)

`build_persona_trials` then derives, for every incorrect option, the
misconception facet set it is keyed to and groups the resulting trials by that
set — the "facet selections" the simulator is evaluated against.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from ..facets import _is_image_example
from ..schemas import FacetMap, RunArtifact

REPO_ROOT = Path(__file__).resolve().parents[3]

# Default generated-item corpora (relative to repo root).
DEFAULT_GENERATED_DIRS = [
    "outputs/sonnet-4-6-prompt-with-images",
    "outputs/gemini-flash-prompt-with-images",
    "outputs/third_pass_sonnet-4-6",
    "outputs/third_pass_no_books",
    "outputs/third_pass_with_edpsy",
]


# ── Normalized item shape ────────────────────────────────────────────────────

class SimOption(BaseModel):
    id: str
    text: str
    facet_tags: list[str]
    is_correct: bool


class SimItem(BaseModel):
    source: str
    stem: str
    response_format: str
    options: list[SimOption]
    figure_data: dict[str, str] = {}


# ── Loaders ──────────────────────────────────────────────────────────────────

def _resolve(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else REPO_ROOT / p


def load_generated(dirs: list[str | Path] | None = None) -> list[SimItem]:
    """Load generated items from RunArtifact JSON directories."""
    dirs = dirs or DEFAULT_GENERATED_DIRS
    items: list[SimItem] = []
    for d in dirs:
        dir_path = _resolve(d)
        if not dir_path.is_dir():
            continue
        for p in sorted(dir_path.glob("*.json")):
            artifact = RunArtifact.model_validate(json.loads(p.read_text()))
            it = artifact.item
            items.append(
                SimItem(
                    source=f"{dir_path.name}/{p.stem}",
                    stem=it.stem,
                    response_format=it.response_format,
                    options=[
                        SimOption(
                            id=o.id,
                            text=o.text,
                            facet_tags=o.facet_tags,
                            is_correct=o.is_correct,
                        )
                        for o in it.options
                    ],
                    figure_data=artifact.figure_data or {},
                )
            )
    return items


def load_experts(
    facet_map: FacetMap,
    exclude_images: bool = True,
) -> list[SimItem]:
    """Load expert-authored examples from a facet map."""
    items: list[SimItem] = []
    for i, ex in enumerate(facet_map.examples, 1):
        if exclude_images and _is_image_example(ex):
            continue
        items.append(
            SimItem(
                source=f"expert_{i}",
                stem=ex.stem,
                response_format=ex.response_format,
                options=[
                    SimOption(
                        id=o.id,
                        text=o.text,
                        facet_tags=o.facet_tags,
                        is_correct=o.is_correct,
                    )
                    for o in ex.options
                ],
                figure_data={},
            )
        )
    return items


def load_corpus(
    facet_map: FacetMap,
    dirs: list[str | Path] | None = None,
    include_experts: bool = True,
    exclude_expert_images: bool = True,
) -> list[SimItem]:
    """Load generated + expert items into one normalized corpus."""
    items = load_generated(dirs)
    if include_experts:
        items += load_experts(facet_map, exclude_images=exclude_expert_images)
    return items


# ── Misconception grouping ───────────────────────────────────────────────────

class Trial(BaseModel):
    """One (item, target option, misconception set) the simulator is run on."""
    group_key: str
    persona_facets: list[str]
    item: SimItem
    target_option_id: str


def problematic_ids(facet_map: FacetMap) -> set[str]:
    return {f.id for f in facet_map.facets if f.type == "problematic"}


def build_persona_trials(
    items: list[SimItem],
    facet_map: FacetMap,
) -> dict[str, list[Trial]]:
    """Group items by the misconception facet set keyed to each incorrect option.

    For every incorrect option, the misconception set is its facet_tags filtered
    to problematic (B-prefix) facets. Options with no misconception tag yield no
    trial. Returns {group_key: [Trial, ...]}.
    """
    bad = problematic_ids(facet_map)
    groups: dict[str, list[Trial]] = {}
    for item in items:
        for o in item.options:
            if o.is_correct:
                continue
            m = sorted(t for t in o.facet_tags if t in bad)
            if not m:
                continue
            key = "+".join(m)
            groups.setdefault(key, []).append(
                Trial(
                    group_key=key,
                    persona_facets=m,
                    item=item,
                    target_option_id=o.id,
                )
            )
    return groups


def coverage_summary(groups: dict[str, list[Trial]]) -> str:
    """Human-readable group -> (#trials, #distinct items) table."""
    lines = ["Misconception group         #trials  #items"]
    lines.append("-" * 44)
    for key in sorted(groups, key=lambda k: (-len(groups[k]), k)):
        trials = groups[key]
        n_items = len({t.item.source for t in trials})
        lines.append(f"{key:26s}  {len(trials):>6d}  {n_items:>6d}")
    total_trials = sum(len(v) for v in groups.values())
    lines.append("-" * 44)
    lines.append(f"{len(groups)} groups, {total_trials} trials total")
    return "\n".join(lines)
