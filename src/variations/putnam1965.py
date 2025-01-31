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
    year='1965', id='A1', 
    generators = {
        'A' : generators.RandomVariable('upper'),
        'B' : generators.RandomVariable('upper'),
        'C' : generators.RandomVariable('upper')
    },
    original_params={
        'A' : 'A',
        'B' : 'B',
        'C' : 'C'
})
def putnam_1965a1(
        A : str = 'A',
        B : str = 'B',
        C : str = 'C'
    ) -> dict:

    functional_q : str = f'Let ${A}{B}{C}$ be a triangle with angle ${A} < \\angle {C} < 90^\\circ < \\angle {B}$. Consider the bisectors of the external angles at ${A}$ and ${B}$, each measured from the vertex to the opposite side (extended). Suppose both of these line-segments are equal to ${A}{B}$. Compute the angle ${A}$.'
    functional_ans : str = f'Suppose the bisector of the exterior angle at ${A}$ intersects line ${B}{C}$ at $X$ and the bisector of the exterior angle at ${B}$ meets the line ${A}{C}$ at $Y$. The assumption that ${C}$ is between ${B}$ and $X$ contradicts the fact that $\\angle {B} > \\angle {C}$, so we may assume that ${B}$ is between $X$ and ${C}$. Similarly, we conclude that ${C}$ is between ${A}$ and $Y$ because $\\angle {A} < \\angle {C}$.\n\nIf $Z$ is a point on line ${A}{B}$ with ${B}$ between ${A}$ and $Z$, we have from triangle ${A}{B}Y$ that $\\angle Z{B}Y = 2{A}$. Hence, $\\angle {B}X{A} = \\angle {A}{B}X = \\angle Z{B}{C} = 2 \\angle Z{B}Y = 4{A}$, and the angle sum of triangle ${A}{B}X$ is $90^\\circ - \\frac{{1}}{{2}}{A} + 8{A}$. Thus, ${A} = \\boxed{{12}}^\\circ$.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1965', id='A2', 
    generators = {
        'n' : generators.RandomVariable('lower'),
        'r' : generators.RandomVariable('lower')
    },
    original_params={
        'n' : 'n',
        'r' : 'r'
})
def putnam_1965a1(
        n : str = 'n',
        r : str = 'r'
    ) -> dict:

    functional_q: str = f'Given any positive integer ${n}$ find the value of \\n\\[ \\sum_{{{r}=0}}^{{\\lfloor ({n}-1)/2 \\rfloor}} \\left\\{{\\frac{{{n} - 2{r}}}{{{n}}}\\binom{{{n}}}{{{r}}}\\right\\}}^2, \\]\\n where $\\lfloor x \\rfloor$ means the greatest integer not exceeding $x$, and $\\binom{{{n}}}{{{r}}}$ is the binomial coefficient \"${n}$ choose ${r}$,\" with the convention $\\binom{{0}}{{0}} = 1$. Return your final answer in binomial coefficient form with all other multiplicants reduced to the lowest form.'
    functional_ans: str = f'Substituting $s={n}-{r}$ in the given summation reveals that twice this sum is equal to:\n\\[\n\\sum_{{{r}=0}}^{n} \\left(\\frac{{{n}-2{r}}}{{n}} \\binom{{n}}{{r}}\\right)^2 = \\sum \\left(1 - 2\\frac{{{r}}}{{{n}}}\\right)^2 \\binom{{{n}}}{{{r}}}^2 = \\sum \\binom{{{n}}}{{{r}}}^2 - 4\\sum \\frac{{{r}}}{{{n}}} \\binom{{{n}}}{{{r}}}^2 + 4\\sum \\left(\\frac{{{r}}}{{{n}}}\\right)^2 \\binom{{{n}}}{{{r}}}^2.\n\\]\n\\[\n= \\binom{{2{n}}}{{{n}}} - 4 \\sum_{{{r}=1}}^{n} \\binom{{{n}-1}}{{{r}-1}} \\binom{{{n}}}{{{r}}} + 4 \\sum_{{{r}=1}}^{n} \\binom{{{n}-1}}{{{r}-1}}^2.\n\\]\n\\[\n= \\binom{{2{n}}}{{{n}}} - 4\\binom{{2{n}-1}}{{{n}-1}} + 4\\binom{{2{n}-2}}{{{n}-1}}.\n\\]\n\\[\n= \\frac{{2{n}(2{n}-1)}}{{{n}^2}} - \\frac{{4({n}-1)}}{{{n}}}\\binom{{2{n}-2}}{{{n}-1}} = \\boxed{{\\frac{{1}}{{{n}}}\\binom{{2{n}-2}}{{{n}-1}}}}.\\n\\]'
   
    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "variable"
    }

@variation(
    year='1965', id='A5', 
    generators = {
        'n' : generators.RandomVariable('lower')
    },
    original_params={
        'n' : 'n'
})
def putnam_1965a5(
        n : str = 'n'
    ) -> dict:

    functional_q : str = f'In how many ways can the integers from 1 to ${n}$ be ordered subject to the condition that, except for the first integer on the left, every integer differs by 1 from some integer to the left of it?'
    functional_ans : str = f'On the basis of the first few cases we conjecture the answer is $2^{{{n}-1}}$ and proceed by induction.\n\nWe first show (also by induction) that an ${n}$-arrangement ends in 1 or ${n}$. Note that when ${n}$ is deleted from an ${n}$-arrangement, the result is an $({n}-1)$-arrangement. If an ${n}$-arrangement does not end in 1 or ${n}$, deletion of ${n}$ produces an $({n}-1)$-arrangement ending (by induction) in $({n}-1)$. This implies the ${n}$-arrangement ended in ${n}$ because ${n}$ cannot precede $({n}-1)$.\n\nFor any ${n}$-arrangement $(a_1, a_2, \\cdots, a_{n})$ there is another ${n}$-arrangement $(a_1\', a_2\', \\cdots, a_{n}\')$, where $a_i\' = {n}+1-a_i$. If one of these ends in ${n}$, the other ends in 1 and consequently exactly half of the ${n}$-arrangements end in ${n}$.\n\nAll of the ${n}$-arrangements which end in ${n}$ can be obtained by adjoining an ${n}$ to the end of all $({n}-1)$-arrangements, and by induction there are $2^{{{n}-2}}$ of these. Hence, there are $\\boxed{{2^{{{n}-1}}}}$ ${n}$-arrangements.'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1965', id='B1', 
    generators = {
        'n' : generators.RandomVariable('lower'),
        'x' : generators.RandomVariable('lower')
    },
    original_params={
        'n' : 'n',
        'x' : 'x'
})
def putnam_1965b1(
        n : str = 'n',
        x : str = 'x'
    ) -> dict:

    functional_q : str = f'Evaluate \n\\[\n\\lim_{{{n} \\to \\infty}} \\int_0^1 \\int_0^1 \\cdots \\int_0^1 \\cos^2 \\left(\\frac{{\\pi}}{{2{n}}}({x}_1 + {x}_2 + \\cdots + {x}_{n})\\right) d{x}_1 d{x}_2 \\cdots d{x}_n.\n\\]'
    functional_ans : str = f'The change of variables ${x}_k \\to 1 - {x}_k$ yields\n\\[\n\\int_0^1 \\int_0^1 \\cdots \\int_0^1 \\cos^2 \\left(\\frac{{\\pi}}{{2{n}}}({x}_1 + {x}_2 + \\cdots + {x}_{n})\\right) d{x}_1 d{x}_2 \\cdots d{x}_{n} \\\\\n= \\int_0^1 \\int_0^1 \\cdots \\int_0^1 \\sin^2 \\left(\\frac{{\\pi}}{{2{n}}}({x}_1 + {x}_2 + \\cdots + {x}_{n})\\right) d{x}_1 d{x}_2 \\cdots d{x}_{n}.\n\\]\nEach of these expressions, being equal to half their sum, must equal $\\frac{{1}}{{2}}$. The limit is also $\\boxed{{\\frac{{1}}{{2}}}}$.'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }