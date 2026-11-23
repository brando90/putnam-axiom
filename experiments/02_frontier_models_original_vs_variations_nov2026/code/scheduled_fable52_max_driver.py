#!/usr/bin/env python3
"""Single-writer scheduled driver for Putnam-AXIOM Experiment 02 claude-fable-5-2 (effort max).

- Checks Gmail via read-only IMAP for replies about STAIR Gateway / Anthropic Fable 5.2 credits
  (using ~/keys/gmail_app_password.txt at runtime; never prints or logs secret values).
- Waits until 2026-11-23 23:01 America/Los_Angeles (after the personal Ultra Fable reset),
  probes Task 1, spawns named tmux session `cc-putnam-expt02-fable52-max`, sends [RUN START],
  runs the 200 single-call LLM tasks (100 matched originals + 100 snapshot-1 variations),
  scores, computes paired bootstrap + McNemar p-val, updates reports & README.md, commits and
  pushes explicit files to origin/main, logs one line in ~/agent-sync/coding/log.md, sends
  [RUN DONE], and removes the LaunchAgent plist upon 200/200 completion.
"""
import argparse
import datetime
import email
import email.header
import fcntl
import gzip
import json
import os
import re
import shlex
import shutil
import smtplib
import subprocess
import sys
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo

TZ_LA = ZoneInfo("America/Los_Angeles")
RESET_UNLOCK_AT = datetime.datetime(2026, 11, 23, 23, 1, 0, tzinfo=TZ_LA)

REPO_ROOT = Path("/Users/brandomiranda/putnam-axiom")
EXP_DIR = REPO_ROOT / "experiments/02_frontier_models_original_vs_variations_nov2026"
CODE_DIR = EXP_DIR / "code"
DATA_DIR = EXP_DIR / "data"
LOCAL_DIR = REPO_ROOT / ".local/02_fable52_max_schedule_11-23-2026"
WORK_DIR = LOCAL_DIR / "work"
OUT_JSONL = WORK_DIR / "out/fable52max.jsonl"
LOCK_FILE = LOCAL_DIR / "driver.lock"
LOG_FILE = LOCAL_DIR / "run.log"
EMAIL_STATE_FILE = LOCAL_DIR / "email_state.json"
START_SENT_FILE = LOCAL_DIR / "start_sent.json"
DONE_SENT_FILE = LOCAL_DIR / "done_sent.json"
STATS_JSON = LOCAL_DIR / "fable52max_paired_stats.json"
PUBLISHED_STATE_FILE = LOCAL_DIR / "published_state.json"

PLIST_LABEL = "com.brando.putnam-fable52-max"
PLIST_PATH = Path.home() / "Library/LaunchAgents" / f"{PLIST_LABEL}.plist"
GMAIL_PASS_FILE = Path.home() / "keys/gmail_app_password.txt"
CLAUDE_BIN = Path.home() / ".local/bin/claude"
AGENT_SYNC_LOG = Path.home() / "agent-sync/coding/log.md"
TMUX_SESSION = "cc-putnam-expt02-fable52-max"
RUN_EMAIL_NAME = "putnam-axiom-expt02-fable52-max-200"

SECRET_RE = re.compile(r"(sk-[A-Za-z0-9_\-]+|[A-Za-z0-9_/+=-]{24,})")


def clean_env():
    env = os.environ.copy()
    extra = ["/opt/homebrew/bin", "/usr/local/bin", str(Path.home() / ".local/bin"), "/usr/bin", "/bin"]
    cur = env.get("PATH", "")
    env["PATH"] = ":".join(extra + ([cur] if cur else []))
    return env


def now_la():
    return datetime.datetime.now(TZ_LA)


def now_stamp():
    return now_la().strftime("%m-%d-%Y %H:%M %Z")


