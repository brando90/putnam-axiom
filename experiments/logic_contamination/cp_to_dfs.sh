#!/bin/bash

# Define source and destination directories
SOURCE_DIR="/lfs/skampere1/0/brando9/data/runs_logic_cont"
DESTINATION_DIR="/dfs/scratch0/brando9/data/runs_logic_cont"
SOURCE_DIR="/lfs/skampere1/0/brando9/data/runs_logic_cont/run_2024_m11_d23_t21h_55m_07s"
DESTINATION_DIR="/dfs/scratch0/brando9/data/runs_logic_cont/run_2024_m11_d23_t21h_55m_07s"

# Create the target directory on DFS
mkdir -p "$DESTINATION_DIR"

# Copy files recursively while preserving attributes, skipping existing files
echo "Starting copy from $SOURCE_DIR to $DESTINATION_DIR..."
cp -aru "$SOURCE_DIR/" "$DESTINATION_DIR/"

# Verify the copy
echo "Copy completed. Verifying the copied files..."
diff -rq "$SOURCE_DIR" "$DESTINATION_DIR"

# Final status message
if [ $? -eq 0 ]; then
    echo "All files successfully copied and verified."
else
    echo "Some files did not copy correctly. Please check the differences above."
fi