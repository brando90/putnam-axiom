import random
import string
import inspect
from typing import Callable, Dict, List, Union

import numpy as np

PUTNAM_VARIATIONS = {}

def replace_map(string: str, map: dict[str, str]) -> str:
    """
    Replaces all instances of the keys in the map with the corresponding values.
    :param string: The string to replace characters in.
    :param map: A dictionary mapping characters to their replacements.
    :return: The string with all replacements made.
    """
    for key, value in map.items():
        string = string.replace(key, str(value))
    return string


# def sample_variation(func, num_probs_per_seed_prob: int = 5):
def sample_variation(func):
    """
    Decorator that takes in a function that generates a problem variation and samples from it using
    func.param_variations
    :param func: The function that generates the variation.
    """

    assert hasattr(func, 'generators'), f'Function {func} does not have generators attribute'


    # TODO: fix me Kai! :)
    # TODO: this always generates the same question 
    def wrapper(**kwargs) -> List[Dict]:
        sampled_params = kwargs.copy()

        assert func.generators is not None, (f'Function {func} does not have generators attribute. Did you '
                                             f'forget to set the generators parameter in the @variation decorator?')

        need_to_generate = func.generators.keys()

        for param in need_to_generate:
            # prioritize the given params over the generated ones
            if param in kwargs:
                sampled_params[param] = kwargs[param]
            else:
                sampled_params[param] = func.generators[param].sample(sampled_params=sampled_params)

        assert set(sampled_params.keys()) == set(func.original_params.keys()), \
            (
                f'Generated params do not match original params: '
                f'{list(sampled_params.keys())} vs {list(func.original_params.keys())}'
            )

        # TODO: has to be tested
        sample = func(**sampled_params)
        try:
            result = {
                'problem': sample['problem'],
                'solution': sample['solution'],
                'type' : sample['type'],
                'params': sampled_params
            }
        except:
            print(sample)
        return result
        # TODO: fix me Kai! :)
        # results: List[Dict] = []
        # for _ in range(num_probs_per_seed_prob):
        #     sample = func(**sampled_params)
        #     result = {
        #         'problem': sample['problem'],
        #         'solution': sample['solution'],
        #         'params': sampled_params
        #     }
        #     results.append(result)
        # result = results
        # return results
    return wrapper


def variation(year: str, id: str,
            #   generators: dict | Callable = None,
            generators: Union[Dict, Callable] = None,
              original_params: dict = None):
    """
    Decorator that takes in a function that generates a problem variation and adds it to the variations dictionary
    with the year and id as the key.
    :param year: The year of the Putnam exam.
    :param id: The id of the problem.
    :param generators: Dictionary of parameter generators or a callable that generates the parameters.
    :param original_params: The original parameters of the problem.
    """

    def decorator(func):
        if year not in PUTNAM_VARIATIONS:
            PUTNAM_VARIATIONS[year] = {}
        if id in PUTNAM_VARIATIONS[year]:
            raise ValueError(f'Variation for year {year} and id {id} already exists.')

        func.original_params = original_params
        if callable(generators):
            func.sample = generators
        else:
            func.generators = generators
            func.sample = sample_variation(func)

        # assert that the function params match the given original_params
        func_params = set(inspect.signature(func).parameters.keys())
        assert func_params == set(original_params.keys()), \
            f'Function {func.__name__} signature {func_params} does not match original parameters {set(original_params.keys())}'

        PUTNAM_VARIATIONS[year][id] = func
        return func

    return decorator


def single_char_variable(excluded_chars: str, case: str = 'both_lower_and_upper_cases') -> str:
    """
    excluded_chars := "Characters that the user specified not to choose"
    ref: https://chat.openai.com/c/31a6b2ce-b9ec-40bd-aad3-c3527aab05b4
    """
    assert excluded_chars != ''
    if case == 'lower':
        characters = string.ascii_lowercase
    elif case == 'upper':
        characters = string.ascii_uppercase
    else:
        characters = string.ascii_letters
    # Create a list of characters to choose from, excluding the specified ones
    allowed_chars = [char for char in characters if char not in excluded_chars]

    # Choose a random character from the allowed list
    random_char = random.choice(allowed_chars)

    # Convert the random character to a string (it is already a string, but for clarity)
    random_char_str = str(random_char)
    return random_char_str


def assert_dicts_different(dict1: dict, dict2: dict):
    """Recursively asserts that two dictionaries are different."""
    assert isinstance(dict1, dict), "First argument must be a dictionary"
    assert isinstance(dict2, dict), "Second argument must be a dictionary"

    if dict1 == dict2:
        raise AssertionError("Dictionaries are equal")

    for key in dict1:
        if key not in dict2:
            continue
        
        value1 = dict1[key]
        value2 = dict2[key]

        if isinstance(value1, dict) and isinstance(value2, dict):
            assert_dicts_different(value1, value2)
        else:
            print(f'key: {key}, value1: {value1}, value2: {value2}')
            assert value1 != value2, f"Values for key '{key}' are equal"

# -- Tests

def single_char_variable_test_():
    # Characters that the user specified not to choose
    for i in range(10):
        excluded_chars = "aeiou"  # Example: Excluding vowels
        rand_char = single_char_variable(excluded_chars)
        excluded_chars += rand_char
        print(rand_char)


if __name__ == '__main__':
    single_char_variable_test_()
    print(f'Done!\a')
