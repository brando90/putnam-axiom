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
    year='1950', id='1', 
    generators = {
        'a' : generators.RandomVariable('lower'),
        'b' : generators.RandomVariable('lower'),
    },
    original_params={
        'a' : 'a',
        'b' : 'b',
})
def putnam_19501(
        a : str = 'a',
        b : str = 'b'
    ) -> dict:

    functional_q : str = f'For what values of the ratio ${a}/{b}$ is the limaçon $r = {a} - {b}\\cos\\theta$ a convex curve? (${a} > {b} > 0$) Return the lower bound of the values.'
    functional_ans : str = replace_map(
        'The graph of $r = f(\\theta)$ in polar coordinates is a simple closed curve surrounding the origin if $f$ is periodic with period $2\\pi$ and everywhere positive. This is the case in the present problem, since by hypothesis ${a} > {b} > 0$. Such a curve is nonsingularly parametrized by $\\theta$ if $r^2 + (r\')^2 > 0$, again true in the present problem. The curvature is given by\n\\[ \\kappa = \\frac{r^2 + 2(r\')^2 - rr\'\'}{[r^2 + (r\')^2]^{3/2}} \\]\n(whenever $f$ is of class $C^2$).\n\nThe curve is convex if and only if the curvature is everywhere non-negative, i.e., if and only if\n\\[ r^2 + 2(r\')^2 - rr\'\' \\geq 0. \\]\n\nFor $r = {a} - {b}\\cos\\theta$, we have $r\' = {b}\\sin\\theta$, $r\'\' = {b}\\cos\\theta$ and\n\\[ r^2 + 2(r\')^2 - rr\'\' = {a}^2 + 2{b}^2 - 3{a}{b}\\cos\\theta. \\]\n\nThis last expression is always non-negative if and only if\n\\[ {a}^2 + 2{b}^2 - 3{a}{b} \\geq 0. \\]\n\n(Since ${a}$ and ${b}$ are positive, the least value occurs for $\\theta = 0$.) This is equivalent to\n\\[ ({a} - 2{b})({a} - {b}) \\geq 0, \\]\nand since ${a} - {b} > 0$ by hypothesis, to\n\\[ {a} \\geq 2{b}. \\]\n\nThus the limaçon is convex if and only if ${a} \\geq 2{b}$ which makes the lower bound \\boxed{2}.',
        map = {'{a}' : a, '{b}' : b}
    )
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='1950', id='9', 
    generators = {
        'day' : generators.RandomInt(1,31)
    },
    original_params={
        'day' : 25
})
def putnam_19509(
        day : int = 25
    ) -> dict:
    dayname = 'Christmas' if day == 25 else f'December {day}'
    functional_q : str = f'In the Gregorian calendar: \\begin{{enumerate}} \\item[(i)] years not divisible by 4 are common years; \\item[(ii)] years divisible by 4 but not by 100 are leap years; \\item[(iii)] years divisible by 100 but not by 400 are common years; \\item[(iv)] years divisible by 400 are leap years; \\item[(v)] a leap year contains 366 days; a common year 365 days. \\end{{enumerate}} Find the probability that {dayname} falls on a Wednesday given its calculated across $N$ years.'
    functional_ans : str = f'According to the rules given, any 400 consecutive Gregorian years will involve 303 ordinary years and 97 leap years making a total of $400 \\cdot 365 + 97$ days. Since this number is divisible by 7 ($400 \\equiv 1, \\; 365 \\equiv 1, \\; 97 \\equiv -1 \\; \\text{{(mod 7)}}$), there is an integral number of weeks in 400 years (in fact, 20,871 weeks) and therefore the day of the week on which {dayname} (or any other calendar date) falls repeats in cycles of 400. If there are $N$ years in such a period on which {dayname} falls on Wednesday, then the probability that {dayname} falls on Wednesday is $\\boxed{{N/400}}$. But $N/400 \\neq 1/7$ for any integer $N$.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }