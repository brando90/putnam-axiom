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
    year='1992', id='A2', 
    generators = {
        'c' : generators.RandomInt(1, 10000),
        'x' : generators.RandomVariable('lower'),
        'y' : generators.RandomVariable('lower')
    },
    original_params={
    'c' : 996, 'x' : 'x', 'y' : 'y'
})
def putnam_1992a2(
        c : int = 996, x : str = 'x', y : str = 'y') -> dict:
    
    c = c * 2
    functional_q: str = f'Define $C(\\alpha)$ to be the coefficient of $x^{c}$ in the power series about ${x}=0$ of $(1 + {x})^\\alpha$. Evaluate \\[ \\int_0^1 \\left( C(-{y}-1) \\sum_{{k=1}}^{c} \\frac{{1}}{{{y}+k}} \\right)\\,d{y}. \\]'
    functional_ans: str = f'From the binomial series, we see that\n\n\\[ C(-{y} - 1) = \\frac{{(-{y} - 1)(-{y} - 2) \\cdots (-{y} - {c})}}{{{c}!}} = \\frac{{({y} + 1)({y} + 2) \\cdots ({y} + {c})}}{{{c}!}}. \\]\n\nTherefore,\n\n\\[ C(-{y} - 1) \\left( \\frac{{1}}{{{y} + 1}} + \\frac{{1}}{{{y} + 2}} + \\cdots + \\frac{{1}}{{{y} + {c}}} \\right) = \\frac{{d}}{{d{y}}} \\left( \\frac{{({y} + 1)({y} + 2) \\cdots ({y} + {c})}}{{{c}!}} \\right). \\]\n\nHence the integral in question is\n\n\\[ \\int_0^1 \\frac{{d}}{{d{y}}} \\left( \\frac{{({y} + 1)({y} + 2) \\cdots ({y} + {c})}}{{{c}!}} \\right) dy = \\frac{{({y} + 1)({y} + 2) \\cdots ({y} + {c})}}{{{c}!}} \\Big|_0^1 = {c+1} - 1 = \\boxed{{{c}}}. \\]'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }



