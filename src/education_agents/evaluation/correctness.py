"""Correctness rubric: have a strong LLM solve the item blind."""

from __future__ import annotations

import os
import re

from pydantic import BaseModel

from ..figures import build_multimodal_content
from ..llm import structured_complete
from ..schemas import GeneratedItem
from .schemas import CorrectnessResult

_FIGURE_REF_RE = re.compile(r"\[FIGURE:[^\]]*\]")


def parse_selected_ids(raw: str) -> set[str]:
    """Parse LLM selected_answer into clean option IDs, stripping figure refs."""
    cleaned = _FIGURE_REF_RE.sub("", raw)
    ids = set()
    for part in cleaned.split(","):
        part = part.strip().rstrip(".")
        if part:
            ids.add(part)
    return ids


def canonicalize_ids(raw_ids, option_ids: list[str]) -> set[str]:
    """Map loosely-formatted picked ids onto the item's actual option ids.

    Models echo option ids inconsistently — ``opt_1`` (positional) vs ``A``
    (letter), ``opt_A`` vs ``A``, different case. This resolves each picked
    token to one of ``option_ids`` so hit detection is robust to formatting.
    Unresolvable tokens are passed through unchanged.
    """
    lower = {o.lower(): o for o in option_ids}
    out: set[str] = set()
    for token in raw_ids:
        s = token.strip().lower().rstrip(".")
        if s.startswith("opt_"):
            s = s[4:]
        elif s.startswith("opt"):
            s = s[3:]
        if s in lower:
            out.add(lower[s]); continue
        if ("opt_" + s) in lower:
            out.add(lower["opt_" + s]); continue
        if s.isdigit() and 0 <= int(s) - 1 < len(option_ids):
            out.add(option_ids[int(s) - 1]); continue
        if len(s) == 1 and s.isalpha() and 0 <= ord(s) - ord("a") < len(option_ids):
            out.add(option_ids[ord(s) - ord("a")]); continue
        out.add(token)
    return out


DEFAULT_EVAL_MODEL = os.getenv(
    "EDU_AGENTS_EVAL_MODEL", "anthropic/claude-sonnet-4-6"
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
    figure_data: dict[str, str] | None = None,
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

    user_text = (
        f"Stem: {item.stem}\n\n"
        f"Options:\n{options_text}"
        f"{format_note}\n\n"
        "Solve this problem. Select the best answer and flag any "
        "distractors that could also be defensibly correct."
    )

    user_content = build_multimodal_content(user_text, figure_data or {})

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    result = structured_complete(messages, _LLMAnswer, model=model)

    selected_ids = parse_selected_ids(result.selected_answer)
    correct_ids = set(item.correct_option_ids)
    is_correct = selected_ids == correct_ids

    return CorrectnessResult(
        selected_answer=result.selected_answer,
        correct_answer_ids=item.correct_option_ids,
        is_correct=is_correct,
        flagged_distractors=result.flagged_distractors,
        reasoning=result.reasoning,
    )
