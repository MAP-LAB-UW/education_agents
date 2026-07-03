"""Compare stem-only vs options-aware permutation-invariant similarity.

For a directory of generated-item artifacts and a topic's expert examples, this
computes per-item similarity-with-experts under two representations:

  - stem_only : embed only the stem (the old behaviour)
  - stem+opts : permutation-invariant match that folds in the option texts

and prints a side-by-side comparison plus corpus-level pairwise diversity.

Usage:
  python scripts/compare_similarity_methods.py outputs/third_pass_sonnet-4-6 \
      --topic confidence_intervals --stem-weight 0.5
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from education_agents.evaluation.corpus_metrics import (
    evaluate_semantic_diversity,
    evaluate_similarity_with_experts,
)
from education_agents.evaluation.facet_latency import _get_model
from education_agents.facets import load_facet_map
from education_agents.schemas import RunArtifact


def load_artifacts(directory: Path) -> list[RunArtifact]:
    arts = []
    for p in sorted(directory.glob("*.json")):
        with open(p) as f:
            arts.append(RunArtifact.model_validate(json.load(f)))
    return arts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_dir")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--stem-weight", type=float, default=0.5)
    args = ap.parse_args()

    facet_map = load_facet_map(args.topic)
    arts = load_artifacts(Path(args.input_dir))
    model = _get_model()
    print(f"Loaded {len(arts)} items, {len(facet_map.examples)} expert examples\n")

    stems = [a.item.stem for a in arts]
    options = [[o.text for o in a.item.options] for a in arts]
    source_ids = [a.created_at[:19] for a in arts]

    ref_stems = [ex.stem for ex in facet_map.examples]
    ref_ids = [f"expert_{i+1}" for i in range(len(ref_stems))]
    ref_opts = [[o.text for o in ex.options] for ex in facet_map.examples]

    # --- Similarity with experts: both representations ---
    old = evaluate_similarity_with_experts(
        stems, source_ids,
        reference_stems=ref_stems, reference_ids=ref_ids,
        embed_model=model,
    )
    new = evaluate_similarity_with_experts(
        stems, source_ids, options=options,
        reference_stems=ref_stems, reference_ids=ref_ids,
        reference_options=ref_opts,
        embed_model=model, stem_weight=args.stem_weight,
    )

    print("SIMILARITY WITH EXPERTS (per item)")
    print(f"{'item':<21} {'stem_only':>20} {'stem+opts':>20}   match changed?")
    print(f"{'':<21} {'mean / max / →':>20} {'mean / max / →':>20}")
    print("-" * 90)
    for sid, o, n in zip(source_ids, old, new):
        changed = "*" if o.most_similar_to != n.most_similar_to else ""
        print(
            f"{sid:<21} "
            f"{o.mean_similarity:>5.3f}/{o.max_similarity:.3f}/{o.most_similar_to:>9} "
            f"{n.mean_similarity:>5.3f}/{n.max_similarity:.3f}/{n.most_similar_to:>9}   {changed}"
        )

    om = sum(r.mean_similarity for r in old) / len(old)
    nm = sum(r.mean_similarity for r in new) / len(new)
    ox = sum(r.max_similarity for r in old) / len(old)
    nx = sum(r.max_similarity for r in new) / len(new)
    changes = sum(1 for o, n in zip(old, new) if o.most_similar_to != n.most_similar_to)
    print("-" * 90)
    print(f"{'AVG':<21} {om:>5.3f}/{ox:.3f}/{'':>9} {nm:>5.3f}/{nx:.3f}/{'':>9}")
    print(f"nearest-expert reassigned for {changes}/{len(old)} items\n")

    # --- Corpus pairwise diversity ---
    div_old = evaluate_semantic_diversity(arts, embed_model=model, stem_weight=1.0)
    div_new = evaluate_semantic_diversity(arts, embed_model=model, stem_weight=args.stem_weight)
    print("CORPUS PAIRWISE DIVERSITY (within generated set)")
    print(f"  stem_only : mean={div_old.mean_pairwise_similarity:.3f}  max={div_old.max_pairwise_similarity:.3f}  pair={div_old.most_similar_pair}")
    print(f"  stem+opts : mean={div_new.mean_pairwise_similarity:.3f}  max={div_new.max_pairwise_similarity:.3f}  pair={div_new.most_similar_pair}")


if __name__ == "__main__":
    main()
