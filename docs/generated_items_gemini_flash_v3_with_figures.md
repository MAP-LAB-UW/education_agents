# Generated Items — V3 Prompt with Figures (Gemini 3 Flash)

**Generator model:** Gemini 3 Flash Preview  
**Judge model:** Gemini 3.1 Pro Preview  
**Topic:** Confidence Intervals  
**Items:** 10  
**Prompt version:** V3 (figure-encouraged, LaTeX notation)  
**Format:** Dynamic (model chooses)  

---

## Item 1

**Target facets:** A6, A7, B17  
**Format:** Single Select  

> **Facet selection reasoning:** This selection focuses on the conceptual factors that determine the width of a confidence interval. It allows for a diagnostic question that tests whether students understand how changing the confidence level (A6) and sample size/standard error (A7) affects the interval width, while specifically targeting the common misconception that higher confidence results in a narrower, more 'precise' interval (B17).

### Stem

A nutritionist calculates a $95\%$ confidence interval for the mean sugar content of a cereal brand as $(12.1, 14.7)$ grams, based on a random sample of $n = 30$ boxes. The nutritionist is shown a plot of how the interval width changes with the confidence level for this specific sample of $n = 30$.

The nutritionist wants to conduct a new study specifically designed to produce an even **narrower** confidence interval for the mean. Which of the following strategies is guaranteed to result in a narrower interval?

![A horizontal line plot showing three confidence intervals for the same sample. The 90% interval is the shortest, the 95% interval is medium length, and the 99% interval is the longest.](figures/gemini_flash_v3_figures/item1_fig1.png)

### Options

**opt_a.** Decrease the confidence level to $90\%$ and increase the sample size to $n = 100$. :white_check_mark:  
*Facets: A6, A7*  
*Rationale: This student correctly identifies that decreasing the confidence level reduces the critical value $z^*$ (A6) and increasing the sample size reduces the standard error (A7), both of which act to narrow the interval width.*

**opt_b.** Increase the confidence level to $99\%$ and increase the sample size to $n = 100$.  
*Facets: B17, A7*  
*Rationale: This student understands that increasing the sample size will help narrow the interval (A7). However, they hold the misconception that a higher confidence level is 'better' or more 'precise,' leading them to believe that $99\%$ confidence would yield a narrower interval than $95\%$ (B17).*

**opt_c.** Decrease the confidence level to $90\%$ and decrease the sample size to $n = 10$.  
*Facets: A6, B10*  
*Rationale: This student correctly understands that a lower confidence level narrows the interval (A6), but they incorrectly believe that a smaller sample size will also narrow the interval, possibly confusing sample size with standard error or believing smaller samples are less spread out (B10).*

**opt_d.** Increase the confidence level to $99\%$ and decrease the sample size to $n = 10$.  
*Facets: B17, B10*  
*Rationale: This student incorrectly believes that a higher confidence level results in a narrower, more precise interval (B17) and incorrectly believes that decreasing the sample size will reduce the spread of the interval (B10).*

### Explanation

To obtain a narrower confidence interval, one must reduce the margin of error, which is defined as $ME = z^* \cdot \frac{\sigma}{\sqrt{n}}$. This can be achieved in two ways: (1) decreasing the confidence level (e.g., from $95\%$ to $90\%$), which reduces the critical value $z^*$ (A6); or (2) increasing the sample size $n$, which reduces the standard error $\frac{\sigma}{\sqrt{n}}$ (A7). Students who believe higher confidence levels lead to shorter intervals (B17) or that smaller sample sizes lead to less spread (B10) will choose incorrect combinations.

### Judge Report

**Overall agreement:** 2/4 options matched  
**Issues:** The generator's tags for options addressing sample size omitted A1, which explicitly covers the relationship between sample size and the standard error of the sampling distribution.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| opt_a | A6, A7 | A1, A6, A7 | partial | 0.95 |
| opt_b | B17, A7 | A1, A7, B17 | partial | 0.95 |
| opt_c | A6, B10 | A6, B10 | match | 0.95 |
| opt_d | B17, B10 | B10, B17 | match | 0.95 |

---

## Item 2

**Target facets:** A4, A5, B15, B16  
**Format:** True False Per Option  

> **Facet selection reasoning:** This selection targets the conceptual interpretation of confidence intervals. It contrasts the correct interpretation of the confidence level as a frequentist long-run proportion (A4) with the common probability misconception (B15). It also addresses the target of the interval, ensuring students understand that CIs are used to estimate population parameters (A5) rather than sample statistics or specific data points (B16).

### Stem

A researcher studying social media habits finds that for a random sample of $n = 150$ high school students, the mean daily usage is $\bar{x} = 3.2$ hours. They calculate a $95\%$ confidence interval for the population mean daily usage ($\mu$) as $(2.9, 3.5)$ hours. Figure illustrates the concept of confidence intervals by showing $20$ simulated intervals calculated from different samples from the same population. Based on this study, evaluate each of the following interpretations.

