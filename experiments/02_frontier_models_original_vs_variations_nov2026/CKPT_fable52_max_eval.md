# Checkpoint: Putnam-AXIOM Experiment 02 claude-fable-5-2 (max effort)

Created: 11-23-2026 12:37 PST
Last updated: 11-23-2026 18:08 PST

## Goal
Measure single-call LLM accuracy and matched original-vs-variation drop of `claude-fable-5-2` (`effort=max`, Claude Code `--safe-mode -p --tools ""`) on the 100 matched Originals and 100 Snapshot-1 Functional Variations (`$0.00` cash budget).

## What ran
- Updated `code/run_eval.py` (`--safe-mode`, `--effort`, `actual_models`, immediate quota-limit stop), added `code/compute_paired_bootstrap.py` and `code/scheduled_fable52_max_driver.py`, created `PROTOCOL.md`, `results.md`, and local `.local/02_fable52_max_schedule_11-23-2026/` state.
- Confirmed `claude -p --safe-mode --model claude-fable-5-2 --effort max` flag support on Claude Code `2.1.330` (returned `usage_limit_reached`: resets `11pm (America/Los_Angeles)`).
- Verified `ub9sc` sent STAIR `bm` key follow-up to `zeyu@cs.stanford.edu` at `11-23-2026 12:25 PST` requesting `claude-fable-5-2` (`REQ-13BF3E` / `34398f0964464299bad9`).

## Results
- none yet (200/200 pending launch after `11-23-2026 23:01 PST`).

## Stuck / blocked
- Waiting until `11-23-2026 23:01 PST` for personal Claude Ultra Fable quota reset (`100% used` as of `12:20 PST`); corrected STAIR `bm` key (`34398f0964464299bad9`) request (`+ Claude 5.2-fable`, `$1000 -> $1000/mo`) logged at `17:01 PST` for Sanmi Koyejo's Friday `11-27-2026` review batch.

## Next steps
- Automated LaunchAgent `com.brando.putnam-fable52-max` checks Gmail IMAP every 30 min and launches `tmux` session `cc-putnam-expt02-fable52-max` after `11-23-2026 23:01 PST`:
  `~/uv_envs/no-gold-ref-judge/bin/python3 ~/putnam-axiom/experiments/02_frontier_models_original_vs_variations_nov2026/code/scheduled_fable52_max_driver.py`

## Brando to-do
- Keep MacBook Pro on AC power (with `com.brando.caffeinate-on-ac` active) past `11:00 PM PST`; wait for Friday `11-27-2026` batch review on STAIR `bm` key change (or file a separate spike key only if needed).

## Log
- 11-23-2026 12:37 PST -- Initialized `PROTOCOL.md`, `results.md`, `CKPT_fable52_max_eval.md`, runner `--effort`/`--safe-mode` fixes, paired bootstrap script, and scheduled LaunchAgent driver waiting on `11-23-2026 23:01 PST`.
- 11-23-2026 12:38 PST -- Observed Zeyu Tang `12:29 PST` IMAP reply recommending STAIR key-change form (`https://forms.gle/zhqcWUqdHyjJ4Knq5`) and lower monthly steady-key budget for `34398f0964464299bad9`.
- 11-23-2026 15:06 PST -- Email update observed (Mon, 23 Nov 2026 22:56:28 +0000): from `Zeyu Tang <zeyu@cs.stanford.edu>`, subject `[STAIR API Key] Received: change to bm`. No auto-spend triggered; keeping `$0` Claude Ultra reset schedule primary unless explicit approved API cap is set.
- 11-23-2026 15:06 PST -- Email update observed (Mon, 23 Nov 2026 23:05:08 +0000): from `Zeyu Tang <zeyu@cs.stanford.edu>`, subject `[STAIR API Key] Not Filed: bm already has a change pending`. No auto-spend triggered; keeping `$0` Claude Ultra reset schedule primary unless explicit approved API cap is set.
- 11-23-2026 16:43 PST -- Email update observed (Mon, 23 Nov 2026 19:36:12 -0500): from `Brando Miranda <brandojazz@gmail.com>`, subject `Re: [STAIR API Key] Not Filed: bm already has a change pending`. No auto-spend triggered; keeping `$0` Claude Ultra reset schedule primary unless explicit approved API cap is set.
- 11-23-2026 17:14 PST -- Email update observed (Mon, 23 Nov 2026 16:50:28 -0800): from `Zeyu Tang <zeyu@cs.stanford.edu>`, subject `Re: [STAIR API Key] Not Filed: bm already has a change pending`. No auto-spend triggered; keeping `$0` Claude Ultra reset schedule primary unless explicit approved API cap is set.
- 11-23-2026 17:14 PST -- Email update observed (Tue, 24 Nov 2026 01:01:27 +0000): from `Zeyu Tang <zeyu@cs.stanford.edu>`, subject `[STAIR API Key] Received: change to bm`. No auto-spend triggered; keeping `$0` Claude Ultra reset schedule primary unless explicit approved API cap is set.
