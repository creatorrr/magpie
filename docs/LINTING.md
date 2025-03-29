# Linting with Ruff

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

## Running Linting Checks

```bash
# Run linting checks only (no fixes)
ruff check

# Run linting checks and apply automatic fixes
ruff check --fix

# Run linting checks and apply automatic fixes (including unsafe ones)
ruff check --fix --unsafe-fixes
```

## Running Formatting

```bash
# Format code
ruff format

# Check formatting without changing files
ruff format --check
```

## Running All Checks

We provide a convenience script to run all checks:

```bash
python run_checks.py
```

## Configured Linting Rules

We've configured Ruff with the following rule sets:

- `E`: pycodestyle errors
- `F`: pyflakes (unused imports, variables, etc.)
- `I`: isort (import sorting)
- `UP`: pyupgrade (modernize Python code)
- `N`: pep8-naming (naming conventions)
- `B`: flake8-bugbear (bug detection)
- `C4`: flake8-comprehensions (list/dict comprehension optimization)
- `SIM`: flake8-simplify (code simplification)
- `PT`: flake8-pytest-style (pytest best practices)
- `RET`: flake8-return (return statement optimization)
- `PL`: pylint (general Python best practices)
- `TRY`: tryceratops (exception handling best practices)
- `RUF`: Ruff-specific rules

## Ignoring Rules

Some rules are too strict for our codebase, so we've ignored them:

- `E501`: Line too long (handled by formatter)
- `PLR0913`: Too many arguments to function call
- `PLR0915`: Too many statements

## Editor Integration

For VSCode users, install the Ruff extension for real-time linting and formatting.

For PyCharm users, you can configure an External Tool to run Ruff.

## CI Integration

In a CI/CD pipeline, use the following commands:

```bash
# Linting check (fails if issues are found)
ruff check

# Format check (fails if formatting is needed)
ruff format --check
```