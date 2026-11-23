# Execution Commands: Experiment 01 (`expt_v1`)

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/cc.md>

**TLDR:** Reproducible command sequence for `experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/`: (1) Phase 1 local statistical analysis of existing Putnam-AXIOM evaluation datasets, (2) Phase 2 (10 open-weight baseline models across `gpu0`, `gpu5`, `gpu7`, `frontier8b`) and Phase 3 (3-model 10-epoch SFT logic-contamination trajectory) on `skampere1.stanford.edu`, and (3) statistical aggregation and verification.

## 1. Phase 1: Existing-Data Paired Statistical Audit (Local, Zero Compute Spend)

```bash
cd ~/putnam-axiom
python3 experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/analyze_phase1_existing_data.py
```

## 2. Phase 2 & Phase 3: Live Multi-Model TFA/EM Calibration & SFT Logic-Contamination Trajectory on SNAP (`skampere1`)

```bash
# Sync scripts and benchmark JSONs to isolated SNAP experiment workspace
ssh brando9@skampere1.stanford.edu 'mkdir -p /lfs/skampere1/0/brando9/putnam_axiom_expt01/data/Putnam-AXIOM_Variations_v4 /lfs/skampere1/0/brando9/putnam_axiom_expt01/results'
scp ~/putnam-axiom/data/Putnam_AXIOM_Original_v3.json brando9@skampere1.stanford.edu:/lfs/skampere1/0/brando9/putnam_axiom_expt01/data/
scp ~/putnam-axiom/data/Putnam-AXIOM_Variations_v4/original.json ~/putnam-axiom/data/Putnam-AXIOM_Variations_v4/test.json brando9@skampere1.stanford.edu:/lfs/skampere1/0/brando9/putnam_axiom_expt01/data/Putnam-AXIOM_Variations_v4/
scp ~/putnam-axiom/experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/run_snap_tfa_and_sft_contamination.py brando9@skampere1.stanford.edu:/lfs/skampere1/0/brando9/putnam_axiom_expt01/

# Run Phase 2 (10-model baseline evaluation across gpu0, gpu5, gpu7, frontier8b)
# and Phase 3 (3-model SFT trajectories: gemma-2b-it on gpu0, Qwen3-1.7B on gpu5, deepseek-math-7b-instruct on gpu7)
ssh brando9@skampere1.stanford.edu '
  export HF_HOME=/lfs/skampere1/0/brando9/.cache/huggingface
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=0 /lfs/skampere1/0/brando9/vllm_env/bin/python \
    /lfs/skampere1/0/brando9/putnam_axiom_expt01/run_snap_tfa_and_sft_contamination.py \
    --data_root /lfs/skampere1/0/brando9/putnam_axiom_expt01/data \
    --output_dir /lfs/skampere1/0/brando9/putnam_axiom_expt01/results \
    --worker_group gpu0

  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=5 /lfs/skampere1/0/brando9/vllm_env/bin/python \
    /lfs/skampere1/0/brando9/putnam_axiom_expt01/run_snap_tfa_and_sft_contamination.py \
    --data_root /lfs/skampere1/0/brando9/putnam_axiom_expt01/data \
    --output_dir /lfs/skampere1/0/brando9/putnam_axiom_expt01/results \
    --worker_group gpu5

  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=5 /lfs/skampere1/0/brando9/vllm_env/bin/python \
    /lfs/skampere1/0/brando9/putnam_axiom_expt01/run_snap_tfa_and_sft_contamination.py \
    --data_root /lfs/skampere1/0/brando9/putnam_axiom_expt01/data \
    --output_dir /lfs/skampere1/0/brando9/putnam_axiom_expt01/results \
    --worker_group gpu7

  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=0 /lfs/skampere1/0/brando9/vllm_env/bin/python \
    /lfs/skampere1/0/brando9/putnam_axiom_expt01/run_snap_tfa_and_sft_contamination.py \
    --data_root /lfs/skampere1/0/brando9/putnam_axiom_expt01/data \
    --output_dir /lfs/skampere1/0/brando9/putnam_axiom_expt01/results \
    --worker_group frontier8b
'
```

## 3. Aggregate Statistics and Verify Consolidation

```bash
cd ~/putnam-axiom
scp 'brando9@skampere1.stanford.edu:/lfs/skampere1/0/brando9/putnam_axiom_expt01/results/snap_*_per_item.csv' \
    'brando9@skampere1.stanford.edu:/lfs/skampere1/0/brando9/putnam_axiom_expt01/results/snap_*_summaries.json' \
    experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/results/
python3 experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/analyze_phase2_phase3_stats.py
python3 experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/verify_expt01.py
python3 src/scripts/verify_consolidation.py
```

**TLDR-end:** [putnam-axiom: expt01 sft-logic-contamination-tfa] Provides the exact commands to run Phase 1 locally, execute Phase 2 (`gpu0`, `gpu5`, `gpu7`, `frontier8b`) and Phase 3 on `skampere1.stanford.edu` GPUs, sync CSV/JSON outputs, and run both deterministic verification suites under `experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/`.
