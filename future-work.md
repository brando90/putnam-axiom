# Putnam-AXIOM future work

Items the repo's data and code cannot settle (written Nov 20 2026, from Brando's thesis-defense notes).

- Quantify the error analysis with human or validated-judge grading. Appendix A.3 (Figs 5-10) is qualitative: it shows o1-preview and GPT-4o reaching correct final answers through unjustified claims and logical leaps, but reports no rate, so "how often?" is unanswered.
- Recover the raw per-question logs of the 2024-25 paper runs (o1-preview, GPT-4o, Claude-3.5 Sonnet and the open models). They are not in this repo, in Brando's Drive, or by file name on skampere1 and skampere2 (searched Nov 20 2026). With them: find where the abstract's 19.6 points (46.8% relative) for o1-preview comes from, and run a paired test on the 100 matched pairs for every Table 2 row.
- Settle which fine-tuning setting produced the 12% / 23% before and 33% / 80% after numbers: 5 epochs full-parameter SFT (rebuttals) or the 20-epoch script in `src/contamination_ft.py`, and LoRA or full (Sec 3.4 says LoRA).
- Re-run the fine-tuned model with a documented setting and report its training log.
