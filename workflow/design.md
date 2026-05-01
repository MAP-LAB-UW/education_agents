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
              │ Persisted run artifact  │  (item + report + metadata)
              └─────────────────────────┘
```

No refinement loop. No human-in-the-loop yet — but artifacts are stored in a shape that a future review UI can consume.

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
- `target_facets`: list of facet IDs the item should diagnose (e.g., `["A4", "B7", "B9"]`)
- `response_format`: `single_select` | `multi_select` | `true_false_per_option`
- `num_options`: typically 4–6
- `book_context_mode`: `none` | `full_tex` | `rag` (rag = `NotImplementedError` for now)
- `n_items`: how many to generate (each is an independent LLM call)

### 2.3 Book context modes

| mode | implementation |
|---|---|
| `none` | no book content in prompt |
| `full_tex` | inline the entire `docs/edpsy490_ch_5.tex` (511 lines, fits comfortably) into the system prompt under a `<book_chapter>` tag |
| `rag` | stub — raises `NotImplementedError("RAG mode not implemented yet")` |

The mode is recorded in the run artifact so we can compare quality across modes later.

## 3. Item Generation Agent

### 3.1 Inputs to the prompt
- Facet map (full list of A and B facets, with text).
- Target facet IDs (the agent must "cover" these — see §3.3 for what coverage means).
- Response format + number of options.
- Optional book chapter (per context mode).
- Few-shot examples from the facet map (`examples` field).

### 3.2 Output schema (structured JSON)

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

### 3.3 Coverage rule (what the prompt enforces)
- Each goal facet (A) in `target_facets` must be tagged on at least one **correct** option.
- Each problematic facet (B) in `target_facets` must be tagged on at least one **incorrect** option (a distractor).
- Every option must have ≥1 facet tag.
- An option may carry multiple tags (e.g., a distractor that conflates A3 with B9, as in Example 2).

### 3.4 Prompt structure (`prompts/generator.md`)
1. Role: assessment item writer for a stats course.
2. Task: write one MC item that diagnoses a specified set of facets.
3. Facet map (rendered from JSON).
4. Coverage rule (§3.3).
5. Few-shot examples (rendered from facet map).
6. Optional book chapter.
7. The specific request (target facets, format, num_options).
8. Output schema reminder.

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

## 5. LLM interface (`src/education_agents/llm.py`)

A thin wrapper over `litellm.completion`:

```python
def complete(messages, model=None, **kwargs) -> str: ...
def structured_complete(messages, schema: type[BaseModel], model=None, **kwargs) -> BaseModel: ...
```

- `model` defaults to `os.getenv("EDU_AGENTS_MODEL", "gemini/gemini-2.5-pro")`.
- `structured_complete` uses `response_format={"type": "json_schema", "json_schema": ...}` via litellm, with a fallback path that does JSON-mode + pydantic validation for providers without strict-schema support.
- `.env` loaded via `python-dotenv`.

This is the only file other modules touch when calling LLMs — swapping providers = changing one env var.

## 6. Module layout

```
src/education_agents/
├── __init__.py
├── llm.py              # litellm wrapper
├── schemas.py          # Facet, FacetMap, Option, GeneratedItem, JudgeReport, OptionAssessment
├── facets.py           # load_facet_map(topic) -> FacetMap; render_facet_map_for_prompt()
├── book_context.py     # load_book_context(mode, path) -> str | None; raises for "rag"
├── generator.py        # generate_item(request, llm) -> GeneratedItem
├── judge.py            # judge_item(item, facet_map, llm) -> JudgeReport
├── pipeline.py         # run(request) -> RunArtifact (calls generator then judge, persists)
└── prompts/
    ├── generator.md
    └── judge.md
```

```
scripts/
├── run_pipeline.py     # CLI: --topic, --facets, --format, --book-mode, --n-items, --out
└── ...                 # (existing extract_figures.py untouched)
```

## 7. Run artifact (`outputs/<timestamp>_<short_hash>.json`)

```json
{
  "request": { "topic": "...", "target_facets": [...], "book_context_mode": "...", ... },
  "models": { "generator": "gemini/...", "judge": "gemini/..." },
  "item": { /* GeneratedItem */ },
  "judge_report": { /* JudgeReport */ },
  "timing": { "generator_s": 2.4, "judge_s": 1.9 },
  "created_at": "2026-04-30T..."
}
```

One artifact per item. Easy to glob, easy to feed into a future review UI.

## 8. Out of scope (explicit, for future)

- Refinement loop where judge feedback is fed back to generator.
- Human verification UI.
- RAG-based book context (interface reserved, raises `NotImplementedError`).
- Cross-item quality metrics (item difficulty estimation, distractor plausibility, etc.).
- Multi-topic batches.

---

## Open design questions

1. **Target-facet selection:** does the user specify `target_facets` per call, or do we add a sampling helper that proposes combinations (e.g., "1 goal + 2 misconceptions")? Leaning toward user-specified for now, with a sampler later.
2. **`is_correct` for `true_false_per_option`:** modeling as "is the keyed verdict True?" — i.e., `is_correct=True` means the statement *is* true. Confirm or use a separate `keyed_verdict: bool` field.
3. **Judge sees target facets or not?** Proposing **not**, so the judge re-derives tags blind. Makes the agreement signal more meaningful.
4. **Few-shot examples:** include all examples from facet map, or sample? With only 2 currently, include all.
