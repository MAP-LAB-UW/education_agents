# Rubric Comparison Across Passes

This document compares evaluation rubric scores across different pipeline configurations.
All runs use the **confidence intervals** topic. Generated runs have 10 items each; the expert baseline has 8 human-authored items.

## Run Configurations

| Run | Prompt | Generator Model | Format | Judge Model |
|-----|--------|----------------|--------|-------------|
| **Expert (baseline)** | N/A (human-authored) | N/A | Mixed (7 single-select, 1 T/F) | Gemini 3.1 Pro Preview |
| First Pass | V1 | Gemini 3 Flash Preview | Single-select (fixed) | Gemini 3.1 Pro Preview |
| Second Pass | V2 (latent-facet) | Gemini 3 Flash Preview | Single-select (fixed) | Gemini 3.1 Pro Preview |
| Third Pass | V2 (latent-facet) | Gemini 3 Flash Preview | Dynamic | Gemini 3.1 Pro Preview |
| Third Pass (Flash Lite) | V2 (latent-facet) | Gemini 3.1 Flash Lite | Dynamic | Gemini 3.1 Pro Preview |
| Third Pass (Pro) | V2 (latent-facet) | Gemini 3.1 Pro Preview | Dynamic | Gemini 3.1 Pro Preview |

---

## Item-Level Rubrics

### Correctness

Measures whether the item has a defensible correct answer (LLM blind-solves the item).

| Run | Correct | Total | Rate |
|-----|---------|-------|------|
| **Expert** | 6 | 8 | 75% |
| First Pass | 10 | 10 | 100% |
| Second Pass | 8 | 10 | 80% |
| Third Pass | 10 | 10 | 100% |
| Third Pass (Flash Lite) | 10 | 10 | 100% |
| Third Pass (Pro) | 10 | 10 | 100% |

**Flagged distractors** (options that could be defensibly correct beyond the keyed answer):

- **Expert:** 2 flagged across 8 items
- **First Pass:** 2 flagged across 10 items
- **Second Pass:** 3 flagged across 10 items
- **Third Pass:** 4 flagged across 10 items
- **Third Pass (Flash Lite):** 2 flagged across 10 items
- **Third Pass (Pro):** 1 flagged across 10 items

### Naturalness

LLM-as-judge rates stem clarity (1–5) and option quality (1–5).

| Run | Stem (avg) | Options (avg) | Overall (avg) |
|-----|-----------|--------------|--------------|
| **Expert** | 4.12 | 4.50 | 4.12 |
| First Pass | 4.90 | 3.60 | 4.10 |
| Second Pass | 4.90 | 4.00 | 4.30 |
| Third Pass | 4.80 | 4.10 | 4.30 |
| Third Pass (Flash Lite) | 5.00 | 4.80 | 4.80 |
| Third Pass (Pro) | 5.00 | 4.70 | 4.80 |

### Facet Latency

Measures how deeply facets are embedded vs. being surface paraphrases of facet definitions.
Higher score = more latent (better). Based on embedding cosine similarity to facet definitions.

| Similarity | Bucket | Score | Interpretation |
|------------|--------|-------|----------------|
| < 0.55 | highly_latent | 4 | Facet deeply embedded in scenario |
| 0.55 – 0.70 | latent | 3 | Present but not a direct paraphrase |
| 0.70 – 0.80 | surface | 2 | Noticeably echoes facet language |
| >= 0.80 | paraphrase | 1 | Near-direct restatement of facet definition |

**Summary scores:**

| Run | Mean Similarity | Mean Score | Interpretation |
|-----|----------------|------------|----------------|
| **Expert** | 0.5726 | 3.50 | Highly Latent |
| First Pass | 0.7156 | 2.40 | Surface |
| Second Pass | 0.6361 | 3.00 | Latent |
| Third Pass | 0.6356 | 3.00 | Latent |
| Third Pass (Flash Lite) | 0.7264 | 2.20 | Surface |
| Third Pass (Pro) | 0.6987 | 2.50 | Latent |

**Bucket distribution** (across all options in all items):

| Run | Highly Latent | Latent | Surface | Paraphrase |
|-----|--------------|--------|---------|------------|
| **Expert** | 14 (44%) | 14 (44%) | 4 (12%) | 0 (0%) |
| First Pass | 2 (5%) | 16 (40%) | 14 (35%) | 8 (20%) |
| Second Pass | 7 (18%) | 23 (57%) | 6 (15%) | 4 (10%) |
| Third Pass | 12 (31%) | 14 (36%) | 10 (26%) | 3 (8%) |
| Third Pass (Flash Lite) | 1 (3%) | 13 (33%) | 14 (36%) | 11 (28%) |
| Third Pass (Pro) | 3 (7%) | 17 (41%) | 12 (29%) | 9 (22%) |

---

## Corpus-Level Rubrics

### Facet Coverage

How uniformly items cover all 17 facets (7 goals + 10 misconceptions). Uniformity is normalized Shannon entropy (1.0 = perfectly uniform).

