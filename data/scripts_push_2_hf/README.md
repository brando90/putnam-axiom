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

6. **fix_zipfit_splits.py**
   - Script to update the zipfit/Putnam-AXIOM-for-zip-fit-splits repository
   - Creates three splits from the full dataset:
     - `train` (150 examples)
     - `validation` (150 examples)
     - `test` (222 examples)

7. **verify_zipfit_splits.py**
   - Verification script for the zipfit repository
   - Checks that all required splits exist with the correct number of examples

## Data Files

The main dataset file is located at `data/Putnam_AXIOM_Original_v3.json`.
``` 