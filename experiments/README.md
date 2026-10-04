# Putnam-Axiom experiment index

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/experiments/README.md>

**TLDR:** This is the canonical index for experiments in `~/putnam-axiom`. Consolidation preserves historical material without starting a run or claiming a historical experiment is complete; new authorized work uses numbered, descriptive homes with versioned runs and live results.

## Current index

There are no newly launched experiments from the consolidation. Historical runtime activity and scientific outcomes have not been established by this file inventory.

| Canonical home | Scope and provenance | Verified status |
|---|---|---|
| [`archive/legacy_logic_contamination/`](archive/legacy_logic_contamination/) | Preserved experiment-specific material from the historical `logic_contamination_experiments` branch; original paths and source revisions are recorded in the [consolidation receipt](../paper_latex_and_notes/consolidation/README.md). | Historical snapshot preserved; execution and results unverified. Archival storage is not a scientific completion verdict. |

The historical snapshot includes the following legacy names. They remain identifiable without allocating new experiment numbers or rewriting their records:

| Historical path in the source branch | Scope evidenced by the files | Outcome |
|---|---|---|
| `experiments/2024/11_nov/` | Training, dataset and tokenization debugging scripts and a sweep configuration. | Unverified. |
| `experiments/logic_contamination/` | A proposed comparison involving training on 53 original Putnam-Axiom examples, with training/inference debugging material. | Hypothesis recorded; no validated outcome asserted here. |
| `experiments/putnam_human_eval_study/` | Human-evaluation preparation, including a 2023 Putnam problem document and dummy optical character recognition (OCR) data. | Preparation artifacts; study execution unverified. |
| `experiments/levenshtein_pg.py` | A small edit-distance demonstration. | Legacy scratch code; not a numbered experiment. |

The exact archived layout is recorded by the consolidation manifest. This table is a provenance index, not permission to run archived scripts. Existing filenames and dates remain unchanged.

## New authorized experiments

Read `~/agents-config/workflows/expts-and-results.md` ([online workflow](https://github.com/brando90/agents-config/blob/main/workflows/expts-and-results.md)) and the current `~/agents-config/INDEX_RULES.md` first. Before choosing the next unused number, check this index, archives, reserved numbers, active branches/worktrees and other owners. Reuse a matching existing home for a continuation.

Create `~/putnam-axiom/experiments/<NN>_<descriptive_setup>/` only for authorized work. The name should say what is compared or measured and the relevant split. Honor an exact user name or workstream label and define the label in the index. Do not preassign a number in this document.

```text
experiments/<NN>_<descriptive_setup>/
├── README.md                 # hypothesis, criterion, method, dependencies, status
├── PROTOCOL.md               # frozen before model-budget spending
├── results.md                # live result ledger, created at launch
├── CKPT_<task>.md            # dated checkpoint for long/dispatched work
└── expt_v1/                  # new setup changes get expt_v2/, and so on
    ├── cc.md                # version-specific execution prompt
    ├── scripts/             # experiment-specific implementation
    ├── data/                # inputs/derived data, subject to access rules
    └── results/             # outputs and RESULTS_<topic>.md reports
```

The tree is a convention, not a scaffold to create before work is authorized. Add a row with the canonical path, question/setup, exact model identifiers and effort when applicable, state, and report links. Preserve each version's inputs and evidence; never overwrite a frozen run to make a new attempt look like the old one.

Before measurement, name the consequential uncertainty, cheapest sufficient comparison, decision criterion and resource bound. A model-budget-spending run needs the locked protocol, complete manifest, exact settings and bounded execution/continuation rules. An evaluation covers every declared model × task × seed/repetition cell, includes the global completion reminder in initial and continuation prompts, and keeps failures, missing and interrupted cells in the full denominator. One successful example does not complete a declared evaluation.

Keep experiment-specific code, data, prompts, configurations, manifests, logs, plots, reports and source archives beneath the same canonical home. Shared production dependencies can remain in `~/putnam-axiom/src/`, and released benchmark data in `~/putnam-axiom/data/`; link them from the experiment. External storage requires an exact location, reason, version/hash where practical and retrieval instructions. Respect private-data and credential boundaries.

## Live records and reporting

Create `results.md` when execution begins. Record the actual start/update timestamps, current state, phase status, measured counts, failures and unresolved stages; commit and push meaningful updates so progress is visible from the canonical repository. Keep detailed outputs and timestamped `RESULTS_<topic>_<MM-DD-YYYY__HH-MM-SS>.md` snapshots under the active version's `results/`. Root `results.md` points to the latest authoritative reports and ends with a project-tagged `**TLDR-end:**`; do not add an opening summary to this live result ledger.

Long or dispatched work also keeps `CKPT_<task>.md` (CKPT means checkpoint), with real `Created:` and `Last updated:` timestamps, execution identity, state, completed steps, blockers and the exact next resume action. Use month-day-year for new human-facing dates. Ordinary experiment documentation uses a title, document link and opening `**TLDR:**`; reusable execution prompts follow the global opening and closing summary formats.

Markdown reports inside the experiment are the primary reporting deliverable. External dashboards and report services require an explicit request. Record measured outcomes, denominators, uncertainty and limitations using `~/agents-config/workflows/statistics-reporting.md`; never infer scientific success from a stopped process, a folder name or a historical script. All model work follows the approved authenticated command-line route and existing resource limits.

## Optional ideas and archives

Use `experiments/ideas/<descriptive_setup>/` for deferred or uncertain-priority proposals, with a separate `experiments/ideas/README.md` index when ideas exist. Keep the hypothesis, motivation, uncertainty, minimal comparison and revisit condition in the idea README; record execution `DEFERRED — NOT RUN` separately from paper inclusion `UNDECIDED`, `INCLUDE` or `OMIT`. Recording an idea does not authorize execution, and a deferred proposal needs no run folders, live results, checkpoint or paper draft.

For an executed strand with a final verdict and no live dependency, move it to `experiments/archive/` in the same commit that records completion/stopping, with a one-sentence outcome and old-to-new map in `experiments/archive/README.md`. Check imports, tests, automation and paper links first; promote shared infrastructure to its established code home rather than burying it in an archive. A README must name any live dependency that keeps concluded work active. Preserve frozen paths/results and coordinate any move of a running checkout.

The consolidation snapshot above is historical preservation with unverified execution status; it is not a newly concluded experiment. No folder renaming, archive entry or policy document authorizes new measurement, a restart, website publication or a change to benchmark reference data.
