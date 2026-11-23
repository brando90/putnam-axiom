#!/usr/bin/env python3
"""Phase 2 & Phase 3 GPU Runner: Multi-Model TFA/EM Calibration & Controlled SFT Logic-Contamination Trajectory.

Executes on SNAP GPU nodes (e.g. skampere1.stanford.edu):
- Phase 2: Evaluates 10 cached open-weight models across 5 families on:
  * orig_contaminated (N=100, data/Putnam-AXIOM_Variations_v4/original.json)
  * func_variations_v1 (N=100 paired Variation-1, data/Putnam-AXIOM_Variations_v4/test.json)
  * func_variations_all5 (N=500 all 5 variations per problem for teacher-forced metrics)
  * orig_unseen_control (N=100 deterministic seed-42 sample from non-overlapping Putnam_AXIOM_Original_v3.json)
  with greedy decoding (do_sample=False, max_new_tokens=384) and SymPy LaTeX equivalence checking.
- Phase 3: Fine-tunes 3 distinct models (google/gemma-2b-it, Qwen/Qwen3-1.7B, deepseek-ai/deepseek-math-7b-instruct)
  directly on the N=100 orig_contaminated problems for 10 epochs, evaluating at Epochs 0, 1, 3, 5, 10 across
  all 3 splits and all 4 metrics (EM, TFA_sol, TFA_box, TFCE_sol).
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
from pathlib import Path
import random
import re
import signal
import time
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList

try:
    import sympy
    from sympy.parsing.latex import parse_latex
    parse_latex("1")
    HAS_SYMPY = True
except Exception as _sympy_exc:
    HAS_SYMPY = False
    print(f"[WARN] SymPy parse_latex unavailable ({_sympy_exc}); EM falls back to normalized string match.", flush=True)


def seed_everything(seed: int = 42) -> None:
    """Seeds Python, NumPy, and PyTorch RNGs deterministically."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _load_json(path: Path):
    """Loads JSON with an explicit closed UTF-8 file handle."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# --- Answer Extraction & Normalization (from src/lm_eval_utils.py) ---

SUBSTITUTIONS = [
    ("an ", ""),
    ("a ", ""),
    (".$", "$"),
    ("\\$", ""),
    (r"\ ", ""),
    (" ", ""),
    ("mbox", "text"),
    (",\\text{and}", ","),
    ("\\text{and}", ","),
    ("\\text{m}", "\\text{}"),
]

REMOVED_EXPRESSIONS = [
    "square", "ways", "integers", "dollars", "mph", "inches", "ft", "hours", "km",
    "units", "\\ldots", "sue", "points", "feet", "minutes", "digits", "cents", "degrees",
    "cm", "gm", "pounds", "meters", "meals", "edges", "students", "childrentickets",
    "multiples", "\\text{s}", "\\text{.}", "\\text{\ns}", "\\text{}^2", "\\text{}^3",
    "\\text{\n}", "\\text{}", r"\mathrm{th}", r"^\circ", r"^{\circ}", r"\;", r",\!",
    "{,}", '"', "\\dots",
]


def _find_matching_brace(string: str, start_idx: int) -> Optional[int]:
    """Returns the index of the closing brace matching the first opening brace at or after start_idx."""
    depth = 0
    seen_open = False
    for i in range(start_idx, len(string)):
        ch = string[i]
        depth += (ch == "{") - (ch == "}")
        seen_open = seen_open or ch == "{"
        if seen_open and depth == 0:
            return i
    return None


def last_boxed_only_string(string: str) -> Optional[str]:
    """Extracts the final balanced \\boxed{...} or \\fbox{...} substring."""
    if "\\boxed " in string:
        return "\\boxed " + string.split("\\boxed ")[-1].split("$")[0]
    idx = string.rfind("\\boxed")
    if idx < 0:
        idx = string.rfind("\\fbox")
    if idx < 0:
        return None
    right_brace_idx = _find_matching_brace(string, idx)
    return None if right_brace_idx is None else string[idx : right_brace_idx + 1]


def remove_boxed(s: str) -> str:
    """Strips outer \\boxed{...} or \\fbox{...} wrapper from a string."""
    if "\\boxed " in s:
        return s[len("\\boxed ") :]
    if s.startswith("\\boxed{") and s.endswith("}"):
        return s[len("\\boxed{") : -1]
    if s.startswith("\\fbox{") and s.endswith("}"):
        return s[len("\\fbox{") : -1]
    return s


def normalize_final_answer(final_answer: str) -> str:
    """Normalizes LaTeX final-answer strings identically to the repository evaluator."""
    if not final_answer:
        return "[invalidanswer]"
    final_answer = final_answer.split("=")[-1]
    for before, after in SUBSTITUTIONS:
        final_answer = final_answer.replace(before, after)
    for expr in REMOVED_EXPRESSIONS:
        final_answer = final_answer.replace(expr, "")
    final_answer = re.sub(r"(.*?)(\$)(.*?)(\$)(.*)", "$\\3$", final_answer)
    final_answer = re.sub(r"(\\text\{)(.*?)(\})", "\\2", final_answer)
    final_answer = re.sub(r"(\\textbf\{)(.*?)(\})", "\\2", final_answer)
    final_answer = re.sub(r"(\\overline\{)(.*?)(\})", "\\2", final_answer)
    final_answer = re.sub(r"(\\boxed\{)(.*)(\})", "\\2", final_answer)
    final_answer = re.sub(r"(frac)([^{])(.)", "frac{\\2}{\\3}", final_answer)
    final_answer = re.sub(r"(sqrt)([^{])", "sqrt{\\2}", final_answer)
    final_answer = final_answer.replace("$", "").strip()
    if final_answer.replace(",", "").isdigit():
        final_answer = final_answer.replace(",", "")
    return final_answer


def extract_answer_from_text(text: str) -> str:
    """Extracts and normalizes the final answer from a generated solution."""
    boxed = last_boxed_only_string(text)
    if boxed is not None:
        try:
            return normalize_final_answer(remove_boxed(boxed))
        except Exception:
            pass
    m = re.search(r"(?:Final Answer: The final answer is|The final answer is|The answer is:?)\s*([^\n\.]+)", text)
    if m:
        return normalize_final_answer(m.group(1).strip())
    return "[invalidanswer]"


class _Timeout:
    """SIGALRM context guard bounding SymPy symbolic equivalence checks."""

    def __init__(self, seconds: int = 2):
        self.seconds = seconds

    def _handler(self, signum, frame):
        raise TimeoutError()

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._handler)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)


def _sympy_equiv(pred_ans: str, gold_ans: str) -> int:
    """Checks SymPy algebraic equivalence under a 2-second SIGALRM timeout."""
    try:
        with _Timeout(2):
            return int(sympy.simplify(parse_latex(pred_ans) - parse_latex(gold_ans)) == 0)
    except Exception:
        return 0


def check_exact_match(pred_ans: str, gold_ans: str) -> int:
    """Returns 1 if predicted answer matches gold answer via string or SymPy equivalence."""
    if not pred_ans or pred_ans == "[invalidanswer]" or not gold_ans:
        return 0
    if pred_ans == gold_ans:
        return 1
    if HAS_SYMPY and len(pred_ans) <= 120 and len(gold_ans) <= 120:
        return _sympy_equiv(pred_ans, gold_ans)
    return 0


PROMPT_TEMPLATE = (
    "Given a mathematics question, compose a detailed solution. "
    "Simplify your answer as much as possible and give the final answer inside \\boxed{{answer}}.\n\n"
    "Problem:\nIf $\\det \\mathbf{{A}} = 2$ and $\\det \\mathbf{{B}} = 12,$ find $\\det(\\mathbf{{A}}\\mathbf{{B}}).$\n\n"
    "Solution: Let's think step by step. Since $\\det(\\mathbf{{A}}\\mathbf{{B}}) = (\\det \\mathbf{{A}})(\\det \\mathbf{{B}}) = 2 \\cdot 12 = 24$, "
    "the final answer is $\\boxed{{24}}$.\n\n"
    "Problem:\n{problem}\n\n"
    "Solution: "
)


def _format_split_item(x: Dict, pid: str, vid: str) -> Dict:
    """Normalizes one benchmark problem dict with its extracted gold final answer."""
    gold_boxed = last_boxed_only_string(x["solution"])
    gold_ans = normalize_final_answer(remove_boxed(gold_boxed)) if gold_boxed else extract_answer_from_text(x["solution"])
    return {
        "problem_id": pid,
        "variation_id": vid,
        "problem": x["problem"],
        "solution": x["solution"],
        "gold_answer": gold_ans,
        "answer_type": x.get("answer_type", ""),
    }


def load_splits(data_root: Path) -> Dict[str, List[Dict]]:
    """Loads the four deterministic evaluation splits under data_root."""
    orig_100_raw = _load_json(data_root / "Putnam-AXIOM_Variations_v4/original.json")
    var_500_raw = _load_json(data_root / "Putnam-AXIOM_Variations_v4/test.json")
    orig_522_raw = _load_json(data_root / "Putnam_AXIOM_Original_v3.json")

    orig_contaminated = [_format_split_item(x, f"{x['year']}_{x['id']}", "0") for x in orig_100_raw]
    orig_ids_set = {it["problem_id"] for it in orig_contaminated}

    func_variations_all5 = []
    var_by_pid_and_v = {}
    for x in var_500_raw:
        item = _format_split_item(x, f"{x['year']}_{x['id']}", str(x["variation"]))
        func_variations_all5.append(item)
        var_by_pid_and_v[(item["problem_id"], item["variation_id"])] = item

    func_variations_v1 = [var_by_pid_and_v[(o["problem_id"], "1")] for o in orig_contaminated]
    non_overlapping = [x for x in orig_522_raw if x["id"] not in orig_ids_set]
    sampled_unseen = random.Random(42).sample(non_overlapping, 100)
    orig_unseen_control = [_format_split_item(x, x["id"], "0") for x in sampled_unseen]

    return {
        "orig_contaminated": orig_contaminated,
        "func_variations_v1": func_variations_v1,
        "func_variations_all5": func_variations_all5,
        "orig_unseen_control": orig_unseen_control,
    }


def _encode_tfa_item(tokenizer: AutoTokenizer, item: Dict, max_seq_len: int) -> Tuple[List[int], int, int, int]:
    """Encodes prompt + gold solution and returns (full_ids, prompt_len, box_start, box_end)."""
    prompt_str = PROMPT_TEMPLATE.format(problem=item["problem"])
    sol_str = item["solution"]
    boxed_str = last_boxed_only_string(sol_str)
    pre_box = sol_str[: sol_str.rfind(boxed_str)] if (boxed_str and boxed_str in sol_str) else sol_str

    p_ids = tokenizer.encode(prompt_str, add_special_tokens=True)
    s_ids = tokenizer.encode(sol_str, add_special_tokens=False)
    pre_box_ids = tokenizer.encode(pre_box, add_special_tokens=False)
    if tokenizer.eos_token_id is not None:
        s_ids = s_ids + [tokenizer.eos_token_id]

    full_ids = (p_ids + s_ids)[:max_seq_len]
    p_len = min(len(p_ids), len(full_ids) - 1)
    box_start = min(len(p_ids) + len(pre_box_ids), len(full_ids) - 1)
    has_eos_tail = tokenizer.eos_token_id is not None and len(p_ids) + len(s_ids) <= max_seq_len
    box_end = len(full_ids) - (1 if has_eos_tail else 0)
    if box_end <= box_start:
        box_start = max(p_len, len(full_ids) - 8)
        box_end = len(full_ids)
    return full_ids, p_len, box_start, box_end


def _score_tfa_item(
    logits_row: torch.Tensor, target_row: torch.Tensor, p_len: int, seq_len: int, box_span: Tuple[int, int]
) -> Dict:
    """Computes TFA_sol, TFA_box, and TFCE_sol for a single forward-passed sequence."""
    if seq_len <= p_len:
        return {"tfa_sol": 0.0, "tfa_box": 0.0, "tfce_sol": 10.0, "n_sol_tokens": 0, "n_box_tokens": 0}
    sol_logits = logits_row[p_len - 1 : seq_len - 1, :].float()
    sol_targets = target_row[p_len:seq_len]
    tfa_sol = float((torch.argmax(sol_logits, dim=-1) == sol_targets).float().mean().item())
    tfce_sol = float(F.cross_entropy(sol_logits, sol_targets, reduction="mean").item())

    b_start, b_end = box_span
    if b_end > b_start and b_start >= 1:
        box_logits = logits_row[b_start - 1 : b_end - 1, :].float()
        box_targets = target_row[b_start:b_end]
        tfa_box = float((torch.argmax(box_logits, dim=-1) == box_targets).float().mean().item())
        n_box = int(b_end - b_start)
    else:
        tfa_box, n_box = tfa_sol, 0

    return {
        "tfa_sol": round(tfa_sol, 6),
        "tfa_box": round(tfa_box, 6),
        "tfce_sol": round(tfce_sol, 6),
        "n_sol_tokens": int(seq_len - p_len),
        "n_box_tokens": n_box,
    }


def compute_tfa_metrics_for_split(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    items: List[Dict],
    max_seq_len: int = 1024,
    batch_size: int = 16,
) -> List[Dict]:
    """Computes per-item TFA_sol, TFA_box, and TFCE_sol in batched forward passes."""
    model.eval()
    device = next(model.parameters()).device
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else (tokenizer.eos_token_id or 0)
    results = []

    for start in range(0, len(items), batch_size):
        batch = items[start : start + batch_size]
        encoded = [_encode_tfa_item(tokenizer, item, max_seq_len) for item in batch]
        max_len = max(len(e[0]) for e in encoded)
        batch_ids = torch.full((len(batch), max_len), pad_id, dtype=torch.long, device=device)
        attn_mask = torch.zeros((len(batch), max_len), dtype=torch.long, device=device)

        for i, (ids, _, _, _) in enumerate(encoded):
            batch_ids[i, : len(ids)] = torch.tensor(ids, dtype=torch.long, device=device)
            attn_mask[i, : len(ids)] = 1

        with torch.no_grad():
            logits = model(input_ids=batch_ids, attention_mask=attn_mask).logits

        for i, (ids, p_len, b_start, b_end) in enumerate(encoded):
            results.append(_score_tfa_item(logits[i], batch_ids[i], p_len, len(ids), (b_start, b_end)))
    return results


class StopOnProblemHeader(StoppingCriteria):
    """Stops generation once all sequences in the batch have emitted 'Problem:' or '<eos>'."""

    def __init__(self, prompt_len: int, tokenizer: AutoTokenizer):
        self.prompt_len = prompt_len
        self.tokenizer = tokenizer

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        if (input_ids.shape[1] - self.prompt_len) % 16 != 0:
            return False
        eos = self.tokenizer.eos_token
        for seq in input_ids:
            gen_text = self.tokenizer.decode(seq[self.prompt_len :], skip_special_tokens=False)
            if "Problem:" not in gen_text and (eos is None or eos not in gen_text):
                return False
        return True


def compute_em_for_split(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    items: List[Dict],
    max_new_tokens: int = 384,
    batch_size: int = 25,
) -> List[Dict]:
    """Computes free-generation Boxed-Answer Exact Match (EM) in left-padded batches."""
    model.eval()
    device = next(model.parameters()).device
    orig_padding_side = tokenizer.padding_side
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    results = []
    for start in range(0, len(items), batch_size):
        batch = items[start : start + batch_size]
        prompts = [PROMPT_TEMPLATE.format(problem=it["problem"]) for it in batch]
        enc = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True, max_length=1024).to(device)
        prompt_len = enc["input_ids"].shape[1]
        stopper = StoppingCriteriaList([StopOnProblemHeader(prompt_len, tokenizer)])

        with torch.no_grad():
            gen_ids = model.generate(
                **enc,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                stopping_criteria=stopper,
                use_cache=True,
            )

        for i, item in enumerate(batch):
            gen_text = tokenizer.decode(gen_ids[i, prompt_len:], skip_special_tokens=True).split("Problem:")[0]
            pred_ans = extract_answer_from_text(gen_text)
            results.append({"em": check_exact_match(pred_ans, item["gold_answer"]), "pred_answer": pred_ans[:120], "gen_chars": len(gen_text)})

    tokenizer.padding_side = orig_padding_side
    return results


def _build_item_row(model_name: str, phase: str, epoch: int, split_name: str, it: Dict, tr: Dict, er: Optional[Dict]) -> Dict:
    """Formats a single per-item CSV record for either EM+TFA splits or TFA-only splits."""
    return {
        "model": model_name,
        "phase": phase,
        "epoch": epoch,
        "split": split_name,
        "problem_id": it["problem_id"],
        "variation_id": it["variation_id"],
        "em": er["em"] if er is not None else -1,
        "pred_answer": er["pred_answer"] if er is not None else "",
        "gold_answer": it["gold_answer"][:120],
        "tfa_sol": tr["tfa_sol"],
        "tfa_box": tr["tfa_box"],
        "tfce_sol": tr["tfce_sol"],
        "n_sol_tokens": tr["n_sol_tokens"],
        "n_box_tokens": tr["n_box_tokens"],
    }


def _mean_metric(rows: List[Dict], key: str) -> float:
    """Computes rounded mean for one metric key across evaluated items."""
    return round(float(np.mean([r[key] for r in rows])), 4)


def _evaluate_primary_split(
    model: AutoModelForCausalLM, tokenizer: AutoTokenizer, items: List[Dict],
    model_name: str, phase: str, epoch: int, split_name: str, gen_batch_size: int, tfa_batch_size: int,
) -> Tuple[List[Dict], Dict]:
    """Runs TFA + EM evaluation for one primary split and returns per-item rows and split stats."""
    tfa_res = compute_tfa_metrics_for_split(model, tokenizer, items, batch_size=tfa_batch_size)
    em_res = compute_em_for_split(model, tokenizer, items, batch_size=gen_batch_size)
    rows = [_build_item_row(model_name, phase, epoch, split_name, it, tr, er) for it, tr, er in zip(items, tfa_res, em_res)]
    stats_dict = {
        "n": len(items),
        "em_mean": _mean_metric(em_res, "em"),
        "em_sum": int(sum(r["em"] for r in em_res)),
        "tfa_sol_mean": _mean_metric(tfa_res, "tfa_sol"),
        "tfa_box_mean": _mean_metric(tfa_res, "tfa_box"),
        "tfce_sol_mean": _mean_metric(tfa_res, "tfce_sol"),
    }
    return rows, stats_dict


def evaluate_model_state(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    splits: Dict[str, List[Dict]],
    model_name: str,
    phase: str,
    epoch: int,
    gen_batch_size: int = 25,
    tfa_batch_size: int = 16,
) -> Tuple[List[Dict], Dict]:
    """Evaluates a model checkpoint across orig_contaminated, func_variations_v1, func_variations_all5, and orig_unseen_control."""
    t0 = time.time()
    item_rows: List[Dict] = []
    summary: Dict = {"model": model_name, "phase": phase, "epoch": epoch, "splits": {}}
    for split_name in ("orig_contaminated", "func_variations_v1", "orig_unseen_control"):
        rows, stats_dict = _evaluate_primary_split(
            model, tokenizer, splits[split_name], model_name, phase, epoch, split_name, gen_batch_size, tfa_batch_size
        )
        item_rows.extend(rows)
        summary["splits"][split_name] = stats_dict

    items_500 = splits["func_variations_all5"]
    tfa_500 = compute_tfa_metrics_for_split(model, tokenizer, items_500, batch_size=tfa_batch_size)
    item_rows.extend(_build_item_row(model_name, phase, epoch, "func_variations_all5", it, tr, None) for it, tr in zip(items_500, tfa_500))
    summary["splits"]["func_variations_all5"] = {
        "n": len(items_500),
        "tfa_sol_mean": _mean_metric(tfa_500, "tfa_sol"),
        "tfa_box_mean": _mean_metric(tfa_500, "tfa_box"),
        "tfce_sol_mean": _mean_metric(tfa_500, "tfce_sol"),
    }
    summary["elapsed_sec"] = round(time.time() - t0, 2)
    print(f"[EVAL DONE] {model_name} | {phase} | ep={epoch} | {summary['elapsed_sec']}s | {summary['splits']}", flush=True)
    return item_rows, summary


def build_sft_tensors(
    tokenizer: AutoTokenizer, items: List[Dict], max_seq_len: int = 1024
) -> List[Tuple[torch.Tensor, torch.Tensor]]:
    """Builds (input_ids, labels) tensors with prompt masked (-100) and solution + EOS supervised."""
    examples = []
    for item in items:
        p_ids = tokenizer.encode(PROMPT_TEMPLATE.format(problem=item["problem"]), add_special_tokens=True)
        s_ids = tokenizer.encode(item["solution"], add_special_tokens=False)
        if tokenizer.eos_token_id is not None:
            s_ids = s_ids + [tokenizer.eos_token_id]
        full_ids = (p_ids + s_ids)[:max_seq_len]
        p_len = min(len(p_ids), len(full_ids) - 1)
        labels = [-100] * p_len + full_ids[p_len:]
        examples.append((torch.tensor(full_ids, dtype=torch.long), torch.tensor(labels, dtype=torch.long)))
    return examples


MODEL_SNAPSHOT_PATHS = {
    "google/gemma-2b": "/lfs/skampere1/0/brando9/.cache/huggingface/hub/models--google--gemma-2b/snapshots/2ac59a5d7bf4e1425010f0d457dde7d146658953",
    "google/gemma-2b-it": "/lfs/skampere1/0/brando9/.cache/huggingface/hub/models--google--gemma-2b-it/snapshots/de144fb2268dee1066f515465df532c05e699d48",
    "Qwen/Qwen3-1.7B-Base": "/lfs/skampere1/0/brando9/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B-Base/snapshots/ea980cb0a6c2ae4b936e82123acc929f1cec04c1",
    "Qwen/Qwen3-1.7B": "/lfs/skampere1/0/brando9/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e",
    "Qwen/Qwen3-4B": "/lfs/skampere1/0/brando9/.cache/huggingface/hub/models--Qwen--Qwen3-4B/snapshots/1cfa9a7208912126459214e8b04321603b3df60c",
    "deepseek-ai/deepseek-math-7b-base": "/lfs/skampere1/0/brando9/.cache/huggingface/hub/models--deepseek-ai--deepseek-math-7b-base/snapshots/036a8c6189aac6e2fc4e07b46e1e57c6b647bca5",
    "deepseek-ai/deepseek-math-7b-instruct": "/lfs/skampere1/0/brando9/.cache/huggingface/hub/models--deepseek-ai--deepseek-math-7b-instruct/snapshots/0a5828f800a36df0fd7f0ed581b983246c0677ff",
    "deepseek-ai/deepseek-math-7b-rl": "/lfs/skampere1/0/brando9/.cache/huggingface/hub/models--deepseek-ai--deepseek-math-7b-rl/snapshots/f3cd419a172ff5a100e9a563ebfe7900d78e9740",
    "meta-llama/Meta-Llama-3.1-8B": "/lfs/skampere1/0/brando9/.cache/huggingface/hub/models--meta-llama--Meta-Llama-3.1-8B/snapshots/48d6d0fc4e02fb1269b36940650a1b7233035cbb",
    "mistralai/Mistral-7B-v0.3": "/lfs/skampere1/0/brando9/.cache/huggingface/hub/models--mistralai--Mistral-7B-v0.3/snapshots/caa1feb0e54d415e2df31207e5f4e273e33509b1",
}

WORKER_CONFIGS = {
    "gpu0": {
        "phase2_models": ["google/gemma-2b", "google/gemma-2b-it", "Qwen/Qwen3-1.7B-Base"],
        "sft_model": "google/gemma-2b-it",
        "sft_lr": 2e-5,
    },
    "gpu5": {
        "phase2_models": ["Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B", "deepseek-ai/deepseek-math-7b-base"],
        "sft_model": "Qwen/Qwen3-1.7B",
        "sft_lr": 2e-5,
    },
    "gpu7": {
        "phase2_models": ["deepseek-ai/deepseek-math-7b-instruct", "deepseek-ai/deepseek-math-7b-rl"],
        "sft_model": "deepseek-ai/deepseek-math-7b-instruct",
        "sft_lr": 1.5e-5,
    },
    "frontier8b": {
        "phase2_models": ["meta-llama/Meta-Llama-3.1-8B", "mistralai/Mistral-7B-v0.3"],
        "sft_model": None,
        "sft_lr": 0.0,
    },
}


def train_one_epoch(
    model: AutoModelForCausalLM,
    optimizer: torch.optim.Optimizer,
    train_examples: List[Tuple[torch.Tensor, torch.Tensor]],
    pad_id: int,
    micro_batch_size: int = 2,
    gradient_accumulation_steps: int = 5,
    seed: int = 42,
) -> float:
    """Runs one epoch of prompt-masked causal SFT with gradient accumulation."""
    model.train()
    device = next(model.parameters()).device
    indices = list(range(len(train_examples)))
    random.Random(seed).shuffle(indices)

    losses = []
    optimizer.zero_grad(set_to_none=True)
    accum_count = 0
    for start in range(0, len(indices), micro_batch_size):
        batch_idx = indices[start : start + micro_batch_size]
        max_len = max(train_examples[i][0].size(0) for i in batch_idx)
        b_input = torch.full((len(batch_idx), max_len), pad_id, dtype=torch.long, device=device)
        b_labels = torch.full((len(batch_idx), max_len), -100, dtype=torch.long, device=device)
        b_mask = torch.zeros((len(batch_idx), max_len), dtype=torch.long, device=device)
        for row_i, ex_i in enumerate(batch_idx):
            ids, lbls = train_examples[ex_i]
            L = ids.size(0)
            b_input[row_i, :L], b_labels[row_i, :L], b_mask[row_i, :L] = ids.to(device), lbls.to(device), 1

        out = model(input_ids=b_input, attention_mask=b_mask, labels=b_labels)
        (out.loss / gradient_accumulation_steps).backward()
        losses.append(float(out.loss.item()))
        accum_count += 1
        if accum_count % gradient_accumulation_steps == 0 or (start + micro_batch_size >= len(indices)):
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            optimizer.zero_grad(set_to_none=True)
    return float(np.mean(losses))


def save_worker_outputs(output_dir: Path, worker_group: str, all_rows: List[Dict], all_summaries: List[Dict]) -> None:
    """Atomically persists worker per-item CSV rows and JSON checkpoint summaries."""
    csv_path = output_dir / f"snap_{worker_group}_per_item.csv"
    if all_rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()), lineterminator="\n")
            writer.writeheader()
            writer.writerows(all_rows)
    (output_dir / f"snap_{worker_group}_summaries.json").write_text(json.dumps(all_summaries, indent=2), encoding="utf-8")


def _load_existing_worker_state(output_dir: Path, worker_group: str) -> Tuple[List[Dict], List[Dict], set]:
    """Resumes prior completed checkpoints for a worker_group if present on disk."""
    existing_csv = output_dir / f"snap_{worker_group}_per_item.csv"
    existing_json = output_dir / f"snap_{worker_group}_summaries.json"
    if not (existing_json.exists() and existing_csv.exists()):
        return [], [], set()
    try:
        prev_summ = json.loads(existing_json.read_text(encoding="utf-8"))
        completed_keys = {(s["model"], s["phase"], int(s["epoch"])) for s in prev_summ}
        with open(existing_csv, encoding="utf-8") as fp:
            all_rows = list(csv.DictReader(fp))
        return all_rows, list(prev_summ), completed_keys
    except Exception:
        return [], [], set()


def _load_hf_model_and_tok(mname: str) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Loads a local cached snapshot in bfloat16 on CUDA."""
    mpath = MODEL_SNAPSHOT_PATHS.get(mname, mname)
    tok = AutoTokenizer.from_pretrained(mpath)
    if tok.pad_token_id is None:
        tok.pad_token_id = tok.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(mpath, dtype=torch.bfloat16).to("cuda")
    return model, tok


