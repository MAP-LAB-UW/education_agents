#!/usr/bin/env python3
"""Evaluate expert examples from the facet map using item-level and corpus-level rubrics."""

import argparse
import base64
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from education_agents.evaluation.correctness import evaluate_correctness
from education_agents.evaluation.corpus_metrics import evaluate_corpus, evaluate_similarity_with_experts
from education_agents.evaluation.facet_latency import _get_model, evaluate_facet_latency
from education_agents.evaluation.figure_necessity import evaluate_figure_necessity
from education_agents.evaluation.figure_spoiler import evaluate_figure_spoiler
from education_agents.evaluation.naturalness import evaluate_naturalness
from education_agents.evaluation.schemas import ItemEvaluation
from education_agents.facets import load_facet_map
from education_agents.schemas import (
    Figure,
    GeneratedItem,
    GenerationRequest,
    JudgeReport,
    Option,
    OptionAssessment,
    RunArtifact,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
_FIG_REF_RE = re.compile(r"\[(?:See figure|Figure):\s*@'([^']+)'\]")



def expert_to_generated_item(example, index: int) -> tuple[GeneratedItem, dict[str, str]]:
    """Convert an expert example to a GeneratedItem + figure_data dict."""
    all_figures: list[Figure] = []
    all_figure_data: dict[str, str] = {}
    seen_paths: dict[str, str] = {}
    fig_counter = [0]

    def _resolve_figures(text: str) -> str:
        def _replace(m: re.Match) -> str:
            path_str = m.group(1)
            if path_str in seen_paths:
                return f"[FIGURE:{seen_paths[path_str]}]"
            fig_counter[0] += 1
            fig_id = f"fig{fig_counter[0]}"
            seen_paths[path_str] = fig_id
            img_path = REPO_ROOT / path_str
            if img_path.exists():
                b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
                all_figure_data[fig_id] = b64
                all_figures.append(Figure(id=fig_id, python_code="", alt_text=img_path.stem))
            return f"[FIGURE:{fig_id}]"
        return _FIG_REF_RE.sub(_replace, text)

    stem = _resolve_figures(example.stem)

    options = []
    for o in example.options:
        opt_text = _resolve_figures(o.text)
        options.append(Option(
            id=o.id,
            text=opt_text,
            facet_tags=o.facet_tags,
            is_correct=o.is_correct,
            rationale="Expert-authored option",
        ))

    correct_ids = [o.id for o in example.options if o.is_correct]
    all_tags = set()
    for o in example.options:
        all_tags.update(o.facet_tags)

    item = GeneratedItem(
        stem=stem,
        response_format=example.response_format,
        options=options,
        correct_option_ids=correct_ids,
        explanation="Expert-authored item",
        target_facets=sorted(all_tags),
        figures=all_figures,
    )
    return item, all_figure_data


def item_to_stub_artifact(item: GeneratedItem, topic: str, index: int) -> RunArtifact:
    stub_assessments = [
        OptionAssessment(
            option_id=o.id,
            generator_tags=o.facet_tags,
            judge_tags=o.facet_tags,
            agreement="match",
            confidence=1.0,
            reasoning="Expert-authored",
        )
        for o in item.options
    ]
    return RunArtifact(
        request=GenerationRequest(
            topic=topic,
            target_facets=item.target_facets,
            response_format=item.response_format,
        ),
        models={"generator": "expert", "judge": "n/a"},
        item=item,
        judge_report=JudgeReport(
            item_stem_preview=item.stem[:60],
            option_assessments=stub_assessments,
            overall_agreement=1.0,
            overall_confidence=1.0,
            issues=[],
        ),
        timing={"generator_s": 0, "judge_s": 0},
        created_at=f"expert_{index+1}",
    )


def print_item_results(results: list[ItemEvaluation], has_llm: bool):
    n = len(results)

    print("\n" + "=" * 70)
    print("  EXPERT EXAMPLES — ITEM SUMMARY")
    print("=" * 70)

    if has_llm:
        n_correct = sum(1 for r in results if r.correctness.is_correct)
        mean_natural = sum(r.naturalness.overall_score for r in results) / n
        print(f"  Correctness: {n_correct}/{n} ({n_correct/n:.0%})")
        print(f"  Naturalness: {mean_natural:.1f}/5")

    mean_latency = sum(r.facet_latency.score for r in results) / n
    mean_sim = sum(r.facet_latency.mean_similarity for r in results) / n
    print(f"  Facet Latency: {mean_latency:.1f}/4 (mean sim={mean_sim:.3f})")

    fig_results = [r for r in results if r.figure_necessity is not None]
    if fig_results:
        fig_avg = sum(r.figure_necessity for r in fig_results) / len(fig_results)
        print(f"  Figure Necessity: {fig_avg:.2f} ({len(fig_results)} items with figures)")

    sem_results = [r for r in results if r.similarity_with_experts is not None]
    if sem_results:
        mean_sem = sum(r.similarity_with_experts.mean_similarity for r in sem_results) / len(sem_results)
        max_sem = max(r.similarity_with_experts.max_similarity for r in sem_results)
        print(f"  Similarity (within experts): mean={mean_sem:.3f}, max={max_sem:.3f}")

    for r in results:
        fl = r.facet_latency
        line = f"    {r.source}: {fl.score}/4 ({fl.bucket}, sim={fl.mean_similarity:.3f})"
        if has_llm:
            c = "PASS" if r.correctness.is_correct else "FAIL"
            line += f"  correct={c}  natural={r.naturalness.overall_score}/5"
        if r.figure_necessity is not None:
            line += f"  fig={r.figure_necessity}"
        if r.similarity_with_experts is not None:
            ss = r.similarity_with_experts
            line += f"  sim={ss.max_similarity:.3f}(max,→{ss.most_similar_to})"
        print(line)


def print_corpus_results(corpus):
    print("\n" + "=" * 70)
    print("  EXPERT EXAMPLES — CORPUS METRICS")
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
    print(f"    Mean pairwise diversity: {1 - pd.semantic.mean_pairwise_similarity:.3f}")
    print(f"    Min pairwise diversity:  {1 - pd.semantic.max_pairwise_similarity:.3f}")
    if pd.semantic.most_similar_pair:
        print(f"    Least diverse pair: {pd.semantic.most_similar_pair}")

    if pd.facet_qmatrix is not None:
        qm = pd.facet_qmatrix
        print(f"\n  Problem Diversity (Facet Q-matrix):")
        print(f"    Mean pairwise diversity: {1 - qm.mean_pairwise_similarity:.3f}")
        print(f"    Min pairwise diversity:  {1 - qm.max_pairwise_similarity:.3f}")
        if qm.most_similar_pair:
            print(f"    Least diverse pair: {qm.most_similar_pair}")

    if corpus.figure_fraction is not None:
        print(f"\n  Figures:")
        print(f"    Fraction with figures: {corpus.figure_fraction:.0%}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate expert examples from the facet map."
    )
    parser.add_argument(
        "--topic",
        default="confidence_intervals",
        help="Topic name for facet map lookup",
    )
    parser.add_argument(
        "--eval-model",
        default=None,
        help="Model for LLM-based rubrics",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip LLM-based rubrics (correctness, naturalness) — only run facet latency",
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

    facet_map = load_facet_map(args.topic)
    print(f"Loaded {len(facet_map.examples)} expert examples for topic '{args.topic}'")

    items_and_figs = [expert_to_generated_item(ex, i) for i, ex in enumerate(facet_map.examples)]
    items = [item for item, _ in items_and_figs]
    figure_datas = [fd for _, fd in items_and_figs]
    artifacts = [item_to_stub_artifact(item, args.topic, i) for i, item in enumerate(items)]

    item_results: list[ItemEvaluation] = []
    if not args.skip_item:
        embed_model = _get_model()
        print("\nRunning item-level evaluation...")
        for i, item in enumerate(items):
            fig_data = figure_datas[i]
            print(f"  [{i+1}/{len(items)}] {item.stem[:60]}...")
            if fig_data:
                print(f"    ({len(fig_data)} figure(s) loaded)")

            correctness = None
            naturalness = None
            if not args.skip_llm:
                correctness = evaluate_correctness(item, model=args.eval_model, figure_data=fig_data)
                naturalness = evaluate_naturalness(item, model=args.eval_model, figure_data=fig_data)
            latency = evaluate_facet_latency(item, facet_map, model=embed_model)

            fig_nec = None
            fig_spoiler = None
            if fig_data:
                fn = evaluate_figure_necessity(item, model=args.eval_model)
                fig_nec = int(fn.is_necessary)
                print(f"    figure_necessity: {fig_nec} ({'essential' if fn.is_necessary else 'decorative'}, {fn.n_correct}/{fn.n_trials} correct without figure)")
                if not args.skip_llm:
                    fs = evaluate_figure_spoiler(item, fig_data, model=args.eval_model)
                    fig_spoiler = int(fs.gives_away_answer)
                    print(f"    figure_spoiler: {fig_spoiler} ({'gives away answer' if fs.gives_away_answer else 'clean'}, {fs.n_giveaway}/{fs.n_trials} judged giveaway)")

            item_results.append(ItemEvaluation(
                source=f"expert_{i+1}",
                correctness=correctness or _dummy_correctness(item),
                naturalness=naturalness or _dummy_naturalness(),
                facet_latency=latency,
                figure_necessity=fig_nec,
                figure_spoiler=fig_spoiler,
            ))

            if correctness and naturalness:
                correct_mark = "PASS" if correctness.is_correct else "FAIL"
                print(f"    correct={correct_mark}  natural={naturalness.overall_score}/5  latency={latency.score}/4 ({latency.bucket})")
            else:
                print(f"    latency={latency.score}/4 ({latency.bucket}, sim={latency.mean_similarity:.3f})")

        print("\nComputing per-item similarity with other experts...")
        stems = [item.stem for item in items]
        options = [[o.text for o in item.options] for item in items]
        source_ids = [f"expert_{i+1}" for i in range(len(items))]
        sem_results = evaluate_similarity_with_experts(
            stems, source_ids, options=options, embed_model=embed_model
        )
        for r, sem in zip(item_results, sem_results):
            r.similarity_with_experts = sem

        print_item_results(item_results, has_llm=not args.skip_llm)

    corpus_result = None
    if not args.skip_corpus:
        print("\nRunning corpus-level evaluation...")
        corpus_result = evaluate_corpus(
            artifacts, facet_map, eval_model=args.eval_model
        )
        print_corpus_results(corpus_result)

    if args.out:
        output = {
            "source": "expert_examples",
            "topic": args.topic,
            "n_items": len(items),
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


def _dummy_correctness(item):
    from education_agents.evaluation.schemas import CorrectnessResult
    return CorrectnessResult(
        selected_answer=",".join(item.correct_option_ids),
        correct_answer_ids=item.correct_option_ids,
        is_correct=True,
        flagged_distractors=[],
        reasoning="LLM eval skipped",
    )


def _dummy_naturalness():
    from education_agents.evaluation.schemas import NaturalnessResult
    return NaturalnessResult(
        stem_score=0,
        stem_reasoning="LLM eval skipped",
        options_score=0,
        options_reasoning="LLM eval skipped",
        overall_score=0,
    )


if __name__ == "__main__":
    main()
