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
    year='1969', id='A2', 
    generators = {
        'D' : generators.RandomVariable('upper'),
        'n' : generators.RandomVariable('lower'),
        'i' : generators.RandomVariable('lower'),
        'j' : generators.RandomVariable('lower')
    },
    original_params={
        'D' : 'D',
        'n' : 'n',
        'i' : 'i',
        'j' : 'j'
})
def putnam_1969a2(
        D : str = 'D',
        n : str = 'n',
        i : str = 'i',
        j : str = 'j'
    ) -> dict:

    functional_q : str = f'Let ${D}_{n}$ be the determinant of order ${n}$ of which the element in the ${i}$th row and the ${j}$th column is the absolute value of the difference of ${i}$ and ${j}$. Find the value of ${D}_{n}$.'
    functional_ans : str = f'Subtract the first column from every other column. Then add the first row to every other row. The last row now has all zeros except for $({n}-1)$ in the first column. ${D}_{n}$ is $(-1)^{{n}-1}({n}-1)$ times the minor formed by deleting the first column and last row from the transformed determinant. This minor has only zeros below the main diagonal and thus is equal to the product of its diagonal elements. Hence the minor has value $2^{{n}-2}$ and ${D}_{n} = \\boxed{(-1)^{{n}-1}({n}-1)2^{{n}-2}}.$'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1969', id='B3', 
    generators = {
        'T' : generators.RandomVariable('upper'),
        'n' : generators.RandomVariable('lower')
    },
    original_params={
        'T' : 'T',
        'n' : 'n'
})
def putnam_1969b3(
        T : str = 'T',
        n : str = 'n'
    ) -> dict:

    functional_q : str = f'The terms of a sequence ${T}_{n}$ satisfy\n\\[ {T}_{n} {T}_{{n}+1} = {n} \\quad ({n} = 1, 2, 3, \\dots) \\text{{ and} } \\lim_{{{n} \\to \\infty}} \\frac{{{T}_{n}}}{{T}_{{n}+1}} = 1. \\]\nFind the value of $\\pi {T}_1^2$.'
    functional_ans : str = f'The first relation implies that\n\\[\n{T}_{n} = \\frac{{({n}-1)({n}-3)({n}-5)\\cdots}}{{({n}-2)({n}-4)({n}-6)\\cdots}} \\cdot {T}_1 \\quad \\text{{if ${n}$ is even}}, \\quad \\text{{and}}\n\\]\n\\[\n{T}_{n} = \\frac{{({n}-1)({n}-3)({n}-5)\\cdots}}{{({n}-2)({n}-4)({n}-6)\\cdots}} \\cdot {T}_1 \\quad \\text{{if ${n}$ is odd}}.\n\\]\nIf ${n}$ is odd, we have\n\\[ \\frac{{T}_{n}}{{T}_{{n}+1}} = ({T}_1)^2 \\cdot \\frac{{2}}{{1}} \\cdot \\frac{{2}}{{3}} \\cdot \\frac{{4}}{{3}} \\cdot \\frac{{4}}{{5}} \\cdot \\cdots \\cdot \\frac{{({n}-1)}}{{({n}-2)}} \\cdot \\frac{{({n}-1)}}{{n}}. \\]\nThe Wallis product gives\n\\[ \\frac{{\\pi}}{{2}} = \\prod \\left( \\frac{{2 \\cdot 4 \\cdot 6 \\cdot \\cdots}}{{1 \\cdot 3 \\cdot 5 \\cdot \\cdots}} \\right). \\]\nThus, after an even number of factors, the partial product is less than $\\pi/2$, and after an odd number of factors, the partial product is greater than $\\pi/2$. Therefore, ${T}_{n}/{T}_{{n}+1} < \\frac{{1}}{{2}} \\pi {T}_1^2$. Similarly, when ${n}$ is even, ${T}_{n}/{T}_{{n}+1} < \\frac{{2}}{{\\pi {T}_1^2}}$. Since the limit of ${T}_{n}/{T}_{{n}+1} \\to 1$, we conclude that\n\\[ \\pi {T}_1^2 = \\boxed{{2}}. \\]'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1969', id='B5', 
    generators = {
        'a' : generators.RandomVariable('lower'),
        'x' : generators.RandomVariable('lower')
    },
    original_params={
        'a' : 'a',
        'x' : 'x'
})
def putnam_1969b5(
        a : str = 'a',
        x : str = 'x'
    ) -> dict:

    functional_q : str = f'Let ${a}_1 < {a}_2 < {a}_3 < \\cdots$ be an increasing sequence of positive integers. Let the series \\[ \\sum_{{n=1}}^{{\\infty}} \\frac{{1}}{{{a}_n}} \\] be convergent. For any number ${x}$, let $k({x})$ be the number of the ${a}_n$\'s which do not exceed ${x}$. Find the value of \\lim_{{x} \\to \\infty} \\frac{k({x})}{{x}}.'
    functional_ans : str = f'The following proof shows it is not necessary to stipulate that the ${a}_n$ be integers. Suppose for some $\\epsilon > 0$ there are ${x}_j \\to \\infty$ with $k({x}_j)/{x}_j \\geq \\epsilon$. Note that if $1 \\leq n \\leq k({x}_j)$, then (because the ${a}_n$ increase) \\[ {a}_n \\leq {a}_{k({x}_j)} \\leq {x}_j \\] and \\[ \\frac{{1}}{{a}_n} \\geq \\frac{{1}}{{x}_j}. \\] Now for any positive integer $N$, \\[ \\sum_{{n=N}}^{{\\infty}} \\frac{{1}}{{{a}_n}} \\geq \\sup_j \\sum_{{n=N}}^{{k({x}_j)}} \\frac{{1}}{{{a}_n}} \\geq \\sup_j \\frac{{k({x}_j) - N}}{{{x}_j}} \\geq \\sup_j \\epsilon - \\frac{{N}}{{{x}_j}} = \\epsilon. \\] But this contradicts the convergence of $\\sum_{{n=1}}^{{\\infty}} \\frac{{1}}{{{a}_n}}$, which implies \\[ \\lim_{{N \\to \\infty}} \\sum_{{n=N}}^{{\\infty}} \\frac{{1}}{{{a}_n}} = \\boxed{0}. \\]'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


