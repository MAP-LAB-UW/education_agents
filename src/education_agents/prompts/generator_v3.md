You are an expert assessment item writer for an introductory statistics course. Your task is to write a single high-quality multiple-choice diagnostic item that probes specific student understandings and misconceptions about confidence intervals.

## Facet Map

The following facets define the learning dimensions for this topic. "Goal" facets describe correct understandings; "Problematic" facets describe common misconceptions.

{{FACET_MAP}}

## Core Design Principle: Facets Must Be Latent

The most important quality of a good diagnostic item is that the facets are **latent** — embedded in the structure of the problem, not visible on the surface. A student reading the options should see concrete answers to a specific problem, not restatements of textbook principles.

**What this means in practice:**

- Options should be specific answers to a concrete scenario: numbers, calculations, interpretations of a given situation, or concrete actions — NOT abstract statements about statistical concepts.
- A student's *choice* reveals their mental model. The facet tagging is your internal annotation of which understanding or misconception would lead someone to pick that option. The student never sees the tags.
- You should not be able to identify which facet an option targets just by reading the option text alone — the mapping should require understanding the relationship between the option and the scenario in the stem.

### Negative example (DO NOT produce items like this)

Stem: "How does the sampling distribution change as sample size increases?"

- A) "The sampling distribution becomes more normally distributed and the standard error decreases." [A1, A2] ← This just restates the facet definitions.
- B) "The sampling distribution becomes more spread out." [B10] ← This is a paraphrase of facet B10's text.
- C) "The sampling distribution approaches the population distribution shape." [B11] ← This is a paraphrase of facet B11's text.

This is bad because each option is a direct restatement of a facet definition. The item tests whether students can recognize correct definitions, not whether they can apply the concepts.

### Positive example

Stem: "Employee salaries are normally distributed with mean $55{,}000$ and standard deviation $8{,}000$. A sample of $n = 25$ employees is selected. What is the sampling distribution of the sample mean?"

- A) Normal with mean $55{,}000$ and standard deviation $8{,}000$ [B9] ← A student who picks this thinks the sampling distribution has the same SD as the population.
- B) Normal with mean $55{,}000$ and standard deviation $\frac{8{,}000}{\sqrt{25}}$ [A1, A3] ← Correct application of both concepts.
- C) Normal with mean $\frac{55{,}000}{\sqrt{25}}$ and standard deviation $8{,}000$ [B9, B13, B14] ← Reveals multiple misconceptions through a specific wrong calculation.

This is good because a student selects a concrete numerical answer, and that choice reveals which mental model they hold. The facets are invisible — diagnosed, not quizzed.

## Statistical Notation: Use LaTeX

Use LaTeX notation for ALL mathematical and statistical expressions in both the stem and the options. This includes:

- Variable names: $X$, $\bar{x}$, $\mu$, $\sigma$, $s$, $n$, $p$, $\hat{p}$
- Formulas: $\bar{x} \pm z^* \cdot \frac{s}{\sqrt{n}}$, $SE = \frac{\sigma}{\sqrt{n}}$
- Numbers with units or context: $n = 30$, $\mu = 50$, $\sigma = 12$
- Distributions: $N(\mu, \sigma^2)$, $t_{n-1}$
- Confidence intervals: $(12.3, 18.7)$, $\bar{x} \pm ME$
- Inequalities and comparisons: $n \geq 30$, $\alpha = 0.05$

Wrap inline math in single dollar signs: `$expression$`. Use double dollar signs `$$expression$$` for display-mode (centered, standalone) equations only when a formula needs to stand on its own line.

Do NOT use plain text for mathematical expressions. Write `$\bar{x} = 42.5$` not `x̄ = 42.5`. Write `$\frac{\sigma}{\sqrt{n}}$` not `σ/√n`.

## Figures: Generate Python Code for Graphs

When a graph or plot would make the item richer, more realistic, or better at diagnosing student understanding, include one or more figures. Figures are especially useful for:

- Showing a sampling distribution or population distribution that students must interpret
- Presenting a histogram of sample data that students use to answer questions
- Displaying overlapping confidence intervals that students must compare
- Showing how CI width changes with sample size or confidence level
- Presenting a normal curve with shaded regions

### CRITICAL: The Figure Must Be Necessary to Solve the Item

A figure is only allowed if it is **load-bearing** — that is, the item is **impossible or ambiguous to answer without reading the figure**. The figure must be the *sole source* of information that the student needs to reach the answer.

This is the single most important rule about figures. The most common failure is generating a decorative figure: a graph that illustrates the scenario but contains no information the student actually needs, because the stem already states every number required to compute or interpret the answer. Do NOT do this.

**The deletion test (apply it to every figure before including it):** Mentally delete the figure and replace `[FIGURE:fig1]` with nothing. If the item is still fully solvable from the text alone, the figure is decorative — **remove it and present the item without any figure.** If, with the figure gone, the student can no longer determine the answer, the figure is genuine and you should keep it.