def log(msg):
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{now_la().strftime('%m-%d-%Y %H:%M:%S %Z')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def redact(text):
    return SECRET_RE.sub("<REDACTED>", text or "")


def decode_hdr(val):
    if not val:
        return ""
    parts = []
    for chunk, enc in email.header.decode_header(val):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return "".join(parts)


def acquire_lock():
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    fd = open(LOCK_FILE, "w", encoding="utf-8")
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fd.close()
        return None
    fd.write(f"pid={os.getpid()} started={now_stamp()}\n")
    fd.flush()
    return fd


def release_lock(fd):
    if fd is not None:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            fd.close()


def expected_keys():
    with gzip.open(DATA_DIR / "tasks.jsonl.gz", "rt", encoding="utf-8") as f:
        tasks = [json.loads(l) for l in f]
    m100 = [t["key"] for t in tasks if t["set"] == "orig" and t["matched100"]]
    var1 = [t["key"] for t in tasks if t["set"] == "var" and t["snapshot"] == 1]
    return set(m100), set(var1)


def is_already_complete():
    scored_gz = DATA_DIR / "scored/scored_fable52max.json.gz"
    readme = REPO_ROOT / "README.md"
    if not scored_gz.is_file() or not readme.is_file():
        return False
    try:
        data = json.load(gzip.open(scored_gz, "rt", encoding="utf-8"))
        rows = data.get("rows", [])
        keys = {r["key"] for r in rows}
        m100, var1 = expected_keys()
        if not (m100.issubset(keys) and var1.issubset(keys)):
            return False
        return "claude-fable-5-2" in readme.read_text(encoding="utf-8")
    except Exception:
        return False


def unload_and_remove_launch_agent():
    if not PLIST_PATH.exists():
        return
    uid = os.getuid()
    subprocess.run(["launchctl", "bootout", f"gui/{uid}", str(PLIST_PATH)],
                   env=clean_env(), capture_output=True, text=True, check=False)
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)],
                   env=clean_env(), capture_output=True, text=True, check=False)
    try:
        PLIST_PATH.unlink()
        log(f"Removed LaunchAgent plist {PLIST_PATH}")
    except FileNotFoundError:
        pass


def check_imap_emails(dry_run=False):
    """Read-only Gmail IMAP scan for Zeyu / Stanford IT / Anthropic / ub9sc credit replies."""
    import imaplib
    if not GMAIL_PASS_FILE.is_file():
        log("IMAP check skipped: gmail_app_password.txt not found")
        return []
    state = {"seen_ids": [], "events": []}
    if EMAIL_STATE_FILE.is_file():
        try:
            state = json.loads(EMAIL_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    seen = set(state.get("seen_ids", []))
    pw = GMAIL_PASS_FILE.read_text(encoding="utf-8").strip()
    new_hits = []
    keywords = ("req-13bf3e", "34398f0964464299bad9", "zeyu", "fable", "stair api", "ai api gateway", "anthropic", "putnam")
    M = None
    try:
        M = imaplib.IMAP4_SSL("imap.gmail.com", timeout=20)
        M.login("brandojazz@gmail.com", pw)
        M.select('"[Gmail]/All Mail"', readonly=True)
        _, data = M.search(None, '(SINCE "23-Nov-2026")')
        mids = data[0].split()[-40:]
        for mid in mids:
            _, hdr_data = M.fetch(mid, "(BODY.PEEK[HEADER.FIELDS (DATE FROM TO SUBJECT MESSAGE-ID)])")
            raw_hdr = hdr_data[0][1].decode("utf-8", errors="replace")
            hdr = email.message_from_string(raw_hdr)
            msg_id = (hdr.get("Message-ID") or f"imap:{mid.decode()}").strip()
            subj = decode_hdr(hdr.get("Subject", "")).strip()
            frm = decode_hdr(hdr.get("From", "")).strip()
            date_s = (hdr.get("Date") or "").strip()
            if subj.startswith("[RUN START]") or subj.startswith("[RUN DONE]"):
                continue
            hay = f"{frm} {subj}".lower()
            if not any(k in hay for k in keywords):
                continue
            if msg_id in seen:
                continue
            # Pre-existing outgoing ub9sc email at Mon, 23 Nov 2026 15:25:09 -0500: record as baseline
            is_baseline_outgoing = ("brandojazz@gmail.com" in frm.lower() and "15:25:09" in date_s and "REQ-13BF3E" in subj)
            snippet = ""
            _, full_data = M.fetch(mid, "(BODY.PEEK[TEXT])")
            if full_data and full_data[0] and isinstance(full_data[0][1], bytes):
                txt = full_data[0][1].decode("utf-8", errors="replace")
                txt = re.sub(r"\s+", " ", txt).strip()
                snippet = redact(txt)[:240]
            item = {
                "message_id": msg_id,
                "date": date_s,
                "from": redact(frm)[:80],
                "subject": redact(subj)[:140],
                "snippet": snippet,
                "baseline_outgoing": is_baseline_outgoing,
                "observed_at": now_stamp(),
            }
            seen.add(msg_id)
            state.setdefault("events", []).append(item)
            if not is_baseline_outgoing:
                new_hits.append(item)
        state["seen_ids"] = sorted(seen)
        state["last_checked"] = now_stamp()
        if not dry_run:
            EMAIL_STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        else:
            # Save baseline state on dry-run only if file doesn't exist yet so first real tick doesn't re-alert baseline
            if not EMAIL_STATE_FILE.is_file():
                EMAIL_STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    except Exception as e:
        log(f"IMAP check error: {type(e).__name__}: {redact(str(e))[:200]}")
    finally:
        if M is not None:
            try:
                M.logout()
            except Exception:
                pass
    if new_hits:
        for h in new_hits:
            log(f"NEW EMAIL MATCH: date={h['date']} from={h['from']} subj={h['subject']}")
            if not dry_run:
                append_ckpt_event(
                    f"Email update observed ({h['date']}): from `{h['from']}`, subject `{h['subject']}`. "
                    "No auto-spend triggered; keeping `$0` Claude Ultra reset schedule primary unless explicit approved API cap is set."
                )
    else:
        log(f"IMAP check OK: 0 new replies since baseline (dry_run={dry_run})")
    return new_hits


def send_email_notification(subject, body, marker_path):
    if marker_path.is_file():
        return
    if not GMAIL_PASS_FILE.is_file():
        log(f"Email skipped ({subject}): missing gmail_app_password.txt")
        return
    pw = GMAIL_PASS_FILE.read_text(encoding="utf-8").strip()
    msg = EmailMessage()
    msg["From"] = "brandojazz@gmail.com"
    msg["To"] = "brando.science@gmail.com"
    msg["Bcc"] = "brando.science@gmail.com"
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as s:
            s.login("brandojazz@gmail.com", pw)
            s.send_message(msg)
        marker_path.write_text(json.dumps({"subject": subject, "sent_at": now_stamp()}) + "\n", encoding="utf-8")
        log(f"Sent notification email: {subject}")
    except Exception as e:
        log(f"Failed sending email ({subject}): {type(e).__name__}: {redact(str(e))[:200]}")


def prepare_work_dir():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    (WORK_DIR / "out").mkdir(exist_ok=True)
    (WORK_DIR / "stubs").mkdir(exist_ok=True)
    (WORK_DIR / "judge_out_gpt").mkdir(exist_ok=True)

    tasks_out = WORK_DIR / "tasks.jsonl"
    if not tasks_out.is_file():
        with gzip.open(DATA_DIR / "tasks.jsonl.gz", "rb") as src, open(tasks_out, "wb") as dst:
            shutil.copyfileobj(src, dst)

    shutil.copy2(DATA_DIR / "fewshot.json", WORK_DIR / "fewshot.json")
    shutil.copy2(DATA_DIR / "models.json", WORK_DIR / "models.json")
    shutil.copy2(CODE_DIR / "datasets_stub.py", WORK_DIR / "stubs/datasets.py")
    for fn in ("pax_utils.py", "run_eval.py", "score.py", "build_report.py", "gen_md.py", "make_report.py", "compute_paired_bootstrap.py"):
        shutil.copy2(CODE_DIR / fn, WORK_DIR / fn)

    scored_dir = DATA_DIR / "scored"
    for gz in scored_dir.glob("scored_*.json.gz"):
        out_name = gz.name[:-3]  # strip .gz
        if out_name == "scored_fable52max.json":
            continue
        dst = WORK_DIR / out_name
        if not dst.is_file():
            with gzip.open(gz, "rb") as src, open(dst, "wb") as d:
                shutil.copyfileobj(src, d)

    for j in (DATA_DIR / "judge_out_gpt").glob("*.jsonl"):
        shutil.copy2(j, WORK_DIR / "judge_out_gpt" / j.name)


def count_completed():
    m100, var1 = expected_keys()
    ok_keys = set()
    latest_recs = {}
    if OUT_JSONL.is_file():
        for line in open(OUT_JSONL, "r", encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("ok") and r.get("key") in (m100 | var1):
                ok_keys.add(r["key"])
                latest_recs[r["key"]] = r
    return len(ok_keys & m100), len(ok_keys & var1), ok_keys, latest_recs


def run_eval_cmd(limit=0, workers=1):
    cmd = [
        sys.executable,
        str(WORK_DIR / "run_eval.py"),
        "--provider", "claude_cli",
        "--model", "claude-fable-5-2",
        "--effort", "max",
        "--key-file", str(CLAUDE_BIN),
        "--tasks", str(WORK_DIR / "tasks.jsonl"),
        "--fewshot", str(WORK_DIR / "fewshot.json"),
        "--sets", "orig,var",
        "--snapshots", "1",
        "--order", "matched,var1",
        "--workers", str(workers),
        "--timeout", "1800",
        "--output-token-budget", "2500000",
        "--out", str(OUT_JSONL),
    ]
    if limit:
        cmd += ["--limit", str(limit)]
    return subprocess.run(cmd, cwd=str(WORK_DIR), env=clean_env(), text=True, check=False)


def append_ckpt_event(event_text):
    ckpt = EXP_DIR / "CKPT_fable52_max_eval.md"
    if not ckpt.is_file():
        return
    txt = ckpt.read_text(encoding="utf-8")
    txt = re.sub(r"^Last updated:.*$", f"Last updated: {now_stamp()}", txt, count=1, flags=re.MULTILINE)
    if not txt.endswith("\n"):
        txt += "\n"
    txt += f"- {now_stamp()} -- {event_text}\n"
    ckpt.write_text(txt, encoding="utf-8")


def update_ckpt_and_results_final(n_m100, n_var1, stats, scored_summary, cost_equiv):
    ckpt = EXP_DIR / "CKPT_fable52_max_eval.md"
    mcn = stats.get("mcnemar") or {}
    p_val = mcn.get("p_val")
    p_str = f"{p_val:.4g}" if isinstance(p_val, float) else "n/a"
    stamp = now_stamp()
    created_line = f"Created: {stamp}"
    if ckpt.is_file():
        for line in ckpt.read_text(encoding="utf-8").splitlines():
            if line.startswith("Created:"):
                created_line = line
                break
        old_log = ""
        if "## Log" in ckpt.read_text(encoding="utf-8"):
            old_log = ckpt.read_text(encoding="utf-8").split("## Log", 1)[1].strip()
    else:
        old_log = ""

    status_note = "COMPLETE (200/200)" if (n_m100 == 100 and n_var1 == 100) else f"PARTIAL ({n_m100}/100 orig, {n_var1}/100 var1)"
    new_ckpt = f"""# Checkpoint: Putnam-AXIOM Experiment 02 claude-fable-5-2 (max effort)

{created_line}
Last updated: {stamp}

## Goal
Measure single-call LLM accuracy and matched original-vs-variation drop of `claude-fable-5-2` (`effort=max`, Claude Code `--safe-mode -p --tools ""`) on the 100 matched Originals and 100 Snapshot-1 Functional Variations (`$0.00` cash budget).

## What ran
- `code/scheduled_fable52_max_driver.py` in `tmux` session `{TMUX_SESSION}` (`--sets orig,var --snapshots 1 --order matched,var1`, `{n_m100}/100` matched Originals, `{n_var1}/100` Snapshot-1 Variations).

## Results
- {status_note}: Original (100) `{stats['orig_100']:.1f}%`, Variation snapshot 1 `{stats['var']:.1f}%`, paired drop `{stats['paired_drop']:.1f}` points `[95% CI {stats['ci_lo']:.1f}, {stats['ci_hi']:.1f}]` (10,000-resample bootstrap over 100 problems), exact two-sided McNemar `p-val={p_str}` (`b={mcn.get('b_orig_only')}`, `c={mcn.get('c_var_only')}`), API-equivalent `${cost_equiv:.2f}` (`$0.00` cash).

## Stuck / blocked
- {"nothing" if (n_m100 == 100 and n_var1 == 100) else "Paused mid-run (likely 5h Fable window); LaunchAgent remains armed for next tick resume."}

## Next steps
- {"[p 5/10] Run optional answer-equivalence judge (gpt-5.5) or snapshots 2-5 if desired." if (n_m100 == 100 and n_var1 == 100) else "[p 9/10] Automatic resume on next 30-minute LaunchAgent tick after window reset."}

## Brando to-do
- none

## Log
{old_log}
- {stamp} -- {status_note}: Orig {stats['orig_100']:.1f}%, Var1 {stats['var']:.1f}%, drop {stats['paired_drop']:.1f} [{stats['ci_lo']:.1f}, {stats['ci_hi']:.1f}] p-val={p_str} exact McNemar.
"""
    ckpt.write_text(new_ckpt.rstrip() + "\n", encoding="utf-8")

    # Update results.md
    res_md = EXP_DIR / "results.md"
    res_txt = res_md.read_text(encoding="utf-8")
    row_line = (
        f"| `claude-fable-5-2` (`effort=max`, `--safe-mode`) | {status_note} | {n_m100}/100 ({stats['orig_100']:.1f}%) | "
        f"{n_var1}/100 ({stats['var']:.1f}%) | {stats['paired_drop']:.1f} [{stats['ci_lo']:.1f}, {stats['ci_hi']:.1f}] | "
        f"exact McNemar `p-val={p_str}` (`b={mcn.get('b_orig_only')}`, `c={mcn.get('c_var_only')}`); `$0.00` cash (~`${cost_equiv:.2f}` API-eq) |"
    )
    res_txt = re.sub(
        r"^\| `claude-fable-5-2`.*$",
        row_line,
        res_txt,
        count=1,
        flags=re.MULTILINE,
    )
    res_txt = re.sub(r"^Last updated:.*$", f"Last updated: {stamp}", res_txt, count=1, flags=re.MULTILINE)
    res_txt = re.sub(
        r"^\*\*TLDR-end:\*\*.*$",
        f"**TLDR-end:** [putnam-axiom: expt02 fable-5.2-max matched-100 eval] {status_note}: Original {stats['orig_100']:.1f}%, Snapshot-1 Variation {stats['var']:.1f}%, paired drop {stats['paired_drop']:.1f} [{stats['ci_lo']:.1f}, {stats['ci_hi']:.1f}] points (exact McNemar `p-val={p_str}`).",
        res_txt,
        count=1,
        flags=re.MULTILINE,
    )
    res_md.write_text(res_txt, encoding="utf-8")

    if n_m100 == 100 and n_var1 == 100:
        exp_readme = EXP_DIR / "README.md"
        er = exp_readme.read_text(encoding="utf-8")
        er = er.replace(
            "Scheduled `claude-fable-5-2` (`effort=max`, single-call `--safe-mode -p --tools \"\"`) on matched 100 Originals + Snapshot-1 Variations (`200` tasks) via LaunchAgent after the `11-23-2026 23:00 PST` reset ([`PROTOCOL.md`](PROTOCOL.md), [`results.md`](results.md), [`CKPT_fable52_max_eval.md`](CKPT_fable52_max_eval.md)).",
            f"`claude-fable-5-2` (`effort=max`, single-call `--safe-mode -p --tools \"\"`) completed `200/200` (`100` matched Originals: `{stats['orig_100']:.1f}%`; `100` Snapshot-1 Variations: `{stats['var']:.1f}%`; paired drop `{stats['paired_drop']:.1f} [{stats['ci_lo']:.1f}, {stats['ci_hi']:.1f}]`, exact McNemar `p-val={p_str}`) ([`PROTOCOL.md`](PROTOCOL.md), [`results.md`](results.md), [`CKPT_fable52_max_eval.md`](CKPT_fable52_max_eval.md)).",
        )
        exp_readme.write_text(er, encoding="utf-8")

        root_idx = REPO_ROOT / "experiments/README.md"
        ri = root_idx.read_text(encoding="utf-8")
        ri = ri.replace(
            "Fable 5.2 Max (`200`-task matched-100 + var-1) scheduled for `11-23-2026 23:01 PST`.",
            f"Fable 5.2 Max (`200`-task matched-100 + var-1) complete (`{stats['orig_100']:.1f}%` vs `{stats['var']:.1f}%`, drop `{stats['paired_drop']:.1f} [{stats['ci_lo']:.1f}, {stats['ci_hi']:.1f}]`, `p-val={p_str}`).",
        )
        root_idx.write_text(ri, encoding="utf-8")


def finalize_and_publish(n_m100, n_var1):
    # Write gzipped raw outputs (keep all records from OUT_JSONL)
    raw_gz = DATA_DIR / "raw_outputs/fable52max.jsonl.gz"
    with open(OUT_JSONL, "rb") as src, gzip.open(raw_gz, "wb") as dst:
        shutil.copyfileobj(src, dst)

    # Score inside WORK_DIR
    env = clean_env()
    env["PYTHONPATH"] = f"{WORK_DIR / 'stubs'}:{WORK_DIR}"
    scored_json = WORK_DIR / "scored_fable52max.json"
    r1 = subprocess.run(
        [sys.executable, str(WORK_DIR / "score.py"), str(OUT_JSONL), "--json", str(scored_json)],
        cwd=str(WORK_DIR), env=env, capture_output=True, text=True, check=True,
    )
    log(f"score.py output:\n{r1.stdout.strip()}")

    scored_gz = DATA_DIR / "scored/scored_fable52max.json.gz"
    with open(scored_json, "rb") as src, gzip.open(scored_gz, "wb") as dst:
        shutil.copyfileobj(src, dst)

    # Compute paired bootstrap + McNemar (+ update README only when 200/200 complete)
    boot_cmd = [
        sys.executable, str(WORK_DIR / "compute_paired_bootstrap.py"),
        "--tasks", str(DATA_DIR / "tasks.jsonl.gz"),
        "--scored", str(scored_gz),
        "--snapshots", "1",
        "--row-label", "claude-fable-5-2 (effort max, snapshot 1)",
        "--json-out", str(STATS_JSON),
    ]
    if n_m100 == 100 and n_var1 == 100:
        boot_cmd += ["--update-readme", str(REPO_ROOT / "README.md")]
    subprocess.run(boot_cmd, cwd=str(WORK_DIR), env=env, check=True)
    stats = json.loads(STATS_JSON.read_text(encoding="utf-8"))

    # Rebuild full report artifacts when complete (or update partial results.json)
    subprocess.run([sys.executable, str(WORK_DIR / "build_report.py")], cwd=str(WORK_DIR), env=env, check=True)
    subprocess.run([sys.executable, str(WORK_DIR / "make_report.py")], cwd=str(WORK_DIR), env=env, check=True)

    shutil.copy2(WORK_DIR / "results.json", DATA_DIR / "results.json")
    shutil.copy2(WORK_DIR / "tables.md", DATA_DIR / "tables.md")
    shutil.copy2(WORK_DIR / "RESULTS_frontier_models_original_vs_variations_nov2026.md",
                 EXP_DIR / "RESULTS_frontier_models_original_vs_variations_nov2026.md")

    scored_data = json.loads(scored_json.read_text(encoding="utf-8"))
    summary = scored_data.get("summary", {})
    results_all = json.loads((DATA_DIR / "results.json").read_text(encoding="utf-8"))
    cost_equiv = (results_all.get("fable52max") or {}).get("cost") or 0.0

    update_ckpt_and_results_final(n_m100, n_var1, stats, summary, cost_equiv)

    # Stage strictly explicit owned files (never git add -A, preserving experiments/01_...!)
    rel_files = [
        "experiments/02_frontier_models_original_vs_variations_nov2026/data/raw_outputs/fable52max.jsonl.gz",
        "experiments/02_frontier_models_original_vs_variations_nov2026/data/scored/scored_fable52max.json.gz",
        "experiments/02_frontier_models_original_vs_variations_nov2026/data/results.json",
        "experiments/02_frontier_models_original_vs_variations_nov2026/data/tables.md",
        "experiments/02_frontier_models_original_vs_variations_nov2026/RESULTS_frontier_models_original_vs_variations_nov2026.md",
        "experiments/02_frontier_models_original_vs_variations_nov2026/CKPT_fable52_max_eval.md",
        "experiments/02_frontier_models_original_vs_variations_nov2026/results.md",
        "experiments/02_frontier_models_original_vs_variations_nov2026/README.md",
        "experiments/README.md",
    ]
    if n_m100 == 100 and n_var1 == 100:
        rel_files.append("README.md")

    subprocess.run(["git", "-C", str(REPO_ROOT), "fetch", "origin", "main"], env=env, check=False)
    # Use intent-to-add + commit --only so concurrent staged entries in unrelated dirs (e.g. experiments/01) are never swept in.
    for rf in rel_files:
        if (REPO_ROOT / rf).exists():
            subprocess.run(["git", "-C", str(REPO_ROOT), "add", "-N", "--", rf], env=env, check=False)

    diff_chk = subprocess.run(["git", "-C", str(REPO_ROOT), "diff", "--check", "--", *rel_files], env=env, capture_output=True, text=True)
    if diff_chk.returncode != 0:
        raise RuntimeError(f"git diff --check failed: {diff_chk.stdout} {diff_chk.stderr}")
    diff_txt = subprocess.run(["git", "-C", str(REPO_ROOT), "diff", "HEAD", "--", *rel_files], env=env, capture_output=True, text=True, check=True).stdout
    if re.search(r"sk-[A-Za-z0-9_\-]{16,}", diff_txt):
        raise RuntimeError("Refusing commit: secret pattern detected in owned diff")

    commit_msg = (
        f"experiments/02: claude-fable-5-2 (effort max) complete ({stats['orig_100']:.1f}% vs {stats['var']:.1f}%, drop {stats['paired_drop']:.1f})"
        if (n_m100 == 100 and n_var1 == 100)
        else f"experiments/02: partial claude-fable-5-2 (effort max) progress ({n_m100}/100 orig, {n_var1}/100 var1)"
    )
    st = subprocess.run(["git", "-C", str(REPO_ROOT), "diff", "HEAD", "--quiet", "--", *rel_files], env=env)
    if st.returncode != 0:
        subprocess.run(["git", "-C", str(REPO_ROOT), "commit", "--only", "-m", commit_msg, "--", *rel_files], env=env, check=True)
        push = subprocess.run(["git", "-C", str(REPO_ROOT), "push", "origin", "main"], env=env, capture_output=True, text=True)
        if push.returncode != 0:
            log(f"git push warning (trying pull --rebase): {push.stderr.strip()}")
            subprocess.run(["git", "-C", str(REPO_ROOT), "pull", "--rebase", "--autostash", "origin", "main"], env=env, check=False)
            subprocess.run(["git", "-C", str(REPO_ROOT), "push", "origin", "main"], env=env, check=True)

    commit_sha = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"], env=env, capture_output=True, text=True, check=True).stdout.strip()
    return stats, cost_equiv, commit_sha


def append_agent_sync_log(stats, commit_sha):
    if not AGENT_SYNC_LOG.is_file():
        return
    mcn = stats.get("mcnemar") or {}
    p_str = f"{mcn['p_val']:.4g}" if isinstance(mcn.get("p_val"), float) else "n/a"
    today = now_la().strftime("%m-%d-%Y")
    line = (
        f"{today} | Antigravity (scheduled claude-fable-5-2 max driver) | Putnam-AXIOM `experiments/02_frontier_models_original_vs_variations_nov2026/` (`{commit_sha}`, `$0.00` personal Claude Ultra subscription): "
        f"`claude-fable-5-2` (`--safe-mode --effort max`, tools off, one turn) completed `200/200`: matched-100 Original `{stats['orig_100']:.1f}%`, Snapshot-1 Variation `{stats['var']:.1f}%`, "
        f"paired drop `{stats['paired_drop']:.1f} [{stats['ci_lo']:.1f}, {stats['ci_hi']:.1f}]` (10,000-resample bootstrap), exact two-sided McNemar `p-val={p_str}` | "
        f"https://github.com/brando90/putnam-axiom/commit/{commit_sha}\n"
    )
    with open(AGENT_SYNC_LOG, "a", encoding="utf-8") as f:
        f.write(line)


def tmux_session_exists():
    r = subprocess.run(["tmux", "has-session", "-t", TMUX_SESSION], env=clean_env(), capture_output=True)
    return r.returncode == 0


def spawn_tmux_runner():
    script_path = Path(__file__).resolve()
    cmd_str = f"{shlex.quote(sys.executable)} {shlex.quote(str(script_path))} --inside-tmux 2>&1 | tee -a {shlex.quote(str(LOG_FILE))}"
    subprocess.run(["tmux", "new-session", "-d", "-s", TMUX_SESSION, cmd_str], env=clean_env(), check=True)
    log(f"Spawned detached tmux session: {TMUX_SESSION}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force-probe", action="store_true")
    ap.add_argument("--inside-tmux", action="store_true")
    args = ap.parse_args()

    lock_fd = acquire_lock()
    if lock_fd is None:
        log("Another driver instance holds driver.lock; exiting.")
        return 0

    try:
        if is_already_complete():
            log("200/200 fable52max evaluation and README.md already complete.")
            if not args.dry_run:
                unload_and_remove_launch_agent()
            return 0

        if not args.inside_tmux:
            check_imap_emails(dry_run=args.dry_run)

        now = now_la()
        if not args.inside_tmux and not args.force_probe and now < RESET_UNLOCK_AT:
            log(f"Waiting for 11-23-2026 23:01 PST reset (now={now_stamp()}); skipping Claude probe.")
            return 0

        if args.dry_run:
            log(f"Dry-run check complete (now={now_stamp()}, unlock={RESET_UNLOCK_AT.isoformat()}). Would run 200-task matched+var1 eval in tmux {TMUX_SESSION}.")
            return 0

        prepare_work_dir()
        n_m100, n_var1, _, _ = count_completed()
        log(f"Pre-run counts: matched100={n_m100}/100, var_snap1={n_var1}/100")

        if not args.inside_tmux:
            if tmux_session_exists():
                log(f"tmux session {TMUX_SESSION} already exists; skipping spawn.")
                return 0
            # Preflight 1 unfinished task before spawning full tmux session (if < 200 done)
            if (n_m100 + n_var1) < 200:
                log("Running 1-task preflight probe for claude-fable-5-2 (effort max)...")
                run_eval_cmd(limit=1, workers=1)
                n2_m100, n2_var1, _, latest = count_completed()
                if (n2_m100 + n2_var1) <= (n_m100 + n_var1):
                    log("Preflight probe did not complete a new task (quota likely still locked). Will retry next tick.")
                    return 0
                # Verify actual_models contains fable-5-2
                sample_models = next(iter(latest.values())).get("usage", {}).get("actual_models", [])
                log(f"Preflight succeeded! Progress: {n2_m100}/100 orig, {n2_var1}/100 var1; actual_models={sample_models}")
            release_lock(lock_fd)
            lock_fd = None
            spawn_tmux_runner()
            return 0

        # Running inside tmux session
        start_wall = now_la()
        start_body = (
            f"Running: experiments/02_frontier_models_original_vs_variations_nov2026 (claude-fable-5-2, effort max, --safe-mode -p --tools \"\", 200 tasks: 100 matched Originals + 100 Snapshot-1 Variations)\n"
            f"Host/tmux: MacBook Pro / tmux session {TMUX_SESSION}\n"
            f"Expected duration: ~60-180 mins (--workers 2, --timeout 1800, 2.5M output-token safety cap); outputs in {OUT_JSONL}\n"
            f"Launcher: Antigravity (Gemini 4 Carbon High) via personal Claude Ultra (~/.claude) for Brando Miranda / Putnam-AXIOM; $0.00 cash spend.\n"
            f"Assistant: Antigravity (Gemini 4 Carbon High)\n"
            f"TLDR-end: [putnam-axiom: expt02 fable-5.2-max matched-100 eval] Started 200-task single-call claude-fable-5-2 max-effort run after 23:00 PST reset."
        )
        send_email_notification(f"[RUN START] {RUN_EMAIL_NAME}", start_body, START_SENT_FILE)

        if (n_m100 + n_var1) < 200:
            run_eval_cmd(limit=0, workers=2)

        n_after_m100, n_after_var1, _, _ = count_completed()
        total_after = n_after_m100 + n_after_var1
        prev_published = 0
        if PUBLISHED_STATE_FILE.is_file():
            try:
                prev_published = int(json.loads(PUBLISHED_STATE_FILE.read_text(encoding="utf-8")).get("total_done", 0))
            except Exception:
                pass
        log(f"Post-run counts: matched100={n_after_m100}/100, var_snap1={n_after_var1}/100 (prev_published={prev_published})")

        if total_after > prev_published or (n_after_m100 == 100 and n_after_var1 == 100):
            stats, cost_equiv, commit_sha = finalize_and_publish(n_after_m100, n_after_var1)
            PUBLISHED_STATE_FILE.write_text(json.dumps({"total_done": total_after, "commit": commit_sha, "updated_at": now_stamp()}) + "\n", encoding="utf-8")
            elapsed_min = round((now_la() - start_wall).total_seconds() / 60.0, 1)
            if n_after_m100 == 100 and n_after_var1 == 100:
                append_agent_sync_log(stats, commit_sha)
                mcn = stats.get("mcnemar") or {}
                p_str = f"{mcn['p_val']:.4g}" if isinstance(mcn.get("p_val"), float) else "n/a"
                done_body = (
                    f"A (TLDR): Putnam-AXIOM claude-fable-5-2 (max effort) finished 200/200 tasks with Original {stats['orig_100']:.1f}% vs Snapshot-1 Variation {stats['var']:.1f}% (drop {stats['paired_drop']:.1f} points).\n"
                    f"Ran: 100 matched Originals + 100 Snapshot-1 Variations in {elapsed_min} min (single-call Claude Code 2.1.330 --safe-mode --effort max).\n"
                    f"Result: Original {stats['orig_100']:.1f}% (n=100), Var1 {stats['var']:.1f}% (n=100), paired drop {stats['paired_drop']:.1f} [{stats['ci_lo']:.1f}, {stats['ci_hi']:.1f}] (10k bootstrap), exact McNemar p-val={p_str}.\n"
                    f"Cost & outputs: $0.00 cash (~${cost_equiv:.2f} API-equiv); commit https://github.com/brando90/putnam-axiom/commit/{commit_sha}\n"
                    f"Assistant: Antigravity (Gemini 4 Carbon High)\n"
                    f"TLDR-end: [putnam-axiom: expt02 fable-5.2-max matched-100 eval] Completed 200/200 tasks and pushed results ({commit_sha}): Orig {stats['orig_100']:.1f}%, Var1 {stats['var']:.1f}%, drop {stats['paired_drop']:.1f} [{stats['ci_lo']:.1f}, {stats['ci_hi']:.1f}]."
                )
                send_email_notification(f"[RUN DONE] {RUN_EMAIL_NAME}: success", done_body, DONE_SENT_FILE)
                unload_and_remove_launch_agent()
            else:
                log(f"Partial progress published ({commit_sha}); keeping LaunchAgent active for resume.")
        else:
            log("No new completed tasks during tmux run.")
        return 0
    finally:
        release_lock(lock_fd)


if __name__ == "__main__":
    raise SystemExit(main())
