# Results Ledger: Putnam-AXIOM Frontier Models (Original vs Functional Variations, Nov 2026)

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/02_frontier_models_original_vs_variations_nov2026/results.md>

Date: 11-23-2026  
Last updated: 11-24-2026 00:03 PST

Authoritative 8-model baseline report: [`RESULTS_frontier_models_original_vs_variations_nov2026.md`](RESULTS_frontier_models_original_vs_variations_nov2026.md) (8 models scored as of `11-20-2026`: `claude-opus-5-5` `78.9%` Original-522 / `83.0%` Matched-100 / `73.6%` Var-500, `claude-sonnet-5-5` `77.4%` / `83.0%` / `71.2%`, `gpt-6-astra` `72.4%` / `82.0%` / `69.4%`, `gpt-6.2-astra` `72.0%` / `81.0%` / `69.0%`, `gpt-5.5` `71.8%` / `80.0%` / `68.6%`, `gemini-3.8-flash` `87.0%` Matched-100 / `73.0%` Var-Snap1, `gpt-4o` `21.3%` / `27.0%` / `23.4%`, `Qwen2-Math-7B-Instruct` `15.3%` / `19.0%` / `16.0%`).

## Scheduled Addition: `claude-fable-5-2` (`effort=max`, single-call LLM)

Protocol: [`PROTOCOL.md`](PROTOCOL.md). Evaluation scope: `200` single-call tasks (`100` matched Originals + `100` Snapshot-1 Functional Variations) using Claude Code `2.1.330` (`-p --safe-mode --model claude-fable-5-2 --effort max --tools "" --no-session-persistence`).

| Model & settings | Status | Original (matched 100) | Variation (snapshot 1) | Paired drop [95% bootstrap CI] | Stats, cost & notes |
|---|---|---|---|---|---|
| `claude-fable-5-2` (`effort=max`, `--safe-mode`) | COMPLETE (200/200) | 100/100 (88.0%) | 100/100 (74.0%) | 14.0 [8.0, 21.0] | exact McNemar `p-val=0.0001221` (`b=14`, `c=0`); `$0.00` cash (~`$34.52` API-eq) |

**TLDR-end:** [putnam-axiom: expt02 fable-5.2-max matched-100 eval] COMPLETE (200/200): Original 88.0%, Snapshot-1 Variation 74.0%, paired drop 14.0 [8.0, 21.0] points (exact McNemar `p-val=0.0001221`).
