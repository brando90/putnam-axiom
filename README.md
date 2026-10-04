# Putnam-AXIOM: A Functional and Static Benchmark for Measuring Higher Level Mathematical Reasoning

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/README.md>

**TLDR:** This is the canonical home for Putnam-AXIOM's datasets, evaluation code, harness integration and experiments. Use the `main` branch here and the local checkout `~/putnam-axiom`.

## Start here

```bash
git clone https://github.com/brando90/putnam-axiom.git
cd putnam-axiom
```

If you already have `~/putnam-axiom`, use that checkout instead of cloning again. No recursive clone or harness submodule is required.

| Home | Contents |
|---|---|
| [`data/`](data/) | Released original and variation datasets; existing contents preserved. |
| [`src/`](src/) | Shared evaluation, training and variation-generation code. |
| [`src/lm_evaluation_harness/`](src/lm_evaluation_harness/) | Project-owned EleutherAI Language Model Evaluation Harness task files and historical integration snapshots. |
| [`experiments/`](experiments/) | Experiment index, future numbered experiments, and preserved historical experiment work. |
| [`paper_latex_and_notes/`](paper_latex_and_notes/) | Project notes, including the [consolidation record](paper_latex_and_notes/consolidation/README.md). |

Read [`AGENTS.md`](AGENTS.md) or [`CLAUDE.md`](CLAUDE.md) before agent work. New experiments follow [`experiments/README.md`](experiments/README.md): one descriptive numbered folder owns its code, inputs, prompts and results.

The historical harness fork is archived and points here. Its Putnam contribution was merged upstream in [EleutherAI pull request #3998](https://github.com/EleutherAI/lm-evaluation-harness/pull/3998). The [integration guide](src/lm_evaluation_harness/README.md) explains how to load this repository's task definitions using an installed harness.

The launch page remains an unmerged draft in [pull request #5](https://github.com/brando90/putnam-axiom/pull/5). Its source branch is preserved; the consolidation does not publish the website.

## Verify the consolidation

```bash
python3 src/scripts/verify_consolidation.py
```

This offline check verifies imported-file hashes, preservation of the existing datasets and evaluation source, task configuration references, and the absence of tracked submodules. It does not run models or evaluate benchmark correctness. The fixed migration manifest records the 10-04-2026 baseline; intentional future changes must update its checks and provenance explicitly.

## Basic Usage and Evaluation Procedure
To perform an evaluation on Putnam-AXIOM, run `python src/eval.py`, including the appropriate arguments.

* `--data_dir` is the path to the dataset. This should either be `data/Putnam_AXIOM_Original_v3.json` to evaluate Putnam-AXIOM Original or use the appropriate variations file from the variations directories.
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

`python src/eval.py --data_dir data/Putnam_AXIOM_Original_v3.json --model_name meta-llama/Meta-Llama-3-8B --output_dir DIRECTORY_PATH`
