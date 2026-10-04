# Putnam-Axiom consolidation record

**Doc link:** <https://github.com/brando90/putnam-axiom/blob/main/paper_latex_and_notes/consolidation/README.md>

**TLDR:** `brando90/putnam-axiom` on `main`, locally `~/putnam-axiom`, is the canonical project. The consolidation preserves current scientific files, imports project-specific harness and historical experiment work, and retires duplicate local checkouts with recoverable backups.

Date: 10-04-2026.

## Canonical contents

The starting `main` revision was `d1bf0cb7b0cf205fa28b55481cda65b811489222`. The laptop had been checked out on `logic_contamination_experiments` at `f4ea749b082f7c209dd8acd250295c93d3dbf4aa`, which diverged from `main`. Its older dataset and evaluation implementations were not merged over the newer main versions.

| Material | Canonical location | Preservation check |
|---|---|---|
| Existing released datasets and shared source | `data/`, existing `src/` files | 182 file hashes match the starting `main`. |
| Final harness task definitions | `src/lm_evaluation_harness/tasks/putnam_axiom/` | Six files copied from `559bd28095842311d62c9ccdf85687f281d80de4`. |
| Historical split-specific harness definitions | `src/lm_evaluation_harness/tasks/putnam_axiom_zipfit/` | Six files copied from `5a2fbe7e4f7e1beb6ffaffaac9d1d1ebea6a752f`. |
| Earlier harness preview, including the 53-problem configuration | `src/lm_evaluation_harness/archive/preview-main/` | Six files copied from `6af252af7849dcdf2d350c9011de05555ca7e2e4`. |
| Historical experiment scripts, training code and output files | `experiments/archive/legacy_logic_contamination/snapshot/` | Original paths and bytes preserved from the experiment branch. Execution and results remain unverified. |
| Agent instructions and new experiment conventions | `AGENTS.md`, `CLAUDE.md`, `experiments/README.md` | Both agent entry points link the current global rules and agree on project behavior. |

The [manifest](manifest.json) records every imported source repository, full commit, original path, destination and SHA-256 (Secure Hash Algorithm, 256-bit) fingerprint. In total, 57 imported files are preserved byte for byte, including the harness license. The active integration has eight named task configurations; archived preview definitions are excluded from its include path.

## Local consolidation and recovery

| Former location | Disposition |
|---|---|
| `~/putnam-axiom` on the experiment branch | Canonical checkout switched to `main`; the experiment branch remains in Git history. |
| `~/putnam axiom` | Retired after a verified compressed backup inside the canonical checkout. The backup preserves its launch-page branch and 145 unstaged source deletions without applying those deletions to `main`. |
| `~/putnam-axiom-preview-lm-evaluation-harness` | Retired after preserving all three branch histories and importing project-specific task files. |
| `~/putnam-axiom/lm-evaluation-harness` | Retired historical submodule checkout; its exact revision and files are recoverable. The canonical branch has no submodule. |

Machine-specific recovery material lives under ignored `~/putnam-axiom/.local/consolidation/`. Its local README describes the archives, hash receipts, Git bundles and private predecessor mirror. Private contents and machine-only receipts are excluded from this public repository. Compressed archives were checked against all original file bytes before retirement: 97 launch-clone files, 15,829 preview-harness files, and 10,103 historical-harness files. Git bundles preserve harness history separately.

Use the canonical checkout for new work. To inspect a retired checkout, extract its archive into a temporary recovery directory rather than recreating a second home-level project. The historical submodule's original `.git` file requires relinking to its restored metadata; its self-contained Git bundle is the simpler history-recovery route.

## Online repositories and in-flight work

The historical [harness fork](https://github.com/brando90/lm-evaluation-harness) was archived on 10-04-2026 after canonical commit [`4137e44`](https://github.com/brando90/putnam-axiom/commit/4137e449965d04755e44eb5c4cf80d21a3e897a1) was pushed. Its description, homepage and README now direct readers here. The [retirement notice](https://github.com/brando90/lm-evaluation-harness/commit/53c820e15e7d702dae5d7cff27d97371d7f25290) is its only added commit; all previous branches and history remain available. The old preview repository address redirects to this archived fork.

The original EleutherAI [pull request #2946](https://github.com/EleutherAI/lm-evaluation-harness/pull/2946) closed unmerged; its successor [#3998](https://github.com/EleutherAI/lm-evaluation-harness/pull/3998) merged on 08-14-2026 as `73da0818e886431c915c9d3356d6eb083a57f3f3`. No open upstream submission depends on keeping this fork writable.

The launch-page [draft pull request #5](https://github.com/brando90/putnam-axiom/pull/5) remains open on `codex/putnam-axiom-launch-page` at `36d6d728ddfe4c2785f39146a2955f82ac85442f`. Its four website files and source branch remain unchanged. They were not relocated into `main` or deployed. The prior agent-instruction branch and original experiment branch are also retained for provenance.

Private predecessor material is retained privately. Separate related research and unrelated repositories are outside this consolidation; no repository visibility was changed.

Final local checks confirmed the three retired checkout paths are absent and all three verified compressed archives remain. The working checkout is on `main`; the public project has zero tracked submodules and zero tracked local recovery files. Detailed before/after remote settings remain in the ignored local receipt.

## Verification scope

Run `python3 src/scripts/verify_consolidation.py` from the canonical checkout (Python 3.10 or later and PyYAML required). It checks the manifest hashes, eight task names, six inherited configuration links, ten function references, syntax of two helper modules, absence of tracked submodules, and exclusion of local recovery files. It never imports evaluation runners, calls a model, downloads a dataset or changes benchmark references.

This proves file preservation and configuration structure at consolidation time. It does not validate historical experiment results, scoring correctness, current remote dataset contents, or model execution. The existing data and evaluation-source fingerprints are a dated migration baseline; future intentional scientific edits must be handled and recorded through their own authorized workflow.
