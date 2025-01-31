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
    year='1952', id='1', 
    generators = {
        'x' : generators.RandomVariable('lower'),
        'a' : generators.RandomVariable('lower'),
        'f' : generators.RandomVariable('lower'),
    },
    original_params={
        'x' : 'x',
        'a' : 'a',
        'f' : 'f'
})
def putnam_19501(
        x : str = 'x',
        a : str = 'a',
        f : str = 'f'
    ) -> dict:

    functional_q : str = f'Let \\[ {f}({x}) = \\sum_{{i=0}}^n {a}_i {x}^{{n-i}} \\] be a polynomial of degree $n$ with integral coefficients. If ${a}_0$, ${a}_n$, and ${f}(1)$ are odd, find the number of rational roots of ${f}({x}) = 0'
    functional_ans : str = replace_map(
        'Suppose ${f}(p/q) = 0$ where $p$ and $q$ are integers having no common factor. Then \\[ q^n {f}\\left(\\frac{p}{q}\\right) = {a}_0 p^n + q {a}_1 p^{n-1} + \\cdots + q^{n-1} {a}_{n-1} p + q^n {a}_n = 0. \\] It follows that $q$ divides ${a}_0$ and $p$ divides ${a}_n$. Therefore $p$ and $q$ are both odd. Hence \\[ {a}_0 p^n + q {a}_1 p^{n-1} + \\cdots + q^{n-1} {a}_{n-1} p + q^n {a}_n \\equiv {a}_0 + {a}_1 + \\cdots + {a}_{n-1} + {a}_n \\equiv {f}(1) \\equiv 1 \\pmod{2}, \\] contradicting $(1)$. This makes the answer \\boxed{0}.',
        map = {'{a}' : a, '{f}' : f, '{x}' : x}
    )
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

