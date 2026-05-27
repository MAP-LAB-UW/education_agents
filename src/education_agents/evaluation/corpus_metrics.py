"""Corpus-level evaluation rubrics."""

from __future__ import annotations

import os
from itertools import combinations

import numpy as np
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from ..llm import structured_complete
from ..schemas import FacetMap, RunArtifact
from .facet_latency import _get_model
from .schemas import (
    CorpusEvaluation,
    FacetCombinationDiversityResult,
    FacetCoverageResult,
    ProblemDiversityResult,
    SemanticDiversityResult,
    SimilarityWithExpertsResult,
    StructuralDiversityResult,
)

DEFAULT_EVAL_MODEL = os.getenv(
    "EDU_AGENTS_EVAL_MODEL", "gemini/gemini-3.1-pro-preview"
)


# ── Facet Coverage (Uniformity) ─────────────────────────────────────────────

def _normalized_entropy(counts: list[int]) -> float:
    total = sum(counts)
    if total == 0 or len(counts) <= 1:
        return 0.0
    probs = np.array(counts, dtype=float) / total
    probs = probs[probs > 0]
    entropy = -np.sum(probs * np.log2(probs))
    max_entropy = np.log2(len(counts))
    return float(entropy / max_entropy) if max_entropy > 0 else 0.0


def evaluate_facet_coverage(
    artifacts: list[RunArtifact],
    facet_map: FacetMap,
) -> FacetCoverageResult:
    all_facet_ids = [f.id for f in facet_map.facets]
    counts: dict[str, int] = {fid: 0 for fid in all_facet_ids}

    for art in artifacts:
        for opt in art.item.options:
            for tag in opt.facet_tags:
                if tag in counts:
                    counts[tag] += 1

    return FacetCoverageResult(
        facet_counts=counts,
        total_facets_in_map=len(all_facet_ids),
        covered_facets=sum(1 for v in counts.values() if v > 0),
        uniformity=_normalized_entropy(list(counts.values())),
    )


# ── Facet Combination Diversity ──────────────────────────────────────────────

def _jaccard_distance(a: set, b: set) -> float:
    union = a | b
    if not union:
        return 0.0
    return 1.0 - len(a & b) / len(union)


def evaluate_facet_combination_diversity(
    artifacts: list[RunArtifact],
) -> FacetCombinationDiversityResult:
    facet_sets = [frozenset(art.item.target_facets) for art in artifacts]
    unique = set(facet_sets)

    distances = []
    for a, b in combinations(facet_sets, 2):
        distances.append(_jaccard_distance(set(a), set(b)))

    mean_dist = float(np.mean(distances)) if distances else 0.0

    return FacetCombinationDiversityResult(
        total_items=len(facet_sets),
        unique_combinations=len(unique),
        combination_ratio=len(unique) / len(facet_sets) if facet_sets else 0.0,
        mean_pairwise_jaccard_distance=round(mean_dist, 4),
    )


# ── Problem Diversity: Structural ───────────────────────────────────────────

class _StyleClassification(BaseModel):
    style: str


STYLE_SYSTEM = """Classify this multiple-choice item into exactly one style category.

Categories:
- "numerical": Options are specific numbers, calculations, or formulas.
- "interpretation": Options are competing interpretations of a specific statistical result (e.g., a confidence interval).
- "prediction": The question asks what happens when something changes.
- "action": Options are concrete actions the researcher should take.
- "conceptual": Options are conceptual statements about properties or definitions.

Respond with the single best-fitting category."""


def _classify_item_style(
    stem: str,
    options_text: str,
    model: str,
) -> str:
    messages = [
        {"role": "system", "content": STYLE_SYSTEM},
        {"role": "user", "content": f"Stem: {stem}\n\nOptions:\n{options_text}"},
    ]
    result = structured_complete(messages, _StyleClassification, model=model)
    return result.style


