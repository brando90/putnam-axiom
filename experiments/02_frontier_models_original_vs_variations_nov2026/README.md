# 02: Frontier models on Putnam-AXIOM Original and Functional Variations (no agent), Nov 2026

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/02_frontier_models_original_vs_variations_nov2026/README.md>

**TLDR:** Plain one-turn runs (no tools, no agent) of Claude Opus 5.5, Claude Sonnet 5.5, gpt-6.2-astra, gpt-6-astra, gpt-5.5, Gemini 3.8 Flash, plus GPT-4o and Qwen2-Math-7B-Instruct as pipeline checks against the paper (arXiv 2508.08292). Results, tables and caveats: [`RESULTS_frontier_models_original_vs_variations_nov2026.md`](RESULTS_frontier_models_original_vs_variations_nov2026.md).

## Status

`PARTIAL` (11-20-2026): all rows done except Claude Opus 5.5 (346 of 500 variation problems, 521 of 522 originals; stopped by the Claude Code 5-hour limit, resets 8:30) and Gemini 3.8 Flash (100 matched originals and variation snapshot 1 only). Not run: Fable 5.2, Fable 5.1 (usage credits or an API gateway key needed), "Claude 6.2" (no such model).

## Layout

- `code/`: runner (`run_eval.py`, resumable), grader (`score.py` with `pax_utils.py`, a copy of `tasks/putnam_axiom/utils.py`), judge (`prep_judge.py`, `judge_run.py`), Qwen generator, report builders.
- `data/raw_outputs/`: one gzipped JSONL per model (every model output, token usage, seconds).
- `data/scored/`: per-problem scores. `data/judge_in/`, `data/judge_out_gpt/`: equivalence-judge items and gpt-5.5 verdicts.
- `data/models.json`, `data/results.json`, `data/tables.md`: aggregated results.

## Resume the unfinished rows

Run from a directory with `tasks.jsonl` (`gunzip data/tasks.jsonl.gz`) and `fewshot.json`; the runner skips finished problems.

```text
python3 code/run_eval.py --provider claude_cli --model claude-opus-5-5 --key-file <claude launcher> --out out/opus55.jsonl --workers 8 --timeout 600
python3 code/run_eval.py --provider gemini --model gemini-3.8-flash --effort high --key-file <key file> --out out/gem38flash.jsonl --workers 1
```

Score with `PYTHONPATH=stubs python3 code/score.py out/<model>.jsonl --json scored_<model>.json` (put `datasets_stub.py` in `stubs/` as `datasets.py`), then `prep_judge.py`, `judge_run.py`, `build_report.py`, `make_report.py`. No API keys are stored in this folder.
