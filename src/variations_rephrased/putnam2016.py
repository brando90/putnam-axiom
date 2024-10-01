import difflib
import random
import numpy as np
import math
from .utils import single_char_variable, replace_map, variation
import os
import json
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
    year='2016', id='A1',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'j': generators.RandomVariable('lower'),
        'p': generators.RandomVariable('lower'),
    },
    original_params={
        'j': 'j', 'p': 'p',
    }
)
def putnam_2016a1(
        j : str = 'j',
        p : str = 'p',
) -> dict:

    functional_q: str = replace_map(
        (
            "Find the smallest positive integer ${j}$ such that for every polynomial ${p}(x)$ with integer coefficients and for every integer $k$," 
            " the integer \\[ {p}^{({j})}(k) = \\left. \\frac{d^{j}}{dx^{j}} {p}(x) \\right|_{x=k}  \\]  (the ${j}$-th derivative of ${p}(x)$ at $k$) is divisible by 2016."
        ),
        {'{j}': j, '{p}' : p}
    )

    functional_ans: str = replace_map(
        (
            "First suppose that ${j}$ satisfies the given condition. For ${p}(x) = x^{j}$, we have ${p}^{({j})}(x) = {j}!$ and thus ${j}!$ is divisible by $2016$." 
            " Since $2016$ is divisible by $2^5$ and $7!$ is not, it follows that ${j} \\geq 8$. Conversely, we claim that ${j}=8$ works. Indeed, let ${p}(x) = \\sum_{m=0}^n a_m x^m$ be a polynomial with integer coefficients;" 
            " then if $k$ is any integer,  \\begin{align*} {p}^{(8)}(k) &= \\sum_{m=8}^n m(m-1)\\cdots (m-7) a_m k^{m-8} \\\\ &= \\sum_{m=8}^n {m\\choose 8} 8! a_m k^{m-8} \\end{align*} is divisible by $8! = 20 \\cdot 2016$," 
            " and so ${p}^{(8)}(k)$ is divisible by $2016$. The answer is ${j}=\\boxed{8}$."
        ),
        {'{j}': j, '{p}' : p}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "variable"
    }

@variation(
    year='2016', id='A2',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'M': generators.RandomVariable('upper'),
        'm': generators.RandomVariable('lower'),
        'n': generators.RandomVariable('lower'),
    },
    original_params={
        'M': 'M', 'm': 'm', 'n' : 'n'
    }
)

def putnam_2016a2(
        M : str = 'M',
        m : str = 'm',
        n : str = 'n'
) -> dict:

    functional_q: str = replace_map(
        (
            "Given a positive integer ${n}$, let ${M}({n})$ be the largest integer ${m}$ such that  \\[ \\binom{{m}}{{n}-1} > \\binom{{m}-1}{{n}}. \\] Evaluate  \\[ \\lim_{{n} \\to \\infty} \\frac{{M}({n})}{{n}}. \\]"
        ),
        {'{M}': M, '{m}' : m, '{n}' : n}
    )

    functional_ans: str = replace_map(
        (
            "Note that for ${m} > {n}+1$, both binomial coefficients are nonzero and their ratio is \\begin{align*} {{m}\\choose {n}-1}/{{m}-1\\choose {n}} &= \\frac{{m}!{n}!({m}-{n}-1)!}{({m}-1)!({n}-1)!({m}-{n}+1)!} \\\\" 
            " &= \\frac{{m}{n}}{({m}-{n}+1)({m}-{n})}. \\end{align*} Thus the condition ${{m}\\choose{{n}-1}} > {{{m}-1}\\choose {n}}$ is equivalent to $({m}-{n}+1)({m}-{n})-{m}{n} < 0$. The left hand side of this last inequality is a quadratic function of ${m}$ with roots" 
            " \\begin{align*} \\alpha({n}) &= \\frac{3{n}-1+\\sqrt{5{n}^2-2{n}+1}}{2}, \\\\ \\beta({n}) &= \\frac{3{n}-1-\\sqrt{5{n}^2-2{n}+1}}{2}, \\end{align*} both of which are real since $5{n}^2-2{n}+1 = 4{n}^2+({n}-1)^2 > 0$; it follows that ${m}$ satisfies the given" 
            " inequality if and only if $\\beta({n}) < {m} < \\alpha({n})$. (Note in particular that since $\\alpha({n})-\\beta({n}) = \\sqrt{5{n}^2-2{n}+1} > 1$, there is always some integer ${m}$ between $\\beta({n})$ and $\\alpha({n})$.)   We conclude that ${M}({n})$" 
            " is the greatest integer strictly less than $\\alpha({n})$, and thus that  $\\alpha({n})-1 \\leq {M}({n}) < \\alpha({n})$. Now \\[ \\lim_{{n}\\to\\infty} \\frac{\\alpha({n})}{{n}} = \\lim_{{n}\\to\\infty} \\frac{3-\\frac{1}{{n}}+\\sqrt{5-\\frac{2}{{n}}+\\frac{1}{{n}^2}}}{2} = \\frac{3+\\sqrt{5}}{2} \\]" 
            " and similarly $\\lim_{{n}\\to\\infty} \\frac{\\alpha({n})-1}{{n}} = \\frac{3+\\sqrt{5}}{2}$, and so by the sandwich theorem, $\\lim_{{n}\\to\\infty} \\frac{{M}({n})}{{n}} = \\frac{3+\\sqrt{5}}{2}$. The answer is $\\boxed{\\frac{3+\\sqrt{5}}{2}}$."
        ),
        {'{M}': M, '{m}' : m, '{n}' : n}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "variable"
    }
