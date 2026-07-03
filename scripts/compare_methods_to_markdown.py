#!/usr/bin/env python3
"""Render the belief-vs-few-shot comparison (a .jsonl/.json of MethodItemResult)
into a readable markdown report with reasoning traces, so the simulator quality
can be reviewed per misconception.

For each tested item it shows the stem + options (target/correct marked), then a
belief subsection and a few-shot subsection: the per-sample hit/score table plus
full reasoning traces (a hit and a miss when both exist).

Usage:
    python scripts/compare_methods_to_markdown.py outputs/compare_methods_gemini.jsonl \
        --out docs/compare_methods_gemini.md
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from education_agents.evaluation.correctness import canonicalize_ids
from education_agents.evaluation.schemas import MethodItemResult
from education_agents.evaluation.sim_corpus import load_corpus
from education_agents.facets import load_facet_map


def load_results(path: Path) -> list[MethodItemResult]:
    text = path.read_text()
    if path.suffix == ".jsonl":
        rows = [json.loads(l) for l in text.splitlines() if l.strip()]
    else:
        rows = json.loads(text)
    return [MethodItemResult.model_validate(r) for r in rows]


def pick_traces(attempts, n):
    """Prefer one hit + one miss; otherwise fill from whichever exists."""
    hits = [a for a in attempts if a.hit]
    misses = [a for a in attempts if not a.hit]
    chosen = []
    if hits:
        chosen.append(("hit", hits[0]))
    if misses:
        chosen.append(("miss", misses[0]))
    pool = (hits[1:] + misses[1:])
    while len(chosen) < n and pool:
        a = pool.pop(0)
        chosen.append(("hit" if a.hit else "miss", a))
    return chosen[:n]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", help="Path to MethodItemResult .jsonl or .json")
    parser.add_argument("--topic", default="confidence_intervals")
    parser.add_argument("--traces-per-method", type=int, default=2)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    res_path = Path(args.results)
    results = load_results(res_path)
    facet_map = load_facet_map(args.topic)
    facet_text = {f.id: f.text for f in facet_map.facets}
    item_by_source = {it.source: it for it in load_corpus(facet_map)}

    # Recompute hits with robust id canonicalization (the streamed hit flags used
    # brittle exact-id matching, which produced false misses on format mismatch).
    for r in results:
        item = item_by_source.get(r.source)
        if not item:
            continue
        option_ids = [o.id for o in item.options]
        for a in r.attempts:
            a.hit = r.target_option_id in canonicalize_ids(a.selected_ids, option_ids)
        hits = [a for a in r.attempts if a.hit]
        r.n_hits = len(hits)
        r.hit_rate = len(hits) / r.k_samples if r.k_samples else 0.0

    # Pair belief + fewshot per (group, item), ordered by group then source.
    paired: dict[tuple, dict] = {}
    for r in results:
        paired.setdefault((r.group_key, r.source), {})[r.method] = r

    def fmt(x, pct=False):
        if x is None:
            return "—"
        return f"{x:.0%}" if pct else f"{x:.1f}"

    out = []
    out.append(f"# Belief vs. Few-shot — Misconception Elicitation\n")
    out.append(f"Source: `{res_path.name}`\n")

    # Overall summary
    def avg(xs):
        xs = [x for x in xs if x is not None]
        return sum(xs) / len(xs) if xs else None
    out.append("## Overall\n")
    out.append("| method | mean hit | fidelity (hits) | naturalness (hits) |")
    out.append("|---|---|---|---|")
    for m in ("belief", "fewshot"):
        rs = [r for r in results if r.method == m]
        if not rs:
            continue
        out.append(f"| {m} | {fmt(avg([r.hit_rate for r in rs]), True)} | "
                   f"{fmt(avg([r.fidelity_among_hits for r in rs]), True)} | "
                   f"{fmt(avg([r.naturalness_among_hits for r in rs]))} |")
    out.append("\n> hit = model selected the misconception-keyed option (ids "
               "canonicalized, so `opt_1`/`opt_A` match `A`); fidelity = judge "
               "confirmed the reasoning exhibits the misconception; naturalness = "
               "1–5 authenticity of reasoning.\n")
    out.append("> ⚠️ Fidelity/naturalness were only scored on samples that hit "
               "under the original (brittle) matcher, so per-row averages may not "
               "cover every canonicalized hit. Hit rates below are corrected.\n")

    for (group_key, source), methods in sorted(paired.items()):
        any_r = next(iter(methods.values()))
        item = item_by_source.get(source)
        out.append("\n---\n")
        out.append(f"## `{group_key}` · `{source}`\n")
        for fid in group_key.split("+"):
            out.append(f"- **{fid}**: {facet_text.get(fid, fid)}")
        out.append("")

        if item:
            out.append(f"**Stem:** {item.stem}\n")
            out.append("**Options:**")
            for o in item.options:
                tags = f" _[{', '.join(o.facet_tags)}]_" if o.facet_tags else ""
                flags = []
                if o.is_correct:
                    flags.append("✓correct")
                if o.id == any_r.target_option_id:
                    flags.append("←target")
                flag = f" **({', '.join(flags)})**" if flags else ""
                out.append(f"- `{o.id}`. {o.text}{tags}{flag}")
            out.append("")

        for method in ("belief", "fewshot"):
            r = methods.get(method)
            if not r:
                continue
            shot_note = f", {r.n_shots} shots" if method == "fewshot" else ""
            out.append(f"### {method}  —  hit {r.hit_rate:.0%} ({r.n_hits}/{r.k_samples}{shot_note})  ·  "
                       f"fidelity {fmt(r.fidelity_among_hits, True)}  ·  "
                       f"naturalness {fmt(r.naturalness_among_hits)}\n")

            # Per-sample summary table
            out.append("| # | picked | hit | exhibits | natural |")
            out.append("|---|---|---|---|---|")
            for i, a in enumerate(r.attempts, 1):
                ex = "—" if a.exhibits_misconception is None else ("yes" if a.exhibits_misconception else "no")
                nat = "—" if a.naturalness is None else str(a.naturalness)
                out.append(f"| {i} | `{', '.join(a.selected_ids) or a.answer[:20]}` | "
                           f"{'✓' if a.hit else '✗'} | {ex} | {nat} |")
            out.append("")

            # Full reasoning traces
            for label, a in pick_traces(r.attempts, args.traces_per_method):
                mark = "✓ hit" if a.hit else "✗ miss"
                out.append(f"**Trace ({mark}):**\n")
                out.append(f"> {a.reasoning.strip().replace(chr(10), chr(10) + '> ')}\n")
                out.append(f"**Answer:** {a.answer.strip()}\n")

    md = "\n".join(out)
    out_path = Path(args.out) if args.out else res_path.with_suffix(".md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)
    print(f"Wrote {out_path}  ({len(results)} method-results, {len(paired)} items)")


if __name__ == "__main__":
    main()
