# Diagnostic Assessment Copilot — Workflow Design

## 1. Top-level pipeline

```
                ┌─────────────────────┐
                │ Facet map (JSON)    │
                │  + target facets    │
                │  + book context     │
                └──────────┬──────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │ Facet Selection Agent   │  (optional, auto mode)
              └──────────┬──────────────┘
                         │  target_facets
                         ▼
              ┌─────────────────────────┐
              │ Item Generation Agent   │  (LLM call, structured output)
              └──────────┬──────────────┘
                         │  GeneratedItem
                         ▼
              ┌─────────────────────────┐
              │ Verifier / Judge Agent  │  (LLM call, structured output)
              └──────────┬──────────────┘
                         │  JudgeReport
                         ▼
              ┌─────────────────────────┐
              │ Evaluation Rubrics      │  (LLM + embedding, per-item)
              └──────────┬──────────────┘
                         │  EvalScores
                         ▼
              ┌─────────────────────────┐
              │ Persisted run artifact  │  (item + report + eval + metadata)
              └─────────────────────────┘
```

Corpus-level evaluation runs separately across a batch of artifacts via `scripts/run_evaluation.py`.

## 2. Inputs

### 2.1 Facet map (`data/facets/<topic>.json`)

```json
{
  "topic": "confidence_intervals",
  "course": "statistics",
  "facets": [
    {"id": "A1", "type": "goal",        "text": "Students understand that as sample size increases, ..."},
    {"id": "B7", "type": "problematic", "text": "CI is interpreted as probabilities of including true population means"}
  ],
  "examples": [
    {
      "stem": "...",
      "response_format": "single_select" | "multi_select" | "true_false_per_option",
      "options": [
        {"text": "...", "facet_tags": ["B9"], "is_correct": false}
      ]
    }
  ]
}
```

`type` ∈ `{goal, problematic}`. Examples come from `workflow/facets.md`.

### 2.2 Generation request

A single call specifies:
- `topic` (which facet map to load)
- `target_facets`: list of facet IDs the item should diagnose (e.g., `["A4", "B7", "B9"]`). If empty, the pipeline auto-selects facets per item.
- `response_format`: `single_select` | `multi_select` | `true_false_per_option` | `null`. When null, the model chooses the best format for the problem.
- `num_options`: typically 3–6, or `null` to let the model choose.
- `book_context_mode`: `none` | `full_tex` | `rag` (rag = `NotImplementedError` for now)
- `n_items`: how many to generate (each is an independent LLM call)
- `exclude_image_examples`: whether to omit image-based few-shot examples (default true)
- `prompt_version`: `v1` | `v2` (see §3.5)

### 2.3 Book context modes

| mode | implementation |
|---|---|
| `none` | no book content in prompt |
| `full_tex` | inline the entire `docs/edpsy490_ch_5.tex` (511 lines, fits comfortably) into the system prompt under a `<book_chapter>` tag |
| `rag` | stub — raises `NotImplementedError("RAG mode not implemented yet")` |

The mode is recorded in the run artifact so we can compare quality across modes later.

## 3. Item Generation Agent

### 3.1 Facet auto-selection

When `target_facets` is empty, the pipeline calls a facet selection agent before generation. The selector receives the full facet map plus the list of facet combinations used by previously generated items in the current batch, and chooses a diverse combination for the next item.

### 3.2 Inputs to the prompt
- Facet map (full list of A and B facets, with text).
- Target facet IDs (the agent must "cover" these — see §3.4 for what coverage means).
- Response format + number of options (or instructions to choose these if null).
- Optional book chapter (per context mode).
- Few-shot examples from the facet map (`examples` field).

### 3.3 Output schema (structured JSON)

```python
class Option(BaseModel):
    id: str                          # "1", "2", ... or "A", "B", ...
    text: str
    facet_tags: list[str]            # e.g. ["A3", "B9"]
    is_correct: bool                 # for single/multi-select: True iff this option is keyed correct
                                     # for true_false_per_option: True means "True is the correct verdict"
    rationale: str                   # short reason this option maps to those facets

class GeneratedItem(BaseModel):
    stem: str
    response_format: Literal["single_select", "multi_select", "true_false_per_option"]
    options: list[Option]
    correct_option_ids: list[str]    # derived; redundant with is_correct but explicit
    explanation: str                 # overall explanation tying the item back to the facets
    target_facets: list[str]         # echo of the request, for traceability
```

### 3.4 Coverage rule (what the prompt enforces)
- Each goal facet (A) in `target_facets` must be tagged on at least one **correct** option.
- Each problematic facet (B) in `target_facets` must be tagged on at least one **incorrect** option (a distractor).
- Every option must have ≥1 facet tag.
- An option may carry multiple tags (e.g., a distractor that conflates A3 with B9).
- Distractors must be plausible — they should represent reasoning a student might actually produce, not strawmen.

### 3.5 Prompt versions

Two generator prompt versions are available, selected via `prompt_version`:

| version | file | description |
|---------|------|-------------|
| `v1` | `prompts/generator.md` | Original prompt. Straightforward coverage-based generation. |
| `v2` | `prompts/generator_v2.md` | Improved prompt with latent-facet design principle, scenario-based stem guidelines, and style variation instructions. |

**V2 core design principle — latent facets:** Facets should be embedded as latent concepts within realistic scenarios. Options must not paraphrase facet definitions; instead they should describe concrete outcomes, actions, or predictions that a student holding a particular understanding (or misconception) would endorse. This was motivated by quantitative comparison showing V1 items had significantly higher embedding similarity to facet definitions (mean 0.716) than expert items (mean 0.576).

### 3.6 Dynamic format and option count

When `response_format` or `num_options` is null, the generator prompt instructs the model to choose the best format and count for the problem:
- `true_false_per_option` when testing multiple independent claims about a single scenario
- `multi_select` when multiple options can be simultaneously correct
- `single_select` for "best answer" questions
- Option count: 3–6, depending on how many distinct facets need representation

## 4. Verifier / Judge Agent

### 4.1 Input
- The full `GeneratedItem`.
- The facet map (so the judge knows what facets exist and what they mean).
- *Not* the original target facets — judge re-derives them from the option text.

### 4.2 Task
For each option, **independently re-tag** which facets it exhibits, then compare against the generator's tags and emit a confidence score.

### 4.3 Output schema

```python
class OptionAssessment(BaseModel):
    option_id: str
    generator_tags: list[str]        # what the generator claimed
    judge_tags: list[str]            # what the judge thinks
    agreement: Literal["match", "partial", "mismatch"]
    confidence: float                # 0.0–1.0, judge's confidence in its OWN tags
    reasoning: str

class JudgeReport(BaseModel):
    item_stem_preview: str           # first 80 chars, for log readability
    option_assessments: list[OptionAssessment]
    overall_agreement: float         # fraction of options with agreement="match"
    overall_confidence: float        # mean of per-option confidences
    issues: list[str]                # e.g., "option 3 has no clear facet", "stem is ambiguous"
```

### 4.4 Prompt structure (`prompts/judge.md`)
1. Role: psychometrician reviewing an MC item.
2. Facet map.
3. The item.
4. Task: independently tag each option, compare to claimed tags, score confidence.
5. Output schema.

## 5. Evaluation Rubrics

Evaluation runs automatically after the judge step (skippable via `--skip-eval`). There are two levels: item-level rubrics (per item) and corpus-level rubrics (across a batch).

Full rubric documentation: `docs/rubrics.md`.

### 5.1 Item-level rubrics

| Rubric | Method | Output | Key metric |
|--------|--------|--------|------------|
| **Correctness** | LLM blind-solves the item (no answer key), flags defensibly-correct distractors | `is_correct`, `flagged_distractors` | Pass/Fail |
| **Naturalness** | LLM-as-judge rates stem (1–5) and options (1–5) for readability and clarity | `stem_score`, `options_score`, `overall_score` | Overall /5 |
| **Facet Latency** | Embedding similarity between option text and concatenated facet definitions | `score` (1–4), `bucket`, `mean_similarity` | Score /4 |

**Facet latency scoring buckets** (empirically calibrated from expert vs. generated item distributions):

| Similarity | Bucket | Score | Interpretation |
|------------|--------|-------|----------------|
| < 0.55 | highly_latent | 4 | Facet deeply embedded in scenario |
| 0.55 – 0.70 | latent | 3 | Present but not a direct paraphrase |
| 0.70 – 0.80 | surface | 2 | Noticeably echoes facet language |
| >= 0.80 | paraphrase | 1 | Near-direct restatement of facet definition |

Embedding model: `Qwen/Qwen3-Embedding-0.6B`.

Item-level results are stored in the `eval_scores` field of each run artifact.

### 5.2 Corpus-level rubrics

| Rubric | Method | Key metric |
|--------|--------|------------|
| **Facet Coverage** | Count per-facet occurrences, compute normalized Shannon entropy | Uniformity (0–1) |
| **Facet Combination Diversity** | Unique facet-set ratio + mean pairwise Jaccard distance | Jaccard distance (0–1) |
| **Structural Diversity** | LLM classifies item style (numerical/interpretation/prediction/action/conceptual) + format distribution; normalized entropy for each | Style entropy, format entropy |
| **Semantic Diversity** | Pairwise cosine similarity of stem embeddings | Mean/max similarity |

Corpus-level evaluation runs via `scripts/run_evaluation.py` or `scripts/eval_experts.py`.

### 5.3 Eval scores schema

```python
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
```

## 6. LLM interface (`src/education_agents/llm.py`)

A thin wrapper over `litellm.completion`:

```python
def complete(messages, model=None, **kwargs) -> str: ...
def structured_complete(messages, schema: type[BaseModel], model=None, **kwargs) -> BaseModel: ...
```

- `model` defaults to `os.getenv("EDU_AGENTS_MODEL", "gemini/gemini-3-flash-preview")`.
- `structured_complete` uses `response_format={"type": "json_schema", "json_schema": ...}` via litellm, with a fallback path that does JSON-mode + schema hint + pydantic validation for providers without strict-schema support.
- `.env` loaded via `python-dotenv`.

Default models:
| Role | Model |
|------|-------|
| Generator | `gemini/gemini-3-flash-preview` |
| Judge | `gemini/gemini-3.1-pro-preview` |
| Eval (LLM rubrics) | `gemini/gemini-3.1-pro-preview` |
| Eval (embeddings) | `Qwen/Qwen3-Embedding-0.6B` |

This is the only file other modules touch when calling LLMs — swapping providers = changing one env var.

## 7. Module layout

```
src/education_agents/
├── __init__.py
├── llm.py              # litellm wrapper
├── schemas.py          # Facet, FacetMap, Option, GeneratedItem, JudgeReport, EvalScores, etc.
├── facets.py           # load_facet_map(topic) -> FacetMap; render_facet_map_for_prompt()
├── book_context.py     # load_book_context(mode, path) -> str | None; raises for "rag"
├── generator.py        # generate_item(request, facet_map, book_context, model) -> GeneratedItem
│                       # select_facets(facet_map, previously_used, model) -> FacetSelection
├── judge.py            # judge_item(item, facet_map, model) -> JudgeReport
├── pipeline.py         # run(request, ...) -> list[RunArtifact]
├── evaluation/
│   ├── __init__.py
│   ├── schemas.py      # CorrectnessResult, NaturalnessResult, FacetLatencyResult, CorpusEvaluation, etc.
│   ├── correctness.py  # evaluate_correctness(item, model) -> CorrectnessResult
│   ├── naturalness.py  # evaluate_naturalness(item, model) -> NaturalnessResult
│   ├── facet_latency.py # evaluate_facet_latency(item, facet_map) -> FacetLatencyResult
│   └── corpus_metrics.py # evaluate_corpus(artifacts, facet_map) -> CorpusEvaluation
└── prompts/
    ├── generator.md    # v1 prompt
    ├── generator_v2.md # v2 prompt (latent-facet, scenario-based)
    └── judge.md
```

```
scripts/
├── run_pipeline.py     # CLI: --topic, --facets, --format, --n-items, --prompt-version, --skip-eval, etc.
├── run_evaluation.py   # CLI: standalone eval on artifact directories
├── eval_experts.py     # CLI: evaluate expert examples from facet map
└── eval_facet_latency.py  # experimental: compare embedding vs surface matching approaches
```

```
web/
├── index.html          # item explorer dashboard
├── app.jsx             # item list, detail, judge report, eval tab, aggregate view
├── mock-data.js        # static facet map for dashboard
├── compare.html        # evaluation comparison dashboard
└── compare.jsx         # side-by-side metrics across runs
```

## 8. Run artifact (`outputs/<timestamp>_<short_hash>.json`)

```json
{
  "request": { "topic": "...", "target_facets": [...], "response_format": null, "num_options": null, "book_context_mode": "...", "prompt_version": "v2", ... },
  "models": { "generator": "gemini/...", "judge": "gemini/..." },
  "facet_selection_reasoning": "...",
  "item": { /* GeneratedItem */ },
  "judge_report": { /* JudgeReport */ },
  "eval_scores": { /* EvalScores — null if --skip-eval */ },
  "timing": { "generator_s": 2.4, "judge_s": 1.9, "eval_s": 3.1 },
  "created_at": "2026-05-14T..."
}
```

One artifact per item. Easy to glob, easy to feed into the dashboards.

## 9. Dashboards

### 9.1 Item explorer (`web/index.html`)
- Load artifact JSONs or folders
- Item list with inline eval badges (correct/wrong, N{score}, L{score})
- Detail view with Generated Item, Judge Report, and Evaluation tabs
- Aggregate view with summary stats, facet coverage, and per-item breakdown

### 9.2 Evaluation comparison (`web/compare.html`)
- Load multiple eval result JSONs or artifact folders
- Side-by-side comparison table: judge scores, item-level rubrics, corpus-level rubrics
- Per-item detail table across datasets
- Facet coverage heatmap

## 10. Out of scope (explicit, for future)

- Refinement loop where judge feedback is fed back to generator.
- Human verification UI.
- RAG-based book context (interface reserved, raises `NotImplementedError`).
- Student simulation for distractor plausibility testing.
- Multi-topic batches.
