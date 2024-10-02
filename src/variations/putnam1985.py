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
    year='1985', id='B5', 
    generators = {
        'a' : generators.RandomInt(100,3000)
    },
    original_params={
        'a' : 1985
})
def putnam_1985b5(
        a : int = 1985
    ) -> dict:

    functional_q : str = f'Given that $\\int_{{-\\infty}}^\\infty e^{{-x^2}}\\,dx = \\sqrt{{\\pi}}$, evaluate the expression $\\int_0^\\infty t^{{-1/2}}e^{{-{a}(t+t^{{-1}})}}\\,dt$.'
    functional_ans : str = f'Let $I(x) = \\int_0^\\infty t^{{-1/2}}e^{{-at-x/t}}\\, dt$, where $a = {a}$. Then \\[ I\'(x) = -\\int_0^\\infty t^{{-3/2}}e^{{-at-x/t}}\\, dt. \\] Make the substitution $u = 1/t$, and the last equation becomes \\[ I\'(x) = -\\int_0^\\infty u^{{-1/2}}e^{{-au-xu}}\\, du. \\] Now let $w = \\frac{{x}}{{a}}u$, and the last equation is \\[ I\'(x) = -\\left(\\frac{{a}}{{x}}\\right)^{{1/2}} \\int_0^\\infty w^{{-1/2}}e^{{-xw-aw}}\\, dw = -\\left(\\frac{{a}}{{x}}\\right)^{{1/2}} I(x). \\] Therefore, $\\log I(x) = -2(ax)^{{1/2}} + C$, or equivalently, $I(x) = ke^{{-2(ax)^{{1/2}}}}$. Also, \\[ k = I(0) = \\int_0^\\infty t^{{-1/2}}e^{{-at}}\\, dt = \\int_0^\\infty 2e^{{-at^2}}\\, dt = \\frac{{\\sqrt{{\\pi}}}}{{\\sqrt{{a}}}}. \\] This yields \\[ I(a) = \\boxed{{\\frac{{\\sqrt{{\\pi}}}}{{\\sqrt{{{a}}}}}e^{{{- 2 * a}}}}}. \\] (Note: the integral is essentially the K-Bessel function $K_{{1/2}}(3970)$.)'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }
