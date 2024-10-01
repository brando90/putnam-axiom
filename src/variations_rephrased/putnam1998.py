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
    year='1998', id='A1', 
    generators = {
        'h' : generators.RandomInt(1, 500),
        'r' : generators.RandomInt(1,500),
    },
    original_params={
    'h' : 3, 'r' : 1
})
def putnam_1998a1(
        h : int = 3, r : int = 1) -> dict:
    
    d = 2 * r
    h_square = h ** 2
    two_hr = 2 * h * r
    bottom = h ** 2 - 2 * (r ** 2)
    ans = f"({h_square}\\sqrt{{2}} - {two_hr})/{bottom}"

    functional_q : str = replace_map(
        ("A cube is inscribed in a right circular cone has base of radius {r} and height {h} so that the bottom face of the cube is entirely contained in the base of the cone.  What is the side-length of the cube?"),
        {'{h}' : h, '{r}' : r}
    )

    functional_ans : str = replace_map(
        ("Consider the plane containing both the axis of the cone and two opposite vertices of the cube's bottom face.  The cross section of the cone and the cube in this plane consists of a rectangle of sides $s$ and $s\\sqrt{2}$ inscribed in an isosceles triangle of base ${d}$ and height ${h}$, where $s$ is the side-length of the cube.  (The $s\\sqrt{2}$ side of the rectangle lies on the base of the triangle.)  Similar triangles yield $s/{h} = ({r}-s\\sqrt{2}/2)/{r}$, or $s = (\\boxed{{ans}}.$"),
        {'{h}' : h, '{r}' : r, '{d}' : d, '{ans}' : ans}
    )
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }


@variation(
    year='1998', id='B5', 
    generators = {
        'N' : generators.RandomVariable('upper'),
        'i' : generators.RandomInt(100,1000),
    },
    original_params={
    'N' : 'N', 'i' : 1000
})
def putnam_1998b5(
        N : str = 'N', i : int = 1000) -> dict:
    ''' 
    "Let $N$ be the positive integer with 1998 decimal digits, all of them 1; that is, \\[N=1111\\cdots 11.\\] Find the thousandth digit after the decimal point of $\\sqrt N$.",
    '''
    dig = 3
    if i == 1000:
        dig = 1
    functional_q : str = f'Let ${N}$ be the positive integer consisting of 1998 decimal digits, all of which are 1; that is, \[{N}=1111\cdots 11.\] Determine the ${i}$th digit after the decimal point in the decimal expansion of $\sqrt{{{N}}}$.'
    functional_ans : str = f'Write ${N}=(10^{{1998}}-1)/9$.  Then \\begin{{align*}} \\sqrt{{{N}}} &=\\frac{{10^{{999}}}}{{3}}\\sqrt{{1-10^{{-1998}}}} \\\\ &=\\frac{{10^{{999}}}}{{3}} (1-\\frac{{1}}{{2}}10^{{-1998}} + r), \\end{{align*}} where $r<10^{{-2000}}$.  Now the digits after the decimal point of $10^{{999}}/3$ are given by $.3333\\ldots$, while the digits after the decimal point of $\\frac{{1}}{{6}}10^{{-999}}$ are given by $.00000\\ldots 1666666\\ldots$. It follows that the first 1000 digits of $\\sqrt N$ are given by $.33333\\ldots 3331$;  in particular, the {i}th digit is $\\boxed{{{dig}}}$.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }
