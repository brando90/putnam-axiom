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
    year='1986', id='A1', 
    generators = {
        'a' : generators.RandomInt(2,50),
        'b' : generators.RandomInt(1,50)
    },
    original_params={
        'a' : 2,
        'b' : 1
})
def putnam_1986a1(
        a = 2, b = 1) -> dict:
    b = a + b # makes b > a
    ans = max((-a)**3 - 3 * (-a), b ** 3 - 3 * b)

    functional_q : str = f'For all real numbers $x$ satisfying $x^4+{a**2 * b**2}\\leq {a**2 + b**2}x^2$, what is the maximum value of $f(x)=x^3-3x$?'
    functional_ans : str = f'The condition that $x^4 + {a**2 * b**2} \\leq {a**2 + b**2}x^2$ is equivalent to \\[ (x - {b})(x - {a})(x + {a})(x + {b}) \\leq 0. \\] The latter is satisfied if and only if $x$ is in the closed interval $[-{b}, -{a}]$ or the closed interval $[{a}, {b}]$. The function $f$ is increasing on these intervals because for such $x$, $f\'(x) = 3(x^2 - 1) > 0$. It follows that the maximum value of $f$ over this domain is $\\max \\{{f(-{a}), f({b})\\}} = \\boxed{{{ans}}}.$'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }
