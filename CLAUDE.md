# Putnam-Axiom project instructions

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/CLAUDE.md>

**TLDR:** Work from `~/putnam-axiom` and the canonical `brando90/putnam-axiom` repository. Keep each authorized experiment, its code, data, prompts and results together, following the current global rules and the project experiment index.

## Start here

Refresh the shared configuration before working:

```bash
git clone https://github.com/brando90/agents-config.git ~/agents-config 2>/dev/null || git -C ~/agents-config pull --ff-only
```

Refresh and read `~/agents-config/INDEX_RULES.md` at the start of each new task. Then read `~/putnam-axiom/README.md` and `~/putnam-axiom/experiments/README.md`. Use the matching machine documentation and applicable workflows routed by the global index. Keep shared project behavior mirrored in `~/putnam-axiom/AGENTS.md` and `~/putnam-axiom/CLAUDE.md`.

## One canonical project

- Main local checkout: `~/putnam-axiom`; main remote: <https://github.com/brando90/putnam-axiom>.
- Shared code and the EleutherAI Language Model Evaluation Harness integration live in `~/putnam-axiom/src/`; the project-owned task files are in `~/putnam-axiom/src/lm_evaluation_harness/tasks/putnam_axiom/` and the separately preserved historical configuration in `~/putnam-axiom/src/lm_evaluation_harness/tasks/putnam_axiom_zipfit/`. Do not create another project clone or fork as an organizational shortcut. Isolated temporary worktrees remain appropriate for concurrent changes.
- Released benchmark data stays in the established `~/putnam-axiom/data/` home. Experiment-specific code, candidate datasets, inputs, prompts, logs and outputs belong to their experiment instead.
- Papers and notes belong in `~/putnam-axiom/paper_latex_and_notes/`. Check open pull requests and active branches/worktrees before relocation; preserve in-flight work in its existing home until a coordinated change is appropriate. Website work does not authorize deployment.
- Read `~/putnam-axiom/paper_latex_and_notes/consolidation/README.md` before recovering or moving legacy material. Historical snapshots are provenance, not a claim that their experiments completed or their results are valid. Keep private recovery material under the ignored `~/putnam-axiom/.local/` tree.

## Experiments

Read [the experiment workflow](https://github.com/brando90/agents-config/blob/main/workflows/expts-and-results.md) at `~/agents-config/workflows/expts-and-results.md` before starting or continuing an authorized experiment.

1. Reuse an existing canonical home for a continuation. For a distinct authorized experiment, check the index, archives, branches and active worktrees before choosing the next unused `experiments/<NN>_<descriptive_setup>/` number. The name states the comparison or measurement and relevant split; do not invent workstream labels or retrospectively renumber history.
2. Add the experiment to `~/putnam-axiom/experiments/README.md`. Give it a root `README.md` with the hypothesis, decision criterion, dependencies, method, structure and honest status. Keep self-contained iterations in `expt_v1/`, `expt_v2/`, and so on; each has its own prompt, execution code/configuration and `results/`.
3. Freeze `PROTOCOL.md` before model-budget spending: full input manifest, exact model identifiers and effort, prompts, scoring, limits, continuation policy and expected cells. Solver/agent evaluations must cover the full frozen model × task × repetition set within those bounds and retain failures, missing outputs and interruptions in the denominator.
4. Create root `results.md` at launch, update and publish meaningful evidence as it arrives, and link the versioned `RESULTS_<topic>.md` reports. Long or dispatched work also keeps a dated `CKPT_<task>.md` checkpoint with the actual state and next command. Distinguish execution, deliverable completeness and scientific correctness.
5. Keep experiment code and data together. Link genuinely shared dependencies and necessary external storage, including versions/hashes and retrieval instructions. Colocation does not authorize publishing private material. Reports in the experiment folder are sufficient; external dashboards require an explicit request.
6. Follow the archive and optional-ideas policies in the experiment index. Organizational work alone does not authorize running, resuming or expanding an experiment.

## Verification and scientific boundaries

Use approved, locally authenticated command-line interfaces (CLIs) for all large language model (LLM) work; follow the current global model, billing and dispatch rules. Never author direct LLM-provider application programming interface (API) calls or use provider keys. Inspect legacy scripts before execution: their presence in this repository is not execution authorization.

Verify changes with relevant deterministic checks and inspect the exact staged diff for secrets and unintended changes before commit or push. Model-reviewer quality assurance is explicit opt-in under the global rules; do not add automatic review hooks. Changes to benchmark reference answers, labels or specifications have separate both-family acceptance requirements in global Trigger Rule 43. Consolidation must preserve scientific inputs, frozen evidence and recorded results; do not repair or reinterpret them merely to organize files.

Use month-day-year for new human-facing dates and dated names. Follow the current response protocol: define abbreviations on first use, close with the project-tagged `**TLDR-end:**` summary, then show a small concrete `**Snapshot:**` of produced artifacts. Report measurements and missing evidence accurately; a process exit or archive location is not a scientific success claim.
