# Protocol: Experiment 01 — SFT Logic Contamination and Teacher-Forced Accuracy (TFA) on Putnam-AXIOM Original vs. Functional Variations

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/PROTOCOL.md>

**TLDR:** Frozen experimental protocol for `experiments/01_sft_logic_contamination_and_tfa_original_vs_variations/expt_v1/`, specifying the input manifest, SHA-256 hashes, open-weight model identifiers, prompt templates, scoring rules, checkpoint evaluation grid, and statistical plan before any compute execution.

- **Locked timestamp:** `10-16-2026 18:18 PDT`
- **Version:** `expt_v1`
- **API Spend Budget:** `$0.00` (all evaluations and supervised fine-tuning runs use open-weight models on Stanford Network Analysis Project [SNAP] GPU node `skampere1.stanford.edu` plus local deterministic analysis of committed repository outputs).

## 1. Input Manifest and SHA-256 Hashes

| Dataset / Input Artifact | Relative Path | Count | SHA-256 | Role |
|---|---|---:|---|---|
| Putnam-AXIOM Original v3 (`full_eval`) | `data/Putnam_AXIOM_Original_v3.json` | 522 problems | `b763cba941864a53557d603634dd519f2f9edb9eda342fe9cf4826b67da3d00b` | Source for `orig_unseen_control` ($N=100$ seed-42 sample from the 422 non-variation originals) |
| Putnam-AXIOM Variations v4 Originals (`orig_contaminated`) | `data/Putnam-AXIOM_Variations_v4/original.json` | 100 problems | `71f5cb5e29d1d8c92e8400ac1a31b64c52a2db486cc7bb2fe92dcb4c77805ef1` | Direct SFT contamination training set ($N=100$) and `orig_contaminated` evaluation split |
| Putnam-AXIOM Variations v4 Test (`func_variations`) | `data/Putnam-AXIOM_Variations_v4/test.json` | 500 variations (100 clusters $\times$ 5) | `76c46b3626a8e8c4f09ad3431dc3add7a1e4a4a467064226ebfc0fe957dae96f` | Paired Functional Variations evaluation split (`func_variations_v1` [$N=100$, `variation == "1"`] and `func_variations_all5` [$N=500$]) |
| Baseline Fine-Tuning Original Outputs (`DeepSeek-R1-Distill-Qwen-14B`) | `src/model_output/baseline/finetuning_output_original.json` | 100 problems | `7a597156c6be2216d274f789d4463c0cb819159557b76187d2b214dbcd01b119` | Phase 1 paired per-problem contamination audit (Original split) |
| Baseline Fine-Tuning Variation Outputs (`DeepSeek-R1-Distill-Qwen-14B`) | `src/model_output/baseline/finetuning_output_variation.json` | 100 problems | `86cc2898b08b84fdd07e5c16a6543c2ceabb456d6a2c6e6b79ddda51a8824b1f` | Phase 1 paired per-problem contamination audit (Variation split) |
| Published 20-Model Summary Scores | `src/data_visualization/interval_gen.py` | 20 models $\times$ 2 splits | `0047319fd5365e31e686121b43f7794224700a8ec56d383fd076ea2f4e65ae5c` | Phase 1 20-model Original vs. Variation benchmark audit |
| 12-Model $\times$ 5-Run MATH Evals | `src/model_evals/test/*/run0..run4.json` | 12 models $\times$ 5 runs $\times$ 5,000 items | Verified by `paper_latex_and_notes/consolidation/manifest.json` | Phase 1 multi-seed stochastic generation variance audit |

## 2. Models and Evaluation / Training Grid

### Phase 2: Baseline Multi-Model TFA vs. EM Calibration Grid (8 Cached Open-Weight Models)
All 8 models are loaded locally in `bfloat16` from `/lfs/skampere1/0/brando9/.cache/huggingface/hub/` on `skampere1.stanford.edu`:
1. `google/gemma-2b`
2. `google/gemma-2b-it`
3. `Qwen/Qwen3-1.7B-Base`
4. `Qwen/Qwen3-1.7B`
5. `Qwen/Qwen3-4B`
6. `deepseek-ai/deepseek-math-7b-base`
7. `deepseek-ai/deepseek-math-7b-instruct`
8. `deepseek-ai/deepseek-math-7b-rl`

Each model is evaluated on:
- `orig_contaminated` ($N=100$ problems from `data/Putnam-AXIOM_Variations_v4/original.json`)
- `func_variations_v1` ($N=100$ paired `variation == "1"` problems from `data/Putnam-AXIOM_Variations_v4/test.json`) and `func_variations_all5` ($N=500$ all 5 variations per problem for teacher-forced metrics)
- `orig_unseen_control` ($N=100$ deterministic `random.Random(42)` sample from the 422 problems in `data/Putnam_AXIOM_Original_v3.json` not in `original.json`)

