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
    year='1990', id='B1', 
    generators = {
        'c' : generators.RandomInt(1, 10000),
        'x' : generators.RandomVariable('lower')
    },
    original_params={
    'c' : 1990, 'x' : 'x'
})
def putnam_1990b1(
        c : int = 1990, x : str = 'x') -> dict:
    
    functional_q: str = f'Find the absolute value of the difference across all real-valued continuously differentiable functions $f$ on the real line such that for all ${x}$, \\[ (f(x))^2 = \\int_0^{x} [(f(t))^2 + (f\'(t))^2]\\,dt + {c}. \\]'
    functional_ans: str = f'There are two such functions, namely $f({x}) = \\sqrt{{{c}}} e^{x}$, and $f({x}) = -\\sqrt{{{c}}} e^{x}$. To see this, suppose that the identity holds. Differentiating each side gives\n\\[ 2f({x})f\'({x}) = (f({x}))^2 + (f\'({x}))^2, \\]\nor equivalently,\n\\[ (f({x}) - f\'({x}))^2 = 0, \\quad f\'({x}) = f({x}), \\]\n\\[ \\log|f({x})| = {x} + C, \\quad |f(x)| = e^C e^{x}. \\]\nBut $f$ is continuous and $f(0) = \\pm \\sqrt{{{c}}}$, and this implies that $f(x) = \\pm \\sqrt{{{c}}} e^{x}$ giving us the absolute value of the difference to be \\boxed{{2\\sqrt{{{c}}} e^{x}}}.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }


