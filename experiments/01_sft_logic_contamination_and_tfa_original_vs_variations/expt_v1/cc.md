# Execution Commands: Experiment 01 (`expt_v1`)

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/cc.md>

**TLDR-start:** Reproducible command sequence for `experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/`: (1) Phase 1 local statistical analysis of existing Putnam-AXIOM evaluation datasets, (2) Phase 2 & Phase 3 GPU execution on `skampere1.stanford.edu` (8-model baseline TFA/EM calibration and 3-model 10-epoch SFT logic-contamination trajectory), and (3) statistical aggregation and verification.

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

# Run Phase 2 (8-model baseline evaluation) and Phase 3 (3-model SFT trajectory) across free GPUs 0 and 5
ssh brando9@skampere1.stanford.edu '
  export HF_HOME=/lfs/skampere1/0/brando9/.cache/huggingface
  CUDA_VISIBLE_DEVICES=0 /lfs/skampere1/0/brando9/vllm_env/bin/python /lfs/skampere1/0/brando9/putnam_axiom_expt01/run_snap_tfa_and_sft_contamination.py \
    --data_root /lfs/skampere1/0/brando9/putnam_axiom_expt01/data \
    --output_dir /lfs/skampere1/0/brando9/putnam_axiom_expt01/results \
    --worker_group gpu0
'
```

## 3. Aggregate Statistics and Verify Consolidation

```bash
cd ~/putnam-axiom
scp 'brando9@skampere1.stanford.edu:/lfs/skampere1/0/brando9/putnam_axiom_expt01/results/*.csv' 'brando9@skampere1.stanford.edu:/lfs/skampere1/0/brando9/putnam_axiom_expt01/results/*.json' experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/results/
python3 experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/analyze_phase2_phase3_stats.py
python3 src/scripts/verify_consolidation.py
```

**TLDR-end:** Provides the exact commands to run Phase 1 locally, execute Phase 2 and Phase 3 on `skampere1.stanford.edu` GPUs, sync CSV/JSON outputs, and verify repository consolidation under `experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/`.
