#!/usr/bin/env python3
"""
Fix the zipfit/Putnam-AXIOM-for-zip-fit-splits repository to have the correct splits:
- train: 150 examples
- validation: 150 examples
- test: 222 examples
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
import numpy as np
from datasets import load_dataset, Dataset, DatasetDict
from huggingface_hub import HfApi

def main():
    # Constants
    source_repo = "Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
    target_repo = "zipfit/Putnam-AXIOM-for-zip-fit-splits"
    temp_dir = tempfile.mkdtemp()
    
    try:
        print(f"Loading source dataset from {source_repo}...")
        source_dataset = load_dataset(source_repo)
        
        # We'll use the full_eval split from the source dataset
        full_dataset = source_dataset["full_eval"]
        total_examples = len(full_dataset)
        print(f"Loaded {total_examples} examples from source dataset.")
        
        if total_examples != 522:
            raise ValueError(f"Expected 522 examples in the full_eval split, but got {total_examples}")
        
        # Set the random seed for reproducibility
        np.random.seed(42)
        
        # Shuffle the indices
        indices = np.random.permutation(total_examples)
        
        # Split into train, validation, and test
        train_indices = indices[:150].tolist()
        validation_indices = indices[150:300].tolist()
        test_indices = indices[300:].tolist()
        
        # Create the splits
        train_dataset = full_dataset.select(train_indices)
        validation_dataset = full_dataset.select(validation_indices)
        test_dataset = full_dataset.select(test_indices)
        
        print(f"Created splits:")
        print(f"  - train: {len(train_dataset)} examples")
        print(f"  - validation: {len(validation_dataset)} examples")
        print(f"  - test: {len(test_dataset)} examples")
        
        # Create dataset dictionary
        dataset_dict = DatasetDict({
            "train": train_dataset,
            "validation": validation_dataset,
            "test": test_dataset
        })
        
        # Push to HF
        print(f"Pushing dataset to {target_repo}...")
        
        # Create the README.md file
        readme_path = os.path.join(temp_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write("""---
dataset_info:
  features:
  - name: year
    dtype: string
  - name: id
    dtype: string
  - name: problem
    dtype: string
  - name: solution
    dtype: string
  - name: answer_type
    dtype: string
  - name: source
    dtype: string
  - name: type
    dtype: string
  - name: original_problem
    dtype: string
  - name: original_solution
    dtype: string
  - name: variation
    dtype: int64
  splits:
  - name: train
    num_examples: 150
  - name: validation
    num_examples: 150
  - name: test
    num_examples: 222
  download_size: 560892
  dataset_size: 1184885
configs:
- config_name: default
---

# Putnam-AXIOM Splits for ZIP-FIT

This repository contains the train, validation, and test splits of the Putnam-AXIOM dataset specifically for use with the ZIP-FIT methodology research. The dataset is split as follows:

- **train**: 150 examples
- **validation**: 150 examples
- **test**: 222 examples

These splits are derived from the original 522 Putnam problems found in the main Putnam-AXIOM repository.

## Main Repository

The full dataset with original problems and variations is available in the main repository:
[Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522](https://huggingface.co/datasets/Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522)

## Usage

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("zipfit/Putnam-AXIOM-for-zip-fit-splits")

# Access each split
train_data = dataset["train"]
validation_data = dataset["validation"]
test_data = dataset["test"]
```

## Citation

If you use this dataset, please cite it as follows:

```bibtex
@article{putnam_axiom2025,
  title={Putnam-AXIOM: A Functional and Static Benchmark for Measuring Higher Level Mathematical Reasoning},
  author={Aryan Gulati and Brando Miranda and Eric Chen and Emily Xia and Kai Fronsdal and Bruno de Moraes Dumont and Sanmi Koyejo},
  journal={39th International Conference on Machine Learning (ICML 2025)},
  year={2025},
  note={Preprint available at: https://openreview.net/pdf?id=YXnwlZe0yf, ICML paper: https://openreview.net/forum?id=kqj2Cn3Sxr}
}

@article{miranda2024zipfit,
  title={ZIP-FIT: Embedding-Free Data Selection via Compression-Based Alignment},
  year = {2024},
  journal = {arXiv preprint arXiv:2410.18194},
}
```

## ZIP-FIT Project

For more information on the ZIP-FIT framework, including code and documentation, visit the [ZIP-FIT GitHub repository](https://github.com/brando90/evals-for-autoformalization).

## License

This dataset is licensed under the Apache 2.0.
""")
        
        print("Created README.md file.")
        
        # Upload README to HF
        api = HfApi()
        api.upload_file(
            path_or_fileobj=readme_path,
            path_in_repo="README.md",
            repo_id=target_repo,
            repo_type="dataset"
        )
        
        print("Successfully uploaded README.md to Hugging Face.")
        
        print("Pushing datasets to Hugging Face...")
        
        # Push the datasets
        dataset_dict.push_to_hub(
            target_repo,
            private=False
        )
        
        print("Successfully pushed datasets to Hugging Face.")
        
        # Create config.json explicitly
        config_path = os.path.join(temp_dir, "config.json")
        config = {
            "version": "1.0.0",
            "description": "Putnam-AXIOM Splits for ZIP-FIT",
            "citation": "@article{putnam_axiom2025,\n  title={Putnam-AXIOM: A Functional and Static Benchmark for Measuring Higher Level Mathematical Reasoning},\n  author={Aryan Gulati and Brando Miranda and Eric Chen and Emily Xia and Kai Fronsdal and Bruno de Moraes Dumont and Sanmi Koyejo},\n  journal={39th International Conference on Machine Learning (ICML 2025)},\n  year={2025},\n  note={Preprint available at: https://openreview.net/pdf?id=YXnwlZe0yf, ICML paper: https://openreview.net/forum?id=kqj2Cn3Sxr}\n}\n\n@article{miranda2024zipfit,\n  title={ZIP-FIT: Embedding-Free Data Selection via Compression-Based Alignment},\n  year = {2024},\n  journal = {arXiv preprint arXiv:2410.18194},\n}",
            "license": "apache-2.0",
            "splits": {
                "train": {"num_examples": 150},
                "validation": {"num_examples": 150},
                "test": {"num_examples": 222}
            }
        }
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        # Upload config.json
        api.upload_file(
            path_or_fileobj=config_path,
            path_in_repo="config.json",
            repo_id=target_repo,
            repo_type="dataset"
        )
        
        print("Successfully uploaded config.json to Hugging Face.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        shutil.rmtree(temp_dir)
        print("Temporary directory cleaned up.")

if __name__ == "__main__":
    main() 