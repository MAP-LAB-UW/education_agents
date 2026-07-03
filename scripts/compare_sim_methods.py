#!/usr/bin/env python3
"""Head-to-head: belief-injection vs. few-shot persona for eliciting misconceptions.

For each selected item we run both methods in select mode, sampling K times, and
report hit rate, judge-confirmed fidelity among hits, and an LLM naturalness
score of the reasoning. Few-shot draws sibling problems from the same
misconception group (misconception never named).

Figure-bearing items are skipped to avoid cross-item multimodal merging.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from education_agents.evaluation.answer_conditioned import run_method_on_item
from education_agents.evaluation.schemas import ComparisonReport, MethodItemResult
from education_agents.evaluation.sim_corpus import build_persona_trials, load_corpus
from education_agents.facets import load_facet_map


def is_figure_free(item) -> bool:
    blobs = [item.stem] + [o.text for o in item.options]
    return not any(("[FIGURE:" in t or "@'" in t) for t in blobs)


def select_targets(groups, group_keys, per_group):
    """Pick per_group figure-free target trials for each requested group."""
    targets = {}
    for key in group_keys:
        trials = [t for t in groups.get(key, []) if is_figure_free(t.item)]
        # de-dup by source so shots and target never coincide trivially
        seen, picked = set(), []
        for t in sorted(trials, key=lambda t: t.item.source):
            if t.item.source in seen:
                continue
            seen.add(t.item.source)
            picked.append(t)
        targets[key] = picked
    return targets


def build_shots(groups, key, target_source, n_shots):
    """Pick up to n_shots sibling shots, stratified round-robin across source
    corpora so exemplars don't cluster in one corpus."""
    candidates = [
        s for s in sorted(groups.get(key, []), key=lambda t: t.item.source)
        if s.item.source != target_source and is_figure_free(s.item)
    ]
    by_corpus: dict[str, list] = {}
    for s in candidates:
        by_corpus.setdefault(s.item.source.split("/")[0], []).append(s)

    shots = []
    while len(shots) < n_shots and any(by_corpus.values()):
        for corpus in sorted(by_corpus):
            if by_corpus[corpus]:
                s = by_corpus[corpus].pop(0)
                shots.append((s.item, s.target_option_id))
                if len(shots) >= n_shots:
                    break
    return shots


def print_summary(results: list[MethodItemResult]):
    print("\n" + "=" * 78)
    print("  PER-ITEM COMPARISON")
    print("=" * 78)
    print(f"{'group':10s} {'item':22s} {'method':8s} {'hit':>6s} {'fidelity':>9s} {'natural':>8s}")
    print("-" * 78)
    by_key = {}
    for r in sorted(results, key=lambda r: (r.group_key, r.source, r.method)):
        by_key.setdefault((r.group_key, r.method), []).append(r)
        fid = f"{r.fidelity_among_hits:.0%}" if r.fidelity_among_hits is not None else "—"
        nat = f"{r.naturalness_among_hits:.1f}" if r.naturalness_among_hits is not None else "—"
        print(f"{r.group_key:10s} {r.source.split('/')[-1][:22]:22s} {r.method:8s} "
              f"{r.hit_rate:>5.0%} {fid:>9s} {nat:>8s}")

    print("\n" + "=" * 78)
    print("  AGGREGATE BY GROUP x METHOD  (fidelity/natural averaged over items with >=1 hit)")
    print("=" * 78)
    print(f"{'group':10s} {'method':8s} {'mean hit':>9s} {'fidelity':>9s} {'natural':>8s}")
    print("-" * 78)

    def avg(xs):
        xs = [x for x in xs if x is not None]
        return sum(xs) / len(xs) if xs else None

    for (key, method), rs in sorted(by_key.items()):
        mh = avg([r.hit_rate for r in rs])
        fid = avg([r.fidelity_among_hits for r in rs])
        nat = avg([r.naturalness_among_hits for r in rs])
        print(f"{key:10s} {method:8s} {mh:>8.0%} "
              f"{(f'{fid:.0%}' if fid is not None else '—'):>9s} "
              f"{(f'{nat:.1f}' if nat is not None else '—'):>8s}")

    print("\n  OVERALL BY METHOD")
    for method in ("belief", "fewshot"):
        rs = [r for r in results if r.method == method]
        if not rs:
            continue
        mh = avg([r.hit_rate for r in rs])
        fid = avg([r.fidelity_among_hits for r in rs])
        nat = avg([r.naturalness_among_hits for r in rs])
        print(f"    {method:8s}  hit={mh:.0%}  "
              f"fidelity={(f'{fid:.0%}' if fid is not None else '—')}  "
              f"naturalness={(f'{nat:.2f}' if nat is not None else '—')}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="confidence_intervals")
    parser.add_argument("--groups", default="B17,B8,B9,B15",
                        help="Comma-separated misconception groups to test")
    parser.add_argument("--per-group", type=int, default=2)
    parser.add_argument("--n-shots", type=int, default=4)
    parser.add_argument("--k", type=int, default=6, help="Samples per (item, method)")
    parser.add_argument("--student-model", default=None)
    parser.add_argument("--judge-model", default=None)
    parser.add_argument("--out", default="outputs/compare_methods.json")
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()

    group_keys = [g.strip() for g in args.groups.split(",") if g.strip()]
    facet_map = load_facet_map(args.topic)
    items = load_corpus(facet_map)
    groups = build_persona_trials(items, facet_map)
    targets = select_targets(groups, group_keys, args.per_group)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stream_path = out_path.with_suffix(".jsonl")

    done: dict[tuple, MethodItemResult] = {}
    if args.fresh and stream_path.exists():
        stream_path.unlink()
    if stream_path.exists():
        for line in stream_path.read_text().splitlines():
            if line.strip():
                r = MethodItemResult.model_validate_json(line)
                done[(r.method, r.source, r.group_key, r.target_option_id)] = r
        print(f"Resuming: {len(done)} (item, method) results already recorded")

    # Build the work list.
    work = []  # (method, trial, shots)
    for key in group_keys:
        picked = targets.get(key, [])[: args.per_group]
        if not picked:
            print(f"  [warn] no figure-free items for group {key}")
        for t in picked:
            shots = build_shots(groups, key, t.item.source, args.n_shots)
            work.append(("belief", t, []))
            if shots:
                work.append(("fewshot", t, shots))
            else:
                print(f"  [warn] no sibling shots for {key}/{t.item.source}; skipping fewshot")

    results: list[MethodItemResult] = list(done.values())
    print(f"\nPlanned {len(work)} (item, method) runs x k={args.k}")
    with open(stream_path, "a") as sf:
        for i, (method, t, shots) in enumerate(work, 1):
            dkey = (method, t.item.source, t.group_key, t.target_option_id)
            if dkey in done:
                continue
            r = run_method_on_item(
                method, t.item, t.persona_facets, t.target_option_id, t.group_key,
                facet_map, shots=shots, k=args.k,
                student_model=args.student_model, judge_model=args.judge_model,
            )
            results.append(r)
            sf.write(r.model_dump_json() + "\n")
            sf.flush()
            print(f"  [{i}/{len(work)}] {method:8s} {t.group_key:8s} "
                  f"{t.item.source.split('/')[-1]}  hit={r.hit_rate:.0%} "
                  f"fid={r.fidelity_among_hits} nat={r.naturalness_among_hits}")

    print_summary(results)
    ComparisonReport(results=results)
    out_path.write_text(json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False))
    print(f"\nSaved to {out_path}  (stream: {stream_path.name})")


if __name__ == "__main__":
    main()
