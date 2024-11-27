# Putnam-AXIOM: A Functional and Static Benchmark for Measuring Higher Level Mathematical Reasoning
This is the repository for Putnam-AXIOM: A Functional and Static Benchmark for Measuring Higher Level Mathematical Reasoning. This repository contains all of the data and evaluation code, including Putnam-AXIOM Original and Putnam-AXIOM Variations.

## Basic Usage and Evaluation Procedure
To perform an evaluation on Putnam-AXIOM, run `python putnam-axiom/src/eval.py`, including the appropriate arguments. Evaluation code inspired by minerva math.

* `--data_dir` is the path to the dataset. This should either be `putnam-axiom/data/Putnam_AXIOM_Original.json` to evaluate Putnam-AXIOM Original or `putnam-axiom/data/Putnam_AXIOM_Variations.json` to evaluate Putnam-AXIOM Variations.
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

`python putnam-axiom/src/eval.py --data_dir putnam-axiom/data/Putnam_AXIOM_Original.json --model_name meta-llama/Meta-Llama-3-8B --output_dir DIRECTORY_PATH`

## Generating Variations
To generate variations, run `python putnam-axiom/src/generate_variations.py`. Change the argument tags accordingly.
* `--num_variations` specifies the number of snapshots to generate per variation. Defaults to 5.
* `--save_dir` specifies the directory to which the variations are saved.
* `--save_orig_dir` specifies the directory to which the corresponding original problems are saved.
* `--original_data_dir` specifies the location of the original problems to reference.
* `--seed` specifies the random seed.
* `--problem_keys` allows the user to specify which variations to  generate snapshots for. If left empty, will generate variations for all problems available.

# Quickstart: Run Evals on Putnam-AXIOM

## Install
```bash
conda create -n putnam_axiom python=3.11
conda activate putnam_axiom
conda activate putnam_axiom
pip install -e ~/putnam-axiom
```

## Run Evals

```bash
conda activate putnam_axiom

# Add the submodule [Optional; if not there already]
cd ~/putnam-axiom
git submodule add git@github.com:emxia18/lm-evaluation-harness.git lm-evaluation-harness
git submodule update --init --recursive
git add .gitmodules lm-evaluation-harness
git commit -m "Added lm-evaluation-harness as a submodule"

#  Install lm-harness from submodule
cd ~/putnam-axiom/lm-evaluation-harness
# Instead of the usual pip install lm_eval[vllm] lm-harness recommends, do the command bellow:
pip install -e ".[vllm]"
pip install antlr4-python3-runtime==4.11
# to check installs worked do (versions and paths should appear)
pip list | grep lm_eval
pip list | grep vllm
pip list | grep antlr4
```

## Bash Command for Eval 
TODO

## Python Eval Puntam-AXIOM
To run the evaluation on the whole 236 Putnam-AXIOM benchmark:
```bash
conda activate putnam_axiom
export CUDA_VISIBLE_DEVICES=6
export task="putnam_axiom_original"
export mode="online"
# export mode="dryrun"
python ~/putnam-axiom/src/eval_logic_contamination.py --task ${task} --mode ${mode}

```
To run the evaluation on the 265 (=53*5) functional variations benchmark:
```bash

conda activate putnam_axiom
export CUDA_VISIBLE_DEVICES=3
export task="putnam_axiom_variations"
export model_name_or_path="~/data/runs_logic_cont/run_2024_m11_d23_t21h_55m_07s"
export mode="online"
# export mode="dryrun"
python ~/putnam-axiom/src/eval_logic_contamination.py --task ${task} --mode ${mode} --model_name_or_path ${model_name_or_path}

```
To run the evaluation on the 53 original problems used to create the functional variation benchmark:
```bash

conda activate putnam_axiom
export CUDA_VISIBLE_DEVICES=2
export task="putnam_axiom_53"
export model_name_or_path="~/data/runs_logic_cont/run_2024_m11_d23_t21h_55m_07s"
export mode="online"
# export mode="dryrun"
python ~/putnam-axiom/src/eval_logic_contamination.py --task ${task} --mode ${mode} --model_name_or_path ${model_name_or_path}

```

## Python Eval MATH
```bash

conda activate putnam_axiom
export CUDA_VISIBLE_DEVICES=2
export task="minerva_math"
export model_name_or_path="/lfs/skampere1/0/brando9/data/runs_logic_cont/run_2024_m11_d23_t22h_24m_50s"
export mode="online"
# export mode="dryrun"
python ~/putnam-axiom/src/eval_logic_contamination.py --task ${task} --mode ${mode} --model_name_or_path ${model_name_or_path}

```

## Logic Contamination Train Commands: Train on Putnam-AXIOM 53 To Learn Logic then Eval on Variations

```bash
conda activate putnam_axiom

# [Optional] HF authentication
# export HF_TOKEN=$(cat ~/keys/master_hf_token.txt)
# huggingface-cli login --token "$HF_TOKEN"

# - Train on the original Putnam-AXIOM 53 Benchmark
export CUDA_VISIBLE_DEVICES=4
# export mode="dryrun"
time python ~/putnam-axiom/src/train/sft_simple.py --mode 'online' --num_train_epochs 100
```
