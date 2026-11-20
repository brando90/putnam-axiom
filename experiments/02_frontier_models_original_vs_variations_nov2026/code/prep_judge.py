#!/usr/bin/env python3
"""Build equivalence-judge items for the strict misses of scored models.
Usage: PYTHONPATH=stubs python prep_judge.py scored_astra62.json out/astra62.jsonl --model astra62 --out judge_in/astra62.jsonl
Only items the repo grader marked wrong (strict False, relaxed False) are judged; raw (un-normalized) answers are sent."""
import argparse, json, sys
sys.path.insert(0, "stubs")
import pax_utils as u
from score import TASKS, cut

ap = argparse.ArgumentParser()
ap.add_argument("scored"); ap.add_argument("outs"); ap.add_argument("--model", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
rows = {r["key"]: r for r in json.load(open(a.scored))["rows"]}
recs = {}
for l in open(a.outs):
    try: r = json.loads(l)
    except Exception: continue
    if r.get("ok"): recs[r["key"]] = r
n = 0
with open(a.out, "w") as f:
    for k, r in rows.items():
        if r["relaxed"]: continue
        t = TASKS[k]
        out = cut(recs[k].get("output") or "")
        try: cand = u.remove_boxed(u.last_boxed_only_string(out))
        except Exception: cand = None
        if cand is None:
            cand = out[-300:]
        try: ref = u.remove_boxed(u.last_boxed_only_string(t["solution"]))
        except Exception: ref = None
        prompt = ("You are grading a math competition answer. Decide whether the CANDIDATE final answer is mathematically equivalent to the REFERENCE final answer. "
                  "Ignore formatting (LaTeX spacing, \\left/\\right, units words, 'x=' prefixes, equivalent forms of the same number or expression, same set or tuple written differently). "
                  "Different values, missing parts, extra conditions that change the answer, or a different set count as DIFFERENT. If the candidate is truncated or garbled so the answer cannot be read, answer DIFFERENT.\n\n"
                  f"PROBLEM:\n{t['problem']}\n\nREFERENCE final answer:\n{ref}\n\nCANDIDATE final answer:\n{cand}\n\n"
                  "Reply with one line: EQUIVALENT or DIFFERENT, then a dash and a reason of at most 15 words.")
        f.write(json.dumps({"id": a.model + "|" + k, "model": a.model, "key": k, "prompt": prompt, "ref": ref, "cand": cand}) + "\n"); n += 1
print(n, "items")
