import os
import json

from pathlib import Path
# Example usage
variation_dir = Path('~/putnam-math/data/Putnam_MATH_variations_static6/test').expanduser() # Change to reflect wherever the variations are.
original_dir = Path('~/putnam-math/data/Putnam_MATH_variations_static6/original').expanduser() # Change to reflect whatever the original problems are.
output_path = Path('~/putnam-math/data/Putnam_MATH_variations_static6/Putnam_AXIOM_Variations.json').expanduser()

combined_data = []

constant = set()
variable = set()
sig = set()
    
# Iterate through all files in the folder
for variation in variation_dir.iterdir():
    var_number = variation.stem.split('_')[-1]
    for prob_file in variation.iterdir():

        # Open and load each JSON file
        with open(prob_file, 'r') as f:
            data = json.load(f)
            data['variation'] = int(var_number)
            data['isOriginal'] = False
            combined_data.append(data)

            if data['type'] == 'constant':
                constant.add(data['year'] + '_' + data['id'])
            elif data['type'] == 'variable':
                variable.add(data['year'] + '_' + data['id'])
            else:
                sig.add(data['year'] + '_' + data['id'])

for og_prob in original_dir.iterdir():
    with open(og_prob, 'r') as f:
        data = json.load(f)
        data['variation'] = 0 # We define the 0th variation to be the originals.
        data['isOriginal'] = True
        if data['year'] + '_' + data['id'] in constant:
            data['type'] = 'constant'
        elif data['year'] + '_' + data['id'] in variable:
            data['type'] = 'variable'
        else:
            data['type'] = 'significant'
        combined_data.append(data)

def key(e):
    return int(e['year']) * 10000 + (ord(e['id'][0]) - 96) * 5000 + int(e['id'][1]) * 100 + int(e['variation']) * 10

combined_data.sort(key = key) # Sort by year and variation number.
# Write the combined data to the output file
with open(output_path, 'w') as output_f:
    json.dump(combined_data, output_f, indent=4)

print(f"All JSON files combined into {output_path}")