### Phase 3: Controlled SFT Logic-Contamination Trajectory Grid (3 Models $\times$ 5 Checkpoints $\times$ 3 Splits)
Three models spanning distinct families and parameter scales are fine-tuned directly on `orig_contaminated` ($N=100$ problems in `data/Putnam-AXIOM_Variations_v4/original.json`):
1. `google/gemma-2b-it` (full parameter SFT in `bfloat16`, learning rate `2e-5`, AdamW, batch size `10`, 10 steps/epoch, 10 epochs = 100 steps)
2. `Qwen/Qwen3-1.7B` (full parameter SFT in `bfloat16`, learning rate `2e-5`, AdamW, batch size `10`, 10 steps/epoch, 10 epochs = 100 steps)
3. `deepseek-ai/deepseek-math-7b-instruct` (full parameter SFT in `bfloat16` with gradient checkpointing, learning rate `1e-5`, AdamW, batch size `10`, 10 steps/epoch, 10 epochs = 100 steps)

Checkpoints evaluated for each model: **Epoch 0 (Pre-SFT Baseline), Epoch 1, Epoch 3, Epoch 5, Epoch 10** (5 checkpoints $\times$ 3 models = 15 model states).

## 3. Prompt Format and Supervision Masking

To avoid the historical EOS/padding bug in `src/contamination_ft.py`, every example uses a canonical prompt-completion split:
- **Prompt prefix (`prompt_text`):**
  ```text
  Given a mathematics question, compose a detailed solution. Simplify your answer as much as possible and place the final answer inside \boxed{answer}.

  Problem:
  {problem}

  Solution:
  ```
- **Target completion (`target_text`):**
  ```text
  {solution}<eos>
  ```
- **Supervised Fine-Tuning Loss Masking:** Prompt tokens have `labels = -100`; only `target_text` tokens (including the single trailing `<eos>` token, up to `max_seq_length = 1024`) contribute to cross-entropy training loss. Padding tokens beyond `<eos>` have `labels = -100` and `attention_mask = 0`.

## 4. Scoring Metrics (Deterministic)

1. **Boxed-Answer Exact Match ($\text{EM}$):**
   - Greedy decoding (`do_sample=False`, `max_new_tokens=512`, stopping at `<eos>` or `\nProblem:`).
   - Extracted via `last_boxed_only_string` $\to$ `remove_boxed` $\to$ `normalize_final_answer` (with fallback regex `Final Answer: The final answer is ...`), compared against normalized ground-truth answer via string equality or SymPy `parse_latex` algebraic equivalence (`is_equiv` with 2-second timeout).
2. **Solution Teacher-Forced Accuracy ($\text{TFA}_{\text{sol}}$):**
   - Given tokenized `prompt_ids + target_ids`, run a single forward pass (`torch.no_grad()`). For each target token position $t \in \{1, \dots, |T|\}$, check whether $\arg\max_v \text{logits}_{t-1, v} = \text{target\_id}_t$. $\text{TFA}_{\text{sol}}$ is the per-problem mean accuracy over all target solution tokens.
3. **Boxed-Final-Answer Token Teacher-Forced Accuracy ($\text{TFA}_{\text{box}}$):**
   - Teacher-forced token accuracy restricted to the token span corresponding to `\boxed{answer}` in the gold solution.
4. **Solution Teacher-Forced Cross-Entropy ($\text{TFCE}_{\text{sol}}$):**
   - Per-problem mean negative log-likelihood (in nats/token) over all target solution tokens.

## 5. Statistical Reporting Plan (Hard Rule 11)

- All means/proportions reported with **95% bootstrap confidence intervals** ($B=10{,}000$ resamples, seed `42`), explicitly naming the resampling unit (`100 paired problem clusters`, `20 models`, or `12 models`).
- Paired comparisons (`Original vs. Variation`, `Epoch 10 vs. Epoch 0`, `Memorization Gap` $\Delta_{\text{mem}}$, `Logic Contamination` $\Delta_{\text{logic}}$) report **two-sided paired permutation / bootstrap p-values** and **exact McNemar p-values** for binary paired outcomes.
- Metric-to-metric comparisons ($\text{TFA}_{\text{sol}}$ vs. $\text{EM}$, $\text{TFA}_{\text{box}}$ vs. $\text{EM}$, Original vs. Variation across models) report **Pearson $r$, Spearman $\rho$, Kendall $\tau$** (never collapsed to a summary) and **mean bias** $\mathbb{E}[X - Y]$ with 95% bootstrap CIs and p-values.
- All failures, timeouts, or unparsed outputs remain in the full denominator ($N=100$ or $N=500$).