def _run_phase2_baselines(
    cfg: Dict, splits: Dict[str, List[Dict]], output_dir: Path, worker_group: str,
    all_rows: List[Dict], all_summaries: List[Dict], completed_keys: set,
) -> Dict[str, Tuple[List[Dict], Dict]]:
    """Evaluates Phase 2 baseline checkpoints for a worker_group and caches Epoch-0 SFT reuse."""
    sft_epoch0_cache: Dict[str, Tuple[List[Dict], Dict]] = {}
    for mname in cfg["phase2_models"]:
        if (mname, "phase2_baseline", 0) in completed_keys:
            print(f"[Phase 2 SKIP] {mname} already completed in worker {worker_group}", flush=True)
            continue
        print(f"=== [Phase 2] Loading {mname} on {worker_group} ===", flush=True)
        model, tok = _load_hf_model_and_tok(mname)
        gen_bs = 20 if ("7b" in mname.lower() or "8b" in mname.lower() or "4b" in mname.lower()) else 34
        rows, summ = evaluate_model_state(model, tok, splits, model_name=mname, phase="phase2_baseline", epoch=0, gen_batch_size=gen_bs)
        all_rows.extend(rows)
        all_summaries.append(summ)
        completed_keys.add((mname, "phase2_baseline", 0))
        if mname == cfg["sft_model"]:
            sft_epoch0_cache[mname] = ([{**r, "phase": "phase3_sft_trajectory"} for r in rows], {**summ, "phase": "phase3_sft_trajectory"})
        save_worker_outputs(output_dir, worker_group, all_rows, all_summaries)
        del model
        gc.collect()
        torch.cuda.empty_cache()
    return sft_epoch0_cache


