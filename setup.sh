#!/bin/bash
# Quick setup script for magpie project

# Install dependencies using uv
echo "Installing dependencies with uv..."
uv sync

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

echo "Environment ready! You can now run:"
echo "python -m magpie.prepare_dataset"
echo "python -m magpie.train"
echo "pyright                                  # Run type checking"
echo "ruff format && ruff check --fix --unsafe-fixes # Run linting and formatting"
