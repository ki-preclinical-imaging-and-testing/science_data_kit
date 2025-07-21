"""
Authentication strategies for Science Data Kit connections.

This module provides authentication strategies for different types of connections,
such as OAuth2, API keys, and username/password credentials, as well as a unified
authentication management interface for cloud storage providers.
"""

from .oauth2 import OAuth2Mixin
from .api_key import APIKeyMixin
from .credentials import CredentialsMixin
from .cloud_storage import (
    CloudStorageAuthProvider,
    DropboxAuthProvider,
    MSGraphAuthProvider,
    CloudStorageAuthManager,
    auth_manager as cloud_storage_auth_manager
)

__all__ = [
    "OAuth2Mixin",
    "APIKeyMixin",
    "CredentialsMixin",
    "CloudStorageAuthProvider",
    "DropboxAuthProvider",
    "MSGraphAuthProvider",
    "CloudStorageAuthManager",
    "cloud_storage_auth_manager",
]
