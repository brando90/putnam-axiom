# Live Results Ledger: Experiment 01 (10-16-2026; Updated 11-23-2026) — SFT Logic Contamination and Teacher-Forced Accuracy (TFA) on Putnam-AXIOM Original vs. Functional Variations

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/results.md>

- **Started:** `10-16-2026 18:18 PDT` | **Last updated (As of):** `11-23-2026 13:14 PST`
- **Current status:** `COMPLETED` — Protocol registered in [`PROTOCOL.md`](PROTOCOL.md); Phase 1 deterministic audit `COMPLETED`; Phase 2 multi-model calibration `COMPLETED` across `10` open-weight models (`5` families, `8,000` per-item evaluations); Phase 3 Supervised Fine-Tuning (SFT) logic-contamination trajectories `COMPLETED` across all `10` epochs on all `3` protocol models (`Qwen/Qwen3-1.7B`, `google/gemma-2b-it`, and `deepseek-ai/deepseek-math-7b-instruct`, `12,000` per-item evaluations) on Stanford Network Analysis Project (SNAP) A100 GPUs (`skampere1`).
- **Scope / Verification Metadata:** `single-call LLM` (no deterministic theorem-proving tooling [`no DT`], not Lean-checked, normalized string-match EM on greedy `max_new_tokens=384` outputs after `antlr4` absence on `skampere1`; post-hoc local SymPy audit finds `28/7,500` equivalent pairs with unchanged verdicts); `$0.00` application programming interface (API) spend.
- **Comprehensive Report:** [`RESULTS_sft_logic_contamination_and_tfa_v1.md`](RESULTS_sft_logic_contamination_and_tfa_v1.md) under `experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/`.

## Phase Execution Tracker

| Phase | Scope | Target Cells | Completed Cells | Status |
|---|---|---:|---:|---|
| Phase 1 | Existing-data paired audit (20-model Original vs. Variation gap; $N=100$ paired `DeepSeek-R1-Distill-Qwen-14B`; 12-model $\times$ 5-run variance) | 3 analyses | 3 / 3 | `COMPLETED` ([`phase1_20models_original_vs_variation.csv`](expt_v1/results/phase1_20models_original_vs_variation.csv)) |
| Phase 2 | 10-model open-weight baseline calibration across 5 families ($\text{EM}$, $\text{TFA}_{\text{sol}}$, $\text{TFA}_{\text{box}}$, $\text{TFCE}_{\text{sol}}$ across 4 splits) | 10 models $\times$ 4 splits = 40 split rows (`30` EM-scored) | 40 / 40 (`8,000` items) | `COMPLETED` ([`phase2_10models_baseline_summary.csv`](expt_v1/results/phase2_10models_baseline_summary.csv)) |
| Phase 3 | Controlled SFT trajectories (`Qwen/Qwen3-1.7B`, `google/gemma-2b-it`, `deepseek-ai/deepseek-math-7b-instruct` across Epochs 0, 1, 3, 5, 10 and 4 splits) | 3 models $\times$ 5 epochs $\times$ 4 splits = 60 split rows (`45` EM-scored) | 60 / 60 (`12,000` items) | `COMPLETED` ([`phase3_3models_sft_trajectory_summary.csv`](expt_v1/results/phase3_3models_sft_trajectory_summary.csv)) |

## Phase 1 Completed Findings (Existing-Data Paired Audit)

- **20-Model Original vs. Functional Variation Gap** ([`phase1_summary_stats.json`](expt_v1/results/phase1_summary_stats.json), resampling unit = $N=20$ models):
  - Original mean Boxed-Answer Exact Match (EM): `17.04% [12.46%, 22.27%]` (`mean=17.0405`) vs. Functional Variation mean EM: `12.60% [8.74%, 17.18%]`.
  - Paired drop (`Original - Variation`): `+4.44 percentage points (pp) [+2.87, +6.10]`, `p = 0.00010` (`10,000`-draw Monte Carlo paired sign-flip test); `19/20` models degrade (`exact binomial sign test p = 4.01e-05`).
  - Cross-model agreement: Pearson $r = 0.9508$ `[0.8355, 0.9849]`, Spearman $\rho = 0.8732$ `[0.6577, 0.9604]`, Kendall $\tau = 0.7205$ `[0.5101, 0.8780]`.
- **Paired Per-Item Audit on `DeepSeek-R1-Distill-Qwen-14B`** (`N=100` paired clusters):
  - Original EM `34/100 (34.0% [25.0%, 43.0%])` vs. Variation EM `17/100 (17.0% [10.0%, 25.0%])`; paired drop `+17.0 pp [+7.0, +27.0]`, **exact McNemar `p = 0.00232`** (`b = 23` orig-only vs. `c = 6` var-only; `23/34 = 67.6%` of solved Originals fail under functional variation).

## Phase 2 Completed Findings (10-Model Open-Weight Baseline Calibration)

