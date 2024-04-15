
#!/bin/bash

# Usage: bash scripts/ci_cd.sh
# Description: Run all ci/cd tests locally.
# These are the same tests that run on GitHub when you push code.

cd "/workspaces/pigeon"

echo "Running ci/cd checks..."
echo "(1) pre-commit checks..."

pre-commit run --all-files

echo "(2) Run Pyright..."

npx pyright

echo "(3) Run Pytests..."

pytest -v -s

echo "Tests complete."
