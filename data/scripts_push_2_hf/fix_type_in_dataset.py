import json
import os
from datasets import load_dataset, Dataset
from huggingface_hub import login

# Define paths
input_path = "~/putnam-axiom/data/Putnam_AXIOM_Original.json"
output_path = "~/putnam-axiom/data/Putnam_AXIOM_Original_v2.json"

# Load the JSON data
with open(input_path, "r") as f:
    data = json.load(f)

# Convert `type` field to a single string by joining elements with space
for entry in data:
    if isinstance(entry.get("type"), list):
        entry["type"] = " ".join(entry["type"])

# Save the modified data to a new file
with open(output_path, "w") as f:
    json.dump(data, f, indent=2)

print(f"Modified dataset saved to {output_path}")