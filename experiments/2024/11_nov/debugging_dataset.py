from datasets import load_dataset

# Load the dataset split causing the issue
dataset_name = "Putnam-AXIOM/putnam-axiom-dataset"
split_name = "func_variations_265_10_30_2024"

# Load the dataset
print(f"Loading dataset: {dataset_name}, split: {split_name}")
dataset = load_dataset(dataset_name, split=split_name)

# Inspect the specific row causing the issue
index_to_inspect = 216

try:
    row = dataset[index_to_inspect]
    print(f"\nRow {index_to_inspect} contents:")
    for key, value in row.items():
        print(f"{key}: {value}")
except IndexError:
    print(f"Row {index_to_inspect} is out of bounds. Dataset has {len(dataset)} rows.")

# Check for potential issues in the 'solution' field
if "solution" in row:
    print("\nSolution field inspection:")
    if row["solution"] is None:
        print("The 'solution' field is None.")
    elif not row["solution"].strip():
        print("The 'solution' field is an empty string.")
    else:
        print(f"The 'solution' field looks valid: {row['solution']}")
else:
    print("\nThe 'solution' field is missing in the dataset.")
