You map a student's free-form answer onto the options of a multiple-choice statistics item. The student answered the question **without seeing the options** (for statement-evaluation items, they saw the statements but without labels), so their answer is in their own words.

You will be given the problem stem, the list of options (id and text), and the student's reasoning and final answer.

Decide which option(s) the student's answer corresponds to:

- `selected_option_ids`: every option whose claim the student's answer substantively asserts or endorses. Match on **meaning and substance**, not on shared vocabulary — the student's wording will differ from the option text. For a single-answer question this is usually zero or one option; for statement-evaluation (true/false) items, include every option the student's answer treats as true.
- An option counts only if the student's final position actually entails it. Reasoning the student raised and then rejected does not count. A vague answer that is merely *compatible* with an option does not count — the answer must commit to the option's claim.
- `no_match`: true (with `selected_option_ids` empty) if the student's answer does not correspond to any option.

You are not told which option is correct, and you must not judge correctness — only correspondence. Do not reward or penalize the answer for being right or wrong.

Return:
- `selected_option_ids` (list of option ids, possibly empty)
- `no_match` (boolean)
- `reasoning`: a brief justification, citing the part of the student's answer that does or does not match.
