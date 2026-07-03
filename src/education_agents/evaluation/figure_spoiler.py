"""Figure spoiler rubric: does the figure give away the answer?

The complement of ``figure_necessity``. Where necessity asks "can the item be
solved WITHOUT the figure?" (decorative failure), the spoiler judge asks the
opposite: "does the figure leak the answer through its labels/annotations, so a
student who does not understand the concept could still read the answer off it?"

This is a judgment, not a solve attempt: the judge is shown the figure and told
which option is correct, and must decide whether the correct option is disclosed
by the figure's surface text (legend, title, axis labels, annotations) rather
than only reachable by interpreting the raw visual evidence with the target
concept. See ``prompts/figure_spoiler_judge.md``.
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel

from ..figures import build_multimodal_content
from ..llm import structured_complete
from ..schemas import GeneratedItem
from .schemas import FigureSpoilerResult, FigureSpoilerTrial

_PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"
SYSTEM_PROMPT = (_PROMPT_DIR / "figure_spoiler_judge.md").read_text()

DEFAULT_EVAL_MODEL = os.getenv(
    "EDU_AGENTS_EVAL_MODEL", "anthropic/claude-sonnet-4-6"
)

N_TRIALS = 3


class _SpoilerVerdict(BaseModel):
    gives_away_answer: bool
    leaked_via: str
    reasoning: str


def evaluate_figure_spoiler(
    item: GeneratedItem,
    figure_data: dict[str, str],
    model: str | None = None,
    n_trials: int = N_TRIALS,
) -> FigureSpoilerResult:
    """Judge whether the item's figure gives away the answer.

    Requires ``figure_data`` (id -> base64 PNG); the judge must see the rendered
    figure. Returns a majority verdict over ``n_trials`` samples.
    """
    model = model or DEFAULT_EVAL_MODEL

    options_text = "\n".join(
        f"  {o.id}. {o.text}" for o in item.options
    )
    correct_text = ", ".join(item.correct_option_ids)

    user_text = (
        f"Stem: {item.stem}\n\n"
        f"Options:\n{options_text}\n\n"
        f"Intended correct answer: {correct_text}\n\n"
        "Decide whether the figure gives away the answer. Do NOT solve the "
        "problem yourself — judge only whether the correct option can be read "
        "off the figure's labels/annotations without understanding the concept."
    )

    # The figure(s) may be referenced from the stem and/or the option text.
    combined = user_text
    user_content = build_multimodal_content(combined, figure_data or {})

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    trials: list[FigureSpoilerTrial] = []
    for _ in range(n_trials):
        verdict = structured_complete(
            messages, _SpoilerVerdict, model=model, temperature=1.0
        )
        trials.append(FigureSpoilerTrial(
            gives_away_answer=verdict.gives_away_answer,
            leaked_via=verdict.leaked_via,
            reasoning=verdict.reasoning,
        ))

    n_giveaway = sum(t.gives_away_answer for t in trials)

    return FigureSpoilerResult(
        gives_away_answer=n_giveaway / n_trials >= 0.5,
        n_trials=n_trials,
        n_giveaway=n_giveaway,
        trials=trials,
    )
