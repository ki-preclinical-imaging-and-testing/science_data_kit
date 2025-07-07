# Module Standards for Science Data Kit

This document outlines the coding standards and best practices for creating and modifying modules in the Science Data Kit. It provides guidelines for module structure, docstring formatting, type hints, error handling, and other important aspects of code organization.

## Module Template

A standardized module template is available at `science_data_kit/core/templates/module_template.py`. This template should be used as a starting point for creating new modules. It includes examples of proper docstring formatting, import organization, class and function structure, type hints, and error handling patterns.

To use the template:
1. Copy the template to create a new module
2. Replace placeholder content with actual implementation
3. Follow the docstring format for all classes and functions
4. Use type hints for all parameters and return values
5. Follow the error handling patterns demonstrated

## Module Structure

Each module should follow this general structure:

1. **Module Docstring**: A comprehensive description of the module's purpose and usage
2. **Imports**: Organized into sections (standard library, third-party, local)
3. **Constants and Type Variables**: Any module-level constants or type variables
4. **Exception Classes**: Custom exception classes for the module
5. **Classes**: Class definitions with proper docstrings
6. **Functions**: Function definitions with proper docstrings
7. **Main Block**: Optional block for script execution

## Import Organization

Imports should be organized into three sections, with each section sorted alphabetically:

```python
# Standard library imports
import logging
import os
import time
from typing import Dict, List, Optional

# Third-party imports
import numpy as np
import pandas as pd

# Local application imports
from science_data_kit.core import some_module
from science_data_kit.core.utils import another_module
```

## Docstring Format

All modules, classes, and functions should have docstrings that follow this format:

### Module Docstring

```python
"""
Module name and brief description.

Detailed description of the module's purpose, functionality, and usage.
Include any important information about the module's behavior.

Examples:
    ```python
    from science_data_kit.core.utils import module_name

    # Use the module
    result = module_name.example_function("example input")
    ```
"""
```

### Class Docstring

```python
class ExampleClass:
    """
    Brief description of the class.

    Detailed description of the class's purpose, functionality, and usage.
    Include any important information about the class's behavior.

    Attributes:
        attribute_name (type): Description of the attribute.
        another_attribute (type): Description of another attribute.
    """
```

### Method/Function Docstring

```python
def example_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    Brief description of the function.

    Detailed description of the function's purpose, functionality, and usage.
    Include any important information about the function's behavior.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter. Defaults to None.
                Additional details about the parameter can be included
                in indented continuation lines.

    Returns:
        Description of the return value.

    Raises:
        ExceptionType: Description of when this exception is raised.
        AnotherExceptionType: Description of when this exception is raised.

    Examples:
        >>> example_function("test")
        {'result': 'test'}
    """
```

## Type Hints

Type hints should be used for all function parameters and return values. Use the `typing` module for complex types:

```python
from typing import Dict, List, Optional, Tuple, TypeVar, Union, Any, Callable

def example_function(
    param1: str,
    param2: int,
    param3: Optional[List[str]] = None,
    *args: Any,
    **kwargs: Any
) -> Dict[str, Any]:
    # Function implementation
```

For generic types, use TypeVar:

```python
T = TypeVar('T')
R = TypeVar('R')

def process_item(item: T) -> R:
    # Function implementation
```

## Error Handling

Error handling should follow these patterns:

1. **Custom Exceptions**: Define custom exception classes for module-specific errors
2. **Input Validation**: Validate inputs at the beginning of functions
3. **Contextual Errors**: Provide context when re-raising exceptions
4. **Logging**: Log errors at appropriate levels

Example:

```python
try:
    # Operation that might fail
    result = process_data(input_data)
except SomeError as e:
    logger.error(f"Failed to process data: {str(e)}")
    raise CustomError(f"Could not process data: {input_data}") from e
```

## Logging

Use the standard logging module for all logging:

```python
import logging

logger = logging.getLogger(__name__)

def example_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
```

## Private Methods and Functions

Private methods and functions (those not intended for external use) should be prefixed with an underscore:

```python
def _private_helper_function():
    # Implementation
```

## Constants

Constants should be defined at the module level and named in ALL_CAPS:

```python
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
```

## Conclusion

Following these standards will ensure consistency across the Science Data Kit codebase, making it more maintainable, readable, and robust. The module template provides a practical example of these standards in action and should be used as a reference when creating new modules or refactoring existing ones.
