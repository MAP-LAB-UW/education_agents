# Generated Items — V3 Prompt with Figures (Claude Sonnet 4.6)

**Generator model:** Claude Sonnet 4.6  
**Judge model:** Gemini 3.1 Pro Preview  
**Topic:** Confidence Intervals  
**Items:** 10  
**Prompt version:** V3 (figure-encouraged, LaTeX notation)  
**Format:** Dynamic (model chooses)  

---

## Item 1

**Target facets:** A6, A7, B17  
**Format:** Single Select  

> **Facet selection reasoning:** These three facets cluster tightly around CI width and precision. A6 addresses the correct understanding that higher confidence levels produce wider intervals, A7 addresses the correct understanding that larger standard errors also produce wider intervals, and B17 captures the common misconception that higher confidence yields a more precise (narrower) interval. An item can present a scenario where a student must reason about what happens to CI width when confidence level is raised, directly distinguishing learners who correctly understand the width-confidence tradeoff (A6) from those holding the B17 misconception, while also probing whether they understand the role of standard error (A7) in determining width. This combination has not yet been used and targets a cohesive conceptual space around interval width determinants.

### Stem

A researcher computes a $95\%$ confidence interval for the mean resting heart rate (in bpm) of adults using a random sample of $n = 40$ participants. The resulting interval is $(68.2, 74.6)$, giving a width of $6.4$ bpm. The researcher wants to reduce the width of the interval in a follow-up study. Which of the following changes would achieve a shorter confidence interval?

### Options

**A.** Increase the confidence level to $99\%$ and increase the sample size to $n = 100$.  
*Facets: A1, A7, B17*  
*Rationale: A student holding the B17 misconception believes higher confidence yields more precision (shorter interval), so they accept the confidence level increase. They also correctly know larger $n$ reduces SE, but the net effect is still a wider interval because the larger critical value from $99\%$ dominates. This option conflates the beneficial effect of larger $n$ with the misconception that higher confidence gives a shorter interval.*

**B.** Increase the confidence level to $99\%$ and keep the sample size at $n = 40$.  
*Facets: A7, B17*  
*Rationale: A student with the B17 misconception believes that higher confidence means more precision, producing a narrower interval. They do not change the sample size, so the standard error stays the same, and the larger critical value from $99\%$ makes the interval even wider. This directly diagnoses the B17 misconception in isolation.*

**C.** Decrease the confidence level to $90\%$ and increase the sample size to $n = 100$. :white_check_mark:  
*Facets: A6, A7*  
*Rationale: This is correct. Decreasing the confidence level from $95\%$ to $90\%$ reduces the critical value $z^*$, making the margin of error smaller (A6). Increasing $n$ from $40$ to $100$ reduces the standard error $SE = \sigma/\sqrt{n}$, which also shrinks the margin of error (A7). Both changes work together to produce a shorter interval.*

**D.** Decrease the confidence level to $90\%$ and decrease the sample size to $n = 20$.  
*Facets: A6, B10*  
*Rationale: A student who correctly understands that lowering the confidence level shortens the interval (A6) but mistakenly believes that a smaller sample size also helps (perhaps confusing a larger spread with a smaller interval, or simply ignoring the effect of $n$ on SE) would choose this. In reality, decreasing $n$ increases the standard error, which widens the interval and partially or fully offsets the benefit of the lower confidence level.*

### Explanation

This item targets three interrelated facets about CI width. Facet A6 states that CI width depends on the confidence level — a higher confidence level requires a larger critical value $z^*$, producing a wider interval, while a lower confidence level produces a narrower one. Facet A7 states that CI width depends on the standard error — since $SE = \sigma/\sqrt{n}$, increasing $n$ decreases $SE$ and narrows the interval. Facet B17 is the misconception that higher confidence yields more precision (a shorter interval), which is exactly backwards. Option C (correct) applies both A6 and A7 correctly: lower confidence level reduces $z^*$ and larger $n$ reduces $SE$, both shrinking the margin of error $ME = z^* \cdot \frac{s}{\sqrt{n}}$. Option B isolates the B17 misconception — a student who thinks $99\%$ confidence gives a shorter interval selects it. Option A combines B17 with a correct understanding of $n$'s role, but the net result is still a wider interval. Option D correctly applies A6 but incorrectly assumes that a smaller $n$ is either neutral or helpful, revealing confusion about how sample size affects SE.

### Judge Report

**Overall agreement:** 2/4 options matched  
**Issues:** Option A is mathematically a correct answer, meaning the item has two correct options (A and C). The standard error reduction from n=40 to n=100 (a factor of ~1.58) completely outpaces the critical value increase from 95% to 99% (a factor of ~1.31). The resulting margin of error is smaller. To fix the item, change the sample size in Option A to something smaller, like n=50. At n=50, the SE reduction (factor of ~1.12) is entirely eclipsed by the critical value increase (factor of ~1.31), ensuring the interval is genuinely wider and fixing the distractor. The generator tagged Option B with A7, but selecting Option B implies the student ignores or does not understand the effect of sample size on CI width, so the goal facet A7 is incorrectly attributed.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A1, A7, B17 | A7, B17 | partial | 0.95 |
| B | A7, B17 | B17 | partial | 0.9 |
| C | A6, A7 | A6, A7 | match | 1.0 |
| D | A6, B10 | A6, B10 | match | 0.9 |

---

## Item 2

**Target facets:** A4, A5, B15, B16  
**Format:** True False Per Option  

> **Facet selection reasoning:** This combination targets the interpretation of confidence intervals, a conceptually rich area that hasn't been covered in the previous item. A4 (correct interpretation of confidence level as a long-run frequency across replications) and A5 (CI captures population parameter, not sample statistics) are paired with B15 (misinterpreting CI as a probability statement about a single interval containing the mean) and B16 (thinking CI estimates sample statistics or sample data rather than population parameters). These four facets are tightly related—they all revolve around what a confidence interval actually means and what it is estimating—making it natural to craft a single item stem that distinguishes correct understanding from common misconceptions about CI interpretation.

