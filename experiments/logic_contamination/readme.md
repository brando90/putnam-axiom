# Logic Contamination

Goal: Demonstrate there is little logic contamination
How: Train in the original Putnam-AXIOM 53 examples, and show the changes the accuracy by very little
Reason: I've observed similar result when training on the MATH test so I'd assume it generalizes to a harder benchmark.

## Train on Putnam-AXIOM 53 to learn the original logic

```bash
conda activate putnam_axiom

# [Optional] HF authentication
# export HF_TOKEN=$(cat ~/keys/master_hf_token.txt)
# huggingface-cli login --token "$HF_TOKEN"

# Train on the original Putnam-AXIOM 53 Benchmark
export CUDA_VISIBLE_DEVICES=5
time python ~/putnam-axiom/src/train/sft_simple.py --mode 'online' --num_train_epochs 100
```

## Run the lm-harness eval
See our [quickstart](../../README.md) to run lm-harness evals on Putnam-AXIOM (any split).