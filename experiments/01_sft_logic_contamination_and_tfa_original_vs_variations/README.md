# Experiment 01: Supervised Fine-Tuning (SFT) Logic Contamination and Teacher-Forced Accuracy (TFA) on Putnam-AXIOM Original vs. Functional Variations

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/README.md>

**TLDR:** Evaluates whether direct supervised fine-tuning (SFT) contamination on the 100 Putnam-AXIOM Original problems (`data/Putnam-AXIOM_Variations_v4/original.json`) transfers to the 500 paired Functional Variations (`test.json`, "logic contamination") versus 100 held-out Unseen Original control problems, and tests whether reference-based Teacher-Forced Accuracy (TFA) tracks free-generation Boxed-Answer Exact Match (EM) across 20 published baselines, 10 live open-weight models (`5` families), and 3 complete 10-epoch SFT trajectories (15 checkpoints).

## Hypothesis

1. **H1 (Functional Variation Robustness to Direct Training-Set / Logic Contamination):**
   When an open-weight language model is directly supervised-fine-tuned (SFT) on the $N=100$ Original Putnam-AXIOM problems that generate functional variations (`data/Putnam-AXIOM_Variations_v4/original.json`), its Boxed-Answer Exact Match ($\text{EM}$) and Teacher-Forced Accuracy ($\text{TFA}_{\text{sol}}$, $\text{TFA}_{\text{box}}$) on the contaminated `orig_contaminated` ($N=100$) split will increase sharply with training epochs ($+30$ to $+80$ percentage points via surface/solution memorization), whereas its accuracy on the paired `func_variations` ($N=100$ Variation-1 and $N=500$ all-5-variations in `data/Putnam-AXIOM_Variations_v4/test.json`) will change by very little ($|\Delta \text{EM}| \le 5\text{ percentage points}$) and remain statistically indistinguishable from general domain/format adaptation on held-out `orig_unseen_control` ($N=100$ disjoint original problems from `data/Putnam_AXIOM_Original_v3.json`).
   *(Empirically, the partial surface-memorization protection prediction $\Delta_{\text{mem}} > 0$ held, whereas the strict zero-transfer null $|\Delta_{\text{logic}}| < 5\text{ percentage points}$ was refuted across SFT checkpoints: reasoning-path contamination transfers substantially onto unseen variations and held-out controls.)*
2. **H2 (Teacher-Forced Accuracy [TFA] as a Reference-Based Proxy for Mathematical Reasoning and Contamination Detection):**
   Reference-based Solution Teacher-Forced Accuracy ($\text{TFA}_{\text{sol}}$, mean next-token argmax accuracy over gold step-by-step solution tokens) and Boxed-Answer Token Teacher-Forced Accuracy ($\text{TFA}_{\text{box}}$, mean next-token argmax accuracy over tokens inside `\boxed{...}`) positively correlate with free-generation Boxed-Answer Exact Match ($\text{EM}$) across open-weight models ($r \ge 0.60$, $\rho \ge 0.60$) and sensitively separate memorized `orig_contaminated` solutions from unmemorized `func_variations` and `orig_unseen_control` problems across SFT checkpoints without requiring symbolic LaTeX answer parsing.

## Decision Criterion

- **For H1 (Logic Contamination):**
  - *Memorization gap ($\Delta_{\text{mem}}$)*: Paired gain on contaminated originals minus paired gain on functional variations at Epoch 10, $\Delta_{\text{mem}} = (\text{Acc}_{\text{orig, ep10}} - \text{Acc}_{\text{orig, ep0}}) - (\text{Acc}_{\text{var, ep10}} - \text{Acc}_{\text{var, ep0}})$. H1 is supported if $\Delta_{\text{mem}} \ge +25.0$ percentage points with $p < 0.01$ (10,000-draw Monte Carlo paired bootstrap/permutation over the $N=100$ problem families) AND net logic contamination $\Delta_{\text{logic}} = (\text{Acc}_{\text{var, ep10}} - \text{Acc}_{\text{var, ep0}}) - (\text{Acc}_{\text{unseen, ep10}} - \text{Acc}_{\text{unseen, ep0}})$ is small ($|\Delta_{\text{logic}}| < 5.0$ percentage points or $p \ge 0.05$).
