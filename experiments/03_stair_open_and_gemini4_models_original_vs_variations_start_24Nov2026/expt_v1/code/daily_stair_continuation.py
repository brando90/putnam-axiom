#!/usr/bin/env python3
"""Daily STAIR Gateway continuation orchestrator (runs on Mac via LaunchAgent).

On each daily run (after midnight America/Los_Angeles):
1. Runs `run_stair_gateway_eval.py` on skampere1 over SSH (<=240 calls/day, $15 total stop).
2. Pulls raw JSONLs + ledger + status JSON from skampere1 back into expt_v1/data/.
3. Runs `score_and_report_exp03.py` to update scores, RESULTS_*.md, results.md, and README.md.
4. Updates CKPT_stair_and_gemini4_eval.md, commits explicit owned paths with `git commit --only`, pushes to origin/main.
5. Emails To: brando.science@gmail.com ONLY (no BCC) on daily progress, cost-cap stop, or final 600/600 completion.
6. Unloads and deletes the LaunchAgent plist once all 600/600 STAIR calls complete (or on $15 cost-cap stop).
"""
import argparse
import datetime
import fcntl
import json
import os
import re
import smtplib
import subprocess
import sys
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo

TZ_LA = ZoneInfo("America/Los_Angeles")
REPO_ROOT = Path("/Users/brandomiranda/putnam-axiom")
EXP03_DIR = REPO_ROOT / "experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026"
LOCAL_DIR = REPO_ROOT / ".local/03_stair_and_gemini4_24Nov2026"
LOCK_FILE = LOCAL_DIR / "stair_daily.lock"
LOG_FILE = LOCAL_DIR / "stair_daily.log"
GMAIL_PASS_FILE = Path.home() / "keys/gmail_app_password.txt"
PLIST_LABEL = "com.brando.putnam-expt03-stair-daily"
PLIST_PATH = Path.home() / "Library/LaunchAgents" / f"{PLIST_LABEL}.plist"
AGENT_SYNC_LOG = Path.home() / "agent-sync/coding/log.md"
REMOTE_HOST = "brando9@skampere1.stanford.edu"
REMOTE_DIR = "/lfs/skampere1/0/brando9/putnam_axiom_expt03"


def now_stamp():
    return datetime.datetime.now(TZ_LA).strftime("%m-%d-%Y %H:%M %Z")


def log(msg):
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{now_stamp()}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def send_email_brando_science_only(subject, body):
    if not GMAIL_PASS_FILE.is_file():
        log(f"Email skipped ({subject}): missing gmail_app_password.txt")
        return
    pw = GMAIL_PASS_FILE.read_text(encoding="utf-8").strip()
    msg = EmailMessage()
    msg["From"] = "brandojazz@gmail.com"
    msg["To"] = "brando.science@gmail.com"
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as s:
        s.login("brandojazz@gmail.com", pw)
        s.send_message(msg)
    log(f"Sent email To brando.science@gmail.com only (no BCC): {subject}")


def unload_and_remove_plist():
    if not PLIST_PATH.exists():
        return
    uid = os.getuid()
    try:
        PLIST_PATH.unlink()
        log(f"Removed LaunchAgent {PLIST_PATH}")
    except FileNotFoundError:
        pass
    subprocess.run(["launchctl", "bootout", f"gui/{uid}/{PLIST_LABEL}"], capture_output=True, check=False)


def pull_stair_outputs():
    raw_dir = EXP03_DIR / "expt_v1/data/raw_outputs"
    raw_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("glm53.jsonl", "kimik3.jsonl", "deepseekv41flash.jsonl"):
        subprocess.run(
            ["scp", "-q", "-o", "BatchMode=yes", f"{REMOTE_HOST}:{REMOTE_DIR}/out/{fname}", str(raw_dir / fname)],
            check=False,
        )
    ok_status = True
    for fname in ("stair_call_ledger.jsonl", "stair_run_status.json"):
        r = subprocess.run(
            ["scp", "-q", "-o", "BatchMode=yes", f"{REMOTE_HOST}:{REMOTE_DIR}/{fname}", str(EXP03_DIR / "expt_v1/data" / fname)],
            check=False,
        )
        if fname == "stair_run_status.json" and r.returncode != 0:
            ok_status = False
    return ok_status


def commit_and_push_exp03(msg):
    py = sys.executable
    subprocess.run([py, str(REPO_ROOT / "src/scripts/verify_consolidation.py")], check=True)
    owned = [
        "README.md",
        "experiments/README.md",
        "experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/README.md",
        "experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/PROTOCOL.md",
        "experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/results.md",
        "experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/CKPT_stair_and_gemini4_eval.md",
        "experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/expt_v1/data/stair_call_ledger.jsonl",
        "experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/expt_v1/data/stair_run_status.json",
        "experiments/03_stair_open_and_gemini4_models_original_vs_variations_start_24Nov2026/expt_v1/results/",
    ]
    for gz in (EXP03_DIR / "expt_v1/data/raw_outputs").glob("*.jsonl.gz"):
        owned.append(str(gz.relative_to(REPO_ROOT)))
    for f in owned:
        if (REPO_ROOT / f).exists():
            subprocess.run(["git", "-C", str(REPO_ROOT), "add", "--", f], check=True)
    st = subprocess.run(["git", "-C", str(REPO_ROOT), "diff", "--cached", "--quiet"])
    if st.returncode == 0:
        return subprocess.check_output(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"], text=True).strip()
    subprocess.run(["git", "-C", str(REPO_ROOT), "diff", "--cached", "--check"], check=True)
    diff_txt = subprocess.check_output(["git", "-C", str(REPO_ROOT), "diff", "--cached"], text=True)
    if re.search(r"sk-[A-Za-z0-9_\-]{16,}", diff_txt):
        raise RuntimeError("Secret detected in staged diff")
    subprocess.run(["git", "-C", str(REPO_ROOT), "fetch", "origin", "main"], check=False)
    subprocess.run(["git", "-C", str(REPO_ROOT), "commit", "--only", "-m", msg, "--", *[f for f in owned if (REPO_ROOT / f).exists()]], check=True)
    push = subprocess.run(["git", "-C", str(REPO_ROOT), "push", "origin", "main"], capture_output=True, text=True)
    if push.returncode != 0:
        subprocess.run(["git", "-C", str(REPO_ROOT), "pull", "--rebase", "--autostash", "origin", "main"], check=False)
        subprocess.run(["git", "-C", str(REPO_ROOT), "push", "origin", "main"], check=True)
    return subprocess.check_output(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"], text=True).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pull-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    lock_fd = open(LOCK_FILE, "w", encoding="utf-8")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log("Another daily STAIR runner holds lock; exiting.")
        return 0

    try:
        status_p = EXP03_DIR / "expt_v1/data/stair_run_status.json"
        if status_p.is_file():
            st = json.loads(status_p.read_text(encoding="utf-8"))
            if st.get("all_600_complete"):
                log("All 600/600 STAIR calls already complete.")
                if not args.dry_run:
                    unload_and_remove_plist()
                return 0

        if args.dry_run:
            log("Dry-run OK: daily_stair_continuation ready.")
            return 0

        if not args.pull_only:
            # Check if a remote tmux run is already executing
            chk = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", REMOTE_HOST, "tmux ls 2>/dev/null | grep -q stair-putnam-expt03"],
                capture_output=True,
            )
            if chk.returncode == 0:
                log("Remote tmux session stair-putnam-expt03 is already running; skipping launch.")
                return 0
            log("Starting daily STAIR batch on skampere1 (cap 240/day, $15 stop)...")
            remote_cmd = (
                f"python3 {REMOTE_DIR}/run_stair_gateway_eval.py "
                f"--tasks {REMOTE_DIR}/tasks.jsonl.gz "
                f"--fewshot {REMOTE_DIR}/fewshot.json "
                f"--manifest {REMOTE_DIR}/matched100_problem_ids.json "
                f"--out-dir {REMOTE_DIR}/out "
                f"--ledger {REMOTE_DIR}/stair_call_ledger.jsonl "
                f"--status-out {REMOTE_DIR}/stair_run_status.json "
                f"--daily-cap 240 --cost-cap-usd 15.0 --workers 3"
            )
            ssh_res = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ServerAliveInterval=30", REMOTE_HOST, remote_cmd],
                timeout=7200,
                check=False,
            )
            if ssh_res.returncode not in (0, 2):
                log(f"Remote STAIR runner failed with exit code {ssh_res.returncode}; aborting sync.")
                send_email_brando_science_only(
                    "[RUN ERROR] putnam-axiom-expt03-stair daily batch failed",
                    f"Remote STAIR Gateway runner on {REMOTE_HOST} exited with code {ssh_res.returncode}.\n"
                    f"Log: {LOG_FILE}\n"
                    f"Next: LaunchAgent remains armed; inspect SSH/remote log before next run.\n"
                    f"Assistant: Antigravity (Gemini 4 Carbon High)\n"
                    f"TLDR-end: [putnam-axiom: expt03 stair-open & gemini4 eval] Daily STAIR SSH run exited with code {ssh_res.returncode}; no repo changes pushed."
                )
                return 1

        if not pull_stair_outputs():
            log("Failed to pull stair_run_status.json from skampere1; aborting sync.")
            send_email_brando_science_only(
                "[RUN ERROR] putnam-axiom-expt03-stair pull failed",
                f"Failed to SCP stair_run_status.json from {REMOTE_HOST}:{REMOTE_DIR}.\n"
                f"Log: {LOG_FILE}\n"
                f"Assistant: Antigravity (Gemini 4 Carbon High)\n"
                f"TLDR-end: [putnam-axiom: expt03 stair-open & gemini4 eval] SCP of stair_run_status.json failed; no repo changes pushed."
            )
            return 1

        uv_py = Path.home() / "uv_envs/no-gold-ref-judge/bin/python3"
        score_py = str(uv_py) if uv_py.is_file() else sys.executable
        score_out = subprocess.check_output(
            [score_py, str(EXP03_DIR / "expt_v1/code/score_and_report_exp03.py")],
            text=True,
        )
        summaries = json.loads(score_out)
        # Keep only *.jsonl.gz in git-tracked raw_outputs after scoring compresses them.
        for fname in ("glm53.jsonl", "kimik3.jsonl", "deepseekv41flash.jsonl"):
            p_raw = EXP03_DIR / "expt_v1/data/raw_outputs" / fname
            if p_raw.is_file() and (EXP03_DIR / "expt_v1/data/raw_outputs" / f"{fname}.gz").is_file():
                p_raw.unlink()
        st = json.loads((EXP03_DIR / "expt_v1/data/stair_run_status.json").read_text(encoding="utf-8"))

        # Update CKPT_stair_and_gemini4_eval.md
        ckpt_p = EXP03_DIR / "CKPT_stair_and_gemini4_eval.md"
        ckpt_txt = ckpt_p.read_text(encoding="utf-8")
        ckpt_txt = re.sub(r"^Last updated:.*$", f"Last updated: {now_stamp()}", ckpt_txt, count=1, flags=re.MULTILINE)
        ckpt_txt = ckpt_txt.rstrip("\n") + f"\n- {now_stamp()} -- Daily STAIR batch synced: counts={st.get('counts')}, est_cost=${st.get('cum_est_cost_usd')}, stop_reason={st.get('stop_reason')}\n"
        ckpt_p.write_text(ckpt_txt, encoding="utf-8")

        sha = commit_and_push_exp03(f"experiments/03: STAIR daily update ({st.get('counts')})")

        stair_lines = []
        for s in summaries:
            if s["meta"]["track"] == "stair":
                o_acc = f"{s['orig_acc']:.1f}%" if s.get("orig_acc") is not None else "n/a"
                v_acc = f"{s['var_acc']:.1f}%" if s.get("var_acc") is not None else "n/a"
                stair_lines.append(
                    f"- {s['meta']['model']}: {s['orig_attempted']}/100 orig ({s['orig_k']}/{s['orig_den']}={o_acc}), "
                    f"{s['var_attempted']}/100 var1 ({s['var_k']}/{s['var_den']}={v_acc}), est=${s['est_cost_usd']:.4f}"
                )

        if st.get("stop_reason") and "COST_CAP" in str(st.get("stop_reason")):
            send_email_brando_science_only(
                "[RUN STOPPED] putnam-axiom-expt03-stair: $15 cost cap reached",
                f"STAIR Gateway run stopped cleanly at conservative cost estimate ${st['cum_est_cost_usd']:.4f} (cap $15.00).\n"
                f"Counts: {st.get('counts')}\n" + "\n".join(stair_lines) + "\n"
                f"Commit: https://github.com/brando90/putnam-axiom/commit/{sha}\n"
                f"Assistant: Antigravity (Gemini 4 Carbon High)\n"
                f"TLDR-end: [putnam-axiom: expt03 stair-open & gemini4 eval] Stopped at ${st['cum_est_cost_usd']:.4f} estimated cost ({st.get('counts')}); LaunchAgent removed."
            )
            unload_and_remove_plist()
        elif st.get("all_600_complete"):
            if AGENT_SYNC_LOG.is_file():
                with open(AGENT_SYNC_LOG, "a", encoding="utf-8") as f:
                    f.write(
                        f"{datetime.datetime.now(TZ_LA).strftime('%m-%d-%Y')} | Antigravity (scheduled STAIR Exp03 continuation) | "
                        f"Putnam-AXIOM Exp 03 all 600/600 STAIR open-model calls complete (`{sha}`, est `${st['cum_est_cost_usd']:.2f}`): "
                        + "; ".join(stair_lines)
                        + f" | https://github.com/brando90/putnam-axiom/commit/{sha}\n"
                    )
            send_email_brando_science_only(
                "[RUN DONE] putnam-axiom-expt03-stair-600: success",
                f"All 600/600 STAIR Gateway calls (GLM 5.3, Kimi K3, DeepSeek V4.1 Flash 1017) finished and pushed ({sha}).\n"
                + "\n".join(stair_lines) + "\n"
                f"Total estimated cost: ${st['cum_est_cost_usd']:.4f}\n"
                f"Commit: https://github.com/brando90/putnam-axiom/commit/{sha}\n"
                f"Assistant: Antigravity (Gemini 4 Carbon High)\n"
                f"TLDR-end: [putnam-axiom: expt03 stair-open & gemini4 eval] Completed 600/600 STAIR calls across GLM 5.3, Kimi K3, and DeepSeek V4.1 Flash 1017 (${st['cum_est_cost_usd']:.4f} est) and updated README.md ({sha})."
            )
            unload_and_remove_plist()
        else:
            send_email_brando_science_only(
                "[RUN PROGRESS] putnam-axiom-expt03-stair daily batch finished",
                f"Daily STAIR batch reached today's 240-call limit ({st.get('counts')}, total est=${st['cum_est_cost_usd']:.4f}).\n"
                + "\n".join(stair_lines) + "\n"
                f"Commit: https://github.com/brando90/putnam-axiom/commit/{sha}\n"
                f"Next: LaunchAgent remains armed for tomorrow's continuation.\n"
                f"Assistant: Antigravity (Gemini 4 Carbon High)\n"
                f"TLDR-end: [putnam-axiom: expt03 stair-open & gemini4 eval] Daily STAIR cap hit at {st.get('counts')} (${st['cum_est_cost_usd']:.4f} est); results pushed ({sha}) and next day armed."
            )
        return 0
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


if __name__ == "__main__":
    raise SystemExit(main())
