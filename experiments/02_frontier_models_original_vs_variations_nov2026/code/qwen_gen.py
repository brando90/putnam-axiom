#!/usr/bin/env python3
"""Open-weight Putnam-AXIOM run (HF transformers, greedy, plain few-shot completion prompt as in the lm-eval task, no chat template).
Usage: CUDA_VISIBLE_DEVICES=0 python qwen_gen.py --model Qwen/Qwen2-Math-7B-Instruct --out out/qwen2math7b.jsonl --batch 24 --max-new 1024"""
import argparse, json, os, time, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from run_eval import build_prompt, fewshot_block
ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--batch", type=int, default=24); ap.add_argument("--max-new", type=int, default=1024)
ap.add_argument("--order", default="matched,var1,orig,var2345")
a = ap.parse_args()
fs = fewshot_block("fewshot.json")
tasks = [json.loads(l) for l in open("tasks.jsonl")]
grp = {"matched": lambda t: t["set"] == "orig" and t["matched100"], "var1": lambda t: t["set"] == "var" and t["snapshot"] == 1,
       "orig": lambda t: t["set"] == "orig" and not t["matched100"], "var2345": lambda t: t["set"] == "var" and t["snapshot"] != 1}
ordered, seen = [], set()
for g in a.order.split(","):
    for t in tasks:
        if t["key"] not in seen and grp[g](t): ordered.append(t); seen.add(t["key"])
done = set()
if os.path.exists(a.out):
    for l in open(a.out):
        try: done.add(json.loads(l)["key"])
        except Exception: pass
todo = [t for t in ordered if t["key"] not in done]
print(len(ordered), "tasks", len(done), "done", len(todo), "to run", flush=True)
tok = AutoTokenizer.from_pretrained(a.model); tok.padding_side = "left"
if tok.pad_token is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.bfloat16, device_map={"": 0}, attn_implementation="sdpa").eval()
fh = open(a.out, "a")
for i in range(0, len(todo), a.batch):
    b = todo[i:i + a.batch]
    prompts = [build_prompt(t["problem"], fs) for t in b]
    enc = tok(prompts, return_tensors="pt", padding=True).to("cuda")
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=a.max_new, do_sample=False, pad_token_id=tok.pad_token_id, stop_strings=["Problem:"], tokenizer=tok)
    for j, t in enumerate(b):
        gen = out[j, enc["input_ids"].shape[1]:]
        n_out = int((gen != tok.pad_token_id).sum())
        text = tok.decode(gen, skip_special_tokens=True)
        fh.write(json.dumps({"key": t["key"], "set": t["set"], "snapshot": t["snapshot"], "matched100": t["matched100"], "model": a.model, "effort": None,
                             "provider": "hf", "ok": True, "output": text, "usage": {"input": int(enc["attention_mask"][j].sum()), "output": n_out, "reasoning": None,
                             "status": "length" if n_out >= a.max_new else "stop", "incomplete": None}, "secs": round(time.time() - t0, 1)}) + "\n")
    fh.flush(); print(time.strftime("%H:%M:%S"), i + len(b), "/", len(todo), flush=True)
print("finished", flush=True)
