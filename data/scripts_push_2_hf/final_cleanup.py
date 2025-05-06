#!/usr/bin/env python3

import json
import os
import time
from pathlib import Path
import tempfile
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
    api = HfApi()
    
    # 1. Ensure README reflects correct structure
    print("Updating README to match new structure...")
    readme_path = "/home/brandomiranda/putnam-axiom/data/scripts_push_2_hf/updated_readme_clean_splits.md"
    try:
        api.upload_file(
            path_or_fileobj=readme_path,
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Update README to reflect only three splits"
        )
        print("✅ Successfully updated README.md")
    except Exception as e:
        print(f"⚠️ README update issue: {e}")
    
    # 2. Try to fix the .gitattributes file
    try:
        # Download the current gitattributes file
        attr_path = None
        files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
        for file in files:
            if file.endswith(".gitattributes"):
                attr_path = file
                break
        
        if attr_path:
            # Download and update the file
            print(f"Found .gitattributes file: {attr_path}")
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                try:
                    local_path = hf_hub_download(repo_id=repo_id, filename=attr_path, repo_type="dataset", token=token)
                    print(f"Downloaded .gitattributes to {local_path}")
                    
                    # Read the file and filter out unwanted splits
                    with open(local_path, 'r') as f:
                        lines = f.readlines()
                    
                    # Keep only lines not referencing unwanted splits
                    unwanted_splits = ["validation", "test", "val"]
                    new_lines = []
                    for line in lines:
                        if not any(f"/{unwanted_split}-" in line for unwanted_split in unwanted_splits):
                            new_lines.append(line)
                    
                    # Write the filtered content
                    with open(tmp.name, 'w') as f:
                        f.writelines(new_lines)
                    
                    # Upload the modified file
                    api.upload_file(
                        path_or_fileobj=tmp.name,
                        path_in_repo=attr_path,
                        repo_id=repo_id,
                        repo_type="dataset",
                        commit_message="Update .gitattributes to remove references to deleted splits"
                    )
                    print("✅ Updated .gitattributes file")
                except Exception as e:
                    print(f"⚠️ Error updating .gitattributes: {e}")
        else:
            print("⚠️ Could not find .gitattributes file")
    except Exception as e:
        print(f"⚠️ Error with .gitattributes: {e}")
    
    # 3. Clean up the dataset_info.json file if it exists
    try:
        # Find the dataset_info.json file
        dataset_info_path = None
        files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
        for file in files:
            if file.endswith("dataset_info.json"):
                dataset_info_path = file
                break
        
        if dataset_info_path:
            print(f"Found dataset_info.json at {dataset_info_path}")
            # Download and update the file
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                try:
                    local_path = hf_hub_download(repo_id=repo_id, filename=dataset_info_path, repo_type="dataset", token=token)
                    print(f"Downloaded dataset_info.json to {local_path}")
                    
                    # Read the file
                    with open(local_path, 'r') as f:
                        dataset_info = json.load(f)
                    
                    # Update the splits information
                    if 'splits' in dataset_info:
                        if isinstance(dataset_info['splits'], list):
                            dataset_info['splits'] = [
                                s for s in dataset_info['splits'] 
                                if s.get('name') in ['full_eval', 'originals_for_generating_vars', 'variations']
                            ]
                            print("Updated splits list in dataset_info.json")
                        elif isinstance(dataset_info['splits'], dict):
                            new_splits = {}
                            for split_name, split_data in dataset_info['splits'].items():
                                if split_name in ['full_eval', 'originals_for_generating_vars', 'variations']:
                                    new_splits[split_name] = split_data
                            dataset_info['splits'] = new_splits
                            print("Updated splits dict in dataset_info.json")
                    
                    # Write the updated content
                    with open(tmp.name, 'w') as f:
                        json.dump(dataset_info, f, indent=2)
                    
                    # Upload the modified file
                    api.upload_file(
                        path_or_fileobj=tmp.name,
                        path_in_repo=dataset_info_path,
                        repo_id=repo_id,
                        repo_type="dataset",
                        commit_message="Update dataset_info.json to remove references to deleted splits"
                    )
                    print("✅ Updated dataset_info.json")
                except Exception as e:
                    print(f"⚠️ Error updating dataset_info.json: {e}")
        else:
            print("⚠️ Could not find dataset_info.json")
    except Exception as e:
        print(f"⚠️ Error with dataset_info.json: {e}")
    
    # 4. Create and update a config.json file to explicitly define the splits
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            config = {
                "splits": ["full_eval", "originals_for_generating_vars", "variations"],
                "version": "1.0.0"
            }
            with open(tmp.name, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Upload the file
            try:
                api.upload_file(
                    path_or_fileobj=tmp.name,
                    path_in_repo="config.json",
                    repo_id=repo_id,
                    repo_type="dataset",
                    commit_message="Add config.json to explicitly define available splits"
                )
                print("✅ Created/updated config.json")
            except Exception as e:
                print(f"⚠️ Error updating config.json: {e}")
    except Exception as e:
        print(f"⚠️ Error with config.json: {e}")
    
    # 5. Verify the final state of the repository
    print("\nVerifying final state...")
    try:
        # List all parquet files
        files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
        parquet_files = [f for f in files if f.startswith("data/") and f.endswith(".parquet")]
        
        print("Parquet files in repository:")
        for file in parquet_files:
            print(f"  - {file}")
        
        # Try loading the dataset again
        print("\nLoading dataset to verify splits...")
        dataset = load_dataset(repo_id, token=token)
        print(f"Available splits: {list(dataset.keys())}")
        
        # Print details for each split
        for split in dataset:
            print(f"Split '{split}': {len(dataset[split])} examples")
        
        if set(dataset.keys()) == set(['full_eval', 'originals_for_generating_vars', 'variations']):
            print("\n✅ VERIFICATION SUCCESSFUL: Repository has exactly the three required splits!")
        else:
            print("\n⚠️ VERIFICATION FAILED: Repository still has incorrect splits.")
            print(f"Current splits: {list(dataset.keys())}")
            print(f"Expected splits: ['full_eval', 'originals_for_generating_vars', 'variations']")
    except Exception as e:
        print(f"Error verifying repository: {e}")
    
    print("\nCleanup process completed.")

if __name__ == "__main__":
    main() 