def _select_trainable_params(model: AutoModelForCausalLM, sft_model: str) -> List[torch.nn.Parameter]:
    """Selects attention projections + lm_head on 7B models to fit 80GB VRAM; full params otherwise."""
    if "7b" in sft_model.lower():
        for name, param in model.named_parameters():
            param.requires_grad = any(k in name for k in ("q_proj", "k_proj", "v_proj", "o_proj", "lm_head"))
    else:
        for param in model.parameters():
            param.requires_grad = True
    return [p for p in model.parameters() if p.requires_grad]


def _record_phase3_checkpoint(
    model: AutoModelForCausalLM, tok: AutoTokenizer, splits: Dict[str, List[Dict]],
    output_dir: Path, worker_group: str, sft_model: str, ep: int, gen_bs: int,
    train_loss: float, all_rows: List[Dict], all_summaries: List[Dict], completed_keys: set,
) -> None:
    """Evaluates and persists one Phase 3 SFT checkpoint if not already recorded."""
    if ep not in {1, 3, 5, 10} or (sft_model, "phase3_sft_trajectory", ep) in completed_keys:
        return
    rows_ep, summ_ep = evaluate_model_state(
        model, tok, splits, model_name=sft_model, phase="phase3_sft_trajectory", epoch=ep, gen_batch_size=gen_bs
    )
    summ_ep["train_loss"] = round(train_loss, 6)
    all_rows.extend(rows_ep)
    all_summaries.append(summ_ep)
    completed_keys.add((sft_model, "phase3_sft_trajectory", ep))
    save_worker_outputs(output_dir, worker_group, all_rows, all_summaries)


