#!/usr/bin/env python3
"""Student simulator v2: open-mode answering + blind mapping, per-item
negative-control batteries, and a blind misconception lineup judge.

For every item, runs one persona per misconception group keyed to its
distractors plus a no-misconception control, each answering the stem with no
options shown. A blind mapper resolves the free response to an option; the
reported signal per target option is the selection-rate gap
P(target | matched persona) − P(target | other personas).
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from education_agents.evaluation.persona_bank import PersonaBank
from education_agents.evaluation.schemas import SimV2Attempt, SimV2Report
from education_agents.evaluation.sim_corpus import (
    DEFAULT_GENERATED_DIRS,
    load_corpus,
)
from education_agents.evaluation.sim_v2 import (
    CONTROL_KEY,
    aggregate_v2,
    battery_run_plan,
    build_item_batteries,
    run_attempt,
)
from education_agents.facets import load_facet_map


def print_report(report: SimV2Report):
    print("\n" + "=" * 72)
    print("  SELECTION-RATE GAP BY MISCONCEPTION GROUP")
    print("=" * 72)
    print(f"{'Group':22s} {'#tgt':>5s} {'matched':>9s} {'gap':>7s} {'lineup-id':>10s}")
    print("-" * 72)
    for g in sorted(report.by_group, key=lambda x: (x.mean_gap, x.group_key)):
        lineup = f"{g.mean_lineup_id_rate:.0%}" if g.mean_lineup_id_rate is not None else "—"
        print(f"{g.group_key:22s} {g.n_targets:>5d} {g.mean_matched_rate:>8.0%} "
              f"{g.mean_gap:>+7.0%} {lineup:>10s}")
    print("-" * 72)

    def pct(x):
        return f"{x:.0%}" if x is not None else "—"

    print(f"\n  Targets scored: {len(report.per_target)} across {report.n_items} items "
          f"({report.n_attempts} persona runs, k={report.k_samples})")
    print(f"  matched persona selects target:      {pct(report.overall_matched_rate)}")
    print(f"  other-misconception personas do:     {pct(report.overall_alternative_rate)}")
    print(f"  control (no misconception) does:     {pct(report.overall_control_target_rate)}")
    print(f"  => mean selection gap:               {report.overall_gap:+.0%}")
    print(f"  control lands exactly on the key:    {pct(report.control_correct_rate)}")
    print(f"  blind lineup judge IDs the facets:   {pct(report.lineup_id_rate)}")
    print(f"  open answer mapped to no option:     {pct(report.open_no_match_rate)} "
          f"(select fallback fills these in)")

    weak = [t for t in report.per_target if t.selection_gap <= 0]
    if weak:
        print(f"\n  {len(weak)} target(s) with non-positive gap (item or persona problems):")
        for t in sorted(weak, key=lambda x: x.selection_gap)[:10]:
            print(f"    {t.group_key:14s} {t.source}  opt={t.target_option_id}  "
                  f"matched={t.matched_target_rate:.0%} gap={t.selection_gap:+.0%}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dirs", nargs="*", default=None,
                        help=f"Generated artifact dirs (default: {len(DEFAULT_GENERATED_DIRS)} standard dirs)")
    parser.add_argument("--topic", default="confidence_intervals")
    parser.add_argument("--no-experts", action="store_true")
    parser.add_argument("--experts-only", action="store_true")
    parser.add_argument("--k", type=int, default=3, help="Samples per (item, persona)")
    parser.add_argument("--no-control", action="store_true",
                        help="Skip the no-misconception control persona")
    parser.add_argument("--no-fallback", action="store_true",
                        help="Skip the select-mode fallback when the open "
                             "answer maps to no option")
    parser.add_argument("--student-model", default=None)
    parser.add_argument("--mapper-model", default=None)
    parser.add_argument("--judge-model", default=None)
    parser.add_argument("--persona-model", default=None,
                        help="Model for building missing personas (default: Claude)")
    parser.add_argument("--bank", default=None, help="Persona bank JSON path")
    parser.add_argument("--temperature", type=float, default=0.9,
                        help="Student sampling temperature; pass a negative "
                             "value to omit (required for models that reject it)")
    parser.add_argument("--limit", type=int, default=None, help="Cap number of items")
    parser.add_argument("--out", default="outputs/sim_v2.json")
    parser.add_argument("--fresh", action="store_true",
                        help="Ignore any existing stream file and start over")
    args = parser.parse_args()

    facet_map = load_facet_map(args.topic)
    items = load_corpus(
        facet_map,
        dirs=args.dirs or None,
        include_experts=not args.no_experts,
    )
    if args.experts_only:
        items = [it for it in items if it.source.startswith("expert_")]
    print(f"Loaded {len(items)} items")

    batteries = build_item_batteries(items, facet_map)
    if args.limit:
        batteries = batteries[: args.limit]
    include_control = not args.no_control
    n_runs = sum(
        len(battery_run_plan(b, args.k, include_control)) for b in batteries
    )
    print(f"{len(batteries)} item batteries, k={args.k} -> {n_runs} persona runs")

    # Pre-build any missing personas (cached; only misses hit the API).
    bank = PersonaBank(args.bank)
    needed = sorted({key for b in batteries for key in b.persona_keys})
    missing = [key for key in needed if key not in bank]
    if missing:
        print(f"Building {len(missing)} missing persona(s): {', '.join(missing)}")
    for key in needed:
        bank.get_or_build(key.split("+"), facet_map, model=args.persona_model)

    temperature = None if args.temperature < 0 else args.temperature

    # Stream attempts to a JSONL sidecar so a killed run can resume.
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stream_path = out_path.with_suffix(".jsonl")
    if args.fresh and stream_path.exists():
        stream_path.unlink()

    done: dict[tuple, SimV2Attempt] = {}
    if stream_path.exists():
        for line in stream_path.read_text().splitlines():
            if not line.strip():
                continue
            a = SimV2Attempt.model_validate_json(line)
            done[(a.source, a.persona_key, a.sample_index)] = a
        print(f"Resuming: {len(done)} attempts already recorded in {stream_path.name}")

    attempts: list[SimV2Attempt] = list(done.values())
    completed = len(done)
    with open(stream_path, "a") as sf:
        for battery in batteries:
            for persona_key, sample_index in battery_run_plan(
                battery, args.k, include_control
            ):
                key = (battery.item.source, persona_key, sample_index)
                if key in done:
                    continue
                a = run_attempt(
                    battery, persona_key, sample_index, bank, facet_map,
                    student_model=args.student_model,
                    mapper_model=args.mapper_model,
                    judge_model=args.judge_model,
                    temperature=temperature,
                    select_fallback=not args.no_fallback,
                )
                attempts.append(a)
                sf.write(a.model_dump_json() + "\n")
                sf.flush()
                completed += 1
                if a.mapped_option_ids:
                    landed = ",".join(a.mapped_option_ids)
                elif a.fallback_used:
                    landed = f"(no open match; select -> {','.join(a.fallback_option_ids) or 'none'})"
                else:
                    landed = "(none)"
                print(f"  [{completed}/{n_runs}] {persona_key:16s} "
                      f"{battery.item.source}#{sample_index}  -> {landed}")

    report = aggregate_v2(attempts, batteries, args.k)
    print_report(report)
    out_path.write_text(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))
    print(f"\nReport saved to {out_path}  (stream: {stream_path.name})")


if __name__ == "__main__":
    main()
