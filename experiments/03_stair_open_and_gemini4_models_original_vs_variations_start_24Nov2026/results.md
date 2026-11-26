# Results Ledger: STAIR Open Models & Antigravity CLI Gemini 4 Models (`11-24-2026`)

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/results.md>

Date: 11-24-2026
Last updated: 11-26-2026 01:14 PST

Protocol: [`PROTOCOL.md`](PROTOCOL.md). Detailed report: [`RESULTS_stair_open_and_gemini4_original_vs_variations_11-24-2026.md`](expt_v1/results/RESULTS_stair_open_and_gemini4_original_vs_variations_11-24-2026.md). Matched `100` problem IDs: [`expt_v1/data/matched100_problem_ids.json`](expt_v1/data/matched100_problem_ids.json).

## Live Per-Model Summary (`100` Matched Originals vs Snapshot-1 Functional Variations, SymPy Paper Grader, Ungraded for LLM Judge)

| Model | Thinking effort | Harness & Route | Date | Calls (Orig/Var) | Orig (100) | Var (Snap 1) | Paired drop [95% CI] | McNemar p-val | Tokens / Est. Cost | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `gemini-4-neon-xhigh` | xhigh (`--effort xhigh`, extra-high) | single-call agy 1.5.15 (`permission_mode=request-review`, `num_turns=1`); Antigravity CLI (`agy`) personal subscription on Mac | 24Nov2026 | 100/100 | 87/100 (87.0% [79.0, 92.2]) | 77/100 (77.0% [67.8, 84.2]) | 10.0 [3.0, 18.0] | exact McNemar `p-val=0.02127` (`b=13`, `c=3`) | 1244161 in / 2965324 out / `$0.00` (sub) | `COMPLETE (200/200; 191 ok, 9 timeouts)` |
| `gemini-4-argon-high` | high (`--effort high`) | single-call agy 1.5.15 (`permission_mode=request-review`, `num_turns=1`); Antigravity CLI (`agy`) personal subscription on Mac | 24Nov2026 | 100/100 | 88/100 (88.0% [80.2, 93.0]) | 77/100 (77.0% [67.8, 84.2]) | 11.0 [5.0, 18.0] | exact McNemar `p-val=0.003418` (`b=12`, `c=1`) | 2485950 in / 779970 out / `$0.00` (sub) | `COMPLETE (200/200; 197 ok, 3 timeouts)` |
| `gemini-4-carbon-high` | high (`--effort high`) | single-call agy 1.5.15 (`permission_mode=request-review`, `num_turns=1`); Antigravity CLI (`agy`) personal subscription on Mac | 24Nov2026 | 100/100 | 86/100 (86.0% [77.9, 91.5]) | 77/100 (77.0% [67.8, 84.2]) | 9.0 [2.0, 16.0] | exact McNemar `p-val=0.02246` (`b=11`, `c=2`) | 1460414 in / 2768242 out / `$0.00` (sub) | `COMPLETE (200/200; 189 ok, 11 timeouts)` |
| `GLM 5.3` | default (unset; reasoning active) | STAIR Gateway OpenAI chat API (`temp=0`, `max_tokens=8192`, 0 retries); STAIR `bm` Gateway (`https://aiapi-prod.stanford.edu/v1`) on `skampere1` | 24Nov2026 | 100/100 | 34/100 (34.0% [25.5, 43.7]) | 28/100 (28.0% [20.1, 37.5]) | 6.0 [-2.0, 14.0] | exact McNemar `p-val=0.2101` (`b=11`, `c=5`) | 323731 in / 1318904 out / `$4.28` est.; rc_fallback_extra=22 | `COMPLETE (200/200)` |
| `Kimi K3` | default (unset; reasoning active) | STAIR Gateway OpenAI chat API (`temp=0`, `max_tokens=8192`, 0 retries); STAIR `bm` Gateway (`https://aiapi-prod.stanford.edu/v1`) on `skampere1` | 26Nov2026 | 100/100 | 67/100 (67.0% [57.3, 75.4]) | 57/100 (57.0% [47.2, 66.3]) | 10.0 [2.0, 18.0] | exact McNemar `p-val=0.03088` (`b=14`, `c=4`) | 312500 in / 788941 out / `$2.68` est.; rc_fallback_extra=6 | `COMPLETE (200/200)` |
| `DeepSeek V4.1 Flash 1017` | default (unset) | STAIR Gateway OpenAI chat API (`temp=0`, `max_tokens=8192`, 0 retries); STAIR `bm` Gateway (`https://aiapi-prod.stanford.edu/v1`) on `skampere1` | 26Nov2026 | 100/53 | 65/100 (65.0% [55.3, 73.6]) | 30/53 (56.6% [43.3, 69.0]) | pending (<200) | pending (<200) | 238441 in / 643474 out / `$2.17` est.; rc_fallback_extra=4 | `PARTIAL (100/100 orig, 53/100 var1)` |

**TLDR-end:** [putnam-axiom: expt03 stair-open & gemini4 eval] Updated live SymPy paper-grader results as of `11-26-2026 01:14 PST`; completed `200/200` models are propagated to root `README.md` with thinking effort, harness and `DDMonYYYY` dates.
