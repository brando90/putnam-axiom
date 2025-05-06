#!/usr/bin/env python3

import os
import json
import shutil
from datasets import load_dataset
from huggingface_hub import login, HfApi

def main():
    # Paths
    token_path = "/home/brandomiranda/keys/master_hf_token.txt"
    repo_id = "Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
    
    # Read the token
    with open(token_path, 'r') as f:
        token = f.read().strip()
    
    # Login to Hugging Face
    login(token=token)
    
    # Clear cache to ensure fresh download
    cache_dir = os.path.expanduser("~/.cache/huggingface/datasets")
    if os.path.exists(cache_dir):
        print(f"Clearing HF datasets cache: {cache_dir}")
        # Only remove the specific dataset cache
        for dir_name in os.listdir(cache_dir):
            if "Putnam-AXIOM--putnam-axiom-dataset-ICML-2025-522" in dir_name:
                path = os.path.join(cache_dir, dir_name)
                print(f"Removing {path}")
                shutil.rmtree(path, ignore_errors=True)
    
    # Load directly from HF
    print(f"Loading dataset from {repo_id} with fresh download...")
    
    # Try loading the dataset to verify the structure
    try:
        dataset = load_dataset(repo_id, token=token, cache_dir=None)
        print(f"Successfully loaded dataset directly from HF")
        print(f"Available splits: {list(dataset.keys())}")
        
        # Print details for each split
        for split in dataset:
            print(f"Split '{split}': {len(dataset[split])} examples")
        
        # Verify the split contents
        if set(dataset.keys()) == set(['full_eval', 'originals_for_generating_vars', 'variations']):
            print("\n✅ VERIFICATION SUCCESSFUL: Repository has exactly the three required splits!")
            
            # Let's also check each split's size
            if len(dataset['full_eval']) == 522 and len(dataset['originals_for_generating_vars']) == 100 and len(dataset['variations']) == 500:
                print("✅ Split sizes are correct")
            else:
                print("⚠️ Split sizes are not as expected")
                print(f"Expected: full_eval=522, originals_for_generating_vars=100, variations=500")
                print(f"Actual: full_eval={len(dataset['full_eval'])}, originals_for_generating_vars={len(dataset['originals_for_generating_vars'])}, variations={len(dataset['variations'])}")
        else:
            print("\n⚠️ VERIFICATION FAILED: Repository still has incorrect splits.")
            print(f"Current splits: {list(dataset.keys())}")
            print(f"Expected splits: ['full_eval', 'originals_for_generating_vars', 'variations']")
        
    except Exception as e:
        print(f"Error verifying dataset: {e}")
    
    # Also check the repository structure
    try:
        api = HfApi()
        files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
        
        # Check for any unwanted split files
        unwanted_files = []
        unwanted_splits = ["validation", "test", "val"]
        for file in files:
            if any(f"/{unwanted_split}-" in file for unwanted_split in unwanted_splits):
                unwanted_files.append(file)
        
        if unwanted_files:
            print("\n⚠️ Found unwanted files in repository:")
            for file in unwanted_files:
                print(f"  - {file}")
        else:
            print("\n✅ No unwanted split files found in repository")
    except Exception as e:
        print(f"Error checking repository files: {e}")

if __name__ == "__main__":
    main() 