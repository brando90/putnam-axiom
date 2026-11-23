#!/usr/bin/env python3
"""Phase 2 & Phase 3 Statistical Aggregation Script (Hard Rule 11 compliant).

Reads snap_{gpu0,gpu5,gpu7,frontier8b}_per_item.csv from expt_v1/results/ and produces:
- phase2_10models_baseline_per_item.csv
- phase2_10models_baseline_summary.csv
- phase3_3models_sft_trajectory_per_item.csv
- phase3_3models_sft_trajectory_summary.csv
- phase2_phase3_by_topic_summary.csv
- phase2_phase3_statistical_tests.json
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats


from analyze_phase1_existing_data import (
    _bootstrap_correlations,
    _paired_perm_pval,
    _write_csv,
    bootstrap_ci_1d,
)


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parent / "results"
PRIMARY_SPLITS = ("orig_contaminated", "func_variations_v1", "orig_unseen_control")
ALL_SPLITS = PRIMARY_SPLITS + ("func_variations_all5",)
CANONICAL_DOMAINS = (
    "Number Theory",
    "Geometry",
    "Calculus",
    "Analysis",
    "Combinatorics",
    "Algebra",
    "Linear Algebra",
    "Probability",
)


def _is_binary(arr: np.ndarray) -> bool:
    """Returns True if every finite entry is 0 or 1."""
    return set(np.unique(arr)).issubset({0.0, 1.0})


def paired_diff_test(
    x: np.ndarray, y: np.ndarray, n_boot: int = 10000, seed: int = 42
) -> Dict:
    """Computes paired difference x - y, bootstrap 95% CI, permutation p-value, and McNemar p for binary data."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    diff = x - y
    mean_diff, lo, hi = bootstrap_ci_1d(diff, n_boot=n_boot, seed=seed)
    rng = np.random.default_rng(seed)
    n = len(diff)
    p_perm = _paired_perm_pval(diff, n_boot, rng)
    method = f"exact_sign_flip_2^{n}" if n <= 16 else f"monte_carlo_sign_flip_{n_boot}"

    out: Dict = {
        "n": int(n),
        "mean_x": round(float(np.mean(x)), 6),
        "mean_y": round(float(np.mean(y)), 6),
        "mean_diff": round(mean_diff, 6),
        "ci_95_lo": round(lo, 6),
        "ci_95_hi": round(hi, 6),
        "p_val_paired_perm": round(p_perm, 6),
        "p_val_method": method,
    }
    if _is_binary(x) and _is_binary(y):
        b10 = int(np.sum((x == 1.0) & (y == 0.0)))
        b01 = int(np.sum((x == 0.0) & (y == 1.0)))
        out["exact_mcnemar_b10"] = b10
        out["exact_mcnemar_b01"] = b01
        out["exact_mcnemar_p"] = (
            float(stats.binomtest(b10, b10 + b01, 0.5, alternative="two-sided").pvalue) if (b10 + b01) > 0 else 1.0
        )
    return out


def two_sample_diff_test(
    x: np.ndarray, y: np.ndarray, n_boot: int = 10000, seed: int = 42
) -> Dict:
    """Computes independent two-sample difference mean(x) - mean(y) with bootstrap CI and permutation p-value."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    rng = np.random.default_rng(seed)
    mean_diff = float(np.mean(x) - np.mean(y))
    ix = rng.integers(0, len(x), size=(n_boot, len(x)))
    iy = rng.integers(0, len(y), size=(n_boot, len(y)))
    boot_diffs = np.mean(x[ix], axis=1) - np.mean(y[iy], axis=1)
    combined = np.concatenate([x, y])
    nx, obs = len(x), abs(mean_diff)
    perm_diffs = np.array([abs(np.mean(p[:nx]) - np.mean(p[nx:])) for p in (rng.permutation(combined) for _ in range(n_boot))])
    p_perm = float((np.sum(perm_diffs >= obs - 1e-12) + 1) / (n_boot + 1))
    return {
        "nx": int(len(x)),
        "ny": int(len(y)),
        "mean_x": round(float(np.mean(x)), 6),
        "mean_y": round(float(np.mean(y)), 6),
        "mean_diff": round(mean_diff, 6),
        "ci_95_lo": round(float(np.percentile(boot_diffs, 2.5)), 6),
        "ci_95_hi": round(float(np.percentile(boot_diffs, 97.5)), 6),
        "p_val_perm": round(p_perm, 6),
        "p_val_method": f"monte_carlo_two_sample_perm_{n_boot}",
    }


def correlation_and_bias(
    x: np.ndarray, y: np.ndarray, n_boot: int = 10000, seed: int = 42, include_bias: bool = True
) -> Dict:
    """Computes Pearson r, Spearman rho, Kendall tau (with bootstrap 95% CIs) and optional mean bias."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    rng = np.random.default_rng(seed)
    valid = np.std(x) > 0 and np.std(y) > 0
    r_val, r_p = stats.pearsonr(x, y) if valid else (0.0, 1.0)
    rho_val, rho_p = stats.spearmanr(x, y) if valid else (0.0, 1.0)
    tau_val, tau_p = stats.kendalltau(x, y) if valid else (0.0, 1.0)
    cis = _bootstrap_correlations(x, y, rng, n_corr_boot=n_boot)

    out: Dict = {
        "n": int(len(x)),
        "mean_x": round(float(np.mean(x)), 6),
        "mean_y": round(float(np.mean(y)), 6),
        "pearson_r": round(float(r_val), 4),
        "pearson_r_ci": [round(v, 4) for v in cis["r"]],
        "pearson_p": float(r_p),
        "spearman_rho": round(float(rho_val), 4),
        "spearman_rho_ci": [round(v, 4) for v in cis["rho"]],
        "spearman_p": float(rho_p),
        "kendall_tau": round(float(tau_val), 4),
        "kendall_tau_ci": [round(v, 4) for v in cis["tau"]],
        "kendall_p": float(tau_p),
    }
    if include_bias:
        bias = paired_diff_test(x, y, n_boot=n_boot, seed=seed)
        out["mean_bias_x_minus_y"] = bias["mean_diff"]
        out["mean_bias_ci_95"] = [bias["ci_95_lo"], bias["ci_95_hi"]]
        out["mean_bias_p_val"] = bias["p_val_paired_perm"]
        out["mean_bias_p_method"] = bias["p_val_method"]
    else:
        out["mean_bias_note"] = "omitted (incommensurable units: nats vs proportion)"
    return out


def _cluster_var5(sub: List[Dict]) -> Dict[str, np.ndarray]:
    """Averages 5 functional variations per problem_id into N=100 independent problem clusters."""
    by_pid: Dict[str, List[Dict]] = {}
    for r in sub:
        by_pid.setdefault(r["problem_id"], []).append(r)
    pids = sorted(by_pid.keys())
    return {
        "tfa_sol": np.array([np.mean([float(x["tfa_sol"]) for x in by_pid[p]]) for p in pids]),
        "tfa_box": np.array([np.mean([float(x["tfa_box"]) for x in by_pid[p]]) for p in pids]),
        "tfce_sol": np.array([np.mean([float(x["tfce_sol"]) for x in by_pid[p]]) for p in pids]),
    }


def _extract_col(sub: List[Dict], key: str) -> np.ndarray:
    """Extracts one float column from a list of CSV row dicts."""
    return np.array([float(r[key]) for r in sub])


def _group_by(rows: List[Dict], keys: Tuple[str, ...]) -> Dict[Tuple, List[Dict]]:
    """Groups row dicts deterministically by a tuple of column names."""
    grouped: Dict[Tuple, List[Dict]] = {}
    for r in rows:
        k = tuple(int(r[c]) if c == "epoch" else r[c] for c in keys)
        grouped.setdefault(k, []).append(r)
    return grouped


def _summarize_split(model: str, split: str, sub: List[Dict], epoch: int | None = None) -> Tuple[Dict, Dict[str, np.ndarray]]:
    """Computes bootstrap summary row and underlying paired vectors for one model/split slice."""
    sub.sort(key=lambda r: (r["problem_id"], r["variation_id"]))
    is_var5 = split == "func_variations_all5"
    vecs = _cluster_var5(sub) if is_var5 else {k: _extract_col(sub, k) for k in ("em", "tfa_sol", "tfa_box", "tfce_sol")}
    ts_m, ts_lo, ts_hi = bootstrap_ci_1d(vecs["tfa_sol"])
    tb_m, tb_lo, tb_hi = bootstrap_ci_1d(vecs["tfa_box"])
    tc_m, tc_lo, tc_hi = bootstrap_ci_1d(vecs["tfce_sol"])
    em_m, em_lo, em_hi = (-1.0, -1.0, -1.0) if is_var5 else bootstrap_ci_1d(vecs["em"])

    row: Dict = {"model": model}
    if epoch is not None:
        row["epoch"] = epoch
    row.update({
        "split": split, "n_items": len(sub), "n_clusters": len(vecs["tfa_sol"]),
        "em_count": -1 if is_var5 else int(np.sum(vecs["em"])),
        "em_mean": -1.0 if is_var5 else round(em_m, 4),
        "em_ci_lo": -1.0 if is_var5 else round(em_lo, 4),
        "em_ci_hi": -1.0 if is_var5 else round(em_hi, 4),
        "tfa_sol_mean": round(ts_m, 4), "tfa_sol_ci_lo": round(ts_lo, 4), "tfa_sol_ci_hi": round(ts_hi, 4),
        "tfa_box_mean": round(tb_m, 4), "tfa_box_ci_lo": round(tb_lo, 4), "tfa_box_ci_hi": round(tb_hi, 4),
        "tfce_sol_mean": round(tc_m, 4), "tfce_sol_ci_lo": round(tc_lo, 4), "tfce_sol_ci_hi": round(tc_hi, 4),
    })
    return row, vecs


def _read_worker_csv(path: Path, dedup: Dict[Tuple, Dict]) -> None:
    """Reads one SNAP worker per-item CSV into the deduplicated row map."""
    with open(path, "r", encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            key = (row["model"], row["phase"], int(row["epoch"]), row["split"], row["problem_id"], row["variation_id"])
            dedup[key] = row


def load_worker_rows() -> List[Dict]:
    """Loads and deduplicates per-item rows from all SNAP worker CSVs."""
    dedup: Dict[Tuple, Dict] = {}
    for wg in ("gpu0", "gpu5", "gpu7", "frontier8b"):
        f = OUT_DIR / f"snap_{wg}_per_item.csv"
        if f.exists():
            _read_worker_csv(f, dedup)
    if not dedup:
        raise RuntimeError("No snap_*_per_item.csv files found in results/")
    return list(dedup.values())


def _append_primary_means(model_vectors: Dict, split: str, row: Dict) -> None:
    """Appends primary-split summary means for cross-model correlation vectors."""
    if split not in PRIMARY_SPLITS:
        return
    for col in ("em", "tfa_sol", "tfa_box", "tfce_sol"):
        model_vectors[split][col].append(row[f"{col}_mean"])


def _summarize_phase2_model(
    model: str, grouped: Dict[Tuple, List[Dict]], summary_rows: List[Dict], model_vectors: Dict
) -> Dict[str, Dict[str, np.ndarray]]:
    """Computes Phase 2 split summaries for one model and updates summary_rows and model_vectors."""
    m_splits: Dict[str, Dict[str, np.ndarray]] = {}
    for sp in ALL_SPLITS:
        sub = grouped.get((model, sp))
        if not sub:
            continue
        row, vecs = _summarize_split(model, sp, sub)
        summary_rows.append(row)
        m_splits[sp] = vecs
        _append_primary_means(model_vectors, sp, row)
    return m_splits


def summarize_phase2(p2_rows: List[Dict]) -> Tuple[List[Dict], Dict, Dict]:
    """Aggregates 10-model Phase 2 baseline summaries and within-model paired contamination gaps."""
    grouped = _group_by(p2_rows, ("model", "split"))
    summary_rows, paired_gaps = [], {}
    model_vectors = {sp: {"em": [], "tfa_sol": [], "tfa_box": [], "tfce_sol": []} for sp in PRIMARY_SPLITS}

    for m in sorted({r["model"] for r in p2_rows}):
        m_splits = _summarize_phase2_model(m, grouped, summary_rows, model_vectors)
        if "orig_contaminated" in m_splits and "func_variations_v1" in m_splits:
            paired_gaps[m] = {
                "em_orig_minus_var1": paired_diff_test(m_splits["orig_contaminated"]["em"], m_splits["func_variations_v1"]["em"]),
                "tfa_sol_orig_minus_var1": paired_diff_test(m_splits["orig_contaminated"]["tfa_sol"], m_splits["func_variations_v1"]["tfa_sol"]),
                "tfa_box_orig_minus_var1": paired_diff_test(m_splits["orig_contaminated"]["tfa_box"], m_splits["func_variations_v1"]["tfa_box"]),
                "tfa_sol_orig_minus_var5": paired_diff_test(m_splits["orig_contaminated"]["tfa_sol"], m_splits["func_variations_all5"]["tfa_sol"]),
            }
    return summary_rows, model_vectors, paired_gaps


def compute_phase2_correlations(model_vectors: Dict, paired_gaps: Dict) -> Dict:
    """Computes cross-model TFA vs EM correlations and exact across-model sign tests."""
    corrs = {}
    for sp in PRIMARY_SPLITS:
        v = model_vectors[sp]
        corrs[sp] = {
            "tfa_sol_vs_em": correlation_and_bias(np.array(v["tfa_sol"]), np.array(v["em"])),
            "tfa_box_vs_em": correlation_and_bias(np.array(v["tfa_box"]), np.array(v["em"])),
            "neg_tfce_vs_em": correlation_and_bias(-np.array(v["tfce_sol"]), np.array(v["em"]), include_bias=False),
        }
    pooled_em = np.concatenate([np.array(model_vectors[sp]["em"]) for sp in PRIMARY_SPLITS])
    pooled_sol = np.concatenate([np.array(model_vectors[sp]["tfa_sol"]) for sp in PRIMARY_SPLITS])
    pooled_box = np.concatenate([np.array(model_vectors[sp]["tfa_box"]) for sp in PRIMARY_SPLITS])
    corrs["pooled_30_cells"] = {
        "tfa_sol_vs_em": correlation_and_bias(pooled_sol, pooled_em),
        "tfa_box_vs_em": correlation_and_bias(pooled_box, pooled_em),
    }

    pos_var1 = sum(1 for v in paired_gaps.values() if v["tfa_sol_orig_minus_var1"]["mean_diff"] > 0)
    pos_var5 = sum(1 for v in paired_gaps.values() if v["tfa_sol_orig_minus_var5"]["mean_diff"] > 0)
    n_models = len(paired_gaps)
    corrs["across_models_tfa_sign_test"] = {
        "n_models": n_models,
        "positive_drop_var1_count": f"{pos_var1}/{n_models}",
        "exact_binom_p_var1": round(float(stats.binomtest(pos_var1, n_models, 0.5, alternative="two-sided").pvalue), 6),
        "positive_drop_var5_count": f"{pos_var5}/{n_models}",
        "exact_binom_p_var5": round(float(stats.binomtest(pos_var5, n_models, 0.5, alternative="two-sided").pvalue), 6),
    }
    return corrs


def _compute_sft_pair_tests(ep0: Dict, ep10: Dict) -> Dict:
    """Computes Ep10 vs Ep0 gains, memorization gaps, and net logic contamination for one model."""
    d_orig_em = ep10["orig_contaminated"]["em"] - ep0["orig_contaminated"]["em"]
    d_var1_em = ep10["func_variations_v1"]["em"] - ep0["func_variations_v1"]["em"]
    d_unseen_em = ep10["orig_unseen_control"]["em"] - ep0["orig_unseen_control"]["em"]
    d_orig_tfa = ep10["orig_contaminated"]["tfa_sol"] - ep0["orig_contaminated"]["tfa_sol"]
    d_var1_tfa = ep10["func_variations_v1"]["tfa_sol"] - ep0["func_variations_v1"]["tfa_sol"]
    d_var5_tfa = ep10["func_variations_all5"]["tfa_sol"] - ep0["func_variations_all5"]["tfa_sol"]
    d_unseen_tfa = ep10["orig_unseen_control"]["tfa_sol"] - ep0["orig_unseen_control"]["tfa_sol"]
    d_orig_box = ep10["orig_contaminated"]["tfa_box"] - ep0["orig_contaminated"]["tfa_box"]
    d_var1_box = ep10["func_variations_v1"]["tfa_box"] - ep0["func_variations_v1"]["tfa_box"]
    d_unseen_box = ep10["orig_unseen_control"]["tfa_box"] - ep0["orig_unseen_control"]["tfa_box"]

    return {
        "gain_ep10_minus_ep0": {
            "orig_contaminated_em": paired_diff_test(ep10["orig_contaminated"]["em"], ep0["orig_contaminated"]["em"]),
            "func_variations_v1_em": paired_diff_test(ep10["func_variations_v1"]["em"], ep0["func_variations_v1"]["em"]),
            "orig_unseen_control_em": paired_diff_test(ep10["orig_unseen_control"]["em"], ep0["orig_unseen_control"]["em"]),
            "orig_contaminated_tfa_sol": paired_diff_test(ep10["orig_contaminated"]["tfa_sol"], ep0["orig_contaminated"]["tfa_sol"]),
            "func_variations_v1_tfa_sol": paired_diff_test(ep10["func_variations_v1"]["tfa_sol"], ep0["func_variations_v1"]["tfa_sol"]),
            "func_variations_all5_tfa_sol": paired_diff_test(ep10["func_variations_all5"]["tfa_sol"], ep0["func_variations_all5"]["tfa_sol"]),
            "orig_unseen_control_tfa_sol": paired_diff_test(ep10["orig_unseen_control"]["tfa_sol"], ep0["orig_unseen_control"]["tfa_sol"]),
            "orig_contaminated_tfa_box": paired_diff_test(ep10["orig_contaminated"]["tfa_box"], ep0["orig_contaminated"]["tfa_box"]),
            "func_variations_v1_tfa_box": paired_diff_test(ep10["func_variations_v1"]["tfa_box"], ep0["func_variations_v1"]["tfa_box"]),
            "orig_unseen_control_tfa_box": paired_diff_test(ep10["orig_unseen_control"]["tfa_box"], ep0["orig_unseen_control"]["tfa_box"]),
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


def _summarize_epoch_splits(
    m: str, ep: int, grouped: Dict[Tuple, List[Dict]], summary_rows: List[Dict]
) -> Dict[str, Dict[str, np.ndarray]]:
    """Computes split summaries for one (model, epoch) checkpoint."""
    ep_splits: Dict[str, Dict[str, np.ndarray]] = {}
    for sp in ALL_SPLITS:
        sub = grouped.get((m, ep, sp))
        if not sub:
            continue
        row, vecs = _summarize_split(m, sp, sub, epoch=ep)
        summary_rows.append(row)
        ep_splits[sp] = vecs
    return ep_splits


def _summarize_one_sft_model(
    m: str, grouped: Dict[Tuple, List[Dict]], summary_rows: List[Dict], hypothesis_tests: Dict
) -> None:
    """Appends checkpoint summaries for one SFT model and computes Ep10-vs-Ep0 hypothesis tests."""
    epochs = sorted({k[1] for k in grouped if k[0] == m})
    ep_data = {ep: _summarize_epoch_splits(m, ep, grouped, summary_rows) for ep in epochs}
    if 0 in ep_data and 10 in ep_data:
        hypothesis_tests[m] = _compute_sft_pair_tests(ep_data[0], ep_data[10])


def summarize_phase3(p3_rows: List[Dict]) -> Tuple[List[Dict], Dict, Dict]:
    """Aggregates Phase 3 SFT checkpoint summaries, hypothesis tests, and trajectory correlations."""
    grouped = _group_by(p3_rows, ("model", "epoch", "split"))
    summary_rows, hypothesis_tests = [], {}
    for m in sorted({r["model"] for r in p3_rows}):
        _summarize_one_sft_model(m, grouped, summary_rows, hypothesis_tests)

    cells = [r for r in summary_rows if r["split"] != "func_variations_all5"]
    em_vec = _extract_col(cells, "em_mean")
    traj_corr = {
        "n_cells": len(cells),
        "tfa_sol_vs_em": correlation_and_bias(_extract_col(cells, "tfa_sol_mean"), em_vec),
        "tfa_box_vs_em": correlation_and_bias(_extract_col(cells, "tfa_box_mean"), em_vec),
    }
    return summary_rows, hypothesis_tests, traj_corr


def _extract_domains(raw_type: str) -> List[str]:
    """Parses space-joined Putnam domain tags into canonical domain labels."""
    cleaned = re.sub(r"\bLinear Algebra\b", "LinearAlgebra", raw_type)
    found = []
    for dom in CANONICAL_DOMAINS:
        tok = "LinearAlgebra" if dom == "Linear Algebra" else dom
        if re.search(rf"\b{re.escape(tok)}\b", cleaned):
            found.append(dom)
    return found or ["Other"]


def _load_domain_lookup() -> Dict[str, List[str]]:
    """Maps problem_id -> canonical mathematical domain tags (multi-label, exact token matching)."""
    with open(ROOT / "data/Putnam_AXIOM_Original_v3.json", "r", encoding="utf-8") as f:
        orig_522 = {x["id"]: x.get("type", "") for x in json.load(f)}
    with open(ROOT / "data/Putnam-AXIOM_Variations_v4/test.json", "r", encoding="utf-8") as f:
        var_type = {f"{x['year']}_{x['id']}": x.get("type", "") for x in json.load(f)}
    all_pids = sorted(set(orig_522) | set(var_type))
    return {pid: _extract_domains(orig_522.get(pid) or var_type.get(pid, "")) for pid in all_pids}


def _topic_tfa_map(
    grouped: Dict[Tuple, List[Dict]], dom: str, dom_lookup: Dict[str, List[str]], key: Tuple
) -> Dict[str, float]:
    """Extracts problem_id -> tfa_sol dict filtered to one domain for a Phase 3 (model, epoch, split)."""
    return {
        r["problem_id"]: float(r["tfa_sol"])
        for r in grouped.get(key, [])
        if dom in dom_lookup.get(r["problem_id"], [])
    }


def _topic_row_for_model(
    dom: str, m: str, dom_lookup: Dict[str, List[str]], p2_vals: Tuple[int, float, float], grouped3: Dict[Tuple, List[Dict]]
) -> Dict | None:
    """Computes one domain x SFT-model summary row comparing variation transfer vs unseen control."""
    ep0_o = _topic_tfa_map(grouped3, dom, dom_lookup, (m, 0, "orig_contaminated"))
    ep10_o = _topic_tfa_map(grouped3, dom, dom_lookup, (m, 10, "orig_contaminated"))
    ep0_v = _topic_tfa_map(grouped3, dom, dom_lookup, (m, 0, "func_variations_v1"))
    ep10_v = _topic_tfa_map(grouped3, dom, dom_lookup, (m, 10, "func_variations_v1"))
    ep0_u = _topic_tfa_map(grouped3, dom, dom_lookup, (m, 0, "orig_unseen_control"))
    ep10_u = _topic_tfa_map(grouped3, dom, dom_lookup, (m, 10, "orig_unseen_control"))
    if not (ep10_o and ep10_v and ep10_u):
        return None
    n_orig, p2_orig, p2_var5 = p2_vals
    pids_o, pids_u = sorted(ep0_o), sorted(ep0_u)
    var_gain = float(np.mean([ep10_v[p] - ep0_v[p] for p in pids_o]))
    unc_gain = float(np.mean([ep10_u[p] - ep0_u[p] for p in pids_u]))
    orig_gain = float(np.mean([ep10_o[p] - ep0_o[p] for p in pids_o]))
    return {
        "domain_multilabel": dom, "sft_model": m, "n_orig_problems": n_orig, "n_unseen_problems": len(pids_u),
        "phase2_10model_tfa_orig_mean": round(p2_orig, 4),
        "phase2_10model_tfa_var5_mean": round(p2_var5, 4),
        "phase2_10model_tfa_gap_pp": round((p2_orig - p2_var5) * 100.0, 3),
        "sft_orig_gain_pp": round(orig_gain * 100.0, 2),
        "sft_var1_gain_pp": round(var_gain * 100.0, 2),
        "sft_unseen_gain_pp": round(unc_gain * 100.0, 2),
        "net_logic_contamination_pp": round((var_gain - unc_gain) * 100.0, 2),
    }


def _phase2_domain_stats(
    grouped2: Dict[Tuple, List[Dict]], dom: str, dom_lookup: Dict[str, List[str]]
) -> Tuple[int, float, float]:
    """Computes N_orig and Phase 2 mean TFA on originals vs var5 within one domain."""
    orig_rows = [r for r in grouped2.get(("orig_contaminated",), []) if dom in dom_lookup.get(r["problem_id"], [])]
    var5_rows = [r for r in grouped2.get(("func_variations_all5",), []) if dom in dom_lookup.get(r["problem_id"], [])]
    n_orig = len({r["problem_id"] for r in orig_rows})
    return n_orig, float(_extract_col(orig_rows, "tfa_sol").mean()), float(_extract_col(var5_rows, "tfa_sol").mean())


def summarize_by_topic(p2_rows: List[Dict], p3_rows: List[Dict]) -> List[Dict]:
    """Computes multi-label mathematical-domain breakdown for Phase 2 TFA gap and Phase 3 SFT Ep10 gains."""
    dom_lookup = _load_domain_lookup()
    grouped2 = _group_by(p2_rows, ("split",))
    grouped3 = _group_by(p3_rows, ("model", "epoch", "split"))
    p3_models = sorted({r["model"] for r in p3_rows})
    out_rows = []
    for dom in CANONICAL_DOMAINS:
        p2_vals = _phase2_domain_stats(grouped2, dom, dom_lookup)
        dom_rows = [_topic_row_for_model(dom, m, dom_lookup, p2_vals, grouped3) for m in p3_models]
        out_rows.extend(row for row in dom_rows if row is not None)
    return out_rows


def main() -> None:
    """Runs Phase 2 + Phase 3 aggregation and writes CSV and JSON statistical artifacts."""
    all_rows = load_worker_rows()
    p2_rows = [r for r in all_rows if r["phase"] == "phase2_baseline"]
    p3_rows = [r for r in all_rows if r["phase"] == "phase3_sft_trajectory"]

    _write_csv(OUT_DIR / "phase2_10models_baseline_per_item.csv", p2_rows)
    _write_csv(OUT_DIR / "phase3_3models_sft_trajectory_per_item.csv", p3_rows)

    p2_summary, p2_vecs, p2_gaps = summarize_phase2(p2_rows)
    _write_csv(OUT_DIR / "phase2_10models_baseline_summary.csv", p2_summary)
    p2_corr = compute_phase2_correlations(p2_vecs, p2_gaps)

    p3_summary, p3_tests, p3_corr = summarize_phase3(p3_rows)
    _write_csv(OUT_DIR / "phase3_3models_sft_trajectory_summary.csv", p3_summary)

    topic_rows = summarize_by_topic(p2_rows, p3_rows)
    if topic_rows:
        _write_csv(OUT_DIR / "phase2_phase3_by_topic_summary.csv", topic_rows)

    full_stats = {
        "phase2_paired_gaps_by_model": p2_gaps,
        "phase2_cross_model_correlations": p2_corr,
        "phase3_sft_hypothesis_tests": p3_tests,
        "phase3_trajectory_all_cells_correlations": p3_corr,
    }
    (OUT_DIR / "phase2_phase3_statistical_tests.json").write_text(json.dumps(full_stats, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 & PHASE 3 STATISTICAL AGGREGATION COMPLETE.")


if __name__ == "__main__":
    main()
