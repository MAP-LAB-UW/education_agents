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


class FigureSpoilerTrial(BaseModel):
    gives_away_answer: bool
    leaked_via: str
    reasoning: str


class FigureSpoilerResult(BaseModel):
    gives_away_answer: bool
    n_trials: int
    n_giveaway: int
    trials: list[FigureSpoilerTrial]


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
    figure_spoiler: int | None = None
    similarity_with_experts: SimilarityWithExpertsResult | None = None


# ── Student simulator ────────────────────────────────────────────────────────

class PersonaResult(BaseModel):
    source: str
    group_key: str
    persona_facets: list[str]
    target_option_id: str
    mode: Literal["open", "select"]
    student_reasoning: str
    student_answer: str
    exhibits_misconception: bool
    judge_reasoning: str
    # Phase 2 (item diagnosticity) — left unset during simulator validation.
    mapped_option_id: str | None = None
    lands_on_target: bool | None = None
    lands_on_consistent_option: bool | None = None


class GroupFidelity(BaseModel):
    group_key: str
    n_trials: int
    misconception_fidelity: float
    open_target_rate: float | None = None
    select_target_rate: float | None = None


class SimulatorEvalReport(BaseModel):
    by_group: list[GroupFidelity]
    by_source: dict[str, float]
    overall_fidelity: float
    single_facet_fidelity: float
    multi_facet_fidelity: float
    n_single_facet_runs: int
    n_multi_facet_runs: int
    persona_results: list[PersonaResult]


# ── Method comparison (belief-injection vs. few-shot persona) ─────────────────

class SampleAttempt(BaseModel):
    answer: str
    selected_ids: list[str]
    hit: bool
    reasoning: str
    exhibits_misconception: bool | None = None
    naturalness: int | None = None


class MethodItemResult(BaseModel):
    method: Literal["belief", "fewshot"]
    source: str
    group_key: str
    persona_facets: list[str]
    target_option_id: str
    k_samples: int
    n_hits: int
    hit_rate: float
    fidelity_among_hits: float | None = None
    naturalness_among_hits: float | None = None
    n_shots: int = 0
    attempts: list[SampleAttempt] = []


class ComparisonReport(BaseModel):
    results: list[MethodItemResult]


# ── Selector check (belief-injection select mode, small model) ────────────────

MissCategory = Literal[
    "model_did_not_adopt", "item_not_diagnostic", "model_inconsistent", "other"
]


class SelectorAttempt(BaseModel):
    answer: str
    selected_ids: list[str]
    hit: bool
    reasoning: str
    exhibits_misconception: bool | None = None   # judged on hits
    miss_category: MissCategory | None = None     # judged on misses
    miss_explanation: str | None = None


class SelectorItemResult(BaseModel):
    source: str
    group_key: str
    persona_facets: list[str]
    target_option_id: str
    k_samples: int
    n_hits: int
    hit_rate: float
    attempts: list[SelectorAttempt] = []


# ── Simulator v2: open-mode battery with negative controls ───────────────────

class SimV2Attempt(BaseModel):
    """One (item, persona, sample) open-mode run, mapped and lineup-judged."""
    source: str
    persona_key: str               # misconception group key, or "control"
    persona_facets: list[str]      # empty for control
    sample_index: int
    student_reasoning: str
    student_answer: str
    # Blind mapper: which option(s) the free response corresponds to.
    mapped_option_ids: list[str]
    mapper_no_match: bool
    mapper_reasoning: str
    # Select-mode fallback: run only when the open answer maps to no option
    # (e.g. option-dependent stems the persona can't engage with blind).
    fallback_used: bool = False
    fallback_option_ids: list[str] | None = None
    fallback_reasoning: str | None = None
    fallback_answer: str | None = None
    # Blind lineup judge (misconception personas only).
    exhibited_facet_ids: list[str] | None = None
    judged_reasoning_correct: bool | None = None
    lineup_judge_reasoning: str | None = None


class TargetDiagnostic(BaseModel):
    """Selection-rate gap for one misconception-keyed option."""
    source: str
    target_option_id: str
    group_key: str
    n_matched: int
    n_alternative: int
    n_control: int
    matched_target_rate: float                 # P(target | matched persona)
    alternative_target_rate: float | None      # P(target | other misconception personas)
    control_target_rate: float | None          # P(target | no-misconception persona)
    selection_gap: float                       # matched − pooled(alternative + control)
    matched_lineup_id_rate: float | None       # blind judge identified the target facets
    matched_open_no_match_rate: float | None = None  # open answer mapped to no option


class SimV2GroupSummary(BaseModel):
    group_key: str
    n_targets: int
    mean_matched_rate: float
    mean_gap: float
    mean_lineup_id_rate: float | None


class SimV2Report(BaseModel):
    n_items: int
    n_attempts: int
    k_samples: int
    overall_matched_rate: float
    overall_alternative_rate: float | None
    overall_control_target_rate: float | None
    overall_gap: float
    control_correct_rate: float | None         # control persona maps exactly onto the key
    lineup_id_rate: float | None               # among matched-persona attempts
    open_no_match_rate: float | None = None    # attempts whose open answer mapped nowhere
    by_group: list[SimV2GroupSummary]
    per_target: list[TargetDiagnostic]
    attempts: list[SimV2Attempt]


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


class FacetQMatrixDiversityResult(BaseModel):
    """Order-invariant similarity over per-item Facet Q-matrices.

    Each item's Q-matrix is an (n_options x n_facets) binary indicator of which
    facets each option probes. Pairwise similarity matches option rows across
    two items via optimal bipartite assignment (permutation-invariant) and
    averages the per-row Jaccard overlap.
    """
    mean_pairwise_similarity: float
    max_pairwise_similarity: float
    most_similar_pair: list[str]


class ProblemDiversityResult(BaseModel):
    structural: StructuralDiversityResult
    semantic: SemanticDiversityResult
    facet_qmatrix: FacetQMatrixDiversityResult | None = None


class CorpusEvaluation(BaseModel):
    facet_coverage: FacetCoverageResult
    facet_combination_diversity: FacetCombinationDiversityResult
    problem_diversity: ProblemDiversityResult
    figure_fraction: float | None = None
