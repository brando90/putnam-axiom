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
    year='1955', id='1', 
    generators = {
        'a' : generators.RandomPrime(min = 2, max = 97),
        'b' : generators.RandomPrime(min = 2, max = 97),
    },
    original_params={
        'a' : 2,
        'b' : 3
})
def putnam_19551(
        a : int = 2,
        b : int = 3
    ) -> dict:
    a = a[0]
    b = b[0]
    assert a != b, "The primes cannot be equal."
    functional_q : str = f'Find the number of sets of integers $m$, $n$, $p$ except $0$, $0$, $0$ for which\n\\[\nm + n\\sqrt{{{a}}} + p\\sqrt{{{b}}} = 0.\n\\]'
    functional_ans : str = f'We recall that $(1)$ if $a$ is a positive integer and $\\sqrt{{a}}$ is not an integer, then $\\sqrt{{a}}$ is irrational.\n\nSuppose that $m$, $n$, $p$ are integers such that\n\\[\nm + n\\sqrt{{{a}}} + p\\sqrt{{{b}}} = 0.\n\\]\n\nIf both $n$ and $p$ are zero, so is $m$. If just one of $n$ and $p$ is zero, we have either $\\sqrt{{{a}}} = -m/n$ or $\\sqrt{{{b}}} = -m/p$, both contrary to $(1)$. If neither $n$ nor $p$ is zero, then\n\\[\nm^2 = (n\\sqrt{{{a}}} + p\\sqrt{{{b}}})^2 = {a}n^2 + {b}p^2 + 2np\\sqrt{{{a*b}}},\n\\]\nand\n\\[\n\\sqrt{{{a*b}}} = (m^2 - {a}n^2 - {b}p^2)/2np,\n\\]\nagain contrary to $(1)$. So the only integer triplet for which $(2)$ is true is $m = 0$, $n = 0$, $p = 0$.\n\nFor completeness we include a proof of $(1)$. Suppose $a$ is a positive integer and $\\sqrt{a} = b/c$ where $b$ and $c$ are positive integers. We may assume $b$ and $c$ are relatively prime. Then $ac^2 = b^2$. Consider a prime $q$ that divides $c$. Then $q$ divides $b^2$ and hence $b$; so if there is such a prime $q$, then $b$ and $c$ have a common factor, which is a contradiction. Hence $c$ has no prime factors, so $c = 1$, and $\\sqrt{{a}} = b$, an integer. Thus there exists \\boxed{{0}} solutions except (0,0,0).'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(
    year='1955', id='6', 
    generators = {
        'n' : generators.RandomVariable('lower'),
        'x' : generators.RandomVariable('lower'),
    },
    original_params={
        'n' : 'n',
        'x' : 'x'
})
def putnam_19556(
        n : str = 'n',
        x : str = 'x'
    ) -> dict:

    functional_q : str = f'Determine a necessary and sufficient condition on the positive integer \\({n}\\) such that the equation \\({x}^{n} + (2+{x})^{n} + (2-{x})^{n} = 0\\) has a rational root.'
    functional_ans : str = f'There can be no real root if \\({n}\\) is even, since for real \\({x}\\), each term is non-negative and they cannot vanish simultaneously. If \\({n} = 1\\), there is obviously a unique root \\({x} = -4\\). Suppose \\({n}\\) is odd and at least 3. When the terms of the equation are expanded and collected, the result is monic with all coefficients non-negative integers and constant term \\(2^{{{n}+1}}\\). The only possible roots, therefore, are of the form \\(-2^p\\). For \\({x} = -1\\), all three terms of the given expression are odd, so \\(-1\\) is not a root. Putting \\({x} = -2\\), we find \\((-2)^{n} + 0 + 4^{n} \\neq 0\\), so \\(-2\\) is not a root. If we put \\({x} = -2^{{p+1}}\\) where \\(p \\geq 1\\), the left member of \\(1\\) becomes:\n\n\\[\n2^{n} \\left[-2^{{p{n}}} + 2\\left(1 + \\binom{{{n}}}{{2}} 2^{{2p}} + \\binom{{{n}}}{{4}} 2^{{4p}} + \\ldots \\right)\\right]\n\\]\n\nThe expression in the brackets is \\(\\equiv 2 \\pmod{{4}}\\) (recall \\({n} \\geq 3\\)), so \\(-2^{{p+1}}\\) is not a root for \\(p \\geq 1\\). Therefore, there are no roots if \\({n} > 1\\). Summarizing, relation \\(1\\) has a rational root if and only if \\(\\boxed{{{n} = 1}}\\).'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }