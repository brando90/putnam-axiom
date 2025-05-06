# Putnam-AXIOM: A Functional and Static Benchmark for Measuring Higher Level Mathematical Reasoning
This is the repository for Putnam-AXIOM: A Functional and Static Benchmark for Measuring Higher Level Mathematical Reasoning. This repository contains all of the data and evaluation code, including Putnam-AXIOM Original and Putnam-AXIOM Variations.

## Paper
The ICML 2025 paper is available on OpenReview: [https://openreview.net/forum?id=kqj2Cn3Sxr](https://openreview.net/forum?id=kqj2Cn3Sxr)

Earlier preprint: [https://openreview.net/pdf?id=YXnwlZe0yf](https://openreview.net/pdf?id=YXnwlZe0yf)

## HuggingFace Datasets
The dataset is published on HuggingFace in two repositories:

1. **Main Dataset**: [Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522](https://huggingface.co/datasets/Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522)
   - Contains the primary splits: `full_eval` (522 examples), `originals_for_generating_vars` (100 examples), `variations` (500 examples)

2. **ZIP-FIT Splits**: [zipfit/Putnam-AXIOM-for-zip-fit-splits](https://huggingface.co/datasets/zipfit/Putnam-AXIOM-for-zip-fit-splits)
   - Contains validation and test splits used for the ZIP-FIT research methodology

## Basic Usage and Evaluation Procedure
To perform an evaluation on Putnam-AXIOM, run `python putnam-axiom/src/eval.py`, including the appropriate arguments.

* `--data_dir` is the path to the dataset. This should either be `putnam-axiom/data/Putnam_AXIOM_Original_v3.json` to evaluate Putnam-AXIOM Original or use the appropriate variations file from the variations directories.
* `--prompt_name` specifies whether the prompt has to be modified for certain instruct models. The supported arguments are `general`, `mistral`, `llama`, or `gemma`. Defaults to `general`
* `--model_name` specifies which model to use. This parameter should be set to the Huggingface path of a model that is supported by VLLM. For instance, to evaluate Mistral-7B V0.1, one could set `--model_name` to `mistralai/Mistral-7B-v0.1`.
* `--output_dir` specifies the directory to which the evaluation results are outputted.
* `--temperature` sets the temperature for model generation, with `temperature = 0` being completely deterministic.
* `--top_p` specifies the percentage of the most common tokens that are taken into account for model generation.
* `--max_tokens` specifies the maximum number of tokens for the model generation. Defaults to `2048`.
* `--stop` specifies a stop sequence for the model. Defaults to `Problem:`
* `--repeat_eval` specifies the number of times to repeat the evaluation. Defaults to `5`.
* `--verbose` specifies whether to print a large volume of text output. Defaults to `True`.

For instance, to run Llama-3-8B on the original dataset, one would run

`python putnam-axiom/src/eval.py --data_dir putnam-axiom/data/Putnam_AXIOM_Original_v3.json --model_name meta-llama/Meta-Llama-3-8B --output_dir DIRECTORY_PATH`

## Repository Organization

- **data/Putnam_AXIOM_Original_v3.json** - The main dataset file with 522 problems
- **data/Putnam-AXIOM_Variations/** - Directories containing variation datasets
- **data/scripts_push_2_hf/** - Scripts for pushing data to HuggingFace
- **src/** - Evaluation code and utilities

See the README in each directory for more details.

## Generating Variation Snapshots

