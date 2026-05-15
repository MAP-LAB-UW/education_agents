# Evaluation Rubrics

This document describes the rubrics used to evaluate generated diagnostic assessment items, both at the individual item level and across a corpus of items.

## Item-Level Rubrics

### 1. Correctness

**What it measures:** Whether the item has a defensible correct answer and no ambiguous distractors.

**Method:** An LLM (blind to the answer key) is given the stem and options and asked to solve the problem independently. It also flags any distractor that could be defensibly correct.

**Output:**
- `is_correct` (bool) — whether the LLM's answer matches the keyed answer
- `flagged_distractors` (list) — option IDs the LLM considers defensibly correct beyond the keyed answer
- `reasoning` — the LLM's solution reasoning

**Interpretation:** A failing item either has an incorrect answer key or an ambiguous stem. Flagged distractors indicate options that may confuse knowledgeable students due to genuine ambiguity rather than a misconception.

**Implementation:** `src/education_agents/evaluation/correctness.py`

---

### 2. Naturalness

**What it measures:** Readability and clarity of the item from an assessment design perspective.

**Method:** An LLM rates the stem and options separately on a 1-5 scale using a detailed rubric.

**Stem scoring (1-5):**
| Score | Description |
|-------|-------------|
| 5 | Clear, concise, real-world scenario. Easy to read on first pass. |
| 4 | Clear scenario with minor wordiness or slightly awkward phrasing. |
| 3 | Understandable but noticeably wordy, complex structure, or contrived scenario. |
| 2 | Confusing structure, multiple re-reads needed, or overly artificial scenario. |
| 1 | Incoherent, contradictory, or unclear question. |

**Options scoring (1-5):**
| Score | Description |
|-------|-------------|
| 5 | All options concise, parallel in structure, easy to compare. |
| 4 | Mostly clear with minor inconsistencies in length or phrasing. |
| 3 | Some options wordy, overly technical, or structurally inconsistent. |
| 2 | Multiple options confusing, excessively long, or hard to compare. |
| 1 | Options incoherent or contradictory in ways unrelated to diagnostic intent. |

**Output:**
- `stem_score` (1-5)
- `options_score` (1-5)
- `overall_score` — rounded average of stem and options scores

**Implementation:** `src/education_agents/evaluation/naturalness.py`

---

### 3. Facet Latency

**What it measures:** How well facets are embedded as latent concepts in the options, rather than appearing as surface-level paraphrases of facet definitions.

**Why it matters:** High-quality diagnostic items weave misconceptions and learning goals into realistic scenarios. If an option simply restates a facet definition, the item tests reading comprehension rather than conceptual understanding.

**Method:** For each option, compute the cosine similarity between the option text embedding and the concatenated text of its tagged facet definitions, using the `Qwen/Qwen3-Embedding-0.6B` model. Lower similarity means the facet is more deeply embedded (more latent).

**Scoring buckets:**

| Similarity | Bucket | Score | Interpretation |
|------------|--------|-------|----------------|
| < 0.55 | highly_latent | 4 | Facet is deeply embedded in a concrete scenario |
| 0.55 - 0.70 | latent | 3 | Facet is present but not a direct paraphrase |
| 0.70 - 0.80 | surface | 2 | Option noticeably echoes facet language |
| >= 0.80 | paraphrase | 1 | Option is a near-direct restatement of the facet definition |

**Threshold derivation:** Buckets were empirically calibrated by comparing similarity distributions across expert-authored items (mean ~0.576) and V1 generated items (mean ~0.716). Expert items cluster in the highly_latent/latent range while V1 items skew toward surface/paraphrase.

**Output:**
- `mean_similarity` — average cosine similarity across all options
- `score` (1-4) — bucket score based on mean similarity
- `bucket` — categorical label
- `option_details` — per-option similarity, score, bucket, and facet tags

**Implementation:** `src/education_agents/evaluation/facet_latency.py`

---

## Corpus-Level Rubrics

