# Putnam-AXIOM Experiment 01 (10-18-2026; Updated 11-23-2026): Supervised Fine-Tuning (SFT) Logic Contamination and Teacher-Forced Accuracy (TFA) vs. Boxed-Answer Exact Match (EM)

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/RESULTS_sft_logic_contamination_and_tfa_v1.md>

**TLDR:** Across 20 published models (`19/20` drop, `+4.44 percentage points [pp]`, `p = 0.00010`) and 10 live open-weight checkpoints spanning 5 families on Stanford Network Analysis Project (SNAP) A100 GPUs (`10/10` drop on functional variations, exact binomial sign test `p = 0.001953`), Solution Teacher-Forced Accuracy ($\text{TFA}_{\text{sol}}$) detects benchmark contamination far more sensitively than discrete Boxed-Answer Exact Match ($\text{EM}$). Across 10 epochs of direct Supervised Fine-Tuning (SFT) on the 100 Putnam-AXIOM Originals across 3 model families (`Qwen/Qwen3-1.7B`, `google/gemma-2b-it`, and `deepseek-ai/deepseek-math-7b-instruct`), $\text{TFA}_{\text{sol}}$ strongly tracks $\text{EM}$ (`r = 0.7909`, `45` evaluation cells) and exposes statistically significant logic transfer to paired functional variations (`+31.82 pp` on `gemma-2b-it`, `+8.38 pp` on `Qwen3-1.7B`, `+3.71 pp` on `deepseek-math-7b-instruct`, all `p = 0.00010`), refuting H1's strict zero-transfer null (`< 5 pp`) while confirming a significant surface-memorization gap ($\Delta_{\text{mem}} > 0$).

- **Date:** `10-18-2026` | **As of:** `11-23-2026`
- **Experiment Folder:** [`experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/`](.)
- **Status:** `COMPLETE` (Phase 1 local audit + 10-model Phase 2 baseline + all 3 protocol-declared Phase 3 SFT trajectories through Epoch 10; 3-stage `agy` Mega Quality Assurance [QA] PASSED in [`mega_qa_agy_11-23-2026.json`](expt_v1/results/mega_qa_agy_11-23-2026.json); cross-company Anthropic gate unmet due to `claude-opus-5-5-high` HTTP 429 cooldown)
- **API Spend:** `$0.00` (Zero application programming interface [API] spend; all open-weight GPU runs executed on `skampere1.stanford.edu` NVIDIA A100-SXM4-80GB GPUs)
- **Solver / Harness / Verification Metadata:** `single-call LLM` (no test-time compute, no multi-turn agent loop, no deterministic theorem-proving tooling [`no DT`]) using local HuggingFace `transformers 5.9.0` / `torch 2.11.0+cu130` in `bfloat16`, 1-shot matrix-determinant chain-of-thought prompt, greedy decoding (`do_sample=False`, `max_new_tokens=384`), and normalized string matching on extracted `\boxed{...}` answers (**not Lean-checked**; SymPy `parse_latex` was configured with a 2-second timeout but silently fell back to normalized string matching on `skampere1` because `antlr4` was absent in `vllm_env` — post-hoc local SymPy sensitivity audit verified in Section 8).

---

## 1. Executive Summary & Hypothesis Verdicts

This experiment tests two pre-registered hypotheses ([`README.md`](README.md)):

1. **H1 (Functional Variation Robustness to Direct Training-Set / Logic Contamination — Split Verdict):**
   - *Partial Surface-Memorization Protection Confirmed ($\Delta_{\text{mem}} > 0$):* Across all 3 SFT models at Epoch 10, direct SFT on `orig_contaminated` ($N=100$) improves $\text{TFA}_{\text{sol}}$ significantly more on the exact memorized original phrasing than on paired functional variations (`+35.00 pp` discrete $\text{EM}$ / `+1.90 pp` $\text{TFA}_{\text{sol}}$ on `google/gemma-2b-it`; `+4.20 pp` $\text{TFA}_{\text{sol}}$ on `Qwen/Qwen3-1.7B`; `+1.66 pp` $\text{TFA}_{\text{sol}}$ on `deepseek-ai/deepseek-math-7b-instruct`; all `p = 0.00010`, `10,000`-draw Monte Carlo paired sign-flip permutation test). Only `google/gemma-2b-it` clears the pre-registered $\Delta_{\text{mem}}(\text{EM}) \ge +25.0\text{ pp}$ magnitude gate (`+35.00 pp`, exact McNemar `p = 5.53e-10`).
   - *Strict Zero-Transfer Null Refuted ($|\Delta_{\text{logic}}| < 5\text{ pp}$ Refuted on Full-Parameter SFT):* Contrary to the strict null in `README.md`, memorizing the original reasoning trace transfers substantial token likelihood—and on `google/gemma-2b-it` discrete solving accuracy (`+25.00 pp`, `p = 0.00010`)—onto unseen isomorphic variations over held-out unseen Putnam control problems: **`+31.82 pp` $\text{TFA}_{\text{sol}}$ on `gemma-2b-it`** and **`+8.38 pp` on `Qwen3-1.7B`** both exceed the `5 pp` threshold at `p = 0.00010`. On attention-only `deepseek-math-7b-instruct`, net logic transfer is **`+3.71 pp`** (`p = 0.00010`), below `5 pp` in raw magnitude because partial-parameter SFT raised Originals by only `+7.13 pp`, yet still `52%` of its Original gain. Thus, functional variations block pure surface answer memorization relative to originals, **yet remain vulnerable to reasoning-path ("logic") contamination**.
