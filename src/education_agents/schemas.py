"""Pydantic schemas for the diagnostic assessment pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Facet(BaseModel):
    id: str
    type: Literal["goal", "problematic"]
    text: str


class ExampleOption(BaseModel):
    id: str
    text: str
    facet_tags: list[str]
    is_correct: bool


class Example(BaseModel):
    stem: str
    response_format: Literal["single_select", "multi_select", "true_false_per_option"]
    options: list[ExampleOption]


class FacetMap(BaseModel):
    topic: str
    course: str
    facets: list[Facet]
    examples: list[Example]


# ---------- Facet selection ----------

class FacetSelection(BaseModel):
    target_facets: list[str]
    reasoning: str


# ---------- Generated item ----------

class Option(BaseModel):
    id: str
    text: str
    facet_tags: list[str]
    is_correct: bool
    rationale: str


class Figure(BaseModel):
    id: str
    python_code: str
    alt_text: str = ""


class GeneratedItem(BaseModel):
    stem: str
    response_format: Literal["single_select", "multi_select", "true_false_per_option"]
    options: list[Option]
    correct_option_ids: list[str]
    explanation: str
    target_facets: list[str]
    figures: list[Figure] = []


# ---------- Judge report ----------

class OptionAssessment(BaseModel):
    option_id: str
    generator_tags: list[str]
    judge_tags: list[str]
    agreement: Literal["match", "partial", "mismatch"]
    confidence: float
    reasoning: str


class JudgeReport(BaseModel):
    item_stem_preview: str
    option_assessments: list[OptionAssessment]
    overall_agreement: float
    overall_confidence: float
    issues: list[str]


# ---------- Pipeline I/O ----------

class GenerationRequest(BaseModel):
    topic: str
    target_facets: list[str] = []
    response_format: Literal["single_select", "multi_select", "true_false_per_option"] | None = None
    num_options: int | None = None
    book_context_mode: Literal["none", "full_tex", "rag"] = "none"
    n_items: int = 1
    exclude_image_examples: bool = True
    prompt_version: Literal["v1", "v2", "v3"] = "v1"

    @property
    def auto_select_facets(self) -> bool:
        return len(self.target_facets) == 0

    @property
    def auto_select_format(self) -> bool:
        return self.response_format is None

    @property
    def auto_select_num_options(self) -> bool:
        return self.num_options is None


class EvalScores(BaseModel):
    correctness_pass: bool
    correctness_flagged_distractors: list[str] = []
    naturalness_stem: int
    naturalness_options: int
    naturalness_overall: int
    latency_score: int
    latency_similarity: float
    latency_bucket: str
    latency_option_details: list[dict] = []
    figure_necessity: int | None = None


class RunArtifact(BaseModel):
    request: GenerationRequest
    models: dict[str, str]
    facet_selection_reasoning: str | None = None
    item: GeneratedItem
    judge_report: JudgeReport
    eval_scores: EvalScores | None = None
    figure_data: dict[str, str] = {}
    timing: dict[str, float]
    created_at: str
