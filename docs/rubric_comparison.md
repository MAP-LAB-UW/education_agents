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
| Third Pass + EDPSY | V2 (latent-facet) | Gemini 3 Flash Preview | Dynamic | Gemini 3.1 Pro Preview |
| Third Pass (Sonnet 4.6) | V2 (latent-facet) | Claude Sonnet 4.6 | Dynamic | Gemini 3.1 Pro Preview |
| V3 + Figures (Flash) | V3 (figure-encouraged) | Gemini 3 Flash Preview | Dynamic | Gemini 3.1 Pro Preview |
| V3 + Figures (Sonnet 4.6) | V3 (figure-encouraged) | Claude Sonnet 4.6 | Dynamic | Gemini 3.1 Pro Preview |

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
| Third Pass + EDPSY | 10 | 10 | 100% |
| Third Pass (Sonnet 4.6) | 7 | 10 | 70% |
| V3 + Figures (Flash) | 10 | 10 | 100% |
| V3 + Figures (Sonnet 4.6) | 7 | 10 | 70% |

**Flagged distractors** (options that could be defensibly correct beyond the keyed answer):

- **Expert:** 2 flagged across 8 items
- **First Pass:** 2 flagged across 10 items
- **Second Pass:** 3 flagged across 10 items
- **Third Pass:** 4 flagged across 10 items
- **Third Pass (Flash Lite):** 2 flagged across 10 items
- **Third Pass (Pro):** 1 flagged across 10 items
- **Third Pass + EDPSY:** 4 flagged across 10 items
- **Third Pass (Sonnet 4.6):** 5 flagged across 10 items
- **V3 + Figures (Flash):** 4 flagged across 10 items
- **V3 + Figures (Sonnet 4.6):** 8 flagged across 10 items

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
| Third Pass + EDPSY | 4.80 | 4.10 | 4.30 |
| Third Pass (Sonnet 4.6) | 4.70 | 4.50 | 4.40 |
| V3 + Figures (Flash) | 5.00 | 4.30 | 4.40 |
| V3 + Figures (Sonnet 4.6) | 4.90 | 4.50 | 4.50 |

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
| Third Pass + EDPSY | 0.6380 | 2.80 | Latent |
| Third Pass (Sonnet 4.6) | 0.6302 | 3.00 | Latent |
| V3 + Figures (Flash) | 0.6159 | 3.00 | Latent |
| V3 + Figures (Sonnet 4.6) | 0.5567 | 3.50 | Highly Latent |

**Bucket distribution** (across all options in all items):

| Run | Highly Latent | Latent | Surface | Paraphrase |
|-----|--------------|--------|---------|------------|
| **Expert** | 14 (44%) | 14 (44%) | 4 (12%) | 0 (0%) |
| First Pass | 2 (5%) | 16 (40%) | 14 (35%) | 8 (20%) |
| Second Pass | 7 (18%) | 23 (57%) | 6 (15%) | 4 (10%) |
| Third Pass | 12 (31%) | 14 (36%) | 10 (26%) | 3 (8%) |
| Third Pass (Flash Lite) | 1 (3%) | 13 (33%) | 14 (36%) | 11 (28%) |
| Third Pass (Pro) | 3 (7%) | 17 (41%) | 12 (29%) | 9 (22%) |
| Third Pass + EDPSY | 9 (21%) | 18 (43%) | 13 (31%) | 1 (2%) |
| Third Pass (Sonnet 4.6) | 13 (30%) | 14 (32%) | 14 (32%) | 2 (4%) |
| V3 + Figures (Flash) | 12 (29%) | 20 (48%) | 8 (19%) | 1 (2%) |
| V3 + Figures (Sonnet 4.6) | 24 (50%) | 22 (45%) | 2 (4%) | 0 (0%) |

### Figure Necessity

Measures whether figures included in items are essential for answering the question. The item is presented to an LLM without its figures 5 times at temperature=1.0. If the model answers correctly in fewer than 50% of trials, the figure is classified as essential (1); otherwise decorative (0). Only applicable to items with figures.

