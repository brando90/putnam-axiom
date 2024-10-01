4 Approach

Given a benchmark test written as a “question, answer” pair, we convert it to three
functions “problem(inputs), solution(inputs), inputs(rngs, seed)”. These functions
are designed to have the property that arriving at answer using a well-reasoned
derivation from the original question is the same that would yield answer’ = solution(in) from question’ = problem(in) where in = inputs(rngs, seed) for an arbitrarily
chosen seed.

Building these functions requires human insight in: a) picking a set of symbolic
inputs that sufficiently generalize both question and answer, b) encoding any implicit
constraints on the inputs in the generator function and that the generator explores
the input space as the seed is varied, c) translating the text of the specific question
and answer, into a respective functions problem and solution that symbolically derive
with the same steps as would have been followed in the derivation of answer from
question.

# Functional variants of a benchmark 
We call a benchmark, e.g., MATH, that
has its test set converted from static “question, answer” form into functionals as
above the functional variant, noted as MATH(). Each test in the functional variant
cannot be directly used to evaluate, but instead it needs to be instantiated.

# Snapshots 
We call an instantiation of each of the functionalized tests using a seed
a snapshot of the benchmark. For our implementation, we use a hash of the month
string, e.g., “Dec-2023”, combined with a hash of the original text QA, as the seed.
When instantiated, each test in the snapshot has the same reasoning as the original
test but the steps to the answer will be different. We can run the evaluation scripts
unmodified from the original benchmark over the snapshot.
Functional accuracy We define the functional accuracy as the accuracy of solving a test in all k snapshots and the static variant. If a model arrives at an answer
given a question, using proper reasoning, then its outcome should be identical over
the static benchmark as well as each snapshot of the functional variant. Thus we
define the functional accuracy of the model against that benchmark as the fraction
of tests it gets correct over k-snapshots and the static variant.
Reasoning Gap The reasoning gap is the percent decrease in the accuracy between the static and functional variants.
Example of functionalizing a test Figure 1 shows an example text QA from
the counting and probability subset of the MATH test dataset, that is solved in its
static form by GPT4. While it is not a particularly complicated counting calculation, it does require more than grade school reasoning of realizing that the problem
6

Text problem:
The letters of the word ‘SIXTEEN’ are randomly arranged.
What is the probability that the two E’s are not next to each other?
Text solution:
The best way to do this is to find the probability that the
two E’s are next to each other. There are $\\dfrac{7!}{2}$
arrangements of the word SIXTEEN. If we want to find the number
of arrangements such that the E’s are next to each other, we find
the number of arrangements of the six-letter word SIXT(EE)N
(where we treat the two E’s as a block), which is $6!$.
So the probability that an arrangement of the word SIXTEEN
has the two E’s next to each other is
$\\dfrac{6!}{\\frac{7!}{2}} = \\dfrac{2}{7}$.
So the probability that the two E’s aren’t next to each other is
$1 - \\dfrac{2}{7} = \\boxed{\\dfrac{5}{7}}$.
Figure 1: Example of a text QA from the MATH test data (Counting and Probability, 714.json). Note that the evaluation suite only compares the correctness of
the output text enclosed in “\\boxed{..}” in this case the correct answer would be
“\\dfrac{5}{7}” .

can be translated into its negated form, followed by canceling of major terms in the
permutation. While it is not impossible that a model would do step-by-step reasoning of such form if it has seen the logic before, inventing that line of reasoning from
first principles would be surprising. We convert it to a functional test as shown in
Figure 2. Of the three snapshots we take of this, GPT4 solved 1/3 of them.
Figure 3 shows an example text QA from the prealgebra subset of the MATH test
dataset, also solved in its static form by GPT4. Figure 4 shows its corresponding
functionalization. GPT4 reports “NO SOLUTION” for each of the snapshots, which
it has been instructed to do if it does not know the answer, indicating that its answer
to the static version was adding spurious accuracy. While hallucinations are not
the core focus of this work, we also test how many times the models report NO
SOLUTION, which they rarely do, and this is one of the rare occasions.