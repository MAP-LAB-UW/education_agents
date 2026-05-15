"""Facet latency rubric: embedding similarity between options and facet definitions."""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from ..schemas import FacetMap, GeneratedItem
from .schemas import FacetLatencyResult, LatencyBucket, OptionLatency

EMBEDDING_MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"

BUCKET_THRESHOLDS: list[tuple[float, LatencyBucket, int]] = [
    (0.55, "highly_latent", 4),
    (0.70, "latent", 3),
    (0.80, "surface", 2),
    (float("inf"), "paraphrase", 1),
]

_model_cache: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model_cache
    if _model_cache is None:
        _model_cache = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model_cache


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def _to_bucket_and_score(similarity: float) -> tuple[LatencyBucket, int]:
    for threshold, bucket, score in BUCKET_THRESHOLDS:
        if similarity < threshold:
            return bucket, score
    return "paraphrase", 1


def evaluate_facet_latency(
    item: GeneratedItem,
    facet_map: FacetMap,
    model: SentenceTransformer | None = None,
) -> FacetLatencyResult:
    model = model or _get_model()
    facet_lookup = {f.id: f.text for f in facet_map.facets}

    option_details = []
    for opt in item.options:
        facet_texts = [facet_lookup[fid] for fid in opt.facet_tags if fid in facet_lookup]
        if not facet_texts:
            continue

        facet_concat = " ".join(facet_texts)
        embeddings = model.encode([opt.text, facet_concat])
        sim = _cosine_sim(embeddings[0], embeddings[1])
        bucket, score = _to_bucket_and_score(sim)

        option_details.append(OptionLatency(
            option_id=opt.id,
            similarity=round(sim, 4),
            score=score,
            bucket=bucket,
            facet_tags=opt.facet_tags,
        ))

    mean_sim = float(np.mean([o.similarity for o in option_details])) if option_details else 0.0
    mean_bucket, mean_score = _to_bucket_and_score(mean_sim)

    return FacetLatencyResult(
        mean_similarity=round(mean_sim, 4),
        score=mean_score,
        bucket=mean_bucket,
        option_details=option_details,
    )
