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
    year='1970', id='A4', 
    generators = {
        'x' : generators.RandomVariable('lower'),
        'n' : generators.RandomVariable('lower')
    },
    original_params={
        'x' : 'x',
        'n' : 'n'
})
def putnam_1970a4(
        x : str = 'x',
        n : str = 'n'
    ) -> dict:

    functional_q : str = f'Given a sequence $\\{{{x}_{n}\\}}$, ${n}=1, 2, \\dots$, such that $\\lim_{{{n} \\to \\infty}} \\{{{x}_{n} - {x}_{{n}-2}\\}} = 0$, find the value of \\lim_{{{n} \\to \\infty}} \\frac{{{x}_{n} - {x}_{{n}-1}}}{{n}}.'
    functional_ans : str = f'For $\\varepsilon > 0$, let $N$ be sufficiently large so that $|{x}_{n} - {x}_{{n}-2}| < \\varepsilon$ for all ${n} \\geq N$. Note that for any ${n} > N$, \\[ {x}_{n} - {x}_{{n}-1} = ({x}_{n} - {x}_{{n}-2}) - ({x}_{{n}-1} - {x}_{{n}-3}) + ({x}_{{n}-2} - {x}_{{n}-4}) - \\dots \\pm ({x}_{N+1} - {x}_{N-1}) \\pm ({x}_N - {x}_{N-1}). \\] Thus \\[ |{x}_{n} - {x}_{{n}-1}| \\leq ({n}-N)\\varepsilon + |{x}_N - {x}_{N-1}|, \\] and $\\lim_{{n \\to \\infty}} \\frac{{{x}_{n} - {x}_{{n}-1}}}{{n}} = \\boxed{0}.$'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1970', id='A5', 
    generators = {
        'a' : generators.RandomVariable('lower'),
        'b' : generators.RandomVariable('lower'),
        'c' : generators.RandomVariable('lower')
    },
    original_params={
        'a' : 'a',
        'b' : 'b',
        'c' : 'c'
})
def putnam_1970a5(
        a : str = 'a',
        b : str = 'b',
        c : str = 'c'
    ) -> dict:

    functional_q : str = f'Determine the radius of the largest circle which can lie on the ellipsoid \\[ \\frac{{x^2}}{{{a}^2}} + \\frac{{y^2}}{{{b}^2}} + \\frac{{z^2}}{{{c}^2}} = 1 \\] \\( ({a} > {b} > {c}) \\).'
    functional_ans : str = f'Since parallel cross sections of the ellipsoid are always similar ellipses, any circular cross section can be increased in size by taking a parallel cutting plane passing through the center. Every plane through \\( (0, 0, 0) \\) which makes a circular cross section must intersect the \\( y-z \\) plane. But this means that a diameter of the circular cross section must be a diameter of the ellipse \\( x = 0, \\frac{{y^2}}{{{b}^2}} + \\frac{{z^2}}{{{c}^2}} = 1 \\). Hence the radius of the circle is at most \\( {b} \\). Similar reasoning with the \\( x-y \\) plane shows that the radius of the circle is at least \\( {b} \\), so that any circular cross section formed by a plane through \\( (0, 0, 0) \\) must have radius \\( {b} \\), and this will be the required maximum radius. To show that circular cross sections of radius \\( {b} \\) actually exist, consider all planes through the \\( y \\)-axis. It can be verified that the two planes given by \\( {a}^2({b}^2 - {c}^2)z^2 = {c}^2({a}^2 - {b}^2)x^2 \\) give circular cross sections of radius \\( \\boxed{{b}} \\).'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1970', id='A6', 
    generators = {
        'L' : generators.RandomVariable('upper')
    },
    original_params={
        'L' : 'L'
})
def putnam_1970a6(
        L : str = 'L'
    ) -> dict:

    functional_q : str = f'Three numbers are chosen independently at random, one from each of the three intervals $[0, {L}_i]$ $(i=1, 2, 3)$. If the distribution of each random number is uniform with respect to length in the interval it is chosen from, determine the expected value of the smallest of the three numbers chosen.'
    functional_ans : str = f'Let $x$ be selected from $[0, {L}_1]$, $y$ from $[0, {L}_2]$, and $z$ from $[0, {L}_3]$, and assume ${L}_3 \\geq {L}_2 \\geq {L}_1$. Let $X = \\min(x, y, z)$. The expected value is given by \\[ E[X] = \\int_0^{{{L}_1}} \\int_0^{{{L}_2}} \\int_0^{{{L}_3}} X \\; dz \\; dy \\; dx. \\] Breaking this into components, we compute the integral \\[ {L}_1 {L}_2 {L}_3 E[X] = \\int_0^{{{L}_1}} \\int_0^{{{L}_2}} \\left( \\int_0^\\mu z \\; dz + \\int_\\mu^{{{L}_3}} \\mu \\; dz \\right) dy \\; dx, \\] where $\\mu = \\min(x, y)$. This evaluates to \\[ \\int_0^{{{L}_1}} \\int_0^{{{L}_2}} \\{{{L}_3 \\mu - \\frac{{1}}{{2}} \\mu^2 \\}} dy \\; dx. \\] Further, we split the integral and calculate the contributions for $x$ and $y$, leading to \\[ \\frac{{1}}{{2}} {L}_1^2 {L}_2 {L}_3 - \\frac{{1}}{{6}} {L}_1^3 ({L}_2 + {L}_3) + \\frac{{1}}{{12}} {L}_1^4. \\] Hence, the expected value is \\[ \\boxed{{\\frac{{1}}{{2}} {L}_1^2 {L}_2 {L}_3 - \\frac{{1}}{{6}} {L}_1^3 ({L}_2 + {L}_3) + \\frac{{1}}{{12}} {L}_1^4}}. \\]'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


