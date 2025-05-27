Dear ACs,

As the discussion period concludes, we would like to point out a few of our paper’s key contributions as well as our major updates during the discussion period.

We would first like to note that, despite our significant efforts to draft rebuttals and conduct experiments during the Author-Reviewer Discussion period, **none** of our reviewers have changed their responses in any way to reflect our responses––all of which offer key clarifications and explanations to address their concerns. **We kindly ask that you take this into consideration when evaluating our paper for acceptance.**

# Core Contributions
## A New Benchmark and Variations to Address Contamination
We present 522 carefully selected Putnam competition problems (with fully evaluable “boxed” answers) that preserve the complexity of university-level mathematics.
To tackle the risk of data contamination, we introduce Putnam-AXIOM Variations – 100 problems whose variable names, constants, or phrasings are functionally altered. This variation set forces models to demonstrate genuine problem-solving, rather than memorized solutions.
## Teacher-Forced Accuracy (TFA)
We propose TFA as a token-level metric that measures how well a model recognizes correct intermediate reasoning steps (by teacher-forcing the solution) rather than purely relying on auto-regressive generation.
During the rebuttal, we added clarifications on how TFA complements standard final-answer accuracy and how we plan to further validate it via human and GPT-4 judgments.
## New Fine-Tuning Experiments for Variations & Contamination
In response to requests for more direct contamination evidence, we fine-tuned **DeepSeek-R1 Distill-Qwen-7B** on our original dataset and evaluated it on our variations dataset:
**Baseline**: 12% accuracy on Variation questions vs. 23% on Original questions.
**After 5-Epoch Fine-Tuning on all 522 Original Problems**: 33% accuracy on Variation vs. 80% on Original.
These results show that fine-tuning on the original problems “contaminates” the model and leads to near-saturation on those (a +57% accuracy jump), yet the Variation set remains challenging (only +21% accuracy), underscoring the real-world utility of these variations to mitigate memorization.
# Key Reviewer Concerns and Our Responses

Below are a couple key concerns reviewers had about our paper as well as our responses. We believe that these clarifications/new results significantly strengthen the importance of our paper as a whole.

## Selection and Coverage of Putnam Problems

We clarify in the paper how we curated problems across diverse topics (algebra, geometry, calculus, combinatorics, etc.) and difficulty levels (Putnam’s 1–6 range). The primary filter was to ensure each problem had a single, definitive final answer, enabling fully automated evaluation without losing mathematical rigor.

## Evidence of Data Contamination and Utility of Variations

Our new fine-tuning results confirm that the Variation set meaningfully resists contamination effects. Even after direct supervised fine-tuning on the entire Original set, the model does not “overfit” to the Variation set, demonstrating that small changes in constants, variables, or phrasing still pose a substantial challenge.

## Clarifications on TFA vs. Final-Answer Accuracy

We acknowledge that final-boxed accuracy aligns more directly with a model’s end performance, while TFA focuses on token-level recognition of correct reasoning. We plan further validation of TFA using step-level judgments from humans or GPT-4, ensuring it reflects deeper reasoning quality rather than merely correlating with final correctness.

## Resolving Presentation or Labeling Issues

We have corrected figure labels (e.g., Figure 3) that were inadvertently swapped and clarified any discrepancies between our tables and scatter plots. We will provide these corrected figures in our updated submission.

## Benchmark Differences Compared to Existing Putnam-Related Work (e.g. PutnamBench)

Putnam-AXIOM focuses on natural-language problems with final answer verification, functional variations to address contamination, and proxy metrics for reasoning. PutnamBench translates Putnam questions into formal statements for theorem-proving languages. Our datasets serve distinct purposes despite being sourced from the same competition.