| Run | Items with Figures | Essential | Decorative |
|-----|--------------------|-----------|------------|
| **Expert** | 1/8 | 1 | 0 |
| First Pass | 0/10 | — | — |
| Second Pass | 0/10 | — | — |
| Third Pass | 0/10 | — | — |
| Third Pass (Flash Lite) | 0/10 | — | — |
| Third Pass (Pro) | 0/10 | — | — |
| Third Pass + EDPSY | 0/10 | — | — |
| Third Pass (Sonnet 4.6) | 0/10 | — | — |
| V3 + Figures (Flash) | 9/10 | 0 | 9 |
| V3 + Figures (Sonnet 4.6) | 1/10 | 0 | 1 |

### Similarity with Experts

Measures how semantically similar each generated item's stem is to the expert-authored reference items. For expert examples, leave-one-out comparison is used. Higher mean similarity indicates the generated items cover similar territory to expert items; very high max values may indicate near-reproduction.

| Run | Avg Mean Sim | Avg Max Sim | Overall Max Sim |
|-----|-------------|-------------|-----------------|
| **Expert** | 0.513 | 0.658 | 0.703 |
| First Pass | 0.575 | 0.727 | 0.858 |
| Second Pass | 0.551 | 0.702 | 0.846 |
| Third Pass | 0.555 | 0.708 | 0.824 |
| Third Pass (Flash Lite) | 0.536 | 0.726 | 0.792 |
| Third Pass (Pro) | 0.537 | 0.714 | 0.840 |
| Third Pass + EDPSY | 0.540 | 0.689 | 0.817 |
| Third Pass (Sonnet 4.6) | 0.549 | 0.729 | 0.787 |
| V3 + Figures (Flash) | 0.537 | 0.692 | 0.798 |
| V3 + Figures (Sonnet 4.6) | 0.543 | 0.714 | 0.799 |

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
| Third Pass + EDPSY | 17 | 17 | 0.987 |
| Third Pass (Sonnet 4.6) | 17 | 17 | 0.963 |
| V3 + Figures (Flash) | 17 | 17 | 0.974 |
| V3 + Figures (Sonnet 4.6) | 17 | 17 | 0.974 |

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
| Third Pass + EDPSY | 0.971 | 0.880 |
| Third Pass (Sonnet 4.6) | 1.000 | 0.935 |
| V3 + Figures (Flash) | 0.722 | 0.948 |
| V3 + Figures (Sonnet 4.6) | 1.000 | 0.881 |

**Format distributions:**

| Run | Single Select | Multi Select | True/False Per Option |
|-----|--------------|-------------|----------------------|
| **Expert** | 7 | 0 | 1 |
| First Pass | 10 | 0 | 0 |
| Second Pass | 10 | 0 | 0 |
| Third Pass | 8 | 0 | 2 |
| Third Pass (Flash Lite) | 10 | 0 | 0 |
| Third Pass (Pro) | 7 | 0 | 3 |
| Third Pass + EDPSY | 6 | 0 | 4 |
| Third Pass (Sonnet 4.6) | 5 | 0 | 5 |
| V3 + Figures (Flash) | 8 | 0 | 2 |
| V3 + Figures (Sonnet 4.6) | 5 | 0 | 5 |

**Style distributions:**

| Run | Action | Prediction | Interpretation | Conceptual | Numerical |
|-----|--------|-----------|----------------|-----------|-----------|
| **Expert** | 1 | 1 | 3 | 2 | 1 |
| First Pass | 1 | 3 | 2 | 4 | 0 |
| Second Pass | 1 | 3 | 2 | 4 | 0 |
| Third Pass | 1 | 0 | 3 | 6 | 0 |
| Third Pass (Flash Lite) | 0 | 6 | 2 | 2 | 0 |
| Third Pass (Pro) | 0 | 6 | 1 | 3 | 0 |
| Third Pass + EDPSY | 1 | 2 | 2 | 5 | 0 |
| Third Pass (Sonnet 4.6) | 1 | 3 | 2 | 3 | 1 |
| V3 + Figures (Flash) | 1 | 3 | 3 | 3 | 0 |
| V3 + Figures (Sonnet 4.6) | 1 | 1 | 3 | 4 | 1 |

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
| Third Pass + EDPSY | 0.5874 | 0.8302 |
| Third Pass (Sonnet 4.6) | 0.5932 | 0.7861 |
| V3 + Figures (Flash) | 0.5880 | 0.8136 |
| V3 + Figures (Sonnet 4.6) | 0.5953 | 0.9249 |

