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


@variation(year='2022', id='A1', 
    generators = {
        'a' : generators.RandomVariable('lower'),
        'b' : generators.RandomVariable('lower'),
        'k' : generators.RandomInt(1,50)
    },
    original_params={
    'a' : 'a', 'b' : 'b', 'k' : 1,
})
def putnam_2022a1(
        a: str = 'a', b: str = 'b', 
        k: int = '1', 
        # debug: bool = False
        ) -> dict:

    functional_q: str = replace_map(
        (
            "Determine all ordered pairs of real numbers $({a},{b})$ such that the line $y = {a}x+{b}$ intersects the curve $y = \\ln({k}+x^2)$ in exactly one point."
        ),
        {'{a}': a, '{b}': b, '{k}': k}
    )

    k_sqrt = (int) (k ** 0.5)
    k_frac = (int) (k_sqrt / k)
    two_k = 2 * k

    functional_q : str = replace_map(
        (
            "Given that 0 < |{a}| < {k_frac}, determine the two conditions on {b} such that the line $y = {a}x+{b}$ intersects the curve $y = \\ln({k}+x^2)$ in exactly one point. Give the final answer as a sum of the expressions {b} is conditioned on (eg. if the conditions are {b} < f({a}) and {b} > g({a}) then the final solution is f({a}) + g({a}))."
        ),
        {'{a}': a, '{b}': b, '{k}': k, '{k_sqrt}' : k_sqrt, '{k_frac}' : k_frac}
    )

    functional_ans: str = replace_map(
        (
            "Write $f(x) = \\ln({k}+x^2)$. Since the graph of $y=f(x)$ is symmetric under reflection in the $y$-axis, it suffices to consider the case ${a} \\geq 0$: $y={a}x+{b}$ and $y=-{a}x+{b}$ intersect $y=f(x)$ the same number of times. For ${a}=0$, by the symmetry of $y=f(x)$ and the fact that $f(x)> 0$ for all $x\\neq 0$ implies that the only line $y={b}$ that intersects $y=f(x)$ exactly once is the line $y=0$. "
            "We next observe that on $[0,\\infty)$, $f'(x) = \\frac{2x}{{k}+x^2}$ increases on $[0,{k_sqrt}]$ from $f'(0)=0$ to a maximum at $f'({k_sqrt})={k_frac}$," 
            " and then decreases on $[{k_sqrt},\\infty)$ with $\\lim_{x\\to\\infty} f'(x)=0$. In particular, $f'(x) \\leq {k_sqrt}$ for all $x$ (including $x<0$ since then $f'(x)<0$) and $f'(x)$ achieves each value in $(0,{k_frac})$ exactly twice on $[0,\\infty)$.  For ${a} \\geq {k_sqrt}$, we claim that any line $y={a}x+{b}$ intersects $y=f(x)$ exactly once." 
            " They must intersect at least once by the intermediate value theorem: for $x\\ll 0$, ${a}x+{b}<0<f(x)$, while for $x \\gg 0$, ${a}x+{b}>f(x)$ since $\\lim_{x\\to\\infty} \\frac{\\ln({k}+x^2)}{x} = 0$. On the other hand, they cannot intersect more than once: for ${a}>{k_sqrt}$, this follows from the mean value theorem, since $f'(x)<{a}$ for all $x$. For ${a}={k_sqrt}$, "
            " suppose that they intersect at two points $(x_0,y_0)$ and $(x_1,y_1)$. Then \\[ {k_sqrt} = \\frac{y_1-y_0}{x_1-x_0} = \\frac{\\int_{x_0}^{x_1} f'(x)\\,dx}{x_1-x_0} < {k_sqrt} \\] since $f'(x)$ is continuous and $f'(x) \\leq {k_frac}$ with equality only at one point.  Finally we consider $0<{a}<{k_sqrt}$."
            " The equation $f'(x) = {a}$ has exactly two solutions, at $x=r_-$ and $x=r_+$ for $r_{\\pm}$ as defined above. If we define $g(x) = f(x)-{a}x$, then $g'(r_\\pm)=0$; $g'$ is strictly decreasing on $(-\\infty,r_-)$, strictly increasing on $(r_-,r_+)$, and strictly decreasing on $(r_+,\\infty)$; and $\\lim_{x\\to-\\infty} g(x) = \\infty$ while $\\lim_{x\\to\\infty} g(x) = -\\infty$." 
            " It follows that $g(x)={b}$ has exactly one solution for ${b}<g(r_-)$ or ${b}>g(r_+)$, exactly three solutions for $g(r_-)<{b}<g(r_+)$, and exactly two solutions for ${b} = g(r_\\pm)$. That is, $y={a}x+{b}$ intersects $y=f(x)$ in exactly one point if and only if ${b}<g(r_-)$ or ${b}>g(r_+)$. We thus show that $y={a}x+{b}$ intersects $y=f(x)$ in exactly one point for $0 < |{a}| < {k_frac}$" 
            " if and only if, and ${b}<\\ln(1 r_-)^2-|{a}|r_-$ or ${b}>\\ln(1-r_+)^2-|{a}|r_+$, where \\[r_\\pm = \\frac{1\\pm\\sqrt{1-{a}^{two_k}}}{{a}}.\\] thus making the final solution \\boxed{2 \\ln\\left(2 - \\frac{2}{{a}}\\right) - 2}."
        ),
        {'{a}': a, '{b}': b, '{k}': k, '{k_sqrt}' : k_sqrt, '{k_frac}' : k_frac, '{two_k}' : two_k}
        )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(year='2022', id='A3', 
    generators = {
        'p' : generators.RandomVariable('lower'),
        'a' : generators.RandomVariable('lower'),
        'f' : generators.RandomVariable('lower')
    },
    original_params={
    'p' : 'p', 'a' : 'a', 'f' : 'f'
})
def putnam_2022a3(
        p: str = 'p', a: str = 'a', f: str = 'f') -> dict:
    ''' 
    Let $p$ be a prime number greater than 5. Let $f(p)$ denote the number of infinite sequences $a_1, a_2, a_3, \\dots$ such that $a_n \\in \\{1, 2, \\dots, p-1\\}$ and $a_n a_{n+2} \\equiv 1 + a_{n+1} \\pmod{p}$ for all $n \\geq 1$. Prove that $f(p)$ is congruent to 0 or 2 $\\pmod{5}$.
    '''

    # # -- question
    # original_q: str = 'Let $p$ be a prime number greater than 5. Let $f(p)$ denote the number of infinite sequences $a_1, a_2, a_3, \\dots$ such that $a_n \\in \\{1, 2, \\dots, p-1\\}$ and $a_n a_{n+2} \\equiv 1 + a_{n+1} \\pmod{p}$ for all $n \\geq 1$. Prove that $f(p)$ is congruent to 0 or 2 $\\pmod{5}$.'
    # functional_q: str = f'''Let ${p}$ be a prime number greater than 5. Let $f({p})$ denote the number of infinite sequences ${a}_1, {a}_2, {a}_3, \\dots$ such that ${a}_n \\in \\{1, 2, \\dots, {p}-1\\}$ and ${a}_n {a}_{n+2} \\equiv 1 + {a}_{n+1} \\pmod{{p}}$ for all $n \\geq 1$. Prove that $f({p})$ is congruent to 0 or 2 $\\pmod{5}$.'''
    # if debug:
    #     assert original_q == functional_q, f'Error:\n\n {original_q}\n\n {functional_q}\n\n'

    functional_q : str = replace_map(
       ("Let ${p}$ be a prime number greater than 5. Let $f({p})$ denote the number of infinite sequences ${a}_1, {a}_2, {a}_3, \\dots$ such that ${a}_n \\in \\{1, 2, \\dots, {p}-1\\}$ "
        " and ${a}_n {a}_{n+2} \\equiv 1 + {a}_{n+1} \\pmod{{p}}$ for all $n \\geq 1$. What is the sum of all values that $f({p})$ can be congruent to modulo 5?"),
       {'{p}' : p, '{a}' : a}
    )

    # # -- boxed answer
    # original_ans: str = "We view the sequence $a_1,a_2,\\ldots$ as lying in $\\mathbb{F}_p^\\times \\subset \\mathbb{F}_p$.  Then the sequence is determined by the values of $a_1$ and $a_2$, via the recurrence $a_{n+2}=(1+a_{n+1})/a_n$.  Using this recurrence, we compute \\begin{gather*} a_3=\\frac{1 + a_2}{a_1}, \\, a_4 = \\frac{1 + a_1 + a_2}{a_1 a_2}, \\\\ a_5=\\frac{1 + a_1}{a_2}, \\, a_6 = a_1, \\, a_7 = a_2  \\end{gather*} and thus the sequence is periodic with period 5.  The values for $a_1$ and $a_2$ may thus be any values in $\\mathbb{F}_p^\\times$ provided that $a_1\\neq p-1$, $a_2\\neq p-1$, and $a_1+a_2\\neq p-1$.  The number of choices for $a_1,a_2\\in\\{1,\\ldots,p-2\\}$ such that $a_1+a_2\\neq p-1$ is thus $(p-2)^2 - (p-2)= (p-2)(p-3)$.  Since $p$ is not a multiple of 5, $(p-2)(p-3)$ is a product of two consecutive integers $a,a+1$, where $a\\not\\equiv 2 \\pmod{5}$. Now $0\\cdot 1\\equiv 0$, $1\\cdot 2 \\equiv 2$, $3\\cdot 4\\equiv 2$, and $4\\cdot 0 \\equiv 0$ (mod 5).  Thus the number of possible sequences $a_1,a_2,\\ldots$ is 0 or 2 (mod 5), as desired.   \\noindent"
    # #no python code to change final boxed answer since it's too hard to generate new q
    # functional_ans: str = f'''We view the sequence ${a}_1,{a}_2,\\ldots$ as lying in $\\mathbb{F}_{p}^\\times \\subset \\mathbb{F}_{p}$.  Then the sequence is determined by the values of ${a}_1$ and ${a}_2$, via the recurrence ${a}_{n+2}=(1+{a}_{n+1})/{a}_n$.  Using this recurrence, we compute \\begin{gather*} {a}_3=\\frac{1 + {a}_2}{{a}_1}, \\, {a}_4 = \\frac{1 + {a}_1 + {a}_2}{{a}_1 {a}_2}, \\\\ {a}_5=\\frac{1 + {a}_1}{{a}_2}, \\, {a}_6 = {a}_1, \\, {a}_7 = {a}_2  \\end{gather*} and thus the sequence is periodic with period 5.  The values for ${a}_1$ and ${a}_2$ may thus be any values in $\\mathbb{F}_{p}^\\times$ provided that ${a}_1\\neq {p}-1$, ${a}_2\\neq {p}-1$, and ${a}_1+{a}_2\\neq {p}-1$.  The number of choices for ${a}_1,{a}_2\\in\\{1,\\ldots,{p}-2\\}$ such that ${a}_1+{a}_2\\neq {p}-1$ is thus $({p}-2)^2 - ({p}-2)= ({p}-2)({p}-3)$.  Since ${p}$ is not a multiple of 5, $({p}-2)({p}-3)$ is a product of two consecutive integers ${a},{a}+1$, where ${a}\\not\\equiv 2 \\pmod{5}$. Now $0\\cdot 1\\equiv 0$, $1\\cdot 2 \\equiv 2$, $3\\cdot 4\\equiv 2$, and $4\\cdot 0 \\equiv 0$ (mod 5).  Thus the number of possible sequences ${a}_1,{a}_2,\\ldots$ is 0 or 2 (mod 5), as desired.   \\noindent'''
    # if debug:
    #     assert original_ans == functional_ans, f'Error:\n\n {original_ans}\n\n {functional_ans}\n\n'

    functional_ans : str = replace_map(
       ("We view the sequence ${a}_1,{a}_2,\\ldots$ as lying in $\\mathbb{F}_{p}^\\times \\subset \\mathbb{F}_{p}$.  Then the sequence is determined by the values of ${a}_1$ and ${a}_2$, via the recurrence ${a}_{n+2}=(1+{a}_{n+1})/{a}_n$."  
        " Using this recurrence, we compute \\begin{gather*} {a}_3=\\frac{1 + {a}_2}{{a}_1}, \\, {a}_4 = \\frac{1 + {a}_1 + {a}_2}{{a}_1 {a}_2}, \\\\ {a}_5=\\frac{1 + {a}_1}{{a}_2}, \\, {a}_6 = {a}_1, \\, {a}_7 = {a}_2  \\end{gather*} and thus the sequence is periodic with period 5."  
        " The values for ${a}_1$ and ${a}_2$ may thus be any values in $\\mathbb{F}_{p}^\\times$ provided that ${a}_1\\neq {p}-1$, ${a}_2\\neq {p}-1$, and ${a}_1+{a}_2\\neq {p}-1$.  The number of choices for ${a}_1,{a}_2\\in\\{1,\\ldots,{p}-2\\}$ such that ${a}_1+{a}_2\\neq {p}-1$ is thus $({p}-2)^2 - ({p}-2)= ({p}-2)({p}-3)$."  
        " Since ${p}$ is not a multiple of 5, $({p}-2)({p}-3)$ is a product of two consecutive integers ${a},{a}+1$, where ${a}\\not\\equiv 2 \\pmod{5}$. Now $0\\cdot 1\\equiv 0$, $1\\cdot 2 \\equiv 2$, $3\\cdot 4\\equiv 2$, and $4\\cdot 0 \\equiv 0$ (mod 5).  Thus the number of possible sequences ${a}_1,{a}_2,\\ldots$ is 0 or 2 (mod 5), as desired giving us the final sum to be \\boxed{2}."),
       {'{p}' : p, '{a}' : a}
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


@variation(year='2022', id='A5', 
    generators = {
        'n' : generators.RandomInt(0,100000)
    },
    original_params={
    'n' : 2022
})
def putnam_2022a5(
    n: int = 2022
) -> dict:
  person_a = 'Alice'
  person_b = 'Bob'
  functional_q : str = replace_map(
      ("{person_a} and {person_b} play a game on a board consisting of one row of {n} consecutive squares. They take turns placing tiles that cover two adjacent squares, with {person_a} going first." 
       " By rule, a tile must not cover a square that is already covered by another tile. The game ends when no tile can be placed according to this rule. {person_a}\'s goal is to maximize the number of uncovered squares when the game ends;" 
       " {person_b}\'s goal is to minimize it. What is the greatest number of uncovered squares that {person_a} can ensure at the end of the game, no matter how {person_b} plays?"),
      {'{person_a}' : person_a, '{person_b}' : person_b, '{n}' : n}
  )

  ans = None
  less_than_6 = np.array([0,1,0,1,2,1,2])
  if (n <= 6):
    ans = less_than_6[n]
  else:
    ans = n//7 + less_than_6[n - 7 * (n//7)]

  # # -- Now, make the answer string
  # original_ans: str = 'We show that the number in question equals \\boxed{290}. More generally, let $a(n)$ (resp.\\ $b(n)$) be the optimal final score for Alice (resp.\\ Bob) moving first in a position with $n$ consecutive squares. We show that \\begin{align*} a(n) &= \\left\\lfloor \\frac{n}{7} \\right\\rfloor + a\\left(n - 7\\left\\lfloor \\frac{n}{7} \\right\\rfloor \\right), \\\\ b(n) &= \\left\\lfloor \\frac{n}{7} \\right\\rfloor + b\\left(n - 7\\left\\lfloor \\frac{n}{7} \\right\\rfloor \\right), \\end{align*} and that the values for $n \\leq 6$ are as follows: \\[ \\begin{array}{c|cccccccccc} n & 0 & 1 & 2 & 3 & 4 & 5 & 6 \\\\ \\hline a(n) & 0 & 1 & 0 & 1 & 2 & 1 & 2  \\\\ b(n) & 0 & 1 & 0 & 1 & 0 & 1 & 0  \\end{array} \\] Since $2022 \\equiv 6 \\pmod{7}$, this will yield $a(2022) = 2 + \\lfloor \\frac{2022}{7} \\rfloor = 290$.  We proceed by induction, starting with the base cases $n \\leq 6$. Since the number of odd intervals never decreases, we have $a(n), b(n) \\geq n - 2 \\lfloor \\frac{n}{2} \\rfloor$; by looking at the possible final positions, we see that equality holds for $n=0,1,2,3,5$. For $n=4,6$, Alice moving first can split the original interval into two odd intervals, guaranteeing at least two odd intervals in the final position; whereas Bob can move to leave behind one or two intervals of length 2, guaranteeing no odd intervals in the final position.  We now proceed to the induction step. Suppose that $n \\geq 7$ and the claim is known for all $m < n$. In particular, this means that $a(m) \\geq b(m)$; consequently, it does not change the analysis to allow a player to pass their turn after the first move, as both players will still have an optimal strategy which involves never passing.  It will suffice to check that \\[ a(n) = a(n-7) + 1, \\qquad b(n) = b(n-7) + 1. \\] Moving first, Alice can leave behind two intervals of length 1 and $n-3$. This shows that \\[ a(n) \\geq 1 + b(n-3) = a(n-7) + 1. \\] On the other hand, if Alice leaves behind intervals of length $i$ and $n-2-i$, Bob can choose to play in either one of these intervals and then follow Alice\'s lead thereafter (exercising the pass option if Alice makes the last legal move in one of the intervals).  This shows that \\begin{align*} a(n) &\\leq \\max\\{\\min\\{a(i) + b(n-2-i), \\\\ & \\qquad b(i)+a(n-2-i)\\}: i =0,1,\\dots,n-2\\} \\\\ &= a(n-7)+1. \\end{align*}  Moving first, Bob can leave behind two intervals of lengths 2 and $n-4$. This shows that \\[ b(n) \\leq a(n-4) = b(n-7) + 1. \\] On the other hand, if Bob leaves behind intervals of length $i$ and $n-2-i$, Alice can choose to play in either one of these intervals and then follow Bob\'s lead thereafter (again passing as needed). This shows that \\begin{align*} b(n) &\\geq \\min\\{\\max\\{a(i) + b(n-2-i), \\\\ & \\qquad b(i)+a(n-2-i)\\}: i =0,1,\\dots,n-2\\} \\\\ &= b(n-7)+1. \\end{align*} This completes the induction.'
  # functional_ans: str = f'''We show that the number in question equals \\boxed{{{ans}}}. More generally, let $a(n)$ (resp.\\ $b(n)$) be the optimal final score for {person_a} (resp.\\ {person_b}) moving first in a position with $n$ consecutive squares. We show that \\begin{{align*}} a(n) &= \\left\\lfloor \\frac{{n}}{{7}} \\right\\rfloor + a\\left(n - 7\\left\\lfloor \\frac{{n}}{{7}} \\right\\rfloor \\right), \\\\ b(n) &= \\left\\lfloor \\frac{{n}}{{7}} \\right\\rfloor + b\\left(n - 7\\left\\lfloor \\frac{{n}}{{7}} \\right\\rfloor \\right), \\end{{align*}} and that the values for $n \\leq 6$ are as follows: \\[ \\begin{{array}}{{c|cccccccccc}} n & 0 & 1 & 2 & 3 & 4 & 5 & 6 \\\\ \\hline a(n) & 0 & 1 & 0 & 1 & 2 & 1 & 2  \\\\ b(n) & 0 & 1 & 0 & 1 & 0 & 1 & 0  \\end{{array}} \\] Since ${n} \\equiv 6 \\pmod{{7}}$, this will yield $a({n}) = 2 + \\lfloor \\frac{{{n}}}{{7}} \\rfloor = {ans}$.  We proceed by induction, starting with the base cases $n \\leq 6$. Since the number of odd intervals never decreases, we have $a(n), b(n) \\geq n - 2 \\lfloor \\frac{{n}}{{2}} \\rfloor$; by looking at the possible final positions, we see that equality holds for $n=0,1,2,3,5$. For $n=4,6$, {person_a} moving first can split the original interval into two odd intervals, guaranteeing at least two odd intervals in the final position; whereas {person_b} can move to leave behind one or two intervals of length 2, guaranteeing no odd intervals in the final position.  We now proceed to the induction step. Suppose that $n \\geq 7$ and the claim is known for all $m < n$. In particular, this means that $a(m) \\geq b(m)$; consequently, it does not change the analysis to allow a player to pass their turn after the first move, as both players will still have an optimal strategy which involves never passing.  It will suffice to check that \\[ a(n) = a(n-7) + 1, \\qquad b(n) = b(n-7) + 1. \\] Moving first, {person_a} can leave behind two intervals of length 1 and $n-3$. This shows that \\[ a(n) \\geq 1 + b(n-3) = a(n-7) + 1. \\] On the other hand, if {person_a} leaves behind intervals of length $i$ and $n-2-i$, {person_b} can choose to play in either one of these intervals and then follow {person_a}'s lead thereafter (exercising the pass option if {person_a} makes the last legal move in one of the intervals).  This shows that \\begin{{align*}} a(n) &\\leq \\max\\{{\\min\\{{a(i) + b(n-2-i), \\\\ & \\qquad b(i)+a(n-2-i)\\}}: i =0,1,\\dots,n-2\\}} \\\\ &= a(n-7)+1. \\end{{align*}}  Moving first, {person_b} can leave behind two intervals of lengths 2 and $n-4$. This shows that \\[ b(n) \\leq a(n-4) = b(n-7) + 1. \\] On the other hand, if {person_b} leaves behind intervals of length $i$ and $n-2-i$, {person_a} can choose to play in either one of these intervals and then follow {person_b}'s lead thereafter (again passing as needed). This shows that \\begin{{align*}} b(n) &\\geq \\min\\{{\\max\\{{a(i) + b(n-2-i), \\\\ & \\qquad b(i)+a(n-2-i)\\}}: i =0,1,\\dots,n-2\\}} \\\\ &= b(n-7)+1. \\end{{align*}} This completes the induction.'''
  # if debug:
  #   assert original_ans == functional_ans, f'Error:\n\n {original_ans}\n\n {functional_ans}\n\n'
  
  var_n = 'n'

  functional_ans : str = replace_map(
      ("More generally, let $a(n)$ (resp.\\ $b(n)$) be the optimal final score for {person_a} (resp.\\ {person_b}) moving first in a position with $n$ consecutive squares. " 
       "We show that \\begin{align*} a(n) &= \\left\\lfloor \\frac{{var_n}}{7} \\right\\rfloor + a\\left(n - 7\\left\\lfloor \\frac{{var_n}}{7} \\right\\rfloor \\right), \\\\ b(n) &= \\left\\lfloor \\frac{{var_n}}{7} \\right\\rfloor + b\\left(n - 7\\left\\lfloor \\frac{{var_n}}{7} \\right\\rfloor \\right), \\end{align*} " 
       "and that the values for $n \\leq 6$ are as follows: \\[ \\begin{array}{c|cccccccccc} n & 0 & 1 & 2 & 3 & 4 & 5 & 6 \\\\ \\hline a(n) & 0 & 1 & 0 & 1 & 2 & 1 & 2  \\\\ b(n) & 0 & 1 & 0 & 1 & 0 & 1 & 0  \\end{array} \\] Since ${n} \\equiv 6 \\pmod{7}$, this will yield $a({n}) = 2 + \\lfloor \\frac{{n}}{7} \\rfloor = {ans}$. "  
       "We proceed by induction, starting with the base cases $n \\leq 6$. Since the number of odd intervals never decreases, we have $a(n), b(n) \\geq n - 2 \\lfloor \\frac{{var_n}}{2} \\rfloor$; by looking at the possible final positions, we see that equality holds for $n=0,1,2,3,5$. " 
       "For $n=4,6$, {person_a} moving first can split the original interval into two odd intervals, guaranteeing at least two odd intervals in the final position; whereas {person_b} can move to leave behind one or two intervals of length 2, guaranteeing no odd intervals in the final position. "  
       "We now proceed to the induction step. Suppose that $n \\geq 7$ and the claim is known for all $m < n$. In particular, this means that $a(m) \\geq b(m)$; consequently, it does not change the analysis to allow a player to pass their turn after the first move, as both players will still have an optimal strategy which involves never passing. "  
       "It will suffice to check that \\[ a(n) = a(n-7) + 1, \\qquad b(n) = b(n-7) + 1. \\] Moving first, {person_a} can leave behind two intervals of length 1 and $n-3$. This shows that \\[ a(n) \\geq 1 + b(n-3) = a(n-7) + 1. \\] On the other hand, if {person_a} leaves behind intervals of length $i$ and $n-2-i$, " 
       "{person_b} can choose to play in either one of these intervals and then follow {person_a}'s lead thereafter (exercising the pass option if {person_a} makes the last legal move in one of the intervals).  This shows that \\begin{align*} a(n) &\\leq \\max\\{\\min\\{a(i) + b(n-2-i), \\\\ & \\qquad b(i)+a(n-2-i)\\}: i =0,1,\\dots,n-2\\} \\\\ &= a(n-7)+1. \\end{align*} "  
       "Moving first, {person_b} can leave behind two intervals of lengths 2 and $n-4$. This shows that \\[ b(n) \\leq a(n-4) = b(n-7) + 1. \\] On the other hand, if {person_b} leaves behind intervals of length $i$ and $n-2-i$, {person_a} can choose to play in either one of these intervals and then follow {person_b}'s lead thereafter (again passing as needed). " 
       "This shows that \\begin{align*} b(n) &\\geq \\min\\{\\max\\{a(i) + b(n-2-i), \\\\ & \\qquad b(i)+a(n-2-i)\\}: i =0,1,\\dots,n-2\\} \\\\ &= b(n-7)+1. \\end{align*} This completes the induction. We show that the number in question equals \\boxed{{ans}}."),
      {'{person_a}' : person_a, '{person_b}' : person_b, '{n}' : n, '{ans}': ans, '{var_n}' : var_n}
  )

  return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(year='2022', id='A6', 
    generators = {
        'n' : generators.RandomVariable('lower'),
        'm' : generators.RandomVariable('lower'),
        'x' : generators.RandomVariable('lower'),
        'k' : generators.RandomVariable('lower')
    },
    original_params={
    'n' : 'n', 'm' : 'm', 'x' : 'x', 'k' : 'k'
})
def putnam_2022a6(
        n: str = 'n', m: str = 'm', x: str = 'x', k: str = 'k') -> dict:

    functional_q : str = replace_map(
       ("Let ${n}$ be a positive integer. Determine, in terms of ${n}$, the largest integer ${m}$ with the following property: There exist real numbers ${x}_1,\\dots,{x}_{2{n}}$ with $-1 < {x}_1 < {x}_2 < \\cdots < {x}_{2{n}} < 1$" 
        " such that the sum of the lengths of the ${n}$ intervals \\[ [{x}_1^{2{k}-1}, {x}_2^{2{k}-1}], [{x}_3^{2{k}-1},{x}_4^{2{k}-1}], \\dots, [{x}_{2{n}-1}^{2{k}-1}, {x}_{2{n}}^{2{k}-1}] \\] is equal to 1 for all integers ${k}$ with" 
        " $1 \\leq {k} \\leq {m}$."),
       {'{n}' : n, '{m}' : m, '{x}' : x, '{k}' : k}
    )

    functional_ans : str = replace_map(
       ("To show that ${m} \\geq {n}$, we take \\[ {x}_j = \\cos \\frac{(2{n}+1-j)\\pi}{2{n}+1} \\qquad (j=1,\\dots,2{n}). \\] It is apparent that $-1 < {x}_1 < \\cdots < {x}_{2{n}} < 1$. The sum of the lengths of the intervals can be interpreted as " 
        "\\begin{align*} & -\\sum_{j=1}^{2{n}} ((-1)^{2{n}+1-j} {x}_j)^{2{k}-1} \\\\ &= -\\sum_{j=1}^{2{n}} \\left(\\cos (2{n}+1-j)\\left(\\pi + \\frac{\\pi}{2{n}+1} \\right)\\right)^{2{k}-1} \\\\ &= -\\sum_{j=1}^{2{n}} \\left(\\cos \\frac{2\\pi({n}+1)j}{2{n}+1}\\right)^{2{k}-1}. \\end{align*} " 
        "For $\\zeta = e^{2 \\pi i ({n}+1)/(2{n}+1)}$, this becomes \\begin{align*} &= -\\sum_{j=1}^{2{n}} \\left( \\frac{\\zeta^j + \\zeta^{-j}}{2} \\right)^{2{k}-1} \\\\ &= -\\frac{1}{2^{2{k}-1}}\\sum_{j=1}^{2{n}} \\sum_{l=0}^{2{k}-1}  \\binom{2{k}-1}{l} \\zeta^{j(2{k}-1-2l)} \\\\ &= -\\frac{1}{2^{2{k}-1}} \\sum_{l=0}^{2{k}-1} \\binom{2{k}-1}{l} \\sum_{j=1}^{2{n}} \\zeta^{j(2{k}-1-2l)} "  
        "\\\\ &= -\\frac{1}{2^{2{k}-1}} \\sum_{l=0}^{2{k}-1} \\binom{2{k}-1}{l} (-1) = 1, \\end{align*} using the fact that $\\zeta^{2{k}-1-2l}$ is a \\emph{nontrivial} root of unity of order dividing $2{n}+1$.  To show that ${m} \\leq {n}$, we use the following lemma. We say that a multiset $\\{{x}_1,\\dots,{x}_{m}\\}$ of complex numbers is \\emph{inverse-free} if there are no two indices " 
        "$1 \\leq i \\leq j \\leq {m}$ such that ${x}_i + {x}_j = 0$; this implies in particular that 0 does not occur. \\begin{lemma*} Let $\\{{x}_1,\\dots,{x}_{m}\\},\\{y_1,\\dots,y_{n}\\}$ be two inverse-free multisets of complex numbers such that \\[ \\sum_{i=1}^{m} {x}_i^{2{k}-1} = \\sum_{i=1}^{n} y_i^{2{k}-1} \\qquad ({k}=1,\\dots,\\max\\{{m},{n}\\}). \\] Then these two multisets are equal. \\end{lemma*} " 
        "\\begin{proof} We may assume without loss of generality that ${m} \\leq {n}$. Form the rational functions \\[ f(z) = \\sum_{i=1}^{m} \\frac{{x}_i z}{1 - {x}_i^2 z^2}, \\quad g(z) = \\sum_{i=1}^{n} \\frac{y_i z}{1 - y_i^2 z^2}; \\] both $f(z)$ and $g(z)$ have total pole order at most $2{n}$. Meanwhile, by expanding in power series around $z=0$, we see that $f(z)-g(z)$ is divisible by $z^{2{n}+1}$. " 
        "Consequently, the two series are equal.   However, we can uniquely recover the multiset $\\{{x}_1,\\dots,{x}_{m}\\}$ from $f(z)$: $f$ has poles at $\\{1/{x}_1^2,\\dots,1/{x}_{m}^2\\}$ and the residue of the pole at $z = 1/{x}_i^2$ uniquely determines both ${x}_i$ (i.e., its sign) and its multiplicity. Similarly, we may recover $\\{y_1,\\dots,y_{n}\\}$ from $g(z)$, so the two multisets must coincide. \\end{proof} "  
        "Now suppose by way of contradiction that we have an example showing that ${m} \\geq {n}+1$. We then have \\[ 1^{2{k}-1} + \\sum_{i=1}^{n} {x}_{2i-1}^{2{k}-1} = \\sum_{i=1}^{n} {x}_{2i}^{2{k}-1} \\qquad ({k}=1,\\dots,{n}+1). \\] By the lemma, this means that the multisets $\\{1,{x}_1,{x}_3,\\dots,{x}_{2{n}-1}\\}$ and $\\{{x}_2,{x}_4,\\dots,{x}_{2{n}}\\}$ become equal after removing pairs of inverses until this becomes impossible. " 
        "However, of the resulting two multisets, the first contains 1 and the second does not, yielding the desired contradiction. "
        "The largest such ${m}$ is $\\boxed{{n}}$."),
       {'{n}' : n, '{m}' : m, '{x}' : x, '{k}' : k}
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(year='2022', id='B3', 
    generators = {
        'D' : generators.RandomVariable('upper'),
        'd' : generators.RandomVariable('lower')
    },
    original_params={
    'D' : 'D', 'd' : 'd'
})
def putnam_2022b3(
        D: str = 'D', d: str = 'd') -> dict:

    functional_q : str = replace_map(
       ("Assign to each positive real number a color, either red or blue. Let ${D}$ be the set of all distances ${d} > 0$ such that there are two points of the same color at distance ${d}$ apart." 
        " Recolor the positive reals so that the numbers in ${D}$ are red and the numbers not in ${D}$ are blue. If we iterate this recoloring process, will we always end up with all the numbers red after a finite number of steps?"
        " Give a yes or no answer."),
       {'{D}' : D, '{d}' : d}
    )

    functional_ans : str = replace_map(
       ("Let $R_0,B_0 \\subset \\mathbb{R}^+$ be the set of red and blue numbers at the start of the process, and let $R_n,B_n$ be the set of red and blue numbers after $n$ steps. We claim that $R_2 = \\mathbb{R}^+$. "  
        "We first note that if $y \\in B_1$, then $y/2 \\in R_1$. Namely, the numbers $y$ and $2y$ must be of opposite colors in the original coloring, and then $3y/2$ must be of the same color as one of $y$ or $2y$. "   
        "Now suppose by way of contradiction that $x \\in B_2$. Then of the four numbers $x,2x,3x,4x$, every other number must be in $R_1$ and the other two must be in $B_1$. By the previous observation, $2x$ and $4x$ " 
        "cannot both be in $B_1$; it follows that $2x,4x \\in R_1$ and $x,3x \\in B_1$. By the previous observation again, $x/2$ and $3x/2$ must both be in $R_1$, but then $x = 3x/2-x/2$ is in $R_2$, contradiction. " 
        "We conclude that $R_2 = \\mathbb{R}^+$, as desired. The answer is \\boxed{yes}."),
       {'{D}' : D, '{d}' : d}
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(year='2022', id='B5',
    generators = {
        'X' : generators.RandomVariable('upper'),
        'n' : generators.RandomVariable('lower'),
        'a' : generators.RandomVariable('lower'),
        'b' : generators.RandomVariable('lower')
    },
    original_params={
    'X' : 'X', 'n' : 'n', 'a' : 'a', 'b' : 'b'
})
def putnam_2022b5(
        X: str = 'X', n: str = 'n', a: str = 'a', b : str = 'b') -> dict:

    functional_q : str = replace_map(
       ("For $0 \\leq p \\leq 1/2$, let ${X}_1, {X}_2, \\dots$ be independent random variables such that \\[ {X}_i = \\begin{cases} 1 & \\mbox{with probability $p$,} \\\\ -1 & \\mbox{with probability $p$,} \\\\ 0 & \\mbox{with probability $1-2p$,} \\end{cases} \\]" 
        " for all $i \\geq 1$. Given a positive integer ${n}$ and integers ${b}, {a}_1, \\dots, {a}_{n}$, let $P({b}, {a}_1, \\dots, {a}_{n})$ denote the probability that ${a}_1 {X}_1 + \\cdots + {a}_{n} {X}_{n} = {b}$. Find the maximum value of $p$ for which it is" 
        " the case that \\[ P(0, {a}_1, \\dots, {a}_{n}) \\geq P({b}, {a}_1, \\dots, {a}_{n}) \\] for all positive integers ${n}$ and all integers ${b}, {a}_1, \\dots, {a}_{n}$?"),
        {'{X}' : X, '{n}' : n, '{a}' : a, '{b}' : b}
    )

    functional_ans : str = replace_map(
       ("We first show that $p >1/4$ does not satisfy the desired condition. For $p>1/3$, $P(0,1) = 1-2p < p = P(1,1)$. For $p=1/3$, it is easily calculated (or follows from the next calculation) that $P(0,1,2) = 1/9 < 2/9 = P(1,1,2)$. Now suppose $1/4 < p < 1/3$, " 
        " and consider $({b},{a}_1,{a}_2,{a}_3,\\ldots,{a}_{n}) = (1,1,2,4,\\ldots,2^{{n}-1})$.  The only solution to \\[ {X}_1+2{X}_2+\\cdots+2^{{n}-1}{X}_{n} = 0 \\] with ${X}_j \\in \\{0,\\pm 1\\}$ is ${X}_1=\\cdots={X}_{n}=0$; thus $P(0,1,2,\\ldots,2^{2{n}-1}) = (1-2p)^{n}$. " 
        " On the other hand, the solutions to \\[ {X}_1+2{X}_2+\\cdots+2^{{n}-1}{X}_{n} = 1 \\] with ${X}_j \\in \\{0,\\pm 1\\}$ are  \\begin{gather*} ({X}_1,{X}_2,\\ldots,{X}_{n}) = (1,0,\\ldots,0),(-1,1,0,\\ldots,0), \\\\ (-1,-1,1,0,\\ldots,0), \\ldots, (-1,-1,\\ldots,-1,1), \\end{gather*} " 
        " and so \\begin{align*} &P(1,1,2,\\ldots,2^{{n}-1}) \\\\ & = p(1-2p)^{{n}-1}+p^2(1-2p)^{{n}-2}+\\cdots+p^{n} \\\\ &= p\\frac{(1-2p)^{{n}}-p^{{n}}}{1-3p}. \\end{align*} It follows that the inequality $P(0,1,2,\\ldots,2^{{n}-1}) \\geq P(1,1,2,\\ldots,2^{{n}-1})$ is equivalent to "  
        " \\[ p^{{n}+1} \\geq (4p-1)(1-2p)^{n}, \\] but this is false for sufficiently large $n$ since $4p-1>0$ and $p<1-2p$.  Now suppose $p \\leq 1/4$; we want to show that for arbitrary ${a}_1,\\ldots,{a}_{n}$ and ${b} \\neq 0$, $P(0,{a}_1,\\ldots,{a}_{n}) \\geq P({b},{a}_1,\\ldots,{a}_{n})$. " 
        " Define the polynomial \\[ f(x) = px+px^{-1}+1-2p,  \\] and observe that $P({b},{a}_1,\\ldots,{a}_{n})$ is the coefficient of $x^{b}$ in $f(x^{{a}_1})f(x^{{a}_2})\\cdots f(x^{{a}_{n}})$. We can write \\[ f(x^{{a}_1})f(x^{{a}_2})\\cdots f(x^{{a}_{n}}) = g(x)g(x^{-1}) \\] for some real polynomial $g$: " 
        " indeed, if we define $\\alpha = \\frac{1-2p+\\sqrt{1-4p}}{2p} > 0$, then $f(x) = \\frac{p}{\\alpha}(x+\\alpha)(x^{-1}+\\alpha)$, and so we can use \\[ g(x) = \\left(\\frac{p}{\\alpha}\\right)^{{n}/2} (x^{{a}_1}+\\alpha)\\cdots(x^{{a}_{n}}+\\alpha). \\]  It now suffices to show that in $g(x)g(x^{-1})$, " 
        " the coefficient of $x^0$ is at least as large as the coefficient of $x^{b}$ for any ${b} \\neq 0$. Since $g(x)g(x^{-1})$ is symmetric upon inverting $x$, we may assume that ${b} > 0$. If we write $g(x) = c_0 x^0 + \\cdots + c_m x^m$, then the coefficients of $x^0$ and $x^{b}$ in $g(x)g(x^{-1})$ are " 
        " $c_0^2+c_1^2+\\cdots+c_m^2$ and $c_0c_{b}+c_1c_{{b}+1}+\\cdots+c_{m-{b}}c_m$, respectively. But \\begin{align*} &2(c_0c_{b}+c_1c_{{b}+1}+\\cdots+c_{m-{b}}c_m)\\\\ &\\leq (c_0^2+c_{b}^2)+(c_1^2+c_{{b}+1}^2)+\\cdots+(c_{m-{b}}^2+c_m^2) \\\\ & \\leq 2(c_0^2+\\cdots+c_m^2), \\end{align*} " 
        " and the result follows. The answer is $\\boxed{1/4}$."),
       {'{X}' : X, '{n}' : n, '{a}' : a, '{b}' : b}
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }
