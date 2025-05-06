#!/bin/bash

# Set strict error handling
set -e

echo "Starting Putnam-AXIOM repository cleanup..."

# Step 1: Clean up the splits to keep only the required ones
echo "Step 1: Cleaning up splits to keep only full_eval, originals_for_generating_vars, and variations..."
cd /home/brandomiranda/putnam-axiom/data/scripts_push_2_hf
python3 cleanup_putnam_axiom_splits.py

# Step 2: Update the README to reflect the changes
echo "Step 2: Updating README to match the new repository structure..."
cd /home/brandomiranda/putnam-axiom/data/scripts_push_2_hf
python3 push_updated_readme_to_putnam.py

echo "Cleanup complete!"
echo "✅ Removed redundant splits from Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
echo "✅ Now repository contains only: full_eval, originals_for_generating_vars, and variations"
echo "✅ Updated README to reflect the current structure" 