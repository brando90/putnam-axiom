import re
from sympy import simplify, sympify, pretty
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations, 
    implicit_multiplication,
    convert_xor
)
from typing import Optional

def ground_truth_boxed_answer(solution: str) -> str:
    return normalize_final_answer(remove_boxed(last_boxed_only_string(solution)))

def get_generated_answer(result: str) -> str:
    unnormalized_answer = get_unnormalized_answer(result)
    answer = normalize_final_answer(unnormalized_answer)

    return answer

def simplify_frac(answer):
    pattern = re.compile(r'\\frac\{(.*?)\}\{(.*?)\}')
    
    # Function to replace each match
    def replacer(match):
        numerator = match.group(1)
        denominator = match.group(2)
        return f'({numerator}) / ({denominator})'

    # Perform the replacement
    return re.sub(pattern, replacer, answer)

def simplify_power(answer):
    # This pattern matches the base and exponent parts of the power expression
    pattern = re.compile(r'(\w+|\(.+?\))\^{([^{}]+)}')
    
    def replacer(match):
        base = match.group(1)
        exponent = match.group(2)
        
        # Wrap base in parentheses if it's not a single word character
        if not re.fullmatch(r'\w+', base):
            base = f'({base})'
        
        # Wrap exponent in parentheses if it's not a single word character
        if not re.fullmatch(r'\w+', exponent):
            exponent = f'({exponent})'
        
        return f'{base}^{exponent}'
    
    return re.sub(pattern, replacer, answer)


def simplify_sqrt(expression):
    # Define the regular expression pattern for \sqrt{X}
    pattern = re.compile(r'\\sqrt\{(.*?)\}')
    
    # Function to replace each match
    def replacer(match):
        content = match.group(1)
        return f'sqrt({content})'
    
    # Perform the replacement
    replaced_expression = re.sub(pattern, replacer, expression)
    
    return replaced_expression

def simplify_algebra(answer, verbose = False):
    try:
        answer = pretty(simplify(sympify(parse_expr(answer, transformations = "all"))), use_unicode = False)
    except:
        if verbose: print("Unable to reduce algebraically:", answer)
    return answer

def parse_answer(answer, verbose = False):
    ret = answer
    answer = answer.lower()
    answer = simplify_algebra(answer, verbose)
    answer = simplify_frac(answer)
    answer = simplify_sqrt(answer)
    answer = simplify_power(answer)
    answer = answer.replace('\\log', 'log')
    answer = answer.replace('\\pi', 'pi')
    answer = answer.replace('\\ln', 'ln')

    try:
        transformations = (
            standard_transformations +
            (implicit_multiplication,
            convert_xor)
        )
        ret = parse_expr(answer, transformations=transformations)
    except:
        if verbose: print("Unsuccessful Parsing:", answer)
    return ret


def simplify_answer(answer, verbose = False):
    answer = parse_answer(answer, verbose)
    try:
        answer = simplify(answer)
    except:
        if verbose: print("Unable to simplify:", answer)
    
    return answer
    

def last_boxed_only_string(string: str) -> Optional[str]:
    idx = string.rfind("\\boxed")
    if "\\boxed " in string:
        return "\\boxed " + string.split("\\boxed ")[-1].split("$")[0]
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1

    if right_brace_idx is None:
        retval = None
    else:
        retval = string[idx : right_brace_idx + 1]

    return retval

def first_boxed_only_string(string: str) -> Optional[str]:
    idx = string.find("\\boxed")
    if "\\boxed " in string:
        return "\\boxed " + string.split("\\boxed ")[-1].split("$")[0]
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1

    if right_brace_idx is None:
        retval = None
    else:
        retval = string[idx : right_brace_idx + 1]
    return retval


def remove_boxed(s: str) -> str:
    if "\\boxed " in s:
        left = "\\boxed "
        assert s[: len(left)] == left
        return s[len(left) :]

    left = "\\boxed{"

    assert s[: len(left)] == left
    assert s[-1] == "}"

    return s[len(left) : -1]


def get_unnormalized_answer(text: str) -> str:
    INVALID_ANSWER = "[invalidanswer]"
    end_seq = "I hope it is correct."
    text += end_seq
    match = re.search(
        r"Final Answer: The final answer is(.*?). I hope it is correct.",
        # r"Final Answer: The final answer is(.*?).",
        text,
    )
    if match:
        return match.group(1).strip()
    else:
        # print('++++++++++++++++++++++++++')
        # print(text)
        # print('++++++++++++++++++++++++++')
        return INVALID_ANSWER

def get_unnormalized_boxed_answer(text: str) -> str:
    INVALID_ANSWER = "[invalidanswer]"
    end_seq = "I hope it is correct."
    text += end_seq
    match = re.search(
        r"Final Answer: The final answer is(.*?). I hope it is correct.",
        # r"Final Answer: The final answer is(.*?).",
        text,
    )
    if match:
        return match.group(1).strip()
    else:
        return INVALID_ANSWER


SUBSTITUTIONS = [
    ("an ", ""),
    ("a ", ""),
    (".$", "$"),
    ("\\$", ""),
    (r"\ ", ""),
    (" ", ""),
    ("mbox", "text"),
    (",\\text{and}", ","),
    ("\\text{and}", ","),
    ("\\text{m}", "\\text{}"),
]
REMOVED_EXPRESSIONS = [
    "square",
    "ways",
    "integers",
    "dollars",
    "mph",
    "inches",
    "ft",
    "hours",
    "km",
    "units",
    "\\ldots",
    "sue",
    "points",
    "feet",
    "minutes",
    "digits",
    "cents",
    "degrees",
    "cm",
    "gm",
    "pounds",
    "meters",
    "meals",
    "edges",
    "students",
    "childrentickets",
    "multiples",
    "\\text{s}",
    "\\text{.}",
    "\\text{\ns}",
    "\\text{}^2",
    "\\text{}^3",
    "\\text{\n}",
    "\\text{}",
    r"\mathrm{th}",
    r"^\circ",
    r"^{\circ}",
    r"\;",
    r",\!",
    "{,}",
    '"',
    "\\dots",
]


def normalize_final_answer(final_answer: str) -> str:
    """
    Normalize a final answer to a quantitative reasoning question.

    Copied character for character from appendix D of Lewkowycz et al. (2022)
    """
    final_answer = final_answer.split("=")[-1]

    for before, after in SUBSTITUTIONS:
        final_answer = final_answer.replace(before, after)
    for expr in REMOVED_EXPRESSIONS:
        final_answer = final_answer.replace(expr, "")

    # Extract answer that is in LaTeX math, is bold,
    # is surrounded by a box, etc.
    final_answer = re.sub(r"(.*?)(\$)(.*?)(\$)(.*)", "$\\3$", final_answer)
    final_answer = re.sub(r"(\\text\{)(.*?)(\})", "\\2", final_answer)
    final_answer = re.sub(r"(\\textbf\{)(.*?)(\})", "\\2", final_answer)
    final_answer = re.sub(r"(\\overline\{)(.*?)(\})", "\\2", final_answer)
    final_answer = re.sub(r"(\\boxed\{)(.*)(\})", "\\2", final_answer)

    # Normalize shorthand TeX:
    #  \fracab -> \frac{a}{b}
    #  \frac{abc}{bef} -> \frac{abc}{bef}
    #  \fracabc -> \frac{a}{b}c
    #  \sqrta -> \sqrt{a}
    #  \sqrtab -> sqrt{a}b
    final_answer = re.sub(r"(frac)([^{])(.)", "frac{\\2}{\\3}", final_answer)
    final_answer = re.sub(r"(sqrt)([^{])", "sqrt{\\2}", final_answer)
    final_answer = final_answer.replace("$", "")

    # Normalize 100,000 -> 100000
    if final_answer.replace(",", "").isdigit():
        final_answer = final_answer.replace(",", "")

    return final_answer