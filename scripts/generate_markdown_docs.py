#!/usr/bin/env python3
"""Generate markdown documentation for item batches from artifact JSON files."""

import base64
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
FIGURES_DIR = DOCS_DIR / "figures"

CHECKMARK = " :white_check_mark:"


def format_response_format(fmt: str) -> str:
    return {
        "single_select": "Single Select",
        "true_false_per_option": "True False Per Option",
        "multiple_select": "Multiple Select",
    }.get(fmt, fmt)


def save_figure(fig_id: str, b64_data: str, batch_name: str, item_num: int) -> str:
    """Save base64 figure data to a PNG file, return relative path from docs/."""
    fig_dir = FIGURES_DIR / batch_name
    fig_dir.mkdir(parents=True, exist_ok=True)
    filename = f"item{item_num}_{fig_id}.png"
    filepath = fig_dir / filename
    filepath.write_bytes(base64.b64decode(b64_data))
    return f"figures/{batch_name}/{filename}"


def strip_figure_refs(stem: str) -> str:
    """Remove [FIGURE:id] placeholders and clean up surrounding whitespace/punctuation."""
    cleaned = re.sub(r"\s*\[FIGURE:\w+\]\s*", " ", stem)
    cleaned = re.sub(r"\s+([.,;:])", r"\1", cleaned)
    cleaned = re.sub(r"  +", " ", cleaned)
    return cleaned.strip()


def render_figures_block(
    figures: list, figure_data: dict, batch_name: str, item_num: int
) -> list[str]:
    """Return markdown lines for all figures in the item."""
    lines = []
    for fig in figures:
        fig_id = fig["id"]
        b64 = figure_data.get(fig_id)
        if b64:
            rel_path = save_figure(fig_id, b64, batch_name, item_num)
            alt = fig.get("alt_text", f"Figure: {fig_id}")
            lines.append(f"![{alt}]({rel_path})")
            lines.append("")
    return lines


