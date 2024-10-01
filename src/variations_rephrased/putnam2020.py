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

@variation(year='2020', id='A1', 
    generators = {
        'N' : generators.RandomVariable('upper'),
        'x' : generators.RandomInt(2,10),
        'y' : generators.RandomInt(1,10)
    },
    original_params={
    'N' : 'N', 'x' : 2, 'y' : 1
})
def putnam_2020a1(
        N: str = 'N', x: int = 2, y : int = 1) -> dict:
    ''' 
    How many positive integers $N$ satisfy all of the following three conditions? \\begin{enumerate} \\item[(i)] $N$ is divisible by 2020. \\item[(ii)] $N$ has at most 2020 decimal digits. \\item[(iii)] The decimal digits of $N$ are a string of consecutive ones followed by a string of consecutive zeros. \\end{enumerate}
    '''
    k = (2**x) * (5**y) * 101
    functional_q: str = replace_map(
        (
            "How many positive integers ${N}$ satisfy all of the following three conditions? \\begin{enumerate} \\item[(i)] ${N}$ is divisible by {k}. \\item[(ii)] ${N}$ has at most {k} decimal digits. \\item[(iii)] The decimal digits of ${N}$ are a string of consecutive ones followed by a string of consecutive zeros. \\end{enumerate}"
        ),
        {'{N}': N, '{k}': k}
    )

    m = max(x, y)
    d = math.floor((k - m) / 4)
    d_minus = d - 1
    total = 2 * (d+1) - 1
    r = (k - m) - 4*d
    first_sum = f"{d}+{d}+{d}+{d_minus}+{d_minus}+{d_minus}+{d_minus}+\\cdots+1+1+1+1"
    second_sum = f"4({d}+{d_minus}+\\cdots+1)-{d} = {d}\\cdot {total}"
    answer = d * total
    
    if y == 1:
        functional_ans: str = replace_map(
        (
            "The values of ${N}$ that satisfy (ii) and (iii) are precisely the numbers of the form ${N} = (10^a-10^b)/9$ for $0\\leq b<a\\leq {k}$; this expression represents the integer with $a$ digits beginning with a string of $1$'s and ending with $b$ $0$'s." 
            " A value ${N}$ of this form is divisible by ${k} = 2^{x} \\cdot 5 \\cdot 101$ if and only if $10^b(10^{a-b}-1)$ is divisible by each of $3^2$, $2^{x}\\cdot 5$, and $101$. Divisibility by $3^2$ is a trivial condition since $10 \\equiv 1 \\pmod{9}$." 
            " Since $10^{a-b}-1$ is odd, divisibility by $2^{x}\\cdot 5$ occurs if and only if $b \\geq {m}$. Finally, since $10^2 \\equiv -1 \\pmod{101}$, we see that $10^{a-b}$ is congruent to $10$, $-1$, $-10$, or $1 \\pmod{101}$ depending on whether $a-b$ is congruent to $1$, $2$, $3$, or $0 \\pmod{4}$;" 
            " thus $10^{a-b}-1$ is divisible by $101$ if and only if $a-b$ is divisible by $4$.  It follows that we need to count the number of $(a,b)$ with ${m}\\leq b<a\\leq {k}$ with $4\\,|\\,a-b$. For given $b$, there are $\\lfloor \\frac{{k}-b}{4} \\rfloor$ possible values of $a$. Thus the answer is \\begin{align*} & {first_sum} \\\\ &\\quad = {second_sum} = \\boxed{{answer}}. \\end{align*}"
        ),
        {'{N}': N, '{k}': k, '{m}': m, '{d}': d, '{r}': r, '{x}' : x, '{y}' : y, '{first_sum}' : first_sum, '{second_sum}' : second_sum, '{answer}' : answer}
    )
    else:
        functional_ans: str = replace_map(
            (
                "The values of ${N}$ that satisfy (ii) and (iii) are precisely the numbers of the form ${N} = (10^a-10^b)/9$ for $0\\leq b<a\\leq {k}$; this expression represents the integer with $a$ digits beginning with a string of $1$'s and ending with $b$ $0$'s." 
                " A value ${N}$ of this form is divisible by ${k} = 2^{x} \\cdot 5^{y} \\cdot 101$ if and only if $10^b(10^{a-b}-1)$ is divisible by each of $3^2$, $2^{x}\\cdot 5^{y}$, and $101$. Divisibility by $3^2$ is a trivial condition since $10 \\equiv 1 \\pmod{9}$." 
                " Since $10^{a-b}-1$ is odd, divisibility by $2^{x}\\cdot 5^{y}$ occurs if and only if $b \\geq {m}$. Finally, since $10^2 \\equiv -1 \\pmod{101}$, we see that $10^{a-b}$ is congruent to $10$, $-1$, $-10$, or $1 \\pmod{101}$ depending on whether $a-b$ is congruent to $1$, $2$, $3$, or $0 \\pmod{4}$;" 
                " thus $10^{a-b}-1$ is divisible by $101$ if and only if $a-b$ is divisible by $4$.  It follows that we need to count the number of $(a,b)$ with ${m}\\leq b<a\\leq {k}$ with $4\\,|\\,a-b$. For given $b$, there are $\\lfloor \\frac{{k}-b}{4} \\rfloor$ possible values of $a$. Thus the answer is \\begin{align*} & {first_sum} \\\\ &\\quad = {second_sum} = \\boxed{{answer}}. \\end{align*}"
            ),
            {'{N}': N, '{k}': k, '{m}': m, '{d}': d, '{r}': r, '{x}' : x, '{y}' : y, '{first_sum}' : first_sum, '{second_sum}' : second_sum, '{answer}' : answer}
        )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(year='2020', id='A2', 
    generators = {
        'k' : generators.RandomVariable('lower'),
        'j' : generators.RandomVariable('lower')
    },
    original_params={
    'k' : 'k', 'j' : 'j'
})
def putnam_2020a2(
    k: str = 'k', j: str = 'j') -> dict:
    functional_q : str = replace_map (
        ("Let ${k}$ be a nonnegative integer. Evaluate \\[ \\sum_{{j}=0}^{k} 2^{{k}-{j}} \\binom{{k}+{j}}{{j}}. \\]"),
        {'{k}' : k, '{j}' : j}
    )
    functional_ans : str = replace_map (
        ("Let $S_{k}$ denote the given sum. Then, with the convention that ${n\\choose{-1}} = 0$ for any $n\\geq 0$, we have for ${k}\\geq 1$," 
        " \\begin{align*} S_{k} &= \\sum_{{j}=0}^{k} 2^{{k}-{j}} \\left[ {{{k}-1+{j}}\\choose {{j}}} + {{{k}-1+{j}}\\choose {{j}-1}} \\right] \\\\ &= 2\\sum_{{j}=0}^{{k}-1} 2^{{k}-1-{j}} {{{k}-1+{j}}\\choose {j}}+{{2{k}-1}\\choose {k}} + \\sum_{{j}=1}^{k} 2^{{k}-{j}}{{{k}-1+{j}}\\choose{{j}-1}} \\\\ &= 2S_{{k}-1} + {{2{k}-1}\\choose{{k}}} + \\sum_{{j}=0}^{{k}-1} 2^{{k}-{j}-1}{{{k}+{j}}\\choose {j}} \\\\ &= 2S_{{k}-1}+S_{k}/2 \\end{align*}" 
        " and so $S_{k} = 4S_{{k}-1}$. Since $S_0 = 1$, it follows that $S_{k} = 4^{k}$ for all ${k}$. The answer is $\\boxed{4^{k}}$."),
        {'{k}' : k, '{j}' : j}   
    )
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }
