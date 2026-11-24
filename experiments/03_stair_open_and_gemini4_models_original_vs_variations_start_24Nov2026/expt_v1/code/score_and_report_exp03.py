#!/usr/bin/env python3
"""Score Experiment 03 runs with Putnam-AXIOM's SymPy paper grader (no LLM/Google judge),
update results.md / RESULTS_*.md / CKPT, and update root README.md with dated Frontier 2026 rows.
"""
import argparse
import datetime
import gzip
import importlib.util
import json
import math
import multiprocessing as mp
import os
import re
import sys
import types
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

TZ_LA = ZoneInfo("America/Los_Angeles")
REPO_ROOT = Path("/Users/brandomiranda/putnam-axiom")
EXP02_DIR = REPO_ROOT / "experiments/02_frontier_models_original_vs_variations_nov2026"
EXP03_DIR = REPO_ROOT / "experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026"

EXP03_MODELS = [
    {
        "slug": "gemini4_neon_xhigh",
        "readme_label": "gemini-4-neon-xhigh (snapshot 1)",
        "model": "gemini-4-neon-xhigh",
        "effort_label": "xhigh (`--effort xhigh`, extra-high)",
        "harness_short": "single-call agy 1.5.15 (`permission_mode=request-review`, `num_turns=1`)",
        "route": "Antigravity CLI (`agy`) personal subscription on Mac",
        "track": "agy",
    },
    {
        "slug": "gemini4_argon_high",
        "readme_label": "gemini-4-argon-high (snapshot 1)",
        "model": "gemini-4-argon-high",
        "effort_label": "high (`--effort high`)",
        "harness_short": "single-call agy 1.5.15 (`permission_mode=request-review`, `num_turns=1`)",
        "route": "Antigravity CLI (`agy`) personal subscription on Mac",
        "track": "agy",
    },
    {
        "slug": "gemini4_carbon_high",
        "readme_label": "gemini-4-carbon-high (snapshot 1)",
        "model": "gemini-4-carbon-high",
        "effort_label": "high (`--effort high`)",
        "harness_short": "single-call agy 1.5.15 (`permission_mode=request-review`, `num_turns=1`)",
        "route": "Antigravity CLI (`agy`) personal subscription on Mac",
        "track": "agy",
    },
    {
        "slug": "glm53",
        "readme_label": "GLM 5.3 (snapshot 1)",
        "model": "GLM 5.3",
        "effort_label": "default (unset; reasoning active)",
        "harness_short": "STAIR Gateway OpenAI chat API (`temp=0`, `max_tokens=8192`, 0 retries)",
        "route": "STAIR `bm` Gateway (`https://aiapi-prod.stanford.edu/v1`) on `skampere1`",
        "track": "stair",
    },
    {
        "slug": "kimik3",
        "readme_label": "Kimi K3 (snapshot 1)",
        "model": "Kimi K3",
        "effort_label": "default (unset; reasoning active)",
        "harness_short": "STAIR Gateway OpenAI chat API (`temp=0`, `max_tokens=8192`, 0 retries)",
        "route": "STAIR `bm` Gateway (`https://aiapi-prod.stanford.edu/v1`) on `skampere1`",
        "track": "stair",
    },
    {
        "slug": "deepseekv41flash",
        "readme_label": "DeepSeek V4.1 Flash 1017 (snapshot 1)",
        "model": "DeepSeek V4.1 Flash 1017",
        "effort_label": "default (unset)",
        "harness_short": "STAIR Gateway OpenAI chat API (`temp=0`, `max_tokens=8192`, 0 retries)",
        "route": "STAIR `bm` Gateway (`https://aiapi-prod.stanford.edu/v1`) on `skampere1`",
        "track": "stair",
    },
]

# Inject minimal datasets stub before loading pax_utils
if "datasets" not in sys.modules:
    _ds_stub = types.ModuleType("datasets")
    _ds_stub.Dataset = object
    sys.modules["datasets"] = _ds_stub
_spec = importlib.util.spec_from_file_location("pax_utils", str(EXP02_DIR / "code/pax_utils.py"))
pax_utils = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pax_utils)

TASKS_BY_KEY = {}


def _init_tasks():
    global TASKS_BY_KEY
    if TASKS_BY_KEY:
        return
    with gzip.open(EXP02_DIR / "data/tasks.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            t = json.loads(line)
            TASKS_BY_KEY[t["key"]] = t


def cut(out):
    i = out.find("Problem:")
    if i >= 0 and "\\boxed" in out[:i]:
        return out[:i]
    return out


def grade_text(text, ref_norm):
    out = cut(text or "")
    try:
        ans = pax_utils.ground_truth_boxed_answer(out)
        has_box = True
    except Exception:
        ans = pax_utils.get_generated_answer(out)
        has_box = False
    strict = bool(pax_utils.is_equiv(ans, ref_norm))
    relaxed = strict or (ans == ref_norm and ans != "[invalidanswer]")
    return strict, relaxed, has_box, ans


def _score_worker(rec):
    _init_tasks()
    key = rec["key"]
    t = TASKS_BY_KEY[key]
    ref = pax_utils.normalize_final_answer(
        pax_utils.remove_boxed(pax_utils.last_boxed_only_string(t["solution"]))
    )
    ok = bool(rec.get("ok")) and not bool(rec.get("tool_violation"))
    output = rec.get("output") or ""
    rc_text = rec.get("reasoning_content") or ""
    if ok and output.strip():
        strict, relaxed, has_box, ans = grade_text(output, ref)
    else:
        strict, relaxed, has_box, ans = False, False, False, "[no_output]"

    rc_fallback_strict = False
    if ok and not output.strip() and rc_text.strip():
        rc_fallback_strict, _, _, _ = grade_text(rc_text, ref)

    usage = rec.get("usage") or {}
    return {
        "key": key,
        "set": rec.get("set"),
        "snapshot": rec.get("snapshot"),
        "orig_v4_id": rec.get("orig_v4_id"),
        "pair_index": rec.get("pair_index"),
        "ok": ok,
        "tool_violation": bool(rec.get("tool_violation")),
        "strict": strict,
        "relaxed": relaxed,
        "rc_fallback_strict": rc_fallback_strict,
        "boxed": has_box,
        "answer": ans,
        "ref": ref,
        "in_tokens": usage.get("input") or usage.get("prompt_tokens") or 0,
        "out_tokens": usage.get("output") or usage.get("completion_tokens") or 0,
        "est_cost_usd": rec.get("est_cost_usd") or 0.0,
        "secs": rec.get("secs"),
        "timestamp": rec.get("timestamp"),
        "finish_reason": rec.get("finish_reason"),
        "content_empty": not bool(output.strip()),
        "error": rec.get("error"),
        "equivalence_judge": "ungraded" if not strict else "sympy_strict_pass",
    }


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


def exact_mcnemar_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    m = min(b, c)
    return min(1.0, 2.0 * sum(math.comb(n, k) for k in range(m + 1)) * (0.5 ** n))


def open_raw_records(raw_dir, slug):
    p_jsonl = raw_dir / f"{slug}.jsonl"
    p_gz = raw_dir / f"{slug}.jsonl.gz"
    lines = []
    if p_jsonl.is_file():
        lines = p_jsonl.read_text(encoding="utf-8", errors="ignore").splitlines()
    elif p_gz.is_file():
        with gzip.open(p_gz, "rt", encoding="utf-8") as f:
            lines = f.read().splitlines()
    else:
        return {}
    recs = {}
    for line in lines:
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        k = r.get("key")
        if k and k not in recs:  # preserve first attempt (1 attempt per problem)
            recs[k] = r
    return recs


def _ts_sort_key(ts_str):
    m = re.match(r"(\d{2})-(\d{2})-(\d{4})(?:\s+(\d{2}):(\d{2}):(\d{2}))?", (ts_str or "").strip())
    if not m:
        return (0, 0, 0, 0, 0, 0)
    return (int(m.group(3)), int(m.group(1)), int(m.group(2)), int(m.group(4) or 0), int(m.group(5) or 0), int(m.group(6) or 0))


def parse_ddmonyyyy(ts_str):
    # Input e.g. "11-24-2026 02:15:00 PST"
    if not ts_str:
        return datetime.datetime.now(TZ_LA).strftime("%d%b%Y")
    m = re.match(r"(\d{2})-(\d{2})-(\d{4})", ts_str.strip())
    if m:
        dt = datetime.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        return dt.strftime("%d%b%Y")
    return datetime.datetime.now(TZ_LA).strftime("%d%b%Y")


def score_model(meta, manifest, raw_dir, res_dir, pool):
    slug = meta["slug"]
    recs = open_raw_records(raw_dir, slug)
    if not recs:
        return None

    # Deduplicate raw -> gzip archive in raw_dir if uncompressed exists
    p_jsonl = raw_dir / f"{slug}.jsonl"
    p_gz = raw_dir / f"{slug}.jsonl.gz"
    if p_jsonl.is_file():
        with open(p_jsonl, "rb") as src, gzip.open(p_gz, "wb") as dst:
            dst.write(src.read())

    scored_rows = pool.map(_score_worker, list(recs.values()), chunksize=8)
    by_key = {r["key"]: r for r in scored_rows}

    orig_keys = [m["orig_key"] for m in manifest]
    var_keys = [m["var_snap1_key"] for m in manifest]

    orig_att = sum(1 for k in orig_keys if k in by_key)
    var_att = sum(1 for k in var_keys if k in by_key)
    complete = (orig_att == 100 and var_att == 100)

    # Full n=100 denominator when complete; partial uses attempted counts transparently too
    orig_k = sum(1 for k in orig_keys if (by_key.get(k) or {}).get("strict"))
    var_k = sum(1 for k in var_keys if (by_key.get(k) or {}).get("strict"))
    orig_den = 100 if complete else orig_att
    var_den = 100 if complete else var_att
    orig_acc = 100.0 * orig_k / orig_den if orig_den else None
    var_acc = 100.0 * var_k / var_den if var_den else None
    o_lo, o_hi = wilson(orig_k, orig_den)
    v_lo, v_hi = wilson(var_k, var_den)

    paired_drop = ci_lo = ci_hi = p_val = None
    b = c = both_r = both_w = 0
    if complete:
        o_arr = np.array([100.0 if (by_key.get(k) or {}).get("strict") else 0.0 for k in orig_keys])
        v_arr = np.array([100.0 if (by_key.get(k) or {}).get("strict") else 0.0 for k in var_keys])
        diffs = o_arr - v_arr
        rng = np.random.default_rng(0)
        idx = rng.integers(0, 100, size=(10000, 100))
        boots = diffs[idx].mean(axis=1)
        ci_lo, ci_hi = map(float, np.percentile(boots, [2.5, 97.5]))
        paired_drop = float(diffs.mean())
        for ok, vk in zip(orig_keys, var_keys):
            os_ = bool((by_key.get(ok) or {}).get("strict"))
            vs_ = bool((by_key.get(vk) or {}).get("strict"))
            if os_ and vs_:
                both_r += 1
            elif os_ and not vs_:
                b += 1
            elif not os_ and vs_:
                c += 1
            else:
                both_w += 1
        p_val = exact_mcnemar_p(b, c)

    tok_in = sum(r["in_tokens"] for r in scored_rows)
    tok_out = sum(r["out_tokens"] for r in scored_rows)
    est_cost = sum(r["est_cost_usd"] for r in scored_rows)
    boxed_n = sum(1 for r in scored_rows if r["boxed"])
    ok_n = sum(1 for r in scored_rows if r["ok"])
    timeout_n = sum(1 for r in scored_rows if not r["ok"] and "timeout" in str(r.get("error") or "").lower())
    finish_len_n = sum(1 for r in scored_rows if r.get("finish_reason") == "length")
    finish_len_empty_n = sum(1 for r in scored_rows if r.get("finish_reason") == "length" and r.get("content_empty"))
    tool_viol_n = sum(1 for r in scored_rows if r["tool_violation"])
    rc_extra = sum(1 for r in scored_rows if r["rc_fallback_strict"])
    latest_ts = max((r.get("timestamp") or "" for r in scored_rows), key=_ts_sort_key, default="")
    date_tok = parse_ddmonyyyy(latest_ts)
    ungraded = [r["key"] for r in scored_rows if not r["strict"]]

    summary = {
        "meta": meta,
        "date_ddmonyyyy": date_tok,
        "complete": complete,
        "orig_attempted": orig_att,
        "var_attempted": var_att,
        "orig_k": orig_k,
        "orig_den": orig_den,
        "orig_acc": orig_acc,
        "orig_wilson_95": [o_lo, o_hi],
        "var_k": var_k,
        "var_den": var_den,
        "var_acc": var_acc,
        "var_wilson_95": [v_lo, v_hi],
        "paired_drop": paired_drop,
        "boot_95": [ci_lo, ci_hi] if complete else None,
        "mcnemar": {"both_right": both_r, "b_orig_only": b, "c_var_only": c, "both_wrong": both_w, "p_val": p_val} if complete else None,
        "ok_calls": ok_n,
        "timeout_calls": timeout_n,
        "finish_length_count": finish_len_n,
        "finish_length_empty_content_count": finish_len_empty_n,
        "attempted_calls": len(scored_rows),
        "tool_violations": tool_viol_n,
        "boxed_count": boxed_n,
        "rc_fallback_extra": rc_extra,
        "tok_in": tok_in,
        "tok_out": tok_out,
        "est_cost_usd": round(est_cost, 6),
        "ungraded_miss_count": len(ungraded),
        "ungraded_misses": ungraded,
    }

    scored_out = res_dir / f"scored_{slug}.json.gz"
    with gzip.open(scored_out, "wt", encoding="utf-8") as f:
        json.dump({"summary": summary, "rows": scored_rows}, f, indent=1)
    return summary


def update_root_readme(exp03_summaries):
    readme_p = REPO_ROOT / "README.md"
    content = readme_p.read_text(encoding="utf-8")
    anchor = "### Frontier models in 2026"
    idx = content.find(anchor)
    if idx < 0:
        raise ValueError("Cannot find Frontier models in 2026 heading in README.md")
    next_h = content.find("\n### ", idx + len(anchor))
    tail = content[next_h:] if next_h >= 0 else ""

    # Load Exp 02 paired stats + fable52max stats cleanly
    exp02_tasks = [json.loads(l) for l in gzip.open(EXP02_DIR / "data/tasks.jsonl.gz", "rt", encoding="utf-8")]
    m100_keys = [t["key"] for t in exp02_tasks if t["set"] == "orig" and t["matched100"]]

    def exp02_row(scored_name, label, effort_str, harness, date_str, nsnaps):
        d = json.load(gzip.open(EXP02_DIR / "data/scored" / f"scored_{scored_name}.json.gz", "rt", encoding="utf-8"))
        rmap = {r["key"]: bool(r["strict"]) for r in d["rows"]}
        o_vals = np.array([100.0 if rmap.get(k, False) else 0.0 for k in m100_keys])
        v_vals = np.array([
            sum(100.0 if rmap.get(f"V:{5*i+s:03d}", False) else 0.0 for s in range(nsnaps)) / nsnaps
            for i in range(100)
        ])
        diffs = o_vals - v_vals
        rng = np.random.default_rng(0)
        idx_b = rng.integers(0, 100, size=(10000, 100))
        lo, hi = np.percentile(diffs[idx_b].mean(axis=1), [2.5, 97.5])
        return f"| {label} | {effort_str} | {harness} | {date_str} | {o_vals.mean():.1f} | {v_vals.mean():.1f} | {diffs.mean():.1f} [{lo:.1f}, {hi:.1f}] |"

    # Keep exact published Nov-20 numbers on existing rows while adding Thinking effort + Harness + Date columns!
    existing_rows = [
        None,  # fable52max computed from scored_fable52max.json.gz
        '| gpt-6.2-astra | max (`reasoning.effort=max`) | OpenAI Responses API (no tools) | 20Nov2026 | 81.0 | 69.0 | 12.0 [6.4, 18.2] |',
        '| gpt-6-astra | max (`reasoning.effort=max`) | OpenAI Responses API (no tools) | 20Nov2026 | 82.0 | 69.4 | 12.6 [7.0, 19.0] |',
        '| gpt-5.5 | high (`reasoning.effort=high`) | OpenAI Responses API (no tools) | 20Nov2026 | 80.0 | 68.6 | 11.4 [5.6, 18.0] |',
        '| claude-sonnet-5-5 | default (unset; no `--effort`) | Claude Code 2.1.278 (`-p --tools ""`) | 20Nov2026 | 83.0 | 71.2 | 11.8 [5.2, 18.8] |',
        '| claude-opus-5-5 | default (unset; no `--effort`) | Claude Code 2.1.329 (`-p --tools ""`) | 20Nov2026 | 83.0 | 73.6 | 9.4 [3.2, 16.0] |',
        '| gemini-3.8-flash (snapshot 1) | high (`thinkingLevel=high`) | Gemini API `generateContent` (no tools) | 20Nov2026 | 87.0 | 73.0 | 14.0 [7.0, 21.0] |',
        '| gpt-4o (2026 rerun) | n/a (non-reasoning; unset) | OpenAI Responses API (no tools) | 20Nov2026 | 27.0 | 23.4 | 3.6 [-3.8, 11.2] |',
        '| Qwen2-Math-7B-Instruct (2026 rerun) | n/a (non-reasoning; greedy) | HF `transformers` completion (`1024` tokens) | 20Nov2026 | 19.0 | 16.0 | 3.0 [-2.8, 9.2] |',
    ]
    if (EXP02_DIR / "data/scored/scored_fable52max.json.gz").is_file():
        existing_rows[0] = exp02_row(
            "fable52max",
            "claude-fable-5-2 (snapshot 1)",
            "max (`--effort max`)",
            'Claude Code 2.1.330 (`--safe-mode -p --tools ""`)',
            "24Nov2026",
            1,
        )

    exp03_rows = []
    for s in exp03_summaries:
        if not s or not s["complete"]:
            continue
        ci_lo, ci_hi = s["boot_95"]
        exp03_rows.append(
            f"| {s['meta']['readme_label']} | {s['meta']['effort_label']} | {s['meta']['harness_short']} | {s['date_ddmonyyyy']} | "
            f"{s['orig_acc']:.1f} | {s['var_acc']:.1f} | {s['paired_drop']:.1f} [{ci_lo:.1f}, {ci_hi:.1f}] |"
        )

    all_rows = [r for r in ([existing_rows[0]] + exp03_rows + existing_rows[1:]) if r]
    section = (
        "### Frontier models in 2026 (different models and a different harness than the paper)\n\n"
        "Per-question paired drop on the 100 matched originals vs their variations (paper grader, "
        "`experiments/02_frontier_models_original_vs_variations_nov2026` and "
        "`experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026`; "
        "5 snapshots = 500 pairs where noted, otherwise snapshot 1 = 100 pairs). "
        "Interval: bootstrap over the 100 problems (10000 resamples). GPT-4o and Qwen2-Math-7B-Instruct are the paper's models, re-run in Nov 2026.\n\n"
        "| Model | Thinking effort | Harness | Date | Original (100) | Variation | Paired drop, points [95% interval] |\n"
        "|---|---|---|---|---|---|---|\n"
        + "\n".join(all_rows)
        + "\n"
    )
    updated = content[:idx] + section + tail
    readme_p.write_text(updated, encoding="utf-8")


def write_reports(summaries, manifest, stamp):
    res_dir = EXP03_DIR / "expt_v1/results"
    res_dir.mkdir(parents=True, exist_ok=True)
    report_p = res_dir / "RESULTS_stair_open_and_gemini4_original_vs_variations_11-24-2026.md"

    table_rows = []
    ledger_rows = []
    for meta in EXP03_MODELS:
        s = next((x for x in summaries if x and x["meta"]["slug"] == meta["slug"]), None)
        if s is None:
            ledger_rows.append(
                f"| `{meta['model']}` | {meta['effort_label']} | {meta['harness_short']}; {meta['route']} | 24Nov2026 | 0/0 | pending | pending | pending | pending | 0 / `$0.00` | `PENDING` |"
            )
            continue
        fail_n = s["attempted_calls"] - s["ok_calls"]
        timeout_n = s.get("timeout_calls", 0)
        if s["complete"]:
            if fail_n > 0:
                if timeout_n == fail_n:
                    status_s = f"COMPLETE (200/200; {s['ok_calls']} ok, {fail_n} timeouts)"
                elif timeout_n > 0:
                    status_s = f"COMPLETE (200/200; {s['ok_calls']} ok, {timeout_n} timeouts, {fail_n - timeout_n} errors)"
                else:
                    status_s = f"COMPLETE (200/200; {s['ok_calls']} ok, {fail_n} errors)"
            else:
                status_s = "COMPLETE (200/200)"
        else:
            status_s = f"PARTIAL ({s['orig_attempted']}/100 orig, {s['var_attempted']}/100 var1)"
        if s["orig_acc"] is not None:
            olo, ohi = s["orig_wilson_95"]
            o_s = f"{s['orig_k']}/{s['orig_den']} ({s['orig_acc']:.1f}% [{olo:.1f}, {ohi:.1f}])"
        else:
            o_s = "n/a"
        if s["var_acc"] is not None:
            vlo, vhi = s["var_wilson_95"]
            v_s = f"{s['var_k']}/{s['var_den']} ({s['var_acc']:.1f}% [{vlo:.1f}, {vhi:.1f}])"
        else:
            v_s = "n/a"
        if s["complete"]:
            ci_lo, ci_hi = s["boot_95"]
            mcn = s["mcnemar"]
            drop_s = f"{s['paired_drop']:.1f} [{ci_lo:.1f}, {ci_hi:.1f}]"
            p_s = f"exact McNemar `p-val={mcn['p_val']:.4g}` (`b={mcn['b_orig_only']}`, `c={mcn['c_var_only']}`)"
        else:
            drop_s = "pending (<200)"
            p_s = "pending (<200)"
        cost_s = f"`${s['est_cost_usd']:.2f}` est." if meta["track"] == "stair" else "`$0.00` (sub)"
        tok_s = f"{s['tok_in']} in / {s['tok_out']} out" if s["tok_in"] else f"{s['tok_out']} total"
        extra_rc = f"; rc_fallback_extra={s['rc_fallback_extra']}" if s["rc_fallback_extra"] else ""
        row = (
            f"| `{meta['model']}` | {meta['effort_label']} | {meta['harness_short']}; {meta['route']} | {s['date_ddmonyyyy']} | "
            f"{s['orig_attempted']}/{s['var_attempted']} | {o_s} | {v_s} | {drop_s} | {p_s} | "
            f"{tok_s} / {cost_s}{extra_rc} | `{status_s}` |"
        )
        ledger_rows.append(row)
        table_rows.append(row)

    agy_sums = [s for s in summaries if s and s["meta"]["track"] == "agy"]
    agy_total = sum(s["attempted_calls"] for s in agy_sums)
    agy_viol = sum(s["tool_violations"] for s in agy_sums)
    s_glm = next((s for s in summaries if s and s["meta"]["slug"] == "glm53"), None)
    glm_boxed = s_glm["boxed_count"] if s_glm else 0
    glm_att = s_glm["attempted_calls"] if s_glm else 0
    glm_rc = s_glm["rc_fallback_extra"] if s_glm else 0
    glm_fl = s_glm.get("finish_length_count", 0) if s_glm else 0
    glm_fl_empty = s_glm.get("finish_length_empty_content_count", 0) if s_glm else 0
    glm_fl_partial = glm_fl - glm_fl_empty
    stair_st_p = EXP03_DIR / "expt_v1/data/stair_run_status.json"
    stair_st = json.loads(stair_st_p.read_text(encoding="utf-8")) if stair_st_p.is_file() else {}
    stair_cum_cost = stair_st.get("cum_est_cost_usd", sum(s["est_cost_usd"] for s in summaries if s and s["meta"]["track"] == "stair"))
    stair_cap = float(stair_st.get("cost_cap_usd", 15.0))
    stair_cost_rel = "below" if stair_cum_cost < stair_cap else "at/above"
    stair_counts = stair_st.get("counts", {})
    stair_done = sum(stair_counts.values()) if stair_counts else sum(s["attempted_calls"] for s in summaries if s and s["meta"]["track"] == "stair")
    stair_sched = (
        "All `600/600` STAIR calls complete."
        if stair_st.get("all_600_complete")
        else f"`{stair_done}/600` active-model STAIR calls complete (`238` active + `1` HTTP-400 `" + '"GLM 5.3 Flash"' + "` ledger row + `1` `" + '"GLM 5.3"' + "` HTTP-200 probe = `240` Day-1 calls); LaunchAgent `com.brando.putnam-expt03-stair-daily` is armed at `00:15 PST` for Day 2 (`11-25-2026`) and Day 3 (`11-26-2026`)."
    )

    id_list_str = ", ".join(f"{m['orig_v4_id']} ({m['orig_key']} / {m['var_snap1_key']})" for m in manifest)
    ungraded_lines = []
    for s in summaries:
        if not s:
            continue
        all_keys = ", ".join(s["ungraded_misses"]) if s["ungraded_misses"] else "none"
        miss_word = "miss" if s["ungraded_miss_count"] == 1 else "misses"
        ungraded_lines.append(
            f"- **`{s['meta']['model']}` (`{s['ungraded_miss_count']}` ungraded strict {miss_word}):** {all_keys}"
        )

    report_md = f"""# Results: STAIR Open Models & Gemini 4 Single-Call Putnam-AXIOM Eval (11-24-2026)

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/expt_v1/results/RESULTS_stair_open_and_gemini4_original_vs_variations_11-24-2026.md>

**TLDR:** SymPy paper-grader results across the `100` matched Putnam-AXIOM Original problems vs Snapshot-1 Functional Variations (`n=100` pairs/model, zero LLM/Google equivalence judging; strict misses left `ungraded`) for STAIR Gateway open models and local `agy` Gemini 4 single-call runs as of `{stamp}`.

Date: 11-24-2026
As of {stamp}

## Summary Table

| Model | Thinking effort | Harness & Route | Date | Attempted (Orig/Var) | Orig (100) | Var (Snap 1) | Paired drop [95% CI] | McNemar p-val | Tokens / Est. Cost | Status |
|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(table_rows)}

**Model ID note:** `"GLM 5.3 Flash"` (listed in `/v1/models`) returned `HTTP 400 Invalid model name` on `/v1/chat/completions`, so `"GLM 5.3"` (verified HTTP 200 on the same STAIR `bm` key) ran instead.

## Diagnostics & Cost Budget
- **Single-call isolation (`agy` Gemini 4):** `{agy_viol}` tool-use violations across all `{agy_total}` `agy` Gemini 4 single-call invocations (`permission_mode=request-review`, `num_turns=1`, empty `chmod 555` working directory).
- **`GLM 5.3` `max_tokens=8192` truncation:** `{glm_fl}/{glm_att}` calls hit `finish_reason="length"` (`{glm_fl_empty}/{glm_att}` inside `reasoning_content` with empty `content`, `{glm_fl_partial}/{glm_att}` truncated mid-`content`; `{glm_boxed}/{glm_att}` boxed in `content`; `{glm_rc}` uncounted `\\boxed{{}}` matches in `reasoning_content`).
- **STAIR budget & schedule:** Cumulative conservative STAIR cost estimate is `${stair_cum_cost:.4f}` ({stair_cost_rel} the `${stair_cap:.2f}` hard stop cap; Day-1 cumulative estimate `$4.6862`). {stair_sched}

## Ungraded Strict Misses (No LLM / Google Equivalence Judge)
{chr(10).join(ungraded_lines)}

## Matched 100 Problem IDs (`original.json` `id` + `O:...` / `V:...` keys)
{id_list_str}

**TLDR-end:** [putnam-axiom: expt03 stair-open & gemini4 eval] SymPy paper-grader report updated at `{stamp}`; `{agy_total}/600` `agy` Gemini 4 calls (`{agy_viol}` tool violations) and `{stair_done}/600` logged STAIR calls (`${stair_cum_cost:.4f}` est.) scored without LLM/Google equivalence judging.
"""
    report_p.write_text(report_md, encoding="utf-8")

    # Update results.md
    res_md = f"""# Results Ledger: STAIR Open Models & Antigravity CLI Gemini 4 Models (`11-24-2026`)

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/results.md>

Date: 11-24-2026
Last updated: {stamp}

Protocol: [`PROTOCOL.md`](PROTOCOL.md). Detailed report: [`RESULTS_stair_open_and_gemini4_original_vs_variations_11-24-2026.md`](expt_v1/results/RESULTS_stair_open_and_gemini4_original_vs_variations_11-24-2026.md). Matched `100` problem IDs: [`expt_v1/data/matched100_problem_ids.json`](expt_v1/data/matched100_problem_ids.json).

## Live Per-Model Summary (`100` Matched Originals vs Snapshot-1 Functional Variations, SymPy Paper Grader, Ungraded for LLM Judge)

| Model | Thinking effort | Harness & Route | Date | Calls (Orig/Var) | Orig (100) | Var (Snap 1) | Paired drop [95% CI] | McNemar p-val | Tokens / Est. Cost | Status |
|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(ledger_rows)}

**TLDR-end:** [putnam-axiom: expt03 stair-open & gemini4 eval] Updated live SymPy paper-grader results as of `{stamp}`; completed `200/200` models are propagated to root `README.md` with thinking effort, harness and `DDMonYYYY` dates.
"""
    (EXP03_DIR / "results.md").write_text(res_md, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-readme", action="store_true")
    a = ap.parse_args()

    manifest = json.load(open(EXP03_DIR / "expt_v1/data/matched100_problem_ids.json", "r", encoding="utf-8"))
    raw_dir = EXP03_DIR / "expt_v1/data/raw_outputs"
    res_dir = EXP03_DIR / "expt_v1/results"
    raw_dir.mkdir(parents=True, exist_ok=True)
    res_dir.mkdir(parents=True, exist_ok=True)

    _init_tasks()
    with mp.Pool(4) as pool:
        summaries = [score_model(m, manifest, raw_dir, res_dir, pool) for m in EXP03_MODELS]

    stamp = datetime.datetime.now(TZ_LA).strftime("%m-%d-%Y %H:%M %Z")
    write_reports(summaries, manifest, stamp)
    if not a.no_readme:
        update_root_readme(summaries)

    print(json.dumps([s for s in summaries if s], indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
