#!/usr/bin/env python3
"""Belief-injection select-mode check with a small student model.

How often does a misconception-bearing student actually pick the keyed option?
For each miss, a judge says whether it's a simulator problem or an item problem.
Defaults to expert items only (most reliable).
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from education_agents.evaluation.schemas import SelectorItemResult
from education_agents.evaluation.selector_check import run_selector_check_on_item
from education_agents.evaluation.sim_corpus import (
    build_persona_trials,
    coverage_summary,
    load_corpus,
    load_experts,
)
from education_agents.facets import load_facet_map


def print_report(results: list[SelectorItemResult]):
    print("\n" + "=" * 72)
    print("  PER-ITEM HIT RATE (belief-injection, select mode)")
    print("=" * 72)
    print(f"{'group':10s} {'item':24s} {'hit':>6s} {'k':>3s}")
    print("-" * 72)
    for r in sorted(results, key=lambda r: (r.group_key, r.source)):
        print(f"{r.group_key:10s} {r.source.split('/')[-1][:24]:24s} "
              f"{r.hit_rate:>5.0%} {r.k_samples:>3d}")

    total = sum(r.k_samples for r in results)
    hits = sum(r.n_hits for r in results)
    miss_cats = Counter()
    for r in results:
        for a in r.attempts:
            if not a.hit and a.miss_category:
                miss_cats[a.miss_category] += 1

    print("\n" + "=" * 72)
    print("  OVERALL")
    print("=" * 72)
    print(f"  hit rate: {hits}/{total} = {hits/total:.0%}" if total else "  no samples")

    n_miss = total - hits
    if n_miss:
        print(f"\n  MISS DIAGNOSIS ({n_miss} misses):")
        for cat, c in miss_cats.most_common():
            kind = "ITEM" if cat == "item_not_diagnostic" else "SIM"
            print(f"    [{kind:4s}] {cat:24s} {c:>3d}  ({c/n_miss:.0%})")
        sim = sum(v for k, v in miss_cats.items() if k != "item_not_diagnostic")
        item = miss_cats.get("item_not_diagnostic", 0)
        print(f"    => simulator-attributed: {sim}/{n_miss} ({sim/n_miss:.0%}), "
              f"item-attributed: {item}/{n_miss} ({item/n_miss:.0%})")

    # Items where the misconception looks non-diagnostic (>=half misses are item)
    print("\n  ITEMS FLAGGED (>=1 'item_not_diagnostic' miss):")
    flagged = False
    for r in sorted(results, key=lambda r: (r.group_key, r.source)):
        item_misses = sum(
            1 for a in r.attempts if a.miss_category == "item_not_diagnostic"
        )
        if item_misses:
            flagged = True
            print(f"    {r.group_key:8s} {r.source:40s} {item_misses}/{r.k_samples} item-misses")
    if not flagged:
        print("    (none)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="confidence_intervals")
    parser.add_argument("--student-model", default="anthropic/claude-haiku-4-5")
    parser.add_argument("--judge-model", default=None)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--groups", default=None,
                        help="Comma-separated groups to restrict to (default: all)")
    parser.add_argument("--include-generated", action="store_true",
                        help="Also include generated items (default: expert only)")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out", default="outputs/selector_check_haiku.json")
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()

    facet_map = load_facet_map(args.topic)
    if args.include_generated:
        items = load_corpus(facet_map)
    else:
        items = load_experts(facet_map)
    print(f"Loaded {len(items)} items "
          f"({'corpus' if args.include_generated else 'expert-only'})")

    groups = build_persona_trials(items, facet_map)
    print("\n" + coverage_summary(groups))

    wanted = set(g.strip() for g in args.groups.split(",")) if args.groups else None
    trials = [t for ts in groups.values() for t in ts
              if wanted is None or t.group_key in wanted]
    trials.sort(key=lambda t: (t.group_key, t.item.source, t.target_option_id))
    if args.limit:
        trials = trials[: args.limit]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stream_path = out_path.with_suffix(".jsonl")

    done = {}
    if args.fresh and stream_path.exists():
        stream_path.unlink()
    if stream_path.exists():
        for line in stream_path.read_text().splitlines():
            if line.strip():
                r = SelectorItemResult.model_validate_json(line)
                done[(r.source, r.group_key, r.target_option_id)] = r
        print(f"Resuming: {len(done)} trials already recorded")

    results = list(done.values())
    print(f"\nRunning {len(trials)} trials x k={args.k} "
          f"(student={args.student_model})...")
    with open(stream_path, "a") as sf:
        for i, t in enumerate(trials, 1):
            key = (t.item.source, t.group_key, t.target_option_id)
            if key in done:
                continue
            r = run_selector_check_on_item(
                t, facet_map, k=args.k,
                student_model=args.student_model, judge_model=args.judge_model,
            )
            results.append(r)
            sf.write(r.model_dump_json() + "\n")
            sf.flush()
            print(f"  [{i}/{len(trials)}] {t.group_key:10s} "
                  f"{t.item.source.split('/')[-1]:14s} hit={r.hit_rate:.0%}")

    print_report(results)
    out_path.write_text(json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False))
    print(f"\nSaved to {out_path}  (stream: {stream_path.name})")


if __name__ == "__main__":
    main()
