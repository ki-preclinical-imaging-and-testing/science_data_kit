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
from .webhooks import DropboxWebhookHandler
from .conflict import DropboxConflictResolver, ConflictResolutionStrategy
from .status import DropboxSyncStatus, SyncStatus, SyncOperation
from .selective_sync import DropboxSelectiveSync
from .file_requests import DropboxFileRequestManager
from .comments import DropboxCommentManager
from .versions import DropboxVersionManager
from .offline import DropboxOfflineDetector, ConnectionStatus

__version__ = "0.3.0"

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
    'DropboxSyncStatus',
    'SyncStatus',
    'SyncOperation',
    'DropboxConflictResolver',
    'ConflictResolutionStrategy',
    'DropboxSelectiveSync',

    # Team components
    'DropboxTeamManager',

    # Sharing components
    'DropboxSharingManager',
    'DropboxFileRequestManager',
    'DropboxCommentManager',
    'DropboxVersionManager',

    # Webhook components
    'DropboxWebhookHandler',

    # Offline mode components
    'DropboxOfflineDetector',
    'ConnectionStatus',

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
