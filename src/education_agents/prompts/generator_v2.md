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

Stem: "Employee salaries are normally distributed with mean $55,000 and standard deviation $8,000. A sample of 25 employees is selected. What is the sampling distribution of the sample mean?"

- A) Normal with mean 55,000 and standard deviation 8,000 [B9] ← A student who picks this thinks the sampling distribution has the same SD as the population.
- B) Normal with mean 55,000 and standard deviation 8,000/√25 [A1, A3] ← Correct application of both concepts.
- C) Normal with mean 55,000/√25 and standard deviation 8,000 [B9, B13, B14] ← Reveals multiple misconceptions through a specific wrong calculation.

This is good because a student selects a concrete numerical answer, and that choice reveals which mental model they hold. The facets are invisible — diagnosed, not quizzed.

## Item Stem Guidelines

Build the stem around a **concrete scenario** with specific details:

- Use real-world contexts with specific numbers (sample sizes, means, standard deviations, confidence levels, interval bounds).
- When target facets involve quantitative relationships (A1, A3, A7, B9, B10, B13, B14), prefer scenarios that require computation or numerical reasoning, so that options can be specific numerical answers.
- When target facets involve interpretation (A4, A5, B15, B16), present a specific confidence interval (e.g., "(1.15, 4.20)") and ask students to interpret it — the options should be concrete interpretive statements about that specific interval, not generic definitions.
- When target facets involve manipulating CI width (A6, A7, B17), present a specific scenario where a researcher wants to change their interval, and options should be concrete actions or predictions.
- Avoid stems that ask "which statement is true" or "which correctly describes" — these invite abstract-definition options. Instead ask "what is…", "what would happen if…", "which interpretation is correct for this specific interval…", etc.

## Vary the Item Style

Choose from a range of item formats to avoid monotony:

- **Numerical/computational:** "What is the standard error?" / "What is the sampling distribution?" with specific numerical options.
- **Interpretation of a specific interval:** Give an interval with context; options are competing interpretations.
- **Predict the effect:** "The researcher changes X. What happens to Y?" with concrete predictions.
- **Action-based:** "What should the researcher do to achieve Z?" with specific combinations of actions.
- **True/false per option:** Present a specific scenario and several claims to evaluate individually.

## Coverage Rules

Your item MUST satisfy these constraints:

1. Each **goal facet** (A-prefix) listed in the target facets must be tagged on at least one **correct** option.
2. Each **problematic facet** (B-prefix) listed in the target facets must be tagged on at least one **incorrect** option (distractor).
3. Every option must have at least one facet tag.
4. An option may carry multiple tags (e.g., a distractor that conflates two misconceptions).
5. The **correct option** cannot be mapped to any **problematic facets**.
6. Each distractor must be a plausible answer that a student with a specific misconception would genuinely select — not an obviously wrong paraphrase of a misconception's definition.

## Few-Shot Examples

Below are examples of well-constructed items with their facet tagging. Study how the facets are embedded as latent concepts within concrete scenarios rather than stated directly:

{{EXAMPLES}}

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

Write a concrete, scenario-based item where the options are specific answers (numerical values, specific interpretations, concrete actions) — not abstract restatements of facet definitions. Each option's facet mapping should reflect which understanding or misconception would lead a student to select it.

Include a brief rationale for each option explaining the reasoning path a student would follow to arrive at that answer, and an overall explanation tying the item back to the target facets.

Respond with a JSON object matching the output schema exactly. Do not include any text outside the JSON.
