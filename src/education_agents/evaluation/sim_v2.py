"""Student simulator v2: open-mode answering with blind mapping, per-item
negative-control batteries, and a blind misconception lineup judge.

Design (vs. the v1 belief-injection / few-shot simulators):

1. The student answers the stem with **no options shown** (for statement-
   evaluation formats, statements are shown unlabeled); a separate blind
   mapper decides which option the free response corresponds to. This removes
   the option-text lexical-matching shortcut — a hit means the distractor sits
   where the misconceived reasoning lands unprompted.
2. Each item runs a **battery** of personas: one persona per misconception
   group keyed to any of the item's distractors, plus a no-misconception
   control. The reported signal is a selection-rate *gap* —
   P(target | matched persona) − P(target | other personas) — i.e. item
   discrimination, not a saturating hit rate.
3. Personas come from the **persona bank** (two-stage instantiation; see
   persona_bank.py), so the student never holds the canonical facet wording.
4. The misconception judge is a **lineup**: it sees every candidate facet (not
   the target) and says which, if any, the reasoning exhibits.
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel

from ..figures import build_multimodal_content
from ..llm import structured_complete
from ..schemas import FacetMap
from .correctness import canonicalize_ids, parse_selected_ids
from .persona_bank import PersonaBank, PersonaRecord, render_knowledge_state
from .schemas import (
    SimV2Attempt,
    SimV2GroupSummary,
    SimV2Report,
    TargetDiagnostic,
)
from .sim_corpus import SimItem, problematic_ids
from .student_simulator import _format_note, _options_block

_PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"
_STUDENT_PERSONA_OPEN = (_PROMPT_DIR / "student_persona_open.md").read_text()
_STUDENT_CONTROL_OPEN = (_PROMPT_DIR / "student_control_open.md").read_text()
_STUDENT_PERSONA_SELECT = (_PROMPT_DIR / "student_persona_select.md").read_text()
_STUDENT_CONTROL_SELECT = (_PROMPT_DIR / "student_control_select.md").read_text()
_ANSWER_MAPPER = (_PROMPT_DIR / "answer_mapper.md").read_text()
_LINEUP_JUDGE = (_PROMPT_DIR / "misconception_lineup_judge.md").read_text()

DEFAULT_V2_STUDENT_MODEL = os.getenv(
    "EDU_AGENTS_V2_STUDENT_MODEL", "anthropic/claude-sonnet-4-6"
)
DEFAULT_MAPPER_MODEL = os.getenv(
    "EDU_AGENTS_V2_MAPPER_MODEL", "anthropic/claude-sonnet-4-6"
)
DEFAULT_JUDGE_MODEL = os.getenv(
    "EDU_AGENTS_V2_JUDGE_MODEL", "anthropic/claude-sonnet-4-6"
)
DEFAULT_SAMPLE_TEMPERATURE = 0.9

CONTROL_KEY = "control"


# ── Structured I/O ───────────────────────────────────────────────────────────

class _OpenResponse(BaseModel):
    reasoning: str
    answer: str


class _MappedAnswer(BaseModel):
    selected_option_ids: list[str]
    no_match: bool
    reasoning: str


class _LineupVerdict(BaseModel):
    exhibited_facet_ids: list[str]
    reasoning_is_correct: bool
    judge_reasoning: str


# ── Battery construction ─────────────────────────────────────────────────────

class TargetSpec(BaseModel):
    option_id: str
    group_key: str            # full facet set (goal + misconception), "+"-joined
    facet_ids: list[str]      # misconception facets only (lineup-judge targets)
    goal_facets: list[str] = []


class ItemBattery(BaseModel):
    """One item plus every persona that should face it.

    persona_keys holds the full facet sets (misconceptions plus any goal facets
    keyed to the same option) of the item's incorrect options; the control
    persona is added implicitly at run time. For each target, every persona
    other than its own acts as a negative control.
    """
    item: SimItem
    targets: list[TargetSpec]
    persona_keys: list[str]


def build_item_batteries(
    items: list[SimItem],
    facet_map: FacetMap,
) -> list[ItemBattery]:
    bad = problematic_ids(facet_map)
    good = {f.id for f in facet_map.facets if f.type == "goal"}
    batteries: list[ItemBattery] = []
    for item in items:
        targets: list[TargetSpec] = []
        for o in item.options:
            if o.is_correct:
                continue
            m = sorted(t for t in o.facet_tags if t in bad)
            if not m:
                continue
            g = sorted(t for t in o.facet_tags if t in good)
            targets.append(TargetSpec(
                option_id=o.id,
                group_key="+".join(g + m),
                facet_ids=m,
                goal_facets=g,
            ))
        if not targets:
            continue
        keys = sorted({t.group_key for t in targets})
        batteries.append(ItemBattery(item=item, targets=targets, persona_keys=keys))
    return batteries


# ── Student / mapper / judge calls ───────────────────────────────────────────

def _open_user_text(item: SimItem) -> str:
    """Stem-only prompt; statement-evaluation formats need the statements,
    so those are shown unlabeled (no option ids, no marking)."""
    text = f"Problem:\n{item.stem}"
    if item.response_format in ("true_false_per_option", "multi_select"):
        statements = "\n".join(f"- {o.text}" for o in item.options)
        text += (
            f"\n\nStatements to evaluate:\n{statements}\n\n"
            "For each statement, decide whether you believe it is true and "
            "explain why. In your final answer, restate the statement(s) you "
            "believe are true."
        )
    return text


def run_open_student(
    item: SimItem,
    persona: PersonaRecord | None,
    student_model: str | None = None,
    temperature: float | None = DEFAULT_SAMPLE_TEMPERATURE,
) -> _OpenResponse:
    """Answer the item open-mode. persona=None runs the control student."""
    student_model = student_model or DEFAULT_V2_STUDENT_MODEL
    if persona is None:
        system = _STUDENT_CONTROL_OPEN
    else:
        system = _STUDENT_PERSONA_OPEN.replace(
            "{{KNOWLEDGE_STATE}}", render_knowledge_state(persona)
        )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": build_multimodal_content(
            _open_user_text(item), item.figure_data or {}
        )},
    ]
    kwargs = {} if temperature is None else {"temperature": temperature}
    return structured_complete(messages, _OpenResponse, model=student_model, **kwargs)


def run_select_student(
    item: SimItem,
    persona: PersonaRecord | None,
    student_model: str | None = None,
    temperature: float | None = DEFAULT_SAMPLE_TEMPERATURE,
) -> tuple[_OpenResponse, list[str]]:
    """Select-mode fallback: same persona, labeled options shown.

    Used when the open answer maps to no option (option-dependent stems).
    Returns the response and the canonicalized picked ids.
    """
    student_model = student_model or DEFAULT_V2_STUDENT_MODEL
    if persona is None:
        system = _STUDENT_CONTROL_SELECT
    else:
        system = _STUDENT_PERSONA_SELECT.replace(
            "{{KNOWLEDGE_STATE}}", render_knowledge_state(persona)
        )
    user_text = (
        f"Problem:\n{item.stem}\n\n"
        f"Options:\n{_options_block(item)}"
        f"{_format_note(item.response_format)}"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": build_multimodal_content(
            user_text, item.figure_data or {}
        )},
    ]
    kwargs = {} if temperature is None else {"temperature": temperature}
    resp = structured_complete(messages, _OpenResponse, model=student_model, **kwargs)
    option_ids = [o.id for o in item.options]
    picked = sorted(canonicalize_ids(parse_selected_ids(resp.answer), option_ids))
    return resp, picked


def map_answer(
    item: SimItem,
    reasoning: str,
    answer: str,
    mapper_model: str | None = None,
) -> _MappedAnswer:
    """Blind mapper: free response -> option ids. Sees no key, no facets."""
    mapper_model = mapper_model or DEFAULT_MAPPER_MODEL
    options = "\n".join(f"  {o.id}. {o.text}" for o in item.options)
    user = (
        f"Problem stem:\n{item.stem}\n\n"
        f"Options:\n{options}\n\n"
        f"Student's reasoning:\n{reasoning}\n\n"
        f"Student's final answer:\n{answer}\n\n"
        "Which option(s) does the student's answer correspond to?"
    )
    messages = [
        {"role": "system", "content": _ANSWER_MAPPER},
        {"role": "user", "content": user},
    ]
    result = structured_complete(messages, _MappedAnswer, model=mapper_model)
    option_ids = [o.id for o in item.options]
    result.selected_option_ids = sorted(
        canonicalize_ids(result.selected_option_ids, option_ids)
    )
    return result


def lineup_judge(
    item: SimItem,
    reasoning: str,
    answer: str,
    facet_map: FacetMap,
    judge_model: str | None = None,
) -> _LineupVerdict:
    """Blind lineup: which candidate misconception(s) does the reasoning show?"""
    judge_model = judge_model or DEFAULT_JUDGE_MODEL
    candidates = "\n".join(
        f"- {f.id}: {f.text}" for f in facet_map.facets if f.type == "problematic"
    )
    system = _LINEUP_JUDGE.replace("{{CANDIDATE_MISCONCEPTIONS}}", candidates)
    user = (
        f"Problem:\n{item.stem}\n\n"
        f"Student's reasoning:\n{reasoning}\n\n"
        f"Student's final answer:\n{answer}\n\n"
        "Which candidate misconception(s), if any, does this reasoning exhibit?"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return structured_complete(messages, _LineupVerdict, model=judge_model)


# ── Battery runner ───────────────────────────────────────────────────────────

def run_attempt(
    battery: ItemBattery,
    persona_key: str,
    sample_index: int,
    bank: PersonaBank,
    facet_map: FacetMap,
    student_model: str | None = None,
    mapper_model: str | None = None,
    judge_model: str | None = None,
    temperature: float | None = DEFAULT_SAMPLE_TEMPERATURE,
    select_fallback: bool = True,
) -> SimV2Attempt:
    """One (item, persona, sample): open student -> blind map -> blind lineup.

    If the open answer maps to no option (option-dependent stems the persona
    can't engage with blind), optionally re-run the same persona in select
    mode so the item still yields a selection signal; the open no-match is
    kept on the record as its own diagnostic.
    """
    item = battery.item
    if persona_key == CONTROL_KEY:
        persona = None
        facets: list[str] = []
    else:
        facets = persona_key.split("+")
        persona = bank.get_or_build(facets, facet_map)

    student = run_open_student(item, persona, student_model, temperature)
    mapped = map_answer(item, student.reasoning, student.answer, mapper_model)

    attempt = SimV2Attempt(
        source=item.source,
        persona_key=persona_key,
        persona_facets=facets,
        sample_index=sample_index,
        student_reasoning=student.reasoning,
        student_answer=student.answer,
        mapped_option_ids=mapped.selected_option_ids,
        mapper_no_match=mapped.no_match,
        mapper_reasoning=mapped.reasoning,
    )
    if select_fallback and not mapped.selected_option_ids:
        resp, picked = run_select_student(item, persona, student_model, temperature)
        attempt.fallback_used = True
        attempt.fallback_option_ids = picked
        attempt.fallback_reasoning = resp.reasoning
        attempt.fallback_answer = resp.answer
    if persona is not None:
        verdict = lineup_judge(
            item, student.reasoning, student.answer, facet_map, judge_model
        )
        attempt.exhibited_facet_ids = verdict.exhibited_facet_ids
        attempt.judged_reasoning_correct = verdict.reasoning_is_correct
        attempt.lineup_judge_reasoning = verdict.judge_reasoning
    return attempt


def effective_option_ids(attempt: SimV2Attempt) -> list[str]:
    """Option ids an attempt counts for: open mapping, else select fallback."""
    if attempt.mapped_option_ids:
        return attempt.mapped_option_ids
    return attempt.fallback_option_ids or []


def battery_run_plan(
    battery: ItemBattery, k: int, include_control: bool = True,
) -> list[tuple[str, int]]:
    """(persona_key, sample_index) pairs for one battery, control included."""
    keys = list(battery.persona_keys) + ([CONTROL_KEY] if include_control else [])
    return [(key, i) for key in keys for i in range(k)]


# ── Aggregation ──────────────────────────────────────────────────────────────

def _mean(xs) -> float | None:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def aggregate_v2(
    attempts: list[SimV2Attempt],
    batteries: list[ItemBattery],
    k_samples: int,
) -> SimV2Report:
    by_item: dict[str, list[SimV2Attempt]] = {}
    for a in attempts:
        by_item.setdefault(a.source, []).append(a)

    per_target: list[TargetDiagnostic] = []
    control_correct: list[float] = []

    for battery in batteries:
        item_attempts = by_item.get(battery.item.source, [])
        if not item_attempts:
            continue
        correct_ids = {o.id for o in battery.item.options if o.is_correct}
        for a in item_attempts:
            if a.persona_key == CONTROL_KEY:
                control_correct.append(
                    float(set(effective_option_ids(a)) == correct_ids)
                )

        for target in battery.targets:
            matched = [a for a in item_attempts if a.persona_key == target.group_key]
            control = [a for a in item_attempts if a.persona_key == CONTROL_KEY]
            alternative = [
                a for a in item_attempts
                if a.persona_key not in (target.group_key, CONTROL_KEY)
            ]
            if not matched:
                continue

            def rate(group):
                return _mean(
                    float(target.option_id in effective_option_ids(a))
                    for a in group
                )

            matched_rate = rate(matched) or 0.0
            others = alternative + control
            pooled_other = rate(others) if others else None
            lineup = _mean(
                float(set(target.facet_ids) <= set(a.exhibited_facet_ids or []))
                for a in matched
                if a.exhibited_facet_ids is not None
            )
            per_target.append(TargetDiagnostic(
                source=battery.item.source,
                target_option_id=target.option_id,
                group_key=target.group_key,
                n_matched=len(matched),
                n_alternative=len(alternative),
                n_control=len(control),
                matched_target_rate=matched_rate,
                alternative_target_rate=rate(alternative),
                control_target_rate=rate(control),
                selection_gap=matched_rate - (pooled_other or 0.0),
                matched_lineup_id_rate=lineup,
                matched_open_no_match_rate=_mean(
                    float(not a.mapped_option_ids) for a in matched
                ),
            ))

    by_group: dict[str, list[TargetDiagnostic]] = {}
    for t in per_target:
        by_group.setdefault(t.group_key, []).append(t)
    group_summaries = [
        SimV2GroupSummary(
            group_key=key,
            n_targets=len(ts),
            mean_matched_rate=_mean(t.matched_target_rate for t in ts) or 0.0,
            mean_gap=_mean(t.selection_gap for t in ts) or 0.0,
            mean_lineup_id_rate=_mean(
                t.matched_lineup_id_rate for t in ts
                if t.matched_lineup_id_rate is not None
            ),
        )
        for key, ts in sorted(by_group.items())
    ]

    alt_rates = [t.alternative_target_rate for t in per_target
                 if t.alternative_target_rate is not None]
    ctrl_rates = [t.control_target_rate for t in per_target
                  if t.control_target_rate is not None]
    lineup_rates = [t.matched_lineup_id_rate for t in per_target
                    if t.matched_lineup_id_rate is not None]

    return SimV2Report(
        n_items=len({t.source for t in per_target}),
        n_attempts=len(attempts),
        k_samples=k_samples,
        overall_matched_rate=_mean(t.matched_target_rate for t in per_target) or 0.0,
        overall_alternative_rate=_mean(alt_rates),
        overall_control_target_rate=_mean(ctrl_rates),
        overall_gap=_mean(t.selection_gap for t in per_target) or 0.0,
        control_correct_rate=_mean(control_correct),
        lineup_id_rate=_mean(lineup_rates),
        open_no_match_rate=_mean(
            float(not a.mapped_option_ids) for a in attempts
        ),
        by_group=group_summaries,
        per_target=per_target,
        attempts=attempts,
    )
