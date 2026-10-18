# Experiment 01: Supervised Fine-Tuning (SFT) Logic Contamination and Teacher-Forced Accuracy (TFA) on Putnam-AXIOM Original vs. Functional Variations

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/README.md>

**TLDR-start:** Evaluates whether direct supervised fine-tuning (SFT) contamination on the 100 Putnam-AXIOM Original problems (`data/Putnam-AXIOM_Variations_v4/original.json`) transfers to the 500 paired Functional Variations (`test.json`, "logic contamination") versus 100 held-out Unseen Original control problems, and tests whether reference-based Teacher-Forced Accuracy (TFA) tracks free-generation Boxed-Answer Exact Match (EM) across 20 published baselines, 8 live open-weight models, and 15 SFT checkpoints.

## Hypothesis

1. **H1 (Functional Variation Robustness to Direct Training-Set / Logic Contamination):**
   When an open-weight language model is directly supervised-fine-tuned (SFT) on the $N=100$ Original Putnam-AXIOM problems that generate functional variations (`data/Putnam-AXIOM_Variations_v4/original.json`), its Boxed-Answer Exact Match ($\text{EM}$) and Teacher-Forced Accuracy ($\text{TFA}_{\text{sol}}$, $\text{TFA}_{\text{box}}$) on the contaminated `orig_contaminated` ($N=100$) split will increase sharply with training epochs ($+30$ to $+80$ percentage points via surface/solution memorization), whereas its accuracy on the paired `func_variations` ($N=100$ Variation-1 and $N=500$ all-5-variations in `data/Putnam-AXIOM_Variations_v4/test.json`) will change by very little ($|\Delta \text{EM}| \le 5\text{ percentage points}$) and remain statistically indistinguishable from general domain/format adaptation on held-out `orig_unseen_control` ($N=100$ disjoint original problems from `data/Putnam_AXIOM_Original_v3.json`).
2. **H2 (Teacher-Forced Accuracy [TFA] as a Reference-Based Proxy for Mathematical Reasoning and Contamination Detection):**
   Reference-based Solution Teacher-Forced Accuracy ($\text{TFA}_{\text{sol}}$, mean next-token argmax accuracy over gold step-by-step solution tokens) and Boxed-Answer Token Teacher-Forced Accuracy ($\text{TFA}_{\text{box}}$, mean next-token argmax accuracy over tokens inside `\boxed{...}`) positively correlate with free-generation Boxed-Answer Exact Match ($\text{EM}$) across open-weight models ($r \ge 0.60$, $\rho \ge 0.60$) and sensitively separate memorized `orig_contaminated` solutions from unmemorized `func_variations` and `orig_unseen_control` problems across SFT checkpoints without requiring symbolic LaTeX answer parsing.

## Decision Criterion

- **For H1 (Logic Contamination):**
  - *Memorization gap ($\Delta_{\text{mem}}$)*: Paired gain on contaminated originals minus paired gain on functional variations at Epoch 10, $\Delta_{\text{mem}} = (\text{Acc}_{\text{orig, ep10}} - \text{Acc}_{\text{orig, ep0}}) - (\text{Acc}_{\text{var, ep10}} - \text{Acc}_{\text{var, ep0}})$. H1 is supported if $\Delta_{\text{mem}} \ge +25.0$ percentage points with $p < 0.01$ (paired cluster bootstrap over the $N=100$ problem families) AND net logic contamination $\Delta_{\text{logic}} = (\text{Acc}_{\text{var, ep10}} - \text{Acc}_{\text{var, ep0}}) - (\text{Acc}_{\text{unseen, ep10}} - \text{Acc}_{\text{unseen, ep0}})$ is small ($|\Delta_{\text{logic}}| < 5.0$ percentage points or $p \ge 0.05$).
