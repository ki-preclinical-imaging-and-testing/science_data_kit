"""
Authentication strategies for Science Data Kit connections.

This module provides authentication strategies for different types of connections,
such as OAuth2, API keys, and username/password credentials.
"""

from .oauth2 import OAuth2Mixin
from .api_key import APIKeyMixin
from .credentials import CredentialsMixin

__all__ = [
    "OAuth2Mixin",
    "APIKeyMixin",
    "CredentialsMixin",
]