def _run_phase3_sft(
    cfg: Dict, splits: Dict[str, List[Dict]], output_dir: Path, worker_group: str,
    all_rows: List[Dict], all_summaries: List[Dict], completed_keys: set,
    sft_epoch0_cache: Dict[str, Tuple[List[Dict], Dict]],
) -> None:
    """Runs 10-epoch SFT on orig_contaminated and evaluates Epochs {0, 1, 3, 5, 10}."""
    sft_model = cfg["sft_model"]
    if sft_model is None or all((sft_model, "phase3_sft_trajectory", ep) in completed_keys for ep in (0, 1, 3, 5, 10)):
        return
    print(f"=== [Phase 3 SFT] Loading {sft_model} on {worker_group} ===", flush=True)
    model, tok = _load_hf_model_and_tok(sft_model)
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()

    if (sft_model, "phase3_sft_trajectory", 0) not in completed_keys:
        rows0, summ0 = sft_epoch0_cache.get(sft_model) or evaluate_model_state(
            model, tok, splits, model_name=sft_model, phase="phase3_sft_trajectory", epoch=0
        )
        all_rows.extend(rows0)
        all_summaries.append(summ0)
        completed_keys.add((sft_model, "phase3_sft_trajectory", 0))
        save_worker_outputs(output_dir, worker_group, all_rows, all_summaries)

    optimizer = torch.optim.AdamW(_select_trainable_params(model, sft_model), lr=cfg["sft_lr"], weight_decay=0.01)
    train_examples = build_sft_tensors(tok, splits["orig_contaminated"], max_seq_len=1024)
    gen_bs = 20 if "7b" in sft_model.lower() else 34
    for ep in range(1, 11):
        t_ep = time.time()
        train_loss = train_one_epoch(model, optimizer, train_examples, pad_id=tok.pad_token_id, seed=42 + ep)
        print(f"[SFT TRAIN] {sft_model} | epoch={ep}/10 | train_loss={train_loss:.4f} | {time.time()-t_ep:.1f}s", flush=True)
        _record_phase3_checkpoint(
            model, tok, splits, output_dir, worker_group, sft_model, ep, gen_bs,
            train_loss, all_rows, all_summaries, completed_keys,
        )


def run_worker(data_root: Path, output_dir: Path, worker_group: str) -> None:
    """Executes Phase 2 and Phase 3 work for the named worker_group."""
    if worker_group not in WORKER_CONFIGS:
        raise ValueError(f"Unknown worker_group: {worker_group}")
    seed_everything(42)
    splits = load_splits(data_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg = WORKER_CONFIGS[worker_group]
    all_rows, all_summaries, completed_keys = _load_existing_worker_state(output_dir, worker_group)
    sft_cache = _run_phase2_baselines(cfg, splits, output_dir, worker_group, all_rows, all_summaries, completed_keys)
    _run_phase3_sft(cfg, splits, output_dir, worker_group, all_rows, all_summaries, completed_keys, sft_cache)
    print(f"=== [ALL DONE] Worker {worker_group} completed successfully ===", flush=True)


def main() -> None:
    """CLI entry point for SNAP GPU evaluation and SFT contamination runner."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", type=Path, required=True)
    parser.add_argument("--output_dir", type=Path, required=True)
    parser.add_argument("--worker_group", type=str, choices=list(WORKER_CONFIGS.keys()), required=True)
    args = parser.parse_args()
    run_worker(args.data_root, args.output_dir, args.worker_group)


if __name__ == "__main__":
    main()
