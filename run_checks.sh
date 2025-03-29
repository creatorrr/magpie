#!/bin/bash
# Checks script for magpie project

# Run linting and formatting
echo "Running linting and formatting..."
uv run ruff format && uv run ruff check --fix --unsafe-fixes

# Run type checking with Pyright
echo "Running type checking..."
uv run pyright

# Run type checking with Pyright
echo "Running tests..."
uv run pytest
