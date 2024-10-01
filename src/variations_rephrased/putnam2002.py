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
    year='2002', id='B1',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'm' : generators.RandomInt(1,5000),
        'n' : generators.RandomInt(1,5000)
    },
    original_params={
        'm' : 50, 'n' : 50
    }
)
def putnam_2002b1(
        m : int = 50, n : int = 50) -> dict:
    tot = m + n
    functional_q: str = f'Shanille O\'Keal is shooting free throws on a basketball court. We know that she hits the first and misses the second. For the following throws, the probability that she hits the next shot is the proportion of shots she has hit so far. What is the probability she hits exactly {m} of her first {tot} shots?'

    functional_ans: str = f'In fact, we show by induction on $n$ that after $n$ shots, the probability of having made any number of shots from $1$ to $n-1$ is equal to $1/(n-1)$. This is evident for $n=2$. Given the result for $n$, we see that the probability of making $i$ shots after $n+1$ attempts is \\begin{{align*}} \\frac{{i-1}}{{n}} \\frac{{1}}{{n-1}} + \\left( 1 - \\frac{{i}}{{n}} \\right) \\frac{{1}}{{n-1}} &= \\frac{{(i-1) + (n-i)}}{{n(n-1)}} \\\\ &= \\frac{{1}}{{n}}, \\end{{align*}} as claimed. The probability is $\\boxed{{1/{tot-1}}}$.'

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : 'constant'
    }