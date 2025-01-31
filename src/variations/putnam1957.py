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
    year='1957', id='5', 
    generators = {
        'S' : generators.RandomVariable('upper'),
        'n' : generators.RandomVariable('lower'),
        'd' : generators.RandomInt(1,100)
    },
    original_params={
        'S' : 'S',
        'n' : 'n',
        'd' : 1
})
def putnam_19575(
        S : str = 'S',
        n : str = 'n',
        d : int = 1
    ) -> dict:

    functional_q : str = f'Let ${S}$ be a set of ${n}$ points in the plane such that the greatest distance between two points of ${S}$ is ${d}$. Find the maximum number of times this distance can occur between pairs of points of ${S}$.'
    functional_ans : str = f'Induction on ${n}$. Obviously true for ${n} \\leq 3$. Suppose it is true for ${n}$. Take ${n}+1$ points. If no point is a distance {d} from more than 2 points, then we are done. So assume that $A, B,$ and $C$ are all a distance {d} from $P$. Without loss of generality, the largest of the three angles $\\angle APB, \\angle APC, \\angle BPC$ is $\\angle APB$. It must be at most $60^\\circ$, since $AB \\leq {d}$. So the ray $PC$ lies between the rays $PA$ and $PB$.\n\nNow suppose there is another point $D$ (apart from $P$) such that $CD = {d}$. Then $CD$ must intersect $PA$, because otherwise one of $CP, CA, DP,$ and $DA$ would exceed {d}. Similarly, it must intersect $PB$. But that is impossible. So there is no such point $D$. Hence, if we remove $C$, we lose only one realization of the distance {d}. But the remaining ${n}$ points have at most ${n}$ realizations, so the result is established. There can be at most $\\boxed{n}$ realizations of the distance {d}.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(
    year='1957', id='8', 
    generators = {
        'a' : generators.RandomVariable('lower'),
        'n' : generators.RandomPrime(97,419)
    },
    original_params={
        'a' : 'a',
        'n' : 101
})
def putnam_19578(
        a : str = 'a',
        n : int = 101
    ) -> dict:
    n = n[0] - 1
    functional_q : str = f'Consider the determinant $|{a}_{{ij}}|$ of order {n} with ${a}_{{ij}} = i \\times j$. Given that the absolute value of each of the {n}! terms in the expansion of this determinant is divided by {n+1}, find the maximum remainder across all cases.'
    functional_ans : str = f'Solution. Each term in the expansion of the given determinant is, except for sign, the product of all possible row indices and all possible column indices, that is, $({n}!)^2$, and this is the absolute value of every term.\n\nNow {n+1} is a prime, so by Wilson\'s theorem ${n}! \\equiv -1 \\pmod{{{n+1}}}$. Hence $({n}!)^2 \\equiv (-1)^2 \\equiv 1 \\pmod{{{n+1}}}$, as required. Thus the remainder will be \\boxed{{{1}}}.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }
