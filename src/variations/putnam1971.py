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
    year='1971', id='A5', 
    generators = {
        'a' : generators.RandomVariable('lower'),
        'b' : generators.RandomVariable('lower')
    },
    original_params={
        'a' : 'a',
        'b' : 'b'
})
def putnam_1971a5(
        a : str = 'a',
        b : str = 'b'
    ) -> dict:

    functional_q : str = f'A game of solitaire is played as follows. After each play, according to the outcome, the player receives either ${a}$ or ${b}$ points (${a}$ and ${b}$ are positive integers with ${a}$ greater than ${b}$), and his score accumulates from play to play. It has been noticed that there are thirty-five non-attainable scores and that one of these is 58. Find ${a}+{b}$.'
    functional_ans : str = f'The attainable scores are those non-negative integers expressible in the form ${a}x + {b}y$ with $x$ and $y$ non-negative integers. If ${a}$ and ${b}$ are not relatively prime there are infinitely many non-attainable scores. Hence $({a}, {b}) = 1$. It will be shown that the number of non-attainable scores is $\\frac{{1}}{{2}}({a} - 1)({b} - 1)$.\n\nIf $m$ is an attainable score, the line ${a}x + {b}y = m$ passes through at least one lattice point in the closed first quadrant. Because ${a}$ and ${b}$ are relatively prime, the lattice points on a line ${a}x + {b}y = m$ are at a horizontal distance of $[b]$. The first-quadrant segment of ${a}x + {b}y = m$ has a horizontal projection of $m/{a}$ and thus every score $m \\geq {a}{b}$ is attainable. Every non-attainable score must satisfy $0 \\leq m < {a}{b}$.\n\nIf $0 \\leq m < {a}{b}$, the first-quadrant segment of the line ${a}x + {b}y = m$ has a horizontal projection less than ${b}$, and so contains at most one lattice point. Thus there is a one-to-one correspondence between lattice points $(x, y)$ with $0 \\leq {a}x + {b}y < {a}{b}$ in the first quadrant and attainable scores with $0 \\leq m < {a}{b}$. The closed rectangle $0 \\leq x \\leq {b}$, $0 \\leq y \\leq {a}$ contains $({a} + 1)({b} + 1)$ lattice points, so the number of lattice points in the first quadrant with $0 \\leq {a}x + {b}y < {a}{b}$ is ${a}{b} - \\frac{{1}}{{2}}({a} + 1)({b} + 1) + 1 = \\frac{{1}}{{2}}({a} - 1)({b} - 1)$.\n\nIn our given example $70 = ({a} - 1)({b} - 1) = 1(70) = 2(35) = 5(14) = 7(10)$. The conditions ${a} > {b}$, $({a}, {b}) = 1$ yield two possibilities ${a} = 71, {b} = 2$ and ${a} = 11, {b} = 8$. Since 58 = 71(0) + 2(29), the first of these alternatives is eliminated. The line $11x + 8y = 58$ passes through $(6, -1)$ and $(-2, 10)$ and thus does not pass through a lattice point in the first quadrant. The unique solution is ${a} = 11$, ${b} = 8$ making the final answer \\boxed{{19}}.'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1971', id='B4', 
    generators = {
        'A' : generators.RandomVariable('upper'),
        'B' : generators.RandomVariable('upper'),
        'P' : generators.RandomVariable('upper')
    },
    original_params={
        'A' : 'A',
        'B' : 'B',
        'P' : 'P'
})
def putnam_1971b4(
        A : str = 'A',
        B : str = 'B',
        P : str = 'P'
    ) -> dict:

    functional_q : str = f'A \"spherical ellipse\" with foci ${A}, {B}$ on a given sphere is defined as the set of all points ${P}$ on the sphere such that $\\widehat{{{P}{A}}} + \\widehat{{{P}{B}}} = \\text{{constant}}$. Here $\\widehat{{{P}{A}}}$ denotes the shortest distance on the sphere between ${P}$ and ${A}$. Determine the entire class of real spherical ellipses which are circles by finding the \\text{{constant}} value.'
    functional_ans : str = f'We take the radius of the sphere as unity and denote the constant sum $\\widehat{{{P}{A}}} + \\widehat{{{P}{B}}}$ by $2a$. To avoid trivial and degenerate cases we assume that $0 < \\widehat{{{A}{B}}} < \\pi$ and that $\\widehat{{{A}{B}}} < 2a < 2\\pi - \\widehat{{{A}{B}}}$.  \n\nThe case $2a > \\pi$ can be reduced to the case $2a < \\pi$. For, if ${A}\'$ and ${B}\'$ are the points diametrically opposite to ${A}$ and ${B}$ then $\\widehat{{{P}{A}}} + \\widehat{{{P}{B}}} = 2a$ if and only if $\\widehat{{{P}{A}}}\' + \\widehat{{{P}{B}}}\' = 2\\pi - 2a$; that is, the spherical ellipses $\\widehat{{{P}{A}}} + \\widehat{{{P}{B}}} = 2a$ and $\\widehat{{{P}{A}}}\' + \\widehat{{{P}{B}}}\' = 2\\pi - 2a$ are identical. Since $\\min(2a, 2\\pi - 2a) \\leq \\pi$, we may assume without loss of generality that $2a \\leq \\pi$. \n\nLet ${A}$ and ${B}$ lie on the equator.  There are two points $V_1$ and $V_2$ (the \"vertices\") on the equator which lie on the spherical ellipse. Obviously, $V_1V_2 = 2a$. The \"center\" of the spherical ellipse (common midpoint of the arcs $\\widehat{{{A}{B}}}$ and $\\widehat{{V_1V_2}}$) will be denoted by $C$.\n\nWe first treat the case $2a < \\pi$ and show that in this case the spherical ellipse cannot be a circle. Assume it were a circle; call it $\\Gamma$ (see Figure 1). $\\Gamma$ would have to be symmetric with respect to the equatorial plane, thus lie in a plane perpendicular to the equatorial plane. $\\Gamma$ would also have to pass through the vertices. Therefore its spherical diameter would be $V_1V_2 = 2a$ and its spherical radius would be equal to $a$. The spherical center of $\\Gamma$, the center of the ellipse, let $M$ be one of the two points on $\\Gamma$ which lie half-way between the two vertices. Then, since $M$ is supposed to be a point on the spherical ellipse, $2a = \\widehat{{M{A}}} + \\widehat{{M{B}}} > \\widehat{{MC}} = 2a$ (note that $\\widehat{{MC}}$ is a right spherical triangle with the right angle at $C$ and with side $\\widehat{{MC}} = a < 2a$). Contradiction shows that the only possible spherical ellipses which are circles must occur when $2a = \\pi$.\n\nIn case $2a = \\pi$, $V_1$ and $V_2$ are diametrically opposite points on the equator. We shall show that the great circle $\\Gamma$ through the vertices and perpendicular to the equatorial plane is identical with the spherical ellipse $\\widehat{{{P}{A}}} + \\widehat{{{P}{B}}} = \\pi$. To see this, let ${B}^*$ be the reflection of ${B}$ about the plane of $\\Gamma$. ${B}^*$ is on the equator diametrically opposite to ${A}$ (see Fig. 2). Let ${P}$ be an arbitrary point on the sphere, and draw the great circle through ${A}$, ${P}$ and ${B}^*$. Then $\\widehat{{{P}{A}}} + \\widehat{{{P}{B}}} = \\pi$ if and only if $\\widehat{{{P}{B}}} = \\widehat{{{P}{B}^*}}$; that is, if and only if ${P}$ is on $\\Gamma$. This shows that $\\Gamma$ is the spherical ellipse $\\widehat{{{P}{A}}} + \\widehat{{{P}{B}}} = \\pi$, as stated above.\n\nThus the only circles on the sphere that are spherical ellipses are the great circles. For any given great circle $\\Gamma$ the foci can be any two points ${A}$ and ${B}$ which lie on the same great circle perpendicular to $\\Gamma$, on the same side of $\\Gamma$ and at equal distances from $\\Gamma$. The equation of any such spherical ellipse is $\\widehat{{{P}{A}}} + \\widehat{{{P}{B}}} = \\boxed{{\\pi}}$.'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }



