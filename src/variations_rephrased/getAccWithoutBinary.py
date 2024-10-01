import os, json
from pathlib import Path
import pandas as pd

# Example usage
var_dataset = Path('~/putnam-math/data/Putnam_MATH_variations_static6/Putnam_AXIOM_Variations.json').expanduser()
lm_outputs = Path('~/putnam-math/data/LM_outputs').expanduser()
vars = None

path_names = []
with open(var_dataset, 'r') as f:
    vars = json.load(f)
nonbin_len = 0
for prob in vars:
    if prob['variation'] == 0 and prob['answer_type'] != 'binary':
        nonbin_len += 1
print(nonbin_len)

final_out = []
output_path = Path('putnam-math/data/LM_outputs/Binary_Analysis.json')
for PATH_NAME in lm_outputs.iterdir():
    ret = {}
    if 'variations' not in PATH_NAME.name or '.csv' not in PATH_NAME.name: continue # We only get the variations.
    model_response = pd.read_csv(PATH_NAME)
    model_name = PATH_NAME.name.split('/')[-1][:-4]
    ret['model'] = model_name
    og_correct = model_response['Original Correct'][0][18:].split(',')  # Gets a list of the correct
    var_correct = model_response['Variation Correct'][0][19:].split(',')

    def isBinary(id):
        for prob in vars:
            prob_str = prob['year'] + '_' + prob['id']
            if prob_str == id:
                return prob['answer_type'] == 'binary'
    
    og_len = len(og_correct)
    for id in og_correct:
        if isBinary(id):
            og_len -= 1
    ret['og_correct'] = len(og_correct)/61
    ret['og_correct_without_binary'] = og_len/nonbin_len
    print('ORIGINAL CORRECT WITHOUT BINARY:', og_len/nonbin_len, len(og_correct)/61)

    var_len = len(var_correct)
    for id in var_correct:
        if isBinary(id):
            var_len -= 1
    print('VARIATION CORRECT WITHOUT BINARY:', var_len/nonbin_len, len(var_correct)/61)
    ret['var_correct'] = len(var_correct)/61
    ret['var_correct_without_binary'] = var_len/nonbin_len
    final_out.append(ret)
with open(output_path, 'w') as f:
    json.dump(final_out, f, indent=4)