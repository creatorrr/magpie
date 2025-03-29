# Magpie Project Guide

## Commands
```
# Setup environment
poetry install
poetry shell

# Always activate virtual environment before running commands
source .venv/bin/activate  # Run from project root directory

# Run pipeline
python -m magpie.prepare_dataset  # Requires HN_USER_COOKIE env var
python -m magpie.train

# Export model to ONNX
optimum-cli export onnx --model diwank/hn-upvote-classifier --task feature-extraction --optimize O4 --device cuda --trust-remote-code hn-upvote-classifier-onnx

# Type checking
pyright

# Linting and formatting
ruff check --fix --unsafe-fixes  # Fix linting issues
ruff format                      # Format code
```

## Code Style Guidelines
- **Imports**: Standard library first, then third-party libraries
- **Formatting**: PEP 8 compliant
- **Types**: Type annotations in function signatures
- **Naming**: Snake_case for variables and functions
- **Lambda Functions**: Compact lambdas for data transformations
- **Error Handling**: Assertions for critical requirements
- **Dependencies**: ML/Data science stack (setfit, torch, datasets), web scraping (beautifulsoup4, requests)
- **Environment**: Python 3.10-3.12 compatibility, Poetry for dependency management