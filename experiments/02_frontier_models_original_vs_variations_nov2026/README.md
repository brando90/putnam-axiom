# 02: Frontier models on Putnam-AXIOM Original and Functional Variations (no agent), Nov 2026

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/02_frontier_models_original_vs_variations_nov2026/README.md>

**TLDR:** Plain one-turn runs (no tools, no agent) of Claude Opus 5.5, Claude Sonnet 5.5, gpt-6.2-astra, gpt-6-astra, gpt-5.5, Gemini 3.8 Flash, plus GPT-4o and Qwen2-Math-7B-Instruct as pipeline checks against the paper (arXiv 2508.08292). Results, tables and caveats: [`RESULTS_frontier_models_original_vs_variations_nov2026.md`](RESULTS_frontier_models_original_vs_variations_nov2026.md).

## Status

`PARTIAL` (11-23-2026): all 8 initial rows done except Gemini 3.8 Flash (100 matched originals and variation snapshot 1 only). Claude Opus 5.5 is complete (522 originals, 500 variation problems) after the 8:30 limit reset, and the one Claude Sonnet 5.5 problem that hung is rerun (500 variation problems). Scheduled `claude-fable-5-2` (`effort=max`, single-call `--safe-mode -p --tools ""`) on matched 100 Originals + Snapshot-1 Variations (`200` tasks) via LaunchAgent after the `11-23-2026 23:00 PST` reset ([`PROTOCOL.md`](PROTOCOL.md), [`results.md`](results.md), [`CKPT_fable52_max_eval.md`](CKPT_fable52_max_eval.md)). Not run: Fable 5.1 (usage credits or an API gateway key needed), "Claude 6.2" (no such model).

## Layout

- `code/`: runner (`run_eval.py`, resumable), grader (`score.py` with `pax_utils.py`, a copy of `tasks/putnam_axiom/utils.py`), judge (`prep_judge.py`, `judge_run.py`), Qwen generator, report builders.
- `data/raw_outputs/`: one gzipped JSONL per model (every model output, token usage, seconds).
- `data/scored/`: per-problem scores. `data/judge_in/`, `data/judge_out_gpt/`: equivalence-judge items and gpt-5.5 verdicts.
- `data/models.json`, `data/results.json`, `data/tables.md`: aggregated results.

## Resume the unfinished row

Run from a directory with `tasks.jsonl` (`gunzip data/tasks.jsonl.gz`) and `fewshot.json`; the runner skips finished problems.

```text
python3 code/run_eval.py --provider gemini --model gemini-3.8-flash --effort high --key-file <key file> --out out/gem38flash.jsonl --workers 1
```

Score with `PYTHONPATH=stubs python3 code/score.py out/<model>.jsonl --json scored_<model>.json` (put `datasets_stub.py` in `stubs/` as `datasets.py`), then `prep_judge.py`, `judge_run.py`, `build_report.py`, `make_report.py`. No API keys are stored in this folder.
