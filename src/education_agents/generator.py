"""Item Generation Agent."""

from __future__ import annotations

import os
from pathlib import Path

from .facets import render_examples_for_prompt, render_facet_map_for_prompt
from .llm import structured_complete
from .schemas import FacetMap, FacetSelection, GeneratedItem, GenerationRequest

DEFAULT_GENERATOR_MODEL = os.getenv(
    "EDU_AGENTS_GENERATOR_MODEL", "gemini/gemini-3-flash-preview"
)

_PROMPT_TEMPLATE = (
    Path(__file__).parent / "prompts" / "generator.md"
).read_text()


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

    prompt = _PROMPT_TEMPLATE
    prompt = prompt.replace("{{FACET_MAP}}", facet_text)
    prompt = prompt.replace("{{EXAMPLES}}", examples_text)
    prompt = prompt.replace("{{BOOK_CONTEXT}}", book_section)
    prompt = prompt.replace("{{TARGET_FACETS}}", target_facets_str)
    prompt = prompt.replace("{{RESPONSE_FORMAT}}", request.response_format)
    prompt = prompt.replace("{{NUM_OPTIONS}}", str(request.num_options))

    return prompt


def generate_item(
    request: GenerationRequest,
    facet_map: FacetMap,
    book_context: str | None = None,
    model: str | None = None,
) -> GeneratedItem:
    model = model or DEFAULT_GENERATOR_MODEL
    system_prompt = _build_system_prompt(request, facet_map, book_context)

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"Generate a {request.response_format} item with "
                f"{request.num_options} options diagnosing facets: "
                f"{', '.join(request.target_facets)}."
            ),
        },
    ]

    return structured_complete(messages, GeneratedItem, model=model)
