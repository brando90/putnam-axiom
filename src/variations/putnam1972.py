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
    year='1972', id='B2', 
    generators = {
        'v' : generators.RandomVariable('lower'),
        's' : generators.RandomVariable('lower')
    },
    original_params={
        'v' : 'v',
        's' : 's'
})
def putnam_1972b2(
        v : str = 'v',
        s : str = 's'
    ) -> dict:

    functional_q : str = f'A particle moving on a straight line starts from rest and attains a velocity ${v}_0$ after traversing a distance ${s}_0$. If the motion is such that the acceleration was never increasing, find the maximum time for the traverse.'
    functional_ans : str = f'We take ${v}_0$ as positive (see Comment) and consider the graph of ${v}$ as a function of $t$ (see Figure 1). From the given data we know that the curve starts at the origin and is concave downward since the acceleration $a = d{v}/dt$ does not increase.\n\n\\[ \\text{{(See Figure for graphical representation)}} \\]\n\nLet $t_0$ be the time of the traverse. Then ${v}(t_0) = {v}_0$. The distance ${s}_0$ is represented by the area bounded by the curve ${v} = {v}(t)$, the $t$-axis, and the line $t = t_0$. The area of the right triangle with vertices at $(0,0)$, $(t_0, 0)$ and $(t_0, {v}_0)$ has area less than or equal to ${s}$. Thus \\[ \\frac{{1}}{{2}} {v}_0 t_0 \\leq {s}_0 \\] or \\[ t_0 \\leq \\boxed{{\\frac{{2{s}_0}}{{{v}_0}}}}. \\]\n\nEquality is possible and gives the maximum value of $t_0$ (for given ${s}_0$ and ${v}_0$) when the graph of ${v}(t)$ is the straight line ${v}(t) = ({v}_0/t_0)t = ({v}_0^2 / 2{s}_0)t$.'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1972', id='B3', 
    generators = {
        'A' : generators.RandomVariable('upper'),
        'B' : generators.RandomVariable('upper')
    },
    original_params={
        'A' : 'A',
        'B' : 'B'
})
def putnam_1972b3(
        A : str = 'A',
        B : str = 'B'
    ) -> dict:

    functional_q : str = f'Let ${A}$ and ${B}$ be two elements in a group such that ${A}{B}{A} = {B}{A}^2{B}$, ${A}^3 = 1$ and ${B}^{{2n-1}} = 1$ for some positive integer $n$. Find the value of ${B}$.'
    functional_ans : str = f'From ${A}{B}{A} = {B}{A}^2{B} = {B}{A}^{-1}{B}$, we have \\[ {A}{B}^2 = {A}{B}{A} \\cdot {A}^{-1}{B} = {B}{A}^{-1}{B}{A}^{-1}{B} = {B}{A}^{-1} \\cdot {A}{B}{A} = {B}^2{A}. \\] By induction, \\[ {A}{B}^{{2r}} = {B}^{{2r}}{A} \\] so that \\[ {A}{B} = {A}{B}^{{2n}} = {B}^{{2n}}{A} = {B}{A}. \\] Since ${A}$ and ${B}$ commute, ${A}{B}{A} = {B}{A}^2{B}$ implies \\[ {A}^2{B} = {A}^2{B}^2, \\] or \\[ {B} = {B}^2, \\] or \\[ {B} = \\boxed{{1}}. \\]'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }



