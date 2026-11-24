#!/usr/bin/env python3
"""Run single-call Putnam-AXIOM evaluations via the STAIR 'bm' Gateway on skampere1.

Settings (mandated):
- Endpoint: https://aiapi-prod.stanford.edu/v1/chat/completions
- Exact model IDs: "GLM 5.3" ("GLM 5.3 Flash" returned HTTP 400 on /chat/completions), "Kimi K3", "DeepSeek V4.1 Flash 1017"
- temperature=0, max_tokens=8192, no tools, 1 attempt per problem & version (0 retries), 240s timeout
- Daily cap <= 240 calls/day across ~/.local/state/plan-router/stair-bm-spend.jsonl + this experiment
- Stop and emit stop marker if conservative estimated cumulative cost >= $15.00 USD
- Never prints, logs, or stores the API key.
"""
import argparse
import concurrent.futures as cf
import datetime
import fcntl
import gzip
import json
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

TZ_LA = ZoneInfo("America/Los_Angeles")
ENDPOINT = "https://aiapi-prod.stanford.edu/v1/chat/completions"

MODELS = [
    ("glm53", "GLM 5.3"),
    ("kimik3", "Kimi K3"),
    ("deepseekv41flash", "DeepSeek V4.1 Flash 1017"),
]

DESC = (
    "Given a mathematics question, compose a detailed solution. Simplify your answer as much as possible. "
    "Always give the final answer inside a \\boxed{answer}. Give your answer in the format: \n"
    "Final Answer: The final answer is $\\boxed{answer}$. I hope it is correct. Here are some examples:"
)

# Conservative upper-bound rate for open-model Gateway cost tracking ($1/M in, $3/M out)
RATE_IN_PER_M = 1.0
RATE_OUT_PER_M = 3.0
RESERVE_PER_INFLIGHT_USD = 0.03


def open_text(path):
    return gzip.open(path, "rt", encoding="utf-8") if str(path).endswith(".gz") else open(path, "r", encoding="utf-8")


def today_la():
    return datetime.datetime.now(TZ_LA).strftime("%Y-%m-%d")


def now_stamp():
    return datetime.datetime.now(TZ_LA).strftime("%m-%d-%Y %H:%M:%S %Z")


def build_prompt(problem, fs_text):
    return DESC + "\n\n" + fs_text + "\n\n" + "Problem:" + "\n" + problem + "\n\n" + "Solution:"


def count_pi_calls_today(pi_spend_path, day_iso):
    p = Path(pi_spend_path).expanduser()
    if not p.is_file():
        return 0
    cnt = 0
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if row.get("day") == day_iso:
                cnt += 1
        except Exception:
            continue
    return cnt


def load_ledger(ledger_path):
    p = Path(ledger_path)
    if not p.is_file():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


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


def estimate_cost_usd(in_tok, out_tok, usage_obj):
    est = ((in_tok or 0) * RATE_IN_PER_M + (out_tok or 0) * RATE_OUT_PER_M) / 1e6
    if isinstance(usage_obj, dict):
        for k in ("cost", "total_cost", "estimated_cost"):
            v = usage_obj.get(k)
            if isinstance(v, (int, float)) and v > est:
                est = float(v)
    return est


def call_gateway(key, model_id, prompt, timeout=240):
    body = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 8192,
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "User-Agent": "putnam-axiom-exp03/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--fewshot", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--status-out", required=True)
    ap.add_argument("--pi-spend", default="~/.local/state/plan-router/stair-bm-spend.jsonl")
    ap.add_argument("--key-file", default="/dfs/scratch0/brando9/keys/stanford_stair_bm_gateway_key.txt")
    ap.add_argument("--key-env", default="STAIR_BM_API_KEY")
    ap.add_argument("--daily-cap", type=int, default=240)
    ap.add_argument("--cost-cap-usd", type=float, default=15.0)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = Path(a.ledger)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    lock_path = ledger_path.with_suffix(".lock")
    lock_fd = open(lock_path, "a", encoding="utf-8")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("Another STAIR Gateway runner holds lock; exiting cleanly.", flush=True)
        return 0

    try:
        api_key = (os.environ.get(a.key_env) or "").strip()
        if not api_key and Path(a.key_file).expanduser().is_file():
            api_key = Path(a.key_file).expanduser().read_text(encoding="utf-8").strip()
        if not api_key:
            api_key = (os.environ.get("STAIR_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError("Missing STAIR Gateway key (checked env vars and --key-file)")

        fs = json.load(open(a.fewshot, "r", encoding="utf-8"))
        fs_text = "\n\n".join("Problem:\n" + e["problem"] + "\n\nSolution: " + e["solution"] for e in fs)

        tasks_by_key = {}
        with open_text(a.tasks) as f:
            for line in f:
                t = json.loads(line)
                tasks_by_key[t["key"]] = t

        manifest = json.load(open(a.manifest, "r", encoding="utf-8"))
        # Build per-model 200-task list: 100 matched originals then 100 snapshot-1 variations
        per_model_keys = []
        for entry in manifest:
            per_model_keys.append((entry["orig_key"], "orig", entry["orig_v4_id"], entry["index"]))
        for entry in manifest:
            per_model_keys.append((entry["var_snap1_key"], "var", entry["orig_v4_id"], entry["index"]))

        attempted_by_slug = {
            slug: load_attempted_keys(out_dir / f"{slug}.jsonl")
            for slug, _ in MODELS
        }

        # Order: first item (index 0 orig) for each of the 3 models (3-call smoke), then finish model-by-model
        queue = []
        seen_pair = set()
        for slug, model_id in MODELS:
            k0, split0, vid0, idx0 = per_model_keys[0]
            if k0 not in attempted_by_slug[slug]:
                queue.append((slug, model_id, k0, split0, vid0, idx0))
                seen_pair.add((slug, k0))
        for slug, model_id in MODELS:
            for k, split, vid, idx in per_model_keys:
                if (slug, k) in seen_pair or k in attempted_by_slug[slug]:
                    continue
                queue.append((slug, model_id, k, split, vid, idx))
                seen_pair.add((slug, k))

        if a.limit:
            queue = queue[: a.limit]

        day_iso = today_la()
        pi_calls_today = count_pi_calls_today(a.pi_spend, day_iso)
        ledger_rows = load_ledger(ledger_path)
        exp_calls_today = sum(1 for r in ledger_rows if r.get("day") == day_iso)
        cum_est_cost = sum(float(r.get("est_cost_usd") or 0.0) for r in ledger_rows)

        state = {
            "today_calls": pi_calls_today + exp_calls_today,
            "reserved_inflight": 0,
            "cum_est_cost": cum_est_cost,
            "stop_reason": None,
            "session_calls": 0,
            "session_ok": 0,
            "session_fail": 0,
        }
        t_lock = threading.Lock()
        fhs = {slug: open(out_dir / f"{slug}.jsonl", "a", encoding="utf-8") for slug, _ in MODELS}
        ledger_fh = open(ledger_path, "a", encoding="utf-8")

        print(
            f"[{now_stamp()}] Queue={len(queue)} pending; day={day_iso} "
            f"used_today={state['today_calls']}/{a.daily_cap} (pi={pi_calls_today}, exp={exp_calls_today}); "
            f"cum_est_cost=${state['cum_est_cost']:.4f}/${a.cost_cap_usd:.2f}",
            flush=True,
        )

        def run_one(item):
            slug, model_id, key, split, vid, idx = item
            with t_lock:
                if state["stop_reason"]:
                    return
                if state["today_calls"] + state["reserved_inflight"] >= a.daily_cap:
                    state["stop_reason"] = f"DAILY_CAP_REACHED ({a.daily_cap})"
                    return
                if state["cum_est_cost"] >= a.cost_cap_usd or (
                    state["cum_est_cost"] + (state["reserved_inflight"] + 1) * RESERVE_PER_INFLIGHT_USD > a.cost_cap_usd
                ):
                    state["stop_reason"] = f"COST_CAP_REACHED (${a.cost_cap_usd:.2f})"
                    return
                state["reserved_inflight"] += 1

            task = tasks_by_key[key]
            prompt = build_prompt(task["problem"], fs_text)
            rec = {
                "key": key,
                "set": task["set"],
                "snapshot": task["snapshot"],
                "matched100": task["matched100"],
                "orig_v4_id": vid,
                "pair_index": idx,
                "model": model_id,
                "slug": slug,
                "harness": "none (OpenAI chat completions, temperature=0, max_tokens=8192, 0 retries)",
                "route": "STAIR bm Gateway (https://aiapi-prod.stanford.edu/v1) on skampere1",
                "timestamp": now_stamp(),
            }
            t0 = time.time()
            in_tok = 0
            out_tok = 0
            est_cost = 0.0
            try:
                j = call_gateway(api_key, model_id, prompt, timeout=a.timeout)
                choice = (j.get("choices") or [{}])[0]
                msg = choice.get("message") or {}
                content = msg.get("content") or ""
                reasoning_content = msg.get("reasoning_content") or ""
                usage = j.get("usage") or {}
                in_tok = int(usage.get("prompt_tokens") or 0)
                out_tok = int(usage.get("completion_tokens") or 0)
                est_cost = estimate_cost_usd(in_tok, out_tok, usage)
                rec.update(
                    ok=True,
                    output=content,
                    reasoning_content=reasoning_content,
                    content_empty=not bool(content.strip()),
                    finish_reason=choice.get("finish_reason"),
                    actual_model=j.get("model"),
                    usage={
                        "input": in_tok,
                        "output": out_tok,
                        "total": usage.get("total_tokens"),
                        "raw": usage,
                    },
                    est_cost_usd=round(est_cost, 6),
                    secs=round(time.time() - t0, 2),
                )
            except urllib.error.HTTPError as e:
                body = ""
                try:
                    body = e.read().decode("utf-8", errors="replace")[:400]
                except Exception:
                    pass
                rec.update(ok=False, error=f"HTTP {e.code}: {body}", secs=round(time.time() - t0, 2))
            except Exception as e:
                rec.update(ok=False, error=f"{type(e).__name__}: {str(e)[:300]}", secs=round(time.time() - t0, 2))

            with t_lock:
                state["reserved_inflight"] -= 1
                state["today_calls"] += 1
                state["session_calls"] += 1
                state["cum_est_cost"] += est_cost
                if rec.get("ok"):
                    state["session_ok"] += 1
                else:
                    state["session_fail"] += 1
                fhs[slug].write(json.dumps(rec) + "\n")
                fhs[slug].flush()
                ledger_row = {
                    "day": day_iso,
                    "timestamp": rec["timestamp"],
                    "slug": slug,
                    "model": model_id,
                    "key": key,
                    "ok": rec.get("ok"),
                    "in_tokens": in_tok,
                    "out_tokens": out_tok,
                    "est_cost_usd": round(est_cost, 6),
                    "cum_est_cost_usd": round(state["cum_est_cost"], 6),
                    "error": rec.get("error"),
                }
                ledger_fh.write(json.dumps(ledger_row) + "\n")
                ledger_fh.flush()

                if state["cum_est_cost"] >= a.cost_cap_usd and not state["stop_reason"]:
                    state["stop_reason"] = f"COST_CAP_REACHED (${state['cum_est_cost']:.4f} >= ${a.cost_cap_usd:.2f})"
                if state["today_calls"] >= a.daily_cap and not state["stop_reason"]:
                    state["stop_reason"] = f"DAILY_CAP_REACHED ({state['today_calls']}/{a.daily_cap})"

                if state["session_calls"] % 10 == 0 or not rec.get("ok") or a.limit:
                    print(
                        f"[{now_stamp()}] calls={state['session_calls']} today={state['today_calls']}/{a.daily_cap} "
                        f"ok={state['session_ok']} fail={state['session_fail']} est=${state['cum_est_cost']:.4f} "
                        f"{slug}:{key} finish={rec.get('finish_reason')} len={len(rec.get('output') or '')} "
                        f"rc_len={len(rec.get('reasoning_content') or '')} err={str(rec.get('error') or '')[:100]}",
                        flush=True,
                    )

        with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
            list(ex.map(run_one, queue))

        for fh in fhs.values():
            fh.close()
        ledger_fh.close()

        counts = {slug: len(load_attempted_keys(out_dir / f"{slug}.jsonl")) for slug, _ in MODELS}
        status = {
            "updated_at": now_stamp(),
            "day": day_iso,
            "today_calls": state["today_calls"],
            "daily_cap": a.daily_cap,
            "cum_est_cost_usd": round(state["cum_est_cost"], 6),
            "cost_cap_usd": a.cost_cap_usd,
            "stop_reason": state["stop_reason"],
            "counts": counts,
            "all_600_complete": all(v == 200 for v in counts.values()),
        }
        Path(a.status_out).write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        print("FINISHED:", json.dumps(status), flush=True)
        return 2 if (state["stop_reason"] and "COST_CAP" in state["stop_reason"]) else 0
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


if __name__ == "__main__":
    raise SystemExit(main())
