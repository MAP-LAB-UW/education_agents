"""Final check: belief-injection in select mode with a small student model.

Samples a misconception-bearing student K times on each item and measures how
often it picks the misconception-keyed (target) option. Each miss is diagnosed
by a judge as a simulator problem (didn't adopt the misconception, or picked
inconsistently) vs. an item problem (misconception doesn't uniquely lead to the
target).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from ..llm import structured_complete
from ..schemas import FacetMap
from .answer_conditioned import DEFAULT_SAMPLE_TEMPERATURE, _belief_messages
from .correctness import canonicalize_ids, parse_selected_ids
from .schemas import SelectorAttempt, SelectorItemResult
from .sim_corpus import SimItem, Trial
from .student_simulator import (
    DEFAULT_JUDGE_MODEL,
    DEFAULT_STUDENT_MODEL,
    _StudentResponse,
    _options_block,
    _render_facets,
    judge_misconception,
)

_PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"
_MISS_DIAGNOSIS = (_PROMPT_DIR / "miss_diagnosis.md").read_text()


class _MissVerdict(BaseModel):
    category: str
    explanation: str


def diagnose_miss(
    item: SimItem,
    persona_facets: list[str],
    target_option_id: str,
    reasoning: str,
    answer: str,
    facet_map: FacetMap,
    judge_model: str | None = None,
) -> _MissVerdict:
    judge_model = judge_model or DEFAULT_JUDGE_MODEL
    misconceptions = _render_facets(facet_map, persona_facets)
    options = "\n".join(
        f"  {o.id}. {o.text}" + ("   <-- TARGET" if o.id == target_option_id else "")
        for o in item.options
    )
    user = (
        f"Misconception(s) the student was told to hold:\n{misconceptions}\n\n"
        f"Item stem:\n{item.stem}\n\n"
        f"Options:\n{options}\n\n"
        f"Target option (expected): {target_option_id}\n\n"
        f"Student's reasoning:\n{reasoning}\n\n"
        f"Student's final answer:\n{answer}\n\n"
        "The student did not choose the target. Diagnose why."
    )
    messages = [
        {"role": "system", "content": _MISS_DIAGNOSIS},
        {"role": "user", "content": user},
    ]
    return structured_complete(messages, _MissVerdict, model=judge_model)


def run_selector_check_on_item(
    trial: Trial,
    facet_map: FacetMap,
    k: int = 5,
    student_model: str | None = None,
    judge_model: str | None = None,
    temperature: float = DEFAULT_SAMPLE_TEMPERATURE,
) -> SelectorItemResult:
    student_model = student_model or DEFAULT_STUDENT_MODEL
    item = trial.item
    option_ids = [o.id for o in item.options]
    messages = _belief_messages(item, trial.persona_facets, facet_map)

    attempts: list[SelectorAttempt] = []
    for _ in range(k):
        resp = structured_complete(
            messages, _StudentResponse, model=student_model, temperature=temperature
        )
        ids = sorted(canonicalize_ids(parse_selected_ids(resp.answer), option_ids))
        hit = trial.target_option_id in ids
        a = SelectorAttempt(
            answer=resp.answer, selected_ids=ids, hit=hit, reasoning=resp.reasoning
        )
        if hit:
            a.exhibits_misconception = judge_misconception(
                resp.reasoning, resp.answer, trial.persona_facets, facet_map, judge_model
            ).exhibits
        else:
            v = diagnose_miss(
                item, trial.persona_facets, trial.target_option_id,
                resp.reasoning, resp.answer, facet_map, judge_model,
            )
            a.miss_category = v.category
            a.miss_explanation = v.explanation
        attempts.append(a)

    hits = [a for a in attempts if a.hit]
    return SelectorItemResult(
        source=item.source,
        group_key=trial.group_key,
        persona_facets=trial.persona_facets,
        target_option_id=trial.target_option_id,
        k_samples=k,
        n_hits=len(hits),
        hit_rate=len(hits) / k if k else 0.0,
        attempts=attempts,
    )