- **For H2 (TFA Calibration & Contamination Sensitivity):**
  - Across the 8 evaluated open-weight models at baseline (Epoch 0) and across SFT checkpoints, report Pearson $r$, Spearman $\rho$, Kendall $\tau$, and mean bias $\mathbb{E}[\text{TFA} - \text{EM}]$ with 10,000-draw bootstrap 95% confidence intervals (resampling problems/clusters or models). H2 is supported if $\text{TFA}_{\text{sol}}$ and $\text{TFA}_{\text{box}}$ exhibit positive rank correlation with $\text{EM}$ and show a statistically significant contamination divergence $\Delta_{\text{mem}}(\text{TFA}_{\text{sol}}) > +30.0$ percentage points ($p < 0.0001$) between `orig_contaminated` and `func_variations`.

## Dependencies

- **Canonical Repository:** `~/putnam-axiom` (`brando90/putnam-axiom`)
- **Shared Benchmark Datasets (committed in repo):**
  - [`data/Putnam-AXIOM_Variations_v4/original.json`](../../data/Putnam-AXIOM_Variations_v4/original.json) ($N=100$ variation-paired original problems; SHA-256 `71f5cb5e29d1d8c92e8400ac1a31b64c52a2db486cc7bb2fe92dcb4c77805ef1`)
  - [`data/Putnam-AXIOM_Variations_v4/test.json`](../../data/Putnam-AXIOM_Variations_v4/test.json) ($N=500$ functional variations, 5 per original problem; SHA-256 `76c46b3626a8e8c4f09ad3431dc3add7a1e4a4a467064226ebfc0fe957dae96f`)
  - [`data/Putnam_AXIOM_Original_v3.json`](../../data/Putnam_AXIOM_Original_v3.json) ($N=522$ full original Putnam problems; SHA-256 `b763cba941864a53557d603634dd519f2f9edb9eda342fe9cf4826b67da3d00b`)
- **Existing Baseline Evaluation Artifacts (committed in repo, Phase 1 audit):**
  - [`src/data_visualization/interval_gen.py`](../../src/data_visualization/interval_gen.py) (20-model Original vs. Variation benchmark summary)
  - [`src/model_output/baseline/finetuning_output_original.json`](../../src/model_output/baseline/finetuning_output_original.json) & [`finetuning_output_variation.json`](../../src/model_output/baseline/finetuning_output_variation.json) ($N=100$ paired `DeepSeek-R1-Distill-Qwen-14B` outputs)
  - [`src/model_evals/test/`](../../src/model_evals/test/) (12 models $\times$ 5 stochastic runs on $N=5{,}000$ Hendrycks MATH problems)
- **Compute Environment (Phase 2 & Phase 3 live GPU runs):**
  - Stanford Network Analysis Project (SNAP) node `skampere1.stanford.edu` (`NVIDIA A100-SXM4-80GB` GPUs, `/lfs/skampere1/0/brando9/vllm_env/bin/python`, `torch 2.11.0+cu130`, `transformers 5.9.0`, local HuggingFace cache `/lfs/skampere1/0/brando9/.cache/huggingface/hub/`).

## Method

1. **Phase 1 (`expt_v1/analyze_phase1_existing_data.py`):** Zero-compute statistical audit of all existing committed evaluation artifacts in `putnam-axiom`:
   - 20-model paired Original vs. Functional Variation gap analysis (with 10,000-draw bootstrap 95% CIs, paired permutation/Wilcoxon/t-test p-values, Pearson $r$, Spearman $\rho$, Kendall $\tau$, and mean bias).
   - 100-problem paired per-item analysis of `DeepSeek-R1-Distill-Qwen-14B` (`finetuning_output_original.json` vs. `finetuning_output_variation.json`), including exact McNemar test, $2\times 2$ concordance matrix, topic-level stratification across Putnam mathematical domains, and solution-length effects.
   - 12-model $\times$ 5-run multi-seed variance and reliability analysis on `src/model_evals/test/`.
