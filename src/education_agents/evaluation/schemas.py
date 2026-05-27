"""Schemas for evaluation rubric outputs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


# ── Item-level rubrics ───────────────────────────────────────────────────────

class CorrectnessResult(BaseModel):
    selected_answer: str
    correct_answer_ids: list[str]
    is_correct: bool
    flagged_distractors: list[str]
    reasoning: str


class NaturalnessResult(BaseModel):
    stem_score: int
    stem_reasoning: str
    options_score: int
    options_reasoning: str
    overall_score: int


LatencyBucket = Literal["highly_latent", "latent", "surface", "paraphrase"]


class OptionLatency(BaseModel):
    option_id: str
    similarity: float
    score: int
    bucket: LatencyBucket
    facet_tags: list[str]


class FacetLatencyResult(BaseModel):
    mean_similarity: float
    score: int
    bucket: LatencyBucket
    option_details: list[OptionLatency]


class FigureNecessityTrial(BaseModel):
    selected_answer: str
    is_correct: bool
    reasoning: str


class FigureNecessityResult(BaseModel):
    is_necessary: bool
    n_trials: int
    n_correct: int
    trials: list[FigureNecessityTrial]


class SimilarityWithExpertsResult(BaseModel):
    mean_similarity: float
    max_similarity: float
    most_similar_to: str


class ItemEvaluation(BaseModel):
    source: str
    correctness: CorrectnessResult
    naturalness: NaturalnessResult
    facet_latency: FacetLatencyResult
    figure_necessity: int | None = None
    similarity_with_experts: SimilarityWithExpertsResult | None = None


# ── Corpus-level rubrics ─────────────────────────────────────────────────────

class FacetCoverageResult(BaseModel):
    facet_counts: dict[str, int]
    total_facets_in_map: int
    covered_facets: int
    uniformity: float


class FacetCombinationDiversityResult(BaseModel):
    total_items: int
    unique_combinations: int
    combination_ratio: float
    mean_pairwise_jaccard_distance: float


class StructuralDiversityResult(BaseModel):
    format_distribution: dict[str, int]
    format_entropy: float
    style_distribution: dict[str, int]
    style_entropy: float


class SemanticDiversityResult(BaseModel):
    mean_pairwise_similarity: float
    max_pairwise_similarity: float
    most_similar_pair: list[str]


class ProblemDiversityResult(BaseModel):
    structural: StructuralDiversityResult
    semantic: SemanticDiversityResult


class CorpusEvaluation(BaseModel):
    facet_coverage: FacetCoverageResult
    facet_combination_diversity: FacetCombinationDiversityResult
    problem_diversity: ProblemDiversityResult
    figure_fraction: float | None = None
