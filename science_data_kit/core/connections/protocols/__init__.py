"""
Protocol definitions for Science Data Kit connections.

This module provides abstract base classes for different types of connection protocols,
defining the interfaces that specific plugin implementations must follow.
"""

from .base import ConnectionProtocol
from .filesystem import FilesystemProtocol
from .database import DatabaseProtocol
from .api import APIProtocol
from .object_storage import ObjectStorageProtocol

__all__ = [
    "ConnectionProtocol",
    "FilesystemProtocol",
    "DatabaseProtocol",
    "APIProtocol",
    "ObjectStorageProtocol",
]