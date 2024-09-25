import json


file_path = 'putnam-axiom/data/Putnam_AXIOM_Original.json'
with open(file_path, 'r') as file:
    data = json.load(file)

output_file_path = 'putnam-axiom/data/Putnam_AXIOM_hard.json'
new_data = []

for i in data:
    if i['answer_type'] != 'binary':
        new_data.append(i)

print(len(new_data))

with open(output_file_path, 'w') as file:
    json.dump(new_data, file, indent = 4)