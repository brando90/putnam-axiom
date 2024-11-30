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
    year='1966', id='B1', 
    generators = {
        'x' : generators.RandomInt(2,100),
        'P' : generators.RandomVariable('upper')
    },
    original_params={
        'x' : 1,
        'P' : 'P'
})
def putnam_1965b1(
        x : 1,
        P: str = 'P'
    ) -> dict:

    partial = 2 * x
    ans = 4 * x
    functional_q : str = f'Let a convex polygon ${P}$ be contained in a square of side {x}. Find the upper bound of the sum of the squares of the sides of ${P}$.'
    functional_ans : str = f'Let ${P}_1, {P}_2, \\dots, {P}_n$ be the vertices of ${P}$. Let ${P}\'_1, {P}\'_2, \\dots, {P}\'_n$ be the projections of ${P}_1, {P}_2, \\dots, {P}_n$ upon one of the sides of the squares, and let ${P}\'\'_1, {P}\'\'_2, \\dots, {P}\'\'_n$ be the projections of ${P}_1, {P}_2, \\dots, {P}_n$ upon a side that is orthogonal to the previous one. Since ${P}$ is convex, the first side will be covered at most twice by the segments ${P}\'_1{P}\'_2, \\dots, {P}\'_{n-1}{P}\'_n, {P}\'_n{P}\'_1$. We thus deduce the inequality \\[ {P}\'_1{P}\'_2^2 + \\dots + {P}\'_n{P}\'_1^2 \\leq {partial}. \\] Similarly \\[ {P}\'\'_1{P}\'\'_2^2 + \\dots + {P}\'\'_n{P}\'\'_1^2 \\leq {partial}. \\] Adding these two inequalities and using the Pythagorean theorem the assertion follows. Thus the upper bound is \\boxed{ans}.'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }




