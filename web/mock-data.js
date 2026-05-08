// mock-data.js -- static facet configuration

const FACET_MAP = {
  topic: "confidence_intervals",
  course: "EDPSY 490 -- Applied Statistics",
  facets: [
    { id: "A1", type: "goal", text: "Students understand that as sample size increases, standard errors of sampling distribution become smaller, sampling distribution will become more packed" },
    { id: "A2", type: "goal", text: "Students understand that as sample size increases, sampling distribution will be closer to normal distribution (it does not mirror population distribution)" },
    { id: "A3", type: "goal", text: "Students understand that the mean of a sampling distribution equals population mean" },
    { id: "A4", type: "goal", text: "Students can correctly interpret the confidence level as the percentage of times (i.e., understand the implications of replications)" },
    { id: "A5", type: "goal", text: "Students understand CI is used to capture true population parameter, not sample statistics" },
    { id: "A6", type: "goal", text: "Students understand the relationship between CI width and critical value: CI width is dependent on confidence level; CI width increases as confidence level increases" },
    { id: "A7", type: "goal", text: "Students understand the relationship between CI width and standard error: CI width increases when standard error gets larger" },
    { id: "B8", type: "problematic", text: "Sampling distribution is derived from a single dataset or is the same as sample distribution (confusion about sampling distribution vs. sample distribution)" },
    { id: "B9", type: "problematic", text: "Sampling distribution mirrors population distribution (hence the standard deviation of the sampling distribution stays the same regardless of sample size; confusion about sampling distribution vs. population distribution)" },
    { id: "B10", type: "problematic", text: "As sample size increases, sampling distribution will be more spread out (misunderstand how sample sizes impact standard error)" },
    { id: "B11", type: "problematic", text: "As sample size increases, sampling distribution will be closer to population distribution" },
    { id: "B12", type: "problematic", text: "Sampling distribution of sample mean will always follow a normal distribution regardless of sample size or population distribution shape" },
    { id: "B13", type: "problematic", text: "The mean of the sampling distribution depends on sample size" },
    { id: "B14", type: "problematic", text: "For any particular sample, sample mean from a larger sample size will always be closer to mean (misunderstand the randomness in sample means)" },
    { id: "B15", type: "problematic", text: "CI is interpreted as probabilities of including either true population means or whichever to be inferred about" },
    { id: "B16", type: "problematic", text: "CI estimates sample statistics (e.g., mean) or true scores or sample data instead of population parameters" },
    { id: "B17", type: "problematic", text: "Higher confidence leads to more precise estimate, and hence shorter interval" }
  ]
};

Object.assign(window, { FACET_MAP });
