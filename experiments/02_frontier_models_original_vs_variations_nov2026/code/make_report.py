#!/usr/bin/env python3
"""Write the final RESULTS markdown (bottom line, Tables 1 and 2, appendix) from results.json. No em dashes."""
import json, subprocess
R = json.load(open("results.json"))
subprocess.run(["python3", "gen_md.py"], capture_output=True)
tables = open("tables.md").read()
g = R["gem38flash"]; o = R["opus55"]; s = R["sonnet55"]
gv_n = g["var_n"]
gem_cost = g["cost"]
oai_cost = sum(R[k]["cost"] for k in ("astra62", "astra6", "gpt55", "gpt4o"))

def f(x, d=1): return "n/a" if x is None else f"{x:.{d}f}"

gem_var_j = "judged" if g["var_judged"] is not None else "not judged"

md = f"""# Putnam-AXIOM on the newest frontier models: Original and Functional Variations, no agent (Nov 20, 2026)

## Bottom line

Frontier models now solve about three quarters of Putnam-AXIOM Original under the paper's own grader, against 42% for o1-preview and 19% for GPT-4o at release (arXiv 2508.08292, Table 1): Claude Opus 5.5 {f(o['orig']['acc'])}% (n={o['orig']['n']} of 522), Claude Sonnet 5.5 {f(s['orig']['acc'])}%, gpt-6-astra {f(R['astra6']['orig']['acc'])}%, gpt-6.2-astra {f(R['astra62']['orig']['acc'])}%, gpt-5.5 {f(R['gpt55']['orig']['acc'])}%. The paper grader marks many correct answers wrong (formatting, extra cases), so an answer-equivalence judge on the misses lifts these models to 86% to 91%. The original-versus-variation gap has not closed: on the matched 100 problems the new models score 6 to 14 points lower on Functional Variations, about the same size as the 8-point gaps of o1-preview and GPT-4o in the paper. Our reruns of GPT-4o ({f(R['gpt4o']['orig']['acc'])}% vs 19.35% in the paper) and Qwen2-Math-7B-Instruct ({f(R['qwen2math7b']['orig']['acc'])}% vs 11.49%) land close to the published numbers, so the pipeline is sound. Gemini 3.8 Flash scored {f(g['m100']['acc'])}% on the matched 100 originals (n={g['m100']['n']}); its variation row is snapshot 1 only (n={gv_n}). Claude Opus 5.5 stopped at the 5-hour usage limit with {o['var_n']} of 500 variation problems done, and Fable 5.2, Fable 5.1 and "Claude 6.2" did not run (Appendix D).

## Tables

Accuracy is boxed exact match under the paper protocol (lm-eval-harness 4-shot prompt, last `\\boxed{{}}` answer, the repo's own sympy equivalence check, unchanged). The judged column counts a paper-grader miss as correct when a gpt-5.5 judge says the final answer is mathematically equivalent to the reference (Appendix B). For Table 2 the variation score is the mean of the 5 snapshots of 100 where all 5 are complete, else pooled over the problems that ran (n column). The gap is the matched-100 original score minus the variation score. Intervals are 95% Wilson on the paper-grader score.

{tables}
Paper numbers for comparison (arXiv 2508.08292). Table 1, original 522, boxed accuracy: o1-preview 219/522 = 41.94%, GPT-4o 101/522 = 19.35%, Claude-3.5 Sonnet 83/522 = 15.96%, GPT-4 59/522 = 11.30%, Qwen2-Math-7B-Instruct 60/522 = 11.49%. Variation versus matched originals (main-text Table 2 and Appendix A.1, correct out of 100): o1-preview 43 vs 51, GPT-4o 22 vs 30, Claude-3.5 Sonnet 27 vs 28, DeepSeek-R1-Distill-Qwen-32B 24 vs 33, Qwen2-Math-7B-Instruct 14 vs 18.

### Now versus at release (paper grader, original 522)

| Model | At release (paper) | Now (this run) |
|---|---|---|
| o1-preview | 41.94% | not rerun |
| GPT-4o | 19.35% | {f(R['gpt4o']['orig']['acc'])}% (same model, our rerun) |
| Qwen2-Math-7B-Instruct | 11.49% | {f(R['qwen2math7b']['orig']['acc'])}% (same model, our rerun) |
| Best new model | n/a | {f(o['orig']['acc'])}% Claude Opus 5.5 (n={o['orig']['n']}) |

## Appendix

### A. Protocol and harness

- Task: Putnam-AXIOM Original (522) and Functional Variations (500 problems = 5 snapshots of 100). The matched 100 originals are the subset the variations were generated from (a subset of the 522).
- Prompt: the lm-eval-harness putnam_axiom task prompt (description plus 4 few-shot examples), sent as one user message. One turn, no tools, no agent, no retries on content.
- OpenAI rows: plain Responses API calls, store off, no tools; effort max for gpt-6-astra and gpt-6.2-astra, high for gpt-5.5, default for gpt-4o. Key is the Koyejo-lab key, read on the cluster only.
- Claude rows: Claude Code print mode with tools off, a one-line system prompt, no session persistence, default effort and no extended thinking budget set (so no "Max" effort, and about 1.2k output tokens per problem against 2.4k to 3.7k for the OpenAI rows). Sonnet 5.5 ran on Claude Code 2.1.278 and Opus 5.5 on 2.1.329, both on the Stanford enterprise login.
- Gemini row: generateContent, thinkingLevel high, one worker, Allen's key. The key's readme says it is for VeriBench evaluations only; Brando asked for this Putnam-AXIOM use himself in his Nov 19 22:27 voice note. The key is not written to any file or message.
- Qwen row: Hugging Face transformers, greedy, plain few-shot completion prompt, 1024 new tokens, local weights on one skampere2 GPU. {f(R['qwen2math7b']['truncated'] / R['qwen2math7b']['n_rows'] * 100, 0)}% of outputs hit the 1024-token cap.
- Run on skampere2 (Stanford) overnight, Nov 19 to Nov 20.

### B. Grader noise and the judge

- The repo normalizer rewrites "\\left" as "\\le" and strips whitespace, and sympy cannot compare answers with extra cases or text. Feeding the reference answer back as the model output scores 499/522 on Original and 490/500 on Variations, so the paper grader itself loses points even for a perfect answer.
- The judge is gpt-5.5 (effort medium, OpenAI Responses API), shown the raw last-boxed answer and the raw reference for each paper-grader miss only. Items the paper grader already accepted are not rejudged.
- Cross-check: a Claude Sonnet 5.5 judge on the gpt-6.2-astra misses called 153 equivalent against 123 for the GPT judge (83% agreement); Sonnet was more lenient on answers with extra cases. The tables use the stricter GPT judge, so the judged column is closer to a lower bound.
- Judged accuracy is an addition to the paper protocol, shown beside it, not a replacement.

### C. Rows, sample sizes and caveats

- Claude Opus 5.5: {o['orig']['n']} of 522 originals (one problem missing, not retried), all 100 matched originals, and {o['var_n']} of 500 variation problems (snapshot 1 complete, snapshots 2 to 5 about 61 each). The Claude Code 5-hour limit on the shared login stopped the run at 04:00 and it resets at 8:30. The Opus gap uses pooled variation accuracy over those {o['var_n']} problems, so treat it as indicative. Resuming is a one-line rerun of the same command (the runner skips finished problems).
- Claude Sonnet 5.5: 1021 of 1022 problems; one snapshot-4 problem hung and was not retried (variation n=499).
- Gemini 3.8 Flash: matched-100 originals complete; variation snapshot 1 only (n={gv_n} of 500); the other 422 originals and snapshots 2 to 5 were not run (about 11k to 14k output tokens per problem and one worker, so about 0.5 problems a minute). Its gap compares the matched 100 originals with snapshot 1.
- Matched-100 accuracy and variation accuracy come from different problem sets, so a gap of a few points is within noise: the 95% interval on a 100-problem score is roughly plus or minus 8 points.
- Single run per model, no repeats; token counts are as reported by each API or CLI.

### D. Asked for but not run

- "Claude 6.2": no model of that name is on Anthropic's models page. Claude Sonnet 5.5 and Claude Opus 5.5 ran instead.
- Fable 5.2 and Fable 5.1: the Stanford login returns "usage credits required" for Fable, and no API gateway key for them exists in the stored files. "Max" is an effort level, not a model; the Claude rows ran at default effort.
- Qwen: only Qwen2-Math-7B-Instruct, the paper's own model, ran. No newer Qwen ran.
- o3 was started and stopped before it produced results; it is not in the tables.

### E. Cost

- OpenAI API (Koyejo-lab key), at list prices from third-party trackers: gpt-6.2-astra ${f(R['astra62']['cost'])}, gpt-6-astra ${f(R['astra6']['cost'])}, gpt-5.5 ${f(R['gpt55']['cost'])}, gpt-4o ${f(R['gpt4o']['cost'])}; judge about $13. Total about ${f(oai_cost + 13, 0)}.
- Gemini 3.8 Flash (Allen's key): about ${f(gem_cost, 0)} at list price ($0.75 in, $3.75 out per million).
- Claude: no cash cost on the Stanford enterprise login; the Claude Code CLI reports an API-equivalent $23.47 for Sonnet 5.5 and $38.34 for Opus 5.5.
- Qwen: local GPU, no cost.

## Open for Brando

- Fable 5.2 and 5.1 route: a Stanford AI API Gateway key on your PTA (form "Add AI API Gateway Key": tick Opus 5.5, Fable 5.1 and Fable 5.2, set a monthly cap, 2 to 5 days, PTA owner approval). List prices per million input and output tokens: Opus 5.5 $4 and $20, Fable 5.2 $8 and $40, Fable 5.1 $10 and $50. A Fable 5.2 run like the OpenAI ones (about 1.7M in, 2.5M to 3.5M out) would cost roughly $115 to $155.
- Anthropic's AI for Science program offers up to $20,000 of API credits.
- Finish Opus 5.5 after 8:30 (about 150 variation problems left), and run the one hung Sonnet problem.
"""
open("RESULTS_frontier_models_original_vs_variations_nov2026.md", "w").write(md)
print(len(md), "chars")
