# Putnam-AXIOM HuggingFace Push Scripts

This directory contains essential scripts for managing the Putnam-AXIOM dataset on Hugging Face.

## Essential Files

1. **push_variations_to_putnam_axiom.py**
   - Primary script for pushing the three main splits to Hugging Face:
     - `full_eval` (522 examples): Complete set of original problems
     - `originals_for_generating_vars` (100 examples): Original problems used for generating variations
     - `variations` (500 examples): Generated variations of original problems

2. **final_cleanup.py**
   - Performs final verification and cleanup of the repository
   - Updates README and configuration files
   - Ensures repository structure matches specifications

3. **verify_splits_from_hf.py**
   - Verification script to check that the HuggingFace repository contains:
     - Exactly the three required splits
     - Correct number of examples in each split
     - No unwanted split files

4. **updated_readme_clean_splits.md**
   - The current README file for the HuggingFace repository
   - Contains dataset documentation, citation information, and usage examples

5. **cleanup_repository.py**
   - Script used to clean up unnecessary files in this repository
   - Created backups in the `/data/archive` directory

## Data Files

The main dataset file is located at `/home/brandomiranda/putnam-axiom/data/Putnam_AXIOM_Original_v3.json`.

## HuggingFace Repositories

- **Main Repository**: [Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522](https://huggingface.co/datasets/Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522)
  - Contains the three main splits

- **Splits Repository**: [zipfit/Putnam-AXIOM-for-zip-fit-splits](https://huggingface.co/datasets/zipfit/Putnam-AXIOM-for-zip-fit-splits)
  - Contains validation and test splits for ZIP-FIT methodology research

## Usage

To verify the current state of the HuggingFace repository:
```
python verify_splits_from_hf.py
```

To update the README and perform final cleanup:
```
python final_cleanup.py
``` 