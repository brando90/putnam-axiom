#!/usr/bin/env python3
"""Compute per-problem paired drop, 10,000-resample bootstrap 95% CI, and exact McNemar p-val
on the 100 matched Putnam-AXIOM Original problems vs their Functional Variations.

Missing/failed tasks are retained as incorrect (0) in the full n=100 denominator.
Optionally updates the 'Frontier models in 2026' table in the repo README.md.
"""
import argparse
import gzip
import json
import math
import os
import re
import numpy as np


def open_text(path):
    return gzip.open(path, "rt", encoding="utf-8") if path.endswith(".gz") else open(path, "r", encoding="utf-8")


def load_tasks(tasks_path):
    tasks = [json.loads(line) for line in open_text(tasks_path)]
    m100 = [t["key"] for t in tasks if t["set"] == "orig" and t["matched100"]]
    assert len(m100) == 100, f"expected 100 matched originals, got {len(m100)}"
    return m100


def load_scored_rows(scored_path):
    data = json.load(open_text(scored_path))
    return {r["key"]: bool(r["strict"]) for r in data["rows"]}


def exact_mcnemar_p(b, c):
    """Two-sided exact binomial McNemar p-value on discordant pairs (b=orig_only, c=var_only)."""
    n = b + c
    if n == 0:
        return 1.0
    m = min(b, c)
    tail = sum(math.comb(n, k) for k in range(m + 1)) * (0.5 ** n)
    return min(1.0, 2.0 * tail)


def compute_paired_stats(m100_keys, rows, snapshots, n_boot=10000, seed=0):
    orig_vals = np.array([100.0 if rows.get(k, False) else 0.0 for k in m100_keys], dtype=float)
    var_vals = np.array([
        sum(100.0 if rows.get(f"V:{5 * i + (s - 1):03d}", False) else 0.0 for s in snapshots) / len(snapshots)
        for i in range(100)
    ], dtype=float)
    diffs = orig_vals - var_vals

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, 100, size=(n_boot, 100))
    boot_means = diffs[idx].mean(axis=1)
    ci_lo, ci_hi = np.percentile(boot_means, [2.5, 97.5])

    orig_present = sum(1 for k in m100_keys if k in rows)
    var_present = sum(1 for i in range(100) for s in snapshots if f"V:{5 * i + (s - 1):03d}" in rows)

    mcnemar = None
    if len(snapshots) == 1:
        s = snapshots[0]
        b = sum(1 for i, k in enumerate(m100_keys) if rows.get(k, False) and not rows.get(f"V:{5 * i + (s - 1):03d}", False))
        c = sum(1 for i, k in enumerate(m100_keys) if not rows.get(k, False) and rows.get(f"V:{5 * i + (s - 1):03d}", False))
        mcnemar = {"b_orig_only": b, "c_var_only": c, "p_val": exact_mcnemar_p(b, c)}

    return {
        "orig_100": float(orig_vals.mean()),
        "var": float(var_vals.mean()),
        "paired_drop": float(diffs.mean()),
        "ci_lo": float(ci_lo),
        "ci_hi": float(ci_hi),
        "orig_present": orig_present,
        "var_present": var_present,
        "var_expected": 100 * len(snapshots),
        "snapshots": snapshots,
        "n_boot": n_boot,
        "seed": seed,
        "mcnemar": mcnemar,
    }


def update_readme_table(readme_path, row_label, stats):
    content = open(readme_path, "r", encoding="utf-8").read()
    new_row = (
        f"| {row_label} | {stats['orig_100']:.1f} | {stats['var']:.1f} | "
        f"{stats['paired_drop']:.1f} [{stats['ci_lo']:.1f}, {stats['ci_hi']:.1f}] |"
    )
    anchor = "### Frontier models in 2026"
    idx = content.find(anchor)
    if idx < 0:
        raise ValueError(f"Could not find {anchor!r} in {readme_path}")
    sep = "|---|---|---|---|"
    sep_idx = content.find(sep, idx)
    if sep_idx < 0:
        raise ValueError(f"Could not find table separator after {anchor!r} in {readme_path}")
    after_sep = content[sep_idx + len(sep):]
    lines = after_sep.splitlines(keepends=True)
    # lines[0] is the newline right after |---|---|---|---|
    prefix = re.escape(f"| {row_label} |")
    replaced = False
    for j in range(1, len(lines)):
        if not lines[j].lstrip().startswith("|"):
            break
        if re.match(prefix, lines[j]):
            lines[j] = new_row + ("\n" if lines[j].endswith("\n") else "")
            replaced = True
            break
    if not replaced:
        lines.insert(1, new_row + "\n")
    updated = content[:sep_idx + len(sep)] + "".join(lines)
    if updated != content:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated)
    return new_row


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tasks", required=True, help="Path to tasks.jsonl or tasks.jsonl.gz")
    ap.add_argument("--scored", required=True, help="Path to scored_<model>.json or .json.gz")
    ap.add_argument("--snapshots", default="1", help="Comma-separated snapshots, e.g. 1 or 1,2,3,4,5")
    ap.add_argument("--row-label", default="claude-fable-5-2 (effort max, snapshot 1)")
    ap.add_argument("--update-readme", default=None, help="Path to repo README.md to insert/update row")
    ap.add_argument("--json-out", default=None, help="Optional path to write stats JSON")
    a = ap.parse_args()

    snaps = [int(x.strip()) for x in a.snapshots.split(",") if x.strip()]
    m100_keys = load_tasks(a.tasks)
    rows = load_scored_rows(a.scored)
    stats = compute_paired_stats(m100_keys, rows, snaps)

    if a.update_readme:
        row_line = update_readme_table(a.update_readme, a.row_label, stats)
        stats["readme_row"] = row_line

    if a.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(a.json_out)), exist_ok=True)
        with open(a.json_out, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
            f.write("\n")

    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
