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
    year='1948', id='2', 
    generators = {
        'r' : generators.RandomVariable('lower'),
        'R' : generators.RandomVariable('upper')
    },
    original_params={
        'r' : 'r',
        'R' : 'R',
})
def putnam_19482(
        r : str = 'r',
        R : str = 'R'
    ) -> dict:

    functional_q : str = f'Two spheres in contact have a common tangent cone. These three surfaces divide the space into various parts, only one of which is bounded by all three surfaces; it is \"ring-shaped.\" Being given the radii of the spheres, ${r}$ and ${R}$, find the volume of the \"ring-shaped\" part. (The desired expression is a rational function of ${r}$ and ${R}$.)'
    functional_ans : str = replace_map(
        'Let $\\alpha$ be the angle of the cone, and place the spheres as shown in the cross-section diagram, with centers at $O_1$ and $O_2$ and origin of the coordinate system at $O$, the point of contact.\n\nThe equation of the larger circle is\n\\[\nx^2 + y^2 + 2{R}x = 0\n\\]\nand the equation of the smaller is\n\\[\nx^2 + y^2 - 2{r}x = 0.\n\\]\nFrom the diagram,\n\\[\n\\sin \\alpha = \\frac{O_1P}{O_1O_2} = \\frac{{R} - {r}}{{R} + {r}},\n\\]\nso\n\\[\n\\cos^2 \\alpha = \\frac{4{R}r}{({R} + {r})^2}.\n\\]\nWe compute $V_1$, the volume of the frustum of the cone obtained by revolving area $A_1A_2B_2B_1$ about the $x$-axis.\n\nVolume of larger cone = \\[\n\\frac{1}{3}\\pi A_1B_1^2 \\cdot B_1T = \\frac{1}{3} \\pi {R}^2 \\cos^2 \\alpha \\cdot {R} \\cot \\alpha \\cos \\alpha = \\frac{16\\pi}{3} {R}^3 \\cdot \\frac{{r}^2{R}^2}{({R} - {r})({R} + {r})^3}.\n\\]\nVolume of smaller cone = \\[\n\\frac{16\\pi}{3} {r}^3 \\cdot \\frac{{r}^2{R}^2}{({R} - {r})({R} + {r})^3}.\n\\]\n\nTheir difference is\n\\[\nV_1 = \\frac{16\\pi}{3} \\cdot \\frac{{r}^2{R}^2}{({R} + {r})^3} \\cdot ({R}^2 + {R}{r} + {r}^2).\n\\]\nLet $V_2$ and $V_3$ be, respectively, the volumes of the larger spherical segment and the smaller spherical segment enclosed in the frustum of the cone.\n\\[\nV_2 = \\pi \\int_{{R} \\sin \\alpha}^0 \\left(-x^2 - 2{R}x\\right) dx = \\frac{4\\pi {R}^3{r}^2}{3({R} + {r})^3}(3{R} + {r}),\n\\]\nand\n\\[\nV_3 = \\pi \\int_0^{{r}(1 + \\sin \\alpha)} \\left(-x^2 + 2{r}x\\right) dx = \\frac{4\\pi}{3} \\cdot \\frac{{R}^2{r}^3}{({R} + {r})^3}({R} + 3{r}).\n\\]\n\nThe desired volume is given by\n\\[\nV_1 - V_2 - V_3 = \\frac{4\\pi}{3} \\cdot \\frac{{R}^2{r}^2}{({R} + {r})^3} \\cdot \\left[4({R}^2 + {R}{r} + {r}^2) - 3{R}^2 - {R}{r} - 3{r}^2 - {R}{r}\\right] = \\boxed{\\frac{4\\pi}{3} \\cdot \\frac{{R}^2{r}^2}{{R} + {r}}}.\n\\]',
        map = {'{r}' : r, '{R}' : R}
    )
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1948', id='11', 
    generators = {
        'a' : generators.RandomVariable('lower'),
        'b' : generators.RandomVariable('lower'),
        't' : generators.RandomVariable('lower')
    },
    original_params={
        'a' : 'a',
        'b' : 'b',
        't' : 't'
})
def putnam_19482(
        a : str = 'a',
        b : str = 'b',
        t : str = 't'
    ) -> dict:

    functional_q : str = f'The pairs of numbers $({a}, {b})$ such that $|{a} + {b}{t} + {t}^2| \\leq 1$ for $0 \\leq {t} \\leq 1$ fill a certain region in the $({a}, {b})$-plane. What is the area of this region?'
    functional_ans : str = replace_map(
        'Consider \\[ f({t}) = {a} + {b}{t} + {t}^2. \\] This function has just one critical value, at ${t} = -{b}/2$ where its value is ${a} - {b}^2/4$. On the interval $[0, 1]$, $f$ can have extreme values only at the endpoints and at the critical point if it should happen to fall in $[0, 1]$ (that is, if ${b} \\in [-2, 0]$). Hence the extreme values of $f$ are \\[ f(0) = [a] \\quad \\text{and} \\quad f(1) = {a} + {b} + 1 \\] if ${b} \\notin [-2, 0]$, and they are in the set \\[ \\{{a}, {a} + {b} + 1, {a} - {b}^2/4\\} \\] if ${b} \\in [-2, 0]$.\\nHence $|f({t})| \\leq 1$ for all ${t} \\in [0, 1]$ if and only if \\[ {b} \\notin [-2, 0] \\quad \\text{and} \\quad |{a}| \\leq 1, \\ |{a} + {b} + 1| \\leq 1 \\] or \\[ {b} \\in [-2, 0], \\quad |{a}| \\leq 1, \\ |{a} + {b} + 1| \\leq 1, \\ |{a} - {b}^2/4| \\leq 1. \\]\\nThe region required is therefore as shown in the diagram where the arc from $A$ to $B$ is part of the parabola ${a} - {b}^2/4 = -1$.\\nThe area of the required region can be obtained in several ways. The parallelogram $CEDF$ evidently has area 4. We must subtract the area of the piece $AFB$. Since $\\overline{AF}$ and $\\overline{FB}$ are tangents to the parabola, the area of $AFB$ is $\\frac{1}{3}$ that of the triangle $AFB$ (Archimedes\' rule). But triangle $AFB$ has base $AF$ of length 1 and altitude 1, so its area is $\\frac{1}{2}$ and the curvilinear piece $AFB$ has area $\\frac{1}{6}$. Hence the area of $CEDBA$ is $4 - \\frac{1}{6} = \\boxed{\\frac{23}{6}}$.',
        map = {'{a}' : a, '{b}' : b, '{t}' : t}
    )
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }
