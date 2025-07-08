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

__version__ = "0.1.0"

__all__ = [
    'DropboxConnector',
    'DropboxFileManager',
    'DropboxFile',
    'DropboxFolder',
    'DropboxNeo4jIntegration',
    'create_entities_from_dropbox_items',
    'validate_dropbox_file',
    'validate_dropbox_folder'
]
