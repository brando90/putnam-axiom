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
    year='1968', id='A4', 
    generators = {
        'n' : generators.RandomVariable('lower'),
        'x' : generators.RandomVariable('lower'),
        'y' : generators.RandomVariable('lower'),
        'z' : generators.RandomVariable('lower')
    },
    original_params={
        'n' : 'n',
        'x' : 'x',
        'y' : 'y',
        'z' : 'z'
})
def putnam_1968a4(
        n : str = 'n',
        x : str = 'x',
        y : str = 'y',
        z : str = 'z'
    ) -> dict:

    functional_q : str = f'Given ${n}$ points on the sphere \\( \\{{({x}, {y}, {z}): {x}^2 + {y}^2 + {z}^2 = 1\\}} \\), find the upper bound of the sum of the squares of the distances between them in terms of ${n}$.'
    functional_ans : str = f'The \\({n}\\) points can be represented by vectors \\(\\mathbf{{v}}_i\\); \\(i = 1, \\dots, {n}\\) with \\(\\|\\mathbf{{v}}_i\\| = 1\\). Expanding \"the sum of the squares of the distances between them\" in the case \\({n} = 3\\) suggests the following general identities:\n\n\\[\n\\sum_{{1 \\leq i < j \\leq {n}}} \\|\\mathbf{{v}}_i - \\mathbf{{v}}_j\\|^2 = \\sum_{{1 \\leq i < j \\leq {n}}} (\\mathbf{{v}}_i - \\mathbf{{v}}_j) \\cdot (\\mathbf{{v}}_i - \\mathbf{{v}}_j)\n\\]\n\\[\n= ({n}-1) \\sum_{{1 \\leq i \\leq {n}}} \\mathbf{{v}}_i \\cdot \\mathbf{{v}}_i - 2 \\sum_{{1 \\leq i < j \\leq {n}}} \\mathbf{{v}}_i \\cdot \\mathbf{{v}}_j\n\\]\n\\[\n= {n} \\sum_{{1 \\leq i \\leq {n}}} \\mathbf{{v}}_i \\cdot \\mathbf{{v}}_i - \\left[ \\sum_{{1 \\leq i \\leq {n}}} \\mathbf{{v}}_i \\cdot \\mathbf{{v}}_i + 2 \\sum_{{1 \\leq i < j \\leq {n}}} \\mathbf{{v}}_i \\cdot \\mathbf{{v}}_j \\right]\n\\]\n\\[\n= {n}^2 - \\left( \\sum_{{1 \\leq i \\leq {n}}} \\mathbf{{v}}_i \\right) \\cdot \\left( \\sum_{{1 \\leq i \\leq {n}}} \\mathbf{{v}}_i \\right).\n\\]\nThus the result follows and, in addition, equality exists if and only if \\(\\sum_{{1 \\leq i \\leq {n}}} \\mathbf{{v}}_i = 0\\). Thus the uper bound is \\boxed{{{n}^2}}.'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1968', id='B1', 
    generators = {
        'x' : generators.RandomVariable('lower'),
        'y' : generators.RandomVariable('lower'),
        'k' : generators.RandomInt(2,200),
    },
    original_params={
        'x' : 'x',
        'y' : 'y',
        'k' : 70
})
def putnam_1968b1(
        x : str = 'x',
        y : str = 'y',
        k = 70
    ) -> dict:

    functional_q : str = f'The temperatures in Chicago and Detroit are ${x}^\\circ$ and ${y}^\\circ$, respectively. These temperatures are not assumed to be independent; namely, we are given: \n\\begin{{itemize}}\n\\item[(i)] $P({x}^\\circ = {k}^\\circ)$, the probability that the temperature in Chicago is ${k}^\\circ$, \n\\item[(ii)] $P({y}^\\circ = {k}^\\circ)$, and \n\\item[(iii)] $P(\\max({x}^\\circ, {y}^\\circ) = {k}^\\circ)$. \n\\end{{itemize}}\nDetermine $P(\\min({x}^\\circ, {y}^\\circ) = {k}^\\circ)$.'
    functional_ans : str = f'Denote the four events ${x}^\\circ = {k}^\\circ$, ${y}^\\circ = {k}^\\circ$, $\\max({x}^\\circ, {y}^\\circ) = {k}^\\circ$, and $\\min({x}^\\circ, {y}^\\circ) = {k}^\\circ$ by $A$, $B$, $C$, $D$, respectively. Then $A \\cup B = C \\cup D$, and $A \\cap B = C \\cap D$. Hence\n\\[ P(A) + P(B) = P(A \\cup B) + P(A \\cap B) = P(C \\cup D) + P(C \\cap D) = P(C) + P(D), \\]\nand\n\\[ P(\\min({x}^\\circ, {y}^\\circ) = {k}^\\circ) = \\boxed{{P({x}^\\circ = {k}^\\circ) + P({y}^\\circ = {k}^\\circ) - P(\\max({x}^\\circ, {y}^\\circ) = {k}^\\circ)}}. \\]'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(
    year='1968', id='B5', 
    generators = {
        'p' : generators.RandomVariable('lower'),
        'J' : generators.RandomVariable('upper')
    },
    original_params={
        'p' : 'p',
        'J' : 'J'
})
def putnam_1968b5(
        p : str = 'p',
        J : str = 'J'
    ) -> dict:

    functional_q : str = f'Let ${p}$ be a prime number. Let ${J}$ be the set of all $2 \\times 2$ matrices \\( \\begin{{bmatrix}} a & b \\\\ c & d \\end{{bmatrix}} \\) whose entries are chosen from $\\{{0, 1, 2, \\dots, {p}-1\\}}$ and satisfy the conditions $a+d \\equiv 1 \\pmod{{p}}$ and $ad-bc \\equiv 0 \\pmod{{p}}$. Determine how many members ${J}$ has.'
    functional_ans : str = f'If $a=0$ then $d=1$, and if $a=1$ then $d=0$. In either case $bc \\equiv 0 \\pmod{{{p}}}$ and $b$ or $c$ is $0$, while the other is arbitrary. There are $2{p}-1$ distinct solutions to $bc \\equiv 0 \\pmod{{{p}}}$, and thus the case $a=0$ or $a=1$ accounts for a total of $4{p}-2$ solutions. If $a \\neq 0$ or $1$, then $d$ is uniquely determined and $bc \\equiv ad \\pmod{{{p}}}$ implies that for each $b \\neq 0$, there is a unique $c$, since the integers mod ${p}$ form a field. Hence for each $a$ in this case, there are ${p}-1$ solutions. The total number of solutions is $4{p}-2+({p}-2)({p}-1)=\\boxed{{{p}^2+{p}}}$.'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


