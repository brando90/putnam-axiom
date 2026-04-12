# Claude Code: run `git clone https://github.com/brando90/agents-config.git ~/agents-config 2>/dev/null || git -C ~/agents-config pull 2>/dev/null` to bootstrap/update config.
# Read `~/agents-config/INDEX_RULES.md` for all agent documentation and routing. Local `~/agents-config/` is the fallback if GitHub is unreachable.

# Putnam-AXIOM

## Project Overview
Putnam-AXIOM is a functional and static benchmark for measuring higher-level mathematical reasoning by LLMs, using problems from the William Lowell Putnam Mathematical Competition. The dataset contains 522 problems with solutions (answers in `\boxed{}`).

## Repository Structure
- `data/Putnam_AXIOM_Original_v3.json` — main dataset (522 problems)
- `data/Putnam-AXIOM_Variations/` — variation datasets for robustness testing (v3 and v4)
- `data/scripts_push_2_hf/` — scripts to push data to HuggingFace
- `src/eval.py` — primary evaluation script (VLLM-based)
- `src/api_eval.py` — API-based evaluation (OpenAI, etc.)
- `src/claude_eval.py` — Anthropic Claude evaluation
- `src/deepseek_eval.py` — DeepSeek model evaluation
- `src/hf_eval.py` — HuggingFace transformers evaluation
- `src/lm_harness_eval.py` — LM Evaluation Harness integration
- `src/prompts.py` — prompt templates (general, mistral, llama, gemma)
- `src/util.py` — answer parsing and math simplification (SymPy)
- `src/contamination_ft.py` — fine-tuning with contamination checking
- `src/variations/` — dataset variation generation scripts (per-year generators)
- `src/data_visualization/` — confidence interval plotting

## Build & Install
```bash
pip install -e .
```

## Running Evaluations
```bash
# VLLM-based evaluation (primary)
python putnam-axiom/src/eval.py \
  --data_dir putnam-axiom/data/Putnam_AXIOM_Original_v3.json \
  --model_name meta-llama/Meta-Llama-3-8B \
  --output_dir DIRECTORY_PATH

# Key arguments: --prompt_name (general|mistral|llama|gemma), --temperature, --top_p,
# --max_tokens (default 2048), --stop (default "Problem:"), --repeat_eval (default 5)
```

```bash
# Multi-GPU fine-tuning
torchrun --nproc_per_node=2 --master_port=29500 \
  ./putnam-axiom/src/contamination_ft.py \
  --deepspeed ./putnam-axiom/src/ds_config.json
```

## Key Dependencies
Python 3.10+, VLLM, PyTorch, Transformers, TRL, PEFT, DeepSpeed, SymPy, wandb, Anthropic SDK.

## Conventions
- Answers are wrapped in `\boxed{}` in the dataset
- Model outputs are parsed and normalized via SymPy for comparison
- Evaluation is repeated multiple times (default 5) for statistical robustness
- Prompt templates vary by model family — check `src/prompts.py`