- **For H2 (TFA Calibration & Contamination Sensitivity):**
  - Across the 10 evaluated open-weight models at baseline (Epoch 0) and across SFT checkpoints, report Pearson $r$, Spearman $\rho$, Kendall $\tau$, and mean bias $\mathbb{E}[\text{TFA} - \text{EM}]$ with 10,000-draw bootstrap 95% confidence intervals (resampling problems/clusters or models). H2 is supported if $\text{TFA}_{\text{sol}}$ and $\text{TFA}_{\text{box}}$ exhibit positive rank correlation with $\text{EM}$ and show a statistically significant contamination divergence $\Delta_{\text{mem}}(\text{TFA}_{\text{sol}}) > +30.0$ percentage points ($p < 0.0001$ on exact / Monte Carlo paired tests) between `orig_contaminated` and `func_variations`.

## Dependencies

- **Canonical Repository:** `~/putnam-axiom` (`brando90/putnam-axiom`)
- **Live Downstream Paper Dependency (keeps concluded experiment active under `experiments/README.md` policy):** [`paper_latex_and_notes/`](../../paper_latex_and_notes/) (SFT logic contamination & TFA findings are being integrated into the manuscript rather than archived prematurely).
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

## Method & Delivered Implementation vs. Locked Protocol

1. **Phase 1 (`expt_v1/analyze_phase1_existing_data.py`):** Zero-compute statistical audit of all existing committed evaluation artifacts in `putnam-axiom` (20-model Original vs. Variation benchmark gap, 100-problem paired `DeepSeek-R1-Distill-Qwen-14B` concordance & domain breakdown, and 12-model $\times$ 5-run MATH multi-seed variance).
2. **Phase 2 (`expt_v1/run_snap_tfa_and_sft_contamination.py` — Baseline Multi-Model TFA & EM Calibration):**
   - Evaluates **10 open-weight models across 5 model families** cached on `skampere1`: `google/gemma-2b`, `google/gemma-2b-it`, `Qwen/Qwen3-1.7B-Base`, `Qwen/Qwen3-1.7B`, `Qwen/Qwen3-4B`, `deepseek-ai/deepseek-math-7b-base`, `deepseek-ai/deepseek-math-7b-instruct`, `deepseek-ai/deepseek-math-7b-rl`, `meta-llama/Meta-Llama-3.1-8B`, and `mistralai/Mistral-7B-v0.3` on `orig_contaminated` ($N=100$), `func_variations_v1` ($N=100$), `func_variations_all5` ($N=500$), and `orig_unseen_control` ($N=100$ seed-42 non-overlapping sample).
   - Computes free-generation Boxed-Answer Exact Match ($\text{EM}$ via normalized string matching on `skampere1`, since `antlr4` was absent for SymPy `parse_latex`; not Lean-checked, single-call chain-of-thought without test-time search or deterministic tooling [no DT]), $\text{TFA}_{\text{sol}}$, $\text{TFA}_{\text{box}}$, and $\text{TFCE}_{\text{sol}}$.
3. **Phase 3 (`expt_v1/run_snap_tfa_and_sft_contamination.py` — Controlled SFT Logic-Contamination Trajectory):**
   - Fine-tunes all **3 protocol-declared models** (`google/gemma-2b-it`, `Qwen/Qwen3-1.7B`, and `deepseek-ai/deepseek-math-7b-instruct`) directly on the $N=100$ `orig_contaminated` problems for 10 epochs with prompt-masked causal loss and explicit EOS supervision, evaluating Epochs $\{0, 1, 3, 5, 10\}$ on all 4 splits.
4. **Delivered Implementation Differences vs. Locked [`PROTOCOL.md`](PROTOCOL.md) (preserved frozen):**
   - `PROMPT_TEMPLATE` includes a 1-shot matrix-determinant chain-of-thought example prior to `Problem:\n{problem}` rather than bare zero-shot.
   - Greedy free-generation cap is `max_new_tokens=384` (vs. `512` in frozen protocol).
   - Phase 2 expanded from 8 to 10 models by adding `meta-llama/Meta-Llama-3.1-8B` and `mistralai/Mistral-7B-v0.3` (`worker_group frontier8b`).
   - Phase 3 SFT on `deepseek-ai/deepseek-math-7b-instruct` trains attention projections plus output head (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `lm_head`) at `lr=1.5e-5` with `micro_batch_size=2` and `gradient_accumulation_steps=5` (`lr=1e-5` full-parameter planned in locked protocol) so 7B SFT fits within single-GPU 80 GB VRAM with gradient checkpointing.
   - On `skampere1` (`vllm_env`), `antlr4` was absent so `_sympy_equiv` raised `ImportError` and fell back to normalized exact string matching (`0` SymPy overrides; post-hoc local SymPy `parse_latex` audit finds `28/7,500` algebraically equivalent pairs with zero change to any hypothesis verdict). In addition, `_encode_tfa_item` sets `box_end` to the final pre-EOS solution token, so $\text{TFA}_{\text{box}}$ spans from `\boxed{...}` through trailing closing prose on `23/100` originals.

## Structure

- [`PROTOCOL.md`](PROTOCOL.md) — Frozen experimental protocol (`10-16-2026`), input manifest, SHA-256 digests, and statistical plan.
- [`results.md`](results.md) — Executive result ledger with links to versioned reports and exact summary numbers.
- [`RESULTS_sft_logic_contamination_and_tfa_v1.md`](RESULTS_sft_logic_contamination_and_tfa_v1.md) — Complete versioned scientific report (corrected `11-23-2026` with all 10 Phase-2 models, all 3 Phase-3 SFT trajectories, domain breakdown, and `agy` Mega QA audit trail).
- [`CKPT_sft_logic_contamination_and_tfa.md`](CKPT_sft_logic_contamination_and_tfa.md) — Durable execution checkpoint tracking Phase 1, Phase 2, Phase 3, and `agy` Mega QA completion.
- [`expt_v1/cc.md`](expt_v1/cc.md) — Exact reproducible command script for Phase 1, Phase 2 (`gpu0`, `gpu5`, `gpu7`, `frontier8b`), Phase 3, aggregation, and verification.
- [`expt_v1/analyze_phase1_existing_data.py`](expt_v1/analyze_phase1_existing_data.py) — Deterministic analysis script for Phase 1 existing datasets.
- [`expt_v1/run_snap_tfa_and_sft_contamination.py`](expt_v1/run_snap_tfa_and_sft_contamination.py) — GPU evaluation and SFT contamination runner for Phase 2 and Phase 3 on SNAP.
- [`expt_v1/analyze_phase2_phase3_stats.py`](expt_v1/analyze_phase2_phase3_stats.py) — Bootstrap confidence interval, hypothesis test, mathematical domain disaggregation, and correlation aggregator for Phase 2 and Phase 3 outputs.
- [`expt_v1/verify_expt01.py`](expt_v1/verify_expt01.py) — Deterministic AST/SLOC/hash/link/statistical-consistency verification suite.
- [`expt_v1/results/`](expt_v1/results/) — Per-item CSV (`phase2_10models_baseline_per_item.csv`, `phase3_3models_sft_trajectory_per_item.csv`), summary CSVs (`phase2_10models_baseline_summary.csv`, `phase3_3models_sft_trajectory_summary.csv`, `phase2_phase3_by_topic_summary.csv`), statistical JSON tables (`phase1_summary_stats.json`, `phase2_phase3_statistical_tests.json`), and 3-stage Mega QA receipt ([`mega_qa_agy_11-23-2026.json`](expt_v1/results/mega_qa_agy_11-23-2026.json)).

## Status

**As of `11-23-2026`:** Phase 1 local audit, Phase 2 (10 open-weight models across 5 families, `8,000` per-item rows), Phase 3 (`Qwen/Qwen3-1.7B`, `google/gemma-2b-it`, and `deepseek-ai/deepseek-math-7b-instruct` through Epoch 10 on `skampere1`, `12,000` per-item rows), and sequential 3-stage `agy` Mega QA (`gemini-4-neon-xhigh` [`FIXED`] $\to$ `gemini-pro-orchestrator-neon` [`PASS`] $\to$ `gemini-4-hydrogen-xhigh` [`PASS`]; `0` errors; cross-company Anthropic gate unmet due to `claude-opus-5-5-high` HTTP 429 cooldown) are **COMPLETE**. Live dependency: manuscript integration into [`paper_latex_and_notes/`](../../paper_latex_and_notes/).

**TLDR-end:** [putnam-axiom: expt01 sft-logic-contamination-tfa] Defines Experiment 01 testing SFT logic contamination and Teacher-Forced Accuracy (TFA) vs. Boxed-Answer Exact Match (EM) across 10 open-weight baseline models and 3 complete 10-epoch SFT trajectories on Putnam-AXIOM under `experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/`.
