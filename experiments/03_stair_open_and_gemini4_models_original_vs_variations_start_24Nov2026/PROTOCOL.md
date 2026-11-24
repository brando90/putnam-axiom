# Protocol: STAIR Open Models & Gemini 4 Single-Call Putnam-AXIOM Eval (11-24-2026)

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/PROTOCOL.md>

**TLDR:** Frozen specification for evaluating `GLM 5.3` (substitute after `GLM 5.3 Flash` returned HTTP 400), `Kimi K3`, `DeepSeek V4.1 Flash 1017`, `gemini-4-neon-xhigh`, `gemini-4-argon-high`, and `gemini-4-carbon-high` on the `100` matched Originals and `100` Snapshot-1 Functional Variations (`1,200` total single-call inferences) with SymPy-only grading, daily `240`-call / `$15` STAIR caps, and `>=20%` `agy` weekly quota reserve.

Date: 11-24-2026
As of 11-24-2026 01:44 PST

## 1. Dataset & Matched 100 Problem IDs
- **Source files:** `data/Putnam-AXIOM_Variations_v4/original.json` (`100` matched Originals) and `experiments/02_frontier_models_original_vs_variations_nov2026/data/tasks.jsonl.gz` (`set == "orig", matched100 == True` paired with `set == "var", snapshot == 1`, keys `V:000, V:005, ..., V:495`).
- **Exact manifest:** Stored in [`expt_v1/data/matched100_problem_ids.json`](expt_v1/data/matched100_problem_ids.json) (`200` tasks/model = `100` Originals + `100` Snapshot-1 Variations).
- **Prompt:** Exact `lm-eval-harness` `putnam_axiom` 4-shot prompt (`DESC` + `fewshot.json` + problem) from `experiments/02_frontier_models_original_vs_variations_nov2026/code/run_eval.py`. For `agy`, prefixed with `"Answer directly in a single response with no tool calls, file reads, or shell commands.\n\n"` and invoked inside an empty read-only `chmod 555` directory `/tmp/pax_agy_single_call_empty`.

## 2. Frozen Models, Settings & Quotas

### Track A — STAIR "bm" Gateway Open Models (`600` calls, `skampere1`)
- **Endpoint & key:** `POST https://aiapi-prod.stanford.edu/v1/chat/completions`, reading `/dfs/scratch0/brando9/keys/stanford_stair_bm_gateway_key.txt` into memory at runtime on `skampere1` (never printed, echoed, logged, or copied to Mac).
- **Exact model IDs:** `"GLM 5.3"` (substituting after `"GLM 5.3 Flash"` returned `HTTP 400 Invalid model name` on `/v1/chat/completions` in our `01:19 PST` smoke test despite appearing in `/v1/models`), `"Kimi K3"`, `"DeepSeek V4.1 Flash 1017"`.
- **Inference settings:** `temperature: 0`, `max_tokens: 8192`, no tools, `1` attempt per problem & version (`0` retries), `240s` request timeout.
- **Hard caps:** At most `240` Gateway calls per calendar day across both `~/.local/state/plan-router/stair-bm-spend.jsonl` and this experiment's ledger; conservative upper-bound cost estimator (`$1.00 / 1M` input + `$3.00 / 1M` output) halts and emails `brando.science@gmail.com` (no BCC) if cumulative estimated cost exceeds `$15.00 USD`.
- **Multi-day schedule (`3` days):**
  - Day 1 (`11-24-2026`, `240` calls): `4` smoke calls (`1` HTTP-400 attempt on `GLM 5.3 Flash`, `1` HTTP-200 probe on `GLM 5.3`, `1` Task-1 `Kimi K3`, `1` Task-1 `DeepSeek V4.1 Flash 1017`) + `236` remaining calls (`GLM 5.3` `200/200` complete + `Kimi K3` `37/200`).
  - Day 2 (`11-25-2026`, `240` calls): remaining `163` calls for `Kimi K3` (`200/200` complete) + `77` calls for `DeepSeek V4.1 Flash 1017` (`78/200`).
  - Day 3 (`11-26-2026`, `122` calls): remaining `122` calls for `DeepSeek V4.1 Flash 1017` (`200/200` complete).

### Track B — Local `agy` Single-Call Gemini 4 Models (`600` calls, Mac)
- **Exact model IDs & flags (`/Users/brandomiranda/.local/bin/agy` `1.5.15`):**
  1. `gemini-4-neon-xhigh` (`--effort xhigh`)
  2. `gemini-4-argon-high` (`--effort high`)
  3. `gemini-4-carbon-high` (`--effort high`)
- **Single-call enforcement:** `agy --disable-slash-commands --new-project --model <id> --effort <effort> --output-format json --print-timeout 600s -p <prompt>` inside `/tmp/pax_agy_single_call_empty` (`chmod 555`, `0` files, `permission_mode=request-review`, no `--dangerously-skip-permissions`, no `--add-dir`; `--sandbox` is omitted because it blocked `agy` outbound HTTPS), `1` attempt per problem, asserting `num_turns == 1` (`0` tool turns).
- **Quota reserve:** Check `agy -p /usage` before each model and every `50` calls; stop cleanly if `Gemini Models` Weekly `< 20%` or Five-Hour `< 5%`.

## 3. Grading, Email & Pre-Registered Predictions
- **Grading:** Repo's SymPy paper grader (`pax_utils.py`, `5s` timeout). Missing/timed-out/empty/tool-violating calls stay `0` in the `n=100` denominator (Trigger Rule 61). **No `agy` or LLM equivalence judge**; all strict misses are marked `ungraded`.
- **Notifications:** `RUN START` / `RUN DONE` / stop emails sent **`To: brando.science@gmail.com` ONLY (no BCC)**.
- **Pre-registered predictions (Rule 76):**
  - `agy` Gemini 4 models: `>= 90%` boxed compliance, `0` tool turns; Original (100) `82%–92%`, Variation (Snap 1) `70%–82%`, paired drop `7–15` percentage points (matching `gemini-3.8-flash` `87%` vs `73%`, drop `14.0`).
  - STAIR open models (`GLM 5.3`, `Kimi K3`, `DeepSeek V4.1 Flash 1017`): `>= 80%` boxed compliance within `8192` `max_tokens`; Original (100) `55%–80%`, Variation (Snap 1) `45%–70%`, paired drop `6–14` percentage points.