These metrics evaluate a set of items as a whole, measuring how well a generated corpus covers the target domain and avoids repetition.

### 1. Facet Coverage

**What it measures:** How uniformly items cover all facets in the facet map.

**Method:** Count how many times each facet appears across all item options, then compute normalized entropy over the distribution.

**Output:**
- `facet_counts` — per-facet occurrence counts
- `covered_facets` / `total_facets_in_map` — how many facets appear at least once
- `uniformity` (0-1) — normalized Shannon entropy; 1.0 means perfectly uniform coverage, 0.0 means all items target the same facet

**Implementation:** `src/education_agents/evaluation/corpus_metrics.py` (`evaluate_facet_coverage`)

---

### 2. Facet Combination Diversity

**What it measures:** Whether items target distinct combinations of facets or repeat similar groupings.

**Method:** For each item, collect the set of target facets. Compute the mean pairwise Jaccard distance across all item pairs.

**Output:**
- `unique_combinations` / `total_items` — count of distinct facet sets
- `combination_ratio` — fraction of items with unique facet combinations (1.0 = all unique)
- `mean_pairwise_jaccard_distance` (0-1) — average Jaccard distance; higher means more diverse combinations

**Interpretation:** Jaccard distance = 1 - |A intersection B| / |A union B|. A value of 0.87 means item pairs share only ~13% of their facets on average.

**Implementation:** `src/education_agents/evaluation/corpus_metrics.py` (`evaluate_facet_combination_diversity`)

---

### 3. Problem Diversity: Structural

**What it measures:** Variety in response formats and question styles across the corpus.

**Method:**
- **Format distribution:** Count items by response format (single_select, multi_select, true_false_per_option) and compute normalized entropy.
- **Style distribution:** An LLM classifies each item into one of five style categories, then normalized entropy is computed over the distribution.

**Style categories:**
| Style | Description |
|-------|-------------|
| numerical | Options are specific numbers, calculations, or formulas |
| interpretation | Options are competing interpretations of a statistical result |
| prediction | The question asks what happens when something changes |
| action | Options are concrete actions a researcher should take |
| conceptual | Options are conceptual statements about properties or definitions |

**Output:**
- `format_distribution` / `format_entropy` — response format variety
- `style_distribution` / `style_entropy` — question style variety
- Higher entropy = more diverse

**Implementation:** `src/education_agents/evaluation/corpus_metrics.py` (`evaluate_structural_diversity`)

---

### 4. Problem Diversity: Semantic

**What it measures:** Whether item stems are semantically distinct or repetitive.

**Method:** Encode all stems using `Qwen/Qwen3-Embedding-0.6B`, then compute pairwise cosine similarity. Report the mean and maximum similarity, plus the most similar pair.

**Output:**
- `mean_pairwise_similarity` — average semantic similarity across all stem pairs; lower is more diverse
- `max_pairwise_similarity` — the highest similarity between any two stems; flags near-duplicate items
- `most_similar_pair` — identifiers of the two most similar items

**Interpretation:** A mean similarity above ~0.85 suggests items are too similar in topic/framing. The most-similar-pair helps identify specific items that may need differentiation.

**Implementation:** `src/education_agents/evaluation/corpus_metrics.py` (`evaluate_semantic_diversity`)

---

## Running Evaluations

```bash
# Item + corpus eval on generated items
conda run -n education-env python scripts/run_evaluation.py outputs/<run_dir>

# Expert examples — full eval
conda run -n education-env python scripts/eval_experts.py --out outputs/eval_experts.json

# Expert examples — corpus metrics only (skip item-level)
conda run -n education-env python scripts/eval_experts.py --skip-item

# Expert examples — facet latency only (no LLM calls)
conda run -n education-env python scripts/eval_experts.py --skip-llm

# Skip corpus metrics (item-level only)
conda run -n education-env python scripts/run_evaluation.py outputs/<run_dir> --skip-corpus

# Save results to file
conda run -n education-env python scripts/run_evaluation.py outputs/<run_dir> --out outputs/eval_results.json
```
