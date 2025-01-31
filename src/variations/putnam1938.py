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
    year='1938', id='1', 
    generators = {
        'z' : generators.RandomVariable('lower'),
        'h' : generators.RandomVariable('lower')
    },
    original_params={
        'z' : 'z',
        'h' : 'h',
})
def putnam_1938a1(
        z : str = 'z',
        h : str = 'h'
    ) -> dict:

    functional_q : str = f'A solid is bounded by two bases in the horizontal planes ${z} = {h}/2$ and ${z} = -{h}/2$, and by such a surface that the area of every section in a horizontal plane is given by a formula of the sort \\[ \\text{Area} = a_0 {z}^3 + a_1 {z}^2 + a_2 {z} + a_3 \\] (where as special cases some of the coefficients may be $0$). Find the volume formula where $B_1$ and $B_2$ are the areas of the bases, and $M$ is the area of the middle horizontal section. Also fine the value of $a_0$ for which the formulas for the volume of a cone and of a sphere can be included in this formula and add it to the expression of the volume you find for the final answer.'
    functional_ans : str = f'The volume in question is given by \\[ V = \\int_{{-{h}/2}}^{{{h}/2}} (a_0 {z}^3 + a_1 {z}^2 + a_2 {z} + a_3) d{z} \\] \\[ = \\frac{{a_1 {h}^3}}{{12}} + a_3 {h}. \\] On the other hand, the base areas and $M$ are given by \\[ B_1 = \\frac{{a_0 {h}^3}}{{8}} + \\frac{{a_1 {h}^2}}{{4}} + \\frac{{a_2 {h}}}{{2}} + a_3, \\] \\[ B_2 = -\\frac{{a_0 {h}^3}}{{8}} + \\frac{{a_1 {h}^2}}{{4}} - \\frac{{a_2 {h}}}{{2}} + a_3, \\] \\[ M = a_3, \\] so that the suggested expression \\( \\frac{{1}}{{6}} {h}[B_1 + B_2 + 4M] \\) works out to be \\[ \\frac{{1}}{{6}} h \\left( \\frac{{a_1 {h}^2}}{{2}} + 6a_3 \\right) = \\frac{{a_1 {h}^3}}{{12}} + a_3 {h} = V \\] as required.\\n\\nThe formula \\( V = \\boxed{{\\frac{{1}}{{6}}{h}(B_1 + B_2 + 4M)}} \\) is known in solid geometry as the prismoidal formula. It is closely related to Simpson's rule in numerical integration.""
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1938', id='11', 
    generators = {
        'm' : generators.RandomVariable('lower')
    },
    original_params={
        'm' : 'm'
})
def putnam_1938b5(
        m : str = 'm'
    ) -> dict:

    functional_q : str = f"Given the parabola $y^2 = 2{m}x$, what is the length of the shortest chord that is normal to the curve at one end?"
    functional_ans : str = f"Any point on the parabola has coordinates of the form $(2{m}t^2, 2{m}t)$. Let $AB$ be a chord normal to the parabola at $A$. Say $A = (2{m}t^2, 2{m}t)$ and $B = (2{m}s^2, 2{m}s)$. The slope of $AB$ is $1/(s + t)$, and the slope of the tangent at $A$ is $1/(2t)$. Hence $s + t = -1/(2t)$.\\n\\nThe length $L$ of $AB$ is given by\\n\\[ L^2 = 4{m}^2[(s^2 - t^2)^2 + (s - t)^2] = 4{m}^2(s - t)^2[(s + t)^2 + 1]. \\]\\nSubstituting $s = -t - 1/(2t)$ we have\\n\\[ L^2 = 4{m}^2 \\left( \\frac{{4t^2 + 1}}{{2t}} \\right)^2 \\frac{{1 + 4t^2}}{{4t^2}} = \\frac{{{m}^2}}{{4}} \\frac{{(4t^2 + 1)^3}}{{t^4}}. \\]\\nWe seek the value of $t$ which minimizes $L$, so we may just as well choose $t$ to minimize\\n\\[ \\frac{{4t^2 + 1}}{{t^{4/3}}} = 4t^{{2/3}} + t^{{-4/3}}. \\]\\nSetting the derivative equal to zero, we find two critical points, $t = \\pm \\sqrt{{2}}/2$. Since $L \\to \\infty$ as $t \\to 0$, $\\pm \\infty$, these two critical values both give minima. Either of the two shortest chords is of length $\\boxed{{3\\sqrt{{3}} |{m}|}}$, from (1)."
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

