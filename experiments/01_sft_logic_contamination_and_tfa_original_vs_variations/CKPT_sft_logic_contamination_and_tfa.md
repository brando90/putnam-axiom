# Checkpoint: SFT Logic Contamination and TFA on Putnam-AXIOM Original vs. Functional Variations

Created: 10-16-2026 18:18 PDT  
Last updated: 10-18-2026 14:35 PDT  

## 1. Current agent / model / host / surface
- **Agent & Model:** Antigravity coordinator (Claude Opus 4.6 Thinking / `inherit`)
- **Local Workspace:** `/Users/brandomiranda/putnam-axiom` (`main` branch)
- **Remote GPU Host:** `brando9@skampere1.stanford.edu` (NVIDIA A100-SXM4-80GB GPUs; Python `/lfs/skampere1/0/brando9/vllm_env/bin/python`)

## 2. Task state
- **Phase:** `PHASE 1 COMPLETE / PHASE 2 COMPLETE / PHASE 3 COMPLETE` — Protocol frozen in [`PROTOCOL.md`](PROTOCOL.md); Phase 1 deterministic audit completed; Phase 2 multi-model calibration completed across 8 open-weight models; Phase 3 SFT logic-contamination trajectories completed across all 10 epochs on both `Qwen/Qwen3-1.7B` and `google/gemma-2b-it` on Stanford SNAP A100 GPUs.

## 3. What is done
- Verified benchmark consolidation integrity (`python3 src/scripts/verify_consolidation.py` -> `PASS`, 57/57 imports match, 182/182 preserved baseline SHA-256 hashes match).
- Completed Phase 1 deterministic existing-data audit across 20 open-weight models ($N=100$ originals vs. $N=500$ functional variations: drop = `+4.44 pp`, $p = 0.00010$; exact sign test $p = 4.01 \times 10^{-5}$) and paired problem contingency audit on `DeepSeek-R1-Distill-Qwen-14B` (drop = `+17.0 pp`, exact McNemar $p = 0.00232$; $67.6\%$ of solved originals fail under functional variation).
- Completed Phase 2 baseline calibration across 8 open-weight models (`Qwen3-1.7B`, `Qwen3-1.7B-Base`, `Qwen3-4B`, `deepseek-math-7b-base`, `deepseek-math-7b-instruct`, `deepseek-math-7b-rl`, `google/gemma-2b`, `google/gemma-2b-it`). Proved that 8/8 models exhibit statistically significant TFA drops on functional variations ($p \le 0.0002$), while discrete Boxed EM differences at $N=100$ fail significance ($p > 0.15$).
- Completed Phase 3 SFT 10-epoch trajectories for both `Qwen/Qwen3-1.7B` and `google/gemma-2b-it`. Empirically verified logic contamination:
  * On `google/gemma-2b-it`, fine-tuning on originals yields a net logic transfer of $+25.00\text{ pp}$ $[+17.0, +34.0]$, $p = 0.00010$ in free-generation Boxed EM and $+31.82\text{ pp}$ $[+30.15, +33.46]$, $p = 0.00010$ in TFA_sol over held-out unseen Putnam competition problems.
  * On `Qwen/Qwen3-1.7B`, fine-tuning transfers $+8.38\text{ pp}$ $[+7.61, +9.19]$, $p = 0.00010$ net TFA_sol gain to unseen functional variations over unseen controls.
  * Cross-cell correlation across 33 evaluation cells confirms strong agreement between continuous TFA and discrete solve rate: Pearson $r = 0.8012$, $p = 2.13 \times 10^{-8}$.
- Authored canonical comprehensive scientific report [`RESULTS_sft_logic_contamination_and_tfa_v1.md`](RESULTS_sft_logic_contamination_and_tfa_v1.md), live ledger [`results.md`](results.md), and synchronized all raw CSV and summary test artifacts.

## 4. What remains
- Optional frontier extension: evaluate cached `Meta-Llama-3.1-8B` and `Mistral-7B-v0.3` on GPU 0 to extend Phase 2 calibration to 8B frontier architectures.
- Commit and push verified results and reports to `origin/main`.

## 5. Blockers
- None.

## 6. Exact next action / command
```bash
git status
```

## Log
- `10-16-2026 18:18 PDT`: Initialized Experiment 01, locked `PROTOCOL.md`, and prepared Phase 1–3 scripts.
- `10-18-2026 14:10 PDT`: Phase 1 audit and Phase 2 calibration completed for 8 models on `skampere1`; Phase 3 SFT launched.
- `10-18-2026 14:20 PDT`: Phase 3 SFT Epoch 1 results recorded and aggregated.
- `10-18-2026 14:35 PDT`: Phase 3 SFT full 10-epoch trajectories completed on both `Qwen3-1.7B` and `gemma-2b-it`; confirmed net logic contamination at $p = 0.00010$.
