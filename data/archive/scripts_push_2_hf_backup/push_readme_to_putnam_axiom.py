#!/usr/bin/env python3

import os
from huggingface_hub import login, HfApi
from datasets import load_dataset

def main():
    # Paths
    readme_path = "/home/brandomiranda/putnam-axiom/data/scripts_push_2_hf/updated_readme_for_putnam_axiom.md"
    token_path = "/home/brandomiranda/keys/master_hf_token.txt"
    repo_id = "Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
    
    # Read the token
    with open(token_path, 'r') as f:
        token = f.read().strip()
    
    # Login to Hugging Face
    login(token=token)
    api = HfApi()
    
    # First check if the repo exists
    try:
        # Try to load the dataset to confirm the repo exists
        dataset = load_dataset(repo_id)
        print(f"Found existing repository: {repo_id}")
    except Exception as e:
        print(f"Repository not found or error accessing it: {e}")
        return
    
    # Upload the README
    print(f"Uploading README to {repo_id}...")
    api.upload_file(
        path_or_fileobj=readme_path,
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="Update README with information about variations data"
    )
    
    print("Successfully uploaded README to the repository.")

if __name__ == "__main__":
    main() 