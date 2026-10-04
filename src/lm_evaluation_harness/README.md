# Putnam-Axiom integration with the Language Model Evaluation Harness

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/src/lm_evaluation_harness/README.md>

**TLDR:** Maintain Putnam-specific task definitions here and install EleutherAI's harness as a dependency. A second project clone or submodule is unnecessary; imported configurations and scoring code are preserved byte for byte.

## Source and status

| Directory | Source revision | Role |
|---|---|---|
| [`tasks/putnam_axiom/`](tasks/putnam_axiom/) | `559bd28095842311d62c9ccdf85687f281d80de4` | Four task definitions plus helper code and original documentation from the final submission branch. |
| [`tasks/putnam_axiom_zipfit/`](tasks/putnam_axiom_zipfit/) | `5a2fbe7e4f7e1beb6ffaffaac9d1d1ebea6a752f` | Four separately named task configurations from the historical `zip_fit` branch. This label is preserved from the source; the configuration files identify its dataset and splits. |
| [`archive/preview-main/`](archive/preview-main/) | `6af252af7849dcdf2d350c9011de05555ca7e2e4` | Earlier preview documentation, runner and task implementations, including the 53-problem configuration. Historical evidence; excluded from the active include path. |

All source revisions belong to [the historical fork](https://github.com/brando90/lm-evaluation-harness). Its old `putnam-axiom-preview-lm-evaluation-harness` address redirects there. The original [submission #2946](https://github.com/EleutherAI/lm-evaluation-harness/pull/2946) was superseded by [#3998](https://github.com/EleutherAI/lm-evaluation-harness/pull/3998), merged on 08-14-2026. Upstream may subsequently evolve; these imported bytes are historical configurations, not a claim of identity with current upstream.

[`LICENSE.md`](LICENSE.md) preserves the harness's license. Exact source paths and SHA-256 (Secure Hash Algorithm, 256-bit) fingerprints are in the [consolidation manifest](../../paper_latex_and_notes/consolidation/manifest.json).

## Use from this repository

Install the upstream harness in the environment for an authorized experiment, following its [installation instructions](https://github.com/EleutherAI/lm-evaluation-harness#install). Record the exact installed version or commit in that experiment. Dataset downloads and model execution are separate from installation and offline configuration validation.

The harness supports external task directories. From `~/putnam-axiom`, pass:

```text
--include_path src/lm_evaluation_harness/tasks
```

Use `putnam_axiom_original`, `putnam_axiom_variations`, or `putnam_axiom_variations_org` as appropriate; `putnam_axiom` is the original-task alias. Historical split configurations are `putnam_axiom_zipfit_train`, `putnam_axiom_zipfit_val`, and `putnam_axiom_zipfit_test`; their base `putnam_axiom_zipfit` supplies shared configuration.

For Python callers, construct `lm_eval.tasks.TaskManager(include_path="src/lm_evaluation_harness/tasks")` and pass that manager to the evaluator. Resolve this path against the repository root when running from an experiment directory. See the [official task guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/new_task_guide.md).

Do not include `archive/` in task discovery: it contains earlier definitions with overlapping names. Do not rewrite dataset splits, prompts, reference answers or scoring during organizational work. An authorized experiment must first follow the [experiment conventions](../../experiments/README.md) and global model-execution rules.
