#!/usr/bin/env python3
"""
Compare two facet-latency measurement approaches on expert examples vs v1 generated items.

Approach 1 (Embedding similarity):
  For each option, compute cosine similarity between the option text and the
  concatenation of its tagged facet definitions. Higher similarity = less latent.

Approach 2 (LLM surface matching):
  Give an LLM the facet definitions + item (no tags, no answer key). Ask it to
  match each option to its most likely facet(s). Measure recovery accuracy.
  Higher recovery = less latent.
"""

import json
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from education_agents.facets import load_facet_map
from education_agents.llm import structured_complete
from education_agents.schemas import FacetMap

# ── Helpers ──────────────────────────────────────────────────────────────────

def build_facet_lookup(facet_map: FacetMap) -> dict[str, str]:
    return {f.id: f.text for f in facet_map.facets}


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


# ── Extract items in a uniform format ────────────────────────────────────────

def extract_expert_items(facet_map: FacetMap) -> list[dict]:
    items = []
    for i, ex in enumerate(facet_map.examples):
        if "@'" in ex.stem or any("@'" in o.text for o in ex.options):
            continue
        items.append({
            "source": f"expert_{i+1}",
            "stem": ex.stem,
            "options": [
                {"id": o.id, "text": o.text, "facet_tags": o.facet_tags, "is_correct": o.is_correct}
                for o in ex.options
            ],
        })
    return items


def extract_generated_items(directory: Path) -> list[dict]:
    items = []
    for p in sorted(directory.glob("*.json")):
        with open(p) as f:
            d = json.load(f)
        item = d["item"]
        items.append({
            "source": p.stem,
            "stem": item["stem"],
            "options": [
                {"id": o["id"], "text": o["text"], "facet_tags": o["facet_tags"], "is_correct": o["is_correct"]}
                for o in item["options"]
            ],
        })
    return items


# ── Approach 1: Embedding similarity ─────────────────────────────────────────

def measure_embedding_similarity(
    items: list[dict],
    facet_lookup: dict[str, str],
    model: SentenceTransformer,
) -> list[dict]:
    results = []
    for item in items:
        option_sims = []
        for opt in item["options"]:
            facet_texts = [facet_lookup[fid] for fid in opt["facet_tags"] if fid in facet_lookup]
            if not facet_texts:
                continue
            facet_concat = " ".join(facet_texts)
            embeddings = model.encode([opt["text"], facet_concat])
            sim = cosine_sim(embeddings[0], embeddings[1])
            option_sims.append({
                "option_id": opt["id"],
                "facet_tags": opt["facet_tags"],
                "similarity": sim,
                "option_text": opt["text"][:80],
            })
        mean_sim = np.mean([o["similarity"] for o in option_sims]) if option_sims else 0.0
        results.append({
            "source": item["source"],
            "stem": item["stem"][:80],
            "mean_similarity": float(mean_sim),
            "option_details": option_sims,
        })
    return results


# ── Approach 2: LLM surface matching ─────────────────────────────────────────

from pydantic import BaseModel


class OptionFacetMatch(BaseModel):
    option_id: str
    matched_facets: list[str]


class SurfaceMatchResult(BaseModel):
    matches: list[OptionFacetMatch]
    selected_answer: str


SURFACE_MATCH_SYSTEM = """You are a student who has MEMORIZED the following facet definitions but does NOT deeply understand statistics. You rely on pattern matching and surface-level similarity between answer options and definitions.

## Facet Definitions

{facet_definitions}

## Your Task

You are given a multiple-choice item. For each option:
1. Try to match it to the facet definition(s) it most closely resembles IN WORDING — look for paraphrases, shared key phrases, or direct restatements.
2. If an option does NOT closely resemble any facet definition in wording, assign an empty list.

Also select the answer you think is correct based ONLY on which option sounds most like a "correct textbook definition." Do NOT reason about the actual statistics — just pattern match.

Return your matches and selected answer."""


def measure_surface_matching(
    items: list[dict],
    facet_lookup: dict[str, str],
    model: str = "gemini/gemini-2.5-flash",
) -> list[dict]:
    facet_defs = "\n".join(f"- {fid}: {text}" for fid, text in facet_lookup.items())
    results = []

    for item in items:
        options_text = "\n".join(
            f"  {o['id']}. {o['text']}" for o in item["options"]
        )
        user_msg = f"Stem: {item['stem']}\n\nOptions:\n{options_text}"

        messages = [
            {"role": "system", "content": SURFACE_MATCH_SYSTEM.format(facet_definitions=facet_defs)},
            {"role": "user", "content": user_msg},
        ]

        try:
            result = structured_complete(messages, SurfaceMatchResult, model=model)
        except Exception as e:
            print(f"  LLM error for {item['source']}: {e}")
            results.append({"source": item["source"], "error": str(e)})
            continue

        # Compute recovery accuracy: for each option, what fraction of
        # ground-truth tags did the surface matcher recover?
        option_scores = []
        for opt in item["options"]:
            gt_tags = set(opt["facet_tags"])
            match_entry = next(
                (m for m in result.matches if m.option_id == opt["id"]), None
            )
            pred_tags = set(match_entry.matched_facets) if match_entry else set()

            if gt_tags:
                recall = len(gt_tags & pred_tags) / len(gt_tags)
                precision = len(gt_tags & pred_tags) / len(pred_tags) if pred_tags else 0.0
            else:
                recall = 1.0 if not pred_tags else 0.0
                precision = recall

            option_scores.append({
                "option_id": opt["id"],
                "gt_tags": sorted(gt_tags),
                "pred_tags": sorted(pred_tags),
                "recall": recall,
                "precision": precision,
                "option_text": opt["text"][:80],
            })

        correct_ids = [o["id"] for o in item["options"] if o["is_correct"]]
        answer_correct = result.selected_answer in correct_ids

        mean_recall = np.mean([s["recall"] for s in option_scores])
        mean_precision = np.mean([s["precision"] for s in option_scores])

        results.append({
            "source": item["source"],
            "stem": item["stem"][:80],
            "mean_tag_recall": float(mean_recall),
            "mean_tag_precision": float(mean_precision),
            "answer_correct": answer_correct,
            "selected_answer": result.selected_answer,
            "correct_answer": correct_ids,
            "option_details": option_scores,
        })
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def print_embedding_summary(label: str, results: list[dict]):
    sims = [r["mean_similarity"] for r in results]
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  Items: {len(sims)}")
    print(f"  Mean option-facet similarity: {np.mean(sims):.4f}")
    print(f"  Std:  {np.std(sims):.4f}")
    print(f"  Min:  {np.min(sims):.4f}  Max: {np.max(sims):.4f}")
    print()
    for r in results:
        print(f"  [{r['source'][:30]}] mean_sim={r['mean_similarity']:.4f}  stem: {r['stem']}")
        for od in r["option_details"]:
            print(f"    {od['option_id']}: sim={od['similarity']:.4f}  tags={od['facet_tags']}  \"{od['option_text']}\"")
    print()


