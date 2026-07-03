"""Persona bank: two-stage persona instantiation for the student simulator.

Stage 1 (this module): for each misconception facet set, a strong model (Claude
by default) expands the canonical facet text into a fuller student knowledge
state written in the student's own voice — concept explanation, operational
rules of thumb, and a worked example — deliberately avoiding the canonical
wording the generator saw. Records are cached to a JSON file so each persona is
generated once and reused across runs.

Stage 2 (sim_v2.run_open_student) answers items from that knowledge state, so
the simulator can't lexically match the facet text against option text.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from pydantic import BaseModel

from ..llm import structured_complete
from ..schemas import FacetMap

REPO_ROOT = Path(__file__).resolve().parents[3]
_PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"
_PERSONA_BUILDER = (_PROMPT_DIR / "persona_builder.md").read_text()

DEFAULT_PERSONA_MODEL = os.getenv(
    "EDU_AGENTS_PERSONA_MODEL", "anthropic/claude-opus-4-8"
)
DEFAULT_BANK_PATH = REPO_ROOT / "outputs" / "persona_bank.json"


class _PersonaGen(BaseModel):
    concept_explanation: str
    rules_of_thumb: list[str]
    worked_example: str


class PersonaRecord(BaseModel):
    group_key: str
    facet_ids: list[str]            # misconception (problematic) facet ids
    facet_texts: list[str]
    goal_facet_ids: list[str] = []  # correct understandings woven into the persona
    goal_facet_texts: list[str] = []
    concept_explanation: str
    rules_of_thumb: list[str]
    worked_example: str
    model: str


def group_key_for(facet_ids: list[str]) -> str:
    return "+".join(sorted(facet_ids))


def render_knowledge_state(record: PersonaRecord) -> str:
    """Render a persona record as the {{KNOWLEDGE_STATE}} block."""
    rules = "\n".join(f"- {r}" for r in record.rules_of_thumb)
    return (
        f"{record.concept_explanation}\n\n"
        f"Rules of thumb you follow:\n{rules}\n\n"
        f"An example of how you solve these problems:\n{record.worked_example}"
    )


_WS_RE = re.compile(r"\s+")


def _leaked_phrases(record: PersonaRecord, min_words: int = 6) -> list[str]:
    """Detect long verbatim runs of the canonical facet text in the persona."""
    persona = _WS_RE.sub(" ", render_knowledge_state(record)).lower()
    leaks = []
    for text in record.facet_texts + record.goal_facet_texts:
        words = _WS_RE.sub(" ", text).lower().split()
        for i in range(len(words) - min_words + 1):
            phrase = " ".join(words[i : i + min_words])
            if phrase in persona:
                leaks.append(phrase)
                break
    return leaks


def build_persona(
    facet_ids: list[str],
    facet_map: FacetMap,
    model: str | None = None,
) -> PersonaRecord:
    """Build a persona from a facet set that may mix misconception (B) and
    goal (A) facets; goal facets become explicit correct understandings."""
    model = model or DEFAULT_PERSONA_MODEL
    by_id = {f.id: f for f in facet_map.facets}
    bad = sorted(f for f in facet_ids if by_id[f].type == "problematic")
    good = sorted(f for f in facet_ids if by_id[f].type == "goal")
    if not bad:
        raise ValueError(
            f"persona needs at least one misconception facet, got {facet_ids}"
        )

    def listing(ids):
        return "\n".join(f"- {fid}: {by_id[fid].text}" for fid in ids)

    user = (
        f"Topic: {facet_map.topic} ({facet_map.course})\n\n"
        f"Misconception(s) the student holds (instructor language):\n{listing(bad)}"
    )
    if good:
        user += (
            "\n\nCorrect understanding(s) the student also has "
            f"(instructor language):\n{listing(good)}"
        )
    messages = [
        {"role": "system", "content": _PERSONA_BUILDER},
        {"role": "user", "content": user},
    ]
    gen = structured_complete(messages, _PersonaGen, model=model)
    record = PersonaRecord(
        group_key=group_key_for(facet_ids),
        facet_ids=bad,
        facet_texts=[by_id[f].text for f in bad],
        goal_facet_ids=good,
        goal_facet_texts=[by_id[f].text for f in good],
        concept_explanation=gen.concept_explanation,
        rules_of_thumb=gen.rules_of_thumb,
        worked_example=gen.worked_example,
        model=model,
    )
    leaks = _leaked_phrases(record)
    if leaks:
        print(f"  [persona_bank] warning: {record.group_key} echoes facet text "
              f"verbatim ({leaks[0][:60]}...)")
    return record


class PersonaBank:
    """Disk-backed cache of persona records, keyed by misconception group."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else DEFAULT_BANK_PATH
        self._records: dict[str, PersonaRecord] = {}
        if self.path.exists():
            raw = json.loads(self.path.read_text())
            self._records = {
                k: PersonaRecord.model_validate(v) for k, v in raw.items()
            }

    def __len__(self) -> int:
        return len(self._records)

    def __contains__(self, group_key: str) -> bool:
        return group_key in self._records

    def get(self, group_key: str) -> PersonaRecord | None:
        return self._records.get(group_key)

    def get_or_build(
        self,
        facet_ids: list[str],
        facet_map: FacetMap,
        model: str | None = None,
    ) -> PersonaRecord:
        key = group_key_for(facet_ids)
        if key not in self._records:
            self._records[key] = build_persona(facet_ids, facet_map, model)
            self.save()
        return self._records[key]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(
            {k: v.model_dump() for k, v in sorted(self._records.items())},
            indent=2, ensure_ascii=False,
        ))