def render_item(data: dict, item_num: int, batch_name: str) -> str:
    """Render a single item artifact to markdown."""
    item = data["item"]
    judge = data["judge_report"]
    figures = item.get("figures", [])
    figure_data = data.get("figure_data", {})

    lines = []
    facets_str = ", ".join(item["target_facets"])
    fmt_str = format_response_format(item["response_format"])

    lines.append(f"## Item {item_num}")
    lines.append("")
    lines.append(f"**Target facets:** {facets_str}  ")
    lines.append(f"**Format:** {fmt_str}  ")
    lines.append("")

    reasoning = data.get("facet_selection_reasoning", "")
    if reasoning:
        lines.append(f"> **Facet selection reasoning:** {reasoning}")
        lines.append("")

    # Stem
    lines.append("### Stem")
    lines.append("")
    stem = item["stem"]
    if figures and figure_data:
        stem = strip_figure_refs(stem)
    lines.append(stem)
    lines.append("")

    # Figures
    if figures and figure_data:
        fig_lines = render_figures_block(figures, figure_data, batch_name, item_num)
        lines.extend(fig_lines)

    # Options
    lines.append("### Options")
    lines.append("")
    for opt in item["options"]:
        oid = opt["id"]
        text = opt["text"]
        is_correct = opt.get("is_correct", False)
        if not is_correct and "correct_option_ids" in item:
            is_correct = oid in item["correct_option_ids"]
        mark = CHECKMARK if is_correct else ""
        facet_tags = ", ".join(opt.get("facet_tags", []))
        rationale = opt.get("rationale", "")

        lines.append(f"**{oid}.** {text}{mark}  ")
        lines.append(f"*Facets: {facet_tags}*  ")
        lines.append(f"*Rationale: {rationale}*")
        lines.append("")

    # Explanation
    explanation = item.get("explanation", "")
    if explanation:
        lines.append("### Explanation")
        lines.append("")
        lines.append(explanation)
        lines.append("")

    # Judge report
    lines.append("### Judge Report")
    lines.append("")
    assessments = judge.get("option_assessments", [])
    matched = sum(1 for a in assessments if a["agreement"] == "match")
    total = len(assessments)
    lines.append(f"**Overall agreement:** {matched}/{total} options matched  ")

    issues = judge.get("issues", [])
    if issues:
        if isinstance(issues, list):
            lines.append(f"**Issues:** {' '.join(issues)}  ")
        else:
            lines.append(f"**Issues:** {issues}  ")
    else:
        lines.append("**Issues:** None  ")
    lines.append("")

    lines.append("| Option | Generator Tags | Judge Tags | Agreement | Confidence |")
    lines.append("|--------|---------------|------------|-----------|------------|")
    for a in assessments:
        gen_tags = ", ".join(a.get("generator_tags", []))
        judge_tags = ", ".join(a.get("judge_tags", []))
        lines.append(
            f"| {a['option_id']} | {gen_tags} | {judge_tags} | {a['agreement']} | {a['confidence']} |"
        )
    lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def generate_markdown(
    output_dir: str,
    title: str,
    header_meta: dict,
    batch_name: str,
) -> str:
    """Generate full markdown for a batch of items."""
    output_path = Path(output_dir)
    files = sorted(output_path.glob("*.json"))

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    for key, val in header_meta.items():
        lines.append(f"**{key}:** {val}  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, fp in enumerate(files, 1):
        with open(fp) as f:
            data = json.load(f)
        lines.append(render_item(data, i, batch_name))

    return "\n".join(lines)


BATCHES = [
    {
        "dir": "outputs/third_pass_with_edpsy",
        "output_file": "docs/generated_items_third_pass_with_edpsy.md",
        "batch_name": "third_pass_with_edpsy",
        "title": "Generated Items — Third Pass (V2 Prompt, Gemini 3 Flash, EDPSY Book Context)",
        "meta": {
            "Generator model": "Gemini 3 Flash Preview",
            "Judge model": "Gemini 3.1 Pro Preview",
            "Topic": "Confidence Intervals",
            "Items": "10",
            "Prompt version": "V2 (latent-facet design)",
            "Format": "Dynamic (model chooses)",
            "Book context": "Full textbook (EDPSY 490 Chapter 5)",
        },
    },
    {
        "dir": "outputs/third_pass_sonnet-4-6",
        "output_file": "docs/generated_items_third_pass_sonnet-4-6.md",
        "batch_name": "third_pass_sonnet_4_6",
        "title": "Generated Items — Third Pass (V2 Prompt, Claude Sonnet 4.6, Dynamic Format)",
        "meta": {
            "Generator model": "Claude Sonnet 4.6",
            "Judge model": "Gemini 3.1 Pro Preview",
            "Topic": "Confidence Intervals",
            "Items": "10",
            "Prompt version": "V2 (latent-facet design)",
            "Format": "Dynamic (model chooses)",
        },
    },
    {
        "dir": "outputs/gemini-flash-prompt-with-images",
        "output_file": "docs/generated_items_gemini_flash_v3_with_figures.md",
        "batch_name": "gemini_flash_v3_figures",
        "title": "Generated Items — V3 Prompt with Figures (Gemini 3 Flash)",
        "meta": {
            "Generator model": "Gemini 3 Flash Preview",
            "Judge model": "Gemini 3.1 Pro Preview",
            "Topic": "Confidence Intervals",
            "Items": "10",
            "Prompt version": "V3 (figure-encouraged, LaTeX notation)",
            "Format": "Dynamic (model chooses)",
        },
    },
    {
        "dir": "outputs/sonnet-4-6-prompt-with-images",
        "output_file": "docs/generated_items_sonnet_4_6_v3_with_figures.md",
        "batch_name": "sonnet_4_6_v3_figures",
        "title": "Generated Items — V3 Prompt with Figures (Claude Sonnet 4.6)",
        "meta": {
            "Generator model": "Claude Sonnet 4.6",
            "Judge model": "Gemini 3.1 Pro Preview",
            "Topic": "Confidence Intervals",
            "Items": "10",
            "Prompt version": "V3 (figure-encouraged, LaTeX notation)",
            "Format": "Dynamic (model chooses)",
        },
    },
]


def main():
    for batch in BATCHES:
        input_dir = REPO_ROOT / batch["dir"]
        output_file = REPO_ROOT / batch["output_file"]

        if not input_dir.exists():
            print(f"SKIP {batch['dir']}: directory not found")
            continue

        md = generate_markdown(
            str(input_dir),
            batch["title"],
            batch["meta"],
            batch["batch_name"],
        )
        output_file.write_text(md)
        print(f"WROTE {batch['output_file']}")


if __name__ == "__main__":
    main()
