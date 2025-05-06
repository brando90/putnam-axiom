#!/bin/bash

# Set strict error handling
set -e

echo "Starting Putnam-AXIOM dataset reorganization..."

# Step 1: Push the Putnam-AXIOM validation and test splits to the ZIP-FIT HF repo
echo "Step 1: Pushing validation and test splits to ZIP-FIT repo..."
cd /home/brandomiranda/ZIP-FIT/data
python3 push_putnam_axiom_to_zipfit.py

# Step 2: Push the README to the ZIP-FIT repo
echo "Step 2: Pushing README to ZIP-FIT repo..."
cd /home/brandomiranda/ZIP-FIT/data
python3 push_readme_to_zipfit.py

# Step 3: Update the original Putnam-AXIOM dataset to remove validation and test splits
echo "Step 3: Updating original Putnam-AXIOM dataset to remove validation and test splits..."
cd /home/brandomiranda/putnam-axiom/data/scripts_push_2_hf
python3 update_original_putnam_axiom.py

# Step 4: Push the variations data to the original Putnam-AXIOM HF repository
echo "Step 4: Pushing variations data to original Putnam-AXIOM repo..."
cd /home/brandomiranda/putnam-axiom/data/scripts_push_2_hf
python3 push_variations_to_putnam_axiom.py

# Step 5: Push the updated README to the original Putnam-AXIOM repo
echo "Step 5: Pushing updated README to original Putnam-AXIOM repo..."
cd /home/brandomiranda/putnam-axiom/data/scripts_push_2_hf
python3 push_readme_to_putnam_axiom.py

echo "Dataset reorganization complete!"
echo "✅ Pushed validation and test splits to zipfit/Putnam-AXIOM-for-zip-fit-splits"
echo "✅ Updated Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522 to remove validation and test splits"
echo "✅ Added variations data to Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
echo "✅ Updated README files in both repositories" 