#!/usr/bin/env python3

import json
import os
from huggingface_hub import login, HfApi, hf_hub_download
from datasets import load_dataset

def main():
    # Paths
    token_path = "/home/brandomiranda/keys/master_hf_token.txt"
    repo_id = "Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
    
    # Read the token
    with open(token_path, 'r') as f:
        token = f.read().strip()
    
    # Login to Hugging Face
    login(token=token)
    
    try:
        # List files in the repository
        api = HfApi()
        files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
        
        print(f"Files in repository {repo_id}:")
        parquet_files = []
        for file in files:
            if file.startswith("data/") and file.endswith(".parquet"):
                parquet_files.append(file)
                
        for file in parquet_files:
            print(f"  - {file}")
        
        # Try loading the dataset
        try:
            print("\nAttempting to load dataset...")
            dataset = load_dataset(repo_id, token=token)
            print(f"Available splits: {list(dataset.keys())}")
            
            # Print details for each split
            for split in dataset:
                print(f"Split '{split}': {len(dataset[split])} examples")
                
        except Exception as e:
            print(f"Error loading dataset: {e}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 