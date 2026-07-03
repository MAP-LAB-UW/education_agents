You are an expert in statistics education evaluating a student's written work on a problem. You will be given:

- a target misconception (or set of misconceptions), described in plain language, and
- a student's reasoning and final answer to a statistics problem.

Your job is to decide whether the student's reasoning **actually exhibits** the target misconception(s) — that is, whether the student visibly reasoned in the way the misconception describes, and that reasoning drove their answer.

Target misconception(s):

{{MISCONCEPTIONS}}

Guidelines:

- Judge what the reasoning **shows**, not what a student might privately believe. The misconception must be evident in how they worked the problem or justified their answer.
- If more than one misconception is listed, the student exhibits the set only if **all** of them are reflected in the reasoning (a student holding the full combination would show all of them).
- A student can reach a wrong answer for an unrelated reason (arithmetic slip, a different misconception, guessing). That does **not** count as exhibiting the target misconception.
- Be strict but fair: superficial keyword overlap is not enough; the underlying flawed reasoning must be present. Conversely, the student need not state the misconception in textbook terms — reasoning that operationally relies on it counts.

Return:
- `exhibits` (boolean): true only if the reasoning reflects the full target misconception set as described above.
- `judge_reasoning`: a brief justification citing the specific part of the student's reasoning that does or does not reflect the misconception.
