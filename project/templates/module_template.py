"""
Module Template for Science Data Kit

This template provides a standardized structure for modules in the Science Data Kit.
It includes examples of proper docstring formatting, import organization, class and
function structure, type hints, and error handling patterns.

Usage:
    1. Copy this template to create a new module
    2. Replace placeholder content with actual implementation
    3. Follow the docstring format for all classes and functions
    4. Use type hints for all parameters and return values
    5. Follow the error handling patterns demonstrated

Examples:
    ```python
    from science_data_kit.core.utils import module_name
    
    # Use the module
    result = module_name.example_function("example input")
    ```
"""

# Standard library imports (alphabetical order)
import logging
import os
import time
from typing import Dict, List, Optional, Tuple, TypeVar, Union, Any, Callable, Generic

# Third-party imports (alphabetical order)
# import numpy as np
# import pandas as pd

# Local application imports (alphabetical order)
# from science_data_kit.core import some_module
# from science_data_kit.core.utils import another_module

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')


class ExampleError(Exception):
    """Base exception for this module."""
    pass


class SpecificError(ExampleError):
    """Raised when a specific error condition occurs."""
    pass


class ExampleClass:
    """
    Example class demonstrating proper structure and documentation.
    
    This class provides a template for creating new classes in the Science Data Kit.
    It demonstrates proper docstring formatting, method structure, type hints,
    and error handling patterns.
    
    Attributes:
        attribute_name (type): Description of the attribute.
        another_attribute (type): Description of another attribute.
    """
    
    def __init__(self, param1: str, param2: Optional[int] = None):
        """
        Initialize the ExampleClass.
        
        Args:
            param1: Description of the first parameter.
            param2: Description of the second parameter. Defaults to None.
                    Additional details about the parameter can be included
                    in indented continuation lines.
        
        Raises:
            ValueError: If param1 is empty.
        """
        if not param1:
            raise ValueError("param1 cannot be empty")
        
        self.param1 = param1
        self.param2 = param2 or 0
        self.logger = logging.getLogger(__name__)
    
    def example_method(self, input_data: List[T]) -> Dict[str, R]:
        """
        Process the input data and return results.
        
        This method demonstrates proper docstring formatting for methods,
        including descriptions of parameters, return values, and exceptions.
        
        Args:
            input_data: List of items to process.
        
        Returns:
            Dictionary mapping item identifiers to processed results.
        
        Raises:
            SpecificError: If input_data is empty.
            ValueError: If an item in input_data is invalid.
        """
        if not input_data:
            raise SpecificError("input_data cannot be empty")
        
        results = {}
        
        for i, item in enumerate(input_data):
            try:
                # Process the item
                result = self._process_item(item)
                results[f"item_{i}"] = result
            except Exception as e:
                self.logger.error(f"Error processing item {i}: {str(e)}")
                raise ValueError(f"Invalid item at index {i}") from e
        
        return results
    
    def _process_item(self, item: T) -> R:
        """
        Process a single item.
        
        This is a private helper method, as indicated by the underscore prefix.
        Private methods should still have proper docstrings.
        
        Args:
            item: The item to process.
        
        Returns:
            The processed result.
        """
        # Implementation details
        return item  # type: ignore


def example_function(input_value: str, option: bool = False) -> int:
    """
    Process the input value and return a result.
    
    This function demonstrates proper docstring formatting for functions,
    including descriptions of parameters, return values, and exceptions.
    
    Args:
        input_value: The value to process.
        option: Whether to enable an optional behavior. Defaults to False.
    
    Returns:
        The processed result as an integer.
    
    Raises:
        ValueError: If input_value is empty.
    
    Examples:
        >>> example_function("test")
        4
        >>> example_function("test", option=True)
        8
    """
    if not input_value:
        raise ValueError("input_value cannot be empty")
    
    # Log at appropriate level
    logger = logging.getLogger(__name__)
    logger.debug(f"Processing input: {input_value}, option: {option}")
    
    try:
        # Process the input
        result = len(input_value)
        
        if option:
            result *= 2
        
        return result
    except Exception as e:
        # Log the error
        logger.error(f"Error processing input: {str(e)}")
        # Re-raise with more context
        raise ValueError(f"Failed to process input: {input_value}") from e


def example_with_multiple_parameters(
    param1: str,
    param2: int,
    param3: Optional[List[str]] = None,
    *args: Any,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Example function with multiple parameters.
    
    This function demonstrates how to format docstrings for functions
    with multiple parameters, including optional parameters, *args, and **kwargs.
    
    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter.
        param3: Description of the third parameter. Defaults to None.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    
    Returns:
        Dictionary containing the processed results.
    """
    # Implementation details
    return {
        "param1": param1,
        "param2": param2,
        "param3": param3 or [],
        "args": args,
        "kwargs": kwargs
    }


# If the module can be run as a script, include this block
if __name__ == "__main__":
    # Example usage of the module
    example = ExampleClass("example")
    result = example.example_method(["item1", "item2"])
    print(result)
    
    value = example_function("test", option=True)
    print(value)