import difflib
import random
import numpy as np
import math
from .utils import single_char_variable, replace_map, variation
import os
import json
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
    year='1994', id='A2',
    generators={
        'a': generators.RandomInt(1, 100),
        'b': generators.RandomInt(1, 100),
        'A': generators.RandomVariable("upper")
    },
    original_params={
        'a': 2, 'b': 3, 'A' : 'A'
    }
)
def putnam_1994a2(
        a : int = 2,
        b : int = 3,
        A : str = 'A'
) -> dict:
    
    b_sq = b ** 2

    functional_q: str = replace_map(
        (
            "Let ${A}$ be the area of the region in the first quadrant bounded by the line $y = \\frac{1}{{a}} x$, "
            "the $x$-axis, and the ellipse $\\frac{1}{{b_sq}} x^2 + y^2 = 1$. Find the positive number $m$ such that ${A}$ is equal "
            "to the area of the region in the first quadrant bounded by the line $y = mx$, the $y$-axis, and the ellipse $\\frac{1}{{b_sq}} x^2 + y^2 = 1$."
        ),
        {'{a}': a, '{b}' : b, '{b_sq}' : b_sq, '{A}' : A}
    )

    functional_ans: str = replace_map(
        (
            "The linear transformation given by $x_1 = \\frac{1}{{b}}x$, $y_1 = y$ transforms the region $R$ bounded by $y = \\frac{1}{{a}}x$, the $x$-axis, "
            "and the ellipse $\\frac{1}{{b_sq}}x^2 + y^2 = 1$ into the region $R'$ bounded by $y_1 = \\frac{{b}}{{a}}x_1$, the $x_1$-axis, and the circle $x_1^2 + y_1^2 = 1$; "
            "it also transforms the region $S$ bounded by $y = mx$, the $y$-axis, and $\\frac{1}{{b_sq}}x^2 + y^2 = 1$ into the region $S'$ bounded by $y_1 = {b}mx_1$, the $y_1$-axis, and the circle. "
            "Since all areas are multiplied by the same (nonzero) factor under the transformation, $R$ and $S$ have the same area if and only if $R'$ and $S'$ have the same area. "
            "However, we can see by symmetry about the line $y_1 = x_1$ that this happens if and only if ${b}m = \\frac{{a}}{{b}}$, that is, $m = \\boxed{\\frac{{a}}{{b_sq}}}$."
        ),
        {'{a}': a, '{b}' : b, '{b_sq}' : b_sq, '{A}' : A}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "constant"
    }