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
    year='1967', id='A3', 
    generators = {
        'a' : generators.RandomVariable('lower'),
        'b' : generators.RandomVariable('lower'),
        'c' : generators.RandomVariable('lower')
    },
    original_params={
        'a' : 'a',
        'b' : 'b',
        'c' : 'c'
})
def putnam_1967a2(
        a : str = 'a',
        b : str = 'b',
        c : str = 'c'
    ) -> dict:

    functional_q : str = f'Consider polynomial forms ${a}x^2 - {b}x + {c}$ with integer coefficients which have two distinct zeros in the open interval $0 < x < 1$. Exhibit with a proof the least positive integer value of ${a}$ for which such a polynomial exists.'
    functional_ans : str = f'Let $f(x) = {a}x^2 - {b}x + {c} = {a}(x - r)(x - s)$. Then $f(0) \\cdot f(1) = {a}^2 r(r - 1)s(s - 1)$. The graph of $r(r - 1)$ shows that $0 < r < 1$ implies $0 < r(r - 1) \\leq \\frac{{1}}{{4}}$, with equality if and only if $r = \\frac{{1}}{{2}}$. Similarly, $0 < s(s - 1) \\leq \\frac{{1}}{{4}}$. Since $r \\neq s$, $r(r - 1)s(s - 1) < \\frac{{1}}{{16}}$ and $0 < f(0) \\cdot f(1) < {a}^2 / 16$. The coefficients ${a}, {b}, {c}$ are integers and thus $1 \\leq f(0) \\cdot f(1)$. Consequently ${a}^2 > 16$, i.e., ${a} \\geq 5$.\\n\\nThe discriminant ${b}^2 - 4{a}{c}$ shows that the minimum possible value for ${b}$ is $5$. Furthermore, $5x^2 - 5x + 1$ has two distinct roots between 0 and 1. Thus the minimum value of {a} is \\boxed{{5}}.'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1967', id='B5', 
    generators = {
        'n' : generators.RandomVariable('lower')
    },
    original_params={
        'n' : 'n'
})
def putnam_1967b5(
        n : str = 'n'
    ) -> dict:

    functional_q : str = f'Find the sum of the first ${n}$ terms in the binomial expansion of $(2 - 1)^{{-{n}}}$ where ${n}$ is a positive integer.'
    functional_ans : str = f'Let $A_{n}$ be the sum of the first ${n}$ terms in the binomial expansion of $(2 - 1)^{{-{n}}}$.\\n\\[ A_{n} = \\sum_{{i=0}}^{{{n}-1}} \\binom{{{n}+i-1}}{{i}} 2^{{-{n}-i}}. \\]\\n\\nRewriting, we use recursive summation to evaluate:\\n\\[ A_{n} = 2^{{-{n}}} + \\sum_{{i=1}}^{{{n}-1}} \\left( \\binom{{{n}+i-2}}{{i}} + \\binom{{{n}+i-2}}{{i-1}} \\right) 2^{{-{n}-i}}. \\]\\n\\nAfter manipulation and combining terms:\\n\\[ A_{n} = \\frac{{1}}{{2}} A_{{{n}-1}} + \\frac{{1}}{{2}} A_{{{n}-1}} + 2^{{-2{n}}}, \\]\\nwhich simplifies to:\\n\\[ A_{n} = \\frac{{1}}{{2}} A_{n} + \\frac{{1}}{{2}}, \\]\\nso \\( A_{n} = \\boxed{{\\frac{{1}}{{2}}}} \\).'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }




