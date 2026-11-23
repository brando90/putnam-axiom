#!/usr/bin/env python3
"""Plain-model Putnam-AXIOM runner (no tools, no agent): one prompt in, one answer out.

Prompt = the lm-eval-harness putnam_axiom task prompt (description + 4 few-shot examples + problem), sent as one user message.
Runs on the cluster so the API key is read from its key file at runtime and never leaves it. Resumable (appends to --out).
Example: python3 run_eval.py --provider openai --model gpt-6.2-astra --effort high --sets orig,var --out out/astra62.jsonl --workers 6
"""
import argparse, json, os, sys, time, threading, urllib.request, urllib.error, concurrent.futures as cf

DESC = ("Given a mathematics question, compose a detailed solution. Simplify your answer as much as possible. "
        "Always give the final answer inside a \\boxed{answer}. Give your answer in the format: \n"
        "Final Answer: The final answer is $\\boxed{answer}$. I hope it is correct. Here are some examples:")


def fewshot_block(fs_path):
    fs = json.load(open(fs_path))
    return "\n\n".join("Problem:\n" + e["problem"] + "\n\nSolution: " + e["solution"] for e in fs)


def build_prompt(problem, fs_text):
    return DESC + "\n\n" + fs_text + "\n\n" + "Problem:" + "\n" + problem + "\n\n" + "Solution:"


def post(url, hdr, body, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={**hdr, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def call_openai(key, model, effort, prompt, max_out, timeout):
    body = {"model": model, "input": prompt, "max_output_tokens": max_out, "store": False}
    if effort:
        body["reasoning"] = {"effort": effort}
    j = post("https://api.openai.com/v1/responses", {"Authorization": "Bearer " + key}, body, timeout)
    text = ""
    for it in j.get("output", []):
        if it.get("type") == "message":
            for c in it.get("content", []):
                if c.get("type") == "output_text":
                    text += c.get("text", "")
    u = j.get("usage", {})
    return text, {"input": u.get("input_tokens"), "output": u.get("output_tokens"),
                  "reasoning": (u.get("output_tokens_details") or {}).get("reasoning_tokens"),
                  "status": j.get("status"), "incomplete": j.get("incomplete_details")}


def call_anthropic(key, model, effort, prompt, max_out, timeout):
    body = {"model": model, "max_tokens": max_out, "messages": [{"role": "user", "content": prompt}]}
    if effort:
        body["output_config"] = {"effort": effort}
    j = post("https://api.anthropic.com/v1/messages", {"x-api-key": key, "anthropic-version": "2023-06-01"}, body, timeout)
    text = "".join(b.get("text", "") for b in j.get("content", []) if b.get("type") == "text")
    u = j.get("usage", {})
    return text, {"input": u.get("input_tokens"), "output": u.get("output_tokens"), "status": j.get("stop_reason")}


def call_gemini(key, model, effort, prompt, max_out, timeout):
    gc = {"maxOutputTokens": max_out}
    if effort:
        gc["thinkingConfig"] = {"thinkingLevel": effort}
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": gc}
    j = post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", {"x-goog-api-key": key}, body, timeout)
    cand = (j.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts", []) if not p.get("thought"))
    u = j.get("usageMetadata", {})
    return text, {"input": u.get("promptTokenCount"), "output": (u.get("candidatesTokenCount") or 0) + (u.get("thoughtsTokenCount") or 0),
                  "reasoning": u.get("thoughtsTokenCount"), "status": cand.get("finishReason"), "incomplete": None}


def call_claude_cli(key, model, effort, prompt, max_out, timeout):
    import subprocess
    cmd = [key, "-p", "--safe-mode", "--model", model]
    if effort:
        cmd += ["--effort", effort]
    cmd += ["--tools", "", "--output-format", "json", "--no-session-persistence",
            "--system-prompt", "You are a helpful assistant."]
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd="/tmp")
    out = p.stdout
    j = json.loads(out[out.find("{"):] if "{" in out else "{}") if out.strip() else {}
    if not j or j.get("is_error"):
        err_prefix = f"{j.get('api_error')}: " if j and j.get("api_error") else ""
        err_msg = (j.get("result") if j else None) or p.stderr or out or f"returncode={p.returncode}"
        raise RuntimeError((err_prefix + str(err_msg))[:300])
    u = j.get("usage", {})
    return j.get("result", ""), {"input": (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0),
                                 "output": u.get("output_tokens"), "reasoning": (u.get("output_tokens_details") or {}).get("thinking_tokens"),
                                 "status": j.get("stop_reason"), "incomplete": None, "cost_usd": j.get("total_cost_usd"),
                                 "actual_models": sorted((j.get("modelUsage") or {}).keys())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True, choices=["openai", "anthropic", "gemini", "claude_cli"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--effort", default=None)
    ap.add_argument("--key-file", required=True)
    ap.add_argument("--tasks", default="tasks.jsonl")
    ap.add_argument("--fewshot", default="fewshot.json")
    ap.add_argument("--sets", default="orig,var")
    ap.add_argument("--snapshots", default="1,2,3,4,5")
    ap.add_argument("--order", default="matched,var1,orig,var2345", help="priority order of groups")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-out", type=int, default=100000)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--output-token-budget", type=int, default=0, help="stop launching new requests after this many output tokens in total (0 = no cap)")
    a = ap.parse_args()
    key = a.key_file if a.provider == "claude_cli" else open(a.key_file).read().strip()
    fs_text = fewshot_block(a.fewshot)
    tasks = [json.loads(l) for l in open(a.tasks)]
    sets = set(a.sets.split(","))
    snaps = set(int(x) for x in a.snapshots.split(","))
    tasks = [t for t in tasks if t["set"] in sets and (t["set"] != "var" or t["snapshot"] in snaps)]
    grp = {"matched": lambda t: t["set"] == "orig" and t["matched100"],
           "var1": lambda t: t["set"] == "var" and t["snapshot"] == 1,
           "orig": lambda t: t["set"] == "orig" and not t["matched100"],
           "var2345": lambda t: t["set"] == "var" and t["snapshot"] != 1}
    ordered, seen = [], set()
    for g in a.order.split(","):
        for t in tasks:
            if t["key"] not in seen and grp[g](t):
                ordered.append(t); seen.add(t["key"])
    done = set()
    if os.path.exists(a.out):
        for l in open(a.out):
            try:
                r = json.loads(l)
                if r.get("ok"):
                    done.add(r["key"])
            except Exception:
                pass
    todo = [t for t in ordered if t["key"] not in done]
    if a.limit:
        todo = todo[:a.limit]
    print(f"{len(ordered)} tasks, {len(done)} done, {len(todo)} to run", flush=True)
    lock = threading.Lock()
    stat = {"out": 0, "n": 0, "fail": 0, "stop": False}
    call = {"openai": call_openai, "anthropic": call_anthropic, "gemini": call_gemini, "claude_cli": call_claude_cli}[a.provider]
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    fh = open(a.out, "a")

    def work(t):
        if stat["stop"]:
            return
        if a.output_token_budget and stat["out"] >= a.output_token_budget:
            stat["stop"] = True
            return
        prompt = build_prompt(t["problem"], fs_text)
        rec = {"key": t["key"], "set": t["set"], "snapshot": t["snapshot"], "matched100": t["matched100"],
               "model": a.model, "effort": a.effort, "provider": a.provider}
        for attempt in range(6):
            t0 = time.time()
            try:
                text, u = call(key, a.model, a.effort, prompt, a.max_out, a.timeout)
                rec.update(ok=True, output=text, usage=u, secs=round(time.time() - t0, 1))
                break
            except urllib.error.HTTPError as e:
                body = e.read().decode()[:400]
                rec.update(ok=False, error=f"HTTP {e.code}: {body}")
                if e.code in (401, 403) or "insufficient_quota" in body or "invalid_request" in body or e.code == 400 or e.code == 404:
                    stat["stop"] = True
                    break
                time.sleep(min(120, 8 * 2 ** attempt))
            except Exception as e:
                msg = str(e)
                el = msg.lower()
                rec.update(ok=False, error=f"{type(e).__name__}: {msg[:300]}")
                if (
                    ("hit your" in el and "limit" in el)
                    or "usage_limit_reached" in el
                    or "usage credits required" in el
                    or "out of extra usage" in el
                    or "weekly limit" in el
                    or "not logged in" in el
                ):
                    stat["stop"] = True
                    break
                time.sleep(min(120, 8 * 2 ** attempt))
        with lock:
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            stat["n"] += 1
            if rec.get("ok"):
                stat["out"] += (rec["usage"].get("output") or 0)
            else:
                stat["fail"] += 1
            if stat["n"] % 10 == 0 or not rec.get("ok"):
                print(f"[{time.strftime('%H:%M:%S')}] n={stat['n']} fail={stat['fail']} out_tokens={stat['out']} last={rec['key']} {rec.get('error','')[:200]}", flush=True)

    with cf.ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(work, todo))
    print("finished", stat, flush=True)


if __name__ == "__main__":
    main()