![A plot showing 20 horizontal lines representing 95% confidence intervals from different samples. Most lines (colored blue) overlap a central vertical dashed line representing the true population mean, while one or two (colored red) do not overlap.](figures/gemini_flash_v3_figures/item2_fig1.png)

### Options

**opt1.** There is a $95\%$ probability that the true population mean ($\mu$) is between $2.9$ and $3.5$ hours.  
*Facets: B15*  
*Rationale: This is a common misconception where students interpret a specific, already-calculated confidence interval as a probability statement about a fixed population parameter. In frequentist statistics, the population mean is a fixed value, so the probability that it falls within a specific range is either 0 or 1.*

**opt2.** We are $95\%$ confident that the true population mean ($\mu$) for all high school students is between $2.9$ and $3.5$ hours. :white_check_mark:  
*Facets: A4, A5*  
*Rationale: This is a correct interpretation of a confidence interval. It uses the appropriate level of confidence to describe our uncertainty about the true population parameter based on the sample data.*

**opt3.** In the long run, if we were to take many random samples of $n = 150$ and calculate a $95\%$ confidence interval for each, about $95\%$ of those intervals would contain the true population mean ($\mu$). :white_check_mark:  
*Facets: A4, A5*  
*Rationale: This correctly describes the frequentist definition of the confidence level as a 'capture rate' over infinite replications of the sampling process.*

**opt4.** Approximately $95\%$ of the high school students in the entire population spend between $2.9$ and $3.5$ hours on social media.  
*Facets: B16*  
*Rationale: This incorrectly interprets the confidence interval for the mean as a range that contains a specific percentage of individual observations in the population. Confidence intervals describe the precision of the estimate for the mean, not the distribution of the individual data points.*

**opt5.** There is a $95\%$ probability that the mean of another random sample of $150$ students will be between $2.9$ and $3.5$ hours.  
*Facets: B15, B16*  
*Rationale: This conflates a confidence interval (which estimates a population parameter) with a prediction interval for future sample statistics (B16), while also applying the probability misconception (B15).*

### Explanation

This item tests the fundamental understanding and common misinterpretations of confidence intervals. Correct interpretations (A4, A5) focus on the long-run capture rate of the population parameter (the mean $\mu$). Common errors include treating the calculated interval as a probability (B15), or confusing the population mean with individual data points or future sample statistics (B16).

### Judge Report

**Overall agreement:** 4/5 options matched  
**Issues:** The inclusion of the figure illustrates the frequentist interpretation (Option 3) nicely, but is somewhat superfluous to answering the questions since the interpretations are standard conceptual definitions.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| opt1 | B15 | B15 | match | 1.0 |
| opt2 | A4, A5 | A5 | partial | 0.9 |
| opt3 | A4, A5 | A4, A5 | match | 1.0 |
| opt4 | B16 | B16 | match | 1.0 |
| opt5 | B15, B16 | B15, B16 | match | 1.0 |

---

## Item 3

**Target facets:** A1, A2, B10, B11  
**Format:** Single Select  

> **Facet selection reasoning:** This combination targets students' conceptual understanding of the Central Limit Theorem and the effect of sample size on the sampling distribution. It contrasts the correct principles that an increased sample size decreases standard error and leads to a more normal shape (A1, A2) against the common misconceptions that larger samples cause the sampling distribution to become more spread out (B10) or to look more like the population distribution itself (B11).

### Stem

The daily commute times for all residents in a large metropolitan area are heavily skewed to the right, with a population mean $\mu = 30$ minutes and a population standard deviation $\sigma = 15$ minutes. The population distribution is shown below: A researcher plans to take many random samples of size $n = 5$ and many random samples of size $n = 100$. How will the sampling distribution of the sample mean ($\bar{x}$) for $n = 100$ compare to the sampling distribution of the sample mean for $n = 5$?

![A graph showing a right-skewed population distribution with a peak near 15 minutes and a long tail extending to the right, with the mean labeled at 30 minutes.](figures/gemini_flash_v3_figures/item3_fig1.png)

### Options

**opt1.** The distribution for $n = 100$ will be more approximately Normal in shape and the sample means will be more tightly clustered around $\mu = 30$ minutes. :white_check_mark:  
*Facets: A1, A2*  
*Rationale: This correctly applies the Central Limit Theorem: as $n$ increases, the sampling distribution of the mean becomes more Normal (A2) and the standard error ($\%sigma/\sqrt{n}$) decreases, making the distribution more concentrated (A1).*

**opt2.** The distribution for $n = 100$ will be more approximately Normal in shape, but the sample means will be more spread out over a larger range of values than for $n = 5$.  
*Facets: A2, B10*  
*Rationale: The student correctly identifies the change in shape towards Normality (A2) but incorrectly believes that a larger sample size leads to more variation in the sample mean (B10).*

**opt3.** The distribution for $n = 100$ will be more heavily skewed to the right than for $n = 5$, more closely resembling the shape of the original population distribution.  
*Facets: B11*  
*Rationale: The student confuses the sampling distribution of the mean with the distribution of individual data points in a single sample, mistakenly believing that the sampling distribution approaches the population shape as $n$ increases (B11).*

**opt4.** The distribution for $n = 100$ will look more like the skewed population distribution and will have a wider range of possible $\bar{x}$ values than the distribution for $n = 5$.  
*Facets: B10, B11*  
*Rationale: The student exhibits two misconceptions: that the sampling distribution mirrors the population shape (B11) and that larger samples result in more spread-out sampling distributions (B10).*

### Explanation

This item assesses the Central Limit Theorem's implications for sampling distributions. As sample size ($n$) increases, the Central Limit Theorem states that the sampling distribution of the sample mean ($ar{x}$) becomes more approximately Normal (A2) regardless of the population shape (as long as it has a finite variance). Additionally, the standard error of the mean is calculated as $\frac{\sigma}{\sqrt{n}}$; therefore, as $n$ increases, the standard error decreases, meaning the sampling distribution becomes more concentrated (A1). Students who miss these points often confuse the sampling distribution with the population distribution (B11) or misunderstand the relationship between sample size and the stability (variance) of the mean (B10).

### Judge Report

**Overall agreement:** 4/4 options matched  
**Issues:** None  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| opt1 | A1, A2 | A1, A2 | match | 1.0 |
| opt2 | A2, B10 | A2, B10 | match | 1.0 |
| opt3 | B11 | B11 | match | 1.0 |
| opt4 | B10, B11 | B10, B11 | match | 1.0 |

---

## Item 4

**Target facets:** A3, B8, B9, B13  
**Format:** Single Select  

> **Facet selection reasoning:** This selection focuses on the conceptual definition and the center of the sampling distribution, which is the foundational concept for confidence intervals. It specifically tests whether students can distinguish the sampling distribution from the population distribution or a single sample (A3 vs B8, B9) and addresses the misconception that the mean of the sampling distribution changes when the sample size increases (A3 vs B13).

### Stem

The scores on a national certification exam are normally distributed with a population mean $\mu = 500$ and a population standard deviation $\sigma = 100$. A researcher plans to conduct a simulation where they repeatedly take random samples of size $n = 100$ students and calculate the sample mean score $\bar{x}$ for each sample. After thousands of repetitions, they plot the distribution of these sample means. Which of the following correctly describes this sampling distribution?

![A graph comparing a wide normal distribution (population, SD=100) and a very narrow normal distribution (sampling distribution, SE=10), both centered at 500.](figures/gemini_flash_v3_figures/item4_dist_comparison.png)

### Options

**opt_a.** The distribution will be centered at $500$ and have a standard deviation of $10$. :white_check_mark:  
*Facets: A3*  
*Rationale: This is correct because the mean of the sampling distribution of the mean is equal to the population mean ($\mu_{\bar{x}} = \mu = 500$) and the standard error is $\sigma/\sqrt{n} = 100/\sqrt{100} = 10$.*

**opt_b.** The distribution will be centered at $500$ and have a standard deviation of $100$.  
*Facets: B9*  
*Rationale: A student picking this correctly identifies the mean of the sampling distribution but fails to realize that the sampling distribution is less spread out than the population distribution, incorrectly assuming the standard deviation remains $100$ regardless of sample size.*

**opt_c.** The distribution will be centered at $50$ (calculated as $500/\sqrt{100}$) and have a standard deviation of $10$.  
*Facets: B13*  
*Rationale: This option reflects the misconception that the mean of the sampling distribution depends on the sample size, applying the square root of $n$ adjustment to the mean rather than the standard deviation.*

**opt_d.** The distribution is simply the set of $100$ individual scores collected from one specific sample of students.  
*Facets: B8*  
*Rationale: This choice reveals a confusion between the 'sampling distribution' (the behavior of statistics across many samples) and the 'sample distribution' (the data within a single dataset).*

### Explanation

This item tests the properties of the sampling distribution of the sample mean. According to the Central Limit Theorem and the properties of expected values, the mean of the sampling distribution ($\mu_{\bar{x}}$) is always equal to the population mean ($\mu$), regardless of the sample size (addressing A3 and B13). The spread of the sampling distribution (Standard Error) is determined by $\sigma/\sqrt{n}$, meaning it is tighter than the population distribution (addressing B9). Finally, the sampling distribution is a theoretical distribution of a statistic (like $\bar{x}$) over many samples, not the distribution of data points within a single sample (addressing B8).

### Judge Report

**Overall agreement:** 4/4 options matched  
**Issues:** The attached image completely gives away the correct answer. The legend in the plot explicitly states 'Sampling Dist. (n=100, SE=10)', which tells the student directly that the standard deviation is 10 and visually shows the distribution centered at 500. This image should not be shown to students alongside the item unless it is part of a scaffolded learning activity rather than an assessment.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| opt_a | A3 | A3 | match | 1.0 |
| opt_b | B9 | B9 | match | 1.0 |
| opt_c | B13 | B13 | match | 1.0 |
| opt_d | B8 | B8 | match | 1.0 |

---

## Item 5

**Target facets:** A2, B12, B14  
**Format:** Single Select  

> **Facet selection reasoning:** This selection focuses on the Central Limit Theorem and the behavior of the sample mean. It tests the understanding that normality is an asymptotic property (A2) against the misconception that the sampling distribution is always normal (B12), while also addressing the deterministic misconception that larger samples always result in a sample mean closer to the population mean (B14).

### Stem

The population distribution of the time (in days) it takes for a specific type of tree seed to germinate is shown in. The distribution is strongly right-skewed with a mean of $\mu = 14$ days and a standard deviation of $\sigma = 10$ days. Alice plans to take a random sample of $n = 4$ seeds and calculate the sample mean $\bar{x}_A$. Bob plans to take a random sample of $n = 100$ seeds and calculate the sample mean $\bar{x}_B$. Which of the following is true regarding their sampling distributions and individual results?

![A right-skewed probability density plot showing germination times peaking near 5 days and tapering off to 50 days, with the population mean marked at 14.](figures/gemini_flash_v3_figures/item5_fig1.png)

### Options

**A.** The sampling distribution of the sample mean will be approximately normal for both Alice and Bob because they are both calculating a mean value.  
*Facets: B12*  
*Rationale: The student incorrectly believes that the Central Limit Theorem (CLT) applies to any sampling distribution of the mean regardless of the sample size or the shape of the underlying population.*

**B.** If Alice and Bob each collect their data once, Bob's calculated sample mean $\bar{x}_B$ is guaranteed to be closer to 14 days than Alice's $\bar{x}_A$ because of his much larger sample size.  
*Facets: B14*  
*Rationale: The student treats the law of large numbers or the lower standard error of a large sample as a deterministic rule for a single trial, failing to recognize that random variation still exists in every individual sample outcome.*

**C.** Bob's sampling distribution for $\bar{x}_B$ will be approximately normal, whereas Alice's sampling distribution for $\bar{x}_A$ will retain a right-skewed shape. :white_check_mark:  
*Facets: A2*  
*Rationale: The student correctly understands that the Central Limit Theorem requires a sufficiently large sample size ($n=100$) to produce a normal sampling distribution from a skewed population, and that small samples ($n=4$) will still exhibit the skewness of the original population.*

**D.** Both researchers will have an approximately normal sampling distribution, and Bob's specific sample mean $\bar{x}_B$ must be more accurate than Alice's $\bar{x}_A$ in any single comparison.  
*Facets: B12, B14*  
*Rationale: The student combines two misconceptions: that normality is automatic for any sample mean and that a larger sample size guarantees a more accurate result for a specific instance.*

### Explanation

This item assesses whether students understand how sample size influences the shape and predictability of the sampling distribution of the mean. Goal facet A2 is addressed by the correct identification that a large sample size ($n=100$) allows the Central Limit Theorem to take effect, while a small sample ($n=4$) does not. The distractors probe the misconception that the sampling distribution is always normal (B12) and the deterministic fallacy that a larger sample always yields a closer mean in a single trial (B14).

### Judge Report

**Overall agreement:** 4/4 options matched  
**Issues:** The item focuses strictly on sampling distributions and the Central Limit Theorem rather than the construction or interpretation of confidence intervals. However, because the provided facet map explicitly contains several facets related to sampling distributions, the item is perfectly aligned with the given criteria.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | B12 | B12 | match | 1.0 |
| B | B14 | B14 | match | 1.0 |
| C | A2 | A2 | match | 1.0 |
| D | B12, B14 | B12, B14 | match | 1.0 |

---

## Item 6

**Target facets:** A5, A7, B8, B9  
**Format:** Single Select  

> **Facet selection reasoning:** This combination of facets focuses on the foundational concept of what a confidence interval is designed to estimate (population parameters versus sample or population data) and the structural factors that determine its width. By pairing goal facets A5 and A7 with problematic facets B8 and B9, the item can diagnose whether a student's difficulty in calculating or interpreting CI width is rooted in a fundamental confusion between the sample distribution, the population distribution, and the sampling distribution.

### Stem

