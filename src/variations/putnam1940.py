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
    year='1940', id='4', 
    generators = {
        'p' : generators.RandomVariable('lower')
    },
    original_params={
        'p' : 'p'
})
def putnam_1940a4(
        p : str = 'p'
    ) -> dict:

    functional_q : str = f'The parabola $y^2 = -4{p}x$ rolls without slipping around the parabola $y^2 = 4{p}x$. Find the equation of the locus of the vertex of the rolling parabola.'
    functional_ans : str = f"If the rolling parabola and the fixed parabola are tangent at the point $Q$, it is obvious from symmetry that the vertex $V$ of the rolling parabola is the reflection of the origin (the vertex of the fixed parabola) in the tangent line at $Q$. \n\nIn the sketch, we have tacitly assumed ${p} > 0$. Suppose that $Q$ is the point $(4{p}t^2, 4{p}t)$. [Any point on the fixed parabola will have this form for a unique $t$.] The slope of the tangent at $Q$ is $1/(2t)$ and the equation of the tangent is \n\\[ y = \\frac{{1}}{{2t}}x + 2pt. \\]\n\nThe perpendicular on this line through the origin has the equation \n\\[ y = -2tx. \\]\n\nThese lines intersect at \n\\[ \\left( \\frac{{-4{p}t^2}}{{1+4t^2}}, \\frac{{8{p}t^3}}{{1+4t^2}} \\right) \\]\nso the vertex $V$ is at\n\\[ \\left( \\frac{{-8{p}t^2}}{{1+4t^2}}, \\frac{{16{p}t^3}}{{1+4t^2}} \\right). \\]\n\nThis gives us the parametric equations\n\\[ x = \\frac{{-8{p}t^2}}{{1+4t^2}}, \\quad y = \\frac{{16{p}t^3}}{{1+4t^2}} \\]\nfor the path of the point $V$. Since $-2t = y/x$ (if $x \\neq 0$), the elimination of $t$ gives \n\\[ x = \\frac{{-2{p}\\left(\\frac{{y}}{{x}}\\right)^2}}{{1+\\left(\\frac{{y}}{{x}}\\right)^2}} \\]\nso that \n\\[ \\boxed{{(x^2 + y^2)x + 2{p}y^2 = 0}} \\tag{{1}} \\]\n\nis an equation satisfied by all points of the locus (including $(0, 0)$). Conversely, any point $(x, y)$ other than the origin satisfying (1) leads to a value of $t(= -y/2x)$ and is therefore on the locus. Thus (1) describes the locus precisely."
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1940', id='5', 
    generators = {
        'm' : generators.RandomVariable('lower'),
        'n' : generators.RandomVariable('lower')
    },
    original_params={
        'm' : 'm',
        'n' : 'n'
})
def putnam_1940a5(
        m : str = 'm',
        n : str = 'n'
    ) -> dict:

    functional_q : str = f"The simultaneous equations $x^4 - x^2 = y^4 - y^2 = z^4 - z^2$ are satisfied by the points of ${n}$ straight lines and ${m}$ ellipses, and by no other points. Find ${m}+{n}$."
    functional_ans : str = f"Let $L$ denote the locus of the given equations. Then a point is on $L$ if and only if its coordinates $(x, y, z)$ satisfy \n\\[ (x^2 + y^2 - 1)(x^2 - y^2) = 0 \\tag{{1}} \\]\n\\[ (y^2 + z^2 - 1)(y^2 - z^2) = 0 \\tag{{2}} \\]\n\\[ (z^2 + x^2 - 1)(z^2 - x^2) = 0 \\tag{{3}} \\]\n\nConsider the loci $A$, $B$, $C$, $D$ defined as follows:\n\\[ A: \\begin{{cases}} x^2 + y^2 - 1 = 0, \\\\ y^2 - z^2 = 0 \\end{{cases}} \\]\n\\[ B: \\begin{{cases}} y^2 + z^2 - 1 = 0, \\\\ z^2 - x^2 = 0 \\end{{cases}} \\]\n\\[ C: \\begin{{cases}} z^2 + x^2 - 1 = 0, \\\\ x^2 - y^2 = 0 \\end{{cases}} \\]\n\\[ D: x^2 = y^2 = z^2. \\]\n\n$A$ is the intersection of a right circular cylinder with the union of the planes $z = y$ and $z = -y$. Hence $A$ is the union of two ellipses. Similarly $B$ and $C$ are each the union of two ellipses. $D$, on the other hand, is the union of four straight lines, namely: \n\\[ x = y = z, \\quad x = y = -z, \\quad x = -y = z, \\quad x = -y = -z. \\]\n\nAny point common to $A$ and $B$ is in fact also on $D$, so the ellipses of $A$ and $B$ are different. Similarly for $B$ and $C$ and for $C$ and $A$. Hence $A \\cup B \\cup C \\cup D$ consists of the union of 6 (distinct) ellipses and 4 (distinct) lines.\n\nWe now show that $L = A \\cup B \\cup C \\cup D$. If $(x, y, z) \\in A$, then evidently $(x, y, z)$ satisfies (1), (2), and (3), the latter because \n\\[ z^2 + x^2 - 1 = (x^2 + y^2 - 1) + (z^2 - y^2) = 0. \\]\nThus $A \\subseteq L$. Similarly $B \\subseteq L$ and $C \\subseteq L$. It is immediate that $D \\subseteq L$. So $A \\cup B \\cup C \\cup D \\subseteq L$.\n\nNow consider a point $p(x, y, z)$ of $L$ that is not on $D$. Assume, therefore, \n\\[ x^2 \\neq y^2 \\text{{ and }} x^2 \\neq z^2. \\]\nSince $p$ satisfies (1) and (3), we have \n\\[ x^2 + y^2 - 1 = 0 \\text{{ and }} x^2 + z^2 - 1 = 0 \\]\nand therefore $y^2 = z^2$, so $p \\in A$. The other cases of inequalities lead to $p \\in B$ or $p \\in C$ by the same argument. Hence $L \\subseteq A \\cup B \\cup C \\cup D$ and indeed $L = A \\cup B \\cup C \\cup D$ is the union of 4 lines and 6 ellipses. The final answer is \\boxed{{10}}."
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


