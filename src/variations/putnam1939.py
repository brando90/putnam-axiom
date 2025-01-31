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
    year='1939', id='2', 
    generators = {
        'P' : generators.RandomVariable('upper'),
        'Q' : generators.RandomVariable('upper'),
        'n' : generators.RandomVariable('lower')
    },
    original_params={
        'P' : 'P',
        'Q' : 'Q',
        'n' : 'n'
})
def putnam_1939a2(
        P : str = 'P',
        Q : str = 'Q',
        n : str = 'n'
    ) -> dict:

    functional_q : str = f'A point ${P}$ is taken on the curve $y = x^3$. The tangent at ${P}$ meets the curve again at ${Q}$. Given the slope of the curve at ${Q}$ is ${n}$ times the slope at ${P}$ find the value of ${n}$.'
    functional_ans : str = f"Let ${P}$ have coordinates $(x_0, y_0)$; then the slope at ${P}$ is $3x_0^2$. The equation of the tangent at ${P}$ is $y = 3x_0^2(x - x_0) + x_0^3$. The points of intersection of the tangent and the original curve are determined by the relation\\n\\[ x^3 = 3x_0^2(x - x_0) + x_0^3, \\]\\nwhich is equivalent to\\n\\[ (x - x_0)^2(x + 2x_0) = 0. \\]\\nHence the second point of intersection is $(-2x_0, -8x_0^3)$. The slope at this point is $12x_0^2$, which is four times the slope at ${P}$, as was to be proved.\\n\\nIf $x_0 = 0$, the tangent does not really meet the curve again. However, since the tangent in this case has a triple point of intersection with the curve, instead of the usual double point of intersection, it is reasonable to say that it meets the curve \"again\" at $(0,0)$ making ${n} = \\boxed{{4}}$."
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1939', id='5', 
    generators = {
        'A' : generators.RandomVariable('upper'),
        'B' : generators.RandomVariable('upper'),
        'a' : generators.RandomVariable('lower')
    },
    original_params={
        'A' : 'A',
        'B' : 'B',
        'a' : 'a'
})
def putnam_1939a5(
        A : str = 'A',
        B : str = 'B',
        a : str = 'a'
    ) -> dict:

    functional_q : str = f"A heavy particle is attached to the end ${A}$ of a light rod ${A}{B}$ of length ${a}$. The rod is hinged at ${B}$ so that it can turn freely in a vertical plane. The rod is balanced in the vertical position above the hinge and then slightly disturbed. Find an expression for the time taken to pass from the horizontal position to the lowest position."
    functional_ans : str = f"Let $m$ be the mass of the particle, and let $\\theta$ be the angular position of the rod, measured from the vertical, at time $t$. The force of gravity $mg$ can be resolved into two components, $mg \\cos \\theta$ acting along the rod, and $mg \\sin \\theta$ acting perpendicular to the rod. The former is counterbalanced by the tension (or compression) in the rod and the latter accelerates the particle along the circle of radius $a$. By Newton’s third law we have \\[ mg \\sin \\theta = ma \\frac{{d^2 \\theta}}{{dt^2}}. \\] Multiply through by \\( \\frac{{2}}{{m}} \\frac{{d\\theta}}{{dt}} \\) to get \\[ 2g \\sin \\theta \\frac{{d \\theta}}{{dt}} = 2a \\frac{{d \\theta}}{{dt}} \\frac{{d^2 \\theta}}{{dt^2}}. \\] This can be integrated to give \\[ -2g \\cos \\theta + k = a \\left( \\frac{{d\\theta}}{{dt}} \\right)^2. \\] From the initial conditions, $\\theta = \\frac{{d \\theta}}{{dt}} = 0$ when $t = 0$, we find $k = 2g$. Thus we have \\[ {a} \\left( \\frac{{d \\theta}}{{dt}} \\right)^2 = 2g(1 - \\cos \\theta) = 4g \\sin^2 (\\theta/2), \\] whence \\[ \\frac{{d \\theta}}{{dt}} = 2\\sqrt{{\\frac{{g}}{{{a}}}}} \\sin (\\theta/2). \\] We have chosen the positive square root because \\( \\frac{{d\\theta}}{{dt}} \\) is positive for $0 < \\theta \\leq \\pi$.\\nThe time required for the passage from $\\theta = \\pi/2$ to $\\theta = \\pi$ is given by \\[ \\int_{{\\pi/2}}^{{\\pi}} \\frac{{dt}}{{d \\theta}} d \\theta = \\int_{{\\pi/2}}^\\pi \\frac{{1}}{{2\\sqrt{{{a}/g}} \\sin (\\theta/2)}} d\\theta = \\sqrt{{\\frac{{{a}}}{{g}}}} \\int_{{\\pi/2}}^\\pi \\csc (\\theta/2) d \\theta. \\] Substituting $u = \\theta/2$, the limits change to $u = \\pi/4$ and $u = \\pi/2$, and the integral becomes \\[ \\sqrt{{\\frac{{{a}}}{{g}}}} \\int_{{\\pi/4}}^{{\\pi/2}} \\csc u \\ d u = \\sqrt{{\\frac{{{a}}}{{g}}}} \\left[ -\\log (\\csc u + \\cot u) \\right]_{{\\pi/4}}^{{\\pi/2}}. \\] Evaluating at the limits, \\[ \\boxed{{\\sqrt{{\\frac{{{a}}}{{g}}}} \\log (1 + \\sqrt{{2}})}}. \\]"
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1939', id='6', 
    generators = {
        'a' : generators.RandomVariable('lower')
    },
    original_params={
        'a' : 'a'
})
def putnam_1939a6(
        a : str = 'a'
    ) -> dict:

    functional_q : str = f"A circle of radius ${a}$ rolls on the inner side of the circumference of a circle of radius $3{a}$. Find the area contained within the closed curve generated by a point on the circumference of the rolling circle."
    functional_ans : str = f"Take rectangular coordinates with the origin at the center of the large circle so that the generating point $P$ is in contact with the large circle at $A = (3{a}, 0)$. It can be seen from the diagram that when the small circle has rolled until the line of centers makes an angle $\\theta$ with $OA$, the coordinates of $P$ are \\[ x = 2{a} \\cos \\theta + {a} \\cos 2\\theta \\] \\[ y = 2{a} \\sin \\theta - {a} \\sin 2\\theta. \\] These are, then, parametric equations for the path of $P$.\\nThe area is given by \\[ A = \\frac{{1}}{{2}} \\oint (x \\ dy - y \\ dx). \\] \\[ = \\frac{{{a}^2}}{{2}} \\int_0^{{2\\pi}} \\{{ [2 \\cos \\theta + \\cos 2\\theta][2 \\cos \\theta - 2 \\cos 2\\theta] - [2 \\sin \\theta - \\sin 2\\theta][2 \\sin \\theta - 2 \\sin 2\\theta] \\}} d\\theta \\] \\[ = \\frac{{{a}^2}}{{2}} \\int_0^{{2\\pi}} (2 - 2 \\cos 3\\theta) d\\theta = \\boxed{{2\\pi {a}^2}}. \\]"
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


