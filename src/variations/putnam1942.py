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
    year='1942', id='2', 
    generators = {
        'a' : generators.RandomVariable('lower')
    },
    original_params={
        'a' : 'a',
        'b' : 'b'
})
def putnam_1942a2(
        a : str = 'a',
        b : str = 'b'
    ) -> dict:

    functional_q : str = f'If a polynomial $f(x)$ is divided by $(x - {a})^2(x - {b})$, where ${a} \\neq {b}$, derive a formula for the remainder.'
    functional_ans : str = f"Since $f(x)$ is divided by a cubic polynomial, the remainder $R(x)$ will be of degree at most two in $x$, say \\[ R(x) = Ax^2 + Bx + C. \\]\n\nThen\\[ f(x) = (x - {a})^2(x - {b})Q(x) + Ax^2 + Bx + C \\] and \\[ f'(x) = 2(x - {a})(x - {b})Q(x) + (x - {a})^2Q(x) + (x - {a})^2(x - {b})Q'(x) + 2Ax + B. \\]\n\nFrom these relations one gets \\[ f({a}) = A{a}^2 + B{a} + C \\] \\[ f({b}) = A{b}^2 + B{b} + C \\] \\[ f'({a}) = 2A{a} + B. \\]\n\nSolving for $A$, $B$, $C$ one gets \\[ A = \\frac{{1}}{{({b} - {a})^2}} \\big[f({b}) - f({a}) - ({b} - {a})f'({a})\\big], \\] \\[ B = \\frac{{-1}}{{({b} - {a})^2}} \\big[2{a}\\big(f({b}) - f({a})\\big) - ({b}^2 - {a}^2)f'({a})\\big], \\] \\[ C = \\frac{{1}}{{({b} - {a})^2}} \\big[({b} - {a})^2f({a}) + {a}^2\\big(f({b}) - f({a})\\big) + {a}{b}({a} - {b})f'({a})\\big]. \\]\n\nHence \\[ R(x) = \\frac{{1}}{{({b} - {a})^2}} \\Big\\{{\\big[f({b}) - f({a}) - ({b} - {a})f'({a})\\big]x^2 \\] \\[ - \\big[2{a}(f({b}) - f({a})) + ({b}^2 - {a}^2)f'({a})\\big]x \\] \\[ + \\big[({b} - {a})^2f({a}) + {a}^2(f({b}) - f({a})) + {a}{b}({a} - {b})f'({a})\\big]\\Big\\}}. \\]\n\nThis is easier to check if written in the form \\[ R(x) = \\boxed{{f({a}) + \\frac{{f({b}) - f({a})}}{{({b} - {a})^2}}(x - {a})^2 - \\frac{{f'({a})}}{{{b} - {a}}}(x - {a})(x - {b})}}. \\]"
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

