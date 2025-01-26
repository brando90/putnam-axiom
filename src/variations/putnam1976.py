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
    year='1976', id='A3',
    generators = {
        'n' : generators.RandomVariable('lower'),
        'm' : generators.RandomVariable('lower')
    },
    original_params={
        'n' : 'n',
        'm' : 'm'
})
def putnam_1975a4(
        p : str = 'p',
        q : str = 'q',
        r : str = 'r',
        s : str = 's'
    ) -> dict:
    
    functional_q : str = f'Find all integral solutions of the equation \\[|{p}^{r} - {q}^{s}| = 1,\\] where ${p}$ and ${q}$ are prime numbers and ${r}$ and ${s}$ are positive integers larger than unity. Prove that there are no other solutions. Return the sum of all quadruples ({p}, {q}, {r}, {s}) by adding corresponding {p}, {q}, {r} and {s} values across all solutions and giving the final summed quadruple.'
    functional_ans : str = f'We show that the only solutions are given by $3^2 - 2^3 = 1$, i.e., $({p}, {r}, {q}, {s}) = (3, 2, 2, 3)$ or $(2, 3, 3, 2)$.\\\n\nClearly either ${p}$ or ${q}$ is $2$. Suppose ${q} = 2$. Then $p$ is an odd prime with ${p}^{r} \\pm 1 = 2^{s}$. If ${r}$ is odd, $({p}^{r} \\pm 1)/({p} \\pm 1)$ is the odd integer ${p}^{r-1} + {p}^{{{r}-2}} + {p}^{{{r}-3}} + \\cdots + 1$, which is greater than $1$ since ${r} > 1$; this contradicts the fact that $2^{s}$ has no such factor.\\\n\nNow we try ${r}$ as an even integer $2t$. Then ${p}^{r} + 1 = 2^{s}$ leads to \\[ 2^{s} = ({p}^t)^2 + 1 = (2n+1)^2 + 1 = 4n^2 + 4n + 2, \\] which is impossible since $4 \\not| (4n^2 + 4n + 2)$.\\\n\nAlso ${r} = 2t$ and ${p}^{r} - 1 = 2^{s}$ leads to \\[ ({p}^t)^2 - 1 = (2n+1)^2 - 1 = 4n^2 + 4n = 4n(n+1) = 2^{s}. \\] Since either $n$ or $n+1$ is odd, this is only possible for $n = 1$, ${s} = 3$, ${p} = 3$, and ${r} = 2$. Thus the final quadruple is \\boxed{(5, 5, 5, 5)}.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }
