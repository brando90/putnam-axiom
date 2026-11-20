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

## Citation

If you find Putnam-AXIOM useful in your research, please cite our ICML 2025 paper ([PMLR](https://proceedings.mlr.press/v267/gulati25a.html) · [arXiv](https://arxiv.org/abs/2508.08292) · [OpenReview](https://openreview.net/forum?id=kqj2Cn3Sxr)):

```bibtex
@inproceedings{gulati2025putnamaxiom,
  title     = {Putnam-{AXIOM}: A Functional \& Static Benchmark for Measuring Higher Level Mathematical Reasoning in {LLM}s},
  author    = {Aryan Gulati and Brando Miranda and Eric Chen and Emily Xia and Kai Fronsdal and Bruno de Moraes Dumont and Sanmi Koyejo},
  booktitle = {Proceedings of the 42nd International Conference on Machine Learning},
  pages     = {20723--20747},
  year      = {2025},
  volume    = {267},
  series    = {Proceedings of Machine Learning Research},
  publisher = {PMLR},
  url       = {https://proceedings.mlr.press/v267/gulati25a.html}
}
```

## Known inconsistencies and fixes (Nov 20 2026)

Recomputed on Nov 20 2026 from the published Table 2 counts and, for the 2026 runs, from the per-question files in `experiments/02_frontier_models_original_vs_variations_nov2026/data/scored/`. The raw per-question logs of the 2024-25 paper runs (o1-preview, GPT-4o, Claude-3.5 Sonnet and the open models) are not in this repository (any branch, any commit), so no paired test is possible for them. They are also not on Brando's Drive, and a file-name search of skampere1, skampere2 and /dfs on Nov 20 2026 (names with o1-preview, LM_outputs, Binary_Analysis) found none. Open items that the repo cannot settle are listed in [`future-work.md`](future-work.md).

| Old figure (paper v2) | Corrected figure | Source file and subset | Still open |
|---|---|---|---|
| Abstract: o1-preview "drops by 19.6% (46.8% relative decrease)" on the paired Variations | 8 points: 51/100 original vs 43/100 variation, i.e. 15.7% relative to the original (18.6% relative to the variation). The plot inputs give 50.61 vs 43.20 (7.41 points, 14.6% relative) | Paper Table 2 (100 matched originals vs the variations, mean of 5 snapshots); `src/data_visualization/interval_gen.py` (Figure 3 inputs). 19.6 / 41.95 = 46.7%, so the 46.8% divides by the 522-problem accuracy (219/522, Table 1) | Where 19.6 comes from. The repo's 100 originals and 500 variations contain no binary answers, so the Appendix A.4 non-binary subset cannot produce it, and a 522-vs-variation drop would be negative for GPT-4o (19.35% vs 22/100). Needs the raw o1-preview logs |
| Sec 4.1: steepest drops "37.5%, 36%, 17%" (R1-Distill-Qwen-32B, GPT-4o, o1-preview) | These are the drop divided by the variation score: 9/24 = 37.5%, 8/22 = 36.4%, 7.41/43.2 = 17.1%. Relative to the original they are 27.3%, 26.7%, 14.6% (Fig 3 inputs) or 15.7% (Table 2 counts) | Paper Table 2 and `interval_gen.py` | The paper should state the denominator; the Introduction's "20-30% relative" uses the original as denominator |
| Abstract and Table 2: variation accuracy is lower for all or nearly all models | 18 of 21 Table 2 rows are lower, 2 are equal (Mistral-7B-v0.3-Base 7 vs 7, Qwen2-Math-7B-Base 9 vs 9), 1 is higher (Llama-3.1-8B 6 vs 7). Claude-3.5 Sonnet 28 vs 27 is a 1-point drop, not distinguishable from zero. Counts are out of 100 on both sides | Paper Table 2 (100 pairs). Without per-question pairing, the exact McNemar p-value is only bounded: under the most favourable pairing it is below 0.05 for 8 rows, under the least favourable for only 2 (Gemma-7B-Instruct 11 vs 2, R1-Distill-Llama-8B 19 vs 7). The conservative unpaired Newcombe 95% interval excludes 0 for 3 rows (those 2 plus R1-Distill-Qwen-7B 23 vs 12) | Per-question pairing for the paper runs, so the real McNemar p-values. The abstract's "eighteen other models" and "ten with non-overlapping intervals" do not match the 21 table rows and cannot be rechecked. The plotted intervals (half-width about 3.4 points for o1-preview) are much narrower than a binomial interval at n=100 (about 9.7 points) and their derivation is undocumented |
| Appendix A.4: binary questions are "26 of 262" originals and "8 of 60" variations | 0 binary answers in the 522 originals, the 100 matched originals and the 500 variations (answer types are only numerical and algebraic) | `data/Putnam_AXIOM_Original_v3.json`, `data/Putnam-AXIOM_Variations_v4/{original,test}.json` | The counts are stale (from the 53/60-problem version). Fig 3 and the A.4 non-binary claim cannot be reproduced without the old logs |
| Sec 3.4: "LoRA fine-tuning ... until convergence", model not named | Model: DeepSeek-R1-Distill-Qwen-7B (`src/contamination_ft.py` line 57; also the rebuttal and `ac_comment.md` in commit 5d6c29f). The script does not use LoRA (`get_peft_model` is imported on line 4 and never called; full-parameter training under DeepSpeed), sets `num_train_epochs=20` (line 92) and `learning_rate=1e-5` (line 93). The rebuttals say 5 epochs of full-parameter SFT | `src/contamination_ft.py`; paper Sec 3.4 (12% / 23% before, 33% / 80% after on 100 variations / 100 originals) | Which setting produced 33% / 80% (5 epochs or 20; full or LoRA) is not recorded in the repo |

### Frontier models in 2026 (different models and a different harness than the paper)

Per-question paired drop on the 100 matched originals vs their variations (paper grader, `experiments/02_frontier_models_original_vs_variations_nov2026`; 5 snapshots, so 500 pairs; Gemini 3.8 Flash has snapshot 1 only, 100 pairs). Interval: bootstrap over the 100 problems (10000 resamples). GPT-4o and Qwen2-Math-7B-Instruct are the paper's models, re-run in Nov 2026.

| Model | Original (100) | Variation | Paired drop, points [95% interval] |
|---|---|---|---|
| gpt-6.2-astra | 81.0 | 69.0 | 12.0 [6.4, 18.2] |
| gpt-6-astra | 82.0 | 69.4 | 12.6 [7.0, 19.0] |
| gpt-5.5 | 80.0 | 68.6 | 11.4 [5.6, 18.0] |
| claude-sonnet-5-5 | 83.0 | 71.2 | 11.8 [5.2, 18.8] |
| claude-opus-5-5 | 83.0 | 73.6 | 9.4 [3.2, 16.0] |
| gemini-3.8-flash (snapshot 1) | 87.0 | 73.0 | 14.0 [7.0, 21.0] |
| gpt-4o (2026 rerun) | 27.0 | 23.4 | 3.6 [-3.8, 11.2] |
| Qwen2-Math-7B-Instruct (2026 rerun) | 19.0 | 16.0 | 3.0 [-2.8, 9.2] |

### Which model was fine-tuned, and is there an evaluation harness?

The fine-tuned model in Sec 3.4 is DeepSeek-R1-Distill-Qwen-7B (see the table above).

Yes, an evaluation harness is used. The paper-era evaluation code runs the EleutherAI lm-evaluation-harness with this repo's task files in `src/lm_evaluation_harness/tasks/putnam_axiom/` (tasks `putnam_axiom_original`, `putnam_axiom_variations`, `putnam_axiom_variations_org`; grader in `utils.py`, `process_results` line 97, `is_equiv` line 188):

- `src/lm_harness_eval.py` lines 140-152: vLLM `LLM(...)` wrapped in a custom `MyLM`, then `lm_eval.simple_evaluate(...)` (second call at line 168).
- `src/hf_eval.py` lines 77-81, `src/lmh_evaluation.py` lines 186-198: the same pattern.
- `src/api_eval.py` lines 163 and 173, `src/claude_eval.py` lines 57 and 67: `evaluator.simple_evaluate` with an API-backed `LM` class.
- `src/deepseek_eval.py` lines 72-81 and 127: a vLLM-backed `LM` class passed to `evaluator.simple_evaluate`.
- `src/model_evals/test/*/run*.json` are lm-eval-harness outputs, but on `hendrycks_math` (the TFA correlation study), not on Putnam-AXIOM.

The one exception is `src/eval.py` (lines 12 and 40: vLLM `LLM` and `SamplingParams` called directly, no harness). The 2026 runs in `experiments/02_...` use the harness's 4-shot prompt and this repo's grader but their own driver scripts (`code/run_eval.py`), with no tools or agent.