def evaluate_structural_diversity(
    artifacts: list[RunArtifact],
    model: str | None = None,
) -> StructuralDiversityResult:
    model = model or DEFAULT_EVAL_MODEL

    format_counts: dict[str, int] = {}
    style_counts: dict[str, int] = {}

    for art in artifacts:
        fmt = art.item.response_format
        format_counts[fmt] = format_counts.get(fmt, 0) + 1

        options_text = "\n".join(f"  {o.id}. {o.text}" for o in art.item.options)
        style = _classify_item_style(art.item.stem, options_text, model)
        style_counts[style] = style_counts.get(style, 0) + 1

    return StructuralDiversityResult(
        format_distribution=format_counts,
        format_entropy=_normalized_entropy(list(format_counts.values())),
        style_distribution=style_counts,
        style_entropy=_normalized_entropy(list(style_counts.values())),
    )


# ── Problem Diversity: Semantic ──────────────────────────────────────────────

def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def evaluate_semantic_diversity(
    artifacts: list[RunArtifact],
    embed_model: SentenceTransformer | None = None,
) -> SemanticDiversityResult:
    embed_model = embed_model or _get_model()

    stems = [art.item.stem for art in artifacts]
    source_ids = [art.request.topic + "_" + str(i) for i, art in enumerate(artifacts)]

    if len(stems) < 2:
        return SemanticDiversityResult(
            mean_pairwise_similarity=0.0,
            max_pairwise_similarity=0.0,
            most_similar_pair=[],
        )

    embeddings = embed_model.encode(stems)

    max_sim = -1.0
    max_pair: list[str] = []
    sims = []
    for i, j in combinations(range(len(stems)), 2):
        sim = _cosine_sim(embeddings[i], embeddings[j])
        sims.append(sim)
        if sim > max_sim:
            max_sim = sim
            max_pair = [source_ids[i], source_ids[j]]

    return SemanticDiversityResult(
        mean_pairwise_similarity=round(float(np.mean(sims)), 4),
        max_pairwise_similarity=round(max_sim, 4),
        most_similar_pair=max_pair,
    )


def evaluate_similarity_with_experts(
    stems: list[str],
    source_ids: list[str],
    reference_stems: list[str] | None = None,
    reference_ids: list[str] | None = None,
    embed_model: SentenceTransformer | None = None,
) -> list[SimilarityWithExpertsResult]:
    """Compute per-item similarity against a reference set.

    If reference_stems is None, compares within stems (leave-one-out).
    """
    embed_model = embed_model or _get_model()

    if reference_stems is None:
        reference_stems = stems
        reference_ids = source_ids
        self_compare = True
    else:
        self_compare = False

    if not reference_stems:
        return [SimilarityWithExpertsResult(
            mean_similarity=0.0, max_similarity=0.0, most_similar_to="",
        ) for _ in stems]

    query_emb = embed_model.encode(stems)
    ref_emb = embed_model.encode(reference_stems) if not self_compare else query_emb

    results = []
    for i in range(len(stems)):
        sims = []
        max_sim = -1.0
        max_j = 0
        for j in range(len(reference_stems)):
            if self_compare and i == j:
                continue
            sim = _cosine_sim(query_emb[i], ref_emb[j])
            sims.append(sim)
            if sim > max_sim:
                max_sim = sim
                max_j = j
        results.append(SimilarityWithExpertsResult(
            mean_similarity=round(float(np.mean(sims)), 4) if sims else 0.0,
            max_similarity=round(max_sim, 4) if sims else 0.0,
            most_similar_to=reference_ids[max_j] if sims else "",
        ))
    return results


# ── Combined ─────────────────────────────────────────────────────────────────

def evaluate_corpus(
    artifacts: list[RunArtifact],
    facet_map: FacetMap,
    eval_model: str | None = None,
    embed_model: SentenceTransformer | None = None,
) -> CorpusEvaluation:
    embed_model = embed_model or _get_model()

    coverage = evaluate_facet_coverage(artifacts, facet_map)
    combination = evaluate_facet_combination_diversity(artifacts)
    structural = evaluate_structural_diversity(artifacts, model=eval_model)
    semantic = evaluate_semantic_diversity(artifacts, embed_model=embed_model)

    items_with_figures = sum(1 for a in artifacts if a.item.figures)
    fig_frac = items_with_figures / len(artifacts) if artifacts else 0.0

    return CorpusEvaluation(
        facet_coverage=coverage,
        facet_combination_diversity=combination,
        problem_diversity=ProblemDiversityResult(
            structural=structural,
            semantic=semantic,
        ),
        figure_fraction=round(fig_frac, 4),
    )
