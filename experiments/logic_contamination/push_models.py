import os
from huggingface_hub import Repository, login, create_repo

# Log in to Hugging Face Hub
key_file_path = "~/keys/master_hf_token.txt"
token = open(os.path.expanduser(key_file_path)).read().strip()
login(token=token)

# Define base path and repository name prefix
base_path = "/lfs/skampere1/0/brando9/data/runs_logic_cont/run_2024_m11_d23_t21h_55m_07s"
base_path = os.path.expanduser(base_path)
repo_prefix = "epochs-100-putnam-axiom-53"  # Prefix for all repositories
username = "brando"  # Your Hugging Face username

# Iterate through the checkpoint directories and push each as a separate repository
for dir_name in sorted(os.listdir(base_path)):
    dir_path = os.path.join(base_path, dir_name)

    # Skip non-checkpoint directories
    if not os.path.isdir(dir_path) or not dir_name.startswith("checkpoint"):
        continue

    # Create a new repository for this checkpoint
    repo_name = f"{repo_prefix}-{dir_name}"  # e.g., epochs-100-putnam-axiom-53-checkpoint-105
    repo_id = f"{username}/{repo_name}"  # e.g., brando/epochs-100-putnam-axiom-53-checkpoint-105

    # Create the repository on Hugging Face
    create_repo(
        repo_id=repo_id,
        repo_type="model",
        private=False,  # Public repository
        token=token,
        exist_ok=True,  # Avoid errors if repo already exists
    )
    print(f"Repository '{repo_id}' created or already exists.")

    # Initialize the local repository
    repo = Repository(local_dir=dir_path, clone_from=f"https://huggingface.co/{repo_id}", use_auth_token=token)

    # Create a simple README
    readme_path = os.path.join(dir_path, "README.md")
    with open(readme_path, "w") as readme_file:
        readme_file.write(f"This repository contains the model checkpoint: {dir_name} from the epochs-100-putnam-axiom-53 collection.")

    # Add and push the files to the new repository
    repo.git_add(pattern="*")
    repo.git_commit(f"Add checkpoint {dir_name}")
    repo.push_to_hub(commit_message=f"Add checkpoint {dir_name}")

    print(f"Checkpoint '{dir_name}' successfully pushed to {repo_id}.")

print("All checkpoints have been pushed.")