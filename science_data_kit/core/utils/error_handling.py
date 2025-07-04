"""
Error Handling Utilities for Science Data Kit

This module provides centralized error handling for the Science Data Kit,
including a hierarchy of custom exception classes, error logging, and
user-friendly error messages.
"""

import logging
import traceback
import sys
from enum import Enum
from typing import Dict, Any, Optional, Type, List, Callable, Union, TypeVar, Generic

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    
    def __str__(self) -> str:
        """Return the string representation of the severity level."""
        return self.value


class ErrorCategory(Enum):
    """Categories of errors in the Science Data Kit."""
    
    # General errors
    GENERAL = "GENERAL"
    
    # Database errors
    DATABASE_CONNECTION = "DATABASE_CONNECTION"
    DATABASE_QUERY = "DATABASE_QUERY"
    DATABASE_TRANSACTION = "DATABASE_TRANSACTION"
    
    # API errors
    API_CONNECTION = "API_CONNECTION"
    API_AUTHENTICATION = "API_AUTHENTICATION"
    API_REQUEST = "API_REQUEST"
    API_RESPONSE = "API_RESPONSE"
    
    # File system errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_PERMISSION = "FILE_PERMISSION"
    FILE_IO = "FILE_IO"
    
    # Configuration errors
    CONFIG_INVALID = "CONFIG_INVALID"
    CONFIG_MISSING = "CONFIG_MISSING"
    
    # Data validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    
    # Session errors
    SESSION_ERROR = "SESSION_ERROR"
    
    # Provider errors
    PROVIDER_ERROR = "PROVIDER_ERROR"
    
    def __str__(self) -> str:
        """Return the string representation of the error category."""
        return self.value


class SDKError(Exception):
    """
    Base exception class for all Science Data Kit errors.
    
    This class provides a consistent interface for all errors in the SDK,
    including error codes, user-friendly messages, and detailed information
    for debugging.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-GENERAL-001",
        category: ErrorCategory = ErrorCategory.GENERAL,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new SDK error.
        
        Args:
            message: User-friendly error message
            error_code: Unique error code for this error
            category: Category of the error
            severity: Severity level of the error
            details: Additional details about the error
            original_exception: Original exception that caused this error
        """
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.original_exception = original_exception
        
        # Add stack trace to details if there's an original exception
        if original_exception:
            self.details["original_exception"] = str(original_exception)
            self.details["original_traceback"] = traceback.format_exception(
                type(original_exception),
                original_exception,
                original_exception.__traceback__
            )
        
        # Create a detailed message for logging
        self.detailed_message = f"{error_code} [{category}] {message}"
        
        # Call the parent constructor with the user-friendly message
        super().__init__(message)
    
    def log(self, logger: Optional[logging.Logger] = None) -> None:
        """
        Log this error with the appropriate severity level.
        
        Args:
            logger: Logger to use. If None, uses the root logger.
        """
        if logger is None:
            logger = logging.getLogger()
        
        log_method = getattr(logger, self.severity.value.lower())
        log_method(self.detailed_message, exc_info=self.original_exception)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this error to a dictionary representation.
        
        Returns:
            Dictionary representation of this error
        """
        return {
            "error_code": self.error_code,
            "message": str(self),
            "category": str(self.category),
            "severity": str(self.severity),
            "details": self.details
        }


# Database Errors
class DatabaseError(SDKError):
    """Base class for database-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-DB-001",
        category: ErrorCategory = ErrorCategory.DATABASE_CONNECTION,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new database error."""
        super().__init__(message, error_code, category, severity, details, original_exception)


class ConnectionError(DatabaseError):
    """Error connecting to a database."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-DB-002",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new connection error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.DATABASE_CONNECTION,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


class QueryError(DatabaseError):
    """Error executing a database query."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-DB-003",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new query error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.DATABASE_QUERY,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


class TransactionError(DatabaseError):
    """Error during a database transaction."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-DB-004",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new transaction error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.DATABASE_TRANSACTION,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


# API Errors
class APIError(SDKError):
    """Base class for API-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-API-001",
        category: ErrorCategory = ErrorCategory.API_CONNECTION,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new API error."""
        super().__init__(message, error_code, category, severity, details, original_exception)


class APIConnectionError(APIError):
    """Error connecting to an API."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-API-002",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new API connection error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.API_CONNECTION,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


class APIAuthenticationError(APIError):
    """Error authenticating with an API."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-API-003",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new API authentication error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.API_AUTHENTICATION,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


class APIRequestError(APIError):
    """Error making a request to an API."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-API-004",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new API request error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.API_REQUEST,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


class APIResponseError(APIError):
    """Error processing a response from an API."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-API-005",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new API response error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.API_RESPONSE,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


# File System Errors
class FileSystemError(SDKError):
    """Base class for file system-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-FS-001",
        category: ErrorCategory = ErrorCategory.FILE_IO,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new file system error."""
        super().__init__(message, error_code, category, severity, details, original_exception)


