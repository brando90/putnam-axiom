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
    year='1975', id='A4',
    generators = {
        'n' : generators.RandomVariable('lower'),
        'm' : generators.RandomVariable('lower')
    },
    original_params={
        'n' : 'n',
        'm' : 'm'
})
def putnam_1975a4(
        n : str = 'n',
        m : str = 'm'
    ) -> dict:
    
    functional_q : str = f'Let ${n} = 2{m}$, where ${m}$ is an odd integer greater than 1. Let $\\theta = e^{{2\\pi i / {n}}}$. Express $(1-\\theta)^{{-1}}$ explicitly as a polynomial in $\\theta$, \n\n$a_k \\theta^k + a_{{k-1}} \\theta^{{k-1}} + \\cdots + a_1 \\theta + a_0$, \n\nwith integer coefficients $a_i$. \n\n[Note that $\\theta$ is a primitive ${n}$-th root of unity, and thus it satisfies all of the identities which hold for such roots.]'
    functional_ans : str = f'Let ${n} = 4k + 2$ with $k > 0$. Then\n\n$$0 = \\theta^{n} - 1 = \\theta^{{4k+2}} - 1 = (\\theta^{{2k+1}} - 1)(\\theta + 1)(\\theta^{{2k}} - \\theta^{{2k-1}} + \\theta^{{2k-2}} - \\cdots - \\theta + 1).$$\n\nSince $\\theta$ is a primitive ${n}$-th root of unity with ${n} > 2k + 1$ and ${n} > 2$,\n\n$$(\\theta^{{2k+1}} - 1)(\\theta + 1) \\neq 0.$$ \n\nHence\n\n(A)\n$$\\theta^{{2k}} - \\theta^{{2k-1}} + \\theta^{{2k-2}} - \\cdots + \\theta^2 - \\theta + 1 = 0,$$\n\n$$1 = \\theta - \\theta^2 + \\theta^3 - \\cdots - \\theta^{{2k}} = (1 - \\theta)(\\theta + \\theta^2 + \\theta^3 + \\cdots + \\theta^{{2k-1}}),$$\n\n$$(1 - \\theta)^{{-1}} = \\theta + \\theta^3 + \\cdots + \\theta^{{2k-1}} \\quad \\text{{[where $2k - 1 = (n - 4)/2$]}}.$$ \n\nAnother solution is $(1 - \\theta)^{{-1}} = \\boxed{{1 + \\theta^2 + \\theta^4 + \\cdots + \\theta^{{2k}}}}$ as one sees from (A).'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1975', id='B5',
    generators = {
        'p' : generators.RandomInt(1,1000)
    },
    original_params={
        'p' : 1
})
def putnam_1975b5(
        p : int = 1
    ) -> dict:
    e = f'{p}^k' if p != 1 else ''
    e1 = f'{p}^k' if p != 1 else '1'
    eexp = f'{{{p}e}}' if p != 1 else 'e'
    functional_q : str = f'Let $f_0(x) = e^x$ and $f_n(x) = xf\'_n(x)$ for $n = 0, 1, 2, \\dots$ Find \\sum_{{n=0}}^\\infty \\frac{{f_n({p})}}{{n!}} in terms of e.'
    functional_ans : str = f'Since $f_0(x) = \\sum_{{k=0}}^\\infty \\frac{{x^k}}{{k!}}$, one easily shows by mathematical induction that \\[ f_n(x) = \\sum_{{k=0}}^\\infty \\frac{{k^n x^k}}{{k!}}. \\] Then, since all terms are positive, one has \\[ \\sum_{{n=0}}^\\infty \\frac{{f_n({p})}}{{n!}} = \\sum_{{n=0}}^\\infty \\sum_{{k=0}}^\\infty \\frac{{k^n{e}}}{{k! n!}} = \\sum_{{k=0}}^\\infty \\frac{{{e1}}}{{k!}} \\sum_{{n=0}}^\\infty \\frac{{k^n}}{{n!}} = \\sum_{{k=0}}^\\infty \\frac{{e^k{e}}}{{k!}} = \\boxed{{e^{eexp}}}. \\]'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }
