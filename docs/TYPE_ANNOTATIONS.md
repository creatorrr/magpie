# Type Annotation Cheat Sheet for Magpie

This document provides a brief overview of the type annotations used in the Magpie project.

## Basic Types

```python
# Basic types
x: int = 1
y: float = 2.0
z: bool = True
name: str = "Magpie"

# Collections
numbers: list[int] = [1, 2, 3]
user: dict[str, Any] = {"name": "diwank", "id": 123}
mapping: Dict[str, int] = {"one": 1, "two": 2}
points: List[Tuple[int, int]] = [(1, 2), (3, 4)]

# Optional values
maybe_user: Optional[str] = None  # Or a string
```

## Function Annotations

```python
def get_user(user_id: int) -> Dict[str, Any]:
    """Get user by ID."""
    return {"id": user_id, "name": "User"}

def process_data(data: List[Dict[str, Any]], limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Process a list of data items."""
    return data[:limit] if limit else data
```

## Type Aliases

```python
from typing import TypeAlias, Dict, List, Any

UserData: TypeAlias = Dict[str, Any]
DataSet: TypeAlias = List[UserData]

def filter_users(dataset: DataSet, min_age: int) -> DataSet:
    return [user for user in dataset if user.get("age", 0) >= min_age]
```

## Lambda Functions

```python
from typing import Callable, Dict, Any, List

# Lambda function type annotations
pluck: Callable[[Dict[str, Any], List[str]], Dict[str, Any]] = lambda d, ks: {k: v for k, v in d.items() if k in ks}
```

## Using Type Checkers

```bash
# Run Pyright in the project
pyright

# Run just on a specific file
pyright magpie/train.py
```

## Documentation in Docstrings

```python
def process_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process a list of items.
    
    Args:
        items: A list of dictionaries with item data
        
    Returns:
        Processed items with additional fields
    """
    # Implementation...
```

## Type Checking Mode

We're using `basic` mode for type checking, which provides a good balance between strictness and practicality. See pyproject.toml for configuration details.