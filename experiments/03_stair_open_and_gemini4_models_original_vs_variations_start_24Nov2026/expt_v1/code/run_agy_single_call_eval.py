#!/usr/bin/env python3
"""Run pure single-call Putnam-AXIOM evaluations using local Antigravity CLI (agy).

Models:
- gemini-4-neon-xhigh   (--effort xhigh)
- gemini-4-argon-high   (--effort high)
- gemini-4-carbon-high  (--effort high)

Single-call isolation:
- Runs inside empty read-only directory /tmp/pax_agy_single_call_empty (chmod 555)
- Passes --disable-slash-commands --new-project --output-format json --print-timeout 600s
  (note: --sandbox is omitted because it blocks agy's outbound HTTPS; permission_mode remains request-review)
- Does NOT pass --dangerously-skip-permissions or --add-dir
- Verifies num_turns == 1 (0 tool turns); 1 attempt per problem & version (0 retries)
- Enforces >= 20% weekly and >= 5% five-hour Gemini Models quota remaining via `agy -p /usage`.
"""
import argparse
import concurrent.futures as cf
import datetime
import gzip
import json
import os
import re
import shutil
import stat
import subprocess
import threading
import time
from pathlib import Path
from zoneinfo import ZoneInfo

TZ_LA = ZoneInfo("America/Los_Angeles")
AGY_BIN = str(Path.home() / ".local/bin/agy")
EMPTY_SANDBOX_DIR = Path("/tmp/pax_agy_single_call_empty")

MODEL_SPECS = {
    "gemini-4-neon-xhigh": ("gemini4_neon_xhigh", "xhigh"),
    "gemini-4-argon-high": ("gemini4_argon_high", "high"),
    "gemini-4-carbon-high": ("gemini4_carbon_high", "high"),
}

DESC = (
    "Answer directly in a single response with no tool calls, file reads, or shell commands.\n\n"
    "Given a mathematics question, compose a detailed solution. Simplify your answer as much as possible. "
    "Always give the final answer inside a \\boxed{answer}. Give your answer in the format: \n"
    "Final Answer: The final answer is $\\boxed{answer}$. I hope it is correct. Here are some examples:"
)


def open_text(path):
    return gzip.open(path, "rt", encoding="utf-8") if str(path).endswith(".gz") else open(path, "r", encoding="utf-8")


def now_stamp():
    return datetime.datetime.now(TZ_LA).strftime("%m-%d-%Y %H:%M:%S %Z")


