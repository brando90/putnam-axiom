#!/usr/bin/env python3
"""Write RESULTS markdown from results.json (made by build_report.py). No em dashes."""
import json, sys
R = json.load(open("results.json"))
extra = json.load(open("extra.json")) if __import__("os").path.exists("extra.json") else {}
ORDER = ["fable52max", "opus55", "sonnet55", "astra62", "astra6", "gpt55", "gem38flash", "gpt4o", "qwen2math7b"]

def f(x, d=1):
    return "n/a" if x is None else f"{x:.{d}f}"
def ci(a):
    return f"{a['lo']:.1f} to {a['hi']:.1f}"

def row_orig(r):
    o = r["orig"]; M = r["meta"]
    s = f"| {M['label']} | {M['harness']}; {M['route']} | {o['n']} | {f(o['acc'])} | {ci(o)} | {f(o.get('judged'))} |"
    return s
def row_var(r):
    M = r["meta"]; v = r["var"]
    n = r["var_n"]
    s = f"| {M['label']} | {M['harness']}; {M['route']} | {n} | {f(r['var_acc'])} | {ci(v)} | {f(r['var_judged'])} | {f(r['m100']['acc'])} (n={r['m100']['n']}) | {f(r['gap'])} | {f(r['gap_j'])} |"
    return s

lines = []
A = lines.append
A("### Table 1. Putnam-AXIOM Original (522 problems)")
A("")
A("| Model | Harness and route | n | Accuracy, paper grader (%) | 95% CI | Accuracy, answer-equivalence judge (%) |")
A("|---|---|---|---|---|---|")
for k in ORDER:
    if k in R: A(row_orig(R[k]))
A("")
A("### Table 2. Putnam-AXIOM Functional Variations (500 problems = 5 snapshots of 100)")
A("")
A("| Model | Harness and route | n | Accuracy, paper grader (%) | 95% CI | Accuracy, answer-equivalence judge (%) | Matched 100 originals, paper grader (%) | Gap original minus variation, paper grader (points) | Gap, judge (points) |")
A("|---|---|---|---|---|---|---|---|---|")
for k in ORDER:
    if k in R: A(row_var(R[k]))
open("tables.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
