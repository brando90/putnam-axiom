# Checkpoint: Putnam-AXIOM Experiment 02 claude-fable-5-2 (max effort)

Created: 11-23-2026 12:37 PST
Last updated: 11-24-2026 00:03 PST

## Goal
Measure single-call LLM accuracy and matched original-vs-variation drop of `claude-fable-5-2` (`effort=max`, Claude Code `--safe-mode -p --tools ""`) on the 100 matched Originals and 100 Snapshot-1 Functional Variations (`$0.00` cash budget).

## What ran
- `code/scheduled_fable52_max_driver.py` in `tmux` session `cc-putnam-expt02-fable52-max` (`--sets orig,var --snapshots 1 --order matched,var1`, `100/100` matched Originals, `100/100` Snapshot-1 Variations).

## Results
- COMPLETE (200/200): Original (100) `88.0%`, Variation snapshot 1 `74.0%`, paired drop `14.0` points `[95% CI 8.0, 21.0]` (10,000-resample bootstrap over 100 problems), exact two-sided McNemar `p-val=0.0001221` (`b=14`, `c=0`), API-equivalent `$34.52` (`$0.00` cash).

## Stuck / blocked
- nothing

## Next steps
- [p 5/10] Run optional answer-equivalence judge (gpt-5.5) or snapshots 2-5 if desired.

## Brando to-do
- none

## Log
- 11-23-2026 12:37 PST -- Initialized `PROTOCOL.md`, `results.md`, `CKPT_fable52_max_eval.md`, runner `--effort`/`--safe-mode` fixes, paired bootstrap script, and scheduled LaunchAgent driver waiting on `11-23-2026 23:01 PST`.
- 11-23-2026 12:38 PST -- Observed Zeyu Tang `12:29 PST` IMAP reply recommending STAIR key-change form (`https://forms.gle/zhqcWUqdHyjJ4Knq5`) and lower monthly steady-key budget for `34398f0964464299bad9`.
- 11-23-2026 15:06 PST -- Email update observed (Mon, 23 Nov 2026 22:56:28 +0000): from `Zeyu Tang <zeyu@cs.stanford.edu>`, subject `[STAIR API Key] Received: change to bm`. No auto-spend triggered; keeping `$0` Claude Ultra reset schedule primary unless explicit approved API cap is set.
- 11-23-2026 15:06 PST -- Email update observed (Mon, 23 Nov 2026 23:05:08 +0000): from `Zeyu Tang <zeyu@cs.stanford.edu>`, subject `[STAIR API Key] Not Filed: bm already has a change pending`. No auto-spend triggered; keeping `$0` Claude Ultra reset schedule primary unless explicit approved API cap is set.
- 11-23-2026 16:43 PST -- Email update observed (Mon, 23 Nov 2026 19:36:12 -0500): from `Brando Miranda <brandojazz@gmail.com>`, subject `Re: [STAIR API Key] Not Filed: bm already has a change pending`. No auto-spend triggered; keeping `$0` Claude Ultra reset schedule primary unless explicit approved API cap is set.
- 11-23-2026 17:14 PST -- Email update observed (Mon, 23 Nov 2026 16:50:28 -0800): from `Zeyu Tang <zeyu@cs.stanford.edu>`, subject `Re: [STAIR API Key] Not Filed: bm already has a change pending`. No auto-spend triggered; keeping `$0` Claude Ultra reset schedule primary unless explicit approved API cap is set.
- 11-23-2026 17:14 PST -- Email update observed (Tue, 24 Nov 2026 01:01:27 +0000): from `Zeyu Tang <zeyu@cs.stanford.edu>`, subject `[STAIR API Key] Received: change to bm`. No auto-spend triggered; keeping `$0` Claude Ultra reset schedule primary unless explicit approved API cap is set.
- 11-24-2026 00:03 PST -- COMPLETE (200/200): Orig 88.0%, Var1 74.0%, drop 14.0 [8.0, 21.0] p-val=0.0001221 exact McNemar.
