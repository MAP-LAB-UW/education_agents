"""Answer-conditioned (few-shot persona) misconception elicitation, and a
head-to-head harness comparing it against belief-injection.

Belief-injection (the existing simulator) names the misconception in the system
prompt. The few-shot persona never names it: the model is shown sibling problems
from the same misconception group with the misconception-keyed option marked as
the answer it chose, and must answer a new problem consistently — reconstructing
the misconception's reasoning rather than reciting it.

Both methods run in select mode so a "hit" = the model picked the target option.
For each (item, method) we record hit rate over K samples, and — among hits —
judge-confirmed misconception fidelity and an LLM naturalness score.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from ..figures import build_multimodal_content
from ..llm import structured_complete
from ..schemas import FacetMap
from .correctness import canonicalize_ids, parse_selected_ids
from .schemas import MethodItemResult, SampleAttempt
from .sim_corpus import SimItem
from .student_simulator import (
    DEFAULT_JUDGE_MODEL,
    DEFAULT_STUDENT_MODEL,
    _StudentResponse,
    _format_note,
    _options_block,
    _render_facets,
    judge_misconception,
)
from .student_simulator import _STUDENT_SELECT  # belief-injection select prompt

_PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"
_STUDENT_FEWSHOT = (_PROMPT_DIR / "student_fewshot.md").read_text()
_NATURALNESS_JUDGE = (_PROMPT_DIR / "naturalness_judge.md").read_text()

DEFAULT_SAMPLE_TEMPERATURE = 0.9


class _NaturalnessScore(BaseModel):
    score: int
    reasoning: str


# ── Message construction ─────────────────────────────────────────────────────

def _belief_messages(item: SimItem, persona_facets: list[str], facet_map: FacetMap):
    system = _STUDENT_SELECT.replace(
        "{{MISCONCEPTIONS}}", _render_facets(facet_map, persona_facets)
    )
    user = (
        f"Problem:\n{item.stem}\n\n"
        f"Options:\n{_options_block(item)}{_format_note(item.response_format)}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": build_multimodal_content(user, item.figure_data or {})},
    ]


def _fewshot_messages(item: SimItem, shots: list[tuple[SimItem, str]]):
    parts = ["Here are several problems you worked on earlier, with the answer you chose for each:\n"]
    for i, (s_item, s_ans) in enumerate(shots, 1):
        parts.append(
            f"--- Problem {i} ---\n{s_item.stem}\n"
            f"Options:\n{_options_block(s_item)}\n"
            f"Your answer: {s_ans}\n"
        )
    parts.append(
        f"--- New problem ---\n{item.stem}\n"
        f"Options:\n{_options_block(item)}{_format_note(item.response_format)}\n"
    )
    parts.append("Reason step by step in your own words, then give your answer.")
    return [
        {"role": "system", "content": _STUDENT_FEWSHOT},
        {"role": "user", "content": "\n".join(parts)},
    ]


# ── Scoring helpers ──────────────────────────────────────────────────────────

def rate_naturalness(
    reasoning: str, answer: str, model: str | None = None
) -> _NaturalnessScore:
    model = model or DEFAULT_JUDGE_MODEL
    messages = [
        {"role": "system", "content": _NATURALNESS_JUDGE},
        {"role": "user", "content": (
            f"Student's reasoning:\n{reasoning}\n\n"
            f"Student's final answer:\n{answer}\n\n"
            "Rate how natural and authentic this reasoning reads."
        )},
    ]
    return structured_complete(messages, _NaturalnessScore, model=model)


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


# ── Per (item, method) run ───────────────────────────────────────────────────

def run_method_on_item(
    method: str,
    item: SimItem,
    persona_facets: list[str],
    target_option_id: str,
    group_key: str,
    facet_map: FacetMap,
    shots: list[tuple[SimItem, str]] | None = None,
    k: int = 6,
    student_model: str | None = None,
    judge_model: str | None = None,
    temperature: float = DEFAULT_SAMPLE_TEMPERATURE,
) -> MethodItemResult:
    student_model = student_model or DEFAULT_STUDENT_MODEL
    judge_model = judge_model or DEFAULT_JUDGE_MODEL
    shots = shots or []

    if method == "belief":
        messages = _belief_messages(item, persona_facets, facet_map)
    elif method == "fewshot":
        messages = _fewshot_messages(item, shots)
    else:
        raise ValueError(f"unknown method: {method}")

    attempts: list[SampleAttempt] = []
    for _ in range(k):
        resp = structured_complete(
            messages, _StudentResponse, model=student_model, temperature=temperature
        )
        option_ids = [o.id for o in item.options]
        ids = sorted(canonicalize_ids(parse_selected_ids(resp.answer), option_ids))
        hit = target_option_id in ids
        attempt = SampleAttempt(
            answer=resp.answer, selected_ids=ids, hit=hit, reasoning=resp.reasoning
        )
        if hit:
            verdict = judge_misconception(
                resp.reasoning, resp.answer, persona_facets, facet_map, judge_model
            )
            attempt.exhibits_misconception = verdict.exhibits
            attempt.naturalness = rate_naturalness(
                resp.reasoning, resp.answer, judge_model
            ).score
        attempts.append(attempt)

    hits = [a for a in attempts if a.hit]
    return MethodItemResult(
        method=method,
        source=item.source,
        group_key=group_key,
        persona_facets=persona_facets,
        target_option_id=target_option_id,
        k_samples=k,
        n_hits=len(hits),
        hit_rate=len(hits) / k,
        fidelity_among_hits=_mean([float(a.exhibits_misconception) for a in hits]),
        naturalness_among_hits=_mean([float(a.naturalness) for a in hits]),
        n_shots=len(shots),
        attempts=attempts,
    )