2. **H2 (Teacher-Forced Accuracy [TFA] Calibration & Contamination Sensitivity — Partial / Conditional Support):**
   - *Extreme Contamination Sensitivity vs. Pre-Registered $\Delta_{\text{mem}}(\text{TFA}_{\text{sol}}) > +30.0\text{ pp}$ Gate:* Across **10 out of 10** baseline open-weight models (`5` families), $\text{TFA}_{\text{sol}}$ drops significantly from `orig_contaminated` to `func_variations_v1` and `func_variations_all5` (exact two-sided binomial sign test `p = 0.001953`), whereas $N=100$ discrete $\text{EM}$ fails significance on `9/10` models. Furthermore, on `Qwen/Qwen3-1.7B` and `deepseek-ai/deepseek-math-7b-instruct` Phase 3 SFT, discrete $\text{EM}$ fails to reach significance (`p >= 0.30`) while $\text{TFA}_{\text{sol}}$ cleanly exposes logic transfer at `p = 0.00010`. However, **0 out of 3 SFT models met the pre-registered $\Delta_{\text{mem}}(\text{TFA}_{\text{sol}}) > +30.0\text{ pp}$ divergence between `orig_contaminated` and `func_variations`** (`+1.90 pp`, `+4.20 pp`, `+1.66 pp`) precisely because reasoning-path transfer lifted `func_variations` almost in lockstep with `orig_contaminated` (whereas `orig_contaminated` vs. `orig_unseen_control` diverged by `+33.72 pp` on `gemma-2b-it`).
   - *Cross-Model Floor Compression vs. Trajectory Correlation:* At Epoch 0 alone across `10` weak baseline checkpoints (`0%–13%` $\text{EM}$ floor), cross-model correlation fails the pre-registered `r >= 0.60, rho >= 0.60` gate (`orig_contaminated` $\text{TFA}_{\text{sol}}$: `r = 0.1785 [-0.8830, 0.6357]`, $\rho = 0.0550$; $\text{TFA}_{\text{box}}$: `r = -0.2093`, $\rho = -0.2875$; `pooled_30_cells` $\text{TFA}_{\text{sol}}$: `r = 0.1728 [-0.2515, 0.4120]`) due to range restriction and instruct-vs-base tokenization style differences. Across all **45 Phase-3 SFT evaluation cells** (`0%–61%` $\text{EM}$ dynamic range), $\text{TFA}_{\text{sol}}$ clears `r >= 0.60` (`r = 0.7909 [0.6914, 0.8849]`, `p = 1.01e-10`) with Spearman $\rho = 0.5532$ (just below `0.60`) and Kendall $\tau = 0.4308$ (and $\text{TFA}_{\text{box}}$ achieves `r = 0.7172`, $\rho = 0.5299$).

---

## 2. Benchmark Manifest, Metrics, and Delivered vs. Protocol Differences

| Split Name | File Source | Count ($N$) | Role | Verified SHA-256 Hash |
| :--- | :--- |---:| :--- | :--- |
| `orig_contaminated` | [`data/Putnam-AXIOM_Variations_v4/original.json`](../../data/Putnam-AXIOM_Variations_v4/original.json) | 100 | Direct SFT training set & original split | `71f5cb5e29d1d8c92e8400ac1a31b64c52a2db486cc7bb2fe92dcb4c77805ef1` |
| `func_variations_v1` | [`data/Putnam-AXIOM_Variations_v4/test.json`](../../data/Putnam-AXIOM_Variations_v4/test.json) | 100 | Paired Variation-1 per original (`variation == "1"`) | `76c46b3626a8e8c4f09ad3431dc3add7a1e4a4a467064226ebfc0fe957dae96f` |
| `func_variations_all5` | [`data/Putnam-AXIOM_Variations_v4/test.json`](../../data/Putnam-AXIOM_Variations_v4/test.json) | 500 | All 5 functional variations per original | `76c46b3626a8e8c4f09ad3431dc3add7a1e4a4a467064226ebfc0fe957dae96f` |
| `orig_unseen_control` | [`data/Putnam_AXIOM_Original_v3.json`](../../data/Putnam_AXIOM_Original_v3.json) | 100 | Seed-42 non-overlapping unseen Putnam originals (from 422 disjoint items) | `b763cba941864a53557d603634dd519f2f9edb9eda342fe9cf4826b67da3d00b` |

### Evaluation Metrics & Statistical Convention
1. **Boxed-Answer Exact Match ($\text{EM}$):** Greedy autoregressive generation (`do_sample=False`, `max_new_tokens=384`) extracted via `last_boxed_only_string` $\to$ `remove_boxed` $\to$ `normalize_final_answer` and scored by normalized string equality on `skampere1` (SymPy `parse_latex` was configured as fallback but unavailable due to missing `antlr4` in `vllm_env`; see Section 8 sensitivity audit). All failures/unparsed outputs remain in the denominator (`100` problems).
2. **Solution Teacher-Forced Accuracy ($\text{TFA}_{\text{sol}}$):** Per-problem mean next-token argmax accuracy over gold solution tokens + `<eos>` conditioned on the prompt (`labels != -100`).
3. **Boxed-Answer Token Teacher-Forced Accuracy ($\text{TFA}_{\text{box}}$):** Next-token argmax accuracy from the start of the final gold `\boxed{answer}` span through the final pre-EOS solution token (includes trailing closing prose after `\boxed{...}` on `23/100` originals; see Section 8).
4. **Solution Teacher-Forced Cross-Entropy ($\text{TFCE}_{\text{sol}}$):** Mean negative log-likelihood in nats/token over gold solution tokens + `<eos>`. (Mean bias between $\text{TFCE}_{\text{sol}}$ and $\text{EM}$ is omitted as unit-incommensurable.)
5. **Statistical Test Distinctions:** All 95% confidence intervals (CIs) use `10,000`-draw bootstrap resampling (seed `42`, naming the explicit resampling unit: `100` paired problem clusters, `20` or `10` models, or pooled non-independent model$\times$split / model$\times$epoch$\times$split cells). Paired sign-flip permutation tests use the **exact** $2^n$ enumeration for $n \le 16$ (e.g., $n = 10$ cross-model bias, exact `p = 0.001953`) and `10,000`-draw Monte Carlo paired sign-flip or two-sample permutation tests for $n > 16$ (minimum achievable `p = 1/10,001 = 0.00010`); McNemar contingency tests and across-model binomial sign tests are **exact** closed-form binomial tests.

