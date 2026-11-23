#!/usr/bin/env python3
"""Deterministic verification suite for Putnam-AXIOM Experiment 01.

Checks:
1. Dataset SHA-256 hashes match PROTOCOL.md and RESULTS_sft_logic_contamination_and_tfa_v1.md.
2. Python AST structural quality (CC <= 10, non-blank/comment SLOC <= 60, closed file handles).
3. Generated CSV/JSON result schemas, row counts, zero NaNs/nulls in summary tables.
4. Markdown link resolution, Rule 16/37/44 headers, and exact numerical alignment with JSON/CSV outputs.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Dict, List, Tuple


EXP_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = EXP_DIR.parent.parent
EXPT_V1 = EXP_DIR / "expt_v1"
RES_DIR = EXPT_V1 / "results"

EXPECTED_DATA_HASHES = {
    "data/Putnam-AXIOM_Variations_v4/original.json": "71f5cb5e29d1d8c92e8400ac1a31b64c52a2db486cc7bb2fe92dcb4c77805ef1",
    "data/Putnam-AXIOM_Variations_v4/test.json": "76c46b3626a8e8c4f09ad3431dc3add7a1e4a4a467064226ebfc0fe957dae96f",
    "data/Putnam_AXIOM_Original_v3.json": "b763cba941864a53557d603634dd519f2f9edb9eda342fe9cf4826b67da3d00b",
}

BANNED_STALE_LITERALS = ("0.6932", "c8742b82", "85a85438", "a10a12cf", "TLDR-start")


def _sha256_file(path: Path) -> str:
    """Computes hex SHA-256 digest of a file in chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_dataset_hashes() -> List[str]:
    """Verifies raw benchmark JSON SHA-256 digests and their documentation."""
    errors = []
    proto_text = (EXP_DIR / "PROTOCOL.md").read_text(encoding="utf-8")
    res_text = (EXP_DIR / "RESULTS_sft_logic_contamination_and_tfa_v1.md").read_text(encoding="utf-8")
    for rel, expected in EXPECTED_DATA_HASHES.items():
        actual = _sha256_file(REPO_ROOT / rel)
        if actual != expected:
            errors.append(f"SHA mismatch for {rel}: got {actual}, expected {expected}")
        if expected not in proto_text:
            errors.append(f"PROTOCOL.md missing SHA-256 {expected} for {rel}")
        if expected not in res_text:
            errors.append(f"RESULTS missing SHA-256 {expected} for {rel}")
    return errors


def _func_cc(node: ast.AST) -> int:
    """Computes McCabe cyclomatic complexity of a function AST node."""
    branch_nodes = (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.AsyncWith, ast.IfExp)
    cc = 1
    for child in ast.walk(node):
        if isinstance(child, branch_nodes):
            cc += 1
        elif isinstance(child, ast.BoolOp):
            cc += len(child.values) - 1
        elif isinstance(child, ast.comprehension):
            cc += 1 + len(child.ifs)
    return cc


def _func_sloc(src_lines: List[str], node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Counts non-blank, non-comment source lines inside a function body."""
    end = getattr(node, "end_lineno", node.lineno)
    body = src_lines[node.lineno - 1 : end]
    return sum(1 for ln in body if ln.strip() and not ln.strip().startswith("#"))


def _block_depth(stmts: List[ast.AST], cur: int) -> int:
    """Returns the maximum nesting depth across a list of sibling statements."""
    return max((_stmt_depth(s, cur) for s in stmts), default=cur)


def _stmt_depth(stmt: ast.AST, cur: int = 0) -> int:
    """Computes maximum control-flow nesting depth inside a statement (excluding nested defs)."""
    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return cur
    if isinstance(stmt, ast.If):
        is_elif = len(stmt.orelse) == 1 and isinstance(stmt.orelse[0], ast.If)
        else_d = _stmt_depth(stmt.orelse[0], cur) if is_elif else _block_depth(stmt.orelse, cur + 1)
        return max(_block_depth(stmt.body, cur + 1), else_d)
    if isinstance(stmt, (ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith)):
        return _block_depth(stmt.body + getattr(stmt, "orelse", []), cur + 1)
    if isinstance(stmt, ast.Try):
        handler_body = [s for h in stmt.handlers for s in h.body]
        return _block_depth(stmt.body + stmt.orelse + stmt.finalbody + handler_body, cur + 1)
    return cur


def _func_max_nesting(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Returns the maximum control-flow nesting depth within a function body."""
    return max((_stmt_depth(s, 0) for s in node.body), default=0)


def _has_open_outside_with(tree: ast.AST) -> bool:
    """Returns True if any open(...) call appears outside a with-statement context manager."""
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    for node in ast.walk(tree):
        is_open = isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open"
        if is_open and not isinstance(parents.get(node), ast.withitem):
            return True
    return False


def _check_one_py_file(py_path: Path) -> List[str]:
    """Checks CC <= 10, SLOC <= 60, nesting <= 2, and context-managed open() for one Python file."""
    src = py_path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(py_path))
    errors = [f"{py_path.name}: contains open(...) outside a with block"] if _has_open_outside_with(tree) else []
    src_lines = src.splitlines()
    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    for node in funcs:
        cc, sloc, nest = _func_cc(node), _func_sloc(src_lines, node), _func_max_nesting(node)
        if cc > 10:
            errors.append(f"{py_path.name}:{node.name} CC={cc} > 10")
        if sloc > 60:
            errors.append(f"{py_path.name}:{node.name} SLOC={sloc} > 60")
        if nest >= 3:
            errors.append(f"{py_path.name}:{node.name} nesting={nest} >= 3")
    return errors