def print_surface_summary(label: str, results: list[dict]):
    valid = [r for r in results if "error" not in r]
    recalls = [r["mean_tag_recall"] for r in valid]
    precisions = [r["mean_tag_precision"] for r in valid]
    answer_accs = [r["answer_correct"] for r in valid]
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  Items: {len(valid)}")
    print(f"  Mean tag recall (surface matcher): {np.mean(recalls):.4f}")
    print(f"  Mean tag precision:                {np.mean(precisions):.4f}")
    print(f"  Answer correct (surface only):     {np.mean(answer_accs):.1%}")
    print()
    for r in valid:
        ans_mark = "✓" if r["answer_correct"] else "✗"
        print(
            f"  [{r['source'][:30]}] recall={r['mean_tag_recall']:.2f}  "
            f"prec={r['mean_tag_precision']:.2f}  "
            f"answer={r['selected_answer']}({ans_mark})  "
            f"stem: {r['stem']}"
        )
        for od in r["option_details"]:
            print(
                f"    {od['option_id']}: gt={od['gt_tags']} pred={od['pred_tags']}  "
                f"recall={od['recall']:.2f}  \"{od['option_text']}\""
            )
    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate facet latency approaches")
    parser.add_argument(
        "--generated-dir",
        default="outputs/first_pass_no_books",
        help="Directory with generated item JSONs",
    )
    parser.add_argument(
        "--approach",
        choices=["embedding", "surface", "both"],
        default="both",
    )
    parser.add_argument(
        "--surface-model",
        default="gemini/gemini-2.5-flash",
        help="Model for surface matching approach",
    )
    args = parser.parse_args()

    facet_map = load_facet_map("confidence_intervals")
    facet_lookup = build_facet_lookup(facet_map)

    expert_items = extract_expert_items(facet_map)
    generated_items = extract_generated_items(Path(args.generated_dir))

    print(f"Expert items: {len(expert_items)}")
    print(f"Generated items: {len(generated_items)}")

    if args.approach in ("embedding", "both"):
        print("\nLoading embedding model...")
        embed_model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

        expert_emb = measure_embedding_similarity(expert_items, facet_lookup, embed_model)
        gen_emb = measure_embedding_similarity(generated_items, facet_lookup, embed_model)

        print_embedding_summary("EMBEDDING SIMILARITY — Expert Examples", expert_emb)
        print_embedding_summary("EMBEDDING SIMILARITY — Generated (v1)", gen_emb)

        expert_mean = np.mean([r["mean_similarity"] for r in expert_emb])
        gen_mean = np.mean([r["mean_similarity"] for r in gen_emb])
        print(f"  DELTA (generated - expert): {gen_mean - expert_mean:+.4f}")
        print(f"  {'→ Generated items are MORE similar to facet defs (less latent)' if gen_mean > expert_mean else '→ Generated items are LESS similar to facet defs (more latent)'}")

    if args.approach in ("surface", "both"):
        print(f"\nRunning surface matching with {args.surface_model}...")

        expert_surf = measure_surface_matching(expert_items, facet_lookup, model=args.surface_model)
        gen_surf = measure_surface_matching(generated_items, facet_lookup, model=args.surface_model)

        print_surface_summary("SURFACE MATCHING — Expert Examples", expert_surf)
        print_surface_summary("SURFACE MATCHING — Generated (v1)", gen_surf)

        expert_recall = np.mean([r["mean_tag_recall"] for r in expert_surf if "error" not in r])
        gen_recall = np.mean([r["mean_tag_recall"] for r in gen_surf if "error" not in r])
        expert_ans = np.mean([r["answer_correct"] for r in expert_surf if "error" not in r])
        gen_ans = np.mean([r["answer_correct"] for r in gen_surf if "error" not in r])
        print(f"  DELTA tag recall (generated - expert): {gen_recall - expert_recall:+.4f}")
        print(f"  DELTA answer acc (generated - expert): {gen_ans - expert_ans:+.1%}")


if __name__ == "__main__":
    main()
