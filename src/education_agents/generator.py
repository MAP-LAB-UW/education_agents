"""Item Generation Agent."""

from __future__ import annotations

import os
from pathlib import Path

from .facets import render_examples_for_prompt, render_facet_map_for_prompt
from .llm import structured_complete
from .schemas import FacetMap, FacetSelection, GeneratedItem, GenerationRequest

DEFAULT_GENERATOR_MODEL = os.getenv(
    "EDU_AGENTS_GENERATOR_MODEL", "anthropic/claude-sonnet-4-6"
)

_PROMPT_DIR = Path(__file__).parent / "prompts"
_PROMPT_TEMPLATES = {
    "v1": (_PROMPT_DIR / "generator.md").read_text(),
    "v2": (_PROMPT_DIR / "generator_v2.md").read_text(),
    "v3": (_PROMPT_DIR / "generator_v3.md").read_text(),
}

# Appended to the user message when this item is selected to carry a figure.
# It demands a *load-bearing* figure (passing the deletion test), not a
# decorative one — otherwise the figure-necessity rubric would flag it.
FIGURE_REQUIRED_DIRECTIVE = (
    "\n\nFIGURE REQUIRED FOR THIS ITEM: This item must include at least one "
    "figure, and the figure must be load-bearing — design the item around it so "
    "it cannot be solved from the text alone. Move the essential quantitative "
    "information (values, bounds, distribution shape, spread, interval "
    "endpoints) into the figure only, and do NOT restate those values in the "
    "stem, so that deleting the figure would make the item unanswerable or "
    "ambiguous. Choose a scenario and facet framing where a graph is genuinely "
    "diagnostic (e.g. reading a sampling distribution, comparing the overlap of "
    "two confidence intervals, interpreting a histogram). Do not add a "
    "decorative figure whose information is already in the text."
)


def select_facets(
    facet_map: FacetMap,
    previously_used: list[list[str]],
    model: str | None = None,
) -> FacetSelection:
    model = model or DEFAULT_GENERATOR_MODEL
    facet_text = render_facet_map_for_prompt(facet_map)

    history_section = ""
    if previously_used:
        history_lines = [
            f"  Item {i + 1}: {', '.join(combo)}"
            for i, combo in enumerate(previously_used)
        ]
        history_section = (
            "\n\n## Previously Used Facet Combinations\n\n"
            "The following facet combinations have already been used to "
            "generate items in this batch. Choose a DIFFERENT combination "
            "to ensure diversity across the item set.\n\n"
            + "\n".join(history_lines)
        )

    system_prompt = (
        "You are an expert assessment designer for an introductory statistics "
        "course on confidence intervals. Your task is to select a set of "
        "target facets for a new diagnostic multiple-choice item.\n\n"
        "## Facet Map\n\n"
        f"{facet_text}\n\n"
        "## Selection Guidelines\n\n"
        "- Pick 2–4 facets that form a coherent diagnostic item.\n"
        "- Include at least one goal facet (A-prefix) and at least one "
        "problematic facet (B-prefix).\n"
        "- Choose facets that are conceptually related so the item stem "
        "can naturally distinguish them.\n"
        "- Prioritize under-covered facets and novel combinations."
        f"{history_section}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                "Select target facets for the next diagnostic item. "
                "Return your chosen facet IDs and a brief reasoning."
            ),
        },
    ]

    return structured_complete(messages, FacetSelection, model=model)


def _build_system_prompt(
    request: GenerationRequest,
    facet_map: FacetMap,
    book_context: str | None,
) -> str:
    facet_text = render_facet_map_for_prompt(facet_map)
    examples_text = render_examples_for_prompt(
        facet_map, exclude_image_examples=request.exclude_image_examples
    )

    book_section = ""
    if book_context:
        book_section = (
            "## Reference Book Chapter\n\n"
            "Use the following textbook content as grounding material "
            "when writing the item. Align terminology, notation, and "
            "conceptual framing with this chapter.\n\n"
            f"<book_chapter>\n{book_context}\n</book_chapter>"
        )

    target_facets_str = ", ".join(request.target_facets)

    format_str = (
        request.response_format
        if request.response_format
        else "Choose the best format (single_select, multi_select, or true_false_per_option) for the target facets"
    )
    num_options_str = (
        str(request.num_options)
        if request.num_options
        else "Choose the best number of options (typically 3–6) for the item"
    )

    prompt = _PROMPT_TEMPLATES[request.prompt_version]
    prompt = prompt.replace("{{FACET_MAP}}", facet_text)
    prompt = prompt.replace("{{EXAMPLES}}", examples_text)
    prompt = prompt.replace("{{BOOK_CONTEXT}}", book_section)
    prompt = prompt.replace("{{TARGET_FACETS}}", target_facets_str)
    prompt = prompt.replace("{{RESPONSE_FORMAT}}", format_str)
    prompt = prompt.replace("{{NUM_OPTIONS}}", num_options_str)

    return prompt


def generate_item(
    request: GenerationRequest,
    facet_map: FacetMap,
    book_context: str | None = None,
    model: str | None = None,
    force_figure: bool = False,
) -> GeneratedItem:
    model = model or DEFAULT_GENERATOR_MODEL
    system_prompt = _build_system_prompt(request, facet_map, book_context)

    facets_str = ", ".join(request.target_facets)
    if request.response_format and request.num_options:
        user_content = (
            f"Generate a {request.response_format} item with "
            f"{request.num_options} options diagnosing facets: {facets_str}."
        )
    elif request.response_format:
        user_content = (
            f"Generate a {request.response_format} item diagnosing "
            f"facets: {facets_str}. Choose the best number of options."
        )
    elif request.num_options:
        user_content = (
            f"Generate an item with {request.num_options} options "
            f"diagnosing facets: {facets_str}. Choose the best response format."
        )
    else:
        user_content = (
            f"Generate an item diagnosing facets: {facets_str}. "
            f"Choose the best response format and number of options."
        )

    if force_figure:
        user_content += FIGURE_REQUIRED_DIRECTIVE

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    return structured_complete(messages, GeneratedItem, model=model)
