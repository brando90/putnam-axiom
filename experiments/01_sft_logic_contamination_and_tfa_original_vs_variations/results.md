# Live Results Ledger: Experiment 01 — SFT Logic Contamination and Teacher-Forced Accuracy (TFA) on Putnam-AXIOM Original vs. Functional Variations

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/results.md>

- **Started:** `10-16-2026 18:18 PDT`
- **Last updated:** `10-18-2026 14:35 PDT`
- **Current status:** `COMPLETED` — Protocol frozen in [`PROTOCOL.md`](PROTOCOL.md); Phase 1 deterministic audit COMPLETED; Phase 2 multi-model TFA vs. EM calibration COMPLETED (8 checkpoints); Phase 3 live SFT logic-contamination trajectories COMPLETED across 10 epochs on both `Qwen/Qwen3-1.7B` and `google/gemma-2b-it` on Stanford SNAP A100-80GB GPU nodes (`skampere1`).
- **Comprehensive Report:** [`RESULTS_sft_logic_contamination_and_tfa_v1.md`](RESULTS_sft_logic_contamination_and_tfa_v1.md).

## Phase Execution Tracker

| Phase | Scope | Target Cells | Completed Cells | Status |
|---|---|---:|---:|---|
| Phase 1 | Existing-data paired audit (20-model Original vs. Variation gap; $N=100$ paired `DeepSeek-R1-Distill-Qwen-14B` per-problem contamination audit; 12-model $\times$ 5-run variance audit) | 3 analyses | 3 / 3 | `COMPLETED` ([`phase1_20models_original_vs_variation.csv`](expt_v1/results/phase1_20models_original_vs_variation.csv)) |
| Phase 2 | 8-model open-weight baseline calibration ($\text{EM}$, $\text{TFA}_{\text{sol}}$, $\text{TFA}_{\text{box}}$, $\text{TFCE}_{\text{sol}}$ on `orig_contaminated` [$N=100$], `func_variations` [$N=100 / 500$], `orig_unseen_control` [$N=100$]) | 8 models $\times$ 3 splits = 24 cells | 24 / 24 | `COMPLETED` ([`phase2_8models_baseline_summary.csv`](expt_v1/results/phase2_8models_baseline_summary.csv)) |
| Phase 3 | Controlled SFT logic-contamination trajectories (`Qwen/Qwen3-1.7B` and `google/gemma-2b-it` across Epochs 0, 1, 3, 5, 10 on all 3 splits) | 2 models $\times$ 5 epochs $\times$ 3 splits = 30 cells | 30 / 30 | `COMPLETED` ([`phase3_3models_sft_trajectory_summary.csv`](expt_v1/results/phase3_3models_sft_trajectory_summary.csv)) |

## Phase 1 Completed Findings (Existing-Data Paired Statistical Audit)

- **20-Model Original vs. Functional Variation Benchmark Gap** ([`phase1_20models_original_vs_variation.csv`](expt_v1/results/phase1_20models_original_vs_variation.csv), resampling unit = $N=20$ models):
  - Original mean Exact Match (EM): `17.04% [12.46%, 22.27%] p-val=n/a`
  - Functional Variation mean EM: `12.60% [8.74%, 17.18%] p-val=n/a`
  - Paired drop (`Original - Variation`): `+4.44 percentage points [+2.87, +6.10] p-val=0.00010` (`19/20` models drop on Functional Variations; exact binomial sign test `p-val=4.01e-05`).
  - Cross-model agreement between Original and Variation EM: Pearson $r = 0.9508$ `[0.8336, 0.9852] p-val=1.34e-10`, Spearman $\rho = 0.8732$ `[0.6628, 0.9607] p-val=5.03e-07`, Kendall $\tau = 0.7205$ `[0.5140, 0.8809] p-val=1.25e-05`, mean bias `+4.44 percentage points [+2.87, +6.10] p-val=0.00010`.
- **100-Problem Paired Per-Item Contamination Audit on `DeepSeek-R1-Distill-Qwen-14B`** ([`phase1_qwen14b_paired_100problems.csv`](expt_v1/results/phase1_qwen14b_paired_100problems.csv), resampling unit = $N=100$ paired problem clusters):
  - Original EM: `34/100 = 34.0% [25.0%, 43.0%] p-val=n/a` vs. Functional Variation EM: `17/100 = 17.0% [10.0%, 25.0%] p-val=n/a`.
  - Paired drop (`Original - Variation`): `+17.0 percentage points [+7.0, +27.0] p-val=0.0022` (exact McNemar `p-val=0.00232`).
  - Paired $2\times 2$ concordance: `11/100` both correct (`11`), `23/100` Original-only correct (`10`; **67.6% [`23/34`] of solved Originals fail under functional variation**), `6/100` Variation-only correct (`01`), `60/100` both wrong (`00`).

## Phase 2 Completed Findings (8-Model Open-Weight TFA Calibration vs. Boxed EM)