### Stem

A nutritionist takes a random sample of $n = 40$ adults and measures their daily sugar intake. From this sample, she computes $\bar{x} = 82$ grams and constructs the following 90% confidence interval for the mean daily sugar intake of all adults in the population:
$$( 76.4, \ 87.6 )$$
For each of the following statements about this confidence interval, decide whether it is **True** or **False**.

### Options

**A.** We are 90% confident that the true mean daily sugar intake of all adults in the population is between $76.4$ and $87.6$ grams. :white_check_mark:  
*Facets: A4, A5*  
*Rationale: This is the correct interpretation. 'We are 90% confident' correctly expresses the confidence level as a long-run frequency property of the procedure (A4), and the interval targets the true population mean $\mu$, not a sample statistic (A5).*

**B.** There is a 90% probability that the true mean daily sugar intake of all adults is between $76.4$ and $87.6$ grams.  
*Facets: B15*  
*Rationale: This statement treats the confidence interval as a probability statement about the fixed (but unknown) population parameter $\mu$. Once the interval is constructed, $\mu$ is either inside or outside it — the probability is not 0.90. A student who selects 'True' here is treating the confidence level as a direct probability that this specific interval contains $\mu$ (B15).*

**C.** If we repeatedly took samples of $n = 40$ adults and constructed 90% confidence intervals the same way, about 90% of those intervals would contain the true population mean. :white_check_mark:  
*Facets: A4, A5*  
*Rationale: This is the correct long-run frequency interpretation of a 90% confidence level (A4). It correctly identifies the target as the true population mean (A5). Students who understand both facets should mark this True.*

**D.** We are 90% confident that the mean daily sugar intake of the 40 adults in the sample is between $76.4$ and $87.6$ grams.  
*Facets: A4, B16*  
*Rationale: The sample mean $\bar{x} = 82$ is a known value computed directly from the data — it is already known with certainty and does not need to be estimated. Saying the CI captures the sample mean confuses the target of inference: CIs are built to capture the unknown population parameter $\mu$, not the observed sample statistic (B16). A student marking this True is misidentifying what the interval estimates.*

**E.** 90% of all adults in the population consume between $76.4$ and $87.6$ grams of sugar per day.  
*Facets: B15, B16*  
*Rationale: This statement misidentifies the CI as capturing individual data values in the population rather than the population mean $\mu$ (B16). It also misreads the confidence level as a statement about what proportion of individuals fall inside the interval (B15). A student selecting 'True' here conflates a confidence interval with a reference range for individual observations.*

**F.** Of 100 confidence intervals constructed using this same method, we would expect approximately 90 of them to contain $\bar{x} = 82$ grams.  
*Facets: A4, B16*  
*Rationale: This option correctly invokes the repeated-sampling interpretation of the confidence level (A4 surface language) but directs it at the wrong target: the sample mean $\bar{x}$ rather than the population mean $\mu$ (B16). The sample mean is not what CI procedures try to capture across replications; the population mean is. A student who marks this True understands the long-run frequency idea but misidentifies the estimand.*

### Explanation

This item diagnoses four facets simultaneously through a concrete 90% CI scenario. Options A and C are both correct and require students to recognize (1) that the confidence level describes a long-run frequency property of the procedure (A4) and (2) that the interval targets the unknown population mean $\mu$, not any sample statistic (A5). Option B targets B15 — the common misconception that the confidence level is a direct probability that this specific realized interval contains the parameter. Options D and F target B16 — the misconception that a CI estimates the sample mean rather than the population mean — while option F also probes whether students can catch a subtle misuse of the correct repeated-sampling language. Option E targets both B15 and B16 simultaneously, representing the misconception that the CI describes a frequency of individual-level data rather than a parameter estimate.

### Judge Report

**Overall agreement:** 3/6 options matched  
**Issues:** The generator frequently tags 'A4' on distractor options (D, F) simply because the option borrows valid A4 phrasing as a trap. However, from a diagnostic perspective, a student marking 'True' on these distractors is primarily demonstrating the B16 misconception, not an understanding of A4. Option E represents the 'population proportion / individual values' misconception. The facet map's B16 explicitly mentions 'true scores or sample data instead of population parameters', making B16 the primary fit. Tagging B15 here dilutes the definition of B15, which is specifically about parameter probability.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A4, A5 | A4, A5 | match | 0.95 |
| B | B15 | B15 | match | 0.95 |
| C | A4, A5 | A4, A5 | match | 1.0 |
| D | A4, B16 | B16 | partial | 0.9 |
| E | B15, B16 | B16 | partial | 0.85 |
| F | A4, B16 | B16 | partial | 0.9 |

---

## Item 3

**Target facets:** A1, A2, B9, B10  
**Format:** Single Select  

> **Facet selection reasoning:** These four facets cluster around a coherent conceptual theme: how sample size affects the shape and spread of the sampling distribution. A1 (larger n → smaller SE, more packed distribution) and A2 (larger n → closer to normal, not mirroring population) represent the correct understandings, while B9 (sampling distribution mirrors population distribution, so spread stays constant regardless of n) and B10 (larger n → more spread out) are the two classic opposing misconceptions. An item stem can present a scenario where sample size is increased and ask what happens to the sampling distribution, naturally discriminating among students who hold these different beliefs. This combination has not been used in prior items and covers important under-tested facets about the Central Limit Theorem and standard error.

### Stem

A population of exam scores is strongly right-skewed with mean $\mu = 72$ and standard deviation $\sigma = 15$. A researcher draws repeated random samples of size $n = 100$ from this population and records the sample mean each time.

The figure below shows four proposed descriptions of the resulting sampling distribution of $\bar{x}$. Which one is correct?

![Four panels showing proposed sampling distributions of the sample mean. Option A is right-skewed and wide (sd=15). Option B is right-skewed and narrow (sd=1.5). Option C is approximately normal and narrow (sd=1.5). Option D is approximately normal and wide (sd=15).](figures/sonnet_4_6_v3_figures/item3_fig1.png)

### Options

**A.** Right-skewed with mean $72$ and standard deviation $15$  
*Facets: B9, B11*  
*Rationale: A student who believes the sampling distribution mirrors the population distribution would choose this option. They preserve both the shape (right-skewed) and the standard deviation ($\sigma = 15$) from the population, ignoring how repeated sampling and the Central Limit Theorem transform the distribution.*

**B.** Right-skewed with mean $72$ and standard deviation $\frac{15}{\sqrt{100}} = 1.5$  
*Facets: B9, B10*  
*Rationale: A student who correctly computes the standard error ($\frac{\sigma}{\sqrt{n}} = 1.5$) but still thinks the shape of the sampling distribution mirrors the population would pick this. They understand sample size reduces spread (A1) but do not understand the CLT's effect on shape (B9 regarding shape, misconception akin to B11).*

**C.** Approximately normal with mean $72$ and standard deviation $\frac{15}{\sqrt{100}} = 1.5$ :white_check_mark:  
*Facets: A1, A2, A3*  
*Rationale: This is correct. With $n = 100 \geq 30$, the Central Limit Theorem guarantees the sampling distribution is approximately normal regardless of the population's skewed shape (A2). The mean of the sampling distribution equals the population mean $\mu = 72$ (A3), and the standard error is $\frac{\sigma}{\sqrt{n}} = \frac{15}{\sqrt{100}} = 1.5$, which is smaller than the population standard deviation (A1).*

**D.** Approximately normal with mean $72$ and standard deviation $15$  
*Facets: A2, B9*  
*Rationale: A student who knows that the CLT makes the sampling distribution approximately normal (A2) but incorrectly believes the spread stays the same as the population would choose this. They carry over the population standard deviation $\sigma = 15$ instead of computing the standard error, reflecting the misconception that the sampling distribution's variability is unchanged (B9, B10 in the sense of not understanding how $n$ reduces spread).*

### Explanation

This item targets four facets simultaneously through a concrete numerical scenario. Facet A1 (standard error decreases with larger $n$) is probed by contrasting options with $\sigma = 15$ versus $SE = 1.5$: students who pick options A or D fail to apply $SE = \frac{\sigma}{\sqrt{n}}$. Facet A2 (sampling distribution approaches normality, not population shape) is probed by contrasting right-skewed options (A, B) with approximately normal options (C, D): students who pick A or B believe the skewed population shape is preserved in the sampling distribution. Facet B9 (sampling distribution mirrors population distribution) manifests in options A and D, where either the shape or the standard deviation — or both — match the population. Facet B10 (larger sample size spreads out the sampling distribution) is implicitly countered by option C, where larger $n$ produces a tighter distribution ($SE = 1.5 < 15$); students who intuit larger samples mean more spread might resist the correct answer. Together the four options form a $2 \times 2$ grid crossing shape (skewed vs. normal) and spread ($\sigma$ vs. $SE$), making each option diagnostic of a specific combination of understandings and misconceptions.

### Judge Report

**Overall agreement:** 2/4 options matched  
**Issues:** The item itself is very well-constructed with an elegant 2x2 distractor design crossing shape and spread. The visuals cleanly align with the text. Facet A3 (the mean of the sampling distribution equals the population mean) is tagged in the correct Option C, but it is not actively tested by any distractors. All four options correctly center the mean at 72. To actively test A3 or B13, a distractor with an incorrect mean would be needed. The generator made a tagging error for Option B by including B10 (sampling distribution is more spread out) when Option B clearly displays a tighter distribution (SD = 1.5 vs population 15). It contradicted its own rationale.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | B9, B11 | B9 | partial | 0.9 |
| B | B9, B10 | A1, B9 | partial | 0.95 |
| C | A1, A2, A3 | A1, A2, A3 | match | 1.0 |
| D | A2, B9 | A2, B9 | match | 0.95 |

---

## Item 4

**Target facets:** A3, A4, B13, B15  
**Format:** True False Per Option  

> **Facet selection reasoning:** This combination focuses on the sampling distribution mean and confidence interval interpretation. A3 (mean of sampling distribution equals population mean) and B13 (misconception that the mean depends on sample size) are conceptually linked around what determines the center of the sampling distribution. Pairing these with A4 (correct interpretation of confidence level as a percentage of replications) and B15 (misconception that CI represents a probability for any particular interval) creates a coherent item that probes whether students understand both the fixed nature of the population mean and what the confidence level actually means across repeated samples. This combination has not been used before and covers under-explored facets around sampling distribution center and repeated-sampling interpretation of confidence levels.

### Stem

A researcher takes repeated random samples of size $n = 40$ from a large population with mean $\mu = 72$ and standard deviation $\sigma = 10$. She constructs a 95% confidence interval from each sample. After collecting many such intervals, she makes the following claims. Indicate whether each claim is **True** or **False**.

### Options

**A.** The mean of the sampling distribution of $\bar{x}$ is $72$, regardless of the sample size used. :white_check_mark:  
*Facets: A3*  
*Rationale: A student who understands that the mean of the sampling distribution always equals the population mean $\mu$ will correctly mark this True. The sample size does not affect the center of the sampling distribution, only its spread.*

**B.** If the researcher had used $n = 100$ instead of $n = 40$, the mean of the sampling distribution of $\bar{x}$ would be closer to $72$.  
*Facets: B13*  
*Rationale: A student holding the B13 misconception believes that sample size influences the mean of the sampling distribution. This claim is False because $\mu_{\bar{x}} = \mu = 72$ regardless of sample size; changing $n$ only changes the standard error, not the center.*

**C.** For a specific 95% CI she computed, say $(69.9, 74.1)$, there is a 95% probability that $\mu$ falls between $69.9$ and $74.1$.  
*Facets: B15*  
*Rationale: A student with the B15 misconception treats the confidence level as a probability that the fixed population parameter $\mu$ lies within a specific already-constructed interval. In reality, $\mu$ is a fixed (unknown) constant — it either is or is not in the interval. The 95% refers to the long-run behavior of the procedure, not a probability about this particular interval.*

