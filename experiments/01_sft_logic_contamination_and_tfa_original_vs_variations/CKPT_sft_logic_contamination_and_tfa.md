# Checkpoint: Experiment 01 — SFT Logic Contamination and TFA on Putnam-AXIOM Original vs. Functional Variations

Created: 10-16-2026 18:18 PDT | Last updated: 11-23-2026 13:34 PST

## 1. Goal
Quantify SFT logic contamination (`orig_contaminated` vs. paired `func_variations` vs. `orig_unseen_control`) and evaluate Teacher-Forced Accuracy ($\text{TFA}_{\text{sol}}$, $\text{TFA}_{\text{box}}$, $\text{TFCE}_{\text{sol}}$) vs. Boxed-Answer Exact Match ($\text{EM}$) on `experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/`.

## 2. What ran
Phase 1 local audit; Phase 2 across 10 open-weight models (`5` families, `8,000` items) and Phase 3 SFT across `Qwen/Qwen3-1.7B`, `google/gemma-2b-it`, and `deepseek-ai/deepseek-math-7b-instruct` through Epoch 10 (`12,000` items) on `skampere1.stanford.edu` (`$0.00` spend); 3-stage sequential `agy` Mega Quality Assurance (`gemini-4-neon-xhigh` $\to$ `gemini-pro-orchestrator-neon` $\to$ `gemini-4-hydrogen-xhigh`).

## 3. Results
Phase 1 (`19/20` drop, `+4.44 pp`, `p=0.00010`; Qwen-14B McNemar `p=0.00232`); Phase 2 (`10/10` positive TFA drop, exact binomial `p=0.001953`; Epoch-0 floor `r=0.1785`); Phase 3 (`45` cells `r=0.7909`, `p=1.01e-10`; significant $\text{TFA}_{\text{sol}}$ net logic transfer `+31.82 pp` `gemma-2b-it`, `+8.38 pp` `Qwen3-1.7B`, `+3.71 pp` `deepseek-math-7b-instruct`, all `p=0.00010`); Mega QA PASSED (`FIXED -> PASS -> PASS`, `0` verification errors).

## 4. Stuck / blocked
No SNAP/code blockers. Optional cross-company Anthropic acceptance gate unmet (`claude-opus-5-5-high` HTTP 429 resets in `55h58m35s`).

## 5. Next steps
Integrate verified Experiment 01 tables into `paper_latex_and_notes/` (`p=9/10`), install `antlr4-python3-runtime` in `skampere1` `vllm_env`, and optionally run Anthropic/OpenAI cross-company QA after quota reset.

## 6. Brando to-do
Optional: manually rename Antigravity conversation `6f991431-c70f-447c-a90b-96ee28bd1a78` in the sidebar using the copy-ready title (`11-23-2026`).

## Log
- `10-16-2026 18:18 PDT`: Initialized Experiment 01, locked `PROTOCOL.md`, and prepared Phase 1–3 scripts.
- `10-18-2026 14:35 PDT`: Phase 1, initial 8-model Phase 2, and `Qwen3-1.7B` / `gemma-2b-it` Phase 3 trajectories completed (`worker_gpu7` OOM recorded).
- `11-23-2026 12:55 PST`: Completed 10-model Phase 2 (`frontier8b` synced) and `deepseek-math-7b-instruct` Phase 3 Epochs 1–10 on `skampere1`, aggregated `8,000` Phase-2 + `12,000` Phase-3 rows, refactored Python scripts to `CC <= 10 / SLOC <= 60`, and updated all reports from verified JSON/CSV outputs prior to 3-stage `agy` Mega QA.
- `11-23-2026 13:14 PST`: Mega QA audit fixed `B=10,000` bootstrap / exact $2^{10}$ sign-flip / unrounded exact McNemar precision, deduplicated stats helpers and eliminated all `3+` nesting in `expt_v1/*.py`, fixed latent Phase-3 resume and `HAS_SYMPY` probe in `run_snap_tfa_and_sft_contamination.py`, and aligned all reports (including `skampere1` `antlr4` fallback sensitivity audit and exact H1/H2 gate verdicts).
- `11-23-2026 13:34 PST`: Completed Stage 2 (`gemini-pro-orchestrator-neon` [`PASS`, `0/0/0`]) and Stage 3 (`gemini-4-hydrogen-xhigh` [`PASS`, `0/0/0`]); saved receipt `mega_qa_agy_11-23-2026.json` (`claude-opus-5-5-high` HTTP 429 unmet cross-company gate disclosed) and prepared landing on `main`.
