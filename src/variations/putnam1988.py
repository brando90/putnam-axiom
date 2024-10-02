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
    year='1988', id='B3', 
    generators = {
        'num' : generators.RandomInt(2,100),
        'c' : generators.RandomVariable('lower'),
        'd' : generators.RandomVariable('lower'),
        'r' : generators.RandomVariable('lower'),
        'g' : generators.RandomVariable('lower')
    },
    original_params={
        'num' : 2,
        'c' : 'c',
        'd' : 'd',
        'r' : 'r',
        'g' : 'g'
})
def putnam_1988b3(
        num = 2, c = 'c', d = 'd', r = 'r', g = 'g') -> dict:
    
    num = num ** 2 - 1 # To ensure that num is NOT a perfect square.
    functional_q : str = f'For every natural number $n$ (a natural number is of the set $\\mathrm{{N}} = \\{{1,2,\\dots \\}}$ of positive integers), let $r_n$ be the minimum value of $|{c}-{d}\\sqrt{{{num}}}|$ for all nonnegative integers ${c}$ and ${d}$ such that ${c}+{d}=n$. Find the smallest positive real number ${g}$ with ${r}_n \\leq {g}$ for all $n \\in \\mathrm{{N}}$, with proof.'
    functional_ans : str = f'Let ${g} = (1 + \\sqrt{{{num}}})/2$. Since for each fixed value of $n$ the sequence \\[n, n - 1 - \\sqrt{{{num}}}, n - 2 - 2\\sqrt{{{num}}}, \\dots, -n\\sqrt{{{num}}}\\] is an arithmetic progression with $-2{g}$ as common difference, there is a unique term $x_n$ in it with $-{g} < x_n < {g}$. Clearly ${r}_n = |x_n|$. Let $\\varepsilon > 0$. By the pigeonhole principle, there exist $a$ and $b$ with $a \\neq b$ and $|x_a - x_b| < \\varepsilon$. Let $t = |a - b|$. In the sequence ${r}_t, {r}_{{2t}}, {r}_{{3t}}, \\dots$, there is an ${r}_{{kt}}$ such that ${g} - \\varepsilon < {r}_{{kt}} \\leq {g}$. Hence ${g} = \\boxed{{(1 + \\sqrt{{{num}}})/2}}$ is the desired least upper bound of the ${r}_n$.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }
