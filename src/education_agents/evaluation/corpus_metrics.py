"""Corpus-level evaluation rubrics."""

from __future__ import annotations

import os
from itertools import combinations

import numpy as np
from pydantic import BaseModel
from scipy.optimize import linear_sum_assignment
from sentence_transformers import SentenceTransformer

from ..llm import structured_complete
from ..schemas import FacetMap, RunArtifact
from .facet_latency import _get_model
from .schemas import (
    CorpusEvaluation,
    FacetCombinationDiversityResult,
    FacetCoverageResult,
    FacetQMatrixDiversityResult,
    ProblemDiversityResult,
    SemanticDiversityResult,
    SimilarityWithExpertsResult,
    StructuralDiversityResult,
)

DEFAULT_EVAL_MODEL = os.getenv(
    "EDU_AGENTS_EVAL_MODEL", "anthropic/claude-sonnet-4-6"
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


# Weight on the stem in the combined item similarity; the remainder (1 - w) goes
# to the permutation-invariant options match.
DEFAULT_STEM_WEIGHT = 0.5


def _encode_items(
    stems: list[str],
    options: list[list[str]] | None,
    embed_model: SentenceTransformer,
) -> tuple[np.ndarray, list[np.ndarray]]:
    """Embed stems and (optionally) per-item option texts in batched calls.

    Returns (stem_embeddings [n, d], per_item_option_embeddings [n][k_i, d]).
    If options is None, every item gets an empty option matrix and similarity
    falls back to stem-only.
    """
    stem_emb = np.asarray(embed_model.encode(stems))
    dim = stem_emb.shape[1] if stem_emb.size else 0

    if options is None:
        return stem_emb, [np.empty((0, dim)) for _ in stems]

    flat: list[str] = []
    spans: list[tuple[int, int]] = []
    for opts in options:
        spans.append((len(flat), len(flat) + len(opts)))
        flat.extend(opts)

    flat_emb = (
        np.asarray(embed_model.encode(flat)) if flat else np.empty((0, dim))
    )
    opt_embs = [flat_emb[s:e] for s, e in spans]
    return stem_emb, opt_embs


def _pi_item_similarity(
    stem_a: np.ndarray,
    opts_a: np.ndarray,
    stem_b: np.ndarray,
    opts_b: np.ndarray,
    stem_weight: float = DEFAULT_STEM_WEIGHT,
) -> float:
    """Permutation-invariant similarity between two items.

    sim_pi(A, B) = w * cos(stem_A, stem_B)
                 + (1 - w) * max over permutations p of mean_i cos(a_i, b_p(i))

    The options term is a maximum-weight bipartite matching (solved exactly via
    the Hungarian algorithm), so each option of A is paired with a *distinct*
    option of B. Unequal option counts match min(k_A, k_B) pairs. With no
    options on either side it reduces to stem cosine similarity.
    """
    stem_sim = _cosine_sim(stem_a, stem_b)
    if len(opts_a) == 0 or len(opts_b) == 0:
        return stem_sim

    a = opts_a / (np.linalg.norm(opts_a, axis=1, keepdims=True) + 1e-9)
    b = opts_b / (np.linalg.norm(opts_b, axis=1, keepdims=True) + 1e-9)
    m = a @ b.T  # [k_A, k_B] pairwise cosine similarities
    row, col = linear_sum_assignment(-m)  # optimal one-to-one pairing
    opt_sim = float(m[row, col].mean())

    return stem_weight * stem_sim + (1.0 - stem_weight) * opt_sim


def evaluate_semantic_diversity(
    artifacts: list[RunArtifact],
    embed_model: SentenceTransformer | None = None,
    stem_weight: float = DEFAULT_STEM_WEIGHT,
) -> SemanticDiversityResult:
    embed_model = embed_model or _get_model()

    stems = [art.item.stem for art in artifacts]
    options = [[o.text for o in art.item.options] for art in artifacts]
    source_ids = [
        f"{getattr(getattr(art, 'request', None), 'topic', 'item')}_{i}"
        for i, art in enumerate(artifacts)
    ]

    if len(stems) < 2:
        return SemanticDiversityResult(
            mean_pairwise_similarity=0.0,
            max_pairwise_similarity=0.0,
            most_similar_pair=[],
        )

    stem_emb, opt_embs = _encode_items(stems, options, embed_model)

    max_sim = -1.0
    max_pair: list[str] = []
    sims = []
    for i, j in combinations(range(len(stems)), 2):
        sim = _pi_item_similarity(
            stem_emb[i], opt_embs[i], stem_emb[j], opt_embs[j], stem_weight
        )
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
    options: list[list[str]] | None = None,
    reference_stems: list[str] | None = None,
    reference_ids: list[str] | None = None,
    reference_options: list[list[str]] | None = None,
    embed_model: SentenceTransformer | None = None,
    stem_weight: float = DEFAULT_STEM_WEIGHT,
) -> list[SimilarityWithExpertsResult]:
    """Compute per-item permutation-invariant similarity against a reference set.

    If reference_stems is None, compares within stems (leave-one-out).
    Pass `options` / `reference_options` (per-item option texts) to fold the
    answer choices into the representation; omit them for stem-only similarity.
    """
    embed_model = embed_model or _get_model()

    if reference_stems is None:
        reference_stems = stems
        reference_ids = source_ids
        reference_options = options
        self_compare = True
    else:
        self_compare = False

    if not reference_stems:
        return [SimilarityWithExpertsResult(
            mean_similarity=0.0, max_similarity=0.0, most_similar_to="",
        ) for _ in stems]

    query_stem, query_opts = _encode_items(stems, options, embed_model)
    if self_compare:
        ref_stem, ref_opts = query_stem, query_opts
    else:
        ref_stem, ref_opts = _encode_items(reference_stems, reference_options, embed_model)

    results = []
    for i in range(len(stems)):
        sims = []
        max_sim = -1.0
        max_j = 0
        for j in range(len(reference_stems)):
            if self_compare and i == j:
                continue
            sim = _pi_item_similarity(
                query_stem[i], query_opts[i], ref_stem[j], ref_opts[j], stem_weight
            )
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


# ── Problem Diversity: Facet Q-matrix ────────────────────────────────────────

def _item_qmatrix(art: RunArtifact, facet_ids: list[str]) -> np.ndarray:
    """Binary (n_options x n_facets) Q-matrix for one item.

    Q[i, j] = 1 iff option i is tagged with facet_ids[j]. Facet tags not present
    in the map are ignored so every item shares the same column space.
    """
    col = {fid: j for j, fid in enumerate(facet_ids)}
    q = np.zeros((len(art.item.options), len(facet_ids)), dtype=float)
    for i, opt in enumerate(art.item.options):
        for tag in opt.facet_tags:
            j = col.get(tag)
            if j is not None:
                q[i, j] = 1.0
    return q


def _row_jaccard(q_a: np.ndarray, q_b: np.ndarray) -> np.ndarray:
    """Pairwise Jaccard similarity between the rows of two binary matrices.

    Returns a [k_A, k_B] matrix. Two all-zero rows (options that probe no
    mapped facet) count as identical (similarity 1.0), matching the convention
    in `_jaccard_distance` that an empty union has zero distance.
    """
    inter = q_a @ q_b.T  # [k_A, k_B] shared-facet counts
    size_a = q_a.sum(axis=1, keepdims=True)  # [k_A, 1]
    size_b = q_b.sum(axis=1, keepdims=True)  # [k_B, 1]
    union = size_a + size_b.T - inter
    with np.errstate(divide="ignore", invalid="ignore"):
        sim = np.where(union > 0, inter / union, 1.0)
    return sim


def _pi_qmatrix_similarity(q_a: np.ndarray, q_b: np.ndarray) -> float:
    """Permutation-invariant similarity between two Facet Q-matrices.

    sim(A, B) = max over one-to-one option pairings of mean_i jaccard(a_i, b_p(i))

    The pairing is a maximum-weight bipartite matching solved via the Hungarian
    algorithm, so each option of A is matched to a *distinct* option of B and
    the score is invariant to option ordering. Unequal option counts match
    min(k_A, k_B) rows.
    """
    if q_a.shape[0] == 0 or q_b.shape[0] == 0:
        return 0.0
    sim = _row_jaccard(q_a, q_b)
    row, col = linear_sum_assignment(-sim)
    return float(sim[row, col].mean())


def evaluate_facet_qmatrix_diversity(
    artifacts: list[RunArtifact],
    facet_map: FacetMap,
) -> FacetQMatrixDiversityResult:
    facet_ids = [f.id for f in facet_map.facets]
    qmats = [_item_qmatrix(art, facet_ids) for art in artifacts]
    source_ids = [
        f"{getattr(getattr(art, 'request', None), 'topic', 'item')}_{i}"
        for i, art in enumerate(artifacts)
    ]

    if len(qmats) < 2:
        return FacetQMatrixDiversityResult(
            mean_pairwise_similarity=0.0,
            max_pairwise_similarity=0.0,
            most_similar_pair=[],
        )

    max_sim = -1.0
    max_pair: list[str] = []
    sims = []
    for i, j in combinations(range(len(qmats)), 2):
        sim = _pi_qmatrix_similarity(qmats[i], qmats[j])
        sims.append(sim)
        if sim > max_sim:
            max_sim = sim
            max_pair = [source_ids[i], source_ids[j]]

    return FacetQMatrixDiversityResult(
        mean_pairwise_similarity=round(float(np.mean(sims)), 4),
        max_pairwise_similarity=round(max_sim, 4),
        most_similar_pair=max_pair,
    )


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
    facet_qmatrix = evaluate_facet_qmatrix_diversity(artifacts, facet_map)

    items_with_figures = sum(1 for a in artifacts if a.item.figures)
    fig_frac = items_with_figures / len(artifacts) if artifacts else 0.0

    return CorpusEvaluation(
        facet_coverage=coverage,
        facet_combination_diversity=combination,
        problem_diversity=ProblemDiversityResult(
            structural=structural,
            semantic=semantic,
            facet_qmatrix=facet_qmatrix,
        ),
        figure_fraction=round(fig_frac, 4),
    )
