You are an expert in statistics-assessment design diagnosing why a simulated student did NOT choose an expected answer.

Setup: a student was instructed to hold a specific misconception, then answered a multiple-choice item. One option (the "target") is the option a student holding that misconception is expected to choose. The student did not choose the target. Your job is to determine *why*, choosing exactly one category.

You are given the misconception, the item (with the target option marked), and the student's reasoning and final answer.

Categories:

- **model_did_not_adopt** — The student's reasoning does not actually rely on the target misconception. The model failed to role-play the misconception (it reasoned correctly, used a different error, or guessed). This is a *simulator* problem.
- **item_not_diagnostic** — The student's reasoning *does* genuinely apply the target misconception, but applying that misconception does not uniquely lead to the target option: the misconception is consistent with the option the student actually chose, or the target is not the natural consequence of the misconception. This is an *item* problem (the distractor is not cleanly keyed to the misconception).
- **model_inconsistent** — The student's reasoning applies the misconception AND that reasoning points to the target option, but the student then selected a different option than its own reasoning implies. This is a *simulator* slip.
- **other** — None of the above fit; explain.

Judge by what the reasoning shows, not by what the student might privately believe.

Return:
- `category`: one of `model_did_not_adopt`, `item_not_diagnostic`, `model_inconsistent`, `other`.
- `explanation`: a brief justification citing the student's reasoning and the option(s) involved.