class FileNotFoundError(FileSystemError):
    """Error when a file is not found."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-FS-002",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new file not found error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.FILE_NOT_FOUND,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


class FilePermissionError(FileSystemError):
    """Error when permission is denied for a file operation."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-FS-003",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new file permission error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.FILE_PERMISSION,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


# Configuration Errors
class ConfigError(SDKError):
    """Base class for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-CFG-001",
        category: ErrorCategory = ErrorCategory.CONFIG_INVALID,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new configuration error."""
        super().__init__(message, error_code, category, severity, details, original_exception)


class ConfigInvalidError(ConfigError):
    """Error when configuration is invalid."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-CFG-002",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new invalid configuration error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.CONFIG_INVALID,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


class ConfigMissingError(ConfigError):
    """Error when required configuration is missing."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-CFG-003",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new missing configuration error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.CONFIG_MISSING,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


# Validation Errors
class ValidationError(SDKError):
    """Error when data validation fails."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-VAL-001",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new validation error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.VALIDATION_ERROR,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


# Session Errors
class SessionError(SDKError):
    """Error related to session management."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-SES-001",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new session error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.SESSION_ERROR,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


# Provider Errors
class ProviderError(SDKError):
    """Error related to data providers."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SDK-PRV-001",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a new provider error."""
        super().__init__(
            message,
            error_code,
            ErrorCategory.PROVIDER_ERROR,
            ErrorSeverity.ERROR,
            details,
            original_exception
        )


# Error handling utilities
def handle_error(
    error: Exception,
    logger: Optional[logging.Logger] = None,
    error_map: Optional[Dict[Type[Exception], Type[SDKError]]] = None,
    default_error_class: Type[SDKError] = SDKError,
    default_message: str = "An unexpected error occurred",
    raise_error: bool = True
) -> Optional[SDKError]:
    """
    Handle an exception by converting it to an SDK error, logging it, and optionally raising it.
    
    Args:
        error: The exception to handle
        logger: Logger to use. If None, uses the root logger.
        error_map: Mapping from exception types to SDK error classes
        default_error_class: Default SDK error class to use if no mapping is found
        default_message: Default message to use if the exception has no message
        raise_error: Whether to raise the SDK error after handling
        
    Returns:
        The SDK error if raise_error is False, otherwise None
        
    Raises:
        SDKError: The converted SDK error if raise_error is True
    """
    if logger is None:
        logger = logging.getLogger()
    
    # If the error is already an SDK error, just log and raise it
    if isinstance(error, SDKError):
        error.log(logger)
        if raise_error:
            raise error
        return error
    
    # Convert the exception to an SDK error
    error_map = error_map or {}
    error_class = error_map.get(type(error), default_error_class)
    message = str(error) or default_message
    
    sdk_error = error_class(
        message=message,
        original_exception=error,
        details={"exception_type": type(error).__name__}
    )
    
    # Log the error
    sdk_error.log(logger)
    
    # Raise or return the error
    if raise_error:
        raise sdk_error
    
    return sdk_error


def with_error_handling(
    error_map: Optional[Dict[Type[Exception], Type[SDKError]]] = None,
    logger: Optional[logging.Logger] = None,
    default_error_class: Type[SDKError] = SDKError,
    default_message: str = "An unexpected error occurred",
    raise_error: bool = True
) -> Callable[[Callable[..., R]], Callable[..., Union[R, Optional[SDKError]]]]:
    """
    Decorator to add error handling to a function.
    
    Args:
        error_map: Mapping from exception types to SDK error classes
        logger: Logger to use. If None, uses the root logger.
        default_error_class: Default SDK error class to use if no mapping is found
        default_message: Default message to use if the exception has no message
        raise_error: Whether to raise the SDK error after handling
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., R]) -> Callable[..., Union[R, Optional[SDKError]]]:
        """
        Decorator function.
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function
        """
        def wrapper(*args: Any, **kwargs: Any) -> Union[R, Optional[SDKError]]:
            """
            Wrapper function that adds error handling.
            
            Args:
                *args: Positional arguments to pass to the function
                **kwargs: Keyword arguments to pass to the function
                
            Returns:
                Result of the function if no error occurs, otherwise an SDK error
                
            Raises:
                SDKError: If an error occurs and raise_error is True
            """
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return handle_error(
                    e,
                    logger=logger,
                    error_map=error_map,
                    default_error_class=default_error_class,
                    default_message=default_message,
                    raise_error=raise_error
                )
        
        return wrapper
    
    return decorator


# Configure logging
def configure_logging(
    log_level: int = logging.INFO,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: Optional[str] = None
) -> None:
    """
    Configure logging for the Science Data Kit.
    
    Args:
        log_level: Logging level
        log_format: Format string for log messages
        log_file: Path to log file. If None, logs to console only.
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)