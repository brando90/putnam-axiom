import difflib
import random
import numpy as np
from .utils import single_char_variable, replace_map, variation
import os
import json
import math
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

@variation(
    year='2017', id='A1',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'S': generators.RandomVariable('upper'),
        'n': generators.RandomVariable('lower'),
    },
    original_params={
        'S': 'S', 'n': 'n'
    }
)

def putnam_2017a1(
        S: str = 'S', n: str = 'n') -> dict:
    functional_q: str = replace_map(
        (
            "Let ${S}$ be the smallest set of positive integers such that \\begin{enumerate} \\item[(a)] $2$ is in ${S}$, \\item[(b)] ${n}$ is in ${S}$ whenever ${n}^2$ is in ${S}$," 
            " and \\item[(c)] $({n}+5)^2$ is in ${S}$ whenever ${n}$ is in ${S}$. \\end{enumerate} Find the sum of the first $k$ positive integers in sorted order that are not in ${S}$." 
            " (The set ${S}$ is ``smallest'' in the sense that ${S}$ is contained in any other such set.)"
        ),
        {'{S}': S, '{n}': n}
    )

    functional_ans: str = replace_map(
        (
            "If ${S}$ consists of all other natural numbers, then ${S}$ satisfies the given conditions:" 
            " note that the only perfect squares not in ${S}$ are $1$ and numbers of the form $(5k)^2$ for some positive integer $k$, and it readily follows that both (b) and (c) hold."
            " Now suppose that $T$ is another set of positive integers satisfying (a), (b), and (c). Note from (b) and (c) that if ${n} \\in T$ then ${n}+5 \\in T$, and so $T$ satisfies the following property:"  
            " \\begin{itemize} \\item[(d)] if ${n}\\in T$, then ${n}+5k \\in T$ for all $k \\geq 0$. \\end{itemize}  The following must then be in $T$, with implications labeled by conditions (b) through (d):" 
            " \\begin{gather*} 2 \\stackrel{c}{\\Rightarrow} 49 \\stackrel{c}{\\Rightarrow} 54^2 \\stackrel{d}{\\Rightarrow} 56^2 \\stackrel{b}{\\Rightarrow} 56 \\stackrel{d}{\\Rightarrow} 121 \\stackrel{b}{\\Rightarrow}" 
            " 11 \\ 11 \\stackrel{d}{\\Rightarrow} 16 \\stackrel{b}{\\Rightarrow} 4 \\stackrel{d}{\\Rightarrow} 9 \\stackrel{b}{\\Rightarrow} 3 \\ 16 \\stackrel{d}{\\Rightarrow} 36 \\stackrel{b}{\\Rightarrow} 6 \\end{gather*}"  
            " Since $2,3,4,6 \\in T$, by (d) ${S} \\subseteq T$, and so ${S}$ is smallest. We claim that the positive integers not in ${S}$ are $1$ and all multiples of $5$, making the sum $\\boxed{\\frac{5k^2-5k+2}{2}}$."
        ),
        {'{S}': S, '{n}': n}
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

# @variation(
#     year='2017', id='A2',
#     generators={  # generators can either be a dictionary of generators or a custom sampling function
#         'Q': generators.RandomVariable('upper'),
#         'n': generators.RandomVariable('lower'),
#         'x': generators.RandomVariable('lower'),
#     },
#     original_params={
#         'Q': 'Q', 'n': 'n', 'x' : 'x'
#     }
# )

# def putnam_2017a2(
#         Q: str = 'Q', n: str = 'n', x : str = 'x') -> dict:
#     functional_q: str = replace_map(
#         (
#             "Let ${Q}_0({x}) = 1$, ${Q}_1({x}) = {x}$, and \\[ {Q}_{n}({x}) = \\frac{({Q}_{{n}-1}({x}))^2 - 1}{{Q}_{{n}-2}({x})} \\] for all ${n} \\geq 2$." 
#             " Show that, whenever ${n}$ is a positive integer, ${Q}_{n}({x})$ is equal to a polynomial with integer coefficients."
#         ),
#         {'{Q}': Q, '{n}': n, '{x}' : x}
#     )

#     functional_ans: str = replace_map(
#         (
#             "Define $P_{n}({x})$ for $P_0({x}) = 1$, $P_1({x}) = {x}$, and $P_{n}({x}) = {x}  P_{{n}-1}({x})-P_{{n}-2}({x})$. We claim that $P_{n}({x}) = {Q}_{n}({x})$ for all $n \\geq 0$;" 
#             " since $P_{n}({x})$ clearly is a polynomial  with integer coefficients for all ${n}$, this will imply the desired result.   Since $\\{P_{n}\\}$ and $\\{{Q}_{n}\\}$ are"
#             " uniquely determined by their respective recurrence relations and the  initial conditions $P_0,P_1$ or ${Q}_0,{Q}_1$, it suffices to check that  $\\{P_{n}\\}$ satisfies the same recurrence as ${Q}$:" 
#             " that is, $(P_{{n}-1}({x}))^2-P_{n}({x})P_{{n}-2}({x}) = 1$ for all ${n} \\geq 2$. Here is one  proof of this: for ${n} \\geq 1$, define the $2\\times 2$ matrices  \\[ M_{n} ="  
#             " \\begin{pmatrix} P_{{n}-1}({x}) & P_{n} ({x}) \\\\ P_{{n}-2}({x}) &  P_{{n}-1}({x}) \\end{pmatrix}, \\quad T = \\begin{pmatrix} {x} & -1 \\\\ 1 & 0 \\end{pmatrix} \\] with $P_{-1}({x}) = 0$" 
#             " (this value being consistent with the recurrence). Then $\\det(T) = 1$ and $T M_{{n}} = M_{{n}+1}$, so by induction on ${n}$ we have \\[ (P_{{n}-1}({x}))^2-P_{n}({x})P_{{n}-2}({x}) = \\det(M_n) =  \\det(M_1) = 1. \\]"
#         ),
#         {'{Q}': Q, '{n}': n, '{x}' : x}
#     )

#     return {
#         'problem' : functional_q,
#         'solution' : functional_ans,
#         'type' : "variable"
#     }


# def putnam_2017a4(
#     var_N: str = 'N', range: int = 10, avg: float = 7.4
# ) -> dict:
#   '''A class with $2N$ students took a quiz, on which the possible scores were $0,1,\\dots,10$. Each of these scores occurred at least once, and the average score was exactly $7.4$. Show that the class can be divided into two groups of $N$ students in such a way that the average score for each group was exactly $7.4$.'''
#   assert range > 0, f'Error: range = {range} must be a positive integer'
#   assert avg >= 0 and avg <= range, f'Error: average = {avg} must satisfy 0 < {avg} < {range}'

#   functional_q: str = f'A class with $2{var_N}$ students took a quiz, on which the possible scores were $0,1,\\dots,{range}$. Each of these scores occurred at least once, and the average score was exactly ${avg}$. Can the class be divided into two groups of ${var_N}$ students in such a way that the average score for each group was exactly ${avg}$?'
#   functional_ans: str = f'\\boxed{{Yes}}, it can. Let $a_1,\\dots,a_{{2{var_N}}}$ be the scores in nondecreasing order, and define the sums $s_i = \\sum_{{j=i+1}}^{{i+{var_N}}} a_j$ for $i=0,\\dots,{var_N}$. Then $s_0 \\leq \\cdots \\leq s_{{{var_N}}}$ and $s_0 + s_{{{var_N}}} = \\sum_{{j=1}}^{{2{var_N}}} a_j = {avg}(2{var_N})$, so $s_0 \\leq {avg}{var_N} \\leq s_{var_N}$. Let $i$ be the largest index for which $s_i \\leq {avg}{var_N}$; note that we cannot have $i = {var_N}$, as otherwise $s_0 = s_{var_N} = {avg}{var_N}$ and hence  $a_1 = \\cdots = a_{{2{var_N}}} = {avg}$, contradiction. Then ${avg}{var_N} - s_i < s_{{i+1}} - s_i = a_{{i+{var_N}+1}} - a_i$ and so \\[ a_i < s_i + a_{{i+{var_N}+1}} - {avg}{var_N} \\leq a_{{i+{var_N}+1}}; \\] since all possible scores occur, this means that we can find ${var_N}$ scores with sum ${avg}{var_N}$ by taking $a_{{i+1}}, \\dots, a_{{i+{var_N}+1}}$ and omitting one occurrence of the value $s_i + a_{{i+{var_N}+1}} - {avg}{var_N}$.  \\noindent'

#   return {
#         'problem' : functional_q,
#         'solution' : functional_ans,
#         'type' : "constant"
#     }

@variation(
    year='2017', id='B2',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'N': generators.RandomVariable('upper'),
        'k': generators.RandomVariable('lower'),
        'a': generators.RandomVariable('lower')
    },
    original_params={
        'N' : 'N', 'k' : 'k', 'a' : 'a'
    }
)
def putnam_2017b2(
        N: str = 'N', k: str = 'k', a: str = 'a') -> dict:
    functional_q: str = f'Suppose that a positive integer ${N}$ can be expressed as the sum of ${k}$ consecutive positive integers \\[ {N} = {a} + ({a}+1) +({a}+2) + \\cdots + ({a}+{k}-1) \\] for ${k}=2017$ but for no other values of ${k}>1$. Considering all positive integers ${N}$ with this property, what is the smallest positive integer ${a}$ that occurs in any of these expressions?'

    functional_ans: str = f'Note that the expression for ${N}$ can be rewritten as ${k}(2{a}+{k}-1)/2$, so that $2{N} = k(2{a}+{k}-1)$. In this expression, ${k}>1$ by requirement; ${k} < 2{a}+{k}-1$ because ${a}>1$; and obviously ${k}$ and $2{a}+{k}-1$ have opposite parity. Conversely, for any factorization $2{N} = mn$ with $1<m<n$ and $m,n$ of opposite parity, we obtain an expression of ${N}$ in the desired form by taking ${k} = m$, ${a} = (n+1-m)/2$.  We now note that $2017$ is prime. (On the exam, solvers would have had to verify this by hand. Since $2017 < 45^2$, this can be done by trial division by the primes up to 43.) For $2{N} = 2017(2{a}+2016)$ not to have another expression of the specified form, it must be the case that $2{a}+2016$ has no odd divisor greater than 1; that is, $2{a}+2016$ must be a power of 2. This first occurs for $2{a}+2016=2048$, yielding the claimed result. We prove that the smallest value of $a$ is \\boxed{{16}}.'

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }