#!/usr/bin/env python3
"""Phase 1: Deterministic Statistical Audit of Existing Putnam-AXIOM Evaluation Datasets.

Analyzes:
1. 20-Model Original vs. Functional Variation Benchmark Gap (src/data_visualization/interval_gen.py)
2. 100-Problem Paired Per-Item Contamination Outputs for DeepSeek-R1-Distill-Qwen-14B
   (src/model_output/baseline/finetuning_output_original.json vs. finetuning_output_variation.json)
3. 12-Model x 5-Run Multi-Seed Variance Audit (src/model_evals/test/*/run0..run4.json)
4. Dataset Structural & Solution-Length Profile across Original (522), Variation-Originals (100),
   Functional Variations (500), and Unseen Original Control (100).
"""

from __future__ import annotations

import csv
import glob
import json
import math
import os
from pathlib import Path
import random
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parent / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def bootstrap_ci_1d(
    values: np.ndarray, n_boot: int = 10000, seed: int = 42, alpha: float = 0.05
) -> Tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    vals = np.asarray(values, dtype=float)
    mean_val = float(np.mean(vals))
    idx = rng.integers(0, len(vals), size=(n_boot, len(vals)))
    boot_means = np.mean(vals[idx], axis=1)
    lo = float(np.percentile(boot_means, 100 * (alpha / 2)))
    hi = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
    return mean_val, lo, hi


def paired_bootstrap_diff_and_pval(
    x: np.ndarray, y: np.ndarray, n_boot: int = 10000, seed: int = 42
) -> Dict[str, float]:
    """Computes paired difference x - y, 95% bootstrap CI, paired permutation p-value, and correlations."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    diff = x - y
    mean_diff, lo, hi = bootstrap_ci_1d(diff, n_boot=n_boot, seed=seed)

    # Exact or Monte Carlo paired sign-flip permutation test against H0: mean(x - y) == 0
    rng = np.random.default_rng(seed)
    n = len(diff)
    obs = abs(np.mean(diff))
    if n <= 16:
        # Exact 2^n sign flips
        signs = np.array(np.meshgrid(*[[-1, 1]] * n)).T.reshape(-1, n)
        perm_means = np.abs(np.mean(signs * diff, axis=1))
        p_perm = float(np.mean(perm_means >= obs - 1e-12))
    else:
        signs = rng.choice([-1.0, 1.0], size=(n_boot, n))
        perm_means = np.abs(np.mean(signs * diff, axis=1))
        p_perm = float((np.sum(perm_means >= obs - 1e-12) + 1) / (n_boot + 1))

    # Correlations with bootstrap CIs
    r_val, r_p = stats.pearsonr(x, y) if np.std(x) > 0 and np.std(y) > 0 else (0.0, 1.0)
    rho_val, rho_p = stats.spearmanr(x, y) if np.std(x) > 0 and np.std(y) > 0 else (0.0, 1.0)
    tau_val, tau_p = stats.kendalltau(x, y) if np.std(x) > 0 and np.std(y) > 0 else (0.0, 1.0)

    boot_r, boot_rho, boot_tau = [], [], []
    for _ in range(2000):
        b_idx = rng.integers(0, n, size=n)
        bx, by = x[b_idx], y[b_idx]
        if np.std(bx) > 0 and np.std(by) > 0:
            boot_r.append(stats.pearsonr(bx, by)[0])
            boot_rho.append(stats.spearmanr(bx, by)[0])
            boot_tau.append(stats.kendalltau(bx, by)[0])

    def ci_arr(arr: List[float]) -> Tuple[float, float]:
        if not arr:
            return (0.0, 0.0)
        return float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))

    r_lo, r_hi = ci_arr(boot_r)
    rho_lo, rho_hi = ci_arr(boot_rho)
    tau_lo, tau_hi = ci_arr(boot_tau)

    return {
        "n": int(n),
        "mean_x": float(np.mean(x)),
        "mean_y": float(np.mean(y)),
        "mean_bias_x_minus_y": mean_diff,
        "ci_95_lo": lo,
        "ci_95_hi": hi,
        "p_val_paired_perm": p_perm,
        "pearson_r": float(r_val),
        "pearson_r_ci": [r_lo, r_hi],
        "pearson_p": float(r_p),
        "spearman_rho": float(rho_val),
        "spearman_rho_ci": [rho_lo, rho_hi],
        "spearman_p": float(rho_p),
        "kendall_tau": float(tau_val),
        "kendall_tau_ci": [tau_lo, tau_hi],
        "kendall_p": float(tau_p),
    }


def analyze_20_models_gap() -> Dict:
    # Scores from src/data_visualization/interval_gen.py: [variation_pct, original_pct]
    scores = {
        "OpenAI o1 Preview": [43.2, 50.61],
        "Chat GPT 4o": [22.0, 30.0],
        "Claude-3.5-Sonnet": [27.0, 28.0],
        "DeepSeek-R1-Distill-Llama-70B": [20.0, 26.0],
        "DeepSeek-R1-Distill-Qwen-32B": [24.0, 33.0],
        "DeepSeek-R1-Distill-Qwen-7B": [12.0, 23.0],
        "DeepSeek-R1-Distill-Llama-8B": [7.0, 19.0],
        "Llama-3.1-70B": [6.0, 11.0],
        "Mistral-Codestral-22B-v0.1": [9.0, 16.0],
        "Meta-Llama-3.1-8B": [7.0, 6.0],
        "Meta-Llama-3.1-8B-Instruct": [7.0, 10.0],
        "Mistral-7B-v0.1": [6.9, 7.1],
        "Mistral-7B-Instruct-v0.1": [2.0, 8.0],
        "Google-Gemma-7b": [6.0, 7.0],
        "Google-Gemma-2b": [3.0, 5.0],
        "Deepseek-math-7b-base": [6.0, 10.0],
        "Deepseek-math-7b-rl": [10.0, 12.0],
        "Deepseek-math-7b-instruct": [11.0, 12.0],
        "Qwen2-math-7b": [8.9, 9.1],
        "Qwen2-math-7b-instruct": [14.0, 18.0],
    }

    rows = []
    orig_arr = []
    var_arr = []
    for model, (var_pct, orig_pct) in scores.items():
        drop_pp = orig_pct - var_pct
        rel_drop_pct = (drop_pp / orig_pct * 100.0) if orig_pct > 0 else 0.0
        rows.append(
            {
                "model": model,
                "original_em_pct": orig_pct,
                "variation_em_pct": var_pct,
                "contamination_gap_orig_minus_var_pp": round(drop_pp, 4),
                "relative_drop_pct": round(rel_drop_pct, 2),
            }
        )
        orig_arr.append(orig_pct)
        var_arr.append(var_pct)

    csv_path = OUT_DIR / "phase1_20models_original_vs_variation.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    orig_np = np.array(orig_arr)
    var_np = np.array(var_arr)
    orig_mean, orig_lo, orig_hi = bootstrap_ci_1d(orig_np)
    var_mean, var_lo, var_hi = bootstrap_ci_1d(var_np)
    paired_stats = paired_bootstrap_diff_and_pval(orig_np, var_np)
    n_models_dropping = int(np.sum(orig_np > var_np))
    binom_p = float(stats.binomtest(n_models_dropping, len(orig_np), 0.5, alternative="two-sided").pvalue)

    return {
        "n_models": len(orig_np),
        "resampling_unit": "models (N=20)",
        "original_mean_pct": orig_mean,
        "original_ci_95": [orig_lo, orig_hi],
        "variation_mean_pct": var_mean,
        "variation_ci_95": [var_lo, var_hi],
        "models_with_positive_drop": f"{n_models_dropping}/{len(orig_np)}",
        "sign_test_binom_p": binom_p,
        "paired_orig_vs_var": paired_stats,
    }


def analyze_qwen14b_paired_100() -> Dict:
    orig_522 = {x["id"]: x for x in json.load(open(ROOT / "data/Putnam_AXIOM_Original_v3.json"))}
    orig_100 = json.load(open(ROOT / "data/Putnam-AXIOM_Variations_v4/original.json"))
    var_500 = json.load(open(ROOT / "data/Putnam-AXIOM_Variations_v4/test.json"))
    var1_by_id = {f"{x['year']}_{x['id']}": x for x in var_500 if str(x.get("variation")) == "1"}

    ft_orig = json.load(open(ROOT / "src/model_output/baseline/finetuning_output_original.json"))
    ft_var = json.load(open(ROOT / "src/model_output/baseline/finetuning_output_variation.json"))

    rows = []
    orig_acc = []
    var_acc = []
    orig_len = []
    var_len = []

    topic_Buckets: Dict[str, List[Tuple[int, int]]] = {}

    for o_item, v_item, meta_o in zip(ft_orig, ft_var, orig_100):
        pid = o_item["id"]
        assert pid == v_item["id"] == f"{meta_o['year']}_{meta_o['id']}"
        oa = int(o_item["accuracy"]["exact_match"])
        va = int(v_item["accuracy"]["exact_match"])
        orig_acc.append(oa)
        var_acc.append(va)
        olen = len(o_item.get("output", ""))
        vlen = len(v_item.get("output", ""))
        orig_len.append(olen)
        var_len.append(vlen)

        full_meta = orig_522.get(pid, {})
        prob_type = full_meta.get("type", var1_by_id.get(pid, {}).get("type", "Unknown")).strip()
        ans_type = meta_o.get("answer_type", "Unknown").strip()
        topic_Buckets.setdefault(prob_type, []).append((oa, va))

        rows.append(
            {
                "problem_id": pid,
                "year": meta_o["year"],
                "topic": prob_type,
                "answer_type": ans_type,
                "orig_exact_match": oa,
                "var_exact_match": va,
                "diff_orig_minus_var": oa - va,
                "orig_output_chars": olen,
                "var_output_chars": vlen,
                "gold_solution_chars": len(meta_o.get("solution", "")),
            }
        )

    csv_path = OUT_DIR / "phase1_qwen14b_paired_100problems.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    topic_rows = []
    for topic, pairs in sorted(topic_Buckets.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        o_vals = np.array([p[0] for p in pairs], dtype=float)
        v_vals = np.array([p[1] for p in pairs], dtype=float)
        topic_rows.append(
            {
                "topic": topic,
                "n_problems": len(pairs),
                "orig_em_count": int(np.sum(o_vals)),
                "orig_em_rate": round(float(np.mean(o_vals)), 4),
                "var_em_count": int(np.sum(v_vals)),
                "var_em_rate": round(float(np.mean(v_vals)), 4),
                "gap_orig_minus_var": round(float(np.mean(o_vals - v_vals)), 4),
            }
        )

    topic_csv = OUT_DIR / "phase1_qwen14b_by_topic.csv"
    with open(topic_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(topic_rows[0].keys()))
        writer.writeheader()
        writer.writerows(topic_rows)

    orig_np = np.array(orig_acc, dtype=float)
    var_np = np.array(var_acc, dtype=float)
    o_mean, o_lo, o_hi = bootstrap_ci_1d(orig_np)
    v_mean, v_lo, v_hi = bootstrap_ci_1d(var_np)
    paired = paired_bootstrap_diff_and_pval(orig_np, var_np)

    # 2x2 contingency table:
    # b11: both correct, b10: orig correct & var wrong, b01: orig wrong & var correct, b00: both wrong
    b11 = int(np.sum((orig_np == 1) & (var_np == 1)))
    b10 = int(np.sum((orig_np == 1) & (var_np == 0)))
    b01 = int(np.sum((orig_np == 0) & (var_np == 1)))
    b00 = int(np.sum((orig_np == 0) & (var_np == 0)))
    mcnemar_p = float(stats.binomtest(b10, b10 + b01, 0.5, alternative="two-sided").pvalue) if (b10 + b01) > 0 else 1.0

    return {
        "n_paired_problems": len(orig_np),
        "resampling_unit": "paired problem clusters (N=100)",
        "orig_em": {"count": int(np.sum(orig_np)), "mean": o_mean, "ci_95": [o_lo, o_hi]},
        "var_em": {"count": int(np.sum(var_np)), "mean": v_mean, "ci_95": [v_lo, v_hi]},
        "contingency_2x2": {
            "both_correct_11": b11,
            "orig_only_correct_10": b10,
            "var_only_correct_01": b01,
            "both_wrong_00": b00,
            "exact_mcnemar_p": mcnemar_p,
        },
        "paired_orig_vs_var": paired,
    }


def analyze_12_models_5runs_math() -> Dict:
    rows = []
    for mdir in sorted(glob.glob(str(ROOT / "src/model_evals/test/*"))):
        mname = os.path.basename(mdir)
        if mname == "Meta-Llama-3.1-70B":
            continue
        runs = sorted(glob.glob(os.path.join(mdir, "*.json")))
        accs = []
        for r in runs:
            d = json.load(open(r))
            accs.append(float(d["results"]["hendrycks_math"]["exact_match,none"]))
        arr = np.array(accs, dtype=float)
        mean_val, lo, hi = bootstrap_ci_1d(arr, n_boot=5000, seed=42)
        rows.append(
            {
                "model": mname,
                "n_runs": len(arr),
                "n_items_per_run": 5000,
                "mean_em": round(mean_val, 6),
                "std_across_runs": round(float(np.std(arr, ddof=1)), 6),
                "ci_95_lo": round(lo, 6),
                "ci_95_hi": round(hi, 6),
                "run0_em": round(float(arr[0]), 6),
                "run1_em": round(float(arr[1]), 6),
                "run2_em": round(float(arr[2]), 6),
                "run3_em": round(float(arr[3]), 6),
                "run4_em": round(float(arr[4]), 6),
            }
        )

    csv_path = OUT_DIR / "phase1_12models_5runs_math_variance.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return {"n_models": len(rows), "models": rows}


def main() -> None:
    res_20 = analyze_20_models_gap()
    res_qwen14b = analyze_qwen14b_paired_100()
    res_12m = analyze_12_models_5runs_math()

    summary = {
        "phase1_20_models_benchmark_gap": res_20,
        "phase1_qwen14b_paired_100_audit": res_qwen14b,
        "phase1_12_models_5runs_variance": res_12m,
    }
    out_json = OUT_DIR / "phase1_summary_stats.json"
    out_json.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary["phase1_20_models_benchmark_gap"], indent=2))
    print(json.dumps(summary["phase1_qwen14b_paired_100_audit"], indent=2))


if __name__ == "__main__":
    main()