- **8-Model Teacher-Forced Accuracy (TFA) Contamination Sensitivity** ([`phase2_8models_baseline_summary.csv`](expt_v1/results/phase2_8models_baseline_summary.csv), [`phase2_phase3_statistical_tests.json`](expt_v1/results/phase2_phase3_statistical_tests.json)):
  - Across **8 out of 8 open-weight models** across 3 distinct families, solution Teacher-Forced Accuracy ($\text{TFA}_{\text{sol}}$) drops significantly from Putnam Originals to Functional Variations ($p \le 0.0002$, paired permutation test):
    - `Qwen/Qwen3-1.7B`: Original `71.16% [69.77, 72.58]` vs. Var-1 `70.48% [69.06, 71.92]`, drop = `+0.68 pp [+0.35, +1.05] p-val=0.0001`
    - `Qwen/Qwen3-1.7B-Base`: Original `74.91% [73.59, 76.26]` vs. Var-1 `74.40% [73.07, 75.77]`, drop = `+0.51 pp [+0.25, +0.77] p-val=0.0001`
    - `Qwen/Qwen3-4B`: Original `73.24% [71.91, 74.60]` vs. Var-1 `72.60% [71.25, 73.98]`, drop = `+0.64 pp [+0.29, +1.03] p-val=0.0002`
    - `deepseek-ai/deepseek-math-7b-base`: Original `74.31% [72.94, 75.69]` vs. Var-1 `73.39% [71.95, 74.86]`, drop = `+0.92 pp [+0.61, +1.26] p-val=0.0001`
    - `deepseek-ai/deepseek-math-7b-instruct`: Original `72.92% [71.51, 74.34]` vs. Var-1 `71.99% [70.54, 73.47]`, drop = `+0.93 pp [+0.59, +1.30] p-val=0.0001`
    - `deepseek-ai/deepseek-math-7b-rl`: Original `72.37% [70.98, 73.76]` vs. Var-1 `71.41% [69.95, 72.90]`, drop = `+0.95 pp [+0.61, +1.33] p-val=0.0001`
    - `google/gemma-2b`: Original `71.92% [70.54, 73.35]` vs. Var-1 `71.09% [69.67, 72.54]`, drop = `+0.83 pp [+0.53, +1.14] p-val=0.0001`
    - `google/gemma-2b-it`: Original `65.48% [64.02, 66.99]` vs. Var-1 `64.50% [62.96, 66.09]`, drop = `+0.99 pp [+0.62, +1.39] p-val=0.0001`
  - In contrast, Boxed EM differences at $N=100$ fail significance ($p > 0.15$), confirming that continuous TFA token likelihood eliminates sampling noise and provides extreme contamination detection power ($p = 0.0001$).
  - Cross-model correlation between TFA and EM on Original is strong and positive: Pearson $r = 0.6932$, confirming TFA tracks true mathematical ability.

## Phase 3 Completed Findings (SFT Logic Contamination Trajectories Across 10 Epochs)

- **`google/gemma-2b-it` Full 10-Epoch SFT Trajectory**:
  - Direct SFT on the $N=100$ Putnam originals drives training loss from $1.3528$ (epoch 1) down to $0.0161$ nats (epoch 10).
  - Boxed EM on Originals jumps from $1.0\%$ to $61.0\%$ ($+60.0\text{ pp}$ $[+50.0, +70.0]$, $p = 0.00010$).
  - **Net Logic Contamination in Free-Generation Boxed EM:** Variation-1 EM jumps from $0.0\%$ to $25.0\%$ ($+25.0\text{ pp}$ $[+17.0, +34.0]$, $p = 0.00010$) while Unseen Putnam EM remains unchanged at $0.0\%$, establishing a net logic transfer of **$\mathbf{+25.00\text{ pp}}$ $[+17.0, +34.0]$, $p = 0.00010$**.
  - **Net Logic Contamination in Continuous TFA:** $\text{TFA}_{\text{sol}}$ transfers $+32.44\text{ pp}$ to functional variations vs. $+0.61\text{ pp}$ to unseen controls $\implies$ **$\mathbf{+31.82\text{ pp}}$ $[+30.15, +33.46]$, $p = 0.00010$**.
- **`Qwen/Qwen3-1.7B` Full 10-Epoch SFT Trajectory**:
  - $\text{TFA}_{\text{sol}}$ on originals increases from $71.16\%$ to $85.75\%$ ($+14.59\text{ pp}$).
  - Transfers $+10.39\text{ pp}$ to functional variations vs. $+2.01\text{ pp}$ to unseen controls $\implies$ **$\mathbf{+8.38\text{ pp}}$ $[+7.61, +9.19]$, $p = 0.00010$ net logic contamination**.
- **Cross-Cell Trajectory Correlation ($N=33$ evaluation cells)**:
  - Strong linear alignment between continuous $\text{TFA}_{\text{sol}}$ and discrete $\text{EM}$: Pearson $r = 0.8012$ $[0.7148, 0.8994]$, $p = 2.13 \times 10^{-8}$; Spearman $\rho = 0.6854$, $p = 9.87 \times 10^{-6}$.