### Delivered Implementation vs. Locked Protocol
[`PROTOCOL.md`](PROTOCOL.md) remains frozen as pre-registered on `10-16-2026`. The delivered SNAP execution script ([`run_snap_tfa_and_sft_contamination.py`](expt_v1/run_snap_tfa_and_sft_contamination.py)) introduced 5 documented operational adjustments / runtime observations:
1. **1-Shot Prompting:** `PROMPT_TEMPLATE` prepends a single short linear-algebra determinant solved example (`\det(AB) = 24`) to stabilize base-model formatting rather than zero-shot.
2. **Generation Cap:** Greedy decoding uses `max_new_tokens=384` (vs. `512` in frozen `PROTOCOL.md`).
3. **Phase 2 Expansion (`8 -> 10` Models):** Added `meta-llama/Meta-Llama-3.1-8B` and `mistralai/Mistral-7B-v0.3` (`worker_group frontier8b`) to cover `5` distinct open-weight model families (`8,000` item evaluations total).
4. **7B Single-GPU Memory Budget Recovery:** On `10-18-2026`, `worker_gpu7` (`deepseek-ai/deepseek-math-7b-instruct` Phase 3) hit CUDA Out-Of-Memory (`torch.OutOfMemoryError`, recorded in gitignored `expt_v1/results/worker_gpu7.log`) when sharing a GPU. On `11-23-2026`, `deepseek-ai/deepseek-math-7b-instruct` was completed on dedicated `skampere1` GPU 5 with `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, updating attention projections and output head (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `lm_head`) at `lr=1.5e-5` (`micro_batch_size=2`, `grad_accum=5`) rather than `lr=1e-5` full-parameter optimization (`/lfs/skampere1/0/brando9/putnam_axiom_expt01/results/worker_gpu7_retry.log`).
5. **SymPy `antlr4` Runtime Fallback:** On `skampere1` (`vllm_env`), `antlr4` was not installed, so `_sympy_equiv` raised `ImportError` and fell back to normalized string matching (`0` SymPy overrides across `7,500` EM-scored rows). A post-hoc local SymPy audit (Section 8) confirms only `28/7,500` items (`0.37%`) differ and zero verdicts change.

---

## 3. Phase 1: Historical Data Paired Audit

### 3.1 20-Model Published Benchmark Gap (`N=20` Models)
From [`phase1_summary_stats.json`](expt_v1/results/phase1_summary_stats.json) ([`phase1_20models_original_vs_variation.csv`](expt_v1/results/phase1_20models_original_vs_variation.csv)):
- **Original EM Mean:** `17.04% [12.46%, 22.27%]`
- **Functional Variation EM Mean:** `12.60% [8.74%, 17.18%]`
- **Paired Drop (`Original - Variation`):** `+4.44 pp [+2.87, +6.10]`, `p = 0.00010` (`10,000`-draw Monte Carlo paired sign-flip test)
- **Across-Model Exact Binomial Sign Test:** `19/20` models degrade on Functional Variations (`exact binomial p = 4.01e-05`)
- **Cross-Model Agreement:** Pearson $r = 0.9508$ `[0.8355, 0.9849]` (`p = 1.34e-10`), Spearman $\rho = 0.8732$ `[0.6577, 0.9604]` (`p = 5.03e-07`), Kendall $\tau = 0.7205$ `[0.5101, 0.8780]` (`p = 1.25e-05`), mean bias `+4.44 pp [+2.87, +6.10]`.

### 3.2 Paired Problem Contingency (`DeepSeek-R1-Distill-Qwen-14B`, `N=100`)
| | Variation Correct | Variation Incorrect | Row Total |
| :--- | :---: | :---: | :---: |
| **Original Correct** | 11 | 23 | 34 (`34.0% [25.0%, 43.0%]`) |
| **Original Incorrect** | 6 | 60 | 66 (`66.0%`) |
| **Column Total** | 17 (`17.0% [10.0%, 25.0%]`) | 83 (`83.0%`) | 100 (`100%`) |

- **Paired Drop:** `+17.0 pp [+7.0, +27.0]`, **exact McNemar `p = 0.00232`** (`b = 23, c = 6`; Monte Carlo sign-flip `p = 0.00220`). **`67.6%` (`23/34`) of solved Originals fail under paired functional variation.**

### 3.3 12-Model $\times$ 5-Seed Variance Floor on MATH (`5,000` Items/Run)
Across 12 open-weight checkpoints (`60` runs total, [`phase1_12models_5runs_math_variance.csv`](expt_v1/results/phase1_12models_5runs_math_variance.csv)), stochastic run-to-run EM standard deviation spans `0.0000` (`gemma-7b-it`, `0.00%`) to `0.001257` (`0.13 pp`, `deepseek-math-7b-rl`, mean `1.22% [1.13%, 1.32%]`).

---

## 4. Phase 2: 10-Model Open-Weight TFA vs. EM Calibration (Epoch 0)

All values computed directly from [`phase2_10models_baseline_summary.csv`](expt_v1/results/phase2_10models_baseline_summary.csv) and [`phase2_phase3_statistical_tests.json`](expt_v1/results/phase2_phase3_statistical_tests.json) (`8,000` per-item evaluations across `5` families; paired `p`-values are `10,000`-draw Monte Carlo sign-flip tests):

| Model Checkpoint | Orig EM (%) [95% CI] | Var-1 EM (%) [95% CI] | Unseen EM (%) [95% CI] | Orig $\text{TFA}_{\text{sol}}$ (%) | Var-1 $\text{TFA}_{\text{sol}}$ (%) | Var-All5 $\text{TFA}_{\text{sol}}$ (%) | $\text{TFA}_{\text{sol}}$ Drop (Orig - Var-1, pp) | Var-1 Sign-Flip $p$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `Qwen/Qwen3-1.7B` | `5.0 [1.0, 10.0]` | `4.0 [1.0, 8.0]` | `8.0 [3.0, 14.0]` | `71.16 [69.77, 72.58]` | `70.48 [69.06, 71.92]` | `70.42 [68.98, 71.89]` | `+0.68 [0.35, 1.05]` | `0.000100` |
| `Qwen/Qwen3-1.7B-Base` | `2.0 [0.0, 5.0]` | `3.0 [0.0, 7.0]` | `1.0 [0.0, 3.0]` | `74.91 [73.59, 76.26]` | `74.40 [73.07, 75.77]` | `74.34 [73.01, 75.73]` | `+0.51 [0.15, 0.92]` | `0.007399` |
| `Qwen/Qwen3-4B` | `8.0 [3.0, 14.0]` | `13.0 [7.0, 20.0]` | `13.0 [7.0, 20.0]` | `73.24 [71.91, 74.60]` | `72.60 [71.25, 73.98]` | `72.60 [71.23, 73.99]` | `+0.64 [0.29, 1.03]` | `0.000200` |
| `deepseek-ai/deepseek-math-7b-base` | `3.0 [0.0, 7.0]` | `10.0 [5.0, 16.0]` | `4.0 [1.0, 8.0]` | `74.31 [72.94, 75.69]` | `73.39 [71.95, 74.86]` | `73.43 [72.00, 74.89]` | `+0.92 [0.56, 1.31]` | `0.000100` |
| `deepseek-ai/deepseek-math-7b-instruct` | `6.0 [2.0, 11.0]` | `5.0 [1.0, 10.0]` | `10.0 [5.0, 16.0]` | `72.92 [71.51, 74.34]` | `71.99 [70.54, 73.47]` | `72.15 [70.69, 73.62]` | `+0.93 [0.59, 1.30]` | `0.000100` |
| `deepseek-ai/deepseek-math-7b-rl` | `7.0 [3.0, 12.0]` | `4.0 [1.0, 8.0]` | `4.0 [1.0, 8.0]` | `72.37 [70.98, 73.76]` | `71.41 [69.95, 72.90]` | `71.54 [70.08, 73.02]` | `+0.95 [0.61, 1.33]` | `0.000100` |
| `google/gemma-2b` | `1.0 [0.0, 3.0]` | `0.0 [0.0, 0.0]` | `1.0 [0.0, 3.0]` | `71.92 [70.54, 73.35]` | `71.09 [69.67, 72.54]` | `71.09 [69.64, 72.55]` | `+0.83 [0.53, 1.14]` | `0.000100` |
| `google/gemma-2b-it` | `1.0 [0.0, 3.0]` | `0.0 [0.0, 0.0]` | `0.0 [0.0, 0.0]` | `65.48 [64.02, 66.99]` | `64.50 [62.96, 66.09]` | `64.52 [62.98, 66.11]` | `+0.99 [0.62, 1.39]` | `0.000100` |
| `meta-llama/Meta-Llama-3.1-8B` | `3.0 [0.0, 7.0]` | `1.0 [0.0, 3.0]` | `3.0 [0.0, 7.0]` | `74.86 [73.57, 76.16]` | `74.28 [72.96, 75.63]` | `74.23 [72.91, 75.59]` | `+0.59 [0.30, 0.89]` | `0.000100` |
| `mistralai/Mistral-7B-v0.3` | `2.0 [0.0, 5.0]` | `0.0 [0.0, 0.0]` | `1.0 [0.0, 3.0]` | `74.79 [73.52, 76.10]` | `74.10 [72.74, 75.47]` | `74.08 [72.73, 75.44]` | `+0.70 [0.37, 1.08]` | `0.000100` |

### Key Phase 2 Findings (`N=10` Models)
1. **Universal `10/10` TFA Contamination Signal Across 5 Families:** Every single tested open-weight model (`Qwen3`, `DeepSeekMath`, `Gemma`, `Llama-3.1`, `Mistral`) exhibits a positive `Orig - Var` drop in $\text{TFA}_{\text{sol}}$ (`+0.51 pp` to `+0.99 pp` on `Var-1`; `+0.56 pp` to `+0.96 pp` on `Var-All5`, where all `10/10` satisfy `p <= 0.00040`; across-model exact binomial sign test `p = 0.001953`). Meanwhile, `N=100` discrete $\text{EM}$ shows `exact McNemar p >= 0.226` on `9/10` models (and only `deepseek-math-7b-base` swings `3% -> 10%` in the opposite direction, `p = 0.015625`).
2. **Baseline Floor Compression ($r = 0.1785$, Correction of Earlier Stale Value):** Across the `10` Epoch-0 baselines clustered near the `0%–13%` $\text{EM}$ floor, cross-model correlation between $\text{TFA}_{\text{sol}}$ and $\text{EM}$ is flat/noisy (`orig_contaminated`: mean $\text{TFA}_{\text{sol}} = 72.60\%$, mean $\text{EM} = 3.80\%$, mean bias `+68.80 pp [+66.78, +70.83]`, exact $2^{10}$ sign-flip `p = 0.001953`, Pearson $r = 0.1785$ `[-0.8830, 0.6357]`, `p = 0.6217`, Spearman $\rho = 0.0550$, Kendall $\tau = 0.0000$; `func_variations_v1`: $r = 0.2552$, $\rho = 0.1169$; `pooled_30_cells` [non-independent model$\times$split cell bootstrap]: $r = 0.1728$ `[-0.2515, 0.4120]`). Unfinetuned base models score high teacher-forced token predictability on human-written proofs despite formatting/reasoning failures in free generation, explaining why Epoch-0 rank correlation requires wide competence variation (as occurs in Phase 3).

---

## 5. Phase 3: 3-Model Controlled SFT Logic-Contamination Trajectories

All 3 protocol-declared models were fine-tuned exclusively on the $N=100$ `orig_contaminated` problems (`original.json`) for 10 epochs (`12,000` per-item evaluation rows, `60` split rows, `45` EM-scored cells in [`phase3_3models_sft_trajectory_summary.csv`](expt_v1/results/phase3_3models_sft_trajectory_summary.csv)).

### 5.1 Epoch-by-Epoch Trajectories (Epochs `0, 1, 3, 5, 10`)

#### Model A: `Qwen/Qwen3-1.7B` (Full Parameter SFT, `lr = 2e-5`)
| Epoch | Train Loss | Orig EM (%) | Var-1 EM (%) | Unseen EM (%) | Orig $\text{TFA}_{\text{sol}}$ (%) | Var-All5 $\text{TFA}_{\text{sol}}$ (%) | Unseen $\text{TFA}_{\text{sol}}$ (%) | Orig $\text{TFCE}_{\text{sol}}$ | Var-All5 $\text{TFCE}_{\text{sol}}$ | Unseen $\text{TFCE}_{\text{sol}}$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | `--` | `5.0 [1.0, 10.0]` | `4.0 [1.0, 8.0]` | `8.0 [3.0, 14.0]` | `71.16` | `70.42` | `70.79` | `1.3801` | `1.4119` | `1.4191` |
| **1** | `1.1317` | `3.0 [0.0, 7.0]` | `2.0 [0.0, 5.0]` | `3.0 [0.0, 7.0]` | `73.86` | `72.84` | `72.71` | `1.0106` | `1.0483` | `1.0774` |
| **3** | `0.8757` | `5.0 [1.0, 10.0]` | `2.0 [0.0, 5.0]` | `4.0 [1.0, 8.0]` | `77.09` | `75.70` | `73.93` | `0.8310` | `0.8880` | `0.9911` |
| **5** | `0.7661` | `3.0 [0.0, 7.0]` | `8.0 [3.0, 14.0]` | `2.0 [0.0, 5.0]` | `79.42` | `77.54` | `73.87` | `0.7323` | `0.8093` | `0.9911` |
| **10** | `0.5437` | `6.0 [2.0, 11.0]` | `6.0 [2.0, 11.0]` | `5.0 [1.0, 10.0]` | `85.75` | `80.81` | `72.80` | `0.5017` | `0.6955` | `1.1359` |

#### Model B: `google/gemma-2b-it` (Full Parameter SFT, `lr = 2e-5`)
| Epoch | Train Loss | Orig EM (%) | Var-1 EM (%) | Unseen EM (%) | Orig $\text{TFA}_{\text{sol}}$ (%) | Var-All5 $\text{TFA}_{\text{sol}}$ (%) | Unseen $\text{TFA}_{\text{sol}}$ (%) | Orig $\text{TFCE}_{\text{sol}}$ | Var-All5 $\text{TFCE}_{\text{sol}}$ | Unseen $\text{TFCE}_{\text{sol}}$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | `--` | `1.0 [0.0, 3.0]` | `0.0 [0.0, 0.0]` | `0.0 [0.0, 0.0]` | `65.48` | `64.52` | `64.80` | `1.8219` | `1.8756` | `1.8880` |
| **1** | `1.3528` | `2.0 [0.0, 5.0]` | `2.0 [0.0, 5.0]` | `3.0 [0.0, 7.0]` | `79.20` | `77.56` | `68.09` | `0.7520` | `0.8208` | `1.2301` |
| **3** | `0.2476` | `25.0 [17.0, 34.0]` | `13.0 [7.0, 20.0]` | `1.0 [0.0, 3.0]` | `98.45` | `95.40` | `66.75` | `0.0723` | `0.2121` | `1.7120` |
| **5** | `0.0332` | `54.0 [44.0, 64.0]` | `22.0 [14.0, 30.0]` | `3.0 [0.0, 7.0]` | `99.71` | `96.93` | `66.39` | `0.0145` | `0.1701` | `2.1934` |
| **10** | `0.0161` | `61.0 [51.0, 70.0]` | `25.0 [17.0, 34.0]` | `0.0 [0.0, 0.0]` | `99.81` | `96.96` | `65.41` | `0.0092` | `0.1744` | `2.3001` |

#### Model C: `deepseek-ai/deepseek-math-7b-instruct` (`q_proj, k_proj, v_proj, o_proj, lm_head`, `lr = 1.5e-5`)
| Epoch | Train Loss | Orig EM (%) | Var-1 EM (%) | Unseen EM (%) | Orig $\text{TFA}_{\text{sol}}$ (%) | Var-All5 $\text{TFA}_{\text{sol}}$ (%) | Unseen $\text{TFA}_{\text{sol}}$ (%) | Orig $\text{TFCE}_{\text{sol}}$ | Var-All5 $\text{TFCE}_{\text{sol}}$ | Unseen $\text{TFCE}_{\text{sol}}$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | `--` | `6.0 [2.0, 11.0]` | `5.0 [1.0, 10.0]` | `10.0 [5.0, 16.0]` | `72.92` | `72.15` | `72.00` | `1.1784` | `1.2092` | `1.2494` |
| **1** | `1.0941` | `7.0 [2.0, 12.0]` | `3.0 [0.0, 7.0]` | `8.0 [3.0, 14.0]` | `74.33` | `73.30` | `72.82` | `1.0228` | `1.0649` | `1.1137` |
| **3** | `0.9298` | `9.0 [4.0, 15.0]` | `6.0 [2.0, 11.0]` | `9.0 [4.0, 15.0]` | `75.95` | `74.68` | `73.57` | `0.9122` | `0.9680` | `1.0437` |
| **5** | `0.8766` | `8.0 [3.0, 14.0]` | `4.0 [1.0, 8.0]` | `9.0 [4.0, 15.0]` | `77.09` | `75.59` | `73.73` | `0.8591` | `0.9225` | `1.0276` |
| **10** | `0.7657` | `5.0 [1.0, 10.0]` | `3.0 [0.0, 7.0]` | `7.0 [3.0, 12.0]` | `80.05` | `77.63` | `73.76` | `0.7448` | `0.8366` | `1.0364` |

### 5.2 Deterministic Hypothesis Tests Across All 3 SFT Models (Epoch 10 vs. Epoch 0)
All cluster bootstrap CIs (`B=10,000`, `N=100` problem clusters) and permutation/exact tests from [`phase2_phase3_statistical_tests.json`](expt_v1/results/phase2_phase3_statistical_tests.json):

| SFT Model | Metric | Orig Gain ($\Delta \text{Orig}$) | Var Gain ($\Delta \text{Var}$) | Unseen Gain ($\Delta \text{Unseen}$) | Memorization Gap $\Delta_{\text{mem}}$ (`Orig - Var`) | Net Logic Contamination $\Delta_{\text{logic}}$ (`Var - Unseen`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `Qwen/Qwen3-1.7B` | **Boxed EM** | `+1.00 pp [-5.00, +7.00]` (`McNemar p=1.0`) | `+2.00 pp [-3.00, +8.00]` (`McNemar p=0.7266`) | `-3.00 pp [-8.00, +2.00]` (`McNemar p=0.4531`) | `-1.00 pp [-8.00, +6.00]`, `p=1.0` | `+5.00 pp [-2.00, +13.00]`, `p=0.3049` |
| `Qwen/Qwen3-1.7B` | **$\text{TFA}_{\text{sol}}$ (Var-All5)** | `+14.59 pp [+13.74, +15.46]`, `p=0.00010` | `+10.39 pp [+9.73, +11.07]`, `p=0.00010` | `+2.01 pp [+1.60, +2.43]`, `p=0.00010` | **`+4.20 pp [+3.64, +4.78]`**, `p=0.00010` | **`+8.38 pp [+7.61, +9.19]`**, `p=0.00010` |
| `Qwen/Qwen3-1.7B` | **$\text{TFA}_{\text{box}}$ (Var-1)** | `+21.88 pp [+18.76, +25.38]`, `p=0.00010` | `+13.48 pp [+11.18, +15.79]`, `p=0.00010` | `+8.02 pp [+4.69, +10.94]`, `p=0.00010` | `+8.41 pp [+5.43, +11.97]`, `p=0.00010` | `+5.45 pp [+1.74, +9.57]`, `p=0.00400` |
| `google/gemma-2b-it` | **Boxed EM** | `+60.00 pp [+50.00, +70.00]` (`McNemar p=1.73e-18`, `b10=60, b01=0`) | `+25.00 pp [+17.00, +34.00]` (`McNemar p=5.96e-08`, `b10=25, b01=0`) | `0.00 pp [0.00, 0.00]` (`McNemar p=1.0`) | **`+35.00 pp [+25.00, +45.00]`** (`McNemar b10=36, b01=1, p=5.53e-10`) | **`+25.00 pp [+17.00, +34.00]`**, `p=0.00010` |
| `google/gemma-2b-it` | **$\text{TFA}_{\text{sol}}$ (Var-All5)** | `+34.33 pp [+32.81, +35.80]`, `p=0.00010` | `+32.43 pp [+30.80, +33.98]`, `p=0.00010` | `+0.61 pp [+0.10, +1.10]`, `p=0.02060` | **`+1.90 pp [+1.14, +2.86]`**, `p=0.00010` | **`+31.82 pp [+30.15, +33.46]`**, `p=0.00010` |
| `google/gemma-2b-it` | **$\text{TFA}_{\text{box}}$ (Var-1)** | `+29.12 pp [+24.61, +33.69]`, `p=0.00010` | `+19.59 pp [+14.76, +24.14]`, `p=0.00010` | `+4.61 pp [+1.60, +7.81]`, `p=0.00570` | `+9.54 pp [+4.88, +14.70]`, `p=0.00010` | `+14.98 pp [+9.17, +20.48]`, `p=0.00010` |
| `deepseek-math-7b-instruct` | **Boxed EM** | `-1.00 pp [-6.00, +4.00]` (`McNemar p=1.0`) | `-2.00 pp [-7.00, +3.00]` (`McNemar p=0.6875`) | `-3.00 pp [-8.00, +2.00]` (`McNemar p=0.4531`) | `+1.00 pp [-4.00, +6.00]`, `p=1.0` | `+1.00 pp [-6.00, +8.00]`, `p=1.0` |
| `deepseek-math-7b-instruct` | **$\text{TFA}_{\text{sol}}$ (Var-All5)** | `+7.13 pp [+6.58, +7.71]`, `p=0.00010` | `+5.47 pp [+5.08, +5.89]`, `p=0.00010` | `+1.76 pp [+1.48, +2.08]`, `p=0.00010` | **`+1.66 pp [+1.32, +2.02]`**, `p=0.00010` | **`+3.71 pp [+3.19, +4.21]`**, `p=0.00010` |
| `deepseek-math-7b-instruct` | **$\text{TFA}_{\text{box}}$ (Var-1)** | `+10.80 pp [+7.89, +14.25]`, `p=0.00010` | `+6.00 pp [+4.45, +7.78]`, `p=0.00010` | `+3.43 pp [+2.04, +5.01]`, `p=0.00010` | `+4.80 pp [+2.07, +8.22]`, `p=0.00010` | `+2.57 pp [+0.40, +4.85]`, `p=0.02510` |

*(For completeness, `Var-1` net logic contamination on $\text{TFA}_{\text{sol}}$ mirrors `Var-All5`: `+8.41 pp [+7.63, +9.24], p = 0.00010` on `Qwen/Qwen3-1.7B`; `+31.84 pp [+30.19, +33.43], p = 0.00010` on `google/gemma-2b-it`; `+3.85 pp [+3.34, +4.37], p = 0.00010` on `deepseek-ai/deepseek-math-7b-instruct`. For `google/gemma-2b-it` EM memorization gap, exact McNemar applies to the paired gain indicators `d_orig_em, d_var1_em` because zero `1 -> 0` regressions occurred; `Qwen3-1.7B` and `deepseek-math-7b-instruct` have ternary `{-1, 0, +1}` EM diffs and use Monte Carlo paired sign-flip tests.)*

### 5.3 Cross-Cell Trajectory Correlation (`N=45` Evaluation Cells)
Across all `45` Phase-3 cells (`3 models × 5 epochs × 3 EM-scored splits`; note that CIs resample non-independent model$\times$epoch$\times$split cells with `B=10,000` draws rather than independent models, so intervals measure cell-level tracking across the SFT trajectory):
- **$\text{TFA}_{\text{sol}}$ vs. Boxed EM:** Pearson $r = 0.7909$ `[0.6914, 0.8849]` (`p = 1.01e-10`), Spearman $\rho = 0.5532$ `[0.2549, 0.7751]` (`p = 8.12e-05`), Kendall $\tau = 0.4308$ `[0.1871, 0.6429]` (`p = 5.09e-05`), mean bias ($\text{TFA}_{\text{sol}} - \text{EM}$) = `+68.37 pp [+66.10, +70.35]` (`p = 0.00010`, `10,000`-draw Monte Carlo paired sign-flip).
- **$\text{TFA}_{\text{box}}$ vs. Boxed EM:** Pearson $r = 0.7172$ `[0.5221, 0.8333]` (`p = 2.97e-08`), Spearman $\rho = 0.5299$ `[0.2387, 0.7433]` (`p = 0.000182`), Kendall $\tau = 0.3870$ `[0.1592, 0.5876]` (`p = 0.000274`), mean bias = `+72.06 pp [+69.50, +74.31]` (`p = 0.00010`, `10,000`-draw Monte Carlo paired sign-flip).

---

## 6. Mathematical Domain Disaggregation (Phase 2 & Phase 3)

Putnam competition problems frequently carry multi-label subject tags (`problem_type`); the table below reports multi-label subsets from [`phase2_phase3_by_topic_summary.csv`](expt_v1/results/phase2_phase3_by_topic_summary.csv) (`n_orig` paired problems out of `100` — all `100/100` covered — and `n_unseen` control problems out of `100`, with `1` problem [`1948_6_i`, `Differential Equations`] outside the `8` canonical tags). The Phase-2 column reports the `10`-model $\text{TFA}_{\text{sol}}$ `Orig - Var-All5` gap; the three Phase-3 columns report Epoch-10 $\text{TFA}_{\text{sol}}$ net logic contamination on `Var-1` minus `Unseen` (`sft_var1_gain_pp - sft_unseen_gain_pp`):

| Mathematical Domain (Multi-Label) | $N_{\text{orig}}$ | $N_{\text{unseen}}$ | Phase-2 10-Model $\text{TFA}_{\text{sol}}$ Gap (pp) | `gemma-2b-it` Net Logic Contamination (pp) | `Qwen3-1.7B` Net Logic Contamination (pp) | `deepseek-math-7b-instruct` Net Logic Contamination (pp) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Algebra** | 28 | 33 | `+1.233` | `+30.05` | `+8.02` | `+4.08` |
| **Calculus** | 27 | 26 | `+1.104` | `+28.11` | `+6.88` | `+3.55` |
| **Analysis** | 23 | 39 | `+0.894` | `+28.92` | `+7.88` | `+2.83` |
| **Geometry** | 25 | 20 | `+0.551` | `+32.87` | `+7.71` | `+4.19` |
| **Number Theory** | 28 | 22 | `+0.538` | `+34.96` | `+9.80` | `+4.59` |
| **Probability** | 10 | 3 | `+0.357` | `+30.30` | `+7.00` | `+4.69` |
| **Combinatorics** | 21 | 19 | `+0.316` | `+34.21` | `+9.30` | `+4.15` |
| **Linear Algebra** | 8 | 6 | `+0.271` | `+37.15` | `+12.37` | `+4.20` |

**Domain Pattern:** At baseline (Phase 2), pre-training `TFA_sol` gaps are largest in **Algebra (`+1.233 pp`)**, **Calculus (`+1.104 pp`)**, and **Analysis (`+0.894 pp`)**; during controlled Phase 3 SFT, parametric variation substitution permits strong reasoning-path logic transfer across **all 8 mathematical domains** (`+28.11` to `+37.15 pp` on `gemma-2b-it`, peaking in Linear Algebra and Number Theory).

---

## 7. Mega QA Audit Trail (`11-23-2026`)

| Stage | Requested CLI & Model | Executed Model / Effort | Reviewed Scope / Base | Conversation ID | Verdict & Counts | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1** | `agy --model claude-opus-5-5-high` | `gemini-4-neon-xhigh` (`XHigh`, `992.0s`) | `cf1bda2..working-tree` (`experiments/01_*`, `experiments/README.md`) | `958e8170-4df8-4dd7-8d1d-0017eb37571f` | `FIXED` (`0` crit / `4` major / `10` fixes / `STRUCTURAL: IMPROVED`) | Initial `claude-opus-5-5-high` (`97c8e996-9c2a-4703-be42-f9845468834b`) hit HTTP 429 (`Resets in 55h58m35s`); fallback fixed SymPy `antlr4` disclosure/sensitivity audit (`28/7,500`), `B=10,000` unification, and AST nesting/dedup. |
| **Stage 2** | `agy --model gemini-pro-orchestrator-neon` | `gemini-pro-orchestrator-neon` (`440.9s`) | `cf1bda2..working-tree` (`experiments/01_*`, `experiments/README.md`) | `210952b9-865b-44bc-b569-2196153525ce` | `PASS` (`0` crit / `0` major / `0` fixes / `STRUCTURAL: PASS`) | Independent programmatic audit verified bit-for-bit JSON/CSV/SHA-256/report alignment and AST limits (`CC <= 9`, `SLOC <= 57`, `nesting <= 2`). |
| **Stage 3** | `agy --model gemini-4-hydrogen-xhigh` | `gemini-4-hydrogen-xhigh` (`XHigh`, `402.4s`) | `cf1bda2..working-tree` (`experiments/01_*`, `experiments/README.md`) | `0d1d3132-9490-45b8-95f6-fca38552234f` | `PASS` (`0` crit / `0` major / `0` fixes / `STRUCTURAL: PASS`) | Final clean-eyes verification across all `95` Python functions, hashes, tables, and checks (`0` errors). |

- **Cross-Company Acceptance Disclosure & Audit Receipt:** Full machine-readable audit telemetry is committed in [`mega_qa_agy_11-23-2026.json`](expt_v1/results/mega_qa_agy_11-23-2026.json). Because `claude-opus-5-5-high` returned HTTP `429` (`Resets in 55h58m35s`), all 3 sequential Mega QA stages ran on flagship Google `agy` models; the **cross-company Anthropic acceptance gate remains unmet** (benchmark `data/` was untouched, so Trigger Rule 43 does not apply).

---

## 8. Limitations & Remaining Work

1. **Sample Size & Prompt Scope:** Paired original/variation sets contain $N=100$ clusters (`500` total variations) under single-call 1-shot greedy decoding (`max_new_tokens=384`); frontier closed models and test-time compute are evaluated separately in `experiments/02_frontier_models_original_vs_variations_nov2026/`.
2. **7B SFT Subset Constraint:** Because full-parameter AdamW on 7B models exceeded remaining single-GPU headroom under shared workloads on `10-18-2026`, `deepseek-ai/deepseek-math-7b-instruct` Phase 3 fine-tuned attention projections and `lm_head` (`lr=1.5e-5`), explaining its steadier `TFA_sol` rise (`+7.13 pp`) without discrete EM explosion compared to full-parameter `google/gemma-2b-it` (`+34.33 pp` `TFA_sol`, `+60.00 pp` EM).
3. **SymPy `antlr4` Runtime Fallback & $\text{TFA}_{\text{box}}$ Span:** On `skampere1`, `vllm_env` lacked `antlr4`, so `_sympy_equiv` raised `ImportError` and recorded EM reflects normalized exact string matching (`0` SymPy overrides across `7,500` EM-scored rows). A post-hoc local SymPy `parse_latex` audit across all `2,327` valid non-matching answers identifies `28/7,500` (`0.37%`: `15` Phase 2, `13` Phase 3) algebraically equivalent pairs; re-scoring them leaves all conclusions intact (`Phase-2 orig r: 0.1785 -> 0.1569`, `Phase-3 45-cell r: 0.7909 -> 0.7971`, `gemma-2b-it` EM $\Delta_{\text{mem}} = +35.00\text{ pp}$ and $\Delta_{\text{logic}} = +25.00\text{ pp}$ unchanged). Separately, `_encode_tfa_item` sets `box_end` to the final pre-EOS solution token, so $\text{TFA}_{\text{box}}$ includes trailing closing remarks after `\boxed{...}` on `23/100` originals (`115/500` variations).

**TLDR-end:** [putnam-axiom: expt01 sft-logic-contamination-tfa] Verified `10/10` open-weight Phase-2 models across 5 families and all `3` protocol-declared Phase-3 SFT models (`45` trajectory cells, `r = 0.7909`), showing continuous $\text{TFA}_{\text{sol}}$ cleanly exposes reasoning-path contamination (`p = 0.00010`) across all 8 Putnam mathematical domains even where discrete Boxed EM lacks statistical power.