| Run | Covered Facets | Total Facets | Uniformity |
|-----|---------------|-------------|-----------|
| **Expert** | 17 | 17 | 0.948 |
| First Pass | 17 | 17 | 0.967 |
| Second Pass | 17 | 17 | 0.978 |
| Third Pass | 17 | 17 | 0.993 |
| Third Pass (Flash Lite) | 17 | 17 | 0.976 |
| Third Pass (Pro) | 17 | 17 | 0.930 |

### Structural Diversity

Variety in response formats and question styles (higher entropy = more diverse).

| Run | Format Entropy | Style Entropy |
|-----|---------------|---------------|
| **Expert** | 0.544 | 0.928 |
| First Pass | 0.000 | 0.923 |
| Second Pass | 0.000 | 0.923 |
| Third Pass | 0.722 | 0.817 |
| Third Pass (Flash Lite) | 0.000 | 0.865 |
| Third Pass (Pro) | 0.881 | 0.817 |

**Format distributions:**

| Run | Single Select | Multi Select | True/False Per Option |
|-----|--------------|-------------|----------------------|
| **Expert** | 7 | 0 | 1 |
| First Pass | 10 | 0 | 0 |
| Second Pass | 10 | 0 | 0 |
| Third Pass | 8 | 0 | 2 |
| Third Pass (Flash Lite) | 10 | 0 | 0 |
| Third Pass (Pro) | 7 | 0 | 3 |

**Style distributions:**

| Run | Action | Prediction | Interpretation | Conceptual | Numerical |
|-----|--------|-----------|----------------|-----------|-----------|
| **Expert** | 1 | 1 | 3 | 2 | 1 |
| First Pass | 1 | 3 | 2 | 4 | 0 |
| Second Pass | 1 | 3 | 2 | 4 | 0 |
| Third Pass | 1 | 0 | 3 | 6 | 0 |
| Third Pass (Flash Lite) | 0 | 6 | 2 | 2 | 0 |
| Third Pass (Pro) | 0 | 6 | 1 | 3 | 0 |

### Semantic Diversity

Pairwise cosine similarity of stem embeddings. Lower = more diverse. Max similarity flags near-duplicate items.

| Run | Mean Similarity | Max Similarity |
|-----|----------------|----------------|
| **Expert** | 0.5130 | 0.7030 |
| First Pass | 0.6542 | 0.8547 |
| Second Pass | 0.6069 | 0.8426 |
| Third Pass | 0.6098 | 0.8412 |
| Third Pass (Flash Lite) | 0.6035 | 0.9093 |
| Third Pass (Pro) | 0.5976 | 0.8802 |

---

## Key Takeaways

### Expert Baseline

The 8 human-authored expert items serve as the quality reference point:
- **Facet latency is the standout metric:** Expert items have a mean similarity of 0.573 (highly latent range), with 44% of options in the highly_latent bucket and 0% paraphrases. This is the gold standard the V2 prompt was designed to approach.
- **Semantic diversity is strongest among experts:** Mean pairwise stem similarity of 0.513 and max of 0.703 — substantially more varied than any generated run.
- **Correctness is lower than expected (75%):** Two items were flagged due to the LLM evaluator disagreeing with the keyed answer or finding defensibly correct distractors. This reflects the difficulty of the evaluation task, not necessarily item quality.
- **Style diversity is the most balanced** across all runs, with representation across all 5 style categories including numerical (unique to experts).

### V1 → V2 Prompt Improvement (First Pass → Second Pass)

- **Facet latency improved significantly:** Mean similarity dropped from 0.716 to 0.636, moving from the surface/paraphrase range into the latent range. This closes much of the gap to the expert baseline (0.573). The V2 prompt's latent-facet design principle is the primary driver.
- **Naturalness improved slightly:** Options score increased from 3.60 to 4.00, reflecting better parallel structure.
- **Correctness decreased slightly:** 8/10 vs 10/10. Two items had answer key mismatches where the evaluator selected a different format for the correct answer ID (e.g., "Option A" vs "A").
- **Semantic diversity improved:** Mean pairwise similarity dropped from 0.654 to 0.607, though still above the expert level (0.513).

### V2 Fixed Format → Dynamic Format (Second Pass → Third Pass)

- **Format diversity emerged:** Third pass includes true/false-per-option items (format entropy 0.72 vs 0.00), approaching the expert baseline (0.54).
- **Correctness restored to 10/10.**
- **Facet latency held steady** at the improved V2 level (~0.636).
- **Facet coverage uniformity** reached near-perfect 0.993 (exceeding experts at 0.948).

### Model Comparison (Third Pass across generators)

- **Flash Lite** scores highest on naturalness (4.80) but has the worst facet latency (0.726, surface range) — further from experts than even the V1 first pass. It produces fluent but formulaic items that closely paraphrase facet definitions.
- **Pro** also scores high on naturalness (4.80) with moderately better facet latency (0.699) than Flash Lite, and includes format diversity (3 true/false items).
- **Flash (base)** has the best facet latency (0.636) among generated runs — closest to the expert baseline — with good but not perfect naturalness (4.30).
