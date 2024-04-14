#!/bin/bash

# Usage: bash scripts/devcontainer_setup.sh
# Description: Installs dependencies and sets up the development environment
# Automatically called when the devcontainer is created
# Also, please keep this file idempotent, i.e., running multiple times is OK

current_user=$(whoami)
if [ "$current_user" != "vscode" ]; then
    echo "Warning: Only run this script from within the dev container (unless you know what you're doing)!"
    exit 1
fi

echo "Installing dependencies..."

parallel --tag -j2 --line-buffer ::: "pip install --user -r requirements.txt -r requirements.dev.txt" "cd client && rm -rf node_modules/ && npm install"

echo "Initializing git repository..."

git config --global --add safe.directory /workspaces/pigeon
