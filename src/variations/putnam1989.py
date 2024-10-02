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
    year='1989', id='A1', 
    generators = {
        'base': generators.RandomInt(2,100)
    },
    original_params={
        'base' : 10
})
def putnam_1989a1(
        base = 10) -> dict:
    if base == 10:
        asUsual = 'as usual '
        disclaimer = ''
    else:
        asUsual = ''
        disclaimer = f'Assume all numbers written are in base {base}. We omit the base for convenience of notation. '
    
    functional_q : str = f'Consider all positive integers written {asUsual}in base {base}, are alternating 1\'s and 0\'s, beginning and ending with 1. How many of these numbers are prime?'
    functional_ans : str = f'{disclaimer}Let $N_k$ be the number \\[ 101010 \\ldots 101 \\] with exactly $k$ digits equal to 0. If $k = 1$, so that $N_k = 101$, then $N_k$ is prime. All other $N_k$\'s are composite, as the following reasoning shows. If $k$ is odd, then $101$ divides $N_k$. If $k$ is even, then \\[ 11N_k = R \\cdot S, \\] where $R$ is the number consisting of $k + 1$ digits all equal to $1$ and $S$ is the number with $k + 2$ digits beginning and ending with $1$ and having only $0$\'s in between. One of the numbers $R$ and $S$ divides $N_k$. Thus the answer is \\boxed{{1}}.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }
