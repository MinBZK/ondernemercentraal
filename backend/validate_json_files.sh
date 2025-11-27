#!/bin/bash

# --- Configuration ---
# FOLDER_PATH="your_folder"  # This is now dynamic
# ---------------------

# Get the folder path from the first command-line argument
FOLDER_PATH="$1"

# Variable to track if any file is invalid
ANY_INVALID=0  # 0 means all are valid so far, 1 means at least one is invalid

# Check if a folder path was provided
if [ -z "$FOLDER_PATH" ]; then
  echo "Usage: $0 <folder_path>"
  echo "Example: $0 ."  # Validate the current directory
  echo "Example: $0 /path/to/your/json/folder"
  exit 1
fi

# Check if the provided path is a directory
if [ ! -d "$FOLDER_PATH" ]; then
  echo "Error: '$FOLDER_PATH' is not a valid directory."
  exit 1
fi

echo "Starting JSON validation in folder: $FOLDER_PATH"
# Removed the starting separator for cleaner output when no errors
# echo "-------------------------------------------------"

# Find all .json files and process them without a pipeline (to avoid subshell)
while IFS= read -r -d $'\0' file; do

  # Use python -m json.tool to validate the file
  # Redirect output and stderr to /dev/null to keep the output clean on successful validation
  if ! python -m json.tool "$file" > /dev/null 2>&1; then
    echo "Invalid JSON: $file"
    ANY_INVALID=1 # Set the flag to indicate an invalid file was found in the main shell

    # Optional: Print the error message from json.tool
    # To see the error, you need to run python -m json.tool again,
    # this time allowing stderr to be printed.
    # echo "Error details:"
    # python -m json.tool "$file" > /dev/null
  fi
  # Removed the newline echo for successful validations

done < <(find "$FOLDER_PATH" -type f -name "*.json" -print0) # Input redirection using process substitution

# Removed the ending separator for cleaner output when no errors
# echo "-------------------------------------------------"

echo "Validation complete."

# Exit with a non-zero status code if any file was invalid
exit $ANY_INVALID