**D.** If the researcher repeats this process many times, about 95% of the confidence intervals she constructs will contain $\mu = 72$. :white_check_mark:  
*Facets: A4, A3*  
*Rationale: A student who correctly understands the confidence level as a long-run frequency property (A4) and recognizes that the intervals are designed to capture the true population mean $\mu$ (A3) will correctly mark this True. The 95% confidence level means that 95% of all such intervals from repeated sampling will capture the true $\mu$.*

**E.** For a specific 95% CI she computed, say $(69.9, 74.1)$, there is a 95% probability that the sample mean $\bar{x}$ falls between $69.9$ and $74.1$.  
*Facets: B15, B13*  
*Rationale: A student conflating B15 (treating CI as a probability statement) and B13 (confusing what the interval captures) might believe the interval is about the sample mean rather than $\mu$. This is False: the sample mean is always the center of the interval and is already known; the interval is designed to capture $\mu$, not $\bar{x}$.*

### Explanation

This item targets four facets. Facet A3 (mean of sampling distribution equals $\mu$) is probed by options A and B: option A is correctly True, while option B is False because sample size does not shift the center of the sampling distribution (B13). Facet A4 (correct long-run frequency interpretation of confidence level) is probed by option D, which is correctly True. Facet B15 (treating the confidence level as a probability about a specific interval) is probed by options C and E, both of which are False — once an interval is constructed, $\mu$ either is or is not inside it, and the 95% refers to the long-run procedure, not to any single realized interval.

### Judge Report

**Overall agreement:** 3/5 options matched  
**Issues:** In Option E, the generator explicitly stated in its rationale that B13 is 'confusing what the interval captures', but according to the provided facet map, B13 is actually 'The mean of the sampling distribution depends on sample size'. The correct facet for confusing the interval's target (sample mean vs. population mean) is B16. In Option D, the generator tagged A3 (mean of sampling distribution), but the option text evaluates the interpretation of the confidence level (A4) and what the interval attempts to capture (A5), not the mean of the sampling distribution.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A3 | A3 | match | 1.0 |
| B | B13 | B13 | match | 1.0 |
| C | B15 | B15 | match | 1.0 |
| D | A4, A3 | A4, A5 | partial | 0.9 |
| E | B15, B13 | B15, B16 | partial | 1.0 |

---

## Item 5

**Target facets:** A5, A6, B16, B17  
**Format:** True False Per Option  

> **Facet selection reasoning:** This combination targets the purpose and precision of confidence intervals together. A5 (CI captures population parameter) and A6 (wider CI with higher confidence level) are paired against B16 (misconception that CI estimates sample statistics) and B17 (misconception that higher confidence yields a shorter/more precise interval). These facets are conceptually linked around what a CI is estimating and how confidence level affects its width, allowing a single item stem to distinguish correct understanding from two common errors simultaneously. This combination differs from all previously used sets while covering under-explored pairings of A5 and B17 together.

### Stem

A nutritionist calculates a 90% confidence interval for the mean daily sodium intake (in mg) of adults in a city and obtains $(1{,}820,\; 2{,}180)$. She is unhappy with the width of this interval and considers two changes for a follow-up study: increasing the confidence level to 99% and reducing the sample size.

For each of the following statements, decide whether it is **True** or **False**.

### Options

**A.** The interval $(1{,}820,\; 2{,}180)$ tells us that 90% of adults in the city have a daily sodium intake between $1{,}820$ mg and $2{,}180$ mg.  
*Facets: B16*  
*Rationale: A student who believes the CI describes individual data values rather than the population parameter would mark this True. The interval estimates the population mean, not the distribution of individual sodium intakes.*

**B.** We are 90% confident that the true mean daily sodium intake of all adults in the city is between $1{,}820$ mg and $2{,}180$ mg. :white_check_mark:  
*Facets: A5*  
*Rationale: This is the correct interpretation: the CI is designed to capture the true population mean, not sample statistics or individual values. A student with a solid understanding of A5 will mark this True.*

**C.** The interval $(1{,}820,\; 2{,}180)$ estimates the mean daily sodium intake $\bar{x}$ observed in her sample.  
*Facets: B16*  
*Rationale: A student who thinks the CI summarizes or estimates the sample mean rather than the population mean would mark this True. In fact, $\bar{x}$ is already known from the sample; the CI is constructed to estimate the unknown population mean $\mu$.*

**D.** Switching from 90% to 99% confidence will produce a shorter interval and therefore a more precise estimate of the population mean.  
*Facets: A6, B17*  
*Rationale: A student holding the B17 misconception (higher confidence = more precise = shorter interval) would mark this True. In reality, increasing the confidence level requires a larger critical value $z^*$, which widens the interval, making it less precise (A6).*

**E.** Reducing the sample size while also switching to 99% confidence will make the follow-up interval shorter than $(1{,}820,\; 2{,}180)$.  
*Facets: A6, B17*  
*Rationale: Both changes work against a shorter interval: increasing the confidence level raises $z^*$ and reducing the sample size increases the standard error $SE = s/\sqrt{n}$, both of which widen the interval. A student who believes higher confidence yields shorter intervals (B17) and misunderstands the effect of sample size may erroneously mark this True.*

**F.** If she instead lowers the confidence level to 80% (keeping the same sample), the resulting interval would be narrower than $(1{,}820,\; 2{,}180)$. :white_check_mark:  
*Facets: A5, A6*  
*Rationale: Lowering the confidence level decreases the critical value $z^*$, which shrinks the margin of error and produces a narrower interval. This correctly applies the relationship between confidence level and CI width (A6) and keeps focus on estimating the population mean (A5).*

### Explanation

