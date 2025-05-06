# Putnam-AXIOM Dataset

This directory contains the Putnam-AXIOM dataset files and scripts related to the ICML 2025 paper.

## Directory Structure

- **Putnam_AXIOM_Original_v3.json** - The main dataset file containing 522 Putnam problems with solutions.

- **scripts_push_2_hf/** - Scripts for pushing data to HuggingFace repositories:
  - See the README in this directory for details on each script
  - Contains scripts for verification, cleanup, and data management

- **Putnam-AXIOM_Variations/**,  **Putnam-AXIOM_Variations_v3/**, **Putnam-AXIOM_Variations_v4/** - 
  Directories containing various versions of generated variations for the original problems.

- **archive/** - Backup directory containing all previously used scripts and data files.

## HuggingFace Datasets

The dataset is published on HuggingFace in two repositories:

1. **Main Dataset**: [Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522](https://huggingface.co/datasets/Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522)
   - Contains the primary splits: `full_eval`, `originals_for_generating_vars`, `variations`

2. **ZIP-FIT Splits**: [zipfit/Putnam-AXIOM-for-zip-fit-splits](https://huggingface.co/datasets/zipfit/Putnam-AXIOM-for-zip-fit-splits)
   - Contains validation and test splits used for the ZIP-FIT research methodology

## Paper

The ICML 2025 paper is available on OpenReview: [https://openreview.net/forum?id=kqj2Cn3Sxr](https://openreview.net/forum?id=kqj2Cn3Sxr)

Earlier preprint: [https://openreview.net/pdf?id=YXnwlZe0yf](https://openreview.net/pdf?id=YXnwlZe0yf) 