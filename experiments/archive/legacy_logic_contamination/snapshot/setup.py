"""
For full details to push to pypi see
```
~/ultimate-utils/tutorials_for_myself/pushing_to_pypi/README.md
```
refs:
    - setup tools: https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#using-find-or-find-packages
    - https://stackoverflow.com/questions/70295885/how-does-one-install-pytorch-and-related-tools-from-within-the-setup-py-install
"""
from setuptools import setup
from setuptools import find_packages
import os

# import pathlib

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='putnam-axiom',  # project name
    version='0.1.0',
    description="Ultimate Eval Benchmark for the Prestigious Putnam Competitions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/brando90/putnam-math',
    author='Brando Miranda',
    author_email='brandojazz@gmail.com',
    python_requires='>=3.10.0',
    license='Apache-2.0',

    # currently
    package_dir={'': 'src'},
    packages=find_packages('src'),  # imports all modules/folders with  __init__.py & python files

    # for pytorch see doc string at the top of file
    install_requires=[
        'dill',
        'networkx>=2.5',
        'scipy',
        'scikit-learn',
        'lark-parser',
        'tensorboard',
        'pandas',
        'progressbar2',
        'requests',
        'aiohttp',
        'numpy',
        'plotly',
        'wandb',
        'matplotlib',
        'fire',
        'Levenshtein',
        # 'statsmodels'
        # 'statsmodels==0.12.2'
        # 'statsmodels==0.13.5'
        # - later check why we are not installing it...
        'seaborn',
        # 'nltk'
        'wandb',
        'twine',
        'nvidia-htop',

        'torch',
        'torchvision',
        'torchaudio',

        # 'fairseq',

        'trl',
        'transformers', 
        'accelerate',
        'peft',

        'datasets',
        'bitsandbytes',
        'einops',

        # 'vllm'
    ]
)

