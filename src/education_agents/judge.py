"""Verifier / Judge Agent."""

from __future__ import annotations

import os
from pathlib import Path

from .facets import render_facet_map_for_prompt
from .figures import build_multimodal_content
from .llm import structured_complete
from .schemas import FacetMap, GeneratedItem, JudgeReport

DEFAULT_JUDGE_MODEL = os.getenv(
    "EDU_AGENTS_JUDGE_MODEL", "anthropic/claude-sonnet-4-6"
)

_PROMPT_TEMPLATE = (
    Path(__file__).parent / "prompts" / "judge.md"
).read_text()


def _render_item_for_prompt(item: GeneratedItem) -> str:
    lines = [f"Stem: {item.stem}", f"Format: {item.response_format}", ""]
    lines.append("Options:")
    for opt in item.options:
        correct_marker = "CORRECT" if opt.is_correct else "incorrect"
        lines.append(
            f"  {opt.id}. {opt.text}\n"
            f"     Generator's tags: {', '.join(opt.facet_tags)} ({correct_marker})\n"
            f"     Rationale: {opt.rationale}"
        )
    lines.append(f"\nGenerator's explanation: {item.explanation}")
    return "\n".join(lines)


def judge_item(
    item: GeneratedItem,
    facet_map: FacetMap,
    model: str | None = None,
    figure_data: dict[str, str] | None = None,
) -> JudgeReport:
    model = model or DEFAULT_JUDGE_MODEL
    facet_text = render_facet_map_for_prompt(facet_map)
    item_text = _render_item_for_prompt(item)

    prompt = _PROMPT_TEMPLATE
    prompt = prompt.replace("{{FACET_MAP}}", facet_text)
    prompt = prompt.replace("{{ITEM}}", item_text)

    user_text = (
        "Review the item above. For each option, independently "
        "re-tag which facets it exhibits, then compare against "
        "the generator's tags. Respond with a JSON object."
    )

    # The item text is in the system prompt which may contain [FIGURE:id]
    # placeholders. Inject images into the user message so the judge can
    # see them (system messages don't support images in most providers).
    figure_content: list[dict] = []
    if figure_data:
        for fig_id, b64 in figure_data.items():
            figure_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}"},
            })

    if figure_content:
        user_content: list[dict] | str = [
            *figure_content,
            {"type": "text", "text": user_text},
        ]
    else:
        user_content = user_text

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_content},
    ]

    return structured_complete(messages, JudgeReport, model=model)
