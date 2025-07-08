"""
Science Data Kit - Dropbox Extension
Error Handling Module

This module provides error handling and retry logic for Dropbox API operations.
"""

import logging
import time
import functools
import random
from typing import Dict, Any, Optional, List, Union, Callable, TypeVar, Type
from datetime import datetime, timedelta

from dropbox.exceptions import (
    ApiError,
    AuthError,
    BadInputError,
    HttpError,
    InternalServerError,
    RateLimitError,
    RouteError
)

logger = logging.getLogger(__name__)

# Type variable for function return type
T = TypeVar('T')

class DropboxApiException(Exception):
    """Base exception for Dropbox API errors with enhanced context."""
    
    def __init__(
        self, 
        message: str, 
        original_error: Optional[Exception] = None,
        operation: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            original_error: Original exception that caused this error
            operation: Name of the operation that failed
            params: Parameters passed to the operation
            retry_count: Number of retries attempted
        """
        self.original_error = original_error
        self.operation = operation
        self.params = params
        self.retry_count = retry_count
        self.timestamp = datetime.now()
        
        # Build detailed message
        detailed_message = f"{message}"
        if operation:
            detailed_message += f" (operation: {operation})"
        if retry_count > 0:
            detailed_message += f" (retries: {retry_count})"
        if original_error:
            detailed_message += f" - Original error: {str(original_error)}"
            
        super().__init__(detailed_message)

class DropboxRateLimitException(DropboxApiException):
    """Exception for rate limit errors."""
    
    def __init__(
        self, 
        message: str, 
        original_error: Optional[Exception] = None,
        operation: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
        retry_after: Optional[int] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            original_error: Original exception that caused this error
            operation: Name of the operation that failed
            params: Parameters passed to the operation
            retry_count: Number of retries attempted
            retry_after: Seconds to wait before retrying
        """
        self.retry_after = retry_after
        super().__init__(message, original_error, operation, params, retry_count)

class DropboxNetworkException(DropboxApiException):
    """Exception for network-related errors."""
    pass

class DropboxAuthException(DropboxApiException):
    """Exception for authentication errors."""
    pass

class DropboxServerException(DropboxApiException):
    """Exception for server-side errors."""
    pass

class DropboxClientException(DropboxApiException):
    """Exception for client-side errors."""
    pass

def map_dropbox_exception(
    error: Exception, 
    operation: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    retry_count: int = 0
) -> DropboxApiException:
    """
    Map a Dropbox API exception to a custom exception.
    
    Args:
        error: Original exception
        operation: Name of the operation that failed
        params: Parameters passed to the operation
        retry_count: Number of retries attempted
        
    Returns:
        Mapped exception
    """
    if isinstance(error, RateLimitError):
        # Extract retry_after if available
        retry_after = None
        if hasattr(error, 'error') and hasattr(error.error, 'retry_after'):
            retry_after = error.error.retry_after
            
        return DropboxRateLimitException(
            "Rate limit exceeded",
            error,
            operation,
            params,
            retry_count,
            retry_after
        )
    elif isinstance(error, AuthError):
        return DropboxAuthException(
            "Authentication error",
            error,
            operation,
            params,
            retry_count
        )
    elif isinstance(error, BadInputError):
        return DropboxClientException(
            "Invalid input",
            error,
            operation,
            params,
            retry_count
        )
    elif isinstance(error, HttpError):
        return DropboxNetworkException(
            f"HTTP error: {error.status_code}",
            error,
            operation,
            params,
            retry_count
        )
    elif isinstance(error, InternalServerError):
        return DropboxServerException(
            "Internal server error",
            error,
            operation,
            params,
            retry_count
        )
    elif isinstance(error, RouteError):
        return DropboxClientException(
            "Invalid API route",
            error,
            operation,
            params,
            retry_count
        )
    elif isinstance(error, ApiError):
        return DropboxApiException(
            "API error",
            error,
            operation,
            params,
            retry_count
        )
    else:
        return DropboxApiException(
            "Unexpected error",
            error,
            operation,
            params,
            retry_count
        )

def with_retry(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: float = 0.1,
    retry_exceptions: List[Type[Exception]] = None,
    operation_name: Optional[str] = None
) -> Callable:
    """
    Decorator for retrying Dropbox API operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries
        retry_delay: Initial delay between retries in seconds
        backoff_factor: Factor to increase delay for each retry
        jitter: Random jitter factor to add to delay
        retry_exceptions: List of exception types to retry on
        operation_name: Name of the operation for logging
        
    Returns:
        Decorated function
    """
    if retry_exceptions is None:
        retry_exceptions = [
            RateLimitError,
            HttpError,
            InternalServerError,
            ApiError
        ]
        
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Get operation name from function if not provided
            op_name = operation_name or func.__name__
            
            # Track retry count
            retry_count = 0
            last_exception = None
            
            # Try the operation with retries
            while retry_count <= max_retries:
                try:
                    return func(*args, **kwargs)
                except tuple(retry_exceptions) as e:
                    last_exception = e
                    retry_count += 1
                    
                    # Check if we've reached max retries
                    if retry_count > max_retries:
                        break
                        
                    # Calculate delay with exponential backoff and jitter
                    delay = retry_delay * (backoff_factor ** (retry_count - 1))
                    jitter_amount = random.uniform(-jitter * delay, jitter * delay)
                    delay += jitter_amount
                    
                    # Handle rate limit errors with retry-after header
                    if isinstance(e, RateLimitError) and hasattr(e, 'error') and hasattr(e.error, 'retry_after'):
                        delay = max(delay, e.error.retry_after)
                        
                    logger.warning(
                        f"Retrying {op_name} after error: {str(e)}. "
                        f"Retry {retry_count}/{max_retries} in {delay:.2f} seconds"
                    )
                    
                    # Sleep before retry
                    time.sleep(delay)
                except Exception as e:
                    # Don't retry on other exceptions
                    raise map_dropbox_exception(e, op_name, kwargs)
                    
            # If we've exhausted retries, raise the last exception
            if last_exception:
                raise map_dropbox_exception(
                    last_exception, 
                    op_name, 
                    kwargs, 
                    retry_count
                )
                
            # This should never happen, but just in case
            raise DropboxApiException(
                f"Failed after {max_retries} retries",
                operation=op_name,
                params=kwargs,
                retry_count=retry_count
            )
                
        return wrapper
    return decorator

class DropboxErrorHandler:
    """
    Class for handling Dropbox API errors and providing retry functionality.
    
    This class provides methods for retrying operations, handling errors,
    and logging error information.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        jitter: float = 0.1
    ):
        """
        Initialize the error handler.
        
        Args:
            max_retries: Maximum number of retries
            retry_delay: Initial delay between retries in seconds
            backoff_factor: Factor to increase delay for each retry
            jitter: Random jitter factor to add to delay
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.error_log = []
        
    def retry(
        self,
        func: Callable[..., T],
        *args,
        operation_name: Optional[str] = None,
        retry_exceptions: List[Type[Exception]] = None,
        **kwargs
    ) -> T:
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Function to retry
            *args: Positional arguments for the function
            operation_name: Name of the operation for logging
            retry_exceptions: List of exception types to retry on
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function
        """
        if retry_exceptions is None:
            retry_exceptions = [
                RateLimitError,
                HttpError,
                InternalServerError,
                ApiError
            ]
            
        # Get operation name from function if not provided
        op_name = operation_name or func.__name__
        
        # Track retry count
        retry_count = 0
        last_exception = None
        
        # Try the operation with retries
        while retry_count <= self.max_retries:
            try:
                return func(*args, **kwargs)
            except tuple(retry_exceptions) as e:
                last_exception = e
                retry_count += 1
                
                # Log the error
                self._log_error(e, op_name, kwargs, retry_count)
                
                # Check if we've reached max retries
                if retry_count > self.max_retries:
                    break
                    
                # Calculate delay with exponential backoff and jitter
                delay = self.retry_delay * (self.backoff_factor ** (retry_count - 1))
                jitter_amount = random.uniform(-self.jitter * delay, self.jitter * delay)
                delay += jitter_amount
                
                # Handle rate limit errors with retry-after header
                if isinstance(e, RateLimitError) and hasattr(e, 'error') and hasattr(e.error, 'retry_after'):
                    delay = max(delay, e.error.retry_after)
                    
                logger.warning(
                    f"Retrying {op_name} after error: {str(e)}. "
                    f"Retry {retry_count}/{self.max_retries} in {delay:.2f} seconds"
                )
                
                # Sleep before retry
                time.sleep(delay)
            except Exception as e:
                # Log the error
                self._log_error(e, op_name, kwargs, retry_count)
                
                # Don't retry on other exceptions
                raise map_dropbox_exception(e, op_name, kwargs)
                
        # If we've exhausted retries, raise the last exception
        if last_exception:
            raise map_dropbox_exception(
                last_exception, 
                op_name, 
                kwargs, 
                retry_count
            )
            
        # This should never happen, but just in case
        raise DropboxApiException(
            f"Failed after {self.max_retries} retries",
            operation=op_name,
            params=kwargs,
            retry_count=retry_count
        )
        
    def _log_error(
        self,
        error: Exception,
        operation: str,
        params: Dict[str, Any],
        retry_count: int
    ) -> None:
        """
        Log an error to the error log.
        
        Args:
            error: Exception that occurred
            operation: Name of the operation that failed
            params: Parameters passed to the operation
            retry_count: Current retry count
        """
        self.error_log.append({
            'timestamp': datetime.now(),
            'operation': operation,
            'error': str(error),
            'error_type': type(error).__name__,
            'params': params,
            'retry_count': retry_count
        })
        
    def get_error_log(self) -> List[Dict[str, Any]]:
        """
        Get the error log.
        
        Returns:
            List of error log entries
        """
        return self.error_log
        
    def clear_error_log(self) -> None:
        """
        Clear the error log.
        """
        self.error_log = []
        
    def get_retry_decorator(
        self,
        operation_name: Optional[str] = None,
        retry_exceptions: List[Type[Exception]] = None
    ) -> Callable:
        """
        Get a retry decorator for a function.
        
        Args:
            operation_name: Name of the operation for logging
            retry_exceptions: List of exception types to retry on
            
        Returns:
            Retry decorator
        """
        return with_retry(
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            backoff_factor=self.backoff_factor,
            jitter=self.jitter,
            retry_exceptions=retry_exceptions,
            operation_name=operation_name
        )