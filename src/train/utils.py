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
