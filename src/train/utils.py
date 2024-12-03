# ref: https://chatgpt.com/c/674784d0-f350-8001-8a5f-35c54ab641ac
import os
import subprocess

def copy_to_dfs(source_dir: str):
    """
    Executes the cp_to_dfs.sh script with the provided source directory.
    """
    # Expand user in the source directory
    source_dir = os.path.expanduser(source_dir)
    
    # Path to the Bash script
    script_path = os.path.expanduser("~/putnam-axiom/experiments/logic_contamination/cp_to_dfs.sh")

    # Run the Bash script with the source directory as an argument
    try:
        subprocess.run([script_path, source_dir], check=True)
        print(f"Successfully executed {script_path} with source_dir={source_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_path}: {e}")
    except FileNotFoundError:
        print(f"The script {script_path} was not found. Please ensure it exists and is executable.")

def seed_everything(seed: int = 0, hf_timeout: float = 5):
    """ Seed all necessary libraries to ensure reproducible results. """
    import random
    import numpy as np
    import torch
    from transformers import set_seed as hf_set_seed
    print(f'{seed=}')
    random.seed(seed)
    np.random.seed(seed)
    # Seed PyTorch (both CPU and CUDA if available)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)  # If you use multi-GPU.
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    # Seed HF
    if torch.cuda.is_available():
        hf_set_seed(seed) # this gives a halting issue, so we are going to just not seed it
    else:
        print('Warning: HF is currently only dermisitic/seeded in gpu')
    # try to seed vllm
    try:
        from vllm import set_seed as vllm_set_seed
        vllm_set_seed(seed)
    except ImportError:
        print("vLLM not installed or vllm set seed has a bug, skipping vLLM seed setting.")
