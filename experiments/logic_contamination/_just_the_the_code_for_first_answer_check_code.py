from typing import Optional


def first_boxed_only_string(string: str) -> Optional[str]:
    idx = string.find("\\boxed")
    if idx < 0:
        idx = string.find("\\fbox")
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

solution = "Hi this is dumm \\boxed{1} or \\boxed{2} or \\boxed{3}, should ouput the 1st box"

print(first_boxed_only_string(solution))
