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
