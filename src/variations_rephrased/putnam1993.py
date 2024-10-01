import difflib
import random
import numpy as np
import math
from .utils import single_char_variable, replace_map, variation
import os
import json
from . import generators
import numpy

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
    year='1993', id='A1',
    generators={
        'm': generators.RandomInt(1, 100),
        'n': generators.RandomInt(1, 100),
        'c': generators.RandomVariable("lower")
    },
    original_params={
        'm': 2, 'n': 3, 'c': 'c'
    }
)
def putnam_1993a1(
        m : int = 2,
        n : int = 3,
        c : str = 'c'
) -> dict:

    functional_q: str = replace_map(
        (
            "Consider the intersection between the horizontal line $y={c}$ and the curve $y = {m}x - {n}x^3$ in the first quadrant. "
            "This creates two regions. The first region is bounded by the $y$-axis, the line $y={c}$ and the curve; the other lies under the curve and above the line $y={c}$ between their two points of intersection. "
            "Find ${c}$ so that the areas of the two shaded regions are equal."
        ),
        {'{m}': m, '{n}' : n, '{c}' : c}
    )

    m_over_2 = m / 2
    n_over_4 = n / 4
    coefficients = [n, -1 * n / 4, -1 * m / 2]
    roots = np.roots(coefficients)
    root = roots[0]
    ans = m * root - n * root ** 3

    functional_ans: str = replace_map(
        (
            "Let $(b, {c})$ denote the second intersection point. We wish to find ${c}$ so that\n\n\\[ \\int_0^b \\left( {c} - \\left({m}x - {n}x^3 \\right) \\right) dx = 0. \\]\n\n"
            "This leads to ${c}b - {m_over_2}b^2 + \\left({n_over_4}\\right)b^4 = 0$. After substituting ${c} = {m}b - {n}b^3$ and solving, we find that $b = {root}$ and the result follows. "
            "The value of ${c}$ is $\\boxed{{ans}}$."
        ),
        {'{m}': m, '{n}' : n, '{c}' : c, '{m_over_2}' : m_over_2, '{n_over_4}' : n_over_4,'{root}' : root, '{ans}' : ans}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "constant"
    }

@variation(
    year='1993', id='B1',
    generators={
        'm': generators.RandomVariable("lower"),
        'n': generators.RandomVariable("lower"),
        'k': generators.RandomVariable("lower"),
        'a': generators.RandomInt(100, 3000)
    },
    original_params={
        'm': 'm', 'n': 'n', 'k' : 'k', 'a': 1993
    }
)
def putnam_1993b1(
        m : str = 'm',
        n : str = 'n',
        k : str = 'k',
        a : int = 1993
) -> dict:
    
    a_plus = a + 1

    functional_q: str = replace_map(
        (
            "Identify the smallest natural number (positive integer) ${n}$ such that for every integer ${m}$ with $0 < {m} < {a}$, there exists an integer ${k}$ for which satisfies the expression \\[ \\frac{{m}}{{a}} < \\frac{{k}}{{n}} < \\frac{m+1}{{a_plus}}. \\]"
        ),
        {'{m}': m, '{n}' : n, '{k}' : k, '{a}' : a, '{a_plus}' : a_plus}
    )

    ans = 2 * a + 1
    a_minus = a - 1
    two_a = 2 * a

    functional_ans: str = replace_map(
        (
            "First, it is easily verified that\n\n\\[ \\frac{{m}}{{a}} < \\frac{2{m} + 1}{{a} + {a_plus}} < \\frac{{m} + 1}{{a_plus}}, \\]\n\nso ${n} = {a} + {a_plus} = {ans}$ suffices. Now consider ${m} = {a_minus}$ and "
            "suppose\n\n\\[ \\frac{{a_minus}}{{a}} < \\frac{{k}}{{n}} < \\frac{{a}}{{a_plus}}. \\]\n\nSince $x/(x + 1)$ is strictly increasing for $x > 0$, we must have ${k} \\leq {n} - 2$ (note: ${n} > {a_plus}$). However,\n\n\\[ \\frac{{a_minus}}{{a}} < \\frac{{n} - 2}{{n}} \\]\n\nimplies ${two_a} < n$, "
            "so $n \\geq \\boxed{{ans}}$, completing the proof."
        ),
        {'{m}': m, '{n}' : n, '{k}' : k, '{a}' : a, '{a_plus}' : a_plus, '{a_minus}' : a_minus, '{ans}' : ans, '{two_a}' : two_a}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "constant"
    }

@variation(
    year='1993', id='B2',
    generators={
        'n': generators.RandomVariable("lower"),
        'A': generators.RandomVariable("upper"),
        'B': generators.RandomVariable("upper")
    },
    original_params={
        'n': 'n', 'A' : 'A', 'B' : 'B'
    }
)
def putnam_1993b2(
        n : str = 'n',
        A : str = 'A',
        B : str = 'B'
) -> dict:
    functional_q: str = replace_map(
        (
            "Consider a game played with a deck of $2{n}$ cards, where each card is uniquely numbered from 1 to $2{n}$. The deck is shuffled randomly, and each of two players, ${A}$ and ${B}$, is dealt ${n}$ cards. Starting with ${A}$, the players take turns discarding one of their remaining cards and announcing its number. The game continues until the sum of all discarded cards becomes divisible by $2{n}+1$. The player who discards the final card, making the sum divisible by $2{n}+1$, wins the game. Assuming both players ${A}$ and ${B}$ use optimal strategy, what is the probability that ${A}$ will win?"
        ),
        {'{n}' : n, '{A}' : A, '{B}' : B}
    )

    functional_ans: str = replace_map(
        (
            "Clearly, ${A}$ cannot win on the first turn. Assume ${B}$ is to play, and that the total of announced numbers is $T$, and that ${A}$ has cards $x_1, x_2, \\dots, x_k$, and ${B}$ has cards $y_1, y_2, \\dots, y_{k+1}$. "
            "Because the integers $T + y_1, \\dots, T + y_{k+1}$ have distinct remainders upon division by $2{n} + 1$, at least one has a remainder other than $2{n} + 1 - x_1, \\dots, 2{n} + 1 - x_k$. If ${B}$ discards that $y_i$, "
            "it is impossible for ${A}$'s next discard to make the total divisible by $2{n} + 1$. Therefore, ${A}$ cannot win under optimal play by ${B}$. The probability that ${A}$ wins is \\boxed{0}."
        ),
        {'{n}' : n, '{A}' : A, '{B}' : B}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "variable"
    }

@variation(
    year='1993', id='B3',
    generators={
        'x': generators.RandomVariable("lower"),
        'y': generators.RandomVariable("lower")
    },
    original_params={
        'x': 'x', 'y' : 'y'
    }
)
def putnam_1993b3(
        x : str = 'x',
        y : str = 'y'
) -> dict:
    functional_q: str = replace_map(
        (
            "Two real numbers ${x}$ and ${y}$ are chosen at random in the interval (0,1) with respect to the uniform distribution. What is the probability that the closest integer to ${x}/{y}$ is even? Express the answer in the form $r+s\\pi$, where $r$ and $s$ are rational numbers."
        ),
        {'{x}' : x, '{y}' : y}
    )

    functional_ans: str = replace_map(
        (
            "The limit is $(5 - \\pi)/4$ (that is, when $r = 5/4$, $s = -1/4$).\n\nNote that the probability that ${x}/{y}$ is exactly half an odd integer is 0, so we may safely ignore this possibility.\n\nFor any choice of ${x}$, the closest integer to ${x}/{y}$ is even if either ${x}/{y} < .5$ or $2n - .5 < {x}/{y} < 2n + .5$ "
            "for some positive integer $n$.\n\nThe event ${x}/{y} < .5$, or $2{x} < {y}$, can occur only if ${x} < .5$. Thus its probability is\n\n\\[ \\int_0^{.5} \\left(1 - 2{x}\\right) d{x} = \\frac{1}{4}. \\]\n\nFor a positive integer $n$, the probability that $2n - .5 < {x}/{y} < 2n + .5$, i.e., "
            "that $2{x}/(4n + 1) < {y} < 2{x}/(4n - 1)$, is\n\n\\[ \\int_0^1 \\left( \\frac{2{x}}{4n - 1} - \\frac{2{x}}{4n + 1} \\right) d{x} = \\frac{1}{4n - 1} - \\frac{1}{4n + 1}. \\]\n\nSumming from $n = 1$ to $\\infty$, we get\n\n\\[ \\sum_{k=1}^{\\infty} \\left(-1\\right)^{k+1} \\frac{1}{2k + 1} = 1 - \\arctan 1 = 1 - \\frac{\\pi}{4}. \\]\n\n"
            "The total probability then is $1/4 + 1 - \\pi/4 = \\boxed{(5 - \\pi)/4}$."
        ),
        {'{x}' : x, '{y}' : y}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "variable"
    }

