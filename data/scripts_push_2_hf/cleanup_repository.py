#!/usr/bin/env python3
"""
Cleanup script to remove unnecessary files and keep only essential ones
for the Putnam-AXIOM dataset push process.
"""

import os
import shutil
from pathlib import Path

def main():
    # Essential files to keep in scripts_push_2_hf directory
    essential_files = [
        'push_variations_to_putnam_axiom.py',  # Script that pushed variations
        'final_cleanup.py',                    # Final verification and cleanup
        'verify_splits_from_hf.py',            # Essential verification script
        'updated_readme_clean_splits.md',      # Current README file
        'cleanup_repository.py',               # This script
        'verify_zipfit_splits.py',             # Verification for zipfit repo
        'fix_zipfit_splits.py',                # Script to fix zipfit repo
        'README.md'                            # Directory documentation
    ]
    
    # Current directory
    scripts_dir = Path('/home/brandomiranda/putnam-axiom/data/scripts_push_2_hf')
    data_dir = Path('/home/brandomiranda/putnam-axiom/data')
    
    # Essential data files to keep in data directory
    essential_data_files = [
        'Putnam_AXIOM_Original_v3.json',       # Latest version of the dataset
        'README.md'                            # Directory documentation
    ]
    
    # Create backup directory
    backup_dir = data_dir / 'archive'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup directory for scripts
    scripts_backup_dir = backup_dir / 'scripts_push_2_hf_backup'
    os.makedirs(scripts_backup_dir, exist_ok=True)
    
    # Backup and clean up scripts_push_2_hf directory
    print("Cleaning up scripts_push_2_hf directory...")
    for item in scripts_dir.iterdir():
        if item.is_file() and item.name not in essential_files:
            print(f"Moving {item.name} to backup...")
            shutil.copy2(item, scripts_backup_dir / item.name)
            os.remove(item)
            print(f"Removed {item.name}")
    
    # Backup and clean up data directory (excluding scripts_push_2_hf and essential data files)
    print("\nCleaning up data directory...")
    for item in data_dir.iterdir():
        if item.is_file() and item.name not in essential_data_files and item.name != 'scripts_push_2_hf':
            print(f"Moving {item.name} to backup...")
            shutil.copy2(item, backup_dir / item.name)
            os.remove(item)
            print(f"Removed {item.name}")
    
    # Keep variation directories but move other directories to backup
    for item in data_dir.iterdir():
        if item.is_dir() and item.name.startswith('Putnam-AXIOM_Variations'):
            print(f"Keeping variation directory: {item.name}")
        elif item.is_dir() and item.name != 'scripts_push_2_hf' and item.name != 'archive':
            print(f"Moving directory {item.name} to backup...")
            if not (backup_dir / item.name).exists():
                shutil.copytree(item, backup_dir / item.name)
            shutil.rmtree(item)
            print(f"Removed directory {item.name}")
    
    print("\nCleanup completed!")
    print(f"Backup created at: {backup_dir}")
    print("\nRemaining essential files in scripts_push_2_hf:")
    for item in scripts_dir.iterdir():
        if item.is_file():
            print(f"  - {item.name}")
    
    print("\nRemaining essential files in data directory:")
    for item in data_dir.iterdir():
        if item.is_file():
            print(f"  - {item.name}")
        elif item.is_dir():
            print(f"  - {item.name}/ (directory)")

if __name__ == "__main__":
    main() 