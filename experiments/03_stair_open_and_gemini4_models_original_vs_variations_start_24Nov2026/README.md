# 03: STAIR Gateway Open Models & Antigravity CLI Gemini 4 Models on Putnam-AXIOM Original vs Variations (`11-24-2026`)

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/README.md>

**TLDR:** Evaluates `6` models in single-turn no-tool style on the `100` matched Putnam-AXIOM Original problems vs their Snapshot-1 Functional Variations (`100` pairs per model): three STAIR Gateway open models (`GLM 5.3` [substituting after `GLM 5.3 Flash` returned HTTP 400], `Kimi K3`, `DeepSeek V4.1 Flash 1017`) run on `skampere1` within the `240`/day request cap and `$15` cost ceiling, plus three local Antigravity CLI (`agy`) Gemini 4 models (`gemini-4-neon-xhigh`, `gemini-4-argon-high`, `gemini-4-carbon-high`) under a `>=20%` weekly quota reserve.

Date: 11-24-2026
As of 11-24-2026 09:35 PST

## Hypothesis & Decision Criterion
- **Hypothesis:** Both open-weight frontier models (`GLM 5.3` [substituting after `GLM 5.3 Flash` returned HTTP 400], `Kimi K3`, `DeepSeek V4.1 Flash 1017`) and Google's Gemini 4 models (`Neon XHigh`, `Argon High`, `Carbon High`) still drop substantially on Functional Variations compared to matched Originals in pure single-call evaluation with zero tools.
- **Decision criterion:** Report strict SymPy paper-grader accuracy (`expt_v1/code/score_and_report_exp03.py`), per-problem paired drop, `10,000`-resample bootstrap 95% CI, and exact two-sided McNemar `p-val` across the `100` matched pairs (with missing/failed calls retained as `0` in `n=100`; strict misses marked `ungraded` for LLM equivalence judging).

## Structure
- [`PROTOCOL.md`](PROTOCOL.md): frozen protocol, exact model IDs, `100` problem IDs, caps, and pre-registered predictions.
- [`results.md`](results.md): live results ledger (updated per completed model / day).
- [`CKPT_stair_and_gemini4_eval.md`](CKPT_stair_and_gemini4_eval.md): resumable operational checkpoint.
- `expt_v1/code/`: STAIR Gateway runner (`run_stair_gateway_eval.py`), `agy` single-call runner (`run_agy_single_call_eval.py`), scorer/README updater (`score_and_report_exp03.py`), daily continuation (`daily_stair_continuation.py`).
- `expt_v1/data/`: `matched100_problem_ids.json` and `raw_outputs/`.
- `expt_v1/results/`: scored JSONs and detailed Markdown reports.

## Status
`IN_PROGRESS` (`11-24-2026 09:35 PST`): All `3` local `agy` Gemini 4 models (`600/600` calls, `0` tool violations) and STAIR Gateway Day-1 (`239` logged [`200` `GLM 5.3`, `37` `Kimi K3`, `1` `DeepSeek V4.1 Flash 1017`, `1` HTTP-400 `GLM 5.3 Flash`] + `1` `"GLM 5.3"` HTTP-200 probe = `240` calls; `$4.6862` est.) are complete. LaunchAgent `com.brando.putnam-expt03-stair-daily` is armed at `00:15 PST` for Day-2 (`11-25-2026`) and Day-3 (`11-26-2026`) STAIR continuations (`362` calls remaining).
