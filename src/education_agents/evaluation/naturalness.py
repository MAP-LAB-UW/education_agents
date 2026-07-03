"""Naturalness rubric: LLM-as-judge for readability and clarity."""

from __future__ import annotations

import os

from pydantic import BaseModel

from ..figures import build_multimodal_content
from ..llm import structured_complete
from ..schemas import GeneratedItem
from .schemas import NaturalnessResult

DEFAULT_EVAL_MODEL = os.getenv(
    "EDU_AGENTS_EVAL_MODEL", "anthropic/claude-sonnet-4-6"
)


class _NaturalnessRating(BaseModel):
    stem_score: int
    stem_reasoning: str
    options_score: int
    options_reasoning: str


SYSTEM_PROMPT = """You are an expert in educational assessment design. Rate the readability and naturalness of a multiple-choice item on a 1–5 scale.

Score the **stem** and **options** separately.

## Scoring rubric

### Stem (1–5):
5 - Clear, concise, real-world scenario. Easy to read on first pass. A student knows exactly what is being asked.
4 - Clear scenario with minor wordiness or slightly awkward phrasing that doesn't impede understanding.
3 - Understandable but noticeably wordy, uses unnecessarily complex sentence structure, or the scenario feels contrived.
2 - Confusing structure, multiple re-reads needed, or the scenario is so artificial it distracts from the question.
1 - Incoherent, contradictory, or so convoluted that the question is unclear.

### Options (1–5):
5 - All options are concise, parallel in structure, and easy to compare. No option is awkwardly long or convoluted.
4 - Options are mostly clear with minor inconsistencies in length or phrasing.
3 - Some options are wordy, overly technical, or structurally inconsistent, making comparison harder.
2 - Multiple options are confusing, excessively long, or so differently structured that comparison is difficult.
1 - Options are incoherent or contradictory in a way unrelated to the diagnostic intent.

Provide a brief reasoning for each score (1–2 sentences)."""


def evaluate_naturalness(
    item: GeneratedItem,
    model: str | None = None,
    figure_data: dict[str, str] | None = None,
) -> NaturalnessResult:
    model = model or DEFAULT_EVAL_MODEL

    options_text = "\n".join(
        f"  {o.id}. {o.text}" for o in item.options
    )

    user_text = (
        f"Rate the naturalness of this item.\n\n"
        f"Format: {item.response_format}\n\n"
        f"Stem: {item.stem}\n\n"
        f"Options:\n{options_text}"
    )

    user_content = build_multimodal_content(user_text, figure_data or {})

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    result = structured_complete(messages, _NaturalnessRating, model=model)

    overall = round((result.stem_score + result.options_score) / 2)

    return NaturalnessResult(
        stem_score=result.stem_score,
        stem_reasoning=result.stem_reasoning,
        options_score=result.options_score,
        options_reasoning=result.options_reasoning,
        overall_score=overall,
    )
