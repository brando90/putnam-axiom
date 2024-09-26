from pathlib import Path
import importlib
import argparse
import json
import random
import numpy as np

from utils import PUTNAM_VARIATIONS

problem_type_dict = {
    
    '2001 A6' : 'constant + variable',
    '2006 A3' : 'constant + variable',
    '2011 A1' : 'constant + variable',
    '2013 B3' : 'variable',
    '2013 B6' : 'variable',
    '2016 A1' : 'variable',
    '2016 A2' : 'variable',
    '2017 A1' : 'variable',
    '2017 A2' : 'variable',
    '2018 A3' : 'significant',
    '2021 A1' : 'variable',
    '2021 A2' : 'variable',
    '2021 A3' : 'variable',
    '2021 A6' : 'variable',
    '2021 B6' : 'constant + variable',
    '2022 A6' : 'variable',
    '2022 B3' : 'variable',
    '2023 A1' : 'constant + variable',
    '2023 A2' : 'variable',
    '2023 A3' : 'variable',
    '2023 A6' : 'variable'
}


def load_generators(original_data_dir: Path):
    for year_file in original_data_dir.iterdir():
        year = year_file.stem
        # import data_variation_gen.putnam2018
        import putnam2018
        try:
        #import data_variation_gen.putnam2023
        #import data_variation_gen.putnam2022
            importlib.import_module(f'data_variation_gen.putnam{year}')
        #try:
        #    x = 0
        except Exception as e:
            if isinstance(e, ImportError):
                print(f'ImportError: No module putnam{year} found.\n{e}')
            else:
                print(f'Error while importing putnam{year}: {e}.\n\nSkipping...')
            continue

        print(f'Loaded generators for Putnam {year}.')


def generate_variations(year, id_, func, save_dir, num_variations=5):
    try:
        for i in range(num_variations):
            variation_save_dir = save_dir / f'variation_{i + 1}'
            variation_save_dir.mkdir(parents=True, exist_ok=True)

            if id_ == "A1" and year == "2023":
                print(func)
                # print(func.sample())
                # print(func.generators)
                # print(func.sample)

            variation = func.sample()

            problem = {
                'year': year,
                'id': id_,
                'problem': variation['problem'],
                'solution': variation['solution'],
                'problem_type': problem_type_dict[year + id_]
            }

            with open(variation_save_dir / f'{year}_{id_}.json', 'w') as f:
                json.dump(problem, f, indent=4)
    except Exception as e:
        print(f'Error while generating variation for {year}_{id_}: {e}.\nSkipping...\n')
    else:
        print(f'Variations generated for {year}_{id_}.')


def generate(args):
    random.seed(args.seed)
    np.random.seed(args.seed)

    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    print('=' * 50)
    print('Loading generators...')
    print('=' * 50)

    original_data_dir = Path(args.original_data_dir)
    load_generators(original_data_dir)

    print('=' * 50)
    print('Generating variations...')
    print('=' * 50)

    if args.problem_keys:
        print(f'Generating variations for problems: {args.problem_keys}.\n')
        for year, ids in args.problem_keys.items():
            for id_ in ids:
                func = PUTNAM_VARIATIONS[year][id_]
                generate_variations(year, id_, func, save_dir, args.num_variations)
                print('Generated')
    else:
        print('Generating variations for all problems.\n')
        for year, problems in PUTNAM_VARIATIONS.items():
            for id_, func in problems.items():
                generate_variations(year, id_, func, save_dir, args.num_variations)

    print('=' * 50)
    print(f'Variations generated and saved in {save_dir}.')
    print('=' * 50)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate variations of problems.')
    parser.add_argument('--num_variations', type=int, default=5, help='Number of variations to generate.')

    parser.add_argument('--save_dir', type=str, default='~/putnam-axiom/data/variation_individual',
                        help='Directory to save variations.')
    parser.add_argument('--original_data_dir', type=str, default='~/putnam-axiom/data',
                        help='Original data directory. i.e. directory containing original Putnam problems.')

    parser.add_argument('--seed', type=int, default=42, help='Random seed.')

    parser.add_argument('--problem_keys', type=str, default='{}',
                        help='Keys of problems to generate variations for. Format: \'{"year": ["id1", "id2", ...], '
                             '...}\'. If not provided, all problems will be generated.')

    args = parser.parse_args()

    
    args.problem_keys = json.loads(args.problem_keys.replace("'", "\""))

    generate(args)
