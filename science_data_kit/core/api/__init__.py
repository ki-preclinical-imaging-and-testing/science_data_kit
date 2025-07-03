"""
API Layer for Science Data Kit

This package provides a comprehensive API layer for the Science Data Kit,
allowing external systems and applications to interact with the SDK's
functionality through a standardized interface.

The API layer includes:
- RESTful API endpoints for core SDK functionality
- Authentication and authorization mechanisms
- API documentation using OpenAPI/Swagger
- Client libraries for different programming languages

Components:
- base: Base classes and utilities for the API layer
- auth: Authentication and authorization mechanisms
- endpoints: RESTful API endpoints
- docs: API documentation
- clients: Client libraries for different programming languages
"""

from .base import APIBase, APIError, APIResponse
from .auth import APIAuth, APIToken
from .endpoints import register_endpoints

__all__ = [
    'APIBase',
    'APIError',
    'APIResponse',
    'APIAuth',
    'APIToken',
    'register_endpoints',
]