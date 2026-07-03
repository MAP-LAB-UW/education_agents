#!/usr/bin/env python3
"""Phase 1: validate the student simulator.

Builds a corpus of generated + expert items, groups items by the misconception
facet set keyed to each incorrect option, runs the simulator on each, and
reports how often the student's reasoning exhibits the intended misconception
(fidelity, signal a). No item conclusions are drawn here.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from education_agents.evaluation.schemas import PersonaResult, SimulatorEvalReport
from education_agents.evaluation.sim_corpus import (
    DEFAULT_GENERATED_DIRS,
    build_persona_trials,
    coverage_summary,
    load_corpus,
)
from education_agents.evaluation.student_simulator import (
    aggregate_report,
    run_trial,
)
from education_agents.facets import load_facet_map


def select_trials(groups: dict, limit: int | None) -> list:
    """Flatten trials; if limited, round-robin across groups for coverage."""
    if limit is None:
        return [t for trials in groups.values() for t in trials]
    selected: list = []
    pools = {k: list(v) for k, v in groups.items()}
    while len(selected) < limit and any(pools.values()):
        for k in list(pools):
            if pools[k]:
                selected.append(pools[k].pop(0))
                if len(selected) >= limit:
                    break
    return selected


def print_report(report: SimulatorEvalReport, modes: tuple[str, ...]):
    print("\n" + "=" * 60)
    print("  SIMULATOR FIDELITY BY MISCONCEPTION GROUP")
    print("=" * 60)
    print(f"{'Group':26s} {'kind':>6s} {'#trials':>8s} {'fidelity':>10s}")
    print("-" * 60)
    for g in sorted(report.by_group, key=lambda x: (x.misconception_fidelity, x.group_key)):
        kind = "multi" if "+" in g.group_key else "single"
        print(f"{g.group_key:26s} {kind:>6s} {g.n_trials:>8d} {g.misconception_fidelity:>9.0%}")
    print("-" * 60)

    print("\n  FIDELITY BY SOURCE CORPUS")
    print("-" * 60)
    corpora: dict[str, list[float]] = {}
    for src, fid in report.by_source.items():
        corpus = src.split("/")[0]
        corpora.setdefault(corpus, []).append(fid)
    for corpus, fids in sorted(corpora.items()):
        mean = sum(fids) / len(fids)
        print(f"{corpus:34s} {mean:>9.0%}  ({len(fids)} items)")
    print("-" * 60)

    print(f"\n  OVERALL FIDELITY ({', '.join(modes)}): "
          f"{report.overall_fidelity:.1%} "
          f"over {len(report.persona_results)} persona runs")
    print(f"    single-facet: {report.single_facet_fidelity:.0%} "
          f"({report.n_single_facet_runs} runs)   "
          f"multi-facet: {report.multi_facet_fidelity:.0%} "
          f"({report.n_multi_facet_runs} runs)")
    print("    (multi-facet misses can reflect items that don't probe the full "
          "combo, not simulator error)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dirs", nargs="*", default=None,
                        help=f"Generated artifact dirs (default: {len(DEFAULT_GENERATED_DIRS)} standard dirs)")
    parser.add_argument("--topic", default="confidence_intervals")
    parser.add_argument("--no-experts", action="store_true",
                        help="Exclude expert examples from the corpus")
    parser.add_argument("--modes", default="open,select",
                        help="Comma-separated answer modes (open, select)")
    parser.add_argument("--student-model", default=None)
    parser.add_argument("--judge-model", default=None)
    parser.add_argument("--limit", type=int, default=None,
                        help="Cap number of trials (round-robin across groups) for smoke runs")
    parser.add_argument("--out", default="outputs/sim_eval.json",
                        help="Output JSON path for the full report")
    parser.add_argument("--fresh", action="store_true",
                        help="Ignore any existing stream file and start over")
    args = parser.parse_args()

    modes = tuple(m.strip() for m in args.modes.split(",") if m.strip())
    facet_map = load_facet_map(args.topic)

    items = load_corpus(
        facet_map,
        dirs=args.dirs or None,
        include_experts=not args.no_experts,
    )
    print(f"Loaded {len(items)} items "
          f"({'with' if not args.no_experts else 'no'} experts)")

    groups = build_persona_trials(items, facet_map)
    print("\n" + coverage_summary(groups))

    trials = select_trials(groups, args.limit)
    n_runs = len(trials) * len(modes)
    print(f"\nPlanned {len(trials)} trials x {len(modes)} mode(s) = {n_runs} persona runs")

    # Stream each persona result to a JSONL sidecar as it completes, so a
    # killed run can resume instead of restarting. Final report -> --out.
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stream_path = out_path.with_suffix(".jsonl")

    def trial_key(source, group_key, target_option_id, mode):
        return (source, group_key, target_option_id, mode)

    done: dict[tuple, PersonaResult] = {}
    if args.fresh and stream_path.exists():
        stream_path.unlink()
    if stream_path.exists():
        for line in stream_path.read_text().splitlines():
            if not line.strip():
                continue
            pr = PersonaResult.model_validate_json(line)
            done[trial_key(pr.source, pr.group_key, pr.target_option_id, pr.mode)] = pr
        print(f"Resuming: {len(done)} persona runs already recorded in {stream_path.name}")

    results: list[PersonaResult] = list(done.values())
    completed = len(done)
    with open(stream_path, "a") as sf:
        for trial in trials:
            for mode in modes:
                key = trial_key(trial.item.source, trial.group_key,
                                trial.target_option_id, mode)
                if key in done:
                    continue
                pr = run_trial(
                    trial, facet_map, modes=(mode,),
                    student_model=args.student_model, judge_model=args.judge_model,
                )[0]
                results.append(pr)
                sf.write(pr.model_dump_json() + "\n")
                sf.flush()
                completed += 1
                print(f"  [{completed}/{n_runs}] {mode:6s} {trial.group_key:18s} "
                      f"{trial.item.source}  exhibits={pr.exhibits_misconception}")

    report = aggregate_report(results)
    print_report(report, modes)

    out_path.write_text(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))
    print(f"\nReport saved to {out_path}  (stream: {stream_path.name})")


if __name__ == "__main__":
    main()
