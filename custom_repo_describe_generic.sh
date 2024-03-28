#!/bin/zsh

# This script allows you to describe a generic repository with a custom list of files to 
# display in full, and a full directory structure to a certain depth. 

# You can combine this with a command like the following to generate a README.md file:

# ```
#   (echo "Please write a README.md from the following, which is a custom printout of the 
#   directory structure and some specific files. Focus on quickstart and setup steps, 
#   as well as providing an overview of what the code does. Assume the user has access 
#   to the files which would be needed in the data/raw/ directory"; 
#   sh custom_repo_describe.sh) | llm
# ```

# Define an array of relative file paths to display in full
file_paths=("file1.txt" "dir_1/file2.py" "...")

# Separator
separator="===================="

echo "Full directory structure to 3 levels deep, excluding .git, .venv, all __pycache__ directories, and all .pyc files"

tree -I ".git|.venv|whatever|a_specific_file" -a -L 3 # change the number to change the nesting

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

