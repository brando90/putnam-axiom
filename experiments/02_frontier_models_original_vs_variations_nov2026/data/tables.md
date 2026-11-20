### Table 1. Putnam-AXIOM Original (522 problems)

| Model | Harness and route | n | Accuracy, paper grader (%) | 95% CI | Accuracy, answer-equivalence judge (%) |
|---|---|---|---|---|---|
| claude-opus-5-5 (default effort) | none (Claude Code 2.1.329 print mode, tools off, one turn); Stanford enterprise login (claude-su profile) on skampere2 | 522 | 78.9 | 75.2 to 82.2 | 90.6 |
| claude-sonnet-5-5 (default effort), substitute for Claude 6.2 | none (Claude Code 2.1.278 print mode, tools off, one turn); Stanford enterprise login (claude-su) on skampere2 | 522 | 77.4 | 73.6 to 80.8 | 89.5 |
| gpt-6.2-astra (effort max) | none (plain call, no tools); OpenAI Responses API, Koyejo-lab key, run from skampere2 | 522 | 72.0 | 68.0 to 75.7 | 87.9 |
| gpt-6-astra (effort max) | none (plain call, no tools); OpenAI Responses API, Koyejo-lab key, run from skampere2 | 522 | 72.4 | 68.4 to 76.1 | 87.9 |
| gpt-5.5 (effort high) | none (plain call, no tools); OpenAI Responses API, Koyejo-lab key, run from skampere2 | 522 | 71.8 | 67.8 to 75.5 | 86.2 |
| gemini-3.8-flash (thinking high) | none (plain call, no tools); Gemini API generateContent, Allen's key, run from skampere2 | 100 | 87.0 | 79.0 to 92.2 | 90.0 |
| gpt-4o (same model as the paper) | none (plain call, no tools); OpenAI Responses API, Koyejo-lab key, run from skampere2 | 522 | 21.3 | 18.0 to 25.0 | 23.9 |
| Qwen2-Math-7B-Instruct (same model as the paper) | none (HF transformers, greedy, plain few-shot completion prompt, 1024 new tokens); local weights on skampere2 GPU 0 | 522 | 15.3 | 12.5 to 18.7 | 17.0 |

### Table 2. Putnam-AXIOM Functional Variations (500 problems = 5 snapshots of 100)

| Model | Harness and route | n | Accuracy, paper grader (%) | 95% CI | Accuracy, answer-equivalence judge (%) | Matched 100 originals, paper grader (%) | Gap original minus variation, paper grader (points) | Gap, judge (points) |
|---|---|---|---|---|---|---|---|---|
| claude-opus-5-5 (default effort) | none (Claude Code 2.1.329 print mode, tools off, one turn); Stanford enterprise login (claude-su profile) on skampere2 | 500 | 73.6 | 69.6 to 77.3 | 85.8 | 83.0 (n=100) | 9.4 | 6.2 |
| claude-sonnet-5-5 (default effort), substitute for Claude 6.2 | none (Claude Code 2.1.278 print mode, tools off, one turn); Stanford enterprise login (claude-su) on skampere2 | 500 | 71.2 | 67.1 to 75.0 | 82.4 | 83.0 (n=100) | 11.8 | 10.6 |
| gpt-6.2-astra (effort max) | none (plain call, no tools); OpenAI Responses API, Koyejo-lab key, run from skampere2 | 500 | 69.0 | 64.8 to 72.9 | 79.4 | 81.0 (n=100) | 12.0 | 9.6 |
| gpt-6-astra (effort max) | none (plain call, no tools); OpenAI Responses API, Koyejo-lab key, run from skampere2 | 500 | 69.4 | 65.2 to 73.3 | 80.8 | 82.0 (n=100) | 12.6 | 8.2 |
| gpt-5.5 (effort high) | none (plain call, no tools); OpenAI Responses API, Koyejo-lab key, run from skampere2 | 500 | 68.6 | 64.4 to 72.5 | 78.8 | 80.0 (n=100) | 11.4 | 8.2 |
| gemini-3.8-flash (thinking high) | none (plain call, no tools); Gemini API generateContent, Allen's key, run from skampere2 | 100 | 73.0 | 63.6 to 80.7 | 82.0 | 87.0 (n=100) | 14.0 | 8.0 |
| gpt-4o (same model as the paper) | none (plain call, no tools); OpenAI Responses API, Koyejo-lab key, run from skampere2 | 500 | 23.4 | 19.9 to 27.3 | 27.6 | 27.0 (n=100) | 3.6 | -0.6 |
| Qwen2-Math-7B-Instruct (same model as the paper) | none (HF transformers, greedy, plain few-shot completion prompt, 1024 new tokens); local weights on skampere2 GPU 0 | 500 | 16.0 | 13.0 to 19.5 | 16.8 | 19.0 (n=100) | 3.0 | 3.2 |
