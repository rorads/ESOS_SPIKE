#!/bin/zsh

# Define an array of relative file paths
file_paths=(".gitignore" "esos_spike/parse.py" ".env" "docs/method.md")

# Separator
separator="===================="

echo "Full directory structure to 3 levels deep, excluding .git, .venv, all __pycache__ directories, and all .pyc files"

tree -I ".git|.venv|**/__pycache__|*.pyc|.doc_cache" -a -L 3
#tree -a -L 3


echo "$separator"
echo "File contents for the following files: ${file_paths[@]}"

# Iterate over each file path in the array
for file in "${file_paths[@]}"; do
  # Check if the file exists
  if [[ -e "$file" ]]; then
    echo "$separator"
    # Print the full path
    echo ">>>> PATH >>>> ./$file"
    echo "$separator"
    # Print the file content
    cat "$file"
    # Print a new line after the content for better readability
    echo
  else
    # Print a warning if the file doesn't exist
    echo "Warning: '$file' does not exist."
  fi

done

