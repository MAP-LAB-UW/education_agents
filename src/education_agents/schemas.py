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


class GeneratedItem(BaseModel):
    stem: str
    response_format: Literal["single_select", "multi_select", "true_false_per_option"]
    options: list[Option]
    correct_option_ids: list[str]
    explanation: str
    target_facets: list[str]


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
    response_format: Literal["single_select", "multi_select", "true_false_per_option"] = "single_select"
    num_options: int = 4
    book_context_mode: Literal["none", "full_tex", "rag"] = "none"
    n_items: int = 1
    exclude_image_examples: bool = True

    @property
    def auto_select_facets(self) -> bool:
        return len(self.target_facets) == 0


class RunArtifact(BaseModel):
    request: GenerationRequest
    models: dict[str, str]
    facet_selection_reasoning: str | None = None
    item: GeneratedItem
    judge_report: JudgeReport
    timing: dict[str, float]
    created_at: str