2. **Phase 2 (`expt_v1/run_snap_tfa_and_sft_contamination.py` — Baseline Multi-Model TFA & EM Calibration):**
   - Evaluates 8 open-weight models cached on `skampere1` (`google/gemma-2b`, `google/gemma-2b-it`, `Qwen/Qwen3-1.7B-Base`, `Qwen/Qwen3-1.7B`, `Qwen/Qwen3-4B`, `deepseek-ai/deepseek-math-7b-base`, `deepseek-ai/deepseek-math-7b-instruct`, `deepseek-ai/deepseek-math-7b-rl`) on:
     - `orig_contaminated` ($N=100$ from `original.json`),
     - `func_variations_v1` ($N=100$ matched Variation-1 from `test.json`) and `func_variations_all5` ($N=500$ all 5 variations from `test.json`),
     - `orig_unseen_control` ($N=100$ deterministic seed-42 sample from the 422 non-overlapping problems in `Putnam_AXIOM_Original_v3.json`).
   - Computes per-problem Boxed-Answer Exact Match ($\text{EM}$), Solution Teacher-Forced Accuracy ($\text{TFA}_{\text{sol}}$), Boxed-Answer Token Teacher-Forced Accuracy ($\text{TFA}_{\text{box}}$), and Solution Teacher-Forced Cross-Entropy ($\text{TFCE}_{\text{sol}}$).
3. **Phase 3 (`expt_v1/run_snap_tfa_and_sft_contamination.py` — Controlled SFT Logic-Contamination Trajectory):**
   - Fine-tunes 3 distinct models (`google/gemma-2b-it`, `Qwen/Qwen3-1.7B`, and `deepseek-ai/deepseek-math-7b-instruct`) directly on the $N=100$ `orig_contaminated` problems (`original.json`) for 10 epochs with proper prompt-masked causal language modeling loss and explicit EOS supervision.
   - Evaluates checkpoints at $\text{Epoch} \in \{0, 1, 3, 5, 10\}$ on `orig_contaminated` ($N=100$), `func_variations_v1` ($N=100$ paired) / `func_variations_all5` ($N=500$), and `orig_unseen_control` ($N=100$) across all 4 metrics ($\text{EM}$, $\text{TFA}_{\text{sol}}$, $\text{TFA}_{\text{box}}$, $\text{TFCE}_{\text{sol}}$).

## Structure

- [`PROTOCOL.md`](PROTOCOL.md) — Frozen experimental protocol, input manifest, model identifiers, prompt templates, scoring rules, and statistical plan.
- [`results.md`](results.md) — Live and final executive summary of experimental results with links to versioned reports.
- [`CKPT_sft_logic_contamination_and_tfa.md`](CKPT_sft_logic_contamination_and_tfa.md) — Durable execution checkpoint tracking Phase 1, Phase 2, and Phase 3 progress.
- [`expt_v1/cc.md`](expt_v1/cc.md) — Exact reproducible command script for Phase 1, Phase 2, and Phase 3.
- [`expt_v1/analyze_phase1_existing_data.py`](expt_v1/analyze_phase1_existing_data.py) — Deterministic analysis script for Phase 1 existing datasets.
- [`expt_v1/run_snap_tfa_and_sft_contamination.py`](expt_v1/run_snap_tfa_and_sft_contamination.py) — GPU evaluation and SFT contamination runner for Phase 2 and Phase 3 on SNAP.
- [`expt_v1/analyze_phase2_phase3_stats.py`](expt_v1/analyze_phase2_phase3_stats.py) — Bootstrap confidence interval, hypothesis test, and correlation aggregator for Phase 2 and Phase 3 per-item outputs.
- [`expt_v1/results/`](expt_v1/results/) — Committed per-item CSV and JSON summary tables.
- [`expt_v1/RESULTS_sft_logic_contamination_and_tfa_v1.md`](expt_v1/RESULTS_sft_logic_contamination_and_tfa_v1.md) — Complete versioned scientific report.

## Status

In progress (launched 10-16-2026; Phase 1 completed locally, Phase 2 and Phase 3 running on `skampere1.stanford.edu`).

**TLDR-end:** Defines Experiment 01 testing SFT logic contamination and Teacher-Forced Accuracy (TFA) vs. Exact Match (EM) on Putnam-AXIOM Original ($N=100$), Functional Variations ($N=500$), and Unseen Original Controls ($N=100$) under `experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/`.
