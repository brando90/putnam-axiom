#!/usr/bin/env python3
"""Phase 2 & Phase 3 Statistical Aggregation Script (Hard Rule 11 compliant).

Reads snap_gpu{0,5,7}_per_item.csv from expt_v1/results/ and produces:
- phase2_8models_baseline_per_item.csv
- phase2_8models_baseline_summary.csv
- phase3_3models_sft_trajectory_per_item.csv
- phase3_3models_sft_trajectory_summary.csv
- phase2_phase3_statistical_tests.json
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats


OUT_DIR = Path(__file__).resolve().parent / "results"


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


def paired_diff_test(
    x: np.ndarray, y: np.ndarray, n_boot: int = 10000, seed: int = 42
) -> Dict[str, float]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    diff = x - y
    mean_diff, lo, hi = bootstrap_ci_1d(diff, n_boot=n_boot, seed=seed)
    rng = np.random.default_rng(seed)
    n = len(diff)
    obs = abs(np.mean(diff))
    signs = rng.choice([-1.0, 1.0], size=(n_boot, n))
    perm_means = np.abs(np.mean(signs * diff, axis=1))
    p_perm = float((np.sum(perm_means >= obs - 1e-12) + 1) / (n_boot + 1))
    return {
        "n": int(n),
        "mean_diff": round(mean_diff, 6),
        "ci_95_lo": round(lo, 6),
        "ci_95_hi": round(hi, 6),
        "p_val_paired_perm": round(p_perm, 6),
    }


def two_sample_diff_test(
    x: np.ndarray, y: np.ndarray, n_boot: int = 10000, seed: int = 42
) -> Dict[str, float]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    rng = np.random.default_rng(seed)
    mean_diff = float(np.mean(x) - np.mean(y))
    ix = rng.integers(0, len(x), size=(n_boot, len(x)))
    iy = rng.integers(0, len(y), size=(n_boot, len(y)))
    boot_diffs = np.mean(x[ix], axis=1) - np.mean(y[iy], axis=1)
    lo = float(np.percentile(boot_diffs, 2.5))
    hi = float(np.percentile(boot_diffs, 97.5))

    combined = np.concatenate([x, y])
    nx = len(x)
    obs = abs(mean_diff)
    perm_diffs = []
    for _ in range(n_boot):
        p = rng.permutation(combined)
        perm_diffs.append(abs(np.mean(p[:nx]) - np.mean(p[nx:])))
    p_perm = float((np.sum(np.array(perm_diffs) >= obs - 1e-12) + 1) / (n_boot + 1))
    return {
        "nx": int(len(x)),
        "ny": int(len(y)),
        "mean_diff": round(mean_diff, 6),
        "ci_95_lo": round(lo, 6),
        "ci_95_hi": round(hi, 6),
        "p_val_perm": round(p_perm, 6),
    }


def correlation_and_bias(
    x: np.ndarray, y: np.ndarray, n_boot: int = 4000, seed: int = 42
) -> Dict:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    rng = np.random.default_rng(seed)

    r_val, r_p = stats.pearsonr(x, y) if np.std(x) > 0 and np.std(y) > 0 else (0.0, 1.0)
    rho_val, rho_p = stats.spearmanr(x, y) if np.std(x) > 0 and np.std(y) > 0 else (0.0, 1.0)
    tau_val, tau_p = stats.kendalltau(x, y) if np.std(x) > 0 and np.std(y) > 0 else (0.0, 1.0)

    boot_r, boot_rho, boot_tau = [], [], []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        bx, by = x[idx], y[idx]
        if np.std(bx) > 0 and np.std(by) > 0:
            boot_r.append(stats.pearsonr(bx, by)[0])
            boot_rho.append(stats.spearmanr(bx, by)[0])
            boot_tau.append(stats.kendalltau(bx, by)[0])

    def ci(arr):
        if not arr:
            return [0.0, 0.0]
        return [round(float(np.percentile(arr, 2.5)), 4), round(float(np.percentile(arr, 97.5)), 4)]

    bias_stats = paired_diff_test(x, y, n_boot=n_boot, seed=seed)
    return {
        "n": int(n),
        "pearson_r": round(float(r_val), 4),
        "pearson_r_ci": ci(boot_r),
        "pearson_p": float(r_p),
        "spearman_rho": round(float(rho_val), 4),
        "spearman_rho_ci": ci(boot_rho),
        "spearman_p": float(rho_p),
        "kendall_tau": round(float(tau_val), 4),
        "kendall_tau_ci": ci(boot_tau),
        "kendall_p": float(tau_p),
        "mean_bias_x_minus_y": bias_stats["mean_diff"],
        "mean_bias_ci_95": [bias_stats["ci_95_lo"], bias_stats["ci_95_hi"]],
        "mean_bias_p_val": bias_stats["p_val_paired_perm"],
    }


def main() -> None:
    all_rows = []
    for wg in ["gpu0", "gpu5", "gpu7"]:
        f = OUT_DIR / f"snap_{wg}_per_item.csv"
        if f.exists():
            with open(f) as fp:
                all_rows.extend(list(csv.DictReader(fp)))

    if not all_rows:
        raise RuntimeError("No snap_gpu*_per_item.csv files found in results/")

    p2_rows = [r for r in all_rows if r["phase"] == "phase2_baseline"]
    p3_rows = [r for r in all_rows if r["phase"] == "phase3_sft_trajectory"]

    with open(OUT_DIR / "phase2_8models_baseline_per_item.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(p2_rows[0].keys()))
        w.writeheader()
        w.writerows(p2_rows)

    with open(OUT_DIR / "phase3_3models_sft_trajectory_per_item.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(p3_rows[0].keys()))
        w.writeheader()
        w.writerows(p3_rows)

    # --- Summarize Phase 2 (8 models x splits) ---
    p2_models = sorted(set(r["model"] for r in p2_rows))
    p2_summary_rows = []
    p2_model_vectors = {sp: {"em": [], "tfa_sol": [], "tfa_box": [], "tfce_sol": []} for sp in ["orig_contaminated", "func_variations_v1", "orig_unseen_control"]}
    p2_paired_gaps = {}

    for m in p2_models:
        m_splits = {}
        for sp in ["orig_contaminated", "func_variations_v1", "orig_unseen_control", "func_variations_all5"]:
            sub = [r for r in p2_rows if r["model"] == m and r["split"] == sp]
            if not sub:
                continue
            # Sort by problem_id, variation_id for deterministic pairing
            sub.sort(key=lambda r: (r["problem_id"], r["variation_id"]))
            tfa_sol = np.array([float(r["tfa_sol"]) for r in sub])
            tfa_box = np.array([float(r["tfa_box"]) for r in sub])
            tfce_sol = np.array([float(r["tfce_sol"]) for r in sub])

            if sp == "func_variations_all5":
                # Cluster-average by problem_id (100 clusters x 5 variations) before bootstrap
                by_pid: Dict[str, List[Dict]] = {}
                for r in sub:
                    by_pid.setdefault(r["problem_id"], []).append(r)
                pids = sorted(by_pid.keys())
                tfa_sol_c = np.array([np.mean([float(x["tfa_sol"]) for x in by_pid[p]]) for p in pids])
                tfa_box_c = np.array([np.mean([float(x["tfa_box"]) for x in by_pid[p]]) for p in pids])
                tfce_sol_c = np.array([np.mean([float(x["tfce_sol"]) for x in by_pid[p]]) for p in pids])
                ts_m, ts_lo, ts_hi = bootstrap_ci_1d(tfa_sol_c)
                tb_m, tb_lo, tb_hi = bootstrap_ci_1d(tfa_box_c)
                tc_m, tc_lo, tc_hi = bootstrap_ci_1d(tfce_sol_c)
                m_splits[sp] = {"tfa_sol": tfa_sol_c, "tfa_box": tfa_box_c, "tfce_sol": tfce_sol_c}
                p2_summary_rows.append(
                    {
                        "model": m,
                        "split": sp,
                        "n_items": len(sub),
                        "n_clusters": len(pids),
                        "em_count": -1,
                        "em_mean": -1.0,
                        "em_ci_lo": -1.0,
                        "em_ci_hi": -1.0,
                        "tfa_sol_mean": round(ts_m, 4),
                        "tfa_sol_ci_lo": round(ts_lo, 4),
                        "tfa_sol_ci_hi": round(ts_hi, 4),
                        "tfa_box_mean": round(tb_m, 4),
                        "tfa_box_ci_lo": round(tb_lo, 4),
                        "tfa_box_ci_hi": round(tb_hi, 4),
                        "tfce_sol_mean": round(tc_m, 4),
                        "tfce_sol_ci_lo": round(tc_lo, 4),
                        "tfce_sol_ci_hi": round(tc_hi, 4),
                    }
                )
            else:
                em = np.array([float(r["em"]) for r in sub])
                em_m, em_lo, em_hi = bootstrap_ci_1d(em)
                ts_m, ts_lo, ts_hi = bootstrap_ci_1d(tfa_sol)
                tb_m, tb_lo, tb_hi = bootstrap_ci_1d(tfa_box)
                tc_m, tc_lo, tc_hi = bootstrap_ci_1d(tfce_sol)
                m_splits[sp] = {"em": em, "tfa_sol": tfa_sol, "tfa_box": tfa_box, "tfce_sol": tfce_sol}
                p2_model_vectors[sp]["em"].append(em_m)
                p2_model_vectors[sp]["tfa_sol"].append(ts_m)
                p2_model_vectors[sp]["tfa_box"].append(tb_m)
                p2_model_vectors[sp]["tfce_sol"].append(tc_m)
                p2_summary_rows.append(
                    {
                        "model": m,
                        "split": sp,
                        "n_items": len(sub),
                        "n_clusters": len(sub),
                        "em_count": int(np.sum(em)),
                        "em_mean": round(em_m, 4),
                        "em_ci_lo": round(em_lo, 4),
                        "em_ci_hi": round(em_hi, 4),
                        "tfa_sol_mean": round(ts_m, 4),
                        "tfa_sol_ci_lo": round(ts_lo, 4),
                        "tfa_sol_ci_hi": round(ts_hi, 4),
                        "tfa_box_mean": round(tb_m, 4),
                        "tfa_box_ci_lo": round(tb_lo, 4),
                        "tfa_box_ci_hi": round(tb_hi, 4),
                        "tfce_sol_mean": round(tc_m, 4),
                        "tfce_sol_ci_lo": round(tc_lo, 4),
                        "tfce_sol_ci_hi": round(tc_hi, 4),
                    }
                )

        if "orig_contaminated" in m_splits and "func_variations_v1" in m_splits:
            p2_paired_gaps[m] = {
                "em_orig_minus_var1": paired_diff_test(m_splits["orig_contaminated"]["em"], m_splits["func_variations_v1"]["em"]),
                "tfa_sol_orig_minus_var1": paired_diff_test(m_splits["orig_contaminated"]["tfa_sol"], m_splits["func_variations_v1"]["tfa_sol"]),
                "tfa_box_orig_minus_var1": paired_diff_test(m_splits["orig_contaminated"]["tfa_box"], m_splits["func_variations_v1"]["tfa_box"]),
                "tfa_sol_orig_minus_var5": paired_diff_test(m_splits["orig_contaminated"]["tfa_sol"], m_splits["func_variations_all5"]["tfa_sol"]),
            }

    with open(OUT_DIR / "phase2_8models_baseline_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(p2_summary_rows[0].keys()))
        w.writeheader()
        w.writerows(p2_summary_rows)

    # Cross-model correlations between TFA and EM across the 8 baseline models
    p2_cross_model_corr = {}
    for sp in ["orig_contaminated", "func_variations_v1", "orig_unseen_control"]:
        vecs = p2_model_vectors[sp]
        p2_cross_model_corr[sp] = {
            "tfa_sol_vs_em": correlation_and_bias(np.array(vecs["tfa_sol"]), np.array(vecs["em"])),
            "tfa_box_vs_em": correlation_and_bias(np.array(vecs["tfa_box"]), np.array(vecs["em"])),
            "neg_tfce_vs_em": correlation_and_bias(-np.array(vecs["tfce_sol"]), np.array(vecs["em"])),
        }

    # Pooled across all 8 models x 3 splits = 24 model-split cells
    pooled_em = np.concatenate([np.array(p2_model_vectors[sp]["em"]) for sp in ["orig_contaminated", "func_variations_v1", "orig_unseen_control"]])
    pooled_tfa_sol = np.concatenate([np.array(p2_model_vectors[sp]["tfa_sol"]) for sp in ["orig_contaminated", "func_variations_v1", "orig_unseen_control"]])
    pooled_tfa_box = np.concatenate([np.array(p2_model_vectors[sp]["tfa_box"]) for sp in ["orig_contaminated", "func_variations_v1", "orig_unseen_control"]])
    p2_cross_model_corr["pooled_24_cells"] = {
        "tfa_sol_vs_em": correlation_and_bias(pooled_tfa_sol, pooled_em),
        "tfa_box_vs_em": correlation_and_bias(pooled_tfa_box, pooled_em),
    }

    # --- Summarize Phase 3 (3 models x 5 epochs x splits) ---
    p3_models = sorted(set(r["model"] for r in p3_rows))
    p3_summary_rows = []
    p3_hypothesis_tests = {}

    for m in p3_models:
        epochs = sorted(set(int(r["epoch"]) for r in p3_rows if r["model"] == m))
        ep_data: Dict[int, Dict[str, Dict[str, np.ndarray]]] = {}

        for ep in epochs:
            ep_data[ep] = {}
            for sp in ["orig_contaminated", "func_variations_v1", "orig_unseen_control", "func_variations_all5"]:
                sub = [r for r in p3_rows if r["model"] == m and int(r["epoch"]) == ep and r["split"] == sp]
                if not sub:
                    continue
                sub.sort(key=lambda r: (r["problem_id"], r["variation_id"]))
                if sp == "func_variations_all5":
                    by_pid = {}
                    for r in sub:
                        by_pid.setdefault(r["problem_id"], []).append(r)
                    pids = sorted(by_pid.keys())
                    tfa_sol_c = np.array([np.mean([float(x["tfa_sol"]) for x in by_pid[p]]) for p in pids])
                    tfa_box_c = np.array([np.mean([float(x["tfa_box"]) for x in by_pid[p]]) for p in pids])
                    tfce_sol_c = np.array([np.mean([float(x["tfce_sol"]) for x in by_pid[p]]) for p in pids])
                    ts_m, ts_lo, ts_hi = bootstrap_ci_1d(tfa_sol_c)
                    tb_m, tb_lo, tb_hi = bootstrap_ci_1d(tfa_box_c)
                    tc_m, tc_lo, tc_hi = bootstrap_ci_1d(tfce_sol_c)
                    ep_data[ep][sp] = {"tfa_sol": tfa_sol_c, "tfa_box": tfa_box_c, "tfce_sol": tfce_sol_c}
                    p3_summary_rows.append(
                        {
                            "model": m,
                            "epoch": ep,
                            "split": sp,
                            "n_items": len(sub),
                            "n_clusters": len(pids),
                            "em_count": -1,
                            "em_mean": -1.0,
                            "em_ci_lo": -1.0,
                            "em_ci_hi": -1.0,
                            "tfa_sol_mean": round(ts_m, 4),
                            "tfa_sol_ci_lo": round(ts_lo, 4),
                            "tfa_sol_ci_hi": round(ts_hi, 4),
                            "tfa_box_mean": round(tb_m, 4),
                            "tfa_box_ci_lo": round(tb_lo, 4),
                            "tfa_box_ci_hi": round(tb_hi, 4),
                            "tfce_sol_mean": round(tc_m, 4),
                            "tfce_sol_ci_lo": round(tc_lo, 4),
                            "tfce_sol_ci_hi": round(tc_hi, 4),
                        }
                    )
                else:
                    em = np.array([float(r["em"]) for r in sub])
                    tfa_sol = np.array([float(r["tfa_sol"]) for r in sub])
                    tfa_box = np.array([float(r["tfa_box"]) for r in sub])
                    tfce_sol = np.array([float(r["tfce_sol"]) for r in sub])
                    em_m, em_lo, em_hi = bootstrap_ci_1d(em)
                    ts_m, ts_lo, ts_hi = bootstrap_ci_1d(tfa_sol)
                    tb_m, tb_lo, tb_hi = bootstrap_ci_1d(tfa_box)
                    tc_m, tc_lo, tc_hi = bootstrap_ci_1d(tfce_sol)
                    ep_data[ep][sp] = {"em": em, "tfa_sol": tfa_sol, "tfa_box": tfa_box, "tfce_sol": tfce_sol}
                    p3_summary_rows.append(
                        {
                            "model": m,
                            "epoch": ep,
                            "split": sp,
                            "n_items": len(sub),
                            "n_clusters": len(sub),
                            "em_count": int(np.sum(em)),
                            "em_mean": round(em_m, 4),
                            "em_ci_lo": round(em_lo, 4),
                            "em_ci_hi": round(em_hi, 4),
                            "tfa_sol_mean": round(ts_m, 4),
                            "tfa_sol_ci_lo": round(ts_lo, 4),
                            "tfa_sol_ci_hi": round(ts_hi, 4),
                            "tfa_box_mean": round(tb_m, 4),
                            "tfa_box_ci_lo": round(tb_lo, 4),
                            "tfa_box_ci_hi": round(tb_hi, 4),
                            "tfce_sol_mean": round(tc_m, 4),
                            "tfce_sol_ci_lo": round(tc_lo, 4),
                            "tfce_sol_ci_hi": round(tc_hi, 4),
                        }
                    )

        # Compute H1 & H2 tests comparing final epoch (10) vs baseline (0)
        if 0 in ep_data and 10 in ep_data:
            d_orig_em = ep_data[10]["orig_contaminated"]["em"] - ep_data[0]["orig_contaminated"]["em"]
            d_var1_em = ep_data[10]["func_variations_v1"]["em"] - ep_data[0]["func_variations_v1"]["em"]
            d_unseen_em = ep_data[10]["orig_unseen_control"]["em"] - ep_data[0]["orig_unseen_control"]["em"]

            d_orig_tfa = ep_data[10]["orig_contaminated"]["tfa_sol"] - ep_data[0]["orig_contaminated"]["tfa_sol"]
            d_var1_tfa = ep_data[10]["func_variations_v1"]["tfa_sol"] - ep_data[0]["func_variations_v1"]["tfa_sol"]
            d_var5_tfa = ep_data[10]["func_variations_all5"]["tfa_sol"] - ep_data[0]["func_variations_all5"]["tfa_sol"]
            d_unseen_tfa = ep_data[10]["orig_unseen_control"]["tfa_sol"] - ep_data[0]["orig_unseen_control"]["tfa_sol"]

            d_orig_box = ep_data[10]["orig_contaminated"]["tfa_box"] - ep_data[0]["orig_contaminated"]["tfa_box"]
            d_var1_box = ep_data[10]["func_variations_v1"]["tfa_box"] - ep_data[0]["func_variations_v1"]["tfa_box"]
            d_unseen_box = ep_data[10]["orig_unseen_control"]["tfa_box"] - ep_data[0]["orig_unseen_control"]["tfa_box"]

            p3_hypothesis_tests[m] = {
                "gain_ep10_minus_ep0": {
                    "orig_contaminated_em": paired_diff_test(ep_data[10]["orig_contaminated"]["em"], ep_data[0]["orig_contaminated"]["em"]),
                    "func_variations_v1_em": paired_diff_test(ep_data[10]["func_variations_v1"]["em"], ep_data[0]["func_variations_v1"]["em"]),
                    "orig_unseen_control_em": paired_diff_test(ep_data[10]["orig_unseen_control"]["em"], ep_data[0]["orig_unseen_control"]["em"]),
                    "orig_contaminated_tfa_sol": paired_diff_test(ep_data[10]["orig_contaminated"]["tfa_sol"], ep_data[0]["orig_contaminated"]["tfa_sol"]),
                    "func_variations_v1_tfa_sol": paired_diff_test(ep_data[10]["func_variations_v1"]["tfa_sol"], ep_data[0]["func_variations_v1"]["tfa_sol"]),
                    "func_variations_all5_tfa_sol": paired_diff_test(ep_data[10]["func_variations_all5"]["tfa_sol"], ep_data[0]["func_variations_all5"]["tfa_sol"]),
                    "orig_unseen_control_tfa_sol": paired_diff_test(ep_data[10]["orig_unseen_control"]["tfa_sol"], ep_data[0]["orig_unseen_control"]["tfa_sol"]),
                    "orig_contaminated_tfa_box": paired_diff_test(ep_data[10]["orig_contaminated"]["tfa_box"], ep_data[0]["orig_contaminated"]["tfa_box"]),
                    "func_variations_v1_tfa_box": paired_diff_test(ep_data[10]["func_variations_v1"]["tfa_box"], ep_data[0]["func_variations_v1"]["tfa_box"]),
                    "orig_unseen_control_tfa_box": paired_diff_test(ep_data[10]["orig_unseen_control"]["tfa_box"], ep_data[0]["orig_unseen_control"]["tfa_box"]),
                },
                "memorization_gap_orig_gain_minus_var_gain": {
                    "em_var1": paired_diff_test(d_orig_em, d_var1_em),
                    "tfa_sol_var1": paired_diff_test(d_orig_tfa, d_var1_tfa),
                    "tfa_sol_var5": paired_diff_test(d_orig_tfa, d_var5_tfa),
                    "tfa_box_var1": paired_diff_test(d_orig_box, d_var1_box),
                },
                "net_logic_contamination_var_gain_minus_unseen_gain": {
                    "em_var1_vs_unseen": two_sample_diff_test(d_var1_em, d_unseen_em),
                    "tfa_sol_var1_vs_unseen": two_sample_diff_test(d_var1_tfa, d_unseen_tfa),
                    "tfa_sol_var5_vs_unseen": two_sample_diff_test(d_var5_tfa, d_unseen_tfa),
                    "tfa_box_var1_vs_unseen": two_sample_diff_test(d_var1_box, d_unseen_box),
                },
            }

    with open(OUT_DIR / "phase3_3models_sft_trajectory_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(p3_summary_rows[0].keys()))
        w.writeheader()
        w.writerows(p3_summary_rows)

    # Also compute trajectory-level correlation between TFA and EM across the 15 Phase-3 checkpoints x 3 splits = 45 cells
    p3_45_cells = [r for r in p3_summary_rows if r["split"] != "func_variations_all5"]
    p3_em_vec = np.array([float(r["em_mean"]) for r in p3_45_cells])
    p3_tfa_sol_vec = np.array([float(r["tfa_sol_mean"]) for r in p3_45_cells])
    p3_tfa_box_vec = np.array([float(r["tfa_box_mean"]) for r in p3_45_cells])
    p3_traj_corr = {
        "n_cells": len(p3_45_cells),
        "tfa_sol_vs_em": correlation_and_bias(p3_tfa_sol_vec, p3_em_vec),
        "tfa_box_vs_em": correlation_and_bias(p3_tfa_box_vec, p3_em_vec),
    }

    full_stats = {
        "phase2_paired_gaps_by_model": p2_paired_gaps,
        "phase2_cross_model_correlations": p2_cross_model_corr,
        "phase3_sft_hypothesis_tests": p3_hypothesis_tests,
        "phase3_trajectory_45cells_correlations": p3_traj_corr,
    }
    (OUT_DIR / "phase2_phase3_statistical_tests.json").write_text(json.dumps(full_stats, indent=2))
    print("PHASE 2 & PHASE 3 STATISTICAL AGGREGATION COMPLETE.")


if __name__ == "__main__":
    main()
