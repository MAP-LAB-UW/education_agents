"""Student simulator: an LLM persona that holds specified misconceptions and
answers an item, plus the misconception judge that scores whether its reasoning
exhibits those misconceptions (signal a, simulator validation).

Phase 2 (mapping judge / item diagnosticity) is layered on later; this module's
`run_trial` fills the fidelity fields and leaves the mapping fields unset.
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel

from ..figures import build_multimodal_content
from ..llm import structured_complete
from ..schemas import FacetMap
from .correctness import DEFAULT_EVAL_MODEL
from .schemas import GroupFidelity, PersonaResult, SimulatorEvalReport
from .sim_corpus import SimItem, Trial

_PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"
_STUDENT_OPEN = (_PROMPT_DIR / "student_open.md").read_text()
_STUDENT_SELECT = (_PROMPT_DIR / "student_select.md").read_text()
_MISCONCEPTION_JUDGE = (_PROMPT_DIR / "misconception_judge.md").read_text()

DEFAULT_STUDENT_MODEL = os.getenv(
    "EDU_AGENTS_STUDENT_MODEL", "anthropic/claude-sonnet-4-6"
)
DEFAULT_JUDGE_MODEL = DEFAULT_EVAL_MODEL


# ── Structured I/O ───────────────────────────────────────────────────────────

class _StudentResponse(BaseModel):
    reasoning: str
    answer: str


class _MisconceptionVerdict(BaseModel):
    exhibits: bool
    judge_reasoning: str


# ── Helpers ──────────────────────────────────────────────────────────────────

def _render_facets(facet_map: FacetMap, ids: list[str]) -> str:
    """Render the persona's misconception facets as 'Bxx: text' lines."""
    by_id = {f.id: f.text for f in facet_map.facets}
    return "\n".join(f"- {fid}: {by_id.get(fid, fid)}" for fid in ids)


def _options_block(item: SimItem) -> str:
    return "\n".join(f"  {o.id}. {o.text}" for o in item.options)


def _format_note(response_format: str) -> str:
    if response_format == "true_false_per_option":
        return (
            "\n\nThis is a true/false-per-option item. Report every option id "
            "you believe is True, comma-separated."
        )
    if response_format == "multi_select":
        return (
            "\n\nThis is a multi-select item. Report every option id you "
            "believe is correct, comma-separated."
        )
    return ""


# ── Student + judge calls ────────────────────────────────────────────────────

def run_student(
    item: SimItem,
    persona_facets: list[str],
    mode: str,
    facet_map: FacetMap,
    student_model: str | None = None,
) -> _StudentResponse:
    student_model = student_model or DEFAULT_STUDENT_MODEL
    misconceptions = _render_facets(facet_map, persona_facets)

    if mode == "open":
        system = _STUDENT_OPEN.replace("{{MISCONCEPTIONS}}", misconceptions)
        user_text = f"Problem:\n{item.stem}"
    elif mode == "select":
        system = _STUDENT_SELECT.replace("{{MISCONCEPTIONS}}", misconceptions)
        user_text = (
            f"Problem:\n{item.stem}\n\n"
            f"Options:\n{_options_block(item)}"
            f"{_format_note(item.response_format)}"
        )
    else:
        raise ValueError(f"unknown mode: {mode}")

    user_content = build_multimodal_content(user_text, item.figure_data or {})
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]
    return structured_complete(messages, _StudentResponse, model=student_model)


def judge_misconception(
    reasoning: str,
    answer: str,
    persona_facets: list[str],
    facet_map: FacetMap,
    judge_model: str | None = None,
) -> _MisconceptionVerdict:
    judge_model = judge_model or DEFAULT_JUDGE_MODEL
    misconceptions = _render_facets(facet_map, persona_facets)
    system = _MISCONCEPTION_JUDGE.replace("{{MISCONCEPTIONS}}", misconceptions)
    user_text = (
        f"Student's reasoning:\n{reasoning}\n\n"
        f"Student's final answer:\n{answer}\n\n"
        "Does this reasoning exhibit the target misconception(s)?"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_text},
    ]
    return structured_complete(messages, _MisconceptionVerdict, model=judge_model)


# ── Trials ───────────────────────────────────────────────────────────────────

def run_trial(
    trial: Trial,
    facet_map: FacetMap,
    modes: tuple[str, ...] = ("open", "select"),
    student_model: str | None = None,
    judge_model: str | None = None,
) -> list[PersonaResult]:
    """Run one trial in each requested mode. Phase 1: fidelity only."""
    results: list[PersonaResult] = []
    for mode in modes:
        student = run_student(
            trial.item, trial.persona_facets, mode, facet_map, student_model
        )
        verdict = judge_misconception(
            student.reasoning,
            student.answer,
            trial.persona_facets,
            facet_map,
            judge_model,
        )
        results.append(
            PersonaResult(
                source=trial.item.source,
                group_key=trial.group_key,
                persona_facets=trial.persona_facets,
                target_option_id=trial.target_option_id,
                mode=mode,
                student_reasoning=student.reasoning,
                student_answer=student.answer,
                exhibits_misconception=verdict.exhibits,
                judge_reasoning=verdict.judge_reasoning,
            )
        )
    return results


# ── Aggregation ──────────────────────────────────────────────────────────────

def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def aggregate_report(results: list[PersonaResult]) -> SimulatorEvalReport:
    """Aggregate persona results into per-group / per-source fidelity."""
    by_group: dict[str, list[PersonaResult]] = {}
    by_source: dict[str, list[PersonaResult]] = {}
    for r in results:
        by_group.setdefault(r.group_key, []).append(r)
        by_source.setdefault(r.source, []).append(r)

    group_fidelities = [
        GroupFidelity(
            group_key=key,
            n_trials=len(rs),
            misconception_fidelity=_mean(
                [float(r.exhibits_misconception) for r in rs]
            ),
        )
        for key, rs in sorted(by_group.items())
    ]
    source_fidelities = {
        src: _mean([float(r.exhibits_misconception) for r in rs])
        for src, rs in sorted(by_source.items())
    }
    overall = _mean([float(r.exhibits_misconception) for r in results])

    single = [r for r in results if len(r.persona_facets) == 1]
    multi = [r for r in results if len(r.persona_facets) > 1]

    return SimulatorEvalReport(
        by_group=group_fidelities,
        by_source=source_fidelities,
        overall_fidelity=overall,
        single_facet_fidelity=_mean([float(r.exhibits_misconception) for r in single]),
        multi_facet_fidelity=_mean([float(r.exhibits_misconception) for r in multi]),
        n_single_facet_runs=len(single),
        n_multi_facet_runs=len(multi),
        persona_results=results,
    )
