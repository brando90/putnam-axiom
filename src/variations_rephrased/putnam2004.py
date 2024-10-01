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
    year='2004', id='A1',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'S' : generators.RandomVariable('upper'),
        'N' : generators.RandomVariable('upper'),
        'n' : generators.RandomInt(2,500)
    },
    original_params={
        'S' : 'S', 'N' : 'N', 'n' : 5
    }
)
def putnam_2004a1(
        S: str = 'S', N: str = 'N', n: int = 5) -> dict:
    
    nice_n = [2, 5, 10, 20, 50, 100]
    if n in nice_n:
        perc = int((n-1) / n * 100) # By construction, this should be a whole integer
        percDot = (f'.{perc * 10}').replace('0', '') # Removes all trailing 0's,
        percPercentage = f'{perc}\\%'
        percFrac = f'{n-1}/{n}'
    else:
        perc = f'\\frac{{{n-1}}}{{{n}}}'
        percDot = perc
        percPercentage = perc
        percFrac = f'{n-1}/{n}'
    
    functional_q: str = f'Shanille O’Keal’s statistician is monitoring her successful free throws out of her first ${N}$ attempts this season, denoted as ${S}({N})$. At the beginning of the season, ${S}({N})$ was below 80\\% of ${N}$, but by the season’s end, ${S}({N})$ exceeded 80\\% of ${N}$. Must there be a point during the season when ${S}({N})$ was exactly {perc}\\% of ${N}$? Provide a yes or no answer.'

    functional_ans: str = f'Suppose there wasn\'t. Then there would be an ${N}$ such that ${S}({N}) < {percDot}{N}$ and ${S}({N}+1) > {percDot}({N}+1)$; that is, O\'Keal\'s free throw percentage is under ${perc}\\%$ at some point, and after one subsequent free throw (necessarily made), her percentage is over ${percPercentage}$. If she makes $m$ of her first $N$ free throws, then $m/{N} < {percFrac}$ and $(m+1)/({N}+1) > {percFrac}$. This means that ${n}m < {n-1}n < {n}m+1$, which is impossible since then ${n-1}n$ is an integer between the consecutive integers ${n}m$ and ${n}m+1$. \\boxed{{Yes}}.'

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : 'constant'
    }
