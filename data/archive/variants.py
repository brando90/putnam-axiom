import json
from collections import Counter
import re


def extract_boxed_content(data):
    boxed_contents = []
    runs = 0
    no_box = []
    for item in data:
        if item.get('answer_type', '').lower() == 'algebraic':
            runs = runs+1
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
                else:
                    no_box.append((problem_id, content))
    
    return boxed_contents, runs, no_box

# Load the JSON data
with open('/Users/aryanguls/Desktop/putnam-axiom/data/Putnam_AXIOM_Original_v3.json', 'r') as file:
    data = json.load(file)

boxed_contents, runs, no_box = extract_boxed_content(data)

print(runs)
print(len(boxed_contents))
print(no_box)
print(boxed_contents)

# Create a list of dictionaries with keys 'id', 'boxed answer', 'variant answer'
extracted_data = []
for problem_id, content in boxed_contents:
    extracted_data.append({
        'id': problem_id,
        'boxed answer': content,
        'variant answer': ''
    })

# Save the extracted data to a JSON file
with open('variant_algebraic_boxed_answers.json', 'w') as outfile:
    json.dump(extracted_data, outfile, indent=4)

print(f"Extracted {len(extracted_data)} boxed answers from {runs} algebraic problems.")