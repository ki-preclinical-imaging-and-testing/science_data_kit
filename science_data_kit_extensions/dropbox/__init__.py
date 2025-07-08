"""
Science Data Kit - Dropbox Extension

This extension provides integration with Dropbox for the Science Data Kit.
It enables access to files and folders stored in Dropbox, supporting data
import, export, and synchronization.
"""

from .connector import DropboxConnector
from .files import DropboxFileManager
from .entities import (
    DropboxFile,
    DropboxFolder,
    create_entities_from_dropbox_items,
    validate_dropbox_file,
    validate_dropbox_folder
)
from .neo4j import DropboxNeo4jIntegration
from .sync import DropboxChangeTracker, DropboxSyncService
from .teams import DropboxTeamManager
from .sharing import DropboxSharingManager
from .error_handling import (
    DropboxErrorHandler,
    with_retry,
    DropboxApiException,
    DropboxRateLimitException,
    DropboxNetworkException,
    DropboxAuthException,
    DropboxServerException,
    DropboxClientException
)

__version__ = "0.2.0"

__all__ = [
    # Core components
    'DropboxConnector',
    'DropboxFileManager',
    'DropboxFile',
    'DropboxFolder',
    'DropboxNeo4jIntegration',
    'create_entities_from_dropbox_items',
    'validate_dropbox_file',
    'validate_dropbox_folder',

    # Sync components
    'DropboxChangeTracker',
    'DropboxSyncService',

    # Team components
    'DropboxTeamManager',

    # Sharing components
    'DropboxSharingManager',

    # Error handling components
    'DropboxErrorHandler',
    'with_retry',
    'DropboxApiException',
    'DropboxRateLimitException',
    'DropboxNetworkException',
    'DropboxAuthException',
    'DropboxServerException',
    'DropboxClientException'
]
