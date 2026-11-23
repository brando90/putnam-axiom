# Protocol: Putnam-AXIOM claude-fable-5-2 (effort max) Original vs Functional Variations (11-23-2026)

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/02_frontier_models_original_vs_variations_nov2026/PROTOCOL.md>

**TLDR:** Frozen pre-run protocol for evaluating single-call `claude-fable-5-2` (`effort=max`, `--safe-mode`, tools disabled) on the 100 matched Putnam-AXIOM Original problems and 100 Snapshot-1 Functional Variations at `$0.00` cash cost after the `11-23-2026 23:00 PST` Claude Ultra quota reset.

Date: 11-23-2026  
As of 11-23-2026 12:37 PST

## 1. Consequential question & decision criterion

- **Question:** Does Anthropic's `claude-fable-5-2` at maximum reasoning effort (`effort=max`) close the Original-versus-Functional-Variations memorization/brittleness gap in a pure single-call large language model (LLM) evaluation (no agent harness, no tools)?
- **Cheapest valid comparison:** Compare the `100` matched Original problems (`set == "orig"` and `matched100 == True` in `data/tasks.jsonl.gz`) against their paired `100` Snapshot-1 Functional Variations (`set == "var"` and `snapshot == 1`, keys `V:000, V:005, ..., V:495`, pairing index `i -> V:{5*i:03d}`), yielding `200` total single-turn LLM calls (`n=100` matched pairs). This matches the `100`-pair scope of `gemini-3.8-flash (snapshot 1)` while preserving personal Claude Ultra weekly Fable allowance (`50%` weekly Fable sub-limit, `58%` total weekly usage as of `11-23-2026 12:20 PST`) for thesis defense work.
- **Decision criterion:** Report accuracy on Original (100), Variation (Snapshot 1, 100), per-question paired drop (points), `10,000`-resample bootstrap 95% confidence interval (`numpy.random.default_rng(0)`), and exact two-sided McNemar `p-val` on discordant pairs $(b, c)$ against the null of zero paired difference.

## 2. Frozen execution specification

- **Model & CLI invocation:** `/Users/brandomiranda/.local/bin/claude` (`2.1.330`), invoked per problem via `code/run_eval.py` (`call_claude_cli`):
  ```text
  claude -p --safe-mode --model claude-fable-5-2 --effort max --tools "" \
    --output-format json --no-session-persistence \
    --system-prompt "You are a helpful assistant."
  ```
- **Why `--safe-mode`:** Disables personal `~/.claude/CLAUDE.md`, hooks (`auto-update-tools.sh`, `refresh-agents-config.sh`, `herdr-agent-state.sh`), skills, plugins, and Model Context Protocol (MCP) servers while keeping first-party `claude.ai` OAuth authentication active, ensuring an uncontaminated single-call LLM evaluation (`--bare` is excluded because it disables OAuth).
- **Prompt & task manifest:** `data/tasks.jsonl.gz` (`--sets orig,var --snapshots 1 --order matched,var1`) + `data/fewshot.json` (`lm-eval-harness` `putnam_axiom` 4-shot prompt, identical to all models in `experiments/02_frontier_models_original_vs_variations_nov2026/`).
- **Execution controls:** `--workers 2`, `--timeout 1800` seconds/problem, `--output-token-budget 2500000` (safety cap on cumulative output tokens), resumable output JSONL inside gitignored `.local/02_fable52_max_schedule_11-23-2026/work/out/fable52max.jsonl`, copied to `data/raw_outputs/fable52max.jsonl.gz` on completion.
- **Schedule & continuation:** Host LaunchAgent `com.brando.putnam-fable52-max` checks Gmail via read-only Internet Message Access Protocol (IMAP) for any external credit updates and gates Claude execution until `>= 11-23-2026 23:01 PST`. Once a 1-task preflight succeeds and confirms `claude-fable-5-2` in `usage.actual_models`, execution proceeds inside detached `tmux` session `cc-putnam-expt02-fable52-max`. If a 5-hour quota window stops the run mid-way, partial `ok=True` rows are preserved and resumed cleanly on the next available window.

## 3. Scoring, denominator & budget rules

- **Paper grader (`code/score.py` + `code/pax_utils.py`):** Last `\boxed{}` answer (falling back to `Final Answer: The final answer is ...`), normalized and compared via SymPy `parse_latex` difference `== 0` (`5s` timeout).
- **Missing/failed tasks (Trigger Rule 61):** Every task in the frozen `200`-task set (`100` matched Originals, `100` Snapshot-1 Variations) stays in the `n=100` denominator (`0` if missing or non-`ok`). Do not mark complete until `200/200` tasks finish or are explicitly verified terminal.
- **Answer-equivalence judge:** Omitted for `fable52max` (`n/a`) unless separately authorized, preserving `$0.00` cash spend and the 6/day Koyejo-lab OpenAI key quota.
- **Budget:** `$0.00` cash spend (personal Claude Ultra subscription on `~/.claude`). Do not auto-spend paid API keys without an explicit approved cap.

## 4. Pre-registered predictions (before running)

- **Format / boxed compliance:** `>= 97%` (`>= 194/200` producing extractable `\boxed{}` answers).
- **Matched 100 Originals (paper grader):** `85.0%` to `93.0%` (above `claude-opus-5-5` `83.0%` and comparable to `gemini-3.8-flash` `87.0%`).
- **Snapshot-1 Functional Variations (paper grader):** `75.0%` to `85.0%`.
- **Per-question paired drop:** `6.0` to `13.0` percentage points (remaining positive and statistically distinguishable from `0` under exact McNemar `p-val < 0.05` if discordant gap matches `9–14` points).
