"""
Science Data Kit - Dropbox Extension
Selective Sync Module

This module provides functionality for configuring and managing selective
synchronization of Dropbox folders.
"""

import logging
import os
import json
from typing import Dict, Any, Optional, List, Union, Set
from pathlib import Path

from .connector import DropboxConnector
from .files import DropboxFileManager

logger = logging.getLogger(__name__)

class DropboxSelectiveSync:
    """
    Class for managing selective synchronization of Dropbox folders.

    This class provides methods for configuring which folders to sync and
    filtering file operations based on sync settings.
    """

    def __init__(
        self, 
        connector: DropboxConnector,
        config_path: Optional[str] = None
    ):
        """
        Initialize the selective sync manager.

        Args:
            connector: DropboxConnector instance for API access
            config_path: Path to the configuration file (created if not exists)
        """
        self.connector = connector
        self.file_manager = DropboxFileManager(connector)
        self.config_path = config_path or os.path.expanduser("~/.dropbox_selective_sync.json")
        self.included_paths = set()
        self.excluded_paths = set()
        self.sync_all = True

        # Load configuration if exists
        self._load_config()

    def _load_config(self):
        """
        Load selective sync configuration from file.
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)

                self.included_paths = set(config.get('included_paths', []))
                self.excluded_paths = set(config.get('excluded_paths', []))
                self.sync_all = config.get('sync_all', True)

                logger.info(f"Loaded selective sync configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading selective sync configuration: {e}")
            # Use defaults
            self.included_paths = set()
            self.excluded_paths = set()
            self.sync_all = True

    def _save_config(self):
        """
        Save selective sync configuration to file.
        """
        try:
            config = {
                'included_paths': list(self.included_paths),
                'excluded_paths': list(self.excluded_paths),
                'sync_all': self.sync_all
            }

            # Create directory if not exists
            os.makedirs(os.path.dirname(os.path.abspath(self.config_path)), exist_ok=True)

            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"Saved selective sync configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving selective sync configuration: {e}")

    def set_sync_all(self, sync_all: bool):
        """
        Set whether to sync all folders.

        Args:
            sync_all: Whether to sync all folders
        """
        self.sync_all = sync_all
        self._save_config()

    def include_path(self, path: str):
        """
        Include a path in selective sync.

        Args:
            path: Path to include
        """
        # Normalize path
        if not path.startswith('/'):
            path = f"/{path}"

        # Remove from excluded paths if present
        self.excluded_paths.discard(path)

        # Add to included paths
        self.included_paths.add(path)

        # Save configuration
        self._save_config()

        logger.info(f"Added {path} to selective sync included paths")

    def exclude_path(self, path: str):
        """
        Exclude a path from selective sync.

        Args:
            path: Path to exclude
        """
        # Normalize path
        if not path.startswith('/'):
            path = f"/{path}"

        # Remove from included paths if present
        self.included_paths.discard(path)

        # Add to excluded paths
        self.excluded_paths.add(path)

        # Save configuration
        self._save_config()

        logger.info(f"Added {path} to selective sync excluded paths")

    def reset(self):
        """
        Reset selective sync configuration to default.
        """
        self.included_paths = set()
        self.excluded_paths = set()
        self.sync_all = True

        # Save configuration
        self._save_config()

        logger.info("Reset selective sync configuration to default")

    def should_sync(self, path: str) -> bool:
        """
        Check if a path should be synced based on configuration.

        Args:
            path: Path to check

        Returns:
            True if the path should be synced, False otherwise
        """
        # Normalize path
        if not path.startswith('/'):
            path = f"/{path}"

        # If sync all and not explicitly excluded, sync
        if self.sync_all:
            return path not in self.excluded_paths

        # If not sync all, only sync if explicitly included
        return self._is_included(path)

    def _is_included(self, path: str) -> bool:
        """
        Check if a path is included in selective sync.

        Args:
            path: Path to check

        Returns:
            True if the path is included, False otherwise
        """
        # Check if path is directly included
        if path in self.included_paths:
            return True

        # Check if path is a child of an included path
        for included_path in self.included_paths:
            if path.startswith(included_path + '/'):
                return True

        return False

    def filter_paths(self, paths: List[str]) -> List[str]:
        """
        Filter a list of paths based on selective sync configuration.

        Args:
            paths: List of paths to filter

        Returns:
            Filtered list of paths
        """
        return [path for path in paths if self.should_sync(path)]

    def filter_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a list of items based on selective sync configuration.

        Args:
            items: List of items (with 'path' key) to filter

        Returns:
            Filtered list of items
        """
        return [item for item in items if self.should_sync(item.get('path', ''))]

    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get the current selective sync status.

        Returns:
            Dictionary with sync status information
        """
        return {
            'sync_all': self.sync_all,
            'included_paths': list(self.included_paths),
            'excluded_paths': list(self.excluded_paths)
        }

    def get_root_folders(self) -> List[Dict[str, Any]]:
        """
        Get a list of root folders for selective sync configuration.

        Returns:
            List of root folder metadata
        """
        try:
            # List root folders
            folders = self.file_manager.list_folder('/')

            # Filter to only folders
            folders = [f for f in folders if f.get('type') == 'folder']

            # Add sync status
            for folder in folders:
                path = folder.get('path', '')
                folder['sync_status'] = 'included' if path in self.included_paths else (
                    'excluded' if path in self.excluded_paths else 'default'
                )

            return folders
        except Exception as e:
            logger.error(f"Error getting root folders: {e}")
            return []