def ensure_empty_sandbox():
    if EMPTY_SANDBOX_DIR.exists():
        try:
            os.chmod(EMPTY_SANDBOX_DIR, 0o755)
        except Exception:
            pass
        for item in EMPTY_SANDBOX_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    else:
        EMPTY_SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(EMPTY_SANDBOX_DIR, stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


def check_gemini_quota():
    try:
        p = subprocess.run([AGY_BIN, "-p", "/usage"], capture_output=True, text=True, timeout=30)
        txt = (p.stdout or "") + "\n" + (p.stderr or "")
        wm = re.search(r"Gemini Models\s+Weekly Limit Remaining\s+(\d+)%", txt)
        hm = re.search(r"Gemini Models\s+Five Hour Limit Remaining\s+(\d+)%", txt)
        weekly = int(wm.group(1)) if wm else None
        five_hr = int(hm.group(1)) if hm else None
        return {"weekly_pct": weekly, "five_hr_pct": five_hr, "raw": txt.strip()}
    except Exception as e:
        return {"weekly_pct": None, "five_hr_pct": None, "error": str(e)}


def build_prompt(problem, fs_text):
    return DESC + "\n\n" + fs_text + "\n\n" + "Problem:" + "\n" + problem + "\n\n" + "Solution:"


def load_attempted_keys(out_jsonl):
    p = Path(out_jsonl)
    p_gz = Path(str(out_jsonl) + ".gz")
    attempted = set()
    for src in (p_gz, p):
        if not src.is_file():
            continue
        with open_text(src) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                    if r.get("key"):
                        attempted.add(r["key"])
                except Exception:
                    continue
    return attempted


def parse_json_output(stdout):
    """Parse single JSON object emitted by `agy --output-format json`."""
    s = stdout.strip()
    start = s.find("{")
    if start < 0:
        return {"ok_parse": False, "error": f"No JSON in stdout: {s[:200]}"}
    try:
        obj = json.loads(s[start:])
    except Exception as e:
        return {"ok_parse": False, "error": f"JSONDecodeError: {e}; raw={s[:200]}"}
    u = obj.get("usage") or {}
    num_turns = obj.get("num_turns")
    valid_turns = isinstance(num_turns, int) and not isinstance(num_turns, bool)
    tool_calls = max(0, (int(num_turns) - 1)) if valid_turns else 0
    return {
        "ok_parse": True,
        "text": obj.get("response") or "",
        "agy_status": obj.get("status"),
        "num_turns": num_turns,
        "tool_calls": tool_calls,
        "tool_violation": valid_turns and num_turns > 1,
        "duration_seconds": obj.get("duration_seconds"),
        "conversation_id": obj.get("conversation_id"),
        "error": obj.get("error"),
        "usage": {
            "input": u.get("input_tokens") or 0,
            "output": u.get("output_tokens") or 0,
            "reasoning": u.get("thinking_tokens") or 0,
            "cache_read": u.get("cache_read_tokens") or 0,
            "total": u.get("total_tokens") or 0,
        },
    }


def call_agy(model_id, effort, prompt, timeout_s=600):
    cmd = [
        AGY_BIN,
        "--disable-slash-commands",
        "--new-project",
        "--model",
        model_id,
        "--effort",
        effort,
        "--output-format",
        "json",
        "--print-timeout",
        f"{timeout_s}s",
        "-p",
        prompt,
    ]
    p = subprocess.run(
        cmd,
        cwd=str(EMPTY_SANDBOX_DIR),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout_s + 45,
    )
    return p.returncode, p.stdout, p.stderr


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True, choices=list(MODEL_SPECS.keys()))
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--fewshot", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--min-weekly-pct", type=int, default=20)
    ap.add_argument("--min-five-hr-pct", type=int, default=5)
    ap.add_argument("--save-raw-events", default=None, help="Optional dir to save raw stdout for inspection")
    a = ap.parse_args()

    slug, effort = MODEL_SPECS[a.model]
    ensure_empty_sandbox()

    q = check_gemini_quota()
    print(f"[{now_stamp()}] Initial quota check for {a.model}: {q}", flush=True)
    if q.get("weekly_pct") is not None and q["weekly_pct"] < a.min_weekly_pct:
        print(f"STOP: Weekly Gemini quota {q['weekly_pct']}% < {a.min_weekly_pct}% reserve.", flush=True)
        return 3
    if q.get("five_hr_pct") is not None and q["five_hr_pct"] < a.min_five_hr_pct:
        print(f"STOP: Five-hour Gemini quota {q['five_hr_pct']}% < {a.min_five_hr_pct}% reserve.", flush=True)
        return 3

    fs = json.load(open(a.fewshot, "r", encoding="utf-8"))
    fs_text = "\n\n".join("Problem:\n" + e["problem"] + "\n\nSolution: " + e["solution"] for e in fs)
    tasks_by_key = {}
    with open_text(a.tasks) as f:
        for line in f:
            t = json.loads(line)
            tasks_by_key[t["key"]] = t

    manifest = json.load(open(a.manifest, "r", encoding="utf-8"))
    ordered = []
    for entry in manifest:
        ordered.append((entry["orig_key"], entry["orig_v4_id"], entry["index"]))
    for entry in manifest:
        ordered.append((entry["var_snap1_key"], entry["orig_v4_id"], entry["index"]))

    out_path = Path(a.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    attempted = load_attempted_keys(out_path)
    todo = [item for item in ordered if item[0] not in attempted]
    if a.limit:
        todo = todo[: a.limit]

    print(f"[{now_stamp()}] {a.model} ({effort}): {len(ordered)} total, {len(attempted)} attempted, {len(todo)} to run", flush=True)
    if not todo:
        return 0

    lock = threading.Lock()
    state = {"n": 0, "ok": 0, "fail": 0, "tool_violations": 0, "stop": None, "last_quota_check_n": 0}
    fh = open(out_path, "a", encoding="utf-8")

    def work(item):
        key, vid, idx = item
        with lock:
            if state["stop"]:
                return
            check_now = (state["n"] > 0 and state["n"] % 50 == 0 and state["n"] != state["last_quota_check_n"])
            if check_now:
                state["last_quota_check_n"] = state["n"]
        if check_now:
            qc = check_gemini_quota()
            with lock:
                if qc.get("weekly_pct") is not None and qc["weekly_pct"] < a.min_weekly_pct:
                    state["stop"] = f"QUOTA_WEEKLY_LOW ({qc['weekly_pct']}%)"
                elif qc.get("five_hr_pct") is not None and qc["five_hr_pct"] < a.min_five_hr_pct:
                    state["stop"] = f"QUOTA_5HR_LOW ({qc['five_hr_pct']}%)"
                if state["stop"]:
                    print(f"[{now_stamp()}] {state['stop']}", flush=True)
                    return

        task = tasks_by_key[key]
        prompt = build_prompt(task["problem"], fs_text)
        rec = {
            "key": key,
            "set": task["set"],
            "snapshot": task["snapshot"],
            "matched100": task["matched100"],
            "orig_v4_id": vid,
            "pair_index": idx,
            "model": a.model,
            "effort": effort,
            "slug": slug,
            "harness": f"none (agy 1.5.15 --disable-slash-commands --new-project --effort {effort}, permission_mode=request-review, num_turns=1, 1 attempt)",
            "route": "Antigravity CLI (agy) personal subscription on Mac",
            "timestamp": now_stamp(),
        }
        t0 = time.time()
        try:
            rc, stdout, stderr = call_agy(a.model, effort, prompt, timeout_s=a.timeout)
            if a.save_raw_events:
                ed = Path(a.save_raw_events)
                ed.mkdir(parents=True, exist_ok=True)
                (ed / f"{slug}_{key.replace(':', '_')}.json").write_text(stdout, encoding="utf-8")
            parsed = parse_json_output(stdout)
            if not parsed.get("ok_parse"):
                rec.update(ok=False, rc=rc, error=parsed.get("error"), tool_calls=0, tool_violation=False, secs=round(time.time() - t0, 2), stderr_tail=(stderr or "")[-200:])
            else:
                text = parsed["text"]
                tool_viol = parsed["tool_violation"]
                ok = (
                    (rc == 0)
                    and bool(text.strip())
                    and not tool_viol
                    and (parsed["num_turns"] == 1)
                    and (str(parsed["agy_status"] or "").upper() == "SUCCESS")
                )
                rec.update(
                    ok=ok,
                    rc=rc,
                    output=text,
                    tool_calls=parsed["tool_calls"],
                    tool_violation=tool_viol,
                    num_turns=parsed["num_turns"],
                    agy_status=parsed["agy_status"],
                    conversation_id=parsed["conversation_id"],
                    usage=parsed["usage"],
                    secs=round(time.time() - t0, 2),
                    stderr_tail=(stderr or "")[-200:] if not ok else "",
                )
                if not ok:
                    rec["error"] = parsed.get("error") or f"rc={rc} status={parsed['agy_status']} turns={parsed['num_turns']} len={len(text)}"
        except subprocess.TimeoutExpired:
            rec.update(ok=False, error=f"TimeoutExpired ({a.timeout}s)", tool_calls=0, tool_violation=False, secs=round(time.time() - t0, 2))
        except Exception as e:
            rec.update(ok=False, error=f"{type(e).__name__}: {str(e)[:250]}", tool_calls=0, tool_violation=False, secs=round(time.time() - t0, 2))

        with lock:
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            state["n"] += 1
            if rec.get("ok"):
                state["ok"] += 1
            else:
                state["fail"] += 1
            if rec.get("tool_violation"):
                state["tool_violations"] += 1
            err_l = str(rec.get("error") or "").lower()
            if "quota" in err_l or "rate limit" in err_l or "429" in err_l or "exhausted" in err_l:
                state["stop"] = f"QUOTA_ERROR: {rec.get('error')}"
            if state["n"] % 10 == 0 or not rec.get("ok") or a.limit:
                print(
                    f"[{now_stamp()}] {slug} n={state['n']} ok={state['ok']} fail={state['fail']} "
                    f"tool_viol={state['tool_violations']} last={key} secs={rec.get('secs')} len={len(rec.get('output') or '')} "
                    f"err={str(rec.get('error') or '')[:100]}",
                    flush=True,
                )

    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(work, todo))
    fh.close()
    print(f"[{now_stamp()}] Finished {a.model}: {state}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
