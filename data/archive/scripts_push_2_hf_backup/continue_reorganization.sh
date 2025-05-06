#!/bin/bash

# Set strict error handling
set -e

echo "Continuing Putnam-AXIOM dataset reorganization from step 4..."

# Step 4: Push the variations data to the original Putnam-AXIOM HF repository
echo "Step 4: Pushing variations data to original Putnam-AXIOM repo..."
cd /home/brandomiranda/putnam-axiom/data/scripts_push_2_hf
python3 push_variations_to_putnam_axiom.py

# Step 5: Push the updated README to the original Putnam-AXIOM repo
echo "Step 5: Pushing updated README to original Putnam-AXIOM repo..."
cd /home/brandomiranda/putnam-axiom/data/scripts_push_2_hf
python3 push_readme_to_putnam_axiom.py

echo "Dataset reorganization complete!"
echo "✅ Pushed validation and test splits to zipfit/Putnam-AXIOM-for-zip-fit-splits (previously completed)"
echo "✅ Updated Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522 to remove validation and test splits (previously completed)"
echo "✅ Added variations data to Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
echo "✅ Updated README files in both repositories" 