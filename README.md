# Diagnostic Assessment Copilot

An LLM-powered pipeline for generating high-quality multiple-choice diagnostic assessment items aligned to learning goals and misconception facets. 
## What This Does

The pipeline takes a **facet map** (learning goals + common misconceptions) and generates diagnostic MC items where:
- Each correct option maps to one or more learning goals (A-facets)
- Each distractor targets a specific student misconception (B-facets)
- A separate judge LLM independently verifies facet-option alignment
- Automated rubrics evaluate correctness, naturalness, and facet embedding depth

## Quick Links for Reviewers

If you just want to look at the generated items and evaluation results:

| Document | Description |
|----------|-------------|
| [First Pass Items](docs/generated_items_first_pass_no_books.md) | 10 items generated with V1 prompt (single-select only) |
| [Second Pass Items](docs/generated_items_second_pass_no_books.md) | 10 items generated with V2 prompt — latent-facet design (single-select only) |
| [Third Pass Items](docs/generated_items_third_pass_no_books.md) | 10 items generated with V2 prompt — dynamic format (model chooses format) |
| [Third Pass + EDPSY Book](docs/generated_items_third_pass_with_edpsy.md) | 10 items generated with V2 prompt + textbook context (Gemini 3 Flash) |
| [Third Pass — Sonnet 4.6](docs/generated_items_third_pass_sonnet-4-6.md) | 10 items generated with V2 prompt — dynamic format (Claude Sonnet 4.6) |
| [V3 + Figures — Gemini Flash](docs/generated_items_gemini_flash_v3_with_figures.md) | 10 items with V3 prompt — figures and LaTeX notation (Gemini 3 Flash) |
| [V3 + Figures — Sonnet 4.6](docs/generated_items_sonnet_4_6_v3_with_figures.md) | 10 items with V3 prompt — figures and LaTeX notation (Claude Sonnet 4.6) |
| [12 Items Selected For Expert Review](docs//expert_review_items.md) | 12 items generated selected from above configurations for review |
| [Rubric Comparison](docs/rubric_comparison.md) | Side-by-side comparison of evaluation metrics across all passes and generator models |
| [Rubric Definitions](docs/rubrics.md) | Detailed description of all evaluation rubrics |
| [Facet Map](workflow/facets.md) | The 17 facets (7 goals + 10 misconceptions) for confidence intervals |
| [System Design](workflow/design.md) | Full pipeline architecture, schemas, and module layout |

## Generate Items in the Dashboard

The quickest way to use this project is the web dashboard: configure a run in the
sidebar, click **Generate**, and review items as they stream in — each with a
judge report, optional evaluation rubrics, and a misconception **student
simulator**. Items can be exported as JSON, Markdown, or LaTeX so collaborators
can review them without touching code.

![Item Explorer Dashboard](docs/screenshots/item_explorer.png)

### Setup

```bash
git clone https://github.com/MAP-LAB-UW/education_agents.git
cd education_agents
conda create -n education-env python=3.11 && conda activate education-env
pip install -e .
```

### Open the dashboard

```bash
conda run -n education-env python scripts/serve_dashboard.py
```

This serves the dashboard and its generation backend and opens
<http://localhost:8000/web/index.html> automatically.

Generation calls Claude, so the backend needs an `ANTHROPIC_API_KEY`. The
dashboard **prompts for one on first launch** if it isn't set — paste a key into
the dialog (optionally saved to `.env` for next time), or click the **🔑** button
in the top-left to set or replace it anytime. You can also set it beforehand:

```bash
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

### On Windows

The whole stack is cross-platform, so Windows works the same way — just run the
commands from the **Anaconda Prompt** so `conda` is on your `PATH`:

1. **Install Miniconda.** Download the Windows installer from
   <https://www.anaconda.com/download/success> (Miniconda is the smaller option;
   full Anaconda works too) and run it. Accept the defaults — you do **not** need
   to add conda to your system `PATH`; the Anaconda Prompt handles that for you.
2. **Open the Anaconda Prompt.** Press the Start key, type *Anaconda Prompt*, and
   open it. It launches with conda ready to use. (Plain PowerShell or Command
   Prompt also work, but only after running `conda init` once.)
3. **Run the setup commands**, one per line — don't paste them as a single block,
   and skip the `&&` from the example above:

   ```bat
   git clone https://github.com/MAP-LAB-UW/education_agents.git
   cd education_agents
   conda create -n education-env python=3.11
   conda activate education-env
   pip install -e .
   ```
4. **Start the dashboard:**

   ```bat
   conda run -n education-env python scripts/serve_dashboard.py
   ```

   Your browser opens the dashboard automatically. On first launch it prompts for
   an `ANTHROPIC_API_KEY` — paste your key into that dialog (it saves to `.env`
   for next time). This is the most reliable way to set the key on Windows.

### Generate items

In the sidebar:

- **Target facets** — leave **Auto-select facets** on (default) to let the model choose diverse goal + misconception combinations per item, or pick specific facets.
- **Response format**, **Options**, and the **Items** slider (1–50).
- **Min. with figures** — force a fraction of the batch to include a load-bearing figure.
- **Generator / Judge** models — default **Opus** generator, **Sonnet** judge.
- **Skip judge** — skip the independent judge pass for speed (auto-enabled above 10 items).
- **Run evaluation rubrics** — optionally score correctness / naturalness / facet latency as items are generated.

Click **Generate**. Items stream into the Item Explorer and are saved to
`outputs/web_generated/`, so you can reload them later with **Load Folder**.

### Review, simulate, and export

- Each item has tabs for the **Generated Item**, **Judge Report**, **Evaluation**, and **Students** (the misconception simulator).
- **Evaluate** (top bar) runs the evaluation rubrics over the loaded items; corpus-level metrics appear in the **Aggregate** view.
- **Simulate Students** runs a control student plus one student per keyed misconception, and reports whether each distractor actually attracts the misconception it targets.
- **Download** the loaded items as **JSON**, **Markdown**, or **LaTeX** — Markdown and LaTeX are formatted for non-technical reviewers.

Server options: `--port` (default `8000`), `--host` (default `127.0.0.1`), `--no-open`.

## Facet Map

The current facet map covers 17 dimensions of student understanding about confidence intervals:

### Learning Goals (A-facets)
| ID | Description |
|----|-------------|
| A1 | As sample size increases, standard errors decrease and sampling distribution becomes more packed |
| A2 | As sample size increases, sampling distribution approaches normal (doesn't mirror population) |
| A3 | Mean of sampling distribution equals population mean |
| A4 | Confidence level = percentage of intervals capturing the parameter across replications |
| A5 | CI captures true population parameter, not sample statistics |
| A6 | CI width depends on confidence level; width increases as confidence level increases |
| A7 | CI width increases when standard error gets larger |

### Misconceptions (B-facets)
| ID | Description |
|----|-------------|
| B8 | Sampling distribution is the same as sample distribution |
| B9 | Sampling distribution mirrors population distribution |
| B10 | Larger samples make sampling distribution more spread out |
| B11 | Larger samples make sampling distribution closer to population distribution |
| B12 | Sampling distribution is always normal regardless of sample size |
| B13 | Mean of sampling distribution depends on sample size |
| B14 | Larger sample mean is always closer to population mean |
| B15 | CI is a probability statement about a specific interval |
| B16 | CI estimates sample statistics instead of population parameters |
| B17 | Higher confidence = more precise (shorter) interval |

## Running the Pipeline

### Setup

> **Note:** The pipeline uses the **Anthropic API** by default (Claude for generation, judging, and LLM-based evaluation). You will need a valid `ANTHROPIC_API_KEY`. Without it, the pipeline will not work.

```bash
# Create and activate conda environment
conda create -n education-env python=3.11
conda activate education-env

# Install the package
pip install -e .

# Set up API keys in .env
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### Generate Items

```bash
# Generate 10 items with V2 prompt, dynamic format
conda run -n education-env python scripts/run_pipeline.py \
  --topic confidence_intervals \
  --n-items 10 \
  --prompt-version v2

# Generate with specific facets and format
conda run -n education-env python scripts/run_pipeline.py \
  --topic confidence_intervals \
  --facets A4 A5 B15 B16 \
  --format true_false_per_option \
  --n-items 5

# Generate with textbook context
conda run -n education-env python scripts/run_pipeline.py \
  --topic confidence_intervals \
  --book-mode full_tex \
  --n-items 10
```

### Run Evaluation

```bash
# Evaluate a batch of generated items
conda run -n education-env python scripts/run_evaluation.py outputs/<run_dir> --out outputs/eval_results.json

# Save evaluation results
conda run -n education-env python scripts/run_evaluation.py outputs/<run_dir> \
  --out outputs/eval_results.json

# Item-level evaluation only (skip corpus metrics)
conda run -n education-env python scripts/run_evaluation.py outputs/<run_dir> \
  --skip-corpus

# Evaluate expert-authored examples
conda run -n education-env python scripts/eval_experts.py --out outputs/eval_experts.json
```

## Project Structure

```
education_agents/
├── src/education_agents/
│   ├── llm.py              # LiteLLM wrapper (swap providers via env var)
│   ├── schemas.py          # Pydantic models for items, reports, eval scores
│   ├── facets.py           # Facet map loader
│   ├── generator.py        # Item generation + facet auto-selection
│   ├── judge.py            # Independent facet-tag verification
│   ├── pipeline.py         # End-to-end orchestration
│   ├── evaluation/         # Rubric implementations
│   └── prompts/            # Generator (V1, V2) and judge prompt templates
├── scripts/
│   ├── run_pipeline.py     # CLI for generation
│   └── run_evaluation.py   # CLI for evaluation
├── web/
│   ├── index.html          # Item explorer dashboard
│   ├── compare.html        # Evaluation comparison dashboard
│   ├── app.jsx             # Item explorer React app
│   ├── compare.jsx         # Comparison React app
│   └── mock-data.js        # Static facet map for dashboards
├── data/facets/            # Facet map definitions
├── outputs/                # Generated artifacts and eval results
├── docs/                   # Rubric docs and generated item markdowns
└── workflow/               # Design docs, facet definitions, project goals
```

## Models Used

| Role | Default Model |
|------|---------------|
| Generator | `anthropic/claude-sonnet-4-6` |
| Judge | `anthropic/claude-sonnet-4-6` |
| Evaluation (LLM rubrics) | `anthropic/claude-sonnet-4-6` |
| Evaluation (embeddings) | `Qwen/Qwen3-Embedding-0.6B` |