A soil scientist is measuring the soil acidity (pH) of a nature reserve. From previous large-scale studies, the population standard deviation of soil pH in this region is known to be $\sigma = 0.60$. The scientist takes a random sample of $n = 36$ soil cores and finds a sample mean $\bar{x} = 6.5$. They wish to construct a 95% confidence interval using the formula $\bar{x} \pm 1.96 \cdot SE$. The relationship between the population distribution and the sampling distribution is shown below: Which of the following is the correct calculation of the 95% confidence interval and its interpretation?

![A plot comparing two normal distributions centered at 6.5. The population distribution is wide and low, spread from about 4.5 to 8.5. The sampling distribution for n=36 is much narrower and taller, concentrated between 6.2 and 6.8, illustrating how the standard error is smaller than the population standard deviation.](figures/gemini_flash_v3_figures/item6_fig1.png)

### Options

**A.** Using $SE = \frac{0.60}{\sqrt{36}} = 0.10$, the interval is $(6.304, 6.696)$. This interval provides an estimate for the true population mean pH of the nature reserve. :white_check_mark:  
*Facets: A5, A7*  
*Rationale: The student correctly applies the standard error formula ($SE = \sigma/\sqrt{n}$) which leads to a narrower interval than the population spread, and they correctly identify that the confidence interval is used to estimate the population parameter (mean pH).*

**B.** Using $SE = 0.60$, the interval is $(5.324, 7.676)$. This interval provides an estimate for the true population mean pH of the nature reserve.  
*Facets: A5, B9*  
*Rationale: The student correctly identifies the population mean as the target for the confidence interval (A5), but they mistakenly assume the sampling distribution has the same standard deviation as the population, ignoring the effect of sample size on the precision of the estimate (B9).*

**C.** Using $SE = \frac{0.60}{\sqrt{36}} = 0.10$, the interval is $(6.304, 6.696)$. This interval indicates that 95% of the soil cores in the current sample have a pH between $6.304$ and $6.696$.  
*Facets: A7, B8*  
*Rationale: The student correctly calculates the standard error and resulting interval width (A7), but they misinterpret the confidence interval as a description of the sample data distribution (where individual observations fall) rather than an estimate for the population parameter (B8).*

**D.** Using $SE = 0.60$, the interval is $(5.324, 7.676)$. This interval indicates that 95% of the soil cores in the current sample have a pH between $5.324$ and $7.676$.  
*Facets: B8, B9*  
*Rationale: This choice reveals two misconceptions: the student uses the population standard deviation instead of the standard error (B9) and interprets the resulting interval as the range containing the majority of individual sample data points (B8).*

### Explanation

The core objective of a confidence interval is to estimate a population parameter, such as the true mean $\mu$ (A5). To do this accurately, one must use the standard error of the sampling distribution, $SE = \sigma / \sqrt{n}$, which accounts for the fact that the distribution of sample means is less variable (more packed) than the population distribution (A7). Students who confuse the sampling distribution with the population distribution (B9) or the sample distribution (B8) will fail to correctly identify the width or the purpose of the interval.

### Judge Report

**Overall agreement:** 1/4 options matched  
**Issues:** The figure's legend explicitly gives away the standard error ('SE = 0.10'). This defeats the purpose of diagnosing whether a student knows how to calculate the standard error or understands the effect of sample size, as they can simply read the correct SE value directly from the image. The item stem states the sample mean is x-bar = 6.5, while the figure legend lists the Population Mean as mu = 6.5 at the same central position. While a sample mean can exactly equal a population mean, showing them as identical in a diagnostic item could severely confuse students trying to differentiate between statistics and parameters, especially since CIs are centered around the sample mean.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| A | A5, A7 | A5 | partial | 0.9 |
| B | A5, B9 | A5, B9 | match | 1.0 |
| C | A7, B8 | B16 | mismatch | 0.85 |
| D | B8, B9 | B9, B16 | partial | 0.9 |

---

## Item 7

**Target facets:** A1, A4, B10, B15  
**Format:** Single Select  

> **Facet selection reasoning:** This facet combination connects the structural mechanics of sampling distributions (sample size effect on standard error) with the conceptual interpretation of the resulting confidence interval. It allows for the creation of a diagnostic item that assesses whether a student can reconcile the physical narrowing of the sampling distribution as n increases (A1 vs B10) with the frequentist definition of confidence level versus the common probability-based misconception (A4 vs B15).

### Stem

A researcher is studying the average caffeine consumption of adults in a city. Based on a random sample of $n = 64$ adults, they calculate a $95\%$ confidence interval for the population mean $\mu$ to be $(180, 220)$ mg/day. The researcher is now considering how their results would change if they increased the sample size to $n = 256$ adults. Based on the sampling distributions shown in the figure, which of the following is a correct prediction and interpretation for the study with $n = 256$?

![A graph showing two normal curves representing sampling distributions. The curve for n=64 is wider and shorter, while the curve for n=256 is much narrower and taller, both centered at 200.](figures/gemini_flash_v3_figures/item7_fig1.png)

### Options

**opt1.** The sampling distribution will become more packed around $\mu$, resulting in a narrower interval; if they repeated this process many times, they would expect $95\%$ of the resulting intervals to contain $\mu$. :white_check_mark:  
*Facets: A1, A4*  
*Rationale: This option correctly identifies that increasing the sample size reduces the standard error (A1), making the sampling distribution narrower, and provides the correct frequentist interpretation of the confidence level as a long-run success rate (A4).*

**opt2.** The sampling distribution will become more spread out because a larger sample size captures more individual variation from the population, likely leading to a wider confidence interval.  
*Facets: B10*  
*Rationale: This option reflects the misconception that increasing the sample size increases the spread of the sampling distribution, when in fact it decreases the standard error.*

**opt3.** For the specific interval of $(180, 220)$ mg/day already calculated, there is a $95\%$ probability that the true population mean $\mu$ falls within these bounds.  
*Facets: B15*  
*Rationale: This option incorrectly interprets the confidence level as a probability that a fixed parameter lies within a fixed interval, a common misconception in Bayesian-like reasoning for frequentist intervals.*

**opt4.** The sampling distribution for $n = 256$ will be wider than for $n = 64$, but we can still say there is a $95\%$ probability that the true mean $\mu$ is inside the resulting interval.  
*Facets: B10, B15*  
*Rationale: This option combines two misconceptions: that larger sample sizes increase the spread of the sampling distribution and that the confidence level describes the probability of the parameter being in a specific interval.*

### Explanation

Increasing the sample size ($n$) reduces the standard error of the sampling distribution ($σ/\sqrt{n}$), causing the distribution of sample means to become more concentrated or 'packed' around the population mean $μ$ (Goal A1). Furthermore, a $95\%$ confidence level means that if we were to take many samples of the same size and construct an interval for each, approximately $95\%$ of those intervals would contain the true population mean (Goal A4). Common misconceptions include thinking that more data leads to a more 'spread out' distribution (B10) or that the confidence level represents the probability of the parameter being in one specific, already-calculated interval (B15).

### Judge Report

**Overall agreement:** 4/4 options matched  
**Issues:** Options lack parallel structure: Options 1 and 4 address both the shape/width of the new distribution and the interpretation of the confidence level, whereas Option 2 only addresses the shape/width, and Option 3 only addresses the interpretation. Option 3 does not directly answer the question asked in the stem. The stem asks for a 'prediction and interpretation for the study with n = 256', but Option 3 only provides an interpretation of the specific interval already calculated for n = 64.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| opt1 | A1, A4 | A1, A4 | match | 1.0 |
| opt2 | B10 | B10 | match | 1.0 |
| opt3 | B15 | B15 | match | 1.0 |
| opt4 | B10, B15 | B10, B15 | match | 1.0 |

---

## Item 8

**Target facets:** A1, A6, B10, B17  
**Format:** Single Select  

> **Facet selection reasoning:** This combination allows for a diagnostic item that tests a student's ability to identify how different factors influence the width and precision of a confidence interval. It contrasts the correct understanding of sample size effects on standard error (A1 vs B10) with the correct understanding of the trade-off between confidence level and interval width (A6 vs B17). This specific combination has not been used before and targets the logic of interval construction.

### Stem

A lake scientist calculates a $95\%$ confidence interval for the mean dissolved oxygen concentration based on a sample of $n = 40$ readings. The resulting interval is $(6.2, 7.8) \text{ mg/L}$. The scientist is unhappy with the width of this interval and wants to obtain a **shorter** (narrower) confidence interval in a follow-up study. Which of the following combinations of changes is guaranteed to produce a shorter confidence interval than the current one?

### Options

**opt1.** Increase the sample size to $n = 100$ and decrease the confidence level to $90\%$. :white_check_mark:  
*Facets: A1, A6*  
*Rationale: The student correctly understands that increasing the sample size reduces the standard error ($A1$) and that decreasing the confidence level reduces the critical value ($A6$). Both of these changes result in a smaller margin of error and thus a narrower (shorter) interval.*

**opt2.** Increase the sample size to $n = 100$ and increase the confidence level to $99\%$.  
*Facets: A1, B17*  
*Rationale: The student understands that a larger sample size helps reduce width ($A1$), but they hold the misconception that a higher confidence level provides more 'precision' and therefore a shorter interval ($B17$). In fact, increasing confidence increases the critical value, which widens the interval.*

**opt3.** Decrease the sample size to $n = 20$ and decrease the confidence level to $90\%$.  
*Facets: A6, B10*  
*Rationale: The student understands that a lower confidence level helps reduce width ($A6$), but they hold the misconception that smaller samples result in a less spread-out sampling distribution ($B10$). In reality, a smaller sample size increases the standard error, which widens the interval.*

**opt4.** Decrease the sample size to $n = 20$ and increase the confidence level to $99\%$.  
*Facets: B10, B17*  
*Rationale: This choice reflects two misconceptions: that smaller sample sizes lead to more 'packed' or less spread-out sampling distributions ($B10$) and that higher confidence levels lead to shorter, more precise intervals ($B17$). Both of these changes actually serve to widen the interval.*

### Explanation

The width of a confidence interval for a mean is given by $2 \cdot z^* \cdot \frac{\sigma}{\sqrt{n}}$. To decrease this width, one must decrease the margin of error ($z^* \cdot \frac{\sigma}{\sqrt{n}}$). This is achieved by either increasing the sample size $n$ (which decreases the standard error, $A1$) or decreasing the confidence level (which decreases the critical value $z^*$, $A6$). Misconceptions include thinking that increasing $n$ makes the distribution more spread out ($B10$) or that higher confidence requirements lead to narrower intervals ($B17$).

### Judge Report

**Overall agreement:** 4/4 options matched  
**Issues:** The item has a severe flaw: Option 2 is mathematically also a correct answer. If we assume constant standard deviation, the original margin of error is proportional to 1.96 / sqrt(40) ≈ 0.310. Option 2's margin of error is proportional to 2.576 / sqrt(100) ≈ 0.258. Since 0.258 < 0.310, the interval in Option 2 is also guaranteed to be shorter. To fix this, change the numbers in the options (e.g., in Option 2, increase sample size to only n=50, which would yield a wider interval) or remove the specific numbers altogether and just ask about the directions of change.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| opt1 | A1, A6 | A1, A6 | match | 1.0 |
| opt2 | A1, B17 | A1, B17 | match | 1.0 |
| opt3 | A6, B10 | A6, B10 | match | 1.0 |
| opt4 | B10, B17 | B10, B17 | match | 1.0 |

---

## Item 9

**Target facets:** A4, A6, B15, B17  
**Format:** True False Per Option  

> **Facet selection reasoning:** This combination focuses on the conceptual meaning and the formal properties of the confidence level. It assesses whether students understand confidence levels as a long-run success rate (A4) rather than a single-interval probability (B15), and whether they correctly identify that increasing confidence requires a wider interval (A6), countering the intuition that more confidence means a more precise or narrower result (B17).

### Stem

A marine biologist measures the shell lengths of a random sample of $n = 40$ adult green sea turtles. Based on the sample mean $\bar{x} = 100.0$ cm and sample standard deviation $s = 15.5$ cm, she calculates a $95\%$ confidence interval for the population mean length $\mu$:

$$(95.2, 104.8) \text{ cm}$$

The biologist is considering how her results would change if she used a $99\%$ confidence level instead. Determine whether each of the following statements is a correct or incorrect interpretation of these statistical results.

![A horizontal bar chart comparing two confidence intervals centered at 100 cm. The 95% confidence interval spans from 95.2 to 104.8, while the 99% confidence interval is visibly wider, spanning from 93.7 to 106.3.](figures/gemini_flash_v3_figures/item9_fig1.png)

### Options

**opt1.** There is a $95\%$ probability that the true population mean length $\mu$ is between $95.2$ cm and $104.8$ cm.  
*Facets: B15*  
*Rationale: This statement reflects the common misconception that the confidence level represents the probability that the population parameter falls within a specific, already-calculated interval. In the frequentist framework, the parameter is a fixed value, and a specific interval either contains it or it does not (probability is 0 or 1).*

**opt2.** If the biologist were to repeat this study many times, taking a new random sample of $n = 40$ each time and calculating a $95\%$ confidence interval from each sample, about $95\%$ of the resulting intervals would contain the true population mean $\mu$. :white_check_mark:  
*Facets: A4*  
*Rationale: This correctly interprets the $95\%$ confidence level as the 'success rate' of the interval-calculation procedure over many hypothetical repetitions of the study.*

**opt3.** To obtain a more precise (shorter) interval from the same sample data, the biologist should increase her confidence level to $99\%$.  
*Facets: B17*  
*Rationale: This option targets the misconception that higher confidence always results in a better or 'more precise' (shorter) estimate. In reality, increasing the confidence level while keeping the sample size the same always results in a wider, less precise interval.*

**opt4.** A $99\%$ confidence interval calculated from this same data would be wider than $(95.2, 104.8)$ cm because a higher confidence level requires a larger critical value (such as $z^*$ or $t^*$). :white_check_mark:  
*Facets: A6*  
*Rationale: This correctly identifies that a wider interval is necessary to achieve a higher level of confidence, as it involves a larger margin of error driven by a higher critical value.*

### Explanation

This item tests the understanding of confidence interval interpretation and the relationship between confidence levels and interval width. It diagnoses the misconception that the confidence level is a probability statement about a fixed interval (B15) and the misconception that higher confidence leads to shorter intervals (B17). It rewards the correct interpretation of confidence as a process-oriented success rate (A4) and the understanding that higher confidence levels require wider intervals due to larger critical values (A6).

### Judge Report

**Overall agreement:** 4/4 options matched  
**Issues:** The inclusion of the figure provides a massive hint and essentially gives away the answers to Option 3 and Option 4. The figure visibly shows that the 99% confidence interval is wider than the 95% confidence interval. Students can easily evaluate options 3 and 4 by simply looking at the image rather than relying on their understanding of the statistical concepts, thereby invalidating the diagnostic power of those options for facets A6 and B17.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| opt1 | B15 | B15 | match | 1.0 |
| opt2 | A4 | A4 | match | 1.0 |
| opt3 | B17 | B17 | match | 1.0 |
| opt4 | A6 | A6 | match | 1.0 |

---

## Item 10

**Target facets:** A2, A3, B12, B13  
**Format:** Single Select  

> **Facet selection reasoning:** This combination focuses on the properties of the sampling distribution. It contrasts the correct understanding that the sampling distribution mean is independent of sample size (A3) and approaches normality only as sample size increases (A2), against common misconceptions that the mean depends on n (B13) or that the distribution is always normal regardless of n (B12).

### Stem

The daily amount of time teenagers spend on a specific social media app is heavily right-skewed, as shown in the population distribution. The population mean is $\mu = 4.5$ hours and the population standard deviation is $\sigma = 2.2$ hours. A researcher plans to take many random samples of size $n$ from this population and calculate the sample mean $\bar{x}$ for each sample to build a sampling distribution of the mean. Which of the following is true regarding the resulting sampling distribution?

![A line graph showing a heavily right-skewed distribution representing the population. The density is highest near the left and tapers off slowly to the right. A vertical dashed line marks the mean at 4.5.](figures/gemini_flash_v3_figures/item10_fig1.png)

### Options

**opt1.** For a sample size of $n = 100$, the sampling distribution of $\bar{x}$ will be approximately normal with a mean of $4.5$ hours. :white_check_mark:  
*Facets: A2, A3*  
*Rationale: The student correctly understands that for a sufficiently large sample ($n=100$), the Central Limit Theorem ensures the sampling distribution is approximately normal (A2) and that its mean remains equal to the population mean (A3).*

**opt2.** The sampling distribution of $\bar{x}$ will be approximately normal with a mean of $4.5$ hours, regardless of whether the sample size is $n = 2$ or $n = 100$.  
*Facets: B12, A3*  
*Rationale: The student correctly identifies the mean (A3) but incorrectly believes that the sampling distribution of the mean is always normal, regardless of the sample size or the skewness of the underlying population (B12).*

**opt3.** For a sample size of $n = 100$, the sampling distribution of $\bar{x}$ will be approximately normal with a mean of $4.5 / \sqrt{100} = 0.45$ hours.  
*Facets: A2, B13*  
*Rationale: The student correctly identifies that the distribution becomes normal for large $n$ (A2) but incorrectly believes that the mean of the sampling distribution decreases as sample size increases, confusing the mean with the standard error formula (B13).*

**opt4.** For a sample size of $n = 100$, the sampling distribution of $\bar{x}$ will be heavily right-skewed with a mean of $4.5$ hours.  
*Facets: A3*  
*Rationale: The student correctly identifies the mean (A3) but fails to recognize that the Central Limit Theorem causes the sampling distribution of the mean to become approximately normal as the sample size increases (A2).*

### Explanation

This item tests the application of the Central Limit Theorem to the sampling distribution of the mean. Key concepts include: 1) the mean of the sampling distribution is always equal to the population mean regardless of sample size (A3); 2) for large sample sizes, the sampling distribution becomes approximately normal even if the population is skewed (A2). Distractors target the misconception that the distribution is always normal regardless of sample size (B12) or that the mean of the sampling distribution changes with sample size (B13).

### Judge Report

**Overall agreement:** 3/4 options matched  
**Issues:** The generator missed tagging facet B9 in option 4, which perfectly describes the misconception that the sampling distribution mirrors the shape of the underlying skewed population. The item topic is labeled as 'confidence_intervals', but the item exclusively tests sampling distribution concepts and the Central Limit Theorem without making any connections to confidence intervals.  

| Option | Generator Tags | Judge Tags | Agreement | Confidence |
|--------|---------------|------------|-----------|------------|
| opt1 | A2, A3 | A2, A3 | match | 1.0 |
| opt2 | B12, A3 | A3, B12 | match | 1.0 |
| opt3 | A2, B13 | A2, B13 | match | 1.0 |
| opt4 | A3 | A3, B9 | partial | 0.95 |

---
