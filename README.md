magpie
======

A simple model to predict what stories I'd like on HN so I don't doomscroll it.

Uses LiqFit framework with the `knowledgator/comprehend_it-base` model as base, featuring focal loss for better handling of imbalanced data. Training on the last 24 months of stories with a sample size of 1000.

Code is experimental but I believe anyone can run it easily.

```
# Install dependencies with uv
uv sync

# Activate virtual environment
source .venv/bin/activate

# Run the pipeline
python -m magpie.prepare_dataset
python -m magpie.train

# Run type checking
pyright

# Run linting and formatting
ruff check --fix --unsafe-fixes && ruff format
```

To convert to ONNX:
`optimum-cli export onnx --model diwank/hn-upvote-classifier --task feature-extraction --optimize O4 --device cuda --trust-remote-code hn-upvote-classifier-onnx`
