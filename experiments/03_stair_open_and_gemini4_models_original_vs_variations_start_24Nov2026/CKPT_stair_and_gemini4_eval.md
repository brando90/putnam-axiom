# Checkpoint: Putnam-AXIOM Experiment 03 STAIR Open Models & Gemini 4 Single-Call Eval

Created: 11-24-2026 01:16 PST
Last updated: 11-26-2026 01:14 PST

## Goal
Evaluate `GLM 5.3` (`GLM 5.3 Flash` returned HTTP 400 on `/chat/completions`), `Kimi K3`, `DeepSeek V4.1 Flash 1017` (STAIR `bm` Gateway on `skampere1`, `240/day` cap, `$15` cost stop) and `gemini-4-neon-xhigh`, `gemini-4-argon-high`, `gemini-4-carbon-high` (local `agy` single-call mode, `>=20%` weekly reserve) on the `100` matched Originals vs Snapshot-1 Variations (`1,200` total calls).

## What ran
- Created canonical experiment folder `experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/`, `expt_v1/data/matched100_problem_ids.json`, `PROTOCOL.md`, `results.md`, `RESULTS_stair_open_and_gemini4_original_vs_variations_11-24-2026.md`, and `expt_v1/code/*`.
- STAIR `bm` Gateway Day-1 (`skampere1`): `239` logged calls (`200` `GLM 5.3`, `37` `Kimi K3`, `1` `DeepSeek V4.1 Flash 1017`, `1` HTTP-400 `GLM 5.3 Flash` = `239` logged, plus `1` earlier HTTP-200 `"GLM 5.3"` probe = `240` Day-1 cap reached; stop reason `DAILY_CAP_REACHED (239)` at `02:47:15 PST`, conservative cumulative estimate `$4.686198`).
- Antigravity CLI (`agy`) single-call Gemini 4 on Mac (`0` tool-use violations across all `600/600` calls; `permission_mode=request-review`, `num_turns=1`, empty `chmod 555` working directory): all `3` models finished `200/200` calls by `09:25:19 PST` (`85%` weekly / `98%` 5-hour Gemini quota remaining).
- Armed macOS LaunchAgent `com.brando.putnam-expt03-stair-daily` at `00:15 PST` daily to run Day-2 (`11-25-2026`) and Day-3 (`11-26-2026`) STAIR continuations (`daily_stair_continuation.py`), and synced Light-QA-hardened `run_stair_gateway_eval.py` to `skampere1`.
- Completed requested Tier-2 Light QA pass (`QA_BASE=9e70e7c`, `agy` `gemini-4-neon-xhigh` `--effort xhigh`): `VERDICT: FIXED` (Day-2 `None` formatting fix, LaunchAgent `unlink`-before-`bootout`, strict `num_turns == 1` + `$15` pre-check, `127+4=131/200` `GLM 5.3` truncation accuracy).
- Added mandatory `Thinking effort` reporting rule to `AGENTS.md`, `CLAUDE.md`, and `.cursor/rules/project.mdc`, and regenerated `README.md`, `results.md`, and `RESULTS_stair_open_and_gemini4_original_vs_variations_11-24-2026.md` with explicit `Thinking effort` columns.

