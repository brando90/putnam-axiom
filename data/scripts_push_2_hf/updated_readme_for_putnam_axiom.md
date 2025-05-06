---
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
  - name: full_eval
    num_examples: 522
  - name: originals_for_generating_vars
    num_examples: 67
  - name: variations
    num_examples: 459
  download_size: 560892
  dataset_size: 1184885
configs:
- config_name: default
extra_gated_prompt: 'By requesting access to this dataset, you agree to cite the following
  works in any publications or projects that utilize this data:

  - Putnam-AXIOM dataset: @article{putnam_axiom2025, title={Putnam-AXIOM: A Functional
  and Static Benchmark for Measuring Higher Level Mathematical Reasoning}, author={Aryan
  Gulati and Brando Miranda and Eric Chen and Emily Xia and Kai Fronsdal and Bruno
  de Moraes Dumont and Sanmi Koyejo}, journal={39th International Conference on Machine Learning (ICML 2025)}, year={2025}, 
  note={Preprint available at: https://openreview.net/pdf?id=YXnwlZe0yf}} '
---

# Putnam AXIOM Dataset (ICML 2025 Version)

**Note: for questions, feedback, bugs, etc. please [open a Huggingface discussion here](https://huggingface.co/datasets/Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522/discussions).**

## Dataset Summary

The [**Putnam AXIOM**](https://openreview.net/pdf?id=YXnwlZe0yf) dataset is designed for evaluating large language models (LLMs) on advanced mathematical reasoning skills. It is based on challenging problems from the Putnam Mathematical Competition. This version contains 522 original problems prepared for the ICML 2025 submission.

The dataset now includes:
- **Full Evaluation Set (522 problems)**: Complete set of original problems
- **Originals for Generating Variations (67 problems)**: A subset of problems used to create variations
- **Variations (459 problems)**: Variations generated from the original problems

Each problem includes:
- Problem statement
- Solution
- Original problem (where applicable)
- Answer type (e.g., numerical, proof)
- Source and type of problem (e.g., Algebra, Calculus, Geometry)
- Year (extracted from problem ID)
- Variation flag (0 for original problems, 1 for variations)

## Note About Splits

For experiments with the Putnam AXIOM dataset in different research contexts, specialized splits are available in separate repositories:
- [ZIP-FIT experiments splits](https://huggingface.co/datasets/zipfit/Putnam-AXIOM-for-zip-fit-splits) - Contains validation/test splits used for ZIP-FIT methodology research

## Supported Tasks and Leaderboards

- **Mathematical Reasoning**: Evaluate mathematical reasoning and problem-solving skills.
- **Language Model Benchmarking**: Use this dataset to benchmark performance of language models on advanced mathematical questions.

## Languages

The dataset is presented in **English**.

## Dataset Structure

### Data Fields

- **year**: The year of the competition (extracted from the problem ID).
- **id**: Unique identifier for each problem.
- **problem**: The problem statement.
- **solution**: The solution or explanation for the problem.
- **answer_type**: The expected type of answer (e.g., numerical, proof).
- **source**: The origin of the problem (Putnam).
- **type**: A description of the problem's mathematical topic (e.g., "Algebra Geometry").
- **original_problem**: Original form of the problem, where applicable.
- **original_solution**: Original solution to the problem, where applicable.
- **variation**: Flag for variations (0 for original problems, 1 for generated variations).

### Splits

| Split                        | Description                                    | Number of Problems |
|------------------------------|------------------------------------------------|--------------------|
| `full_eval`                  | Complete set of 522 original problems          | 522                |
| `originals_for_generating_vars` | Original problems used to create variations  | 67                 |
| `variations`                 | Generated variations of the original problems   | 459                |

### Variations

The `variations` split contains problems that were algorithmically generated as variations of problems in the `originals_for_generating_vars` split. These variations maintain the core mathematical concepts of the original problems but present them with different contexts, numbers, or phrasings. The variation field is set to 1 for these problems to distinguish them from the original problems.

## Dataset Usage

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522")

# Access each split
full_eval = dataset["full_eval"]  # Original problems
originals = dataset["originals_for_generating_vars"]  # Original problems used for variations
variations = dataset["variations"]  # Generated variations

# Filter for original problems only (variation = 0)
original_problems = [p for p in full_eval if p["variation"] == 0]

# Filter for variation problems (variation = 1)
variation_problems = [p for p in variations if p["variation"] == 1]

# Example usage: print the first original problem
print(full_eval[0])
```
    
## Citation
If you use this dataset, please cite it as follows:

```bibtex
@article{putnam_axiom2025,
  title={Putnam-AXIOM: A Functional and Static Benchmark for Measuring Higher Level Mathematical Reasoning},
  author={Aryan Gulati and Brando Miranda and Eric Chen and Emily Xia and Kai Fronsdal and Bruno de Moraes Dumont and Sanmi Koyejo},
  journal={39th International Conference on Machine Learning (ICML 2025)},
  year={2025},
  note={Preprint available at: https://openreview.net/pdf?id=YXnwlZe0yf}
}
```

## License

This dataset is licensed under the Apache 2.0.

Last updated: May 22, 2024 