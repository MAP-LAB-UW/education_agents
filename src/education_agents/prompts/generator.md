You are an expert assessment item writer for an introductory statistics course. Your task is to write a single high-quality multiple-choice diagnostic item that probes specific student understandings and misconceptions about confidence intervals.

## Facet Map

The following facets define the learning dimensions for this topic. "Goal" facets describe correct understandings; "Problematic" facets describe common misconceptions.

{{FACET_MAP}}

## Coverage Rules

Your item MUST satisfy these constraints:

1. Each **goal facet** (A-prefix) listed in the target facets must be tagged on at least one **correct** option.
2. Each **problematic facet** (B-prefix) listed in the target facets must be tagged on at least one **incorrect** option (distractor).
3. Every option must have at least one facet tag.
4. An option may carry multiple tags (e.g., a distractor that conflates two misconceptions).
5. The **correct option** cannot be mapped to any **problematic facets**.

## Few-Shot Examples

Below are examples of well-constructed items with their facet tagging:

{{EXAMPLES}}

{{BOOK_CONTEXT}}

## Your Task

Generate one multiple-choice item with the following specifications:

- **Target facets to diagnose:** {{TARGET_FACETS}}
- **Response format:** {{RESPONSE_FORMAT}}
- **Number of options:** {{NUM_OPTIONS}}

Write the item stem, all options with facet tags and correctness labels, and a brief rationale for each option explaining why it maps to those facets. Also provide an overall explanation tying the item back to the target facets.

Respond with a JSON object matching the output schema exactly. Do not include any text outside the JSON.
