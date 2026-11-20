#!/usr/bin/env python3
"""Run equivalence-judge items through the claude-su launcher (Claude Code CLI, tools off, one turn). Resumable.
Usage: python3 judge_run.py judge_in/x.jsonl judge_out/x.jsonl --workers 8 [--model claude-sonnet-5-5]"""
import argparse, json, os, threading, time, concurrent.futures as cf
from run_eval import call_claude_cli, call_openai
ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--workers", type=int, default=6)
ap.add_argument("--model", default="claude-sonnet-5-5"); ap.add_argument("--launcher", default="/dfs/scratch0/brando9/bin/claude-su")
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--provider", default="claude_cli", choices=["claude_cli", "openai"])
ap.add_argument("--effort", default=None)
ap.add_argument("--key-file", default="/dfs/scratch0/brando9/keys/openai_bm_key_koyejolab.txt")
a = ap.parse_args()
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
done = set()
if os.path.exists(a.out):
    for l in open(a.out):
        try:
            r = json.loads(l)
            if r.get("ok"): done.add(r["id"])
        except Exception: pass
items = [json.loads(l) for l in open(a.inp)]
todo = [i for i in items if i["id"] not in done]
if a.limit: todo = todo[:a.limit]
print(len(items), "items", len(done), "done", len(todo), "to run", flush=True)
KEY = open(a.key_file).read().strip() if a.provider == "openai" else None
lock = threading.Lock(); fh = open(a.out, "a"); cnt = [0]
def work(i):
    rec = {"id": i["id"], "model": i["model"], "key": i["key"]}
    for attempt in range(3):
        try:
            if a.provider == "openai":
                text, u = call_openai(KEY, a.model, a.effort, i["prompt"], 4000, 240)
            else:
                text, u = call_claude_cli(a.launcher, a.model, None, i["prompt"], 0, 240)
            rec.update(ok=True, verdict=text.strip()[:300], usage=u); break
        except Exception as e:
            rec.update(ok=False, error=str(e)[:200]); time.sleep(5 * (attempt + 1))
    with lock:
        fh.write(json.dumps(rec) + "\n"); fh.flush(); cnt[0] += 1
        if cnt[0] % 25 == 0: print(time.strftime("%H:%M:%S"), cnt[0], flush=True)
with cf.ThreadPoolExecutor(a.workers) as ex: list(ex.map(work, todo))
print("finished", flush=True)