This item diagnoses four facets simultaneously through a concrete CI scenario. **A5** is probed by options B, C, and F: the correct interpretation (B, F) targets the population mean $\mu$, while C reveals B16 thinking by claiming the interval estimates the already-known sample mean $\bar{x}$. **B16** is further probed by option A, where a student mistakes the CI for a description of individual data values. **A6** and **B17** are jointly probed by options D and E: a student holding B17 (higher confidence $\Rightarrow$ shorter interval) will incorrectly endorse D or E, while a student who correctly understands A6 (higher confidence level $\Rightarrow$ wider interval via larger $z^*$) will mark both False. Option F provides a positive application of A6: lowering confidence level from 90% to 80% unambiguously narrows the interval.

### Judge Report

**Overall agreement:** 4/6 options matched  
**Issues:** None  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | B16 | B16 | match | 1.0 |
| B | A5 | A5 | match | 1.0 |
| C | B16 | B16 | match | 1.0 |
| D | A6, B17 | A6, B17 | match | 1.0 |
| E | A6, B17 | A6, A7, B17 | partial | 0.9 |
| F | A5, A6 | A6 | partial | 0.9 |

---

## Item 6

**Target facets:** A1, A7, B8, B10  
**Format:** Single Select  

> **Facet selection reasoning:** This combination focuses on how sample size affects the sampling distribution and, by extension, the confidence interval width. A1 (larger sample → smaller standard error → tighter sampling distribution) and A7 (CI width increases with larger standard error) form the correct conceptual chain. B8 (confusing sampling distribution with sample distribution) and B10 (mistakenly believing larger samples spread out the sampling distribution) are common misconceptions that directly oppose A1 and A7. Together these facets support a question that asks students to reason about what happens to a CI when sample size changes, naturally distinguishing correct understanding from two distinct but related misconceptions. This combination has not been used in any prior item and covers B8, which is so far uncovered.

### Stem

A researcher surveys $n = 16$ students from a university and records their weekly study hours. The data have a sample mean of $\bar{x} = 20$ hours and a sample standard deviation of $s = 8$ hours. She constructs a $95\%$ confidence interval and gets $(16.74, 23.26)$.

A colleague suggests replicating the study but surveying $n = 64$ students instead. Assuming the sample mean and standard deviation remain the same ($\bar{x} = 20$, $s = 8$), what would happen to the width of the $95\%$ confidence interval in the new study?

### Options

**A.** The interval would be wider, approximately $(18.04, 21.96)$, because more data points create more variability in the estimate.  
*Facets: B10*  
*Rationale: A student holding misconception B10 believes that a larger sample size leads to a more spread-out sampling distribution, and therefore a wider confidence interval. They might reason that 'more data = more spread,' producing the incorrect wider interval.*

**B.** The interval would be the same width $(16.74, 23.26)$, because the width depends only on the variability within the original sample data, not on how many people you survey.  
*Facets: B8*  
*Rationale: A student with misconception B8 confuses the sampling distribution with the single-sample distribution. They think the CI width is determined solely by the spread of scores within the collected dataset, not by the standard error of the sampling distribution, so changing $n$ would have no effect.*

**C.** The interval would be narrower, approximately $(18.04, 21.96)$, because a larger sample size reduces the standard error $SE = \frac{s}{\sqrt{n}}$, producing a tighter interval. :white_check_mark:  
*Facets: A1, A7*  
*Rationale: A student with correct understanding sees that increasing $n$ from 16 to 64 cuts the standard error in half: $SE = \frac{8}{\sqrt{64}} = 1.0$ vs. $\frac{8}{\sqrt{16}} = 2.0$. Because CI width depends directly on the standard error ($\text{width} = 2 \times z^* \times SE$), halving $SE$ halves the width, producing the narrower interval $(18.04, 21.96)$.*

**D.** The interval would be wider, approximately $(16.74, 23.26)$ or even broader, because a larger sample is more likely to include extreme values, increasing the margin of error.  
*Facets: B10, B8*  
*Rationale: This distractor combines two misconceptions: the student believes larger samples produce more spread (B10) and that the CI reflects the variability of individual scores in the sample rather than the precision of the mean estimate (B8). They reason that more participants means more outliers, which widens the interval.*

### Explanation

This item targets four facets. Correct option C requires understanding that increasing sample size shrinks the standard error ($SE = s/\sqrt{n}$), which directly reduces CI width (A1 and A7). Option A targets B10: the misconception that larger samples create more spread in the sampling distribution, leading to a wider interval. Option B targets B8: confusing the sampling distribution with the single sample's distribution, so the student thinks only within-sample variability determines CI width, making $n$ irrelevant. Option D combines B8 and B10, reflecting a student who both conflates sample and sampling distributions and believes larger samples yield more spread. The concrete numerical values in each option make the facet distinctions latent — a student's choice directly reveals their mental model without the item ever naming the underlying concepts.

### Judge Report

**Overall agreement:** 4/4 options matched  
**Issues:** The 95% confidence interval in the stem is mathematically incorrect. With mean = 20, s = 8, n = 16, the standard error is 2. The margin of error provided is 3.26 (23.26 - 20), implying a critical value of 1.63, which is incorrect for a 95% confidence level (z = 1.96 or t = 2.13). Option A contains an internal contradiction: it states the interval would be 'wider' but provides the numerical interval (18.04, 21.96), which has a margin of error of 1.96 and is actually *narrower* than the original interval (16.74, 23.26). Option D contains a similar contradiction: it states the interval would be 'wider, approximately (16.74, 23.26)', but this interval is exactly the *same width* as the original interval provided in the stem.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | B10 | B10 | match | 1.0 |
| B | B8 | B8 | match | 1.0 |
| C | A1, A7 | A1, A7 | match | 1.0 |
| D | B10, B8 | B8, B10 | match | 0.95 |

---

## Item 7

**Target facets:** A2, A3, B11, B12  
**Format:** Single Select  

