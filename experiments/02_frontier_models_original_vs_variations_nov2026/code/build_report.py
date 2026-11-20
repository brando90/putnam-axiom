#!/usr/bin/env python3
"""Aggregate scored runs + judge verdicts into tables (json + markdown fragments)."""
import json, math, os, sys
sys.path.insert(0, "stubs")
from score import wilson

MODELS = json.load(open("models.json"))   # list of dicts: id, label, harness, route, price_in, price_out, note

def load_scored(m):
    p = f"scored_{m}.json"
    return json.load(open(p))["rows"] if os.path.exists(p) else None

def load_judge(m):
    d = {}
    p = f"judge_out_gpt/{m}.jsonl"
    if os.path.exists(p):
        for l in open(p):
            r = json.loads(l)
            if r.get("ok"):
                d[r["key"]] = r["verdict"].upper().startswith("EQUIV")
    return d

def acc(rows, sel, judged=None):
    r = [x for x in rows if sel(x)]
    n = len(r); k = sum(x["strict"] for x in r)
    lo, hi = wilson(k, n)
    out = {"n": n, "k": k, "acc": 100 * k / n if n else None, "lo": lo, "hi": hi}
    out["relaxed"] = 100 * sum(x["relaxed"] for x in r) / n if n else None
    if judged is not None:
        kj = sum(1 for x in r if x["relaxed"] or judged.get(x["key"], False))
        out["judged_k"] = kj; out["judged"] = 100 * kj / n if n else None
        out["jlo"], out["jhi"] = wilson(kj, n)
    return out

res = {}
for M in MODELS:
    rows = load_scored(M["id"])
    if rows is None: continue
    J = load_judge(M["id"])
    has_j = len(J) > 0 or all(x["relaxed"] for x in rows if not x["strict"])
    jj = J if has_j else None
    o = acc(rows, lambda x: x["set"] == "orig", jj)
    m100 = acc(rows, lambda x: x["set"] == "orig" and x["matched100"], jj)
    v = acc(rows, lambda x: x["set"] == "var", jj)
    snaps = {s: acc(rows, lambda x, s=s: x["set"] == "var" and x["snapshot"] == s, jj) for s in range(1, 6)}
    full = [s for s in snaps.values() if s["n"] == 100]
    # variation accuracy on the snapshots that are complete (mean, as in the paper); else pooled over what ran
    if len(full) == 5:
        vmean = sum(s["acc"] for s in full) / 5
        vjmean = sum(s["judged"] for s in full) / 5 if jj is not None else None
        vn = 500
    else:
        vmean, vjmean, vn = v["acc"], v.get("judged"), v["n"]
    tok_out = sum((x["out_tokens"] or 0) for x in rows); tok_in = sum((x["in_tokens"] or 0) for x in rows)
    n_trunc = sum(1 for x in rows if x["status"] in ("incomplete", "max_tokens", "length", "MAX_TOKENS"))
    boxed = 100 * sum(x["boxed"] for x in rows) / len(rows)
    cost = (tok_in * M["price_in"] + tok_out * M["price_out"]) / 1e6 if M.get("price_in") is not None else None
    res[M["id"]] = {"meta": M, "orig": o, "m100": m100, "var": v, "snaps": snaps, "var_acc": vmean, "var_judged": vjmean, "var_n": vn,
                    "gap": (m100["acc"] - vmean) if (m100["n"] and vmean is not None) else None,
                    "gap_j": (m100["judged"] - vjmean) if (jj is not None and vjmean is not None and m100["n"]) else None,
                    "tok_in": tok_in, "tok_out": tok_out, "truncated": n_trunc, "boxed": boxed, "cost": cost, "n_rows": len(rows),
                    "n_judged_items": len(J)}
json.dump(res, open("results.json", "w"), indent=1)
for k, r in res.items():
    print(k, "orig", r["orig"]["n"], round(r["orig"]["acc"] or 0, 1), "judged", r["orig"].get("judged"), "| m100", r["m100"]["n"], r["m100"]["acc"], r["m100"].get("judged"),
          "| var", r["var_n"], round(r["var_acc"] or 0, 1), r["var_judged"], "| gap", r["gap"], r["gap_j"], "| cost", r["cost"], "| tok", r["tok_in"], r["tok_out"])
