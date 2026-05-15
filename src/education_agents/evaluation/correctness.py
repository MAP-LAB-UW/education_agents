"""Correctness rubric: have a strong LLM solve the item blind."""

from __future__ import annotations

import os

from pydantic import BaseModel

from ..llm import structured_complete
from ..schemas import GeneratedItem
from .schemas import CorrectnessResult

DEFAULT_EVAL_MODEL = os.getenv(
    "EDU_AGENTS_EVAL_MODEL", "gemini/gemini-3.1-pro-preview"
)


class _LLMAnswer(BaseModel):
    selected_answer: str
    reasoning: str
    flagged_distractors: list[str]
    flagged_reasoning: str


SYSTEM_PROMPT = """You are an expert statistician. You will be given a multiple-choice item about statistics. Your job is to:

1. Solve the problem and select the best answer.
2. Identify any distractor (incorrect option) that could also be defensibly correct — i.e., an option that a knowledgeable statistician could argue is also a valid answer due to ambiguity in the stem or options.

Be rigorous. Only flag a distractor if there is a genuine statistical argument for it, not just because it contains a partial truth."""


def evaluate_correctness(
    item: GeneratedItem,
    model: str | None = None,
) -> CorrectnessResult:
    model = model or DEFAULT_EVAL_MODEL

    options_text = "\n".join(
        f"  {o.id}. {o.text}" for o in item.options
    )

    format_note = ""
    if item.response_format == "true_false_per_option":
        format_note = (
            "\n\nThis is a true/false per option item. For each option, "
            "determine if it is True or False. Then select all option IDs "
            "where the correct verdict is True. Return them comma-separated "
            "as your selected_answer."
        )
    elif item.response_format == "multi_select":
        format_note = (
            "\n\nThis is a multi-select item. Select ALL correct options. "
            "Return them comma-separated as your selected_answer."
        )

    user_msg = (
        f"Stem: {item.stem}\n\n"
        f"Options:\n{options_text}"
        f"{format_note}\n\n"
        "Solve this problem. Select the best answer and flag any "
        "distractors that could also be defensibly correct."
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    result = structured_complete(messages, _LLMAnswer, model=model)

    selected_ids = {s.strip() for s in result.selected_answer.split(",")}
    correct_ids = set(item.correct_option_ids)
    is_correct = selected_ids == correct_ids

    return CorrectnessResult(
        selected_answer=result.selected_answer,
        correct_answer_ids=item.correct_option_ids,
        is_correct=is_correct,
        flagged_distractors=result.flagged_distractors,
        reasoning=result.reasoning,
    )