> **Facet selection reasoning:** This combination focuses on the shape and center of the sampling distribution, which are conceptually linked but distinct ideas. A2 (sampling distribution approaches normality as n increases, not population shape) and B12 (misconception that it's always normal regardless of n or population shape) contrast the correct understanding of the Central Limit Theorem with a common over-generalization. A3 (mean of sampling distribution equals population mean) and B11 (misconception that larger samples make the sampling distribution closer to the population distribution in shape) add the center-of-distribution concept and a related shape misconception. Together these facets allow a single item stem to probe whether students truly understand what the CLT says about shape versus what stays constant (the mean), distinguishing nuanced correct knowledge from two distinct but related misconceptions. This combination has not been used in prior items.

### Stem

A researcher studies the reaction times of adults in a population that is **strongly right-skewed** with mean $\mu = 320$ ms and standard deviation $\sigma = 80$ ms. The researcher draws a random sample of $n = 64$ adults and computes the sample mean $\bar{x}$.

Which of the following correctly describes the sampling distribution of $\bar{x}$?

### Options

**A.** Approximately normal with mean $320$ ms and standard deviation $\frac{80}{\sqrt{64}} = 10$ ms :white_check_mark:  
*Facets: A2, A3*  
*Rationale: The student correctly applies the Central Limit Theorem: with $n = 64$ (large enough), the sampling distribution of $\bar{x}$ is approximately normal regardless of the population's skewed shape. They also correctly identify that the mean of the sampling distribution equals $\mu = 320$ ms and the standard error equals $\sigma/\sqrt{n} = 10$ ms.*

**B.** Strongly right-skewed with mean $320$ ms and standard deviation $\frac{80}{\sqrt{64}} = 10$ ms  
*Facets: B11*  
*Rationale: A student who believes the sampling distribution mirrors the population distribution in shape would choose this option. They correctly compute the standard error but incorrectly believe the sampling distribution inherits the right-skewed shape of the population, reflecting the misconception that a larger sample makes the sampling distribution look more like the population (B11).*

**C.** Approximately normal with mean $320$ ms and standard deviation $80$ ms  
*Facets: A2, B9*  
*Rationale: A student who knows the CLT produces a normal shape (A2) but confuses the standard deviation of the sampling distribution with the population standard deviation $\sigma$ would select this. They fail to divide by $\sqrt{n}$, believing the spread of the sampling distribution is the same as the population spread.*

**D.** Approximately normal with mean $320$ ms and standard deviation $80$ ms, because the population is large  
*Facets: B12*  
*Rationale: A student who believes the sampling distribution is always normal regardless of sample size or population shape (B12) might select this and attribute normality to population size rather than the Central Limit Theorem applying due to sufficient sample size. They also fail to correctly apply the standard error formula.*

**E.** Strongly right-skewed with mean $320$ ms and standard deviation $80$ ms  
*Facets: B9, B11, B12*  
*Rationale: A student who thinks the sampling distribution always mirrors the population distribution in both shape and spread would choose this. They conflate the sampling distribution with the population distribution entirely, showing misconceptions about both the shape (B11) and the spread (B9) of the sampling distribution.*

### Explanation

This item targets four facets. A student who correctly understands the Central Limit Theorem (A2) knows that for a large enough sample ($n = 64$), the sampling distribution of $\bar{x}$ is approximately normal even when the population is strongly right-skewed — the sampling distribution does NOT mirror the population shape. A student who understands (A3) knows the mean of the sampling distribution equals the population mean $\mu = 320$ ms. Distractors expose misconceptions: option B targets B11 (sampling distribution mirrors population shape), option C targets the belief that the SD of the sampling distribution equals the population SD (B9), and option D targets B12 (always normal regardless of conditions). Option E combines B9, B11, and B12 for students with the deepest confusion between population and sampling distributions.

### Judge Report

**Overall agreement:** 3/5 options matched  
**Issues:** The generator erroneously tagged Option E with B12, which contradicts the option's text (B12 asserts the distribution is always normal, while Option E describes it as strongly right-skewed). Options C and D are very similar (both present a normal distribution with mean 320 and SD 80). D merely adds a flawed rationale. This might make the distractor space slightly redundant. The generator missed tagging Option D with B9, despite the option exhibiting the exact same incorrect standard deviation as Option C and Option E.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A2, A3 | A2, A3 | match | 1.0 |
| B | B11 | B11 | match | 0.9 |
| C | A2, B9 | A2, B9 | match | 0.9 |
| D | B12 | B9, B12 | partial | 0.85 |
| E | B9, B11, B12 | B9, B11 | partial | 1.0 |

---

## Item 8

**Target facets:** A4, A6, B15, B17  
**Format:** True False Per Option  

> **Facet selection reasoning:** This combination focuses on the interplay between confidence level interpretation and CI width. A4 (correct interpretation of confidence level as long-run frequency) and A6 (higher confidence level → wider CI) contrast directly with B15 (misinterpreting CI as a probability statement) and B17 (believing higher confidence yields a more precise/shorter interval). Together they form a coherent item that probes whether students understand both what confidence level means AND its directional effect on interval width — a novel pairing not yet used in the batch.

### Stem

A nutritionist is studying daily sugar intake among adults. After collecting a random sample of $n = 50$ adults and measuring their daily sugar intake (in grams), she computes the following 90% confidence interval for the population mean daily sugar intake: $(42.3, 57.7)$ grams.

For each of the following statements about this confidence interval, indicate whether it is **True** or **False**.

### Options

**A.** There is a 90% probability that the true mean daily sugar intake $\mu$ falls between $42.3$ and $57.7$ grams.  
*Facets: B15*  
*Rationale: A student who treats confidence level as a post-hoc probability about a fixed (but unknown) parameter will mark this True. In reality, $\mu$ is a fixed value — it either is or is not in this particular interval. The 90% refers to the long-run behavior of the procedure, not the probability that this specific interval contains $\mu$.*

**B.** If the nutritionist repeated this study many times and constructed a 90% CI each time, about 90% of those intervals would contain the true mean $\mu$. :white_check_mark:  
*Facets: A4*  
*Rationale: This is the correct frequentist interpretation of confidence level: in the long run, 90% of all intervals produced by this procedure will capture the true population mean. A student who understands A4 will recognize this as a valid replication-based interpretation.*

**C.** There is a 90% probability that a randomly selected adult's daily sugar intake falls between $42.3$ and $57.7$ grams.  
*Facets: B15, B16*  
*Rationale: A student confusing confidence level with a probability about individual data values (rather than the population mean) would mark this True. This conflates the CI for a population mean with a prediction interval for individual observations, and also misreads the 90% as a direct probability statement.*

**D.** To obtain a more precise (narrower) interval, the nutritionist should switch to a 95% confidence level while keeping $n = 50$.  
*Facets: A6, B17*  
*Rationale: A student holding the B17 misconception — that higher confidence means more precision — will mark this True. In fact, increasing the confidence level from 90% to 95% requires a larger critical value $z^*$, which widens the interval, not narrows it. This directly contradicts A6, which states that CI width increases with confidence level.*

**E.** To obtain a narrower interval than $(42.3, 57.7)$, the nutritionist could decrease the confidence level to 80% while keeping $n = 50$. :white_check_mark:  
*Facets: A6*  
*Rationale: A student who understands A6 knows that CI width depends on the critical value $z^*$, and a lower confidence level corresponds to a smaller $z^*$, producing a narrower interval. Decreasing from 90% to 80% confidence would indeed yield a shorter interval at the same sample size.*

### Explanation

This item targets four facets. **B15** is probed by option A (and also option C): students who interpret the confidence level as a direct probability that the parameter lies in *this specific* interval hold a common misconception — the 90% is a property of the long-run procedure, not a posterior probability for one realized interval. **A4** is probed by option B, the canonical correct interpretation: about 90% of intervals constructed by replication of this procedure would capture $\mu$. **B16** is probed alongside B15 in option C, where the interval is misread as covering individual observations. **A6** and **B17** are jointly probed by options D and E: option D targets B17 (the false belief that higher confidence = more precision/shorter interval), while option E rewards A6 understanding (that lower confidence level yields a narrower interval via a smaller critical value $z^*$).

### Judge Report

**Overall agreement:** 5/5 options matched  
**Issues:** None  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | B15 | B15 | match | 1.0 |
| B | A4 | A4 | match | 1.0 |
| C | B15, B16 | B15, B16 | match | 1.0 |
| D | A6, B17 | A6, B17 | match | 1.0 |
| E | A6 | A6 | match | 1.0 |

---

## Item 9

**Target facets:** A1, A5, B14, B16  
**Format:** True False Per Option  

> **Facet selection reasoning:** This combination targets two distinct but complementary conceptual areas: (1) how sample size affects the sampling distribution (A1) and the misconception that larger samples guarantee a closer sample mean (B14, confusing probabilistic improvement with certainty), and (2) the purpose of a CI to estimate population parameters (A5) versus the misconception that CIs estimate sample statistics (B16). Together these facets support an item stem about a researcher collecting a large sample and constructing a CI, where distractors can probe whether students think the larger sample guarantees closeness to the mean (B14) or that the CI is about the sample mean itself (B16), while correct reasoning requires understanding both reduced standard error (A1) and the population-parameter focus of CIs (A5). This combination has not been used before and spans both the sampling distribution and CI interpretation domains.

### Stem

A university administrator collects a random sample of $n = 9$ student loan balances and computes a 95% confidence interval of $(\$18{,}400,\ \$23{,}600)$. The administrator then collects a new random sample of $n = 81$ students and computes a 95% confidence interval from this larger sample.

For each of the following statements, decide whether it is **True** or **False**.

### Options

**A.** The 95% confidence interval from the $n = 81$ sample is guaranteed to be closer to the true population mean loan balance than $\$21{,}000$ (the midpoint of the first interval).  
*Facets: B14*  
*Rationale: A student who thinks larger samples guarantee individual sample means land closer to the population mean will mark this True. In fact, due to sampling variability, the new sample mean could fall anywhere — a larger sample reduces the standard error (narrowing the interval) but does not guarantee the specific sample mean is closer to μ.*

**B.** We can be 95% confident that the true mean loan balance of all students at the university is between $\$18{,}400$ and $\$23{,}600$. :white_check_mark:  
*Facets: A5*  
*Rationale: This is the correct interpretation of the confidence interval: it targets the unknown population parameter (true mean for all students), not the sample. A student who understands A5 will correctly mark this True.*

**C.** The confidence interval $(\$18{,}400,\ \$23{,}600)$ tells us that 95% of the students in the original sample of $n = 9$ have loan balances between $\$18{,}400$ and $\$23{,}600$.  
*Facets: B16*  
*Rationale: A student who believes the CI describes or estimates individual data values or the sample itself (rather than the population parameter) will mark this True. The CI is not about where individual observations fall; it is about capturing the population mean.*

**D.** The confidence interval computed from the $n = 81$ sample will be narrower than the interval $(\$18{,}400,\ \$23{,}600)$ from the $n = 9$ sample, because the larger sample produces a smaller standard error. :white_check_mark:  
*Facets: A1, A5*  
*Rationale: A student who understands A1 (larger $n$ → smaller standard error → narrower CI) will correctly mark this True. The standard error $SE = \frac{\sigma}{\sqrt{n}}$ decreases as $n$ increases from 9 to 81 (by a factor of 3), so the margin of error shrinks and the CI narrows. This also reinforces A5 because the CI width is about estimating the population parameter more precisely.*

**E.** The sample mean from the $n = 81$ sample will definitely be closer to the true population mean than $\$21{,}000$ was from the $n = 9$ sample.  
*Facets: B14*  
*Rationale: This again targets the B14 misconception: the belief that a larger sample size guarantees the specific sample mean will be closer to μ. While larger samples tend to produce sample means that are closer to μ on average (smaller SE), no individual sample mean is guaranteed to be closer. There is always random variability in any one sample.*

### Explanation

This item diagnoses four facets through a concrete CI scenario. **A1** is probed by option D: students must recognize that increasing $n$ from 9 to 81 reduces the standard error by a factor of $\sqrt{81}/\sqrt{9} = 3$, making the interval narrower — not because we're guaranteed a better point estimate, but because the sampling distribution is more tightly packed. **A5** is probed by options B and D: the correct interpretation of a CI targets the population parameter (true mean for all students), not the sample itself. **B14** is probed by options A and E: students with this misconception believe larger samples guarantee that the specific observed sample mean will be numerically closer to μ, confusing the reduction in standard error (a distributional property) with a deterministic guarantee about any one sample. **B16** is probed by option C: students with this misconception misread the CI as describing the distribution of individual data values in the sample rather than as an estimate of the population mean.

### Judge Report

**Overall agreement:** 4/5 options matched  
**Issues:** Options A and E test the exact same misconception (B14) using highly similar logic. Option A's phrasing ('The 95% confidence interval... is guaranteed to be closer... than $21,000') is somewhat nonsensical because comparing the 'distance' of an entire interval to a point estimate is vague. Option E is much clearer and correctly references the sample mean. Option A should be revised to target a different facet or removed to avoid redundancy. The generator missed tagging A7 on Option D, which directly addresses the relationship between CI width and standard error.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | B14 | B14 | match | 0.9 |
| B | A5 | A5 | match | 1.0 |
| C | B16 | B16 | match | 1.0 |
| D | A1, A5 | A1, A7 | partial | 0.9 |
| E | B14 | B14 | match | 1.0 |

---

## Item 10

**Target facets:** A2, A3, B9, B13  
**Format:** Single Select  

> **Facet selection reasoning:** This combination targets two distinct but related misconceptions about sampling distributions: B9 (that the sampling distribution mirrors the population distribution, implying its shape and spread are unchanged) and B13 (that the mean of the sampling distribution depends on sample size). These are contrasted against the correct understandings A2 (sampling distribution approaches normality as n increases, regardless of population shape) and A3 (the mean of the sampling distribution equals the population mean, independent of n). This pairing is coherent because both misconceptions stem from confusion about what properties of the sampling distribution are influenced by sample size versus what remains fixed. This combination is novel — while A2, A3, B9, and B13 have appeared individually in prior items, this exact grouping has not been used, and the specific contrast of 'what changes vs. what stays constant in the sampling distribution as n grows' has not been the central diagnostic focus of any prior item.

### Stem

A researcher studies the annual income of adults in a city. The population distribution of income is right-skewed with a mean of $\mu = \$52{,}000$ and a standard deviation of $\sigma = \$15{,}000$. A random sample of $n = 100$ adults is drawn.

What is the sampling distribution of the sample mean $\bar{x}$?

### Options

**A.** Right-skewed with mean $\$52{,}000$ and standard deviation $\$15{,}000$  
*Facets: B9*  
*Rationale: A student who believes the sampling distribution mirrors the population distribution would choose a right-skewed shape and keep the standard deviation the same as the population's $\sigma$, ignoring both the Central Limit Theorem and the effect of sample size on standard error.*

**B.** Right-skewed with mean $\$52{,}000$ and standard deviation $\dfrac{\$15{,}000}{\sqrt{100}}$  
*Facets: B9*  
*Rationale: A student who correctly applies the standard error formula but still believes the sampling distribution mirrors the population's shape (right-skewed) would select this option. They understand that $SE = \sigma/\sqrt{n}$ but have not grasped that the CLT produces a normal sampling distribution regardless of population shape.*

**C.** Approximately normal with mean $\dfrac{\$52{,}000}{\sqrt{100}}$ and standard deviation $\dfrac{\$15{,}000}{\sqrt{100}}$  
*Facets: B13*  
*Rationale: A student who mistakenly believes that the mean of the sampling distribution depends on (and is divided by) the sample size would select this option. They correctly apply the standard error formula but incorrectly scale the mean by $\sqrt{n}$ as well, revealing the B13 misconception.*

**D.** Approximately normal with mean $\$52{,}000$ and standard deviation $\dfrac{\$15{,}000}{\sqrt{100}}$ :white_check_mark:  
*Facets: A2, A3*  
*Rationale: A student with correct understanding selects this option. By the Central Limit Theorem, with $n = 100 \geq 30$, the sampling distribution of $\bar{x}$ is approximately normal regardless of the right-skewed population shape (A2). The mean of the sampling distribution equals the population mean $\mu = \$52{,}000$ (A3), and the standard deviation is $SE = \sigma/\sqrt{n} = \$15{,}000/\sqrt{100} = \$1{,}500$.*

### Explanation

This item targets four facets. **A2** (the sampling distribution approaches normality with large $n$, not the population shape): the correct answer is approximately normal even though the population is right-skewed, while options A and B trap students who believe the sampling distribution inherits the population's skewed shape (B9). **A3** (the mean of the sampling distribution equals $\mu$): the correct answer keeps the mean at $\$52{,}000$, while option C reveals the B13 misconception by dividing the mean by $\sqrt{n}$. **B9** is probed by options A (wrong shape AND wrong SE) and B (wrong shape but correct SE). **B13** is probed by option C, where a student incorrectly treats both the mean and the standard deviation as divided by $\sqrt{n}$.

### Judge Report

**Overall agreement:** 4/4 options matched  
**Issues:** The facet B9 contains two interconnected misconceptions (mirrored shape and mirrored standard deviation). Option B assesses the mirrored shape but not the mirrored standard deviation. This makes B9 slightly overloaded as a single facet, but the tagging is still accurate under the current facet map. The item topic is labeled as 'confidence_intervals', but the item solely assesses 'sampling distributions'. While sampling distributions are foundational to confidence intervals, this item does not explicitly cover any CI-specific concepts.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | B9 | B9 | match | 1.0 |
| B | B9 | B9 | match | 0.9 |
| C | B13 | B13 | match | 1.0 |
| D | A2, A3 | A2, A3 | match | 1.0 |

---
