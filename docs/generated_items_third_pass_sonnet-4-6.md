# Generated Items — Third Pass (V2 Prompt, Claude Sonnet 4.6, Dynamic Format)

**Generator model:** Claude Sonnet 4.6  
**Judge model:** Gemini 3.1 Pro Preview  
**Topic:** Confidence Intervals  
**Items:** 10  
**Prompt version:** V2 (latent-facet design)  
**Format:** Dynamic (model chooses)  

---

## Item 1

**Target facets:** A6, A7, B17  
**Format:** Single Select  

> **Facet selection reasoning:** These three facets form a coherent cluster around CI width and precision. A6 addresses the correct understanding that higher confidence levels produce wider intervals, A7 addresses the correct understanding that larger standard errors also produce wider intervals, and B17 captures the common misconception that higher confidence yields a more precise (narrower) interval. A single item stem—such as asking students to compare interval widths under varying confidence levels and sample sizes—can naturally distinguish students who hold the misconception (B17) from those who correctly understand the directional relationships (A6, A7). This combination is novel in that B17 is directly contradicted by A6, making the distractor logic tight and diagnostically powerful, while A7 adds a second dimension that further separates nuanced understanding from surface-level guessing.

### Stem

A market researcher constructs a 90% confidence interval for the average monthly spending of customers and gets an interval of ($312, $388). She wants to redesign the study to get a narrower confidence interval. She is considering two changes:

1. Switch from a 90% to a 99% confidence level
2. Increase the sample size from n = 40 to n = 160

Which combination of changes will actually produce a narrower interval?

### Options

**A.** Make both changes: use the 99% confidence level and increase n to 160.  
*Facets: A1, A7, B17*  
*Rationale: A student who holds misconception B17 (higher confidence = more precise = shorter interval) would think that switching to 99% confidence narrows the interval. Combined with the correct belief that larger n helps, they would select both changes, not realizing the higher confidence level actually widens the interval and partially or fully offsets the gain from larger n.*

**B.** Make only Change 1: switch to the 99% confidence level, and keep n = 40.  
*Facets: B17*  
*Rationale: A student who only holds misconception B17 would think that higher confidence yields a more precise (shorter) interval and would believe switching to 99% alone is sufficient. This reveals a pure B17 misconception without any correct understanding of sample size effects.*

**C.** Make only Change 2: keep the 90% confidence level and increase n to 160. :white_check_mark:  
*Facets: A6, A7*  
*Rationale: A student who correctly understands A6 (higher confidence level widens the interval) and A7 (larger sample size reduces standard error and narrows the interval) knows that switching to 99% would widen the interval, and that increasing n shrinks the standard error and thus the interval. Keeping the 90% level and increasing n is the only change that guarantees a narrower interval.*

**D.** Make neither change; the interval width is fixed once the data are collected.  
*Facets: A6, A7*  
*Rationale: A student who does not understand the relationship between confidence level, sample size, and CI width might believe the interval cannot be changed by study design choices. This reveals a lack of understanding of both A6 and A7.*

### Explanation

This item targets three facets. A6 states that CI width increases as confidence level increases — switching from 90% to 99% would make the interval wider, not narrower. A7 states that CI width increases when standard error increases (and decreases when standard error decreases) — increasing n from 40 to 160 cuts the standard error in half (SE ∝ 1/√n), which narrows the interval. B17 is the misconception that higher confidence produces a shorter, more precise interval. The only correct strategy is to keep the lower (90%) confidence level and increase the sample size, combining a correct understanding of both A6 and A7. Students selecting option A or B are revealing misconception B17; students selecting option D lack understanding of both A6 and A7.

### Judge Report

**Overall agreement:** 2/4 options matched  
**Issues:** Tagging incorrect options with goal facets to indicate a 'lack of understanding' (as done in Option D) is a poor psychometric practice. Options should be tagged with the facets they actually exhibit (whether goal facets for partial correctness or problematic facets for misconceptions). Option D should be left untagged or mapped to a new misconception facet.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A1, A7, B17 | A1, A7, B17 | match | 0.9 |
| B | B17 | B17 | match | 1.0 |
| C | A6, A7 | A1, A6, A7 | partial | 0.9 |
| D | A6, A7 |  | mismatch | 0.95 |

---

## Item 2

**Target facets:** A4, A5, B15, B16  
**Format:** True False Per Option  

> **Facet selection reasoning:** This combination targets the interpretation of confidence intervals, which is distinct from the previously used Item 1 (which focused on CI width). A4 and A5 represent correct understanding: A4 captures the frequentist replication interpretation of confidence level, and A5 clarifies that CIs estimate population parameters. B15 and B16 represent two common and conceptually related misconceptions — that CIs express probability of capturing the true mean for a single interval (B15), and that CIs estimate sample statistics or sample data rather than population parameters (B16). Together these four facets allow a single item stem to probe whether students correctly understand both what a CI is estimating (population parameter, not sample statistic) and what the confidence level means (long-run frequency, not single-interval probability), making for a rich diagnostic that distinguishes nuanced misunderstandings from correct understanding.

### Stem

A nutritionist surveys a random sample of 50 adults and constructs a 90% confidence interval for the mean daily sugar intake (in grams) of all adults in the city. The resulting interval is (48.3, 61.7) grams.

For each statement below, decide whether it is True or False.

### Options

**A.** We are 90% confident that the true mean daily sugar intake of all adults in the city is between 48.3 and 61.7 grams. :white_check_mark:  
*Facets: A4, A5*  
*Rationale: A student who understands that a CI is designed to capture the true population parameter (A5) and that the confidence level refers to long-run reliability of the procedure (A4) will correctly identify this as the valid interpretation.*

**B.** There is a 90% probability that the true mean daily sugar intake of all adults in the city is between 48.3 and 61.7 grams.  
*Facets: A5, B15*  
*Rationale: A student who conflates confidence level with the probability that this specific interval contains the parameter (B15) will mistakenly call this true. The population mean is fixed; the interval either contains it or it does not. The 90% refers to the procedure across repeated samples, not to a probability statement about this one interval.*

**C.** 90% of all adults in the city consume between 48.3 and 61.7 grams of sugar per day.  
*Facets: B15, B16*  
*Rationale: A student who thinks the CI describes individual data values rather than the population mean (B16) and who misinterprets the confidence level as a proportion of individuals (B15) would incorrectly mark this as true. The CI estimates where the population mean lies, not the distribution of individual values.*

**D.** We are 90% confident that the mean daily sugar intake of the 50 adults in the sample is between 48.3 and 61.7 grams.  
*Facets: A4, B16*  
*Rationale: A student who believes the CI is estimating the sample mean rather than the population mean (B16) might accept this statement. However, the sample mean is already known and fixed (it is the center of the interval, approximately 55 g); the CI is constructed to estimate the unknown population mean, not the sample statistic.*

**E.** If this procedure were repeated many times with new samples of 50 adults each, approximately 90% of the resulting confidence intervals would contain the true mean daily sugar intake. :white_check_mark:  
*Facets: A4, A5*  
*Rationale: A student who correctly understands confidence level as referring to long-run behavior across repeated replications (A4) and knows the CI targets the true population parameter (A5) will recognize this as an accurate interpretation of what 90% confidence means.*

### Explanation

This item targets four facets. Options A and E are correct because they reflect the proper interpretation of a confidence interval: the confidence level describes the long-run proportion of intervals (from repeated sampling) that would capture the true population mean (A4), and the interval is designed to estimate that population parameter, not sample statistics or individual values (A5). Option B is incorrect because it assigns a post-hoc probability to a single, already-constructed interval — the 90% is a property of the procedure, not of any one interval (B15). Option C is incorrect because it applies the interval to individual data points rather than the population mean, confusing what the CI estimates (B16) and misreading the confidence level as describing individuals (B15). Option D is incorrect because the sample mean is already known; confidence intervals estimate the unknown population parameter, not sample statistics (B16).

### Judge Report

**Overall agreement:** 1/5 options matched  
**Issues:** The item itself is very well-constructed and effectively distinguishes between the correct frequentist interpretation, the colloquial interpretation, and common misconceptions (probability, individual data proportions, and sample statistics).  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A4, A5 | A5 | partial | 0.9 |
| B | A5, B15 | B15 | partial | 0.95 |
| C | B15, B16 | B16 | partial | 0.85 |
| D | A4, B16 | B16 | partial | 0.9 |
| E | A4, A5 | A4, A5 | match | 1.0 |

---

## Item 3

**Target facets:** A1, A2, B9, B10  
**Format:** Single Select  

> **Facet selection reasoning:** These facets cluster around how sample size affects the shape and spread of the sampling distribution. A1 (larger n → smaller SE, more packed distribution) and A2 (larger n → closer to normal, not mirroring population) are the correct understandings to reinforce, while B9 (sampling distribution mirrors population distribution, so spread stays constant) and B10 (larger n → more spread out) are the two most common opposing misconceptions. Together they allow a single item stem — e.g., asking what happens to the sampling distribution as n increases — to naturally distinguish all four facets. This combination has not been used in prior items and complements the previously covered topics of CI width/confidence level and CI interpretation.

### Stem

A large urban hospital records that the length of patient stays is right-skewed, with a mean of 4.5 days and a standard deviation of 3.2 days. A researcher first takes random samples of size n = 10 and records the sample means, then repeats the process with random samples of size n = 100.

Compared to the sampling distribution of x̄ when n = 10, what is true about the sampling distribution of x̄ when n = 100?

### Options

**A.** It will be more spread out (larger standard error) and will more closely resemble the right-skewed population distribution.  
*Facets: B10, B11*  
*Rationale: A student who believes larger samples produce more spread in the sampling distribution (B10) and that the sampling distribution converges toward the population shape rather than normality (B11) would select this option. Both parts of this answer reflect misconceptions.*

**B.** It will be more tightly packed (smaller standard error) and will more closely resemble the right-skewed population distribution.  
*Facets: A1, B11*  
*Rationale: A student who correctly understands that larger n reduces the standard error (A1) but incorrectly believes the sampling distribution moves toward the population distribution shape rather than toward normality (B11) would choose this. It gets the spread right but gets the shape wrong.*

**C.** It will be more spread out (larger standard error) and will look more like a normal distribution.  
*Facets: B9, B10*  
*Rationale: A student who thinks larger samples cause the sampling distribution to spread out more (B10) but also recognizes (perhaps via rote memorization of CLT) that normality is involved might pick this. Alternatively, a student confusing sampling distribution spread with population spread (B9) would be drawn here.*

**D.** It will be more tightly packed (smaller standard error) and will look more like a normal distribution. :white_check_mark:  
*Facets: A1, A2*  
*Rationale: This is the correct answer. As n increases from 10 to 100, the standard error shrinks (SE = 3.2/√n), so the sampling distribution becomes more concentrated around the mean (A1). Additionally, by the Central Limit Theorem, the sampling distribution of x̄ approaches normality regardless of the right-skewed population shape (A2). A student who understands both principles arrives here.*

### Explanation

This item targets four facets simultaneously through a single concrete comparison. Facet A1 concerns how increasing sample size reduces the standard error (SE = σ/√n), making the sampling distribution more tightly concentrated — the SE drops from 3.2/√10 ≈ 1.01 to 3.2/√100 = 0.32. Facet A2 concerns how the sampling distribution approaches normality as n grows, regardless of the population's right-skewed shape — this is the Central Limit Theorem. Misconception B9 is that the sampling distribution mirrors the population distribution (same SD, same shape), so students holding this belief would expect the spread to stay the same or expect right-skewedness to persist. Misconception B10 is that larger samples produce more spread in the sampling distribution (confusing sample variability with standard error behavior). Options A, B, and C each combine one correct and one incorrect element or two incorrect elements, so only students who correctly understand both A1 and A2 can identify option D.

### Judge Report

**Overall agreement:** 3/4 options matched  
**Issues:** The generator's tag for Option C includes B9, which is a mismatch. B9 corresponds to the belief that the sampling distribution mirrors the population distribution. Because the population is right-skewed, choosing 'will look more like a normal distribution' explicitly contradicts B9 and correctly exhibits A2.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | B10, B11 | B10, B11 | match | 1.0 |
| B | A1, B11 | A1, B11 | match | 1.0 |
| C | B9, B10 | A2, B10 | partial | 0.95 |
| D | A1, A2 | A1, A2 | match | 1.0 |

---

## Item 4

**Target facets:** A3, A4, B13, B15  
**Format:** True False Per Option  

> **Facet selection reasoning:** These facets form a coherent cluster around the sampling distribution mean and confidence interval interpretation. A3 (mean of sampling distribution equals population mean) pairs naturally with B13 (misconception that the mean of the sampling distribution depends on sample size), probing whether students understand that the center of the sampling distribution is fixed at the population mean regardless of n. Layering in A4 (correct interpretation of confidence level as percentage of replications) and B15 (misconception that CI is a probability statement about including the true mean for a particular interval) creates a rich item that distinguishes correct frequentist interpretation from probabilistic misreading. This combination has not been used before and covers under-addressed facets around sampling distribution center and CI probability language.

### Stem

A researcher collects a random sample of 64 college students and measures their daily screen time. The population mean daily screen time is 6.5 hours with a standard deviation of 2.4 hours. The researcher constructs a 95% confidence interval and obtains (5.91, 7.09).

For each of the following statements, indicate whether it is TRUE or FALSE.

### Options

**A.** The mean of the sampling distribution of the sample mean is 6.5 hours, regardless of sample size. :white_check_mark:  
*Facets: A3*  
*Rationale: A student who correctly understands that the mean of the sampling distribution always equals the population mean (μ = 6.5) — and importantly, that this is not affected by sample size — will mark this TRUE. This directly targets A3.*

**B.** The mean of the sampling distribution would be larger if the researcher had used a sample of 256 students instead of 64.  
*Facets: B13*  
*Rationale: A student holding the B13 misconception believes the mean of the sampling distribution depends on sample size. They would mark this TRUE (incorrectly), thinking a larger n shifts the center of the sampling distribution upward.*

**C.** There is a 95% probability that the population mean daily screen time falls between 5.91 and 7.09 hours.  
*Facets: A5, B15*  
*Rationale: A student with the B15 misconception treats confidence level as a probability statement about a single fixed interval capturing the population mean. Because μ is a fixed (non-random) value, it either is or is not in this interval — the 95% refers to the long-run procedure, not a probability for this particular interval.*

**D.** If the researcher repeated this study many times and constructed a 95% CI each time, about 95% of those intervals would contain the true population mean of 6.5 hours. :white_check_mark:  
*Facets: A4, A5*  
*Rationale: A student who correctly understands confidence level as a long-run frequency property of the procedure — that 95% of intervals constructed this way would capture the true population mean — will mark this TRUE. This targets A4 directly.*

**E.** There is a 95% probability that the sample mean from a future sample falls between 5.91 and 7.09 hours.  
*Facets: A4, B15, B16*  
*Rationale: A student with B15 and B16 misconceptions might confuse the CI as a probability statement about future sample means rather than a long-run property of the procedure capturing the fixed population parameter. The CI is about the population mean, not future sample statistics.*

### Explanation

This item targets four facets. Option A (TRUE) diagnoses A3: the mean of the sampling distribution always equals the population mean regardless of sample size. Option B (FALSE) is the trap for B13: students who think the center of the sampling distribution shifts with sample size will incorrectly mark it TRUE — in reality, only the standard error changes with n, not the mean. Option C (FALSE) targets B15: the 95% confidence level is not a probability that this specific, already-computed interval contains the fixed population mean; it is a property of the repeated procedure. Option D (TRUE) correctly captures A4 by framing confidence level as a long-run frequency over many repetitions of the procedure. Option E (FALSE) combines B15 and B16: the CI does not describe a probability about future sample means, but rather about the fixed population parameter captured by the long-run procedure.

### Judge Report

**Overall agreement:** 3/5 options matched  
**Issues:** The stem explicitly states the population mean is known ('The population mean daily screen time is 6.5 hours...'). This creates a significant conceptual issue because confidence intervals are used to estimate unknown population parameters. Constructing a CI when the population mean is already known is pedagogically confusing and contradicts the fundamental purpose of inferential statistics.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A3 | A3 | match | 1.0 |
| B | B13 | B13 | match | 1.0 |
| C | A5, B15 | B15 | partial | 0.9 |
| D | A4, A5 | A4, A5 | match | 0.95 |
| E | A4, B15, B16 | B15, B16 | partial | 0.95 |

---

## Item 5

**Target facets:** A5, A6, B16, B17  
**Format:** True False Per Option  

> **Facet selection reasoning:** This combination targets a coherent cluster around what a confidence interval estimates and how confidence level affects its width. A5 (CI captures population parameter) and B16 (misconception that CI estimates sample statistics) probe whether students correctly identify the target of inference. A6 (higher confidence → wider interval) and B17 (misconception that higher confidence → shorter/more precise interval) probe whether students understand the trade-off between confidence level and precision. Together these facets allow a single item stem—e.g., comparing two CIs at different confidence levels—to simultaneously reveal whether students know what is being estimated and whether they correctly reason about the direction of width change. This combination differs from all previously used sets and covers the under-used pairing of B16 with B17.

### Stem

A researcher calculates a 90% confidence interval for the average commute time (in minutes) of city employees and obtains (22.4, 31.6). She wants a shorter confidence interval. A colleague suggests: 

### Options

**A.** The interval (22.4, 31.6) estimates the true average commute time of all city employees. :white_check_mark:  
*Facets: A5*  
*Rationale: A student who understands that a CI is designed to capture the true population parameter (not sample statistics) will correctly identify this as true.*

**B.** The interval (22.4, 31.6) estimates the average commute time of the employees in the sample.  
*Facets: B16*  
*Rationale: A student who confuses the target of a CI — thinking it estimates the sample mean rather than the population mean — would incorrectly mark this as true.*

**C.** Switching to a 99% confidence level will produce a shorter interval.  
*Facets: B17, A6*  
*Rationale: A student holding the misconception that higher confidence yields a more precise (shorter) interval would mark this true. In reality, a higher confidence level requires a larger critical value, which widens the interval.*

**D.** Switching to an 80% confidence level will produce a shorter interval. :white_check_mark:  
*Facets: A6*  
*Rationale: A student who correctly understands the relationship between confidence level and CI width knows that decreasing the confidence level reduces the critical value and therefore narrows the interval.*

**E.** The interval (22.4, 31.6) tells us that 90% of city employees have commute times between 22.4 and 31.6 minutes.  
*Facets: B16*  
*Rationale: A student who thinks the CI describes the distribution of individual sample data (rather than estimating the population mean) would incorrectly mark this as true.*

### Explanation

This item targets four facets. Options A and B together probe whether students understand that a CI estimates a population parameter (A5) versus a sample statistic (B16): option A is the correct target of the CI, while option B misidentifies the sample mean as the target, and option E misidentifies individual data values as the target. Options C and D together probe the relationship between confidence level and interval width (A6) versus the misconception that higher confidence yields a shorter interval (B17): option C reflects the B17 misconception (increasing confidence shortens the interval), while option D correctly applies A6 (decreasing confidence level narrows the interval).

### Judge Report

