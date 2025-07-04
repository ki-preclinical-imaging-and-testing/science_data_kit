# Science Data Kit Code Standards

This document outlines the coding standards and linting configuration for the Science Data Kit project.

## Linting with Flake8

The Science Data Kit uses [Flake8](https://flake8.pycqa.org/) for code linting to ensure consistent code quality and style. The configuration is defined in the `.flake8` file at the root of the project.

### Configuration

The Flake8 configuration includes:

- **Maximum line length**: 100 characters
- **Excluded directories**: `.git`, `__pycache__`, `build`, `dist`
- **Ignored rules**:
  - `E203`: Whitespace before ':'
  - `W503`: Line break before binary operator
- **Per-file ignores**:
  - `__init__.py`: `F401` (imported but unused), `F403` (unable to detect undefined names)
  - `test_*.py`: `E501` (line too long)
- **Selected checks**: `C`, `E`, `F`, `W`, `B`, `B950` (style, errors, warnings, bugs)

### Running Flake8

To run Flake8 manually:

```bash
flake8 science_data_kit/
```

## Pre-commit Hooks

The project uses [pre-commit](https://pre-commit.com/) to run checks automatically before each commit. The configuration is defined in the `.pre-commit-config.yaml` file.

### Installed Hooks

- **pre-commit-hooks**:
  - `trailing-whitespace`: Removes trailing whitespace
  - `end-of-file-fixer`: Ensures files end with a newline
  - `check-yaml`: Validates YAML files
  - `check-added-large-files`: Prevents large files from being committed

- **flake8**:
  - Runs Flake8 with docstring checks

- **isort**:
  - Sorts imports according to PEP8 with Black compatibility

- **mypy**:
  - Performs static type checking

### Installation and Usage

To install pre-commit hooks:

1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Install the git hooks:
   ```bash
   pre-commit install
   ```

3. The hooks will now run automatically on every commit. To run them manually:
   ```bash
   pre-commit run --all-files
   ```

## Type Hints

The Science Data Kit uses type hints throughout the codebase to improve code readability, enable better IDE support, and catch type-related errors early.

### Guidelines for Type Hints

- Use type hints for all function parameters and return values
- Use the `typing` module for complex types (e.g., `List`, `Dict`, `Optional`)
- Use `Optional[Type]` instead of `Type | None` for compatibility
- Use type variables (`TypeVar`) for generic functions
- Document type variables in docstrings

### Example

```python
from typing import Dict, List, Optional, TypeVar

T = TypeVar('T')  # Generic type variable

def process_data(items: List[T], config: Optional[Dict[str, str]] = None) -> Dict[str, T]:
    """
    Process a list of items according to the configuration.
    
    Args:
        items: List of items to process
        config: Optional configuration dictionary
        
    Returns:
        Dictionary mapping item identifiers to processed items
    """
    result = {}
    # Implementation
    return result
```

## Docstrings

The Science Data Kit uses Google-style docstrings for all modules, classes, and functions.

### Docstring Format

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """
    Short description of the function.
    
    Longer description if needed, explaining the purpose and behavior
    of the function in more detail.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter. Defaults to 0.
            Additional details can be included in indented continuation lines.
    
    Returns:
        Description of the return value
        
    Raises:
        ValueError: Description of when this error is raised
        TypeError: Description of when this error is raised
        
    Examples:
        >>> example_function("test", 1)
        True
    """
    # Implementation
    return True
```

## Import Organization

Imports should be organized in the following order, with a blank line between each group:

1. Standard library imports
2. Third-party imports
3. Local application imports

Within each group, imports should be sorted alphabetically.

### Example

```python
# Standard library imports
import os
import sys
from typing import Dict, List

# Third-party imports
import numpy as np
import pandas as pd

# Local application imports
from science_data_kit.core import utils
from science_data_kit.core.db import db_manager
```

## Conclusion

Following these code standards ensures consistency across the Science Data Kit codebase and makes it easier for contributors to understand and maintain the code. The automated linting and type checking tools help catch issues early and maintain code quality.