## Results
- `gemini-4-argon-high` | Thinking effort: `high` (`--effort high`) | (`200/200`; `197` ok, `3` 600s timeouts): Orig `88/100` (`88.0%` [80.2, 93.0]), Var1 `77/100` (`77.0%` [67.8, 84.2]), paired drop `11.0 [5.0, 18.0]`, exact McNemar `p-val=0.003418` (`b=12`, `c=1`).
- `gemini-4-neon-xhigh` | Thinking effort: `xhigh` (`--effort xhigh`, extra-high) | (`200/200`; `191` ok, `9` 600s timeouts): Orig `87/100` (`87.0%` [79.0, 92.2]), Var1 `77/100` (`77.0%` [67.8, 84.2]), paired drop `10.0 [3.0, 18.0]`, exact McNemar `p-val=0.02127` (`b=13`, `c=3`).
- `gemini-4-carbon-high` | Thinking effort: `high` (`--effort high`) | (`200/200`; `189` ok, `11` 600s timeouts): Orig `86/100` (`86.0%` [77.9, 91.5]), Var1 `77/100` (`77.0%` [67.8, 84.2]), paired drop `9.0 [2.0, 16.0]`, exact McNemar `p-val=0.02246` (`b=11`, `c=2`).
- `GLM 5.3` | Thinking effort: `default (unset; reasoning active)` | (`200/200`, Day-1 STAIR): Orig `34/100` (`34.0%` [25.5, 43.7]), Var1 `28/100` (`28.0%` [20.1, 37.5]), paired drop `6.0 [-2.0, 14.0]`, exact McNemar `p-val=0.2101` (`b=11`, `c=5`), est. `$4.28` (`131/200` hit `finish_reason="length"` at `max_tokens=8192`: `127/200` inside `reasoning_content` with empty `content`, `4/200` truncated mid-`content`; `22` uncounted `\boxed{}` hits in `reasoning_content`).
- `Kimi K3` | Thinking effort: `default (unset; reasoning active)` | (`37/200` partial, Day-1 STAIR): Orig `25/37` (`67.6%` [51.5, 80.4]), `rc_fallback_extra=2`, est. `$0.39`.
- `DeepSeek V4.1 Flash 1017` | Thinking effort: `default (unset)` | (`1/200` partial, Day-1 STAIR): Orig `0/1` (`0.0%` [0.0, 79.3]), est. `$0.01`.

## Stuck / blocked
- STAIR Day 1 stopped intentionally at `DAILY_CAP_REACHED (239)` (`240` total Day-1 calls on `bm` key); `Kimi K3` (`163` remaining) and `DeepSeek V4.1 Flash 1017` (`199` remaining) resume automatically via LaunchAgent at `00:15 PST` (`11-25-2026` Day 2, `11-26-2026` Day 3).

## Next steps
- Push Day-1 Experiment 03 results (`838/1,200` calls), Light QA fixes, and `AGENTS.md`/`CLAUDE.md`/`.cursor/rules/project.mdc` updates straight to `origin/main`, log to `~/agent-sync/coding/log.md`, and email `brando.science@gmail.com` ONLY (no BCC).
- LaunchAgent completes remaining `362` STAIR calls across Day 2 (`11-25-2026`) and Day 3 (`11-26-2026`), then add `_end_<DDMonYYYY>` suffix when all `1,200/1,200` calls complete.

## Brando to-do
- none

## Log
- 11-24-2026 01:16 PST -- Initialized Experiment 03 folder, manifest (`100` matched pairs), `PROTOCOL.md`, `results.md`, and `CKPT_stair_and_gemini4_eval.md`.
- 11-24-2026 02:47 PST -- Completed STAIR Day-1 batch (`239` logged + `1` test probe = `240` calls; `GLM 5.3` `200/200`, `Kimi K3` `37/200`, `DeepSeek` `1/200`; est. `$4.686198`), armed LaunchAgent `00:15 PST`.
- 11-24-2026 09:35 PST -- Completed all `600/600` local `agy` Gemini 4 calls (`argon-high` `88/77`, `neon-xhigh` `87/77`, `carbon-high` `86/77`; `0` tool violations), compressed raw outputs to `*.jsonl.gz`, and regenerated reports and `README.md`.
- 11-24-2026 09:52 PST -- Completed Tier-2 Light QA (`VERDICT: FIXED` via `agy` `gemini-4-neon-xhigh` `--effort xhigh`), synced updated `run_stair_gateway_eval.py` to `skampere1`, added mandatory `Thinking effort` rule to `AGENTS.md`/`CLAUDE.md`/`.cursor/rules/project.mdc`, and regenerated `README.md`, `results.md`, and `RESULTS_*.md` with explicit `Thinking effort` columns.
- 11-26-2026 01:14 PST -- Daily STAIR batch synced: counts={'glm53': 200, 'kimik3': 200, 'deepseekv41flash': 153}, est_cost=$9.128629, stop_reason=DAILY_CAP_REACHED (240)
