from pathlib import Path
import importlib
import argparse
import json
import random
import numpy as np

from variations.utils import PUTNAM_VARIATIONS
ORIGINAL_DATASET = {}

def load_generators(original_data_dir: Path):
    years = set()

    with open(original_data_dir, 'r') as f:
        data = json.load(f)
        
    for i in range(len(data)):
        
        year_id = data[i]['id']
        year = year_id.split('_')[0]

        ORIGINAL_DATASET[year_id] = data[i]
        if year in years:
            continue
        years.add(year)
        try:
            importlib.import_module(f'variations.putnam{year}')
        except Exception as e:
            if isinstance(e, ImportError):
                print(f'ImportError: No module putnam{year} found.\n{e}')
            else:
                print(f'Error while importing putnam{year}: {e}.\n\nSkipping...')
            continue

        print(f'Loaded generators for Putnam {year}.')


def generate_variations(year, id_, func, save_dir, orig_dir, num_variations=5):
    try:
        original = ORIGINAL_DATASET[year + '_' + id_]
    except Exception as e:
        return None, None
    save_dir.mkdir(parents=True, exist_ok=True)
    problems = []

    try:
        for i in range(num_variations):

            # variation_save_dir = save_dir / f'variation_{i + 1}'
            # variation_save_dir.mkdir(parents=True, exist_ok=True)

            variation = func.sample()

            problem = {
                'year': year,
                'id': id_,
                'problem': variation['problem'],
                'solution': variation['solution'],
                'type': variation['type'],
                'answer_type': original['answer_type'],
                'variation': str(i + 1)
            }
            problems.append(problem)
        
        original_problem = {
            'year': year,
            'id' : id_,
            'problem': original['problem'],
            'solution': original['solution'],
            'answer_type': original['answer_type']
        }
    
    except Exception as e:
        print(f'Error while generating variation for {year}_{id_}: {e}.\nSkipping...\n')
    else:
        print(f'Variations generated for {year}_{id_}.')
    
    return problems, original_problem

# def generate_originals(year, id_, func, save_dir):
#     try:
#         orig_save = save_dir / 'original'
#         orig_save.mkdir(parents=True, exist_ok=True)

def generate(args):
    random.seed(args.seed)
    np.random.seed(args.seed)

    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    save_orig_dir = Path(args.save_orig_dir)
    save_orig_dir.mkdir(parents=True, exist_ok=True)

    print('=' * 50)
    print('Loading generators...')
    print('=' * 50)

    original_data_dir = Path(args.original_data_dir)
    load_generators(original_data_dir)

    print('=' * 50)
    print('Generating variations...')
    print('=' * 50)

    vars = []
    original = []
    
    if args.problem_keys:
        print(f'Generating variations for problems: {args.problem_keys}.\n')
        for year, ids in args.problem_keys.items():
            for id_ in ids:
                func = PUTNAM_VARIATIONS[year][id_]
                generate_variations(year, id_, func, save_dir, save_orig_dir, args.num_variations)
    else:

        totCount = 0
        print('Generating variations for all problems.\n')
        # print(PUTNAM_VARIATIONS)
        for year, problems in PUTNAM_VARIATIONS.items():
            for id_, func in problems.items():
                var = func.sample()
                problems, original_problem = generate_variations(year, id_, func, save_dir, save_orig_dir, args.num_variations)
                if not problems: continue
                totCount += 1
                vars.extend(problems)
                original.append(original_problem)
    print('TOTAL COUNT:',totCount)
    with open(f'{save_dir}/test.json', 'w') as f:
        json.dump(vars, f, indent = 4)
    
    with open(f'{save_dir}/original.json', 'w') as f:
        json.dump(original, f, indent = 4)

    print('=' * 50)
    print(f'Variations generated and saved in {save_dir}.')
    print('=' * 50)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate variations of problems.')
    parser.add_argument('--num_variations', type=int, default=5, help='Number of variations to generate.')

    parser.add_argument('--save_dir', type=str, default='putnam-axiom/data/Putnam-AXIOM_Variations_v4',
                        help='Directory to save variations.')
    parser.add_argument('--save_orig_dir', type=str, default='putnam-axiom/data/Putnam-AXIOM_Variations_v4',
                        help='Directory to save original version of variations.')
    parser.add_argument('--original_data_dir', type=str, default='putnam-axiom/data/Putnam_AXIOM_Original_v3.json',
                        help='Original data directory. i.e. directory containing original Putnam problems.')

    parser.add_argument('--seed', type=int, default=42, help='Random seed.')

    parser.add_argument('--problem_keys', type=str, default='{}',
                        help='Keys of problems to generate variations for. Format: \'{"year": ["id1", "id2", ...], '
                             '...}\'. If not provided, all problems will be generated.')

    args = parser.parse_args()
    args.problem_keys = json.loads(args.problem_keys.replace("'", "\""))
    generate(args)
    # print(PUTNAM_VARIATIONS)
    # with open('putnam-axiom/data/Putnam_AXIOM_Original.json', 'r') as file:
    #     data = json.load(file)
    #     print(len(data))
