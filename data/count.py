'''
Script to count the number of questions with boxed solutions, the number of questions with modified boxing, and the number of binary solutions.
'''

import json
from collections import Counter
import re

def count_boxed_solutions(data):
    return sum('\\boxed{' in item.get('solution', '') for item in data)

def count_modified_boxing(data):
    return sum(item.get('source') == 'putnam (modified boxing)' for item in data)

def count_answer_types(data):
    answer_types = [item.get('answer_type') for item in data if 'answer_type' in item]
    return Counter(answer_types)

def extract_boxed_content(data):
    boxed_contents = []
    for item in data:
        solution = item.get('solution', '')
        problem_id = item.get('id', 'Unknown ID')
        # Find all \boxed{ occurrences
        start_indices = [m.start() for m in re.finditer(r'\\boxed{', solution)]
        for start in start_indices:
            # Initialize brace count and starting position
            brace_count = 1
            pos = start + 7  # Start after '\boxed{'
            
            # Find the matching closing brace
            while brace_count > 0 and pos < len(solution):
                if solution[pos] == '{':
                    brace_count += 1
                elif solution[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            # Extract the content if we found a matching closing brace
            if brace_count == 0:
                content = solution[start+7:pos-1]  # Exclude the outer braces
                boxed_contents.append((problem_id, content))
    
    return boxed_contents

def count_binary_solutions(boxed_contents):
    return sum(1 for _, content in boxed_contents if content.strip() in ['0', '1'])

def find_unboxed_questions(data):
    unboxed = []
    for item in data:
        if '\\boxed{' not in item.get('solution', ''):
            problem_id = item.get('id', 'Unknown ID')
            solution = item.get('solution', 'No solution provided')
            unboxed.append((problem_id, solution))
    return unboxed


# Load the JSON data
with open('/Users/aryanguls/Desktop/putnam-axiom/data/Putnam_AXIOM_Original_v3.json', 'r') as file:
    data = json.load(file)

# Count the occurrences
boxed_count = count_boxed_solutions(data)
modified_boxing_count = count_modified_boxing(data)
answer_type_counts = count_answer_types(data)
boxed_contents = extract_boxed_content(data)
binary_solutions_count = count_binary_solutions(boxed_contents)
unboxed_questions = find_unboxed_questions(data)

# Output results
print(f"Number of questions with '\\boxed{{' in their solution: {boxed_count}")
print(f"Number of items with 'putnam (modified boxing)' as source: {modified_boxing_count}")
print(f"Number of solutions that are either 0 or 1: {binary_solutions_count}")
print("\nAnswer type counts:")
for answer_type, count in answer_type_counts.items():
    print(f"{answer_type}: {count}")

print(f"\nTotal number of questions: {len(data)}")
print(f"Number of unique answer types: {len(answer_type_counts)}")
print("\nContents of \\boxed{} in solutions:")
for i, (problem_id, content) in enumerate(boxed_contents, 1):
    print(f"{i}. Problem ID: {problem_id}, Boxed Content: {content}")
for problem_id, solution in unboxed_questions:
    print(f"Problem ID: {problem_id}")
    print(f"Solution: {solution}\n")