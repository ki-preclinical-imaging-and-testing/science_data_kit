"""
Error Handler for Science Data Kit

This module provides a wrapper around the error handling functionality in error_handling.py,
adding an ErrorHandler class and additional utility functions for easier error management.
"""

import logging
import traceback
import sys
from typing import Dict, Any, Optional, Type, List, Callable, Union, TypeVar

# Import error handling utilities
from science_data_kit.core.utils.error_handling import (
    SDKError, ErrorSeverity, ErrorCategory, handle_error as _handle_error,
    with_error_handling as _with_error_handling, configure_logging
)

# Re-export error handling utilities for backward compatibility
__all__ = [
    'ErrorHandler', 'handle_error', 'log_error', 'with_error_handling',
    'SDKError', 'ErrorSeverity', 'ErrorCategory', 'configure_logging'
]


class ErrorHandler:
    """
    A class for handling errors in the Science Data Kit.
    
    This class provides a convenient interface for handling errors, including
    logging, formatting, and converting standard exceptions to SDK errors.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize a new error handler.
        
        Args:
            logger: Logger to use for logging errors. If None, uses the root logger.
        """
        self.logger = logger or logging.getLogger()
        self.error_map: Dict[Type[Exception], Type[SDKError]] = {}
        
    def register_error_mapping(self, exception_type: Type[Exception], sdk_error_type: Type[SDKError]) -> None:
        """
        Register a mapping from a standard exception type to an SDK error type.
        
        Args:
            exception_type: The standard exception type to map from
            sdk_error_type: The SDK error type to map to
        """
        self.error_map[exception_type] = sdk_error_type
        
    def handle_error(self, error: Exception, context: Optional[str] = None, raise_error: bool = True) -> Optional[SDKError]:
        """
        Handle an exception by converting it to an SDK error, logging it, and optionally raising it.
        
        Args:
            error: The exception to handle
            context: Optional context information
            raise_error: Whether to raise the SDK error after handling
            
        Returns:
            The SDK error if raise_error is False, otherwise None
            
        Raises:
            SDKError: The converted SDK error if raise_error is True
        """
        details = {"context": context} if context else {}
        
        return _handle_error(
            error=error,
            logger=self.logger,
            error_map=self.error_map,
            default_error_class=SDKError,
            default_message="An unexpected error occurred",
            raise_error=raise_error
        )
        
    def log_error(self, error: Exception, context: Optional[str] = None) -> Optional[SDKError]:
        """
        Log an exception without raising it.
        
        Args:
            error: The exception to log
            context: Optional context information
            
        Returns:
            The SDK error
        """
        return self.handle_error(error, context, raise_error=False)
        
    def with_error_handling(self, func: Callable, context: Optional[str] = None, raise_error: bool = True) -> Callable:
        """
        Decorate a function with error handling.
        
        Args:
            func: The function to decorate
            context: Optional context information
            raise_error: Whether to raise the SDK error after handling
            
        Returns:
            The decorated function
        """
        error_map = self.error_map
        logger = self.logger
        
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                details = {"context": context} if context else {}
                return _handle_error(
                    error=e,
                    logger=logger,
                    error_map=error_map,
                    default_error_class=SDKError,
                    default_message="An unexpected error occurred",
                    raise_error=raise_error
                )
                
        return wrapper


# Create a default error handler for convenience
default_error_handler = ErrorHandler()

# Convenience functions that use the default error handler
def handle_error(error: Exception, context: Optional[str] = None, raise_error: bool = True) -> Optional[SDKError]:
    """
    Handle an exception using the default error handler.
    
    Args:
        error: The exception to handle
        context: Optional context information
        raise_error: Whether to raise the SDK error after handling
        
    Returns:
        The SDK error if raise_error is False, otherwise None
        
    Raises:
        SDKError: The converted SDK error if raise_error is True
    """
    return default_error_handler.handle_error(error, context, raise_error)

def log_error(error: Exception, context: Optional[str] = None) -> Optional[SDKError]:
    """
    Log an exception using the default error handler without raising it.
    
    Args:
        error: The exception to log
        context: Optional context information
        
    Returns:
        The SDK error
    """
    return default_error_handler.log_error(error, context)

def with_error_handling(func: Callable, context: Optional[str] = None, raise_error: bool = True) -> Callable:
    """
    Decorate a function with error handling using the default error handler.
    
    Args:
        func: The function to decorate
        context: Optional context information
        raise_error: Whether to raise the SDK error after handling
        
    Returns:
        The decorated function
    """
    return default_error_handler.with_error_handling(func, context, raise_error)