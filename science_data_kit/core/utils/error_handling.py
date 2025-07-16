"""
Error Handling Utilities for Science Data Kit

This module provides utilities for error handling and logging in the Science Data Kit.
It includes custom exception classes, error codes, and utilities for consistent
error handling across the application.

The module offers several key components:
- SDKError: Base exception class for all SDK-specific exceptions
- ErrorCode: Enum of error codes for categorizing errors
- ErrorHandler: Utility class for handling errors consistently
- Logging utilities: Functions for consistent logging across the application

Usage:
    ```python
    from science_data_kit.core.utils.error_handling import SDKError, ErrorCode, log_error

    # Example 1: Raising a custom exception
    try:
        # Some operation that might fail
        if not valid_operation():
            raise SDKError(
                code=ErrorCode.INVALID_OPERATION,
                message="The operation is not valid",
                details={"operation": "example_operation", "reason": "invalid parameters"}
            )
    except SDKError as e:
        # Handle the error
        log_error(e)
        # Perform recovery or cleanup

    # Example 2: Using the error handler
    from science_data_kit.core.utils.error_handling import ErrorHandler

    handler = ErrorHandler()
    result = handler.handle_operation(
        lambda: potentially_failing_function(),
        error_code=ErrorCode.OPERATION_FAILED,
        error_message="Failed to execute the operation",
        default_value=None
    )
    ```
"""

# Standard library imports
import enum
import functools
import inspect
import logging
import sys
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')


class ErrorCode(enum.Enum):
    """Error codes for categorizing errors in the Science Data Kit."""
    # General errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    INVALID_OPERATION = "INVALID_OPERATION"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    TIMEOUT = "TIMEOUT"
    
    # Parallel processing errors
    PARALLEL_EXECUTION_ERROR = "PARALLEL_EXECUTION_ERROR"
    TASK_EXECUTION_ERROR = "TASK_EXECUTION_ERROR"
    TASK_TIMEOUT = "TASK_TIMEOUT"
    TASK_CANCELLED = "TASK_CANCELLED"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    EXECUTOR_SHUTDOWN = "EXECUTOR_SHUTDOWN"
    
    # Data processing errors
    DATA_PROCESSING_ERROR = "DATA_PROCESSING_ERROR"
    EMPTY_DATA = "EMPTY_DATA"
    INVALID_DATA_FORMAT = "INVALID_DATA_FORMAT"
    DATA_TRANSFORMATION_ERROR = "DATA_TRANSFORMATION_ERROR"
    
    # State management errors
    STATE_ERROR = "STATE_ERROR"
    STATE_NOT_FOUND = "STATE_NOT_FOUND"
    STATE_INVALID_TYPE = "STATE_INVALID_TYPE"
    STATE_SERIALIZATION_ERROR = "STATE_SERIALIZATION_ERROR"
    
    # I/O errors
    IO_ERROR = "IO_ERROR"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    
    # Network errors
    NETWORK_ERROR = "NETWORK_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    REQUEST_ERROR = "REQUEST_ERROR"
    RESPONSE_ERROR = "RESPONSE_ERROR"
    
    # Authentication errors
    AUTH_ERROR = "AUTH_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    
    # Framework-specific errors
    FRAMEWORK_ERROR = "FRAMEWORK_ERROR"
    ADAPTER_ERROR = "ADAPTER_ERROR"
    UI_ERROR = "UI_ERROR"


class SDKError(Exception):
    """
    Base exception class for all SDK-specific exceptions.
    
    This class provides a consistent interface for all exceptions raised by the SDK,
    including error codes, messages, and additional details.
    """
    
    def __init__(
        self,
        code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        message: str = "An unknown error occurred",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize an SDK error.
        
        Args:
            code: Error code from the ErrorCode enum.
            message: Human-readable error message.
            details: Additional details about the error.
            cause: Original exception that caused this error, if any.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        self.cause = cause
        self.timestamp = time.time()
        
        # Construct the full error message
        full_message = f"{code.value}: {message}"
        if details:
            full_message += f" - Details: {details}"
        if cause:
            full_message += f" - Caused by: {str(cause)}"
        
        super().__init__(full_message)


class ParallelExecutionError(SDKError):
    """Exception raised when an error occurs during parallel execution."""
    
    def __init__(
        self,
        message: str = "An error occurred during parallel execution",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize a parallel execution error.
        
        Args:
            message: Human-readable error message.
            details: Additional details about the error.
            cause: Original exception that caused this error, if any.
        """
        super().__init__(
            code=ErrorCode.PARALLEL_EXECUTION_ERROR,
            message=message,
            details=details,
            cause=cause
        )


class TaskExecutionError(SDKError):
    """Exception raised when an error occurs during task execution."""
    
    def __init__(
        self,
        message: str = "An error occurred during task execution",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize a task execution error.
        
        Args:
            message: Human-readable error message.
            details: Additional details about the error.
            cause: Original exception that caused this error, if any.
        """
        super().__init__(
            code=ErrorCode.TASK_EXECUTION_ERROR,
            message=message,
            details=details,
            cause=cause
        )


class TaskTimeoutError(SDKError):
    """Exception raised when a task times out."""
    
    def __init__(
        self,
        message: str = "Task execution timed out",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize a task timeout error.
        
        Args:
            message: Human-readable error message.
            details: Additional details about the error.
            cause: Original exception that caused this error, if any.
        """
        super().__init__(
            code=ErrorCode.TASK_TIMEOUT,
            message=message,
            details=details,
            cause=cause
        )


class TaskNotFoundError(SDKError):
    """Exception raised when a task is not found."""
    
    def __init__(
        self,
        message: str = "Task not found",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize a task not found error.
        
        Args:
            message: Human-readable error message.
            details: Additional details about the error.
            cause: Original exception that caused this error, if any.
        """
        super().__init__(
            code=ErrorCode.TASK_NOT_FOUND,
            message=message,
            details=details,
            cause=cause
        )


class ExecutorShutdownError(SDKError):
    """Exception raised when an operation is attempted on a shutdown executor."""
    
    def __init__(
        self,
        message: str = "Executor has been shut down",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize an executor shutdown error.
        
        Args:
            message: Human-readable error message.
            details: Additional details about the error.
            cause: Original exception that caused this error, if any.
        """
        super().__init__(
            code=ErrorCode.EXECUTOR_SHUTDOWN,
            message=message,
            details=details,
            cause=cause
        )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    If no name is provided, the logger name is derived from the calling module.
    
    Args:
        name: Name of the logger. If None, uses the calling module's name.
        
    Returns:
        Logger instance.
    """
    if name is None:
        # Get the calling frame
        frame = inspect.currentframe()
        if frame is not None:
            frame = frame.f_back
        if frame is not None:
            # Get the module name from the frame
            module = inspect.getmodule(frame)
            if module is not None:
                name = module.__name__
    
    # Fall back to a default name if we couldn't determine the module name
    if name is None:
        name = "science_data_kit"
    
    return logging.getLogger(name)


def log_exception(
    exc: Exception,
    logger: Optional[logging.Logger] = None,
    level: int = logging.ERROR,
    include_traceback: bool = True
) -> None:
    """
    Log an exception with detailed information.
    
    Args:
        exc: The exception to log.
        logger: Logger to use. If None, a logger is created based on the calling module.
        level: Logging level to use.
        include_traceback: Whether to include the traceback in the log message.
    """
    if logger is None:
        logger = get_logger()
    
    # Get exception details
    exc_type = type(exc).__name__
    exc_msg = str(exc)
    
    # Construct the log message
    log_msg = f"Exception {exc_type}: {exc_msg}"
    
    # Add SDK-specific error details if available
    if isinstance(exc, SDKError):
        log_msg = f"SDK Error {exc.code.value}: {exc.message}"
        if exc.details:
            log_msg += f" - Details: {exc.details}"
        if exc.cause:
            log_msg += f" - Caused by: {type(exc.cause).__name__}: {str(exc.cause)}"
    
    # Log the message
    if include_traceback:
        logger.log(level, log_msg, exc_info=True)
    else:
        logger.log(level, log_msg)


def log_error(
    message: Union[str, Exception],
    logger: Optional[logging.Logger] = None,
    details: Optional[Dict[str, Any]] = None,
    include_traceback: bool = True
) -> None:
    """
    Log an error message or exception.
    
    Args:
        message: Error message or exception to log.
        logger: Logger to use. If None, a logger is created based on the calling module.
        details: Additional details to include in the log message.
        include_traceback: Whether to include the traceback in the log message.
    """
    if logger is None:
        logger = get_logger()
    
    if isinstance(message, Exception):
        log_exception(message, logger, logging.ERROR, include_traceback)
    else:
        log_msg = message
        if details:
            log_msg += f" - Details: {details}"
        logger.error(log_msg)


def log_warning(
    message: str,
    logger: Optional[logging.Logger] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a warning message.
    
    Args:
        message: Warning message to log.
        logger: Logger to use. If None, a logger is created based on the calling module.
        details: Additional details to include in the log message.
    """
    if logger is None:
        logger = get_logger()
    
    log_msg = message
    if details:
        log_msg += f" - Details: {details}"
    logger.warning(log_msg)


def log_info(
    message: str,
    logger: Optional[logging.Logger] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an info message.
    
    Args:
        message: Info message to log.
        logger: Logger to use. If None, a logger is created based on the calling module.
        details: Additional details to include in the log message.
    """
    if logger is None:
        logger = get_logger()
    
    log_msg = message
    if details:
        log_msg += f" - Details: {details}"
    logger.info(log_msg)


def log_debug(
    message: str,
    logger: Optional[logging.Logger] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a debug message.
    
    Args:
        message: Debug message to log.
        logger: Logger to use. If None, a logger is created based on the calling module.
        details: Additional details to include in the log message.
    """
    if logger is None:
        logger = get_logger()
    
    log_msg = message
    if details:
        log_msg += f" - Details: {details}"
    logger.debug(log_msg)


class ErrorHandler:
    """
    Utility class for handling errors consistently.
    
    This class provides methods for handling errors in a consistent way,
    including logging, retrying operations, and providing default values.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize an error handler.
        
        Args:
            logger: Logger to use. If None, a logger is created based on the calling module.
        """
        self.logger = logger or get_logger()
    
    def handle_operation(
        self,
        operation: Callable[[], R],
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        error_message: str = "Operation failed",
        default_value: Optional[R] = None,
        raise_error: bool = False,
        log_level: int = logging.ERROR,
        include_traceback: bool = True
    ) -> Optional[R]:
        """
        Handle an operation that might raise an exception.
        
        Args:
            operation: Function to execute.
            error_code: Error code to use if an exception is raised.
            error_message: Error message to use if an exception is raised.
            default_value: Value to return if an exception is raised and raise_error is False.
            raise_error: Whether to re-raise the exception as an SDKError.
            log_level: Logging level to use if an exception is raised.
            include_traceback: Whether to include the traceback in the log message.
            
        Returns:
            Result of the operation, or default_value if an exception is raised and raise_error is False.
            
        Raises:
            SDKError: If an exception is raised and raise_error is True.
        """
        try:
            return operation()
        except Exception as e:
            # Log the error
            self.logger.log(
                log_level,
                f"{error_message}: {str(e)}",
                exc_info=include_traceback
            )
            
            # Raise an SDKError if requested
            if raise_error:
                raise SDKError(
                    code=error_code,
                    message=error_message,
                    details={"exception": str(e)},
                    cause=e
                )
            
            # Otherwise, return the default value
            return default_value
    
    def retry_operation(
        self,
        operation: Callable[[], R],
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        error_message: str = "Operation failed after retries",
        default_value: Optional[R] = None,
        raise_error: bool = True,
        log_level: int = logging.ERROR,
        include_traceback: bool = True
    ) -> Optional[R]:
        """
        Retry an operation that might raise an exception.
        
        Args:
            operation: Function to execute.
            max_retries: Maximum number of retries.
            retry_delay: Initial delay between retries in seconds.
            backoff_factor: Factor to increase the delay by after each retry.
            error_code: Error code to use if all retries fail.
            error_message: Error message to use if all retries fail.
            default_value: Value to return if all retries fail and raise_error is False.
            raise_error: Whether to re-raise the exception as an SDKError if all retries fail.
            log_level: Logging level to use if an exception is raised.
            include_traceback: Whether to include the traceback in the log message.
            
        Returns:
            Result of the operation, or default_value if all retries fail and raise_error is False.
            
        Raises:
            SDKError: If all retries fail and raise_error is True.
        """
        last_exception = None
        current_delay = retry_delay
        
        for attempt in range(max_retries + 1):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                
                # Log the error
                if attempt < max_retries:
                    self.logger.log(
                        logging.WARNING,
                        f"Operation failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}",
                        exc_info=include_traceback
                    )
                    
                    # Wait before retrying
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
                else:
                    # Log the final failure
                    self.logger.log(
                        log_level,
                        f"Operation failed after {max_retries + 1} attempts: {str(e)}",
                        exc_info=include_traceback
                    )
        
        # If we get here, all retries failed
        if raise_error and last_exception is not None:
            raise SDKError(
                code=error_code,
                message=error_message,
                details={"exception": str(last_exception), "attempts": max_retries + 1},
                cause=last_exception
            )
        
        return default_value


def retry(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
    error_message: str = "Operation failed after retries",
    raise_error: bool = True,
    log_level: int = logging.ERROR,
    include_traceback: bool = True
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for retrying a function that might raise an exception.
    
    Args:
        max_retries: Maximum number of retries.
        retry_delay: Initial delay between retries in seconds.
        backoff_factor: Factor to increase the delay by after each retry.
        error_code: Error code to use if all retries fail.
        error_message: Error message to use if all retries fail.
        raise_error: Whether to re-raise the exception as an SDKError if all retries fail.
        log_level: Logging level to use if an exception is raised.
        include_traceback: Whether to include the traceback in the log message.
        
    Returns:
        Decorator function.
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            handler = ErrorHandler()
            
            def operation() -> R:
                return func(*args, **kwargs)
            
            result = handler.retry_operation(
                operation=operation,
                max_retries=max_retries,
                retry_delay=retry_delay,
                backoff_factor=backoff_factor,
                error_code=error_code,
                error_message=error_message,
                raise_error=raise_error,
                log_level=log_level,
                include_traceback=include_traceback
            )
            
            # The result should never be None if raise_error is True,
            # but we need to satisfy the type checker
            if result is None and raise_error:
                raise SDKError(
                    code=error_code,
                    message=error_message
                )
            
            return cast(R, result)
        
        return wrapper
    
    return decorator


class PerformanceMonitor:
    """
    Utility class for monitoring performance of operations.
    
    This class provides methods for measuring execution time, memory usage,
    and other performance metrics for operations.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize a performance monitor.
        
        Args:
            logger: Logger to use. If None, a logger is created based on the calling module.
        """
        self.logger = logger or get_logger()
        self.timers: Dict[str, float] = {}
    
    def start_timer(self, name: str) -> None:
        """
        Start a timer with the specified name.
        
        Args:
            name: Name of the timer.
        """
        self.timers[name] = time.time()
    
    def stop_timer(self, name: str) -> float:
        """
        Stop a timer and return the elapsed time.
        
        Args:
            name: Name of the timer.
            
        Returns:
            Elapsed time in seconds.
            
        Raises:
            KeyError: If the timer with the specified name does not exist.
        """
        if name not in self.timers:
            raise KeyError(f"Timer '{name}' does not exist")
        
        elapsed = time.time() - self.timers[name]
        del self.timers[name]
        return elapsed
    
    def log_timer(self, name: str, level: int = logging.INFO) -> float:
        """
        Stop a timer, log the elapsed time, and return the elapsed time.
        
        Args:
            name: Name of the timer.
            level: Logging level to use.
            
        Returns:
            Elapsed time in seconds.
            
        Raises:
            KeyError: If the timer with the specified name does not exist.
        """
        elapsed = self.stop_timer(name)
        self.logger.log(level, f"Timer '{name}' elapsed: {elapsed:.6f} seconds")
        return elapsed
    
    def measure_execution_time(
        self,
        operation: Callable[[], R],
        name: str = "operation",
        level: int = logging.INFO
    ) -> R:
        """
        Measure the execution time of an operation.
        
        Args:
            operation: Function to execute.
            name: Name to use in the log message.
            level: Logging level to use.
            
        Returns:
            Result of the operation.
        """
        self.start_timer(name)
        try:
            result = operation()
            return result
        finally:
            elapsed = self.stop_timer(name)
            self.logger.log(level, f"Operation '{name}' took {elapsed:.6f} seconds")


def measure_execution_time(
    name: str = "operation",
    level: int = logging.INFO,
    logger: Optional[logging.Logger] = None
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for measuring the execution time of a function.
    
    Args:
        name: Name to use in the log message. If None, uses the function name.
        level: Logging level to use.
        logger: Logger to use. If None, a logger is created based on the calling module.
        
    Returns:
        Decorator function.
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            nonlocal name
            if name == "operation":
                name = func.__name__
            
            monitor = PerformanceMonitor(logger)
            monitor.start_timer(name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = monitor.stop_timer(name)
                monitor.logger.log(level, f"Function '{name}' took {elapsed:.6f} seconds")
        
        return wrapper
    
    return decorator