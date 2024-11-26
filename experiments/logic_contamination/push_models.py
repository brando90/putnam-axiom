import os
from huggingface_hub import Repository, login

# Log in to Hugging Face Hub
key_file_path = "~/keys/master_hf_token.txt"
token = open(os.path.expanduser(key_file_path)).read().strip()
login(token=token)

# Define base path and repository name prefix
base_path = "~/data/runs_logic_cont/run_2024_m11_d20_t21h_22m_22s"
base_path = os.path.expanduser(base_path)
repo_prefix = "logic-contamination"  # Prefix for all repositories on Hugging Face

# Iterate through the checkpoint directories and push to the repository
for dir_name in sorted(os.listdir(base_path)):
    dir_path = os.path.join(base_path, dir_name)

    # Skip if it's not a directory or doesn't start with 'checkpoint'
    if not os.path.isdir(dir_path) or not dir_name.startswith("checkpoint"):
        continue

    # Define repository name with prefix
    repo_name = f"{repo_prefix}-{dir_name}"  # e.g., logic-contamination-checkpoint-105
    print(f"Processing {dir_name} as {repo_name}...")

    # Check if the directory is already a Git repository
    if not os.path.exists(os.path.join(dir_path, ".git")):
        print(f"Initializing Git repository in {dir_path}...")
        os.system(f"cd {dir_path} && git init && git remote add origin https://huggingface.co/{repo_name}")

    # Initialize Repository object and push to Hugging Face Hub
    repo = Repository(local_dir=dir_path, use_auth_token=token)
    repo.git_pull()  # Ensure the repository is up-to-date
    repo.push_to_hub(commit_message=f"Upload {dir_name}")

    print(f"Uploaded {repo_name} successfully.")

print("All checkpoints processed.")