### Figure Fraction

Proportion of items in the corpus that include generated figures.

| Run | Figure Fraction |
|-----|-----------------|
| **Expert** | 12.5% (1/8) |
| First Pass | 0% |
| Second Pass | 0% |
| Third Pass | 0% |
| Third Pass (Flash Lite) | 0% |
| Third Pass (Pro) | 0% |
| Third Pass + EDPSY | 0% |
| Third Pass (Sonnet 4.6) | 0% |
| V3 + Figures (Flash) | 90% (9/10) |
| V3 + Figures (Sonnet 4.6) | 10% (1/10) |

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

### Textbook Context (Third Pass + EDPSY)

- **Adding EDPSY book context did not meaningfully change item quality** relative to the base Third Pass: facet latency (0.638 vs 0.636), naturalness (4.30 vs 4.30), and correctness (10/10 vs 10/10) are nearly identical.
- **Format and style diversity improved slightly** (format entropy 0.971 vs 0.722; style entropy 0.880 vs 0.817), with more true/false items (4 vs 2).
- **Semantic diversity is the best among generated runs** (mean 0.587, max 0.830), approaching the expert baseline more closely than other configurations.

### Claude Sonnet 4.6 as Generator (Third Pass Sonnet 4.6)

- **Facet latency is strong** (0.630, latent range) — comparable to Flash base and better than Flash Lite and Pro.
- **Correctness dropped to 70%** (7/10). Three items had evaluator disagreements, mostly involving answer key format mismatches or mathematically ambiguous distractors. This run also had the most flagged distractors (5) among V2 runs.
- **Naturalness is high** (4.40 overall), with the best options score among V2 runs (4.50).
- **Structural diversity is the highest of any run** (format entropy 1.000, style entropy 0.935), with a perfect 5/5 split between single-select and true/false formats and representation across all 5 style categories including numerical.
- **Semantic diversity is the best across all generated runs** (max similarity 0.786 — lowest max among all generated runs, closest to experts at 0.703).

### V3 Prompt with Figures

The V3 prompt encourages models to generate figures and use LaTeX notation.

- **V3 + Figures (Flash)** achieves the best facet latency among Gemini runs (0.616, latent range), surpassing V2 runs. 90% of items include generated figures. Naturalness is strong (4.40 overall) with perfect stem scores (5.00). However, the judge frequently flagged that figures give away answers or are pedagogically unnecessary — the figure_necessity score was 0 for all 9 evaluated items (all decorative).
- **V3 + Figures (Sonnet 4.6)** achieves the best facet latency of any run (0.557), entering the highly latent range and matching experts (0.573). 50% of options land in the highly_latent bucket (matching the expert rate of 44%) with 0% paraphrases. Only 10% of items include figures (Sonnet chose not to generate them for most items). The single figure was also classified as decorative. Correctness is lower at 70%, with 8 flagged distractors — the highest of any run, suggesting the model creates more mathematically ambiguous options. Max pairwise similarity (0.925) indicates some near-duplicate stems.
- **Overall:** The V3 prompt's LaTeX notation and figure encouragement appear to correlate with improved facet latency, possibly because the mathematical framing forces models to embed concepts in computational scenarios rather than paraphrasing definitions. The figure generation itself adds limited diagnostic value — all generated figures were classified as decorative (answerable without the figure in >=50% of trials). In contrast, the single expert figure was classified as essential (0/5 correct without it).

### Similarity with Expert Items

- **All generated runs have higher mean similarity to experts (0.536–0.575) than experts have among themselves (0.513),** indicating generated items land in similar conceptual territory without being copies.
- **First Pass has the highest similarity** (avg mean 0.575, overall max 0.858), suggesting V1 items most closely mirror expert phrasing — consistent with V1's surface-level facet embedding.
- **Later passes and V3 runs converge to a similar range (0.537–0.555),** suggesting the V2/V3 prompts produce items that are appropriately similar to expert items without over-mimicking them.
- **Third Pass + EDPSY has the lowest avg max similarity (0.689)** among all generated runs, suggesting textbook context helps produce items that are more distinct from the expert set.
- **Third Pass (Sonnet 4.6) has the lowest overall max (0.787)** among generated runs, further supporting Sonnet's tendency toward more structurally diverse items.