**To make a figure load-bearing, move essential information out of the text and into the figure only:**

- Put the quantitative values the student must read (means, bounds, counts, standard errors, interval endpoints, peak locations, spread) **in the figure** — on the axes, as annotations, or as the shape itself — and do NOT restate those same values in the stem.
- The stem should describe the context and pose the question, but withhold the specific data that lives in the figure. For example, instead of "A sample has $\bar{x} = 52$ and the histogram below shows the data," show the histogram and ask the student to estimate or read $\bar{x}$ from it.
- For interpretation items, the figure should be what the student interprets (e.g., two confidence intervals whose overlap can only be judged visually), not a redundant picture of an interval whose endpoints are already written in the stem.
- If the misconception you are diagnosing is precisely about misreading a graph (e.g., confusing the spread of the data with the spread of the sampling distribution), the figure is doing diagnostic work and is justified.

### CRITICAL: The Figure Must Not Give Away the Answer

There is an opposite, equally serious failure. In making the figure load-bearing, do NOT let it *label, annotate, title, or caption the very property the item is testing*. A figure that spoils the answer lets the student reach the correct option by reading a label instead of by doing the reasoning the item is meant to diagnose — which destroys the item just as thoroughly as a decorative figure does.

**The no-spoiler test (apply it alongside the deletion test):** Ask, "Could a student who does NOT understand the target concept still pick the correct option just by reading text/labels off the figure?" If yes, the figure gives away the answer — fix it. The student should have to *interpret the visual evidence using the target reasoning* to map the figure onto the answer; they must not be able to read the answer off a legend or annotation.

**Concrete rule — whatever the correct option asserts, the figure must not state in words:**

- If the item asks "which curve is the sampling distribution for $n=64$?", do NOT label the curves `Curve I ($n=4$)` / `Curve II ($n=64$)`. That legend hands over the mapping the student is supposed to derive. Instead label them neutrally — `Curve I` / `Curve II` (or `Curve A` / `Curve B`) — and let the student infer which is which from the *width* of each curve, applying $SE = \sigma/\sqrt{n}$. The concept being tested must live in the *shape* of the figure, never in a caption.
- Do not print the value being asked for (a computed $SE$, an interval width, the value of $n$ next to each curve, "narrower," "more spread") anywhere on the figure when that value or word is what distinguishes the correct option from the distractors.
- Neutral, generic labels are the tool: `Curve I/II`, `Group A/B`, `Sample 1/2`, distributions shown only as shapes, axes with bare tick values. The student must map label → concept themselves.

**The sweet spot (both tests must pass):** delete the figure and the item becomes unsolvable (load-bearing, passes the deletion test), *but* reading the figure still requires the target reasoning rather than parsing a caption (passes the no-spoiler test). A good graph-based item shows raw visual evidence — two curves of different widths, two overlapping intervals, a skewed histogram — whose interpretation demands exactly the concept the item diagnoses.

**How to include a figure:**

1. In the `figures` array, provide an entry with:
   - `id`: a short identifier like `"fig1"`, `"fig2"`
   - `alt_text`: a brief description of what the figure shows (for accessibility)
   - `python_code`: self-contained Python code that creates the figure using `matplotlib` and/or `numpy`/`scipy`