**Overall agreement:** 5/5 options matched  
**Issues:** The stem ends with 'A colleague suggests:', which only makes grammatical and logical sense for options C and D. Options A, B, and E are statements about interpreting the existing interval, not suggestions for how to get a shorter one. The stem needs to be revised to remove 'A colleague suggests:' or the item should be split into two separate questions (one about interpreting the interval, one about changing its width).  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A5 | A5 | match | 1.0 |
| B | B16 | B16 | match | 1.0 |
| C | B17, A6 | A6, B17 | match | 1.0 |
| D | A6 | A6 | match | 1.0 |
| E | B16 | B16 | match | 0.9 |

---

## Item 6

**Target facets:** A1, A7, B8, B11  
**Format:** Single Select  

> **Facet selection reasoning:** This combination targets the relationship between sample size, standard error, and CI width through the lens of misconceptions about what a sampling distribution actually represents. A1 (larger sample → smaller SE) and A7 (CI width increases with larger SE) form the correct conceptual chain. B8 (confusing sampling distribution with a single dataset's distribution) and B11 (thinking larger samples make the sampling distribution look more like the population) are related misconceptions that would lead students astray when reasoning about how increasing sample size affects the spread of the sampling distribution and consequently CI width. This combination has not been used before and covers under-represented facets B8 and B11 while reinforcing the SE-to-CI-width link from a different angle than Items 1 and 3.

### Stem

A researcher collects a random sample of n = 100 households and measures the number of streaming services each household subscribes to. The population distribution of streaming service subscriptions is right-skewed with mean 3.2 and standard deviation 2.4. The researcher constructs a 95% confidence interval and finds it to be (2.73, 3.67).

The researcher wants a narrower confidence interval. A colleague suggests: 'Just increase your sample size to n = 400. That will shrink the interval.'

Which of the following best explains why increasing the sample size to n = 400 would produce a narrower confidence interval?

### Options

**A.** Because with n = 400, the sampling distribution will look more like the right-skewed population distribution, reducing uncertainty about the population shape and therefore narrowing the interval.  
*Facets: B11*  
*Rationale: A student who thinks that increasing sample size brings the sampling distribution closer to the population distribution (rather than closer to normal) would select this. This also misidentifies the mechanism for CI width reduction.*

**B.** Because with n = 400, the sampling distribution is built from the larger dataset itself, so the spread of scores in that single sample better represents the population, narrowing the interval.  
*Facets: B8*  
*Rationale: A student who confuses the sampling distribution with the sample distribution — thinking the sampling distribution is derived from one dataset rather than from repeated sampling — would select this explanation.*

**C.** Because with n = 400, the standard error (2.4/√400 = 0.12) is smaller than with n = 100 (2.4/√100 = 0.24), which directly reduces the width of the confidence interval. :white_check_mark:  
*Facets: A1, A7*  
*Rationale: A student who correctly understands that larger sample size reduces the standard error (A1), and that a smaller standard error leads to a narrower confidence interval (A7), will select this. The specific numerical calculation makes the mechanism concrete and verifiable.*

**D.** Because with n = 400, each individual observation is measured more precisely, so the standard deviation of the population decreases from 2.4 to 2.4/√4 = 1.2, which narrows the interval.  
*Facets: B9, B11*  
*Rationale: A student who conflates the population standard deviation with the standard error, or believes that sampling more changes the population distribution itself, would select this. It reflects confusion about what changes versus what stays fixed when sample size increases.*

### Explanation

The correct answer (C) requires understanding two linked ideas: (A1) increasing sample size shrinks the standard error because SE = σ/√n, and (A7) a smaller standard error directly produces a narrower confidence interval since CI width = 2 × z* × SE. Distractor A targets B11 — the misconception that larger samples make the sampling distribution look more like the population distribution, confusing the direction of the Central Limit Theorem effect. Distractor B targets B8 — the misconception that the sampling distribution is derived from a single dataset, conflating sample distribution with sampling distribution. Distractor D targets B9 and B11 by suggesting the population standard deviation itself changes with sample size, reflecting confusion between population parameters (fixed) and sampling distribution properties (variable with n). The concrete numerical values in option C (SE dropping from 0.24 to 0.12) make the correct mechanism explicit while the distractors offer plausible-sounding but conceptually flawed explanations that real students with these misconceptions would find compelling.

### Judge Report

**Overall agreement:** 3/4 options matched  
**Issues:** Options C and D contain mathematical formulas and calculations, while Options A and B are purely conceptual. This formatting difference could cue test-takers to focus only on the options with math. Option D is an excellent distractor conceptually, but it stretches the definition of B9 slightly. B9 explicitly lists the misconception that the sampling distribution's standard deviation stays the same (mirroring the population), whereas Option D suggests the population standard deviation changes (mirroring the sampling distribution's SE). While both are confusions between the two distributions, an explicit facet for 'applying SE properties to population parameters' might be useful.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | B11 | B11 | match | 1.0 |
| B | B8 | B8 | match | 1.0 |
| C | A1, A7 | A1, A7 | match | 1.0 |
| D | B9, B11 | B9 | partial | 0.9 |

---

## Item 7

**Target facets:** A2, A3, B11, B12  
**Format:** Single Select  

