#!/usr/bin/env python3
"""CLI for running evaluation rubrics on generated items."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from education_agents.evaluation.correctness import evaluate_correctness
from education_agents.evaluation.corpus_metrics import evaluate_corpus, evaluate_similarity_with_experts
from education_agents.evaluation.facet_latency import evaluate_facet_latency
from education_agents.evaluation.figure_necessity import evaluate_figure_necessity
from education_agents.evaluation.naturalness import evaluate_naturalness
from education_agents.evaluation.schemas import (
    CorpusEvaluation,
    CorrectnessResult,
    FacetLatencyResult,
    ItemEvaluation,
    NaturalnessResult,
    OptionLatency,
)
from education_agents.facets import load_facet_map
from education_agents.schemas import RunArtifact


def load_artifacts(directory: Path) -> list[RunArtifact]:
    artifacts = []
    for p in sorted(directory.glob("*.json")):
        with open(p) as f:
            artifacts.append(RunArtifact.model_validate(json.load(f)))
    return artifacts


def print_item_results(results: list[ItemEvaluation]):
    print("\n" + "=" * 70)
    print("  ITEM-LEVEL RESULTS")
    print("=" * 70)

    for r in results:
        print(f"\n--- {r.source} ---")

        c = r.correctness
        correct_mark = "PASS" if c.is_correct else "FAIL"
        print(f"  Correctness: {correct_mark}")
        print(f"    LLM answer: {c.selected_answer}  Keyed: {','.join(c.correct_answer_ids)}")
        if c.flagged_distractors:
            print(f"    Flagged distractors: {c.flagged_distractors}")
        print(f"    Reasoning: {c.reasoning[:150]}")

        n = r.naturalness
        print(f"  Naturalness: {n.overall_score}/5  (stem={n.stem_score}, options={n.options_score})")
        print(f"    Stem: {n.stem_reasoning[:120]}")
        print(f"    Options: {n.options_reasoning[:120]}")

        fl = r.facet_latency
        print(f"  Facet Latency: {fl.score}/4 ({fl.bucket}, sim={fl.mean_similarity:.3f})")
        for od in fl.option_details:
            print(f"    {od.option_id}: {od.score}/4 ({od.bucket}, sim={od.similarity:.3f})  tags={od.facet_tags}")

        if r.figure_necessity is not None:
            label = "essential" if r.figure_necessity == 1 else "decorative"
            print(f"  Figure Necessity: {r.figure_necessity} ({label})")

    # Summary table
    n = len(results)
    n_correct = sum(1 for r in results if r.correctness.is_correct)
    mean_stem = sum(r.naturalness.stem_score for r in results) / n
    mean_opts = sum(r.naturalness.options_score for r in results) / n
    mean_natural = sum(r.naturalness.overall_score for r in results) / n
    mean_latency_score = sum(r.facet_latency.score for r in results) / n
    flagged = sum(len(r.correctness.flagged_distractors) for r in results)

    fig_results = [r for r in results if r.figure_necessity is not None]

    print("\n" + "=" * 80)
    print("  ITEM SUMMARY")
    print("=" * 80)
    header = "{:22s} {:>9s} {:>12s} {:>12s} {:>14s}".format(
        "Source", "Correct", "Natural /5", "Latency /4", "Flagged Dist",
    )
    if fig_results:
        header += "  {:>6s}".format("Fig")
    print(header)
    print("-" * 80)
    for r in results:
        row = "{:22s} {:>9s} {:>12s} {:>12s} {:>14d}".format(
            r.source[:22],
            "PASS" if r.correctness.is_correct else "FAIL",
            "{}/5 ({},{})".format(r.naturalness.overall_score, r.naturalness.stem_score, r.naturalness.options_score),
            "{}/4 ({})".format(r.facet_latency.score, r.facet_latency.bucket[:7]),
            len(r.correctness.flagged_distractors),
        )
        if fig_results:
            row += "  {:>6s}".format(str(r.figure_necessity) if r.figure_necessity is not None else "—")
        print(row)
    print("-" * 80)

    print("\n  AVERAGES:")
    print("    Correctness:        {:.0%} ({}/{})".format(n_correct / n, n_correct, n))
    print("    Naturalness:        {:.1f}/5  (stem={:.1f}, options={:.1f})".format(mean_natural, mean_stem, mean_opts))
    print("    Facet Latency:      {:.1f}/4".format(mean_latency_score))
    print("    Flagged distractors: {} across {} items".format(flagged, n))
    if fig_results:
        fig_avg = sum(r.figure_necessity for r in fig_results) / len(fig_results)
        print("    Figure Necessity:   {:.2f} ({}/{} items with figures)".format(
            fig_avg, sum(r.figure_necessity for r in fig_results), len(fig_results)
        ))


def print_corpus_results(corpus: CorpusEvaluation):
    print("\n" + "=" * 70)
    print("  CORPUS-LEVEL RESULTS")
    print("=" * 70)

    fc = corpus.facet_coverage
    print(f"\n  Facet Coverage:")
    print(f"    Covered: {fc.covered_facets}/{fc.total_facets_in_map} facets")
    print(f"    Uniformity: {fc.uniformity:.3f} (1.0 = perfectly uniform)")
    print(f"    Counts:")
    for fid, count in sorted(fc.facet_counts.items()):
        bar = "#" * count
        print(f"      {fid:4s}: {bar} ({count})")

    fcd = corpus.facet_combination_diversity
    print(f"\n  Facet Combination Diversity:")
    print(f"    Unique combos: {fcd.unique_combinations}/{fcd.total_items} ({fcd.combination_ratio:.0%})")
    print(f"    Mean pairwise Jaccard distance: {fcd.mean_pairwise_jaccard_distance:.3f}")

    pd = corpus.problem_diversity
    print(f"\n  Problem Diversity (Structural):")
    print(f"    Format entropy: {pd.structural.format_entropy:.3f}")
    for fmt, count in sorted(pd.structural.format_distribution.items()):
        print(f"      {fmt}: {count}")
    print(f"    Style entropy: {pd.structural.style_entropy:.3f}")
    for style, count in sorted(pd.structural.style_distribution.items()):
        print(f"      {style}: {count}")

    print(f"\n  Problem Diversity (Semantic):")
    print(f"    Mean pairwise stem similarity: {pd.semantic.mean_pairwise_similarity:.3f}")
    print(f"    Max pairwise stem similarity:  {pd.semantic.max_pairwise_similarity:.3f}")
    if pd.semantic.most_similar_pair:
        print(f"    Most similar pair: {pd.semantic.most_similar_pair}")

    if corpus.figure_fraction is not None:
        print(f"\n  Figures:")
        print(f"    Fraction with figures: {corpus.figure_fraction:.0%}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate generated diagnostic assessment items."
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing run artifact JSON files",
    )
    parser.add_argument(
        "--topic",
        default="confidence_intervals",
        help="Topic name for facet map lookup",
    )
    parser.add_argument(
        "--eval-model",
        default=None,
        help="Model for LLM-based rubrics (default: gemini/gemini-2.5-flash)",
    )
    parser.add_argument(
        "--skip-item",
        action="store_true",
        help="Skip item-level evaluation (only run corpus metrics)",
    )
    parser.add_argument(
        "--skip-corpus",
        action="store_true",
        help="Skip corpus-level evaluation (only run item metrics)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output JSON file for results",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    facet_map = load_facet_map(args.topic)
    artifacts = load_artifacts(input_dir)
    print(f"Loaded {len(artifacts)} artifacts from {input_dir}")

    item_results: list[ItemEvaluation] = []
    corpus_result: CorpusEvaluation | None = None

    if not args.skip_item:
        print("\nRunning item-level evaluation...")
        embed_model = None
        skipped = 0
        for i, art in enumerate(artifacts):
            if art.eval_scores:
                es = art.eval_scores
                fig_nec = es.figure_necessity
                if fig_nec is None and art.figure_data:
                    fn = evaluate_figure_necessity(art.item, model=args.eval_model)
                    fig_nec = int(fn.is_necessary)
                item_results.append(ItemEvaluation(
                    source=art.created_at[:19],
                    correctness=CorrectnessResult(
                        selected_answer="",
                        correct_answer_ids=art.item.correct_option_ids,
                        is_correct=es.correctness_pass,
                        flagged_distractors=es.correctness_flagged_distractors,
                        reasoning="From cached eval_scores",
                    ),
                    naturalness=NaturalnessResult(
                        stem_score=es.naturalness_stem,
                        stem_reasoning="From cached eval_scores",
                        options_score=es.naturalness_options,
                        options_reasoning="From cached eval_scores",
                        overall_score=es.naturalness_overall,
                    ),
                    facet_latency=FacetLatencyResult(
                        mean_similarity=es.latency_similarity,
                        score=es.latency_score,
                        bucket=es.latency_bucket,
                        option_details=[OptionLatency(**od) for od in es.latency_option_details],
                    ),
                    figure_necessity=fig_nec,
                ))
                skipped += 1
                continue

            print(f"  [{i+1}/{len(artifacts)}] {art.item.stem[:60]}...")

            figure_data = art.figure_data or {}
            correctness = evaluate_correctness(art.item, model=args.eval_model, figure_data=figure_data)
            naturalness = evaluate_naturalness(art.item, model=args.eval_model, figure_data=figure_data)

            if embed_model is None:
                from education_agents.evaluation.facet_latency import _get_model
                embed_model = _get_model()
            latency = evaluate_facet_latency(art.item, facet_map, model=embed_model)

            fig_nec = None
            if figure_data:
                fn = evaluate_figure_necessity(art.item, model=args.eval_model)
                fig_nec = int(fn.is_necessary)

            item_results.append(ItemEvaluation(
                source=art.created_at[:19],
                correctness=correctness,
                naturalness=naturalness,
                facet_latency=latency,
                figure_necessity=fig_nec,
            ))

        if skipped:
            print(f"  Skipped {skipped}/{len(artifacts)} items (eval_scores already present)")

        print("\nComputing similarity with expert examples...")
        ref_stems = [ex.stem for ex in facet_map.examples]
        ref_ids = [f"expert_{i+1}" for i in range(len(ref_stems))]
        stems = [art.item.stem for art in artifacts]
        source_ids = [art.created_at[:19] for art in artifacts]
        sem_results = evaluate_similarity_with_experts(
            stems, source_ids,
            reference_stems=ref_stems, reference_ids=ref_ids,
        )
        for r, sem in zip(item_results, sem_results):
            r.similarity_with_experts = sem

        print_item_results(item_results)

    if not args.skip_corpus:
        print("\nRunning corpus-level evaluation...")
        corpus_result = evaluate_corpus(
            artifacts, facet_map, eval_model=args.eval_model
        )
        print_corpus_results(corpus_result)

    if args.out:
        output = {
            "input_dir": str(input_dir),
            "n_items": len(artifacts),
        }
        if item_results:
            item_dicts = []
            for r, art in zip(item_results, artifacts):
                d = r.model_dump()
                jr = art.judge_report
                if jr:
                    d["judge"] = {
                        "overall_agreement": jr.overall_agreement,
                        "overall_confidence": jr.overall_confidence,
                        "issues": jr.issues,
                    }
                item_dicts.append(d)
            output["item_evaluations"] = item_dicts
        if corpus_result:
            output["corpus_evaluation"] = corpus_result.model_dump()

        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
        print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