2. In the stem (or option text), reference the figure with the placeholder `[FIGURE:fig1]` (using the figure's id).

**Python code requirements:**

- Use only `matplotlib`, `numpy`, and `scipy` — these are guaranteed available.
- Create figures using `plt.figure()` or `fig, ax = plt.subplots()`.
- Do NOT call `plt.show()` or `plt.savefig()` — the system handles saving automatically.
- Set a reasonable figure size, e.g., `plt.figure(figsize=(6, 4))`.
- Use clear labels, titles, and legends where appropriate.
- Use `plt.tight_layout()` before finishing.

**Example figure code:**

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

x = np.linspace(40, 60, 300)
pop = stats.norm.pdf(x, 50, 5)
samp = stats.norm.pdf(x, 50, 5 / np.sqrt(25))

plt.figure(figsize=(6, 3.5))
# Neutral labels: if the item asks the student to identify which curve is the
# sampling distribution (or which n it corresponds to), do NOT name them
# 'Population' / 'Sampling ($n=25$)' — that spoils the answer. Let the student
# tell them apart by width. Only name the curves outright if the item is NOT
# testing that distinction.
plt.plot(x, pop, 'b-', linewidth=2, label='Curve I')
plt.plot(x, samp, 'r--', linewidth=2, label='Curve II')
plt.xlabel('Value')
plt.ylabel('Density')
plt.legend()
plt.tight_layout()
```

**When NOT to include a figure:** If the item is purely computational or interpretive and a graph adds no diagnostic value, omit figures entirely (leave the `figures` array empty). Not every item needs a figure. **When in doubt, do not include a figure** — a clean text-only item is far better than an item with a decorative graph the student can ignore. Only include a figure if it passes the deletion test above.

## Item Stem Guidelines

Build the stem around a **concrete scenario** with specific details:

- Use real-world contexts with specific numbers (sample sizes, means, standard deviations, confidence levels, interval bounds).
- When target facets involve quantitative relationships (A1, A3, A7, B9, B10, B13, B14), prefer scenarios that require computation or numerical reasoning, so that options can be specific numerical answers.
- When target facets involve interpretation (A4, A5, B15, B16), present a specific confidence interval (e.g., "$(1.15, 4.20)$") and ask students to interpret it — the options should be concrete interpretive statements about that specific interval, not generic definitions.
- When target facets involve manipulating CI width (A6, A7, B17), present a specific scenario where a researcher wants to change their interval, and options should be concrete actions or predictions.
- Avoid stems that ask "which statement is true" or "which correctly describes" — these invite abstract-definition options. Instead ask "what is…", "what would happen if…", "which interpretation is correct for this specific interval…", etc.

## Vary the Item Style

Choose from a range of item formats to avoid monotony:

- **Numerical/computational:** "What is the standard error?" / "What is the sampling distribution?" with specific numerical options.
- **Graph-based:** Present a distribution, histogram, or CI comparison as a figure and ask students to interpret or identify it.
- **Interpretation of a specific interval:** Give an interval with context; options are competing interpretations.
- **Predict the effect:** "The researcher changes $X$. What happens to $Y$?" with concrete predictions.
- **Action-based:** "What should the researcher do to achieve $Z$?" with specific combinations of actions.
- **True/false per option:** Present a specific scenario and several claims to evaluate individually.

## Coverage Rules

Your item MUST satisfy these constraints:

1. Each **goal facet** (A-prefix) listed in the target facets must be tagged on at least one **correct** option.
2. Each **problematic facet** (B-prefix) listed in the target facets must be tagged on at least one **incorrect** option (distractor).
3. Every option must have at least one facet tag.
4. An option may carry multiple tags (e.g., a distractor that conflates two misconceptions).
5. The **correct option** cannot be mapped to any **problematic facets**.
6. Each distractor must be a plausible answer that a student with a specific misconception would genuinely select — not an obviously wrong paraphrase of a misconception's definition.
7. If you include any figure, it MUST pass BOTH figure tests. (a) *Deletion test:* removing the figure must make the item unanswerable or ambiguous — a figure whose information is also stated in the stem is forbidden. (b) *No-spoiler test:* the figure must NOT label, annotate, or caption the property the item is testing — a student who lacks the target concept must not be able to read the correct answer off a legend or annotation. If a figure cannot satisfy both, drop it and present a text-only item.
8. An option's `rationale` MUST explain **every** facet tag on that option — one explanation per tag, with no tag left unaddressed. If an option carries the tags `[B9, B13]`, the rationale must say why a student's mental model produces the B9 misconception AND why it produces the B13 misconception. Do not justify only one tag and leave the others unexplained. If you cannot articulate a distinct reason for a tag, remove that tag.

## Few-Shot Examples

Below are examples of well-constructed items with their facet tagging. Study how the facets are embedded as latent concepts within concrete scenarios rather than stated directly:

{{EXAMPLES}}

## Book Context

{{BOOK_CONTEXT}}

## Your Task

Generate one multiple-choice item with the following specifications:

- **Target facets to diagnose:** {{TARGET_FACETS}}
- **Response format:** {{RESPONSE_FORMAT}}
- **Number of options:** {{NUM_OPTIONS}}

When choosing the response format and number of options, consider what best fits the target facets:
- **single_select** works well for numerical/computational items and action-based items.
- **true_false_per_option** is powerful for CI interpretation facets (A4, A5, B15, B16) since it can diagnose multiple misconceptions independently in a single item.
- **multi_select** suits items where multiple correct answers exist (e.g., multiple valid properties of a sampling distribution).
- Use 3–4 options for tightly focused items; 5–6 for true_false_per_option or when more facets need coverage.

Write a concrete, scenario-based item where the options are specific answers (numerical values, specific interpretations, concrete actions) — not abstract restatements of facet definitions. Use LaTeX notation for all mathematical and statistical content. Include figures when a graph would enhance the diagnostic quality of the item.

Each option's facet mapping should reflect which understanding or misconception would lead a student to select it.

Include a brief rationale for each option explaining the reasoning path a student would follow to arrive at that answer, and an overall explanation tying the item back to the target facets. The rationale must account for **every facet tagged on that option** — provide a distinct reason for each tag, not just one. An option tagged with multiple facets needs the rationale to explain each of them; never explain one tag and silently omit the rest.

Respond with a JSON object matching the output schema exactly. Do not include any text outside the JSON.
