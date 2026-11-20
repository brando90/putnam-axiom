#!/usr/bin/env python3
"""Score Putnam-AXIOM runs with the repo's own grader (pax_utils.py = tasks/putnam_axiom/utils.py, unchanged).

Primary = repo protocol: last \\boxed{} in the model output (else 'Final Answer: The final answer is ...'), normalised, then
sympy parse_latex difference == 0 (5 s timeout). Secondary = same, or normalised strings identical.
Run: PYTHONPATH=stubs ~/.venvs/pax/bin/python score.py out/astra62.jsonl [more.jsonl ...] --json scored.json
"""
import argparse, json, math, sys, collections, multiprocessing as mp
sys.path.insert(0, "stubs")
import pax_utils as u

TASKS = {}
for l in open("tasks.jsonl"):
    t = json.loads(l); TASKS[t["key"]] = t


def cut(out):
    i = out.find("Problem:")
    if i >= 0 and "\\boxed" in out[:i]:
        return out[:i]
    return out


def score_one(rec):
    t = TASKS[rec["key"]]
    ref = u.normalize_final_answer(u.remove_boxed(u.last_boxed_only_string(t["solution"])))
    out = cut(rec.get("output") or "")
    try:
        ans = u.ground_truth_boxed_answer(out)
        has_box = True
    except Exception:
        ans = u.get_generated_answer(out)
        has_box = False
    strict = bool(u.is_equiv(ans, ref))
    relaxed = strict or (ans == ref and ans != "[invalidanswer]")
    return {"key": rec["key"], "set": rec["set"], "snapshot": rec["snapshot"], "matched100": rec["matched100"],
            "strict": strict, "relaxed": relaxed, "boxed": has_box, "answer": ans, "ref": ref,
            "out_tokens": (rec.get("usage") or {}).get("output"), "in_tokens": (rec.get("usage") or {}).get("input"),
            "reasoning_tokens": (rec.get("usage") or {}).get("reasoning"), "status": (rec.get("usage") or {}).get("status"),
            "secs": rec.get("secs")}


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


def summarize(rows):
    S = {}
    def agg(sel):
        r = [x for x in rows if sel(x)]
        n = len(r); k = sum(x["strict"] for x in r); kr = sum(x["relaxed"] for x in r)
        lo, hi = wilson(k, n)
        ot = [x["out_tokens"] for x in r if x["out_tokens"] is not None]
        return {"n": n, "correct": k, "acc": 100 * k / n if n else None, "ci_lo": lo, "ci_hi": hi,
                "relaxed_acc": 100 * kr / n if n else None, "boxed_rate": 100 * sum(x["boxed"] for x in r) / n if n else None,
                "mean_out_tokens": sum(ot) / len(ot) if ot else None, "total_out_tokens": sum(ot) if ot else 0,
                "total_in_tokens": sum(x["in_tokens"] or 0 for x in r),
                "truncated": sum(1 for x in r if x["status"] in ("incomplete", "max_tokens", "length", "MAX_TOKENS"))}
    S["orig_all"] = agg(lambda x: x["set"] == "orig")
    S["orig_matched100"] = agg(lambda x: x["set"] == "orig" and x["matched100"])
    S["var_all"] = agg(lambda x: x["set"] == "var")
    for s in range(1, 6):
        S[f"var_snap{s}"] = agg(lambda x, s=s: x["set"] == "var" and x["snapshot"] == s)
    snaps = [S[f"var_snap{s}"] for s in range(1, 6) if S[f"var_snap{s}"]["n"] == 100]
    S["var_mean_complete_snapshots"] = {"n_snapshots": len(snaps), "acc": sum(x["acc"] for x in snaps) / len(snaps) if snaps else None}
    return S


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", required=True)
    a = ap.parse_args()
    recs = {}
    for f in a.files:
        for l in open(f):
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get("ok") and r["key"] in TASKS:
                recs[r["key"]] = r
    with mp.Pool(4) as p:
        rows = p.map(score_one, list(recs.values()), chunksize=8)
    S = summarize(rows)
    json.dump({"summary": S, "rows": rows}, open(a.json, "w"))
    for k, v in S.items():
        print(k, v)
