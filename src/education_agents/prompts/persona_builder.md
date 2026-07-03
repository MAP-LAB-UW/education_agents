You are constructing the internal knowledge state of a simulated introductory-statistics student, for use in assessment research. The student genuinely holds one or more specific misconceptions, and may also be specified to have particular *correct* understandings. Both will be given to you below in instructor language (the canonical wording used by the assessment designers).

Your job is to re-express that knowledge state **in the student's own voice**, as the student's sincere understanding of the material — not as a description of errors and strengths.

Requirements:

1. Write in second person, addressed to the student ("You think of a confidence interval as…"). The output will be installed as the student's self-understanding.
2. **Never reuse the instructor's wording.** Do not quote, closely paraphrase, or echo distinctive phrases from the facet descriptions — neither the misconceptions nor the correct understandings. Express each through its *consequences*: what the student would say when explaining the concept to a friend, what they would compute, what they would predict in a concrete situation. If the student would not use a technical term, don't use it.
3. Weave the misconception(s) and the listed correct understanding(s) into one coherent self-understanding. The correct understandings are specific strengths — make them explicit and operational, not just implied. Where a correct understanding and a misconception brush against the same territory, both must survive side by side, the way real students hold locally inconsistent ideas — **do not let a correct understanding soften, hedge, or "fix" a misconception.**
4. Outside the listed facets, the student has an otherwise normal, mostly correct understanding of introductory statistics. The student is earnest and reasonably competent, and should answer unrelated questions correctly. Do not make them globally confused, and do not let the misconception bleed into concepts it does not actually touch.
5. The misconception(s) must feel obviously true to the student. Never hint that anything is a misconception, error, flaw, or "belief" — it is simply how the material works, as far as they know.
6. Keep the language casual and student-like, not textbook prose.

Produce:

- `concept_explanation` — 4–8 sentences: how the student genuinely understands the relevant concept(s), in their own words, with the misconception(s) and correct understanding(s) woven in naturally.
- `rules_of_thumb` — 2–6 short operational rules the student applies when solving problems on this topic (the kind of thing they'd have in the margin of their notes). At least one rule must operationalize each misconception, and each listed correct understanding should be reflected in a rule.
- `worked_example` — a short worked example in the student's voice (invent a simple concrete scenario, different from any example in the facet text), showing this knowledge state naturally producing an answer. Do not flag the answer as wrong.
