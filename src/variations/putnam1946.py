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
    year='1946', id='1', 
    generators = {
        'x' : generators.RandomVariable('lower'),
        'p' : generators.RandomVariable('lower'),
        'bound' : generators.RandomInt(1,100)
    },
    original_params={
        'x' : 'x',
        'p' : 'p',
        'bound' : 1
})
def putnam_1946a1(
        x : str = 'x',
        p : str = 'p',
        bound : int = 1
    ) -> dict:

    functional_q : str = f'Suppose that the function ${p}({x}) = a{x}^2 + b{x} + c$, where $a$, $b$, $c$ are real constants, satisfies the condition $|{p}({x})| \\leq {bound}$ for $|{x}| \\leq 1$. Find the upper bound of $|{p}\'({x})|$ for $|x| \\leq 1$.'
    functional_ans : str = f'If $a \\neq 0$, the graph of $y = ax^2 + bx + c$ is a parabola that opens upward, i.e., $a > 0$. Without loss of generality, assume $b \\geq 0$. The vertex falls in the left half-plane, and the maximum value of $|f\'(x)|$ for $|x| \\leq 1$ occurs at $x = 1$. Therefore, $|f\'(1)| = 2a + b$.\n\nNow evaluate $f(1)$ and $f(0)$:\n\\[\nf(1) = a + b + c \\leq {bound}, \\quad f(0) = c \\geq -{bound}.\n\\]\nFrom these, $a + b \\leq {2*bound}$, and since $a, b \\geq 0$, we also have $a \\leq {2*bound}$ and $2a + b \\leq {4*bound}$.\n\nFor the case $a = 0$, the function is linear: $f(x) = bx + c$, and $f\'(x) = b$. Using the conditions $f(1), f(-1)$:\n\\[\n|f\'(x)| = |b| = \\frac{{|f(1) - f(-1)|}}{{2}} \\leq {4*bound}.\n\\]\nThus, $|f\'(x)| \\leq \\boxed{{{4*bound}}}$ for all $|x| \\leq 1$ as required.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(
    year='1946', id='5', 
    generators = {
        'a' : generators.RandomVariable('lower'),
        'b' : generators.RandomVariable('lower'),
        'c' : generators.RandomVariable('lower'),
        'x' : generators.RandomVariable('lower'),
        'y' : generators.RandomVariable('lower'),
        'z' : generators.RandomVariable('lower'),
    },
    original_params={
        'a' : 'a',
        'b' : 'b',
        'c' : 'c',
        'x' : 'x',
        'y' : 'y',
        'z' : 'z'
})
def putnam_1946a5(
        a : str = 'a',
        b : str = 'b',
        c : str = 'c',
        x : str = 'x',
        y : str = 'y',
        z : str = 'z',
    ) -> dict:

    functional_q : str = f"Find the smallest volume bounded by the coordinate planes and by a tangent plane to the ellipsoid\n\\[\n\\frac{{{x}^2}}{{{a}^2}} + \\frac{{{y}^2}}{{{b}^2}} + \\frac{{{z}^2}}{{{c}^2}} = 1.\n\\]"
    functional_ans : str = replace_map(
        (
            "The tangent plane to the ellipsoid at the point $({x}_1, {y}_1, z_1)$ has the equation\n\\[\n\\frac{{x}_1}{{a}^2} + \\frac{{y}_1}{{b}^2} + \\frac{{z}_1}{{c}^2} = 1.\n\\]\nIts intercepts on the ${x}$, ${y}$, and ${z}$-axes are respectively $\\frac{{a}^2}{{x}_1}$, $\\frac{{b}^2}{{y}_1}$, and $\\frac{{c}^2}{{z}_1}$. The volume of the solid cut off by the tangent plane and the three coordinate planes is\n\\[\nV = \\frac{1}{6} \\left| \\frac{{a}^2 {b}^2 {c}^2}{{x}_1 {y}_1 {z}_1} \\right|.\n\\]\nUsing the constraint that $({x}_1, {y}_1, {z}_1)$ is a point on the ellipsoid, we express the volume as:\n\\[\nV^2 = \\frac{1}{36} {a}^2 {b}^2 {c}^2 \\left( \\frac{{x}_1^2}{{a}^2} \\cdot \\frac{{y}_1^2}{{b}^2} \\cdot \\frac{{z}_1^2}{{c}^2} \\right)^{-1}.\n\\]\nUsing the arithmetic-geometric mean inequality:\n\\[\n\\left( \\frac{{x}_1^2}{{a}^2} \\cdot \\frac{{y}_1^2}{{b}^2} \\cdot \\frac{{z}_1^2}{{c}^2} \\right)^{1/3} \\leq \\frac{1}{3} \\left( \\frac{{x}_1^2}{{a}^2} + \\frac{{y}_1^2}{{b}^2} + \\frac{{z}_1^2}{{c}^2} \\right) = \\frac{1}{3}.\n\\]\nEquality holds if and only if $\\frac{{x}_1^2}{{a}^2} = \\frac{{y}_1^2}{{b}^2} = \\frac{{z}_1^2}{{c}^2} = \\frac{1}{3}$. Thus,\n\\[\nV^2 \\geq \\frac{27}{36} {a}^2 {b}^2 {c}^2 \\quad \\text{and} \\quad V \\geq \\boxed{\\frac{1}{2} \\sqrt{3} {a}{b}{c}}.\n\\]\nEquality is achieved when $({x}_1, {y}_1, {z}_1)$ is one of the eight points for which $\\frac{{x}_1^2}{{a}^2} = \\frac{{y}_1^2}{{b}^2} = \\frac{{z}_1^2}{{c}^2} = \\frac{1}{3}$, namely\n\\[\n(\\pm \\frac{{a}}{\\sqrt{3}}, \\pm \\frac{{b}}{\\sqrt{3}}, \\pm \\frac{{c}}{\\sqrt{3}}).\n\\]"
        ),
        map = {
            '{a}' : a, '{b}' : b, '{c}' : c, '{x}' : x, '{y}' : y, '{z}' : z
        }
    )
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

