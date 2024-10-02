import difflib
import random
import numpy as np
from .utils import single_char_variable, replace_map, variation
import os
import json
from . import generators


@variation(
    year='2015', id='A2',
    generators={
        'var_a': generators.RandomVariable('lower'),
        'var_n': generators.RandomVariable('lower'),
        'num': generators.RandomInt(0,100)
    },
    original_params={
        'var_a' : 'a', 'var_n' : 'n', 'num' : 403
    }
)
def putnam_2015a2(
    var_a: str = 'a', var_n: str = 'n', num: int = 403
) -> dict:
  #WARNING: The answer generated for this question may not be the **only** possible answer. Evaluate with caution.
  '''Let $a_0=1$, $a_1=2$, and $a_n=4a_{n-1}-a_{n-2}$ for $n\\geq 2$. Find an odd prime factor of $a_{2015}$.'''
  # assert num % 5 == 0 and (num/5) % 2 == 1, f'Error: {num} must be an odd multiple of 5.'
  num = num * 5
  def a(n):
    answers = []
    answers.append(1)
    answers.append(2)
    for i in range(2,n+1):
      answers.append(4*answers[i-1] - answers[i-2])
    return answers[n]

  functional_q: str = f'Consider the sequence defined by ${var_a}_0=1$, ${var_a}_1=2$, and ${var_a}_{var_n}=4{var_a}_{{{var_n}-1}}-{var_a}_{{{var_n}-2}}$ for ${var_n}\\geq 2$. Determine the smallest odd prime factor of ${var_a}_{{{num}}}$.'
  functional_ans: str = f'By induction, we have ${var_a}_{var_n} = ((2+\\sqrt{{3}})^{var_n}+(2-\\sqrt{{3}})^{var_n})/2 = (\\alpha^{var_n}+\\beta^{var_n})/2$ for all ${var_n}$, where $\\alpha = 2+\\sqrt{{3}}$ and $\\beta = 2-\\sqrt{{3}}$. Now note that if $k$ is an odd positive integer and ${var_a}_{var_n} \\neq 0$, then $\\frac{{{var_a}_{{k{var_n}}}}}{{{var_a}_{var_n}}} = \\frac{{\\alpha^{{k{var_n}}}+\\beta^{{k{var_n}}}}}{{\\alpha^{var_n}+\\beta^{var_n}}} = \\alpha^{{(k-1){var_n}}}-\\alpha^{{(k-2){var_n}}}\\beta^{var_n}+\\cdots-\\alpha^{var_n}\\beta^{{(k-2){var_n}}}+\\beta^{{(k-1){var_n}}}$. This expression is both rational (because ${var_a}_{var_n}$ and ${var_a}_{{k{var_n}}}$ are integers) and of the form $a+b\\sqrt{{3}}$ for some integers $a,b$ by the expressions for $\\alpha,\\beta$; it follows that it must be an integer, and so ${var_a}_{{k{var_n}}}$ is divisible by ${var_a}_{var_n}$. Applying this to ${var_n}=5$ and $k=403$, we find that ${var_a}_{{{num}}}$ is divisible by ${var_a}_5 = 362$ and thus by $181$. The answer is $\\boxed{{181}}$.'
  return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }
