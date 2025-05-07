#!/usr/bin/env python3
"""
Verify the splits in the zipfit/Putnam-AXIOM-for-zip-fit-splits repository.
"""

import argparse
from datasets import load_dataset

def main():
    # Repository ID
    repo_id = "zipfit/Putnam-AXIOM-for-zip-fit-splits"
    
    # Try to load the dataset
    try:
        print(f"Loading dataset from {repo_id} with fresh download...")
        dataset = load_dataset(repo_id, download_mode="force_redownload")
        print("Successfully loaded dataset directly from HF")
        
        # Check available splits
        print(f"Available splits: {dataset.keys()}")
        
        # Check number of examples in each split
        for split in dataset.keys():
            print(f"Split '{split}': {len(dataset[split])} examples")
        
        # Check if we have the expected splits
        expected_splits = ['train', 'validation', 'test']
        expected_counts = {'train': 150, 'validation': 150, 'test': 222}
        
        has_all_splits = all(split in dataset.keys() for split in expected_splits)
        correct_counts = all(len(dataset.get(split, [])) == count for split, count in expected_counts.items())
        
        if has_all_splits:
            print("\n✅ Repository has all three required splits!")
        else:
            print("\n❌ Repository is missing some required splits!")
            missing_splits = [split for split in expected_splits if split not in dataset.keys()]
            print(f"  Missing splits: {missing_splits}")
        
        if correct_counts:
            print("✅ Split sizes are correct")
        else:
            print("❌ Split sizes are incorrect:")
            for split, expected_count in expected_counts.items():
                actual_count = len(dataset.get(split, []))
                if actual_count != expected_count:
                    print(f"  - Split '{split}' has {actual_count} examples (expected {expected_count})")
        
        # Check for unwanted splits
        unwanted_splits = [split for split in dataset.keys() if split not in expected_splits]
        if not unwanted_splits:
            print("\n✅ No unwanted splits found in repository")
        else:
            print(f"\n❌ Found unwanted splits in repository: {unwanted_splits}")
    
    except Exception as e:
        print(f"Error loading dataset: {e}")

if __name__ == "__main__":
    main() 