- **`10/10` Positive TFA Contamination Sensitivity Across 5 Families** ([`phase2_10models_baseline_summary.csv`](expt_v1/results/phase2_10models_baseline_summary.csv), [`phase2_phase3_statistical_tests.json`](expt_v1/results/phase2_phase3_statistical_tests.json)):
  - Every model exhibits a statistically significant paired drop in Solution Teacher-Forced Accuracy ($\text{TFA}_{\text{sol}}$) from Originals to `Var-1` and `Var-All5` (`exact binomial sign test p = 0.001953`):
    - `Qwen/Qwen3-1.7B`: `71.16% -> 70.48%` (`+0.68 pp [0.35, 1.05]`, `p = 0.000100`)
    - `Qwen/Qwen3-1.7B-Base`: `74.91% -> 74.40%` (`+0.51 pp [0.15, 0.92]`, `p = 0.007399`; `Var-All5`: `+0.56 pp [0.24, 0.92]`, `p = 0.000400`)
    - `Qwen/Qwen3-4B`: `73.24% -> 72.60%` (`+0.64 pp [0.29, 1.03]`, `p = 0.000200`)
    - `deepseek-ai/deepseek-math-7b-base`: `74.31% -> 73.39%` (`+0.92 pp [0.56, 1.31]`, `p = 0.000100`)
    - `deepseek-ai/deepseek-math-7b-instruct`: `72.92% -> 71.99%` (`+0.93 pp [0.59, 1.30]`, `p = 0.000100`)
    - `deepseek-ai/deepseek-math-7b-rl`: `72.37% -> 71.41%` (`+0.95 pp [0.61, 1.33]`, `p = 0.000100`)
    - `google/gemma-2b`: `71.92% -> 71.09%` (`+0.83 pp [0.53, 1.14]`, `p = 0.000100`)
    - `google/gemma-2b-it`: `65.48% -> 64.50%` (`+0.99 pp [0.62, 1.39]`, `p = 0.000100`)
    - `meta-llama/Meta-Llama-3.1-8B`: `74.86% -> 74.28%` (`+0.59 pp [0.30, 0.89]`, `p = 0.000100`)
    - `mistralai/Mistral-7B-v0.3`: `74.79% -> 74.10%` (`+0.70 pp [0.37, 1.08]`, `p = 0.000100`)
- **Cross-Model Epoch-0 Calibration (`n=10`):** Near the `0%–13%` EM floor (`mean EM = 3.80%`, `mean TFA_sol = 72.60%`), cross-model linear correlation is noisy (`orig_contaminated`: Pearson $r = 0.1785$ `[-0.8830, 0.6357]`, Spearman $\rho = 0.0550$, Kendall $\tau = 0.0000$; `pooled_30_cells`: $r = 0.1728$), unlike across SFT competence regimes.

## Phase 3 Completed Findings (3-Model 10-Epoch SFT Trajectories)

- **`google/gemma-2b-it` (Full SFT):** Originals EM `1.0% -> 61.0%` (`exact McNemar p = 1.73e-18`), `Var-1` EM `0.0% -> 25.0%` (`exact McNemar p = 5.96e-08`), Unseen `0.0% -> 0.0%`. Memorization gap $\Delta_{\text{mem}}(\text{EM}) = +35.00\text{ pp}$ (`exact McNemar p = 5.53e-10`); net logic contamination $\Delta_{\text{logic}}(\text{EM}) = +25.00\text{ pp}\;[+17.00, +34.00]$ (`p = 0.00010`) and $\Delta_{\text{logic}}(\text{TFA}_{\text{sol}}) = +31.82\text{ pp}\;[+30.15, +33.46]$ (`p = 0.00010`).
- **`Qwen/Qwen3-1.7B` (Full SFT):** Discrete EM stays noisy (`+5.00 pp`, `p = 0.3049`), while $\text{TFA}_{\text{sol}}$ detects `+4.20 pp [+3.64, +4.78]` memorization gap (`p = 0.00010`) and **`+8.38 pp [+7.61, +9.19]` (`p = 0.00010`) net logic contamination**.
- **`deepseek-ai/deepseek-math-7b-instruct` (Attention Projections + `lm_head`, `lr = 1.5e-5`):** Discrete EM remains flat (`-1.00 pp` orig `McNemar p = 1.0`, `-2.00 pp` var-1 `p = 0.6875`, `-3.00 pp` unseen `p = 0.4531`; net $\Delta_{\text{logic}} = +1.00\text{ pp}$, `p = 1.0`), yet continuous $\text{TFA}_{\text{sol}}$ captures **`+1.66 pp [+1.32, +2.02]` memorization gap** and **`+3.71 pp [+3.19, +4.21]` net logic contamination** (`p = 0.00010`).
- **Trajectory Correlation (`N=45` EM-Scored Cells Across All 3 Models):** Continuous $\text{TFA}_{\text{sol}}$ strongly tracks discrete solve rate (cell-level bootstrap, `B = 10,000`): Pearson $r = 0.7909$ `[0.6914, 0.8849]` (`p = 1.01e-10`), Spearman $\rho = 0.5532$, Kendall $\tau = 0.4308$, mean bias `+68.37 pp [+66.10, +70.35]` (`p = 0.00010`). Domain breakdown ([`phase2_phase3_by_topic_summary.csv`](expt_v1/results/phase2_phase3_by_topic_summary.csv)) shows logic transfer across all `8` Putnam domains.

**TLDR-end:** [putnam-axiom: expt01 sft-logic-contamination-tfa] Completed all `10` Phase-2 models (`8,000` rows, `10/10` significant TFA drop) and all `3` Phase-3 SFT trajectories (`12,000` rows, `45` EM cells, `r = 0.7909`) under `experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/`, proving continuous $\text{TFA}_{\text{sol}}$ exposes significant logic contamination even where discrete EM cannot.
