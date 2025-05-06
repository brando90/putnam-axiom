#!/usr/bin/env python3

import json
import os
from pathlib import Path
import datasets
from datasets import Dataset, Features, Value, DatasetDict
from huggingface_hub import login, HfApi

def load_json_data(file_path):
    """Load JSON data from file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

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

def ensure_consistent_features(data, required_fields):
    """Ensure all items in data have the same set of fields."""
    for item in data:
        for field in required_fields:
            if field not in item:
                item[field] = ""  # Add empty string for missing text fields
                if field == "variation":
                    item[field] = 0  # Default for variation field is 0
    return data

def preprocess_data(data):
    """Preprocess data to ensure consistent fields."""
    # Define all required fields that should be present
    required_fields = [
        "id", "problem", "solution", "answer_type", "source", "type",
        "original_problem", "original_solution", "year", "variation"
    ]
    
    # Ensure all fields exist
    data = ensure_consistent_features(data, required_fields)
    
    for item in data:
        # Extract year from ID if not already present or empty
        if (not item.get("year") or item["year"] == "") and '_' in item['id']:
            year = item['id'].split('_')[0]
            item['year'] = year
        
        # Standardize the keys
        # If 'original solution' exists but 'original_solution' doesn't, copy it
        if 'original solution' in item and 'original_solution' not in item:
            item['original_solution'] = item['original solution']
            del item['original solution']
    
    return data

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
            if key in item and item[key] is not None:
                dataset_dict[key].append(item[key])
            else:
                # Handle missing keys with an appropriate default value
                dataset_dict[key].append("" if key != "variation" else 0)
    
    return Dataset.from_dict(dataset_dict, features=schema)

def push_dataset(dataset_dict, repo_id, token_path):
    """Push the dataset to Hugging Face."""
    # Read the token
    with open(token_path, 'r') as f:
        token = f.read().strip()
    
    # Login to Hugging Face
    login(token=token)
    
    # Create a datasets.DatasetDict
    hf_dataset = DatasetDict(dataset_dict)
    
    # Push to Hugging Face
    hf_dataset.push_to_hub(repo_id, private=True)
    
    print(f"Successfully pushed dataset with {len(dataset_dict)} splits to {repo_id}")
    for split_name, split_data in dataset_dict.items():
        print(f"- {split_name}: {len(split_data)} examples")

def main():
    # Paths
    putnam_original_path = "/home/brandomiranda/putnam-axiom/data/Putnam_AXIOM_Original_v3.json"
    variations_original_path = "/home/brandomiranda/putnam-axiom/data/Putnam-AXIOM_Variations_v4/original.json"
    variations_test_path = "/home/brandomiranda/putnam-axiom/data/Putnam-AXIOM_Variations_v4/test.json"
    token_path = "/home/brandomiranda/keys/master_hf_token.txt"
    repo_id = "Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
    
    # Load data for all three splits
    print("Loading data for all three splits...")
    full_eval_data = load_json_data(putnam_original_path)
    originals_for_vars_data = load_json_data(variations_original_path)
    variations_data = load_json_data(variations_test_path)
    
    # Check if data loaded successfully
    if not full_eval_data or not originals_for_vars_data or not variations_data:
        print("Error: Failed to load one or more required datasets. Aborting.")
        return
    
    print(f"Loaded {len(full_eval_data)} examples for full_eval")
    print(f"Loaded {len(originals_for_vars_data)} examples for originals_for_generating_vars")
    print(f"Loaded {len(variations_data)} examples for variations")
    
    # Preprocess data
    print("Preprocessing data...")
    full_eval_data = preprocess_data(full_eval_data)
    for item in full_eval_data:
        item['variation'] = 0  # Ensure original problems have variation=0
        
    originals_for_vars_data = preprocess_data(originals_for_vars_data)
    for item in originals_for_vars_data:
        item['variation'] = 0  # Ensure original problems have variation=0
        
    variations_data = preprocess_data(variations_data)
    for item in variations_data:
        item['variation'] = 1  # Ensure variations have variation=1
    
    # Convert to HF format
    print("Converting to HF format...")
    dataset_dict = {
        "full_eval": dataset_to_hf_format(full_eval_data),
        "originals_for_generating_vars": dataset_to_hf_format(originals_for_vars_data),
        "variations": dataset_to_hf_format(variations_data)
    }
    
    # Push to HF
    print(f"Pushing cleaned dataset to {repo_id} with 3 splits: full_eval, originals_for_generating_vars, variations")
    push_dataset(dataset_dict, repo_id, token_path)
    
    print("Done! Repository now contains only the 3 required splits.")

if __name__ == "__main__":
    main() 