#!/usr/bin/env python3

import json
import os
from pathlib import Path
import datasets
from datasets import Dataset, Features, Value
from huggingface_hub import login, HfApi

def load_existing_data(repo_id, token_path):
    """Load the existing dataset from Hugging Face."""
    # Read the token
    with open(token_path, 'r') as f:
        token = f.read().strip()
    
    # Login to Hugging Face
    login(token=token)
    
    # Try to load the existing dataset
    try:
        existing_dataset = datasets.load_dataset(repo_id, use_auth_token=token)
        print(f"Loaded existing dataset with splits: {list(existing_dataset.keys())}")
        
        # Convert to Python dictionaries
        result = {}
        for split_name in existing_dataset:
            if split_name in ['full_eval', 'originals_for_generating_vars', 'variations']:
                result[split_name] = []
                for i in range(len(existing_dataset[split_name])):
                    item = dict(existing_dataset[split_name][i])
                    result[split_name].append(item)
                
                print(f"Kept {len(result[split_name])} examples from {split_name} split")
            else:
                print(f"Skipping split: {split_name}")
        
        return result
    except Exception as e:
        print(f"Could not load existing dataset: {e}")
        return {}

def get_dataset_schema():
    """Define a consistent schema for all datasets."""
    return Features({
        'id': Value('string'),
        'problem': Value('string'),
        'solution': Value('string'),
        'answer_type': Value('string'),
        'source': Value('string'),
        'type': Value('string'),
        'original_problem': Value('string'),
        'original_solution': Value('string'),
        'year': Value('string'),
        'variation': Value('int64')
    })

def dataset_to_hf_format(data_list):
    """Convert the list of dictionaries to the format expected by Hugging Face datasets."""
    if not data_list:
        return Dataset.from_dict({})
    
    # Use fixed schema for consistency
    schema = get_dataset_schema()
    
    # Initialize dataset with empty lists for each key in schema
    dataset_dict = {key: [] for key in schema.keys()}
    
    # Fill the dataset dictionary
    for item in data_list:
        for key in dataset_dict:
            if key in item:
                dataset_dict[key].append(item[key])
            else:
                # Handle missing keys with an appropriate default value
                dataset_dict[key].append("" if key != "variation" else 0)
    
    return Dataset.from_dict(dataset_dict, features=schema)

def push_dataset(splits, repo_id, token_path):
    """Push the dataset to Hugging Face."""
    # Read the token
    with open(token_path, 'r') as f:
        token = f.read().strip()
    
    # Login to Hugging Face
    login(token=token)
    
    # Create a DatasetDict with the splits
    dataset_dict = {}
    for split_name, split_data in splits.items():
        dataset_dict[split_name] = dataset_to_hf_format(split_data)
    
    # Create a datasets.DatasetDict from the dictionary
    hf_dataset = datasets.DatasetDict(dataset_dict)
    
    # Push to Hugging Face
    hf_dataset.push_to_hub(repo_id, private=True)
    
    print(f"Successfully pushed dataset with {len(splits)} splits to {repo_id}")
    for split_name, split_data in splits.items():
        print(f"- {split_name}: {len(split_data)} examples")

def main():
    # Paths
    token_path = "/home/brandomiranda/keys/master_hf_token.txt"
    repo_id = "Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
    
    # Load existing data (only keeping specific splits)
    print(f"Loading and filtering data from repository: {repo_id}")
    splits = load_existing_data(repo_id, token_path)
    
    if not splits:
        print("Error: Failed to load existing splits. Aborting.")
        return
    
    # Verify we have the required splits
    required_splits = ["full_eval", "originals_for_generating_vars", "variations"]
    for split in required_splits:
        if split not in splits:
            print(f"Error: Required split '{split}' not found in existing data. Aborting.")
            return
    
    # Push the cleaned dataset with only the required splits
    print(f"Pushing cleaned dataset to {repo_id} with only 3 splits")
    push_dataset(splits, repo_id, token_path)
    
    print("Done! Repository now contains only full_eval, originals_for_generating_vars, and variations splits.")

if __name__ == "__main__":
    main() 