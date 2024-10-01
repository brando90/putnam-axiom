import difflib
import random
import numpy as np
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
    year = '2011', id = 'A1', 
    generators = {
        'x' : generators.RandomVariable('lower'),
        'y' : generators.RandomVariable('lower'),
        'P' : generators.RandomVariable('upper'),
        'n' : generators.RandomInt(3,5000)
    },
    original_params = {
        'x' : 'x', 'y' : 'y', 'P' : 'P', 'n' : 2011
    })
def putnam_2011a1(
    x : str = 'x', y : str = 'y', P : str = 'P', n : int = 2011
) -> dict:
    assert n >= 3, f'We need n = {n} to be >=3 for the question to actually be intereseting.'
    
    functional_q = f'Define a \\textit{{growing spiral}} in the plane to be a sequence of points with integer coordinates ${P}_0 = (0,0), {P}_1, \\dots, {P}_n$ such that $n \\geq 2$ and: \\begin{{itemize}} \\item the directed line segments ${P}_0 {P}_1, {P}_1 {P}_2, \\dots, {P}_{{n-1}} P_n$ are in the successive coordinate directions east (for ${P}_0 {P}_1$), north, west, south, east, etc.; \\item the lengths of these line segments are positive and strictly increasing. \\end{{itemize}} [Picture omitted.]  How many of the points $({x},{y})$ with integer coordinates $0\\leq {x}\\leq {n}, 0\\leq {y}\\leq {n}$ \\emph{{cannot}} be the last point, ${P}_n$ of any growing spiral?'
    
    ans1 = (n - 0) + 1 # (0,y)
    ans2 = (n - 1) + 1 # (x,0) and (x,1)
    ans3 = (n - 2) + 1 # (x,2)
    ans4 = (n - 3) + 1 # (x,3)

    ans = ans1 + ans2 + ans2 + ans3 + ans4
    functional_ans = f'We claim that the set of points with $0\\leq {x}\\leq {n}$ and $0\\leq {y}\\leq {n}$ that cannot be the last point of a growing spiral are as follows: $(0,{y})$ for $0\\leq {y}\\leq {n}$; $({x},0)$ and $({x},1)$ for $1\\leq {x}\\leq {n}$; $({x},2)$ for $2\\leq {x}\\leq {n}$; and $({x},3)$ for $3\\leq {x}\\leq {n}$.  The complement of this set is the set of $({x},{y})$ with $0<{x}<{y}$, along with $(x,y)$ with ${x} \\geq {y} \\geq 4$. Clearly the former set is achievable as ${P}_2$ in a growing spiral, while a point $({x},{y})$ in the latter set is ${P}_6$ in a growing spiral with successive lengths $1$, $2$, $3$, ${x}+1$, ${x}+2$, and ${x}+{y}-1$.  We now need to rule out the other cases. Write ${x}_1<{y}_1<{x}_2<{y}_2<\\ldots$ for the lengths of the line segments in the spiral in order, so that ${P}_1 = ({x}_1,0)$, ${P}_2 = ({x}_1,{y}_1)$, ${P}_3 = ({x}_1-{x}_2,{y}_1)$, and so forth. Any point beyond ${P}_0$ has ${x}$-coordinate of the form ${x}_1-{x}_2+\\cdots+(-1)^{{n-1}} {x}_n$ for $n\\geq 1$; if $n$ is odd, we can write this as ${x}_1 + (-{x}_2+{x}_3) + \\cdots + (-{x}_{{n-1}}+{x}_n) > 0$, while if $n$ is even, we can write this as $({x}_1-{x}_2) + \\cdots + ({x}_{{n-1}}-{x}_n) < 0$. Thus no point beyond ${P}_0$ can have ${x}$-coordinate $0$, and we have ruled out $(0,{y})$ for $0\\leq {y}\\leq {n}$.  Next we claim that any point beyond ${P}_3$ must have ${y}$-coordinate either negative or $\\geq 4$. Indeed, each such point has ${y}$-coordinate of the form ${y}_1-{y}_2+\\cdots+(-1)^{{n-1}} {y}_n$ for $n \\geq 2$, which we can write as $({y}_1-{y}_2) + \\cdots + ({y}_{{n-1}}-{y}_n) < 0$ if $n$ is even, and \\[ {y}_1 +(-{y}_2+{y}_3) + \\cdots + (-{y}_{{n-1}}+{y}_n) \\geq {y}_1 + 2 \\geq 4 \\] if $n \\geq 3$ is odd. Thus to rule out the rest of the forbidden points, it suffices to check that they cannot be ${P}_2$ or ${P}_3$ for any growing spiral. But none of them can be ${P}_3 = ({x}_1-{x}_2,{y}_1)$ since ${x}_1-{x}_2<0$, and none of them can be ${P}_2 = ({x}_1,{y}_1)$ since they all have ${y}$-coordinate at most equal to their ${x}$-coordinate. This gives a total of \\[ {ans1} + {ans2} + {ans2} + {ans3} + {ans4} = \\boxed{{{ans}}} \\] excluded points.'

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }
