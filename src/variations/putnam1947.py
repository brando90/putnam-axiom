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
    year='1947', id='2', 
    generators = {
        'x' : generators.RandomVariable('lower'),
        'y' : generators.RandomVariable('lower'),
        'i' : generators.RandomInt(1,100)
    },
    original_params={
        'x' : 'x',
        'y' : 'y',
        'i' : 1
})
def putnam_1947a2(
        x : str = 'x',
        y : str = 'y',
        i : int = 1
    ) -> dict:

    functional_q : str = f'A real valued continuous function satisfies for all real $x$ and $y$ the functional equation \n\\[ f(\\sqrt{{{x}^2 + {y}^2}}) = f({x})f({y}). \\]\nFind the value of f(x) in terms of f({i}). \\]'
    functional_ans : str = f'A slight qualification in the statement of the problem is needed since the real valued continuous function $f(x) \\equiv 0$ satisfies the functional equation for all real ${x}$ and ${y}$, but does not satisfy the relation $f(0) = [f(1)]^0$, since $0^0$ is undefined.\n\nAssume then that for some $y_0$, $f(y_0) \\neq 0$. Since\n\\[ f({x})f(y_0) = f(\\sqrt{{{x}^2 + y_0^2}}) = f(-{x})f(y_0), \\]\nwe have $f({x}) = f(-{x}) = f(|{x}|)$ for all ${x}$. We now show by induction that for any positive integer $n$ and any real number ${x}$, we have\n\\[ f(\\sqrt{{n}}{x}) = [f({x})]^n. \\]\nThis is certainly true for $n = 1$, and assuming it true for $n = k$ we have\n\\[ f(\\sqrt{{k+1}}{x}) = f(\\sqrt{{k+1}}|{x}|) = f(\\sqrt{{(\\sqrt{{k}}{x})^2 + {x}^2}}) = f(\\sqrt{{k}}{x})f({x}) \\]\n\\[ = [f({x})]^k f({x}) = [f({x})]^{{k+1}}. \\]\nTherefore (1) is true for all positive integers $n$.\n\nIf $p$ and $q$ are non-zero integers, then\n\\[ f(p) = f(|p|) = f(\\sqrt{{p^2 \\cdot 1}}) = [f(1)]^{{p^2}} \\]\nand\n\\[ f(|p|) = f\\left(\\sqrt{{\\frac{{q^2}}{{q^2}}|p|^2}}\\right) = \\left[f\\left(\\frac{{|p|}}{{q}}\\right)\\right]^{{q^2}}. \\]\nFrom these two relations it follows that\n\\[ \\left[f\\left(\\frac{{p}}{{q}}\\right)\\right]^{{q^2}} = [f(1)]^{{p^2}}. \\]\nIf $f(1) > 0$ it then follows that\n\\[ \\left[f\\left(\\frac{{p}}{{q}}\\right)\\right] = [f(1)]^{{p^2/q^2}}; \\]\nthat is, the required equation is valid for all rational values of $x$ except, perhaps, $x = 0$. By continuity it follows for all values of $x$.\n\nIf $f({i}) = 0$, then (2) implies that $f(\\frac{{p}}{{q}}) = 0$ for all non-zero integers $p$ and $q$, and thus $f({x}) = 0$ for all rational ${x}$, hence for all real $x$.\n\nFinally we show that $f({i}) < 0$ is impossible. If $p$ is even and $q$ is odd, equation (2) implies that $f(\\frac{{p}}{{q}}) > 0$. Hence $f(x) > 0$ for a dense set of ${x}$, and therefore $f({x}) \\geq 0$ for all ${x}$; in particular, $f({i}) \\geq 0$. This makes the final answer \\boxed{{f({i})^{{{str(x) if i == 1 else '(' + str(x) + '/' + str(i) + ')^2'}}}}}.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(
    year='1947', id='10', 
    generators = {
        'z' : generators.RandomVariable('lower'),
        'a' : generators.RandomVariable('lower'),
        'b' : generators.RandomVariable('lower'),
        'r' : generators.RandomInt(1,100)
    },
    original_params={
        'z' : 'z',
        'a' : 'a',
        'b' : 'b',
        'r' : 1
})
def putnam_1947b4(
        z : str = 'z',
        a : str = 'a',
        b : str = 'b',
        r : int = 1
    ) -> dict:

    rreplace = r if r != 1 else ''
    unitreplace = 'unit ' if r == 1 else 'r-'
    functional_q : str = f"Given $P({z}) = {rreplace}{z}^2 + {a}{z} + {b}$, a quadratic polynomial of the complex variable ${z}$ with complex coefficients ${a}, {b}$. Suppose that $|P({z})| = {r}$ for every ${z}$ such that $|{z}| = {r}$. Find the values of ${a}$ and ${b}$ and give their sum."
    functional_ans : str = f'In particular, \\( |p({r})| = |p(-{r})| = {r} \\), so \\( {r} + {a} + {b} \\) and \\( {r} - {a} + {b} \\) lie on the {unitreplace}circle. Hence their midpoint \\( {r} + {b} \\) lies in the {unitreplace}disk. Similarly, \\( |p({rreplace}i)| = |p(-{rreplace}i)| = {r} \\), so \\( -{r} + i{a} + {b} \\) and \\( -{r} - i{a} + {b} \\) lie on the {unitreplace}circle and hence their midpoint \\( -{r} + {b} \\) lies in the {unitreplace}disk. But \\( {r} + {b} \\) and \\( -{r} + {b} \\) are a distance {2*r} apart, so they must lie at either end of a diameter of the {unitreplace}circle and hence \\( {b} = 0 \\). Now \\( {r} + {a} \\) and \\( {r} - {a} \\) lie on the {unitreplace}circle, as does their midpoint \\( {r} \\). Hence they must coincide and so \\( {a} = 0 \\). Thus, \\( a + b = 0 \\).'
    
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(
    year='1947', id='11', 
    generators = {
        'a' : generators.RandomVariable('lower'),
        'b' : generators.RandomVariable('lower'),
        'c' : generators.RandomVariable('lower'),
        'd' : generators.RandomVariable('lower'),
        'x' : generators.RandomVariable('lower'),
        'r' : generators.RandomVariable('lower')
    },
    original_params={
        'a' : 'a',
        'b' : 'b',
        'c' : 'c',
        'd' : 'd',
        'x' : 'x',
        'r' : 'r'
})
def putnam_1947b5(
        a : str = 'a',
        b : str = 'b',
        c : str = 'c',
        d : str = 'd',
        x : str = 'x',
        r : str = 'r'
    ) -> dict:

    functional_q : str = f"{a}, {b}, {c}, {d} are distinct integers such that\n\\[ ({x} - {a})({x} - {b})({x} - {c})({x} - {d}) - 4 = 0 \\]\nhas an integral root ${r}$. Find the value of $4{r}$."
    functional_ans : str = f'Since ${r}$ is a root,\n\\[ ({r} - {a})({r} - {b})({r} - {c})({r} - {d}) = 4, \\]\nand since ${a}, {b}, {c}, {d}$ are distinct integers, ${r} - {a}, {r} - {b}, {r} - {c}, {r} - {d}$ are distinct integers whose product is 4. But the only set of four distinct integers whose product is 4 is the set \\{{1, -1, 2, -2\\}}. Hence\n\\[ ({r} - {a}) + ({r} - {b}) + ({r} - {c}) + ({r} - {d}) = 1 - 1 + 2 - 2 = 0, \\]\nso\n\\[ 4{r} = \\boxed{{a + b + c + d}}. \\]'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }
