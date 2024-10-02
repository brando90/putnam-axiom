import difflib
import random
import numpy as np
from .utils import single_char_variable, replace_map, variation
import os
import json
from . import generators
dataset = {}


def check_and_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' was created.")
    else:
        print(f"Folder '{folder_path}' already exists.")


def add_variation_to_dataset(question_index, category, variation_type, question, answer):
    question_index_str = str(question_index)

    if question_index_str not in dataset:
        dataset[question_index_str] = {
            "category": category,
            "variation_type": variation_type,
            "variations": []
        }

    dataset[question_index_str]["variations"].append({"question": question, "answer": answer})


def save_dataset_to_file(file_path):
    with open(file_path, 'w') as json_file:
        json.dump(dataset, json_file, indent=4)
    print(f"Dataset written to {file_path}.")

# @variation(
#     year='2006', id='A3',
#     generators={
#         'c_2006' : generators.RandomInt(10, 100000)
#     },
#     original_params={
#         'c_2006' : 2006
#     }
# )
# def putnam_2006a3(
#     c_2006: int = 2006
# ) -> dict:
#   assert c_2006 > 3, f'Error: Constant must be positive and greater than 3 for an actually challenging problem.'

#   # -- Formulate the questions
#   original_q: str = 'Let $1, 2, 3, \\dots, 2005, 2006, 2007, 2009, 2012, 2016, \\dots$ be a sequence defined by $x_k = k$ for $k=1, 2, \\dots, 2006$ and $x_{k+1} = x_k + x_{k-2005}$ for $k \\geq 2006$. Show that the sequence has 2005 consecutive terms each divisible by 2006.'
#   functional_q : str = f'Let $1, 2, 3, \\dots, {c_2006-1}, {c_2006}, {c_2006+1}, {c_2006+3}, {c_2006+6}, {c_2006 + 10}, \\dots$ be a sequence defined by $x_k = k$ for $k=1, 2, \\dots, {c_2006}$ and $x_{{k+1}} = x_k + x_{{k-{c_2006-1}}}$ for $k \\geq {c_2006}$. Show that the sequence has {c_2006-1} consecutive terms each divisible by {c_2006}.'

#   # -- Now, make the answer string
#   original_ans: str = 'We first observe that given any sequence of integers $x_1, x_2, \\dots$ satisfying a recursion \\[ x_k = f(x_{k-1}, \\dots, x_{k-n}) \\qquad (k > n), \\] where $n$ is fixed and $f$ is a fixed polynomial of $n$ variables with integer coefficients, for any positive integer $N$, the sequence modulo $N$ is eventually periodic. This is simply because there are only finitely many possible sequences of $n$ consecutive values modulo $N$, and once such a sequence is repeated, every subsequent value is repeated as well.  We next observe that if one can rewrite the same recursion as \\[ x_{k-n} = g(x_{k-n+1}, \\dots, x_k) \\qquad (k > n), \\] where $g$ is also a polynomial with integer coefficients, then the sequence extends uniquely to a doubly infinite sequence $\\dots, x_{-1}, x_0, x_1, \\dots$ which is fully periodic modulo any $N$. That is the case in the situation at hand, because we can rewrite the given recursion as \\[ x_{k-2005} = x_{k+1} - x_k. \\] It thus suffices to find 2005 consecutive terms divisible by $N$ in the doubly infinite sequence, for any fixed $N$ (so in particular for $N = 2006$). Running the recursion backwards, we easily find \\begin{gather*} x_1 = x_0 = \\cdots = x_{-2004} = 1 \\\\ x_{-2005} = \\cdots = x_{-4009} = 0, \\end{gather*} yielding the desired result.'
#   functional_ans: str = f'''We first observe that given any sequence of integers $x_1, x_2, \\dots$ satisfying a recursion \\[ x_k = f(x_{{k-1}}, \\dots, x_{{k-n}}) \\qquad (k > n), \\] where $n$ is fixed and $f$ is a fixed polynomial of $n$ variables with integer coefficients, for any positive integer $N$, the sequence modulo $N$ is eventually periodic. This is simply because there are only finitely many possible sequences of $n$ consecutive values modulo $N$, and once such a sequence is repeated, every subsequent value is repeated as well.  We next observe that if one can rewrite the same recursion as \\[ x_{{k-n}} = g(x_{{k-n+1}}, \\dots, x_k) \\qquad (k > n), \\] where $g$ is also a polynomial with integer coefficients, then the sequence extends uniquely to a doubly infinite sequence $\\dots, x_{{-1}}, x_0, x_1, \\dots$ which is fully periodic modulo any $N$. That is the case in the situation at hand, because we can rewrite the given recursion as \\[ x_{{k-{c_2006-1}}} = x_{{k+1}} - x_k. \\] It thus suffices to find {c_2006-1} consecutive terms divisible by $N$ in the doubly infinite sequence, for any fixed $N$ (so in particular for $N = {c_2006}$). Running the recursion backwards, we easily find \\begin{{gather*}} x_1 = x_0 = \\cdots = x_{{-{c_2006-2}}} = 1 \\\\ x_{{-{c_2006-1}}} = \\cdots = x_{{-{2*c_2006 - 3}}} = 0, \\end{{gather*}} yielding the desired result.'''


