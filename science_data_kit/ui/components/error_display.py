"""
Error Display Components for Science Data Kit

This module provides standardized components for displaying errors in the Science Data Kit UI.
It works with the error handling system in science_data_kit.core.utils.error_handling.
"""

import streamlit as st
import traceback
from typing import Optional, Dict, Any, Union
from enum import Enum
import datetime

# Try to import error handling utilities
try:
    from science_data_kit.core.utils.error_handling import SDKError, ErrorSeverity
    HAS_ERROR_HANDLING = True
except ImportError:
    HAS_ERROR_HANDLING = False
    # Define fallback classes if error_handling module is not available
    class ErrorSeverity(Enum):
        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"
    
    class SDKError(Exception):
        def __init__(self, message, error_code="SDK-UI-001", category=None, severity=ErrorSeverity.ERROR, details=None, original_exception=None):
            self.error_code = error_code
            self.category = category
            self.severity = severity
            self.details = details or {}
            self.original_exception = original_exception
            super().__init__(message)


class ErrorDisplayStyle(Enum):
    """Styles for displaying errors."""
    MINIMAL = "minimal"  # Just the error message
    STANDARD = "standard"  # Error message with icon and basic details
    DETAILED = "detailed"  # Full error details including stack trace
    TOAST = "toast"  # Temporary notification
    MODAL = "modal"  # Modal dialog


def format_error_message(error: Union[Exception, SDKError], context: Optional[str] = None) -> str:
    """
    Format an error message for display.
    
    Args:
        error: The error to format
        context: Optional context information
        
    Returns:
        Formatted error message
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if isinstance(error, SDKError):
        # Format SDK error
        message = f"Error: {str(error)}"
        if hasattr(error, 'error_code'):
            message = f"[{error.error_code}] {message}"
        
        details = []
        if context:
            details.append(f"Context: {context}")
        if hasattr(error, 'category') and error.category:
            details.append(f"Category: {error.category}")
        if hasattr(error, 'details') and error.details:
            for key, value in error.details.items():
                if key != "original_traceback":  # Skip traceback in the message
                    details.append(f"{key}: {value}")
        
        if details:
            message = f"{message}\n{' | '.join(details)}"
    else:
        # Format standard exception
        message = f"Error: {str(error)}"
        if context:
            message = f"{message}\nContext: {context}"
    
    return f"{message}\nTimestamp: {timestamp}"


def display_error(
    error: Union[Exception, SDKError, str],
    context: Optional[str] = None,
    level: str = "error",
    style: ErrorDisplayStyle = ErrorDisplayStyle.STANDARD,
    show_traceback: bool = False,
    container: Optional[Any] = None
) -> None:
    """
    Display an error in the Streamlit UI.
    
    Args:
        error: The error to display (can be an exception, SDK error, or string)
        context: Optional context information
        level: Display level (info, warning, error)
        style: Display style
        show_traceback: Whether to show the traceback
        container: Optional container to display the error in
    """
    # Convert string to exception if needed
    if isinstance(error, str):
        error = Exception(error)
    
    # Format the error message
    message = format_error_message(error, context)
    
    # Get the display container
    display_container = container if container is not None else st
    
    # Display based on level
    if level == "info":
        display_func = display_container.info
    elif level == "warning":
        display_func = display_container.warning
    else:  # Default to error
        display_func = display_container.error
    
    # Display based on style
    if style == ErrorDisplayStyle.MINIMAL:
        # Just show the error message without any formatting
        if isinstance(error, SDKError):
            display_func(str(error))
        else:
            display_func(str(error))
    
    elif style == ErrorDisplayStyle.TOAST:
        # Show as a toast notification
        st.toast(message, icon="⚠️" if level == "warning" else "❌")
    
    elif style == ErrorDisplayStyle.MODAL:
        # Show as a modal dialog
        st.error("An error has occurred")
        with st.expander("Error Details", expanded=True):
            st.markdown(f"```\n{message}\n```")
            if show_traceback and hasattr(error, 'original_exception') and error.original_exception:
                st.markdown("### Traceback")
                st.markdown(f"```\n{''.join(traceback.format_exception(type(error.original_exception), error.original_exception, error.original_exception.__traceback__))}\n```")
            elif show_traceback:
                st.markdown("### Traceback")
                st.markdown(f"```\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}\n```")
    
    elif style == ErrorDisplayStyle.DETAILED:
        # Show detailed error information
        display_func(message)
        if show_traceback and hasattr(error, 'original_exception') and error.original_exception:
            with st.expander("Traceback", expanded=False):
                st.code(''.join(traceback.format_exception(type(error.original_exception), error.original_exception, error.original_exception.__traceback__)))
        elif show_traceback:
            with st.expander("Traceback", expanded=False):
                st.code(''.join(traceback.format_exception(type(error), error, error.__traceback__)))
    
    else:  # Default to STANDARD
        # Show standard error display
        display_func(message)


def create_error_boundary(func):
    """
    Decorator to create an error boundary around a function.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            display_error(e, context=f"Error in {func.__name__}")
            return None
    
    return wrapper


class ErrorBoundary:
    """
    Context manager for creating an error boundary.
    
    Example:
        with ErrorBoundary("Loading data"):
            data = load_data()
    """
    
    def __init__(self, context: str, level: str = "error", style: ErrorDisplayStyle = ErrorDisplayStyle.STANDARD):
        """
        Initialize the error boundary.
        
        Args:
            context: Context information for the error
            level: Display level (info, warning, error)
            style: Display style
        """
        self.context = context
        self.level = level
        self.style = style
    
    def __enter__(self):
        """Enter the context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager and handle any exceptions.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
            
        Returns:
            True if the exception was handled, False otherwise
        """
        if exc_val is not None:
            display_error(exc_val, context=self.context, level=self.level, style=self.style)
            return True  # Suppress the exception
        return False  # No exception to handle