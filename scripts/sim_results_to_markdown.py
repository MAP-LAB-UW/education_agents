#!/usr/bin/env python3
"""Render student-simulator results (a .jsonl stream of PersonaResult rows) into
a readable markdown report, joining each result back to its item so the problem
stem and options are shown alongside the student's reasoning and the judge.

Usage:
    python scripts/sim_results_to_markdown.py outputs/sim_eval_full_open_sonnet.jsonl \
        --out docs/sim_eval_full_open_sonnet.md
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from education_agents.evaluation.schemas import PersonaResult
from education_agents.evaluation.sim_corpus import build_persona_trials, load_corpus
from education_agents.facets import load_facet_map


def load_results(jsonl_path: Path) -> list[PersonaResult]:
    rows = []
    for line in jsonl_path.read_text().splitlines():
        if line.strip():
            rows.append(PersonaResult.model_validate_json(line))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", help="Path to the PersonaResult .jsonl stream")
    parser.add_argument("--topic", default="confidence_intervals")
    parser.add_argument("--out", default=None, help="Output markdown path")
    args = parser.parse_args()

    jsonl_path = Path(args.jsonl)
    results = load_results(jsonl_path)
    facet_map = load_facet_map(args.topic)
    facet_text = {f.id: f.text for f in facet_map.facets}

    # Index items by source so we can show the stem + options for each result.
    items = load_corpus(facet_map)
    item_by_source = {it.source: it for it in items}

    # Group results by misconception group, then sort groups weakest-first.
    by_group: dict[str, list[PersonaResult]] = {}
    for r in results:
        by_group.setdefault(r.group_key, []).append(r)

    def fidelity(rs):
        return sum(r.exhibits_misconception for r in rs) / len(rs)

    n = len(results)
    n_ex = sum(r.exhibits_misconception for r in results)

    out = []
    out.append(f"# Student Simulator Results — `{jsonl_path.name}`\n")
    out.append(f"**Overall fidelity:** {n_ex}/{n} = {n_ex / n:.0%}  "
               f"({len(by_group)} misconception groups)\n")
    out.append("Groups are ordered weakest-first. ✓ = reasoning exhibited the "
               "misconception; ✗ = it did not.\n")

    # Summary table
    out.append("| Group | kind | fidelity | n |")
    out.append("|---|---|---|---|")
    for key in sorted(by_group, key=lambda k: (fidelity(by_group[k]), k)):
        rs = by_group[key]
        kind = "multi" if "+" in key else "single"
        out.append(f"| `{key}` | {kind} | {fidelity(rs):.0%} | {len(rs)} |")
    out.append("")

    for key in sorted(by_group, key=lambda k: (fidelity(by_group[k]), k)):
        rs = by_group[key]
        out.append(f"\n---\n\n## `{key}` — fidelity {fidelity(rs):.0%} "
                   f"({sum(r.exhibits_misconception for r in rs)}/{len(rs)})\n")
        for fid in key.split("+"):
            out.append(f"- **{fid}**: {facet_text.get(fid, fid)}")
        out.append("")

        # Failures first within a group, for quick review.
        for r in sorted(rs, key=lambda r: r.exhibits_misconception):
            mark = "✓" if r.exhibits_misconception else "✗"
            item = item_by_source.get(r.source)
            out.append(f"### {mark} `{r.source}` · {r.mode}\n")
            if item:
                out.append(f"**Stem:** {item.stem}\n")
                out.append("**Options:**")
                for o in item.options:
                    tags = f" _[{', '.join(o.facet_tags)}]_" if o.facet_tags else ""
                    flags = []
                    if o.is_correct:
                        flags.append("✓correct")
                    if o.id == r.target_option_id:
                        flags.append("←target")
                    flag = f" **({', '.join(flags)})**" if flags else ""
                    out.append(f"- `{o.id}`. {o.text}{tags}{flag}")
                out.append("")
            out.append(f"**Student reasoning:** {r.student_reasoning}\n")
            out.append(f"**Student answer:** {r.student_answer}\n")
            verdict = "EXHIBITS" if r.exhibits_misconception else "DOES NOT exhibit"
            out.append(f"**Judge ({verdict}):** {r.judge_reasoning}\n")

    md = "\n".join(out)
    out_path = Path(args.out) if args.out else jsonl_path.with_suffix(".md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)
    print(f"Wrote {out_path}  ({n} results, {len(by_group)} groups)")


if __name__ == "__main__":
    main()