#   return {
#         'problem' : functional_q,
#         'solution' : functional_ans,
#         'type' : "constant"
#     }

@variation(
    year='2006', id='B4',
    generators={
        'Z' : generators.RandomVariable("upper"),
        'V' : generators.RandomVariable("upper")
    },
    original_params={
        'Z' : 'Z',
        'V' : 'V'
    }
)
def putnam_2006b4(
    Z: str = 'Z', V: str = 'V'
) -> dict:
  functional_q : str = replace_map(
      (
        "Consider the set ${Z}$ consisting of points in $\\mathbb{R}^n$ where each coordinate is either 0 or 1. Consequently, ${Z}$ contains $2^n$ points, representing the vertices of a unit hypercube in $\\mathbb{R}^n$. "
       "For a given vector subspace ${V}$ of $\\mathbb{R}^n$, define ${Z}({V})$ as the count of points in ${Z}$ that are also in ${V}$. Given an integer $k$ such that $0 \\leq k \\leq n$, "
       "find the maximum possible value of ${Z}({V})$ among all $k$-dimensional vector subspaces ${V}$ of $\\mathbb{R}^n$. "
       "[Note: The proposers likely meant to use ${Z}({V})$ instead of ``the number of points in ${V} \\cap {Z}$'', but this does not affect the problem.]"
       ),
       {'{Z}' : Z, '{V}' : V}
  )
  
  # -- Now, make the answer string
  functional_ans: str = replace_map(
      ("More generally, we show that any affine $k$-dimensional plane in $\\mathbb{R}^n$ can contain at most $2^k$ points in ${Z}$. The proof is by induction on $k+n$; the case $k=n=0$ is clearly true.  "
       "Suppose that ${V}$ is a $k$-plane in $\\mathbb{R}^n$. Denote the hyperplanes $\\{x_n = 0\\}$ and $\\{x_n = 1\\}$ by ${V}_0$ and ${V}_1$, respectively. If ${V}\\cap {V}_0$ and ${V}\\cap {V}_1$ are each at most $(k-1)$-dimensional, "
       "then ${V}\\cap {V}_0\\cap {Z}$ and ${V}\\cap {V}_1 \\cap {Z}$ each have cardinality at most $2^{k-1}$ by the induction assumption, and hence ${V}\\cap {Z}$ has at most $2^k$ elements. Otherwise, if ${V}\\cap {V}_0$ or ${V}\\cap {V}_1$ is $k$-dimensional, "
       "then ${V} \\subset {V}_0$ or ${V}\\subset {V}_1$; now apply the induction hypothesis on ${V}$, viewed as a subset of $\\mathbb{R}^{n-1}$ by dropping the last coordinate. The maximum is $\\boxed{2^k}$, achieved for instance by the subspace \\[ \\{(x_1, \\dots, x_n) \\in \\mathbb{R}^n: x_1 = \\cdots = x_{n-k} = 0\\}. \\]"),
      {'{Z}' : Z, '{V}' : V}
  )

  return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }