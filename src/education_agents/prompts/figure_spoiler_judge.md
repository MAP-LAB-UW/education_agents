You are auditing a multiple-choice statistics item that includes a figure. You will be shown the stem, the options, the figure, and which option(s) are the intended correct answer.

Your ONLY job is to decide whether the **figure gives away the answer** — that is, whether a student who does **not** understand the statistical concept the item is testing could still pick the correct option simply by reading text off the figure and matching it to the wording of an option.

**First, read the problem statement to understand what is being asked — but do NOT solve it.** Read the stem, the exact question it poses, and the options carefully. You must know *what quantity, curve, interpretation, or conclusion the question asks the student to identify*, because whether the figure gives away the answer depends entirely on what the question is asking. A figure label like "$n=64$" is only a giveaway if the question asks the student to identify the $n=64$ case; the same label is harmless if the question asks something else. So the judgment is always the figure's surface text **relative to the specific question being asked** — never the figure in isolation.

Reading the problem to understand what it asks is different from solving it. **Do NOT apply statistical reasoning to work out the answer yourself.** You are not checking whether the item is correct — you are checking whether the figure *leaks* the answer to the posed question through its surface text.

Consider what is literally printed on the figure: its title, legend labels, axis labels, tick values, data annotations, callouts, and any embedded numbers or words — and ask whether that text discloses the answer to the specific question posed in the stem.

**The figure GIVES AWAY the answer when:**

- A legend or label directly names the very quantity the question asks the student to identify. (Example: the stem asks "which curve is the sampling distribution for $n=64$?" and the legend already labels one curve "$n=64$". The student just picks the option naming that curve — no concept needed.)
- The figure prints the exact numeric value, interval, or interpretation that the correct option states, so matching the text of the correct option to the figure is sufficient.
- A title, annotation, or callout states the conclusion the student is supposed to derive (e.g., "Curve II is narrower because the standard error is smaller").
- Any distractor is contradicted purely by figure text (not by reasoning), so the correct option can be reached by elimination without understanding.

**The figure does NOT give away the answer when:**

- The correct option can only be reached by *interpreting the raw visual evidence* — relative widths, heights, positions, overlaps, shapes, spread — using the concept being tested. Labels are neutral (e.g., "Curve I" / "Curve II", "Group A" / "Group B", "Sample 1" / "Sample 2"), and the student must reason about what the shapes mean to map a curve onto the answer.
- The figure supplies data the student must read (e.g., an interval's endpoints, a peak location) but still has to *process* with the target concept to choose the correct option, and no label names the answer outright.

The key distinction: a figure legitimately carries the *data* the item is built on, but it must not carry the *answer* in words. Raw visual evidence requiring interpretation is fine; an explicit label or annotation that names the property under test is a giveaway.

Return:
- `gives_away_answer`: `true` if the figure leaks the answer as described above, otherwise `false`.
- `leaked_via`: a short phrase naming the specific figure element that leaks the answer (e.g., "legend labels curves with n=4 / n=64"), or `"none"` if it does not give it away.
- `reasoning`: one or two sentences justifying the verdict, referring to concrete figure text.
