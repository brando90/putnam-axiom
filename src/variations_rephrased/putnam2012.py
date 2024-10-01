import difflib
import random
import numpy as np
from .utils import single_char_variable, replace_map, variation
import os
import json
from . import generators

@variation(year='2012', id='B4', 
    generators = {
        'a0' : generators.RandomInt(0,100),
        'a' : generators.RandomVariable('lower'),
    },
    original_params={
    'a0' : 1, 'a' : 'a'
})

def putnam_2012b4(
    a0 : int = 1, a : str = 'a'
) -> dict:

  # -- Formulate the questions
  functional_q : str = f'Suppose that ${a}_0 = {a0}$ and that ${a}_{{n+1}} = {a}_n + e^{{-{a}_n}}$ for $n=0,1,2,\\dots$. Does ${a}_n - \\log n$ have a finite limit as $n \\to \\infty$? (Here $\\log n = \\log_e n = \\ln n$.) Give a yes or no answer.'

  # -- Now, make the answer string
  functional_ans: str = f'First note that for all $x>-1$, $e^x \\geq 1+x$ and thus \\begin{{equation}} \\label{{eq:log}} x \\geq \\log(1+x). \\end{{equation}} We next claim that ${a}_n > \\log(n+1)$ (and in particular that ${a}_n-\\log n > 0$) for all $n$, by induction on $n$. For $n=0$ this follows from ${a}_0={a0}$. Now suppose that ${a}_n > \\log(n+1)$, and define $f(x) = x+e^{{-x}}$, which is an increasing function in $x>0$; then \\begin{{align*}} a_{{n+1}} &= f({a}_n) > f(\\log(n+1)) \\\\ &= \\log(n+1) + 1/(n+1) \\geq \\log(n+2), \\end{{align*}} where the last inequality is \\eqref{{eq:log}} with $x=1/(n+1)$. This completes the induction step.  It follows that ${a}_n-\\log n$ is a decreasing function in $n$: we have \\begin{{align*}} &({a}_{{n+1}} - \\log(n+1)) - ({a}_n - \\log n) \\\\ &\\,= e^{{-{a}_n}} + \\log(n/(n+1)) \\\\ &\\,< 1/(n+1) + \\log(n/(n+1)) \\leq 0, \\end{{align*}} where the final inequality is \\eqref{{eq:log}} with $x = -1/(n+1)$. Thus $\\{{{a}_n-\\log n\\}}_{{n=0}}^\\infty$ is a decreasing sequence of positive numbers, and so it has a limit as $n\\to\\infty$. We will show that the answer is \\boxed{{yes}}.'

  return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }
