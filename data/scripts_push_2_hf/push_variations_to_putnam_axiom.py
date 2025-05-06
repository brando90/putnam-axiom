#!/usr/bin/env python3

import json
import os
from pathlib import Path
import datasets
from datasets import Dataset, Features, Value
from huggingface_hub import login, HfApi
import copy

def load_json_data(file_path):
    """Load JSON data from file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def ensure_consistent_features(data, required_fields):
    """Ensure all items in data have the same set of fields."""
    for item in data:
        for field in required_fields:
            if field not in item:
                item[field] = ""  # Add empty string for missing text fields
                if field == "variation":
                    item[field] = 0  # Default for variation field is 0
    return data

def preprocess_originals(data):
    """Preprocess the original problems that were used to generate variations."""
    # Define all required fields that should be present
    required_fields = [
        "id", "problem", "solution", "answer_type", "source", "type",
        "original_problem", "original_solution", "year", "variation"
    ]
    
    # Ensure all fields exist
    data = ensure_consistent_features(data, required_fields)
    
    for item in data:
        # Extract year from ID if not already present
        if not item["year"] and '_' in item['id']:
            year = item['id'].split('_')[0]
            item['year'] = year
        
        # Set variation field to 0 for originals
        item['variation'] = 0
        
        # Standardize the keys
        # If 'original solution' exists but 'original_solution' doesn't, copy it
        if 'original solution' in item and 'original_solution' not in item:
            item['original_solution'] = item['original solution']
            del item['original solution']
    
    return data

def preprocess_variations(data):
    """Preprocess the variation problems."""
    # Define all required fields that should be present
    required_fields = [
        "id", "problem", "solution", "answer_type", "source", "type",
        "original_problem", "original_solution", "year", "variation"
    ]
    
    # Ensure all fields exist
    data = ensure_consistent_features(data, required_fields)
    
    for item in data:
        # Extract year from ID if not already present
        if not item["year"] and '_' in item['id']:
            year = item['id'].split('_')[0]
            item['year'] = year
        
        # Set variation field to 1 for variations
        item['variation'] = 1
        
        # Standardize the keys
        # If 'original solution' exists but 'original_solution' doesn't, copy it
        if 'original solution' in item and 'original_solution' not in item:
            item['original_solution'] = item['original solution']
            del item['original solution']
    
    return data

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

def push_full_dataset(splits, repo_id, token_path):
    """Push the complete dataset to Hugging Face, replacing everything."""
    # Read the token
    with open(token_path, 'r') as f:
        token = f.read().strip()
    
    # Login to Hugging Face
    login(token=token)
    
    # Create a DatasetDict with consistent features
    dataset_dict = {}
    features = get_dataset_schema()
    
    for split_name, split_data in splits.items():
        dataset_dict[split_name] = dataset_to_hf_format(split_data)
    
    # Create a datasets.DatasetDict from the dictionary
    hf_dataset = datasets.DatasetDict(dataset_dict)
    
    # Push to Hugging Face
    hf_dataset.push_to_hub(repo_id, private=True)
    
    print(f"Successfully pushed complete dataset with {len(splits)} splits to {repo_id}")
    for split_name, split_data in splits.items():
        print(f"- {split_name}: {len(split_data)} examples")

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
            result[split_name] = []
            for i in range(len(existing_dataset[split_name])):
                item = dict(existing_dataset[split_name][i])
                result[split_name].append(item)
            
            print(f"Loaded {len(result[split_name])} examples from {split_name} split")
        
        return result
    except Exception as e:
        print(f"Could not load existing dataset: {e}")
        return {}

def main():
    # Paths
    originals_path = "/home/brandomiranda/putnam-axiom/data/Putnam-AXIOM_Variations_v4/original.json"
    variations_path = "/home/brandomiranda/putnam-axiom/data/Putnam-AXIOM_Variations_v4/test.json"
    token_path = "/home/brandomiranda/keys/master_hf_token.txt"
    repo_id = "Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
    
    # Load the original problems data
    print(f"Loading original problems from {originals_path}...")
    originals_data = load_json_data(originals_path)
    print(f"Loaded {len(originals_data)} original examples")
    
    # Load the variations data
    print(f"Loading variations from {variations_path}...")
    variations_data = load_json_data(variations_path)
    print(f"Loaded {len(variations_data)} variation examples")
    
    # Load existing data from HF repository
    existing_data = load_existing_data(repo_id, token_path)
    
    # Preprocess data
    print("Preprocessing original problems...")
    originals_data = preprocess_originals(originals_data)
    
    print("Preprocessing variations...")
    variations_data = preprocess_variations(variations_data)
    
    # Create a complete dataset dictionary
    complete_dataset = {}
    
    # Add full_eval split if it exists in the existing data
    if 'full_eval' in existing_data:
        complete_dataset['full_eval'] = existing_data['full_eval']
    
    # Add the new splits
    complete_dataset['originals_for_generating_vars'] = originals_data
    complete_dataset['variations'] = variations_data
    
    # Push the complete dataset
    print(f"Pushing complete dataset to Hugging Face repository: {repo_id}")
    push_full_dataset(complete_dataset, repo_id, token_path)
    
    print("Done!")

if __name__ == "__main__":
    main() 