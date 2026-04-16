#!/bin/bash

if ! command -v terraform-docs &> /dev/null; then
  echo "Error: 'terraform-docs' is not installed or not in your PATH."
  echo "Please install it with 'sudo snap install terraform-docs' before running this script."
  exit 1
fi

TERRAFORM_DIR=$(pwd)/../terraform

echo "Starting terraform-docs update from $TERRAFORM_DIR"

find "$TERRAFORM_DIR" -maxdepth 2 -mindepth 2 -type d | while read -r MODULE_DIR; do
  echo "Processing $MODULE_DIR"
  if [ -d "$MODULE_DIR" ]; then
    cd "$MODULE_DIR"

    if [ -f "README.md" ]; then
      terraform-docs markdown table . \
          --output-mode inject \
          --output-file README.md \
          --indent 3
    else
      echo "Skipping $MODULE_DIR"
    fi
  fi
done

echo "Finished updating documentation."
