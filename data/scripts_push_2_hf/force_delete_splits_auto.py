#!/usr/bin/env python3

import os
import json
import time
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
    
    # List all files in the repository
    print(f"Listing all files in repository: {repo_id}")
    files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
    
    # Identify the parquet files for the splits we want to remove
    unwanted_splits = ["validation", "test", "val"]
    files_to_delete = []
    
    for file in files:
        # Delete parquet files for unwanted splits
        if any(file.startswith(f"data/{split}-") for split in unwanted_splits):
            files_to_delete.append(file)
        # Also check for any split metadata files
        elif any(f"/{split}/" in file for split in unwanted_splits):
            files_to_delete.append(file)
    
    if not files_to_delete:
        print("No unwanted split files found. Repository might already be cleaned.")
    else:
        print(f"Found {len(files_to_delete)} files to delete:")
        for file in files_to_delete:
            print(f"  - {file}")
        
        # Delete each file (auto-confirm)
        print("Deleting files automatically...")
        for file in files_to_delete:
            try:
                api.delete_file(path_in_repo=file, repo_id=repo_id, repo_type="dataset", commit_message=f"Remove unwanted split file: {file}")
                print(f"  ✓ Deleted {file}")
                # Add a short delay to avoid rate limiting
                time.sleep(0.5)
            except Exception as e:
                print(f"  ✗ Failed to delete {file}: {e}")
    
    # Now download the dataset_dict.json file to update it
    try:
        # Try to get the dataset_dict.json file
        dataset_dict_path = None
        for file in files:
            if file.endswith("dataset_dict.json"):
                dataset_dict_path = file
                break
        
        if dataset_dict_path:
            print(f"Found dataset_dict.json at {dataset_dict_path}")
            # Download the file
            try:
                local_path = hf_hub_download(repo_id=repo_id, filename=dataset_dict_path, repo_type="dataset", token=token)
                print(f"Downloaded dataset_dict.json to {local_path}")
                
                # Read the file
                with open(local_path, 'r') as f:
                    dataset_dict = json.load(f)
                
                # Remove unwanted splits
                modified = False
                for split in unwanted_splits:
                    if split in dataset_dict:
                        del dataset_dict[split]
                        modified = True
                        print(f"Removed {split} from dataset_dict.json")
                
                if modified:
                    # Write back the modified file
                    with open(local_path, 'w') as f:
                        json.dump(dataset_dict, f, indent=2)
                    
                    # Upload the modified file
                    api.upload_file(
                        path_or_fileobj=local_path,
                        path_in_repo=dataset_dict_path,
                        repo_id=repo_id,
                        repo_type="dataset",
                        commit_message="Remove unwanted splits from dataset_dict.json"
                    )
                    print(f"Updated {dataset_dict_path} in the repository")
                else:
                    print("No changes needed in dataset_dict.json")
            except Exception as e:
                print(f"Error with dataset_dict.json: {e}")
        else:
            print("Warning: Could not find dataset_dict.json")
    except Exception as e:
        print(f"Error updating dataset metadata: {e}")
    
    # Also update the dataset_info.json file if it exists
    try:
        dataset_info_path = None
        for file in files:
            if file.endswith("dataset_info.json"):
                dataset_info_path = file
                break
        
        if dataset_info_path:
            print(f"Found dataset_info.json at {dataset_info_path}")
            # Download the file
            try:
                local_path = hf_hub_download(repo_id=repo_id, filename=dataset_info_path, repo_type="dataset", token=token)
                print(f"Downloaded dataset_info.json to {local_path}")
                
                # Read the file
                with open(local_path, 'r') as f:
                    dataset_info = json.load(f)
                
                # Modify the splits information if present
                modified = False
                if 'splits' in dataset_info:
                    # Filter out unwanted splits
                    if isinstance(dataset_info['splits'], list):
                        dataset_info['splits'] = [s for s in dataset_info['splits'] if s.get('name') not in unwanted_splits]
                        modified = True
                        print(f"Removed unwanted splits from dataset_info.json")
                    elif isinstance(dataset_info['splits'], dict):
                        for split in unwanted_splits:
                            if split in dataset_info['splits']:
                                del dataset_info['splits'][split]
                                modified = True
                                print(f"Removed {split} from dataset_info.json")
                
                if modified:
                    # Write back the modified file
                    with open(local_path, 'w') as f:
                        json.dump(dataset_info, f, indent=2)
                    
                    # Upload the modified file
                    api.upload_file(
                        path_or_fileobj=local_path,
                        path_in_repo=dataset_info_path,
                        repo_id=repo_id,
                        repo_type="dataset",
                        commit_message="Remove unwanted splits from dataset_info.json"
                    )
                    print(f"Updated {dataset_info_path} in the repository")
                else:
                    print("No changes needed in dataset_info.json")
            except Exception as e:
                print(f"Error with dataset_info.json: {e}")
        else:
            print("Warning: Could not find dataset_info.json")
    except Exception as e:
        print(f"Error updating dataset info: {e}")
    
    # Finally, also update the README.md file to match our desired structure
    readme_path = "/home/brandomiranda/putnam-axiom/data/scripts_push_2_hf/updated_readme_clean_splits.md"
    if os.path.exists(readme_path):
        print("\nUpdating README to match new structure...")
        try:
            api.upload_file(
                path_or_fileobj=readme_path,
                path_in_repo="README.md",
                repo_id=repo_id,
                repo_type="dataset",
                commit_message="Update README to match cleaned splits structure"
            )
            print("✅ Successfully updated README.md")
        except Exception as e:
            print(f"❌ Failed to update README.md: {e}")
    
    print("\nDeletion of unwanted splits completed.")
    print("✅ Repository cleanup attempted. Please verify the results.")

if __name__ == "__main__":
    main() 