> **Facet selection reasoning:** This combination focuses on the shape and center of the sampling distribution. A2 (sampling distribution approaches normal, not population shape) and A3 (mean of sampling distribution equals population mean) represent correct understanding, while B11 (sampling distribution mirrors population distribution as n increases) and B12 (sampling distribution is always normal regardless of n or population shape) are complementary misconceptions about the CLT. Together they probe whether students understand both what changes (shape converges to normal) and what stays constant (mean equals population mean) as sample size grows, without duplicating any previously used combination.

### Stem

A population of customer wait times at a call center is strongly right-skewed with a mean of 8 minutes and a standard deviation of 6 minutes. A researcher takes repeated random samples of size n = 50 and records the sample mean each time.

What is the sampling distribution of the sample mean?

### Options

**A.** Right-skewed with mean 8 and standard deviation 6  
*Facets: B9, B11*  
*Rationale: A student who selects this believes the sampling distribution mirrors the population distribution — it is right-skewed like the population and has the same standard deviation. This reflects the misconception that the sampling distribution looks like or approaches the population distribution (B11) and that the SD remains the same as the population (B9).*

**B.** Right-skewed with mean 8 and standard deviation 6/√50  
*Facets: B11*  
*Rationale: A student who selects this correctly applies the standard error formula but still believes the shape of the sampling distribution mirrors the population (right-skewed). This isolates the B11 misconception — thinking the sampling distribution approaches the population distribution shape — while showing partial knowledge of the standard error.*

**C.** Approximately normal with mean 8 and standard deviation 6/√50 :white_check_mark:  
*Facets: A1, A2, A3*  
*Rationale: By the Central Limit Theorem, with n = 50 (a sufficiently large sample), the sampling distribution of the sample mean is approximately normal regardless of the population's right-skewed shape. The mean equals the population mean (8) and the standard error is 6/√50. This reflects correct understanding of CLT (A2) and the mean of the sampling distribution (A3).*

**D.** Exactly normal with mean 8 and standard deviation 6/√50 for any sample size  
*Facets: B12*  
*Rationale: A student who selects this believes the sampling distribution of the sample mean is always exactly normal regardless of sample size or population shape. The word 'exactly' and 'any sample size' reveal the B12 misconception — that normality of the sampling distribution is guaranteed regardless of conditions, when in fact it is only an approximation that improves with larger n.*

### Explanation

This item probes four facets. The correct answer (C) requires understanding that the Central Limit Theorem causes the sampling distribution to become approximately normal for large n even when the population is strongly skewed (A2), and that the mean of the sampling distribution equals the population mean of 8 (A3). Distractor A targets students who think the sampling distribution inherits the shape and spread of the population (B11, B9). Distractor B isolates students who know the standard error formula but still believe the shape mirrors the skewed population (B11). Distractor D targets students who think the sampling distribution is always exactly normal regardless of sample size or population shape (B12) — the key error being that normality requires sufficiently large n and is an approximation, not a guaranteed exact result.

### Judge Report

**Overall agreement:** 4/4 options matched  
**Issues:** The item is generally excellent and tests the facets well. One minor nuance is that facet A1 explicitly mentions 'as sample size increases', while the item provides a single fixed sample size (n=50); however, applying the standard error formula correctly is sufficient evidence of understanding the SE relationship.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | B9, B11 | B9, B11 | match | 1.0 |
| B | B11 | B11 | match | 0.9 |
| C | A1, A2, A3 | A1, A2, A3 | match | 1.0 |
| D | B12 | B12 | match | 1.0 |

---

## Item 8

**Target facets:** A1, A4, B14, B15  
**Format:** True False Per Option  

> **Facet selection reasoning:** This combination targets two distinct but complementary areas: (1) understanding how sample size affects the sampling distribution (A1) and the misconception that larger samples always yield a sample mean closer to the true mean (B14), and (2) correctly interpreting the confidence level in terms of repeated sampling (A4) versus the common error of treating CI as a probability statement about any particular interval (B15). These facets are conceptually linked because both involve understanding what happens across repeated samples — a core idea in inference — yet span sampling distribution behavior and CI interpretation. This combination has not been used before and covers B14, which has not yet appeared in any prior item.

### Stem

A researcher takes repeated random samples of size n = 4 from a large population and records the sample mean each time. She then repeats the entire process using samples of size n = 64. Consider the following statements about what happens when she switches from n = 4 to n = 64.

For each statement below, decide whether it is True or False.

### Options

**A.** The standard deviation of the sampling distribution of the sample mean will be smaller when n = 64 than when n = 4. :white_check_mark:  
*Facets: A1*  
*Rationale: A student who understands that increasing sample size reduces the standard error (SE = σ/√n) will recognize that going from n=4 to n=64 cuts the standard deviation of the sampling distribution by half (dividing by √64=8 vs. √4=2), making it smaller. This reflects goal facet A1.*

