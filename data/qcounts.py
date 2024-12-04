import json

with open('putnam-axiom/data/Putnam_AXIOM_Original.json', 'r') as f:
    d = json.load(f)


tcounts = {}
atypes = {
    'modified' : 0,
    'boxed' : 0
}
difficulties = {
    'low' : 0, # 1 or 2
    'medium' : 0, # 3 or 4
    'hard' : 0 # 5 or 6
}
for i in range(len(d)):
    id = int(d[i]['id'][-1:])
    types = d[i]['type']
    for t in types:
        if t in tcounts:
            tcounts[t] += 1
        else:
            tcounts[t] = 1
    if id == 1 or id == 2:
        difficulties['low'] += 1
    elif id == 3 or id == 4:
        difficulties['medium'] += 1
    elif id == 5 or id == 6:
        difficulties['hard'] += 1

    if 'modified boxing' in d[i]['source']:
        atypes['modified'] += 1
    else:
        atypes['boxed'] += 1

print(tcounts)
print(difficulties)
print(atypes)