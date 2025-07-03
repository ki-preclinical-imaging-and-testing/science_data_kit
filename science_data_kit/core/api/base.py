"""
Base Classes for Science Data Kit API Layer

This module provides base classes and utilities for the Science Data Kit API layer,
including the base API class, error handling, and response formatting.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import json
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class APIErrorCode(Enum):
    """Error codes for API errors."""
    UNKNOWN_ERROR = 1000
    AUTHENTICATION_ERROR = 1001
    AUTHORIZATION_ERROR = 1002
    VALIDATION_ERROR = 1003
    RESOURCE_NOT_FOUND = 1004
    RESOURCE_ALREADY_EXISTS = 1005
    INTERNAL_SERVER_ERROR = 1006
    BAD_REQUEST = 1007
    METHOD_NOT_ALLOWED = 1008
    CONFLICT = 1009
    RATE_LIMIT_EXCEEDED = 1010


class APIError(Exception):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, code: APIErrorCode = APIErrorCode.UNKNOWN_ERROR, 
                 status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the API error.
        
        Args:
            message: The error message.
            code: The error code.
            status_code: The HTTP status code.
            details: Additional details about the error.
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error to a dictionary.
        
        Returns:
            A dictionary representation of the error.
        """
        return {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "details": self.details
            }
        }


class APIResponse:
    """Class for formatting API responses."""
    
    def __init__(self, data: Any = None, meta: Optional[Dict[str, Any]] = None, 
                 status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the API response.
        
        Args:
            data: The response data.
            meta: Metadata about the response.
            status_code: The HTTP status code.
            headers: Additional HTTP headers.
        """
        self.data = data
        self.meta = meta or {}
        self.status_code = status_code
        self.headers = headers or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the response to a dictionary.
        
        Returns:
            A dictionary representation of the response.
        """
        result = {}
        if self.data is not None:
            result["data"] = self.data
        if self.meta:
            result["meta"] = self.meta
        return result
    
    def to_json(self) -> str:
        """
        Convert the response to a JSON string.
        
        Returns:
            A JSON string representation of the response.
        """
        return json.dumps(self.to_dict())


class APIBase(ABC):
    """Base class for API endpoints."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the API endpoint.
        
        Args:
            config: Configuration for the API endpoint.
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def handle_request(self, method: str, path: str, params: Dict[str, Any], 
                       body: Optional[Dict[str, Any]] = None, 
                       headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """
        Handle an API request.
        
        Args:
            method: The HTTP method (GET, POST, PUT, DELETE, etc.).
            path: The request path.
            params: The query parameters.
            body: The request body.
            headers: The request headers.
            
        Returns:
            An APIResponse object.
            
        Raises:
            APIError: If there is an error handling the request.
        """
        pass
    
    def validate_request(self, method: str, path: str, params: Dict[str, Any], 
                         body: Optional[Dict[str, Any]] = None, 
                         headers: Optional[Dict[str, str]] = None) -> None:
        """
        Validate an API request.
        
        Args:
            method: The HTTP method (GET, POST, PUT, DELETE, etc.).
            path: The request path.
            params: The query parameters.
            body: The request body.
            headers: The request headers.
            
        Raises:
            APIError: If the request is invalid.
        """
        # Default implementation does nothing
        pass
    
    def format_response(self, data: Any, meta: Optional[Dict[str, Any]] = None, 
                        status_code: int = 200, 
                        headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """
        Format an API response.
        
        Args:
            data: The response data.
            meta: Metadata about the response.
            status_code: The HTTP status code.
            headers: Additional HTTP headers.
            
        Returns:
            An APIResponse object.
        """
        return APIResponse(data=data, meta=meta, status_code=status_code, headers=headers)
    
    def handle_error(self, error: Exception) -> APIResponse:
        """
        Handle an error.
        
        Args:
            error: The error to handle.
            
        Returns:
            An APIResponse object.
        """
        if isinstance(error, APIError):
            self.logger.error(f"API error: {error.message}", exc_info=True)
            return APIResponse(
                data=error.to_dict(),
                status_code=error.status_code
            )
        else:
            self.logger.error(f"Unexpected error: {str(error)}", exc_info=True)
            api_error = APIError(
                message="An unexpected error occurred",
                code=APIErrorCode.INTERNAL_SERVER_ERROR,
                status_code=500
            )
            return APIResponse(
                data=api_error.to_dict(),
                status_code=api_error.status_code
            )