def check_python_structure() -> List[str]:
    """Enforces CC <= 10, SLOC <= 60, nesting <= 2, and context-managed open() across expt_v1/*.py."""
    errors = []
    for py_path in sorted(EXPT_V1.glob("*.py")):
        errors.extend(_check_one_py_file(py_path))
    return errors


def _read_csv_rows(path: Path) -> List[Dict]:
    """Loads CSV rows into dicts."""
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _check_csv_clean(path: Path, rows: List[Dict], errors: List[str]) -> None:
    """Verifies CSV rows contain zero missing, NaN, or Inf string tokens."""
    bad_tokens = {"nan", "inf", "-inf", "none", "null"}
    bad = sum(1 for r in rows for v in r.values() if v is None or str(v).strip().lower() in bad_tokens)
    if bad:
        errors.append(f"{path.name}: contains {bad} NaN/Inf/null cell(s)")


def _check_json_finite(obj, ctx: str, errors: List[str]) -> None:
    """Recursively verifies JSON numbers contain zero NaN or Inf values."""
    if isinstance(obj, float) and not math.isfinite(obj):
        errors.append(f"Non-finite float {obj} at {ctx}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _check_json_finite(v, f"{ctx}.{k}", errors)
    elif isinstance(obj, list):
        for idx, v in enumerate(obj):
            _check_json_finite(v, f"{ctx}[{idx}]", errors)


def check_result_files() -> Tuple[List[str], Dict, Dict]:
    """Verifies required CSV/JSON outputs exist, have exact row counts, and contain zero NaNs."""
    errors: List[str] = []
    p1 = json.loads((RES_DIR / "phase1_summary_stats.json").read_text(encoding="utf-8"))
    p23 = json.loads((RES_DIR / "phase2_phase3_statistical_tests.json").read_text(encoding="utf-8"))
    _check_json_finite(p1, "phase1_summary_stats", errors)
    _check_json_finite(p23, "phase2_phase3_statistical_tests", errors)

    p2_items = _read_csv_rows(RES_DIR / "phase2_10models_baseline_per_item.csv")
    p2_summ = _read_csv_rows(RES_DIR / "phase2_10models_baseline_summary.csv")
    p3_items = _read_csv_rows(RES_DIR / "phase3_3models_sft_trajectory_per_item.csv")
    p3_summ = _read_csv_rows(RES_DIR / "phase3_3models_sft_trajectory_summary.csv")
    topic_summ = _read_csv_rows(RES_DIR / "phase2_phase3_by_topic_summary.csv")
    for p, r in (
        (RES_DIR / "phase2_10models_baseline_per_item.csv", p2_items),
        (RES_DIR / "phase2_10models_baseline_summary.csv", p2_summ),
        (RES_DIR / "phase3_3models_sft_trajectory_per_item.csv", p3_items),
        (RES_DIR / "phase3_3models_sft_trajectory_summary.csv", p3_summ),
        (RES_DIR / "phase2_phase3_by_topic_summary.csv", topic_summ),
    ):
        _check_csv_clean(p, r, errors)

    if len(p2_items) != 8000 or len(p2_summ) != 40:
        errors.append(f"Unexpected Phase 2 row counts: items={len(p2_items)} (exp 8000), summ={len(p2_summ)} (exp 40)")
    p3_models = {r["model"] for r in p3_summ}
    if len(p3_items) != 12000 or len(p3_summ) != 60 or len(p3_models) != 3:
        errors.append(f"Unexpected Phase 3 row counts: items={len(p3_items)}, summ={len(p3_summ)}, models={sorted(p3_models)}")
    if len(topic_summ) != 24:
        errors.append(f"Unexpected domain topic row count: {len(topic_summ)} (exp 24)")
    return errors, p1, p23


def _strip_code_blocks(text: str) -> str:
    """Removes fenced code blocks before Markdown link scanning."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def _check_links_in_file(md: Path) -> List[str]:
    """Checks relative Markdown links inside one file resolve on disk."""
    errs = []
    cleaned = _strip_code_blocks(md.read_text(encoding="utf-8"))
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", cleaned):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        rel_path = target.split("#", 1)[0]
        if rel_path.endswith(".log"):
            errs.append(f"Gitignored .log link in {md.relative_to(REPO_ROOT)}: {target}")
        elif rel_path and not (md.parent / rel_path).resolve().exists():
            errs.append(f"Broken link in {md.relative_to(REPO_ROOT)}: {target}")
    return errs


def check_markdown_links_and_headers() -> List[str]:
    """Verifies all relative Markdown links resolve and required Rule 16/37/44 headers exist."""
    errors = []
    for md in [EXP_DIR.parent / "README.md"] + sorted(EXP_DIR.rglob("*.md")):
        errors.extend(_check_links_in_file(md))
    for name in ("README.md", "PROTOCOL.md", "RESULTS_sft_logic_contamination_and_tfa_v1.md", "expt_v1/cc.md"):
        txt = (EXP_DIR / name).read_text(encoding="utf-8")
        if "**Doc link:**" not in txt or "**TLDR:**" not in txt:
            errors.append(f"{name}: missing required **Doc link:** or **TLDR:** header")
    res_ledger = (EXP_DIR / "results.md").read_text(encoding="utf-8")
    if "**TLDR-end:** [" not in res_ledger or "**TLDR:**" in res_ledger:
        errors.append("results.md: must end with project-tagged **TLDR-end:** [...] and omit opening **TLDR:**")
    ckpt = (EXP_DIR / "CKPT_sft_logic_contamination_and_tfa.md").read_text(encoding="utf-8")
    for h in ("## 1. Goal", "## 2. What ran", "## 3. Results", "## 4. Stuck / blocked", "## 5. Next steps", "## 6. Brando to-do", "## Log"):
        if h not in ckpt:
            errors.append(f"CKPT missing Rule 44 heading: {h}")
    return errors


def _fmt_pct(val: float, dec: int = 2) -> str:
    """Formats a 0-1 proportion as a percentage string for text consistency matching."""
    return f"{val * 100:.{dec}f}"


def _find_banned_literals(md: Path) -> List[str]:
    """Scans one Markdown file for stale or banned literal strings."""
    txt = md.read_text(encoding="utf-8")
    return [f"{md.name}: contains stale/banned string {b!r}" for b in BANNED_STALE_LITERALS if b in txt]


def check_text_consistency(p1: Dict, p23: Dict) -> List[str]:
    """Verifies banned stale literals are absent and key headline figures match JSON ground truth."""
    errors = [err for md in sorted(EXP_DIR.rglob("*.md")) for err in _find_banned_literals(md)]

    res_doc = (EXP_DIR / "RESULTS_sft_logic_contamination_and_tfa_v1.md").read_text(encoding="utf-8")
    ledger = (EXP_DIR / "results.md").read_text(encoding="utf-8")
    qwen_base_var1 = p23["phase2_paired_gaps_by_model"]["Qwen/Qwen3-1.7B-Base"]["tfa_sol_orig_minus_var1"]
    qwen_base_ci = f"[{_fmt_pct(qwen_base_var1['ci_95_lo'])}, {_fmt_pct(qwen_base_var1['ci_95_hi'])}]"
    traj_r = f"{p23['phase3_trajectory_all_cells_correlations']['tfa_sol_vs_em']['pearson_r']:.4f}"
    orig_20m = f"{p1['phase1_20_models_benchmark_gap']['original_mean_pct']:.2f}"

    for doc_name, txt in (("RESULTS", res_doc), ("results.md", ledger)):
        if qwen_base_ci not in txt:
            errors.append(f"{doc_name}: missing verified Qwen3-1.7B-Base TFA CI {qwen_base_ci}")
        if traj_r not in txt:
            errors.append(f"{doc_name}: missing trajectory Pearson r={traj_r}")
        if orig_20m not in txt:
            errors.append(f"{doc_name}: missing 20-model Original EM mean {orig_20m}")
    return errors


def main() -> None:
    """Runs all Experiment 01 deterministic checks and exits non-zero on any error."""
    errors = []
    errors.extend(check_dataset_hashes())
    errors.extend(check_python_structure())
    res_errs, p1, p23 = check_result_files()
    errors.extend(res_errs)
    errors.extend(check_markdown_links_and_headers())
    if p1 and p23:
        errors.extend(check_text_consistency(p1, p23))

    if errors:
        print("EXPT01 VERIFICATION: FAIL")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)
    print("EXPT01 VERIFICATION: PASS (0 errors)")


if __name__ == "__main__":
    main()