**B.** If she takes a single sample of size n = 64, that sample mean is guaranteed to be closer to the population mean than a single sample mean from n = 4.  
*Facets: B14*  
*Rationale: A student with misconception B14 believes that a larger sample always produces a sample mean that is closer to the population mean. In reality, while larger samples reduce variability on average, any individual sample mean can still land far from the population mean due to random chance. This option is false.*

**C.** There is a 95% probability that the population mean falls inside any particular 95% confidence interval constructed from these samples.  
*Facets: B15*  
*Rationale: A student holding misconception B15 treats the confidence level as the probability that the true population mean is inside a specific, already-constructed interval. In reality, the population mean is fixed; once an interval is constructed, it either contains the mean or it does not. The 95% refers to the long-run proportion of intervals that capture the population mean, not the probability for any single interval.*

**D.** If she constructs 95% confidence intervals from 200 samples of size n = 64, she should expect approximately 190 of those intervals to contain the true population mean. :white_check_mark:  
*Facets: A4*  
*Rationale: A student who correctly interprets confidence level as a long-run frequency (goal facet A4) will recognize that 95% of 200 intervals = 190 intervals are expected to capture the true population mean. This reflects the replication-based meaning of confidence level, not a probability statement about any single interval.*

### Explanation

This item targets four facets. Option A tests A1: students must recognize that larger samples produce a smaller standard error (σ/√n), so the sampling distribution becomes more tightly packed around the population mean. Option B targets misconception B14: although larger samples produce less variable estimates on average, any single sample mean from n=64 can still deviate substantially from the population mean — the guarantee that a larger sample is always closer is false. Option C targets misconception B15: treating a 95% CI as carrying a 95% probability for a specific interval is incorrect; the population mean is a fixed (though unknown) value, and a computed interval either captures it or not. Option D tests A4: confidence level is correctly understood as the long-run proportion of intervals (across many replications) that contain the true population parameter, so about 190 out of 200 intervals are expected to succeed.

### Judge Report

**Overall agreement:** 4/4 options matched  
**Issues:** There is a structural mismatch between the stem and Options C and D. The stem asks students to consider 'what happens when she switches from n = 4 to n = 64', but Options C and D do not address this change; they are standalone statements about confidence intervals.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A1 | A1 | match | 1.0 |
| B | B14 | B14 | match | 1.0 |
| C | B15 | B15 | match | 1.0 |
| D | A4 | A4 | match | 1.0 |

---

## Item 9

**Target facets:** A2, A6, B12, B17  
**Format:** True False Per Option  

> **Facet selection reasoning:** This combination targets two distinct but related conceptual areas: (1) the shape of the sampling distribution and its dependence on sample size (A2 vs. B12 — students should know CLT requires sufficient n, not that normality is guaranteed regardless), and (2) the relationship between confidence level and CI width (A6 vs. B17 — students should know higher confidence yields a wider, less precise interval, not a shorter one). These facets are conceptually coherent because both involve understanding how increasing a quantity (sample size or confidence level) affects a distribution property, making it natural to craft a stem that probes both misconceptions. This combination has not been used before and complements prior items by pairing the CLT/normality misconception with the CI width misconception in a novel pairing.

### Stem

A researcher collects a sample of n = 10 from a heavily right-skewed population (e.g., household incomes) and computes a 90% confidence interval for the mean. Later, she collects a much larger sample of n = 200 from the same population and computes a 99% confidence interval. A colleague makes the following claims about these two scenarios. For each claim, indicate whether it is TRUE or FALSE.

### Options

**A.** With n = 200, the sampling distribution of the sample mean will be approximately normal, even though the population is heavily right-skewed. :white_check_mark:  
*Facets: A2*  
*Rationale: A student who understands the Central Limit Theorem correctly knows that with a sufficiently large sample size (n = 200), the sampling distribution of the sample mean approaches normality regardless of the shape of the population distribution. This correctly applies A2.*

**B.** With n = 10, the sampling distribution of the sample mean will also be approximately normal because sample means are always normally distributed.  
*Facets: B12*  
*Rationale: A student holding misconception B12 believes that the sampling distribution of the sample mean is always normal regardless of sample size or population shape. With n = 10 from a heavily skewed population, the CLT has not yet 'kicked in,' so this claim is false.*

**C.** The 99% confidence interval (n = 200) will be wider than the 90% confidence interval (n = 10), solely because a higher confidence level always produces a wider interval no matter what else changes. :white_check_mark:  
*Facets: A6*  
*Rationale: A student who correctly understands A6 knows that a higher confidence level requires a larger critical value, which widens the interval. Although the larger n reduces the standard error (which would narrow the interval), the claim specifically attributes width to the confidence level — which is directionally correct as an isolated effect. This statement is TRUE as a statement about the effect of confidence level alone on CI width.*

**D.** Because the 99% CI reflects greater confidence than the 90% CI, the 99% CI gives a more precise (narrower) estimate of the population mean.  
*Facets: B17*  
*Rationale: A student with misconception B17 conflates higher confidence with greater precision. In reality, increasing the confidence level widens the interval, making it less precise. A student who correctly understands A6 would reject this claim.*

### Explanation

This item probes four facets through a concrete two-scenario setup. Option A targets A2: students must recognize that the CLT guarantees approximate normality of the sampling distribution for large n (n = 200), even when the population is heavily skewed — normality comes from sample size, not population shape. Option B targets B12: students who believe sample means are always normally distributed regardless of n or population shape would incorrectly mark this true; with n = 10 from a skewed population, the CLT does not apply. Option C targets A6: a higher confidence level (99% vs. 90%) requires a larger critical value, directly widening the CI — students must understand this relationship between confidence level and interval width. Option D targets B17: students who think higher confidence yields a more precise (narrower) interval have the relationship backwards; more confidence means a wider, less precise interval.

### Judge Report

**Overall agreement:** 3/4 options matched  
**Issues:** Option C is fundamentally flawed and factually incorrect in its intended key. The generator asserts this claim is TRUE, but mathematically, the 99% CI with n=200 will be significantly NARROWER than the 90% CI with n=10. The reduction in the standard error (divided by approx. 4.47) overwhelmingly outweighs the larger critical value (approx. 2.576 vs 1.645). A high-performing student who understands both A6 and A7 would correctly mark this claim FALSE, thereby being penalized. Option C's phrasing ('solely because... no matter what else changes') asks the student to evaluate a demonstrably false empirical prediction based on a rigid, absolute rule. This creates a confusing paradox for the test-taker.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A2 | A2 | match | 1.0 |
| B | B12 | B12 | match | 1.0 |
| C | A6 | A6, A7 | partial | 0.95 |
| D | B17 | B17 | match | 1.0 |

---

## Item 10

**Target facets:** A3, A7, B13, B9  
**Format:** Single Select  

> **Facet selection reasoning:** This combination focuses on the sampling distribution's mean and spread properties. A3 (mean of sampling distribution equals population mean) and B13 (misconception that the mean depends on sample size) form a natural contrast about what sample size does and does not affect. A7 (CI width increases with larger standard error) and B9 (misconception that sampling distribution mirrors population distribution, so SD stays constant regardless of sample size) extend this into CI implications. Together they create a coherent item around the question of how sample size affects the sampling distribution's center and spread, and downstream effects on CI width — a combination not yet used in the batch.

### Stem

Heights of adult women in the United States are normally distributed with a mean of 64 inches and a standard deviation of 2.5 inches. A researcher takes a random sample of 100 women.

What is the sampling distribution of the sample mean x̄?

### Options

**A.** Normal with mean 64 and standard deviation 2.5  
*Facets: A3, B9*  
*Rationale: A student choosing this believes the sampling distribution has the same standard deviation as the population (B9), even though they correctly identify the mean as 64 (A3). They do not apply the formula SE = σ/√n.*

**B.** Normal with mean 64 and standard deviation 2.5/√100 :white_check_mark:  
*Facets: A3, A7*  
*Rationale: This is correct. The mean of the sampling distribution equals the population mean of 64 (A3), and the standard error is σ/√n = 2.5/10 = 0.25, which correctly reflects how larger sample sizes reduce variability (A7).*

**C.** Normal with mean 64/√100 and standard deviation 2.5/√100  
*Facets: A7, B13*  
*Rationale: A student choosing this correctly reduces the standard deviation by √n (A7) but incorrectly also divides the mean by √n (B13), believing that the mean of the sampling distribution depends on sample size.*

**D.** Normal with mean 64/√100 and standard deviation 2.5  
*Facets: B9, B13*  
*Rationale: A student choosing this holds two misconceptions: they believe the mean of the sampling distribution changes with sample size (B13) by dividing by √n, and they retain the population standard deviation unchanged (B9), not recognizing that standard error decreases with larger samples.*

### Explanation

This item probes four facets through a concrete numerical scenario. The correct answer (B) requires knowing that the mean of the sampling distribution equals the population mean (A3) and that the standard error is σ/√n, reflecting how larger samples reduce spread (A7). Option A isolates the B9 misconception: the student knows the mean is correct but thinks the spread of the sampling distribution is the same as the population's SD. Option C isolates B13: the student applies the √n reduction correctly to SD but wrongly applies it to the mean as well. Option D combines both misconceptions (B9 and B13), scaling the mean by √n while leaving the SD unchanged.

### Judge Report

**Overall agreement:** 2/4 options matched  
**Issues:** The generator applied facet A7, which specifically refers to Confidence Interval width, to an item that asks only about the sampling distribution and does not mention or assess confidence intervals. While the course context mentions 'confidence intervals', this specific item functions purely as a pre-requisite check on sampling distributions and does not assess any CI-specific facets directly.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A3, B9 | A3, B9 | match | 1.0 |
| B | A3, A7 | A1, A3 | partial | 0.9 |
| C | A7, B13 | A1, B13 | partial | 0.9 |
| D | B9, B13 | B9, B13 | match | 1.0 |

---
