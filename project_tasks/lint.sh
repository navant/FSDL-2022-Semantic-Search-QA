#!/bin/bash
set -uo pipefail
set +e

FAILURE=false

# sort imports
echo "isort"
pre-commit run --all-files isort || FAILURE=true

# apply automatic formatting
echo "black"
pre-commit run --all-files black || FAILURE=true

# remove unused imports and variables
echo "autoflake"
pre-commit run --all-files autoflake || FAILURE=true

# check for python code style violations, see .flake8 for details
echo "flake8"
pre-commit run --all-files flake8 || FAILURE=true

# check for shell scripting style violations and common bugs
echo "shellcheck"
pre-commit run --all-files shellcheck || FAILURE=true

# check python types
echo "mypy"
pre-commit run --all-files mypy || FAILURE=true

if [ "$FAILURE" = true ]; then
  echo "Linting failed"
  exit 1
fi
echo "Linting passed"
exit 0