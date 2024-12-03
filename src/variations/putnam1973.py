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
    year='1973', id='A1', 
    generators = {
        'A' : generators.RandomVariable('upper'),
        'B' : generators.RandomVariable('upper'),
        'C' : generators.RandomVariable('upper'),
        'X' : generators.RandomVariable('upper'),
        'Y' : generators.RandomVariable('upper'),
        'Z' : generators.RandomVariable('upper')
    },
    original_params={
        'A' : 'A',
        'B' : 'B',
        'C' : 'C',
        'X' : 'X',
        'Y' : 'Y',
        'Z' : 'Z'
})
def putnam_1973a1(
        A : str = 'A',
        B : str = 'B',
        C : str = 'C',
        X : str = 'X',
        Y : str = 'Y',
        Z : str = 'Z'
    ) -> dict:

    functional_q : str = f'Let ${A}{B}{C}$ be any triangle. Let ${X}, {Y}, {Z}$ be points on the sides ${B}{C}, {C}{A}, {A}{B}$ respectively. Suppose the distances ${B}{X} \\leq {X}{C}, {C}{Y} \\leq {Y}{A}, {A}{Z} \\leq {Z}{B}$. Given that the area of the triangle ${X}{Y}{Z}$ is $\\geq n$ (area of triangle ${A}{B}{C}$) find the lowest non-zero value of $n$.'
    functional_ans : str = f'(a) If ${X}, {Y}, {Z}$ are at the midpoints of the sides, the area of $\\triangle {X}{Y}{Z}$ is one fourth of the area of $\\triangle {A}{B}{C}$. Also, as long as ${B}{X} \\leq {X}{C}, {C}{Y} \\leq {Y}{A}$ and ${A}{Z} \\leq {Z}{B}$, moving one of ${X}, {Y}, {Z}$ to the midpoint of its side, while leaving the other two fixed, does not increase the area of $\\triangle {X}{Y}{Z}$ since the altitude to the fixed base of $\\triangle {X}{Y}{Z}$ decreases or remains constant. This gives us \\boxed{{\\frac{1}{4}}}.'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


