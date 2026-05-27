"""Figure necessity rubric: can the item be answered correctly without its figure?"""

from __future__ import annotations

import os

from ..llm import structured_complete
from ..schemas import GeneratedItem
from .correctness import _LLMAnswer, SYSTEM_PROMPT, parse_selected_ids
from .schemas import FigureNecessityResult, FigureNecessityTrial

DEFAULT_EVAL_MODEL = os.getenv(
    "EDU_AGENTS_EVAL_MODEL", "gemini/gemini-3.1-pro-preview"
)

N_TRIALS = 5


def evaluate_figure_necessity(
    item: GeneratedItem,
    model: str | None = None,
    n_trials: int = N_TRIALS,
) -> FigureNecessityResult:
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

    correct_ids = set(item.correct_option_ids)
    trials: list[FigureNecessityTrial] = []

    for _ in range(n_trials):
        result = structured_complete(messages, _LLMAnswer, model=model, temperature=1.0)
        selected_ids = parse_selected_ids(result.selected_answer)
        trials.append(FigureNecessityTrial(
            selected_answer=result.selected_answer,
            is_correct=selected_ids == correct_ids,
            reasoning=result.reasoning,
        ))

    n_correct = sum(t.is_correct for t in trials)

    return FigureNecessityResult(
        is_necessary=n_correct / n_trials < 0.5,
        n_trials=n_trials,
        n_correct=n_correct,
        trials=trials,
    )
