"""
Local Storage Provider for Science Data Kit

This module provides a local storage provider for accessing CSV and Excel files
stored on the local file system or network mountpoints.

This is a compatibility layer that uses the new LocalStoragePlugin under the hood
while maintaining the old interface for backward compatibility.
"""

import os
import io
import pandas as pd
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import warnings

from ...providers.registry import BaseProvider
from science_data_kit.core.connections.manager import manager
from science_data_kit.plugins.local.filesystem.local_storage_plugin import LocalStoragePlugin


class LocalStorageProvider(BaseProvider):
    """
    Local storage file provider for CSV/Excel data access

    This is a compatibility layer that uses the new LocalStoragePlugin under the hood
    while maintaining the old interface for backward compatibility.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the local storage provider.

        Args:
            config: Configuration dictionary containing base_path and optional allowed_paths
                   base_path: Root directory for file access
                   allowed_paths: List of allowed paths (for security)
        """
        super().__init__(config)
        self.base_path = None
        self.allowed_paths = []
        self._plugin = None

        # Emit deprecation warning
        warnings.warn(
            "LocalStorageProvider is deprecated and will be removed in a future version. "
            "Please use the new plugin architecture instead. "
            "See docs/guides/plugin_migration_guide.md for migration instructions.",
            DeprecationWarning,
            stacklevel=2
        )

    async def initialize(self) -> bool:
        """
        Initialize local storage access.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Get base path from config
            base_path = self.config.get("base_path")
            if not base_path:
                print("Base path not found in configuration")
                return False

            # Convert to absolute path and check if it exists
            base_path = os.path.abspath(os.path.expanduser(base_path))
            if not os.path.exists(base_path):
                print(f"Base path does not exist: {base_path}")
                return False

            self.base_path = base_path

            # Get allowed paths (optional)
            allowed_paths = self.config.get("allowed_paths", [])
            if allowed_paths:
                self.allowed_paths = [os.path.abspath(os.path.expanduser(p)) for p in allowed_paths]

            # Initialize the plugin
            try:
                # Try to get the plugin from the manager
                self._plugin = manager.get_plugin_instance("local_storage")
            except Exception:
                # If the plugin is not registered, create a new instance
                self._plugin = LocalStoragePlugin()

            # Convert old config format to new format
            plugin_config = {
                "root_directory": self.base_path,
                "allowed_paths": self.allowed_paths,
                "read_only": self.config.get("read_only", False),
                "create_if_missing": self.config.get("create_if_missing", False)
            }

            # Connect to the plugin
            self._plugin.connect(plugin_config)

            self.is_initialized = True
            return True

        except Exception as e:
            print(f"Error initializing local storage provider: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """
        Verify local storage access is working.

        Returns:
            True if the access is healthy, False otherwise
        """
        if not self.is_initialized or not self._plugin:
            return False

        try:
            # Use the plugin's test_connection method
            return self._plugin.test_connection()
        except Exception as e:
            print(f"Local storage health check failed: {str(e)}")
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return provider capabilities.

        Returns:
            Dictionary of provider capabilities
        """
        return {
            "data_types": ["files", "csv", "excel"],
            "real_time": True,
            "formats": ["csv", "xlsx", "xls"],
            "max_size": "system-dependent"
        }

    def _is_path_allowed(self, path: str) -> bool:
        """
        Check if a path is allowed based on security settings.

        Args:
            path: Path to check

        Returns:
            True if the path is allowed, False otherwise
        """
        # Always allow paths under base_path
        if os.path.commonpath([path, self.base_path]) == self.base_path:
            return True

        # Check against allowed_paths if specified
        if self.allowed_paths:
            for allowed_path in self.allowed_paths:
                if os.path.commonpath([path, allowed_path]) == allowed_path:
                    return True
            return False

        # If no allowed_paths specified, only allow paths under base_path
        return False

    def _get_absolute_path(self, relative_path: str) -> str:
        """
        Convert a relative path to an absolute path.

        Args:
            relative_path: Path relative to base_path

        Returns:
            Absolute path
        """
        # If path is empty, use base_path
        if not relative_path:
            return self.base_path

        # Join with base_path if not already absolute
        if os.path.isabs(relative_path):
            path = relative_path
        else:
            path = os.path.join(self.base_path, relative_path)

        # Normalize path
        return os.path.abspath(path)

    async def list_files(self, folder_path: str = "", file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        List CSV/Excel files in local folder.

        Args:
            folder_path: Path to the folder (relative to base_path)
            file_types: List of file extensions to filter by (e.g., ["csv", "xlsx"])

        Returns:
            List of file metadata dictionaries
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Local storage provider not initialized")

        if file_types is None:
            file_types = ["csv", "xlsx", "xls"]

        try:
            # Use the plugin's list_directory method
            directory_contents = self._plugin.list_directory(folder_path)

            # Filter and convert to the old format
            files = []
            for item in directory_contents:
                if item["is_dir"]:
                    # Include directories for navigation
                    files.append({
                        "id": item["path"],
                        "name": item["name"],
                        "path": item["path"],
                        "type": "folder"
                    })
                else:
                    # Check if file has one of the specified extensions
                    file_ext = os.path.splitext(item["name"])[1].lower().lstrip(".")
                    if file_ext in file_types:
                        files.append({
                            "id": item["path"],
                            "name": item["name"],
                            "path": item["path"],
                            "size": item["size"],
                            "modified": item["modified"],
                            "type": file_ext
                        })

            return files

        except Exception as e:
            print(f"Error listing local files: {str(e)}")
            raise

    async def download_file_data(self, file_path: str) -> pd.DataFrame:
        """
        Read file and return as pandas DataFrame.

        Args:
            file_path: Path to the file (relative to base_path)

        Returns:
            Pandas DataFrame containing the file data
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Local storage provider not initialized")

        try:
            # Use the plugin's read_file method
            file_content = self._plugin.read_file(file_path)

            # Detect file type
            file_ext = os.path.splitext(file_path)[1].lower()

            # Parse with appropriate pandas function
            if file_ext == '.csv':
                return pd.read_csv(io.BytesIO(file_content))
            elif file_ext in ['.xlsx', '.xls']:
                return pd.read_excel(io.BytesIO(file_content))
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

        except Exception as e:
            print(f"Error reading local file: {str(e)}")
            raise

    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata without reading the file.

        Args:
            file_path: Path to the file (relative to base_path)

        Returns:
            Dictionary containing file metadata
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Local storage provider not initialized")

        try:
            # Check if file exists using the plugin
            if not self._plugin.file_exists(file_path):
                raise FileNotFoundError(f"File does not exist: {file_path}")

            # Get absolute path
            abs_path = self._get_absolute_path(file_path)

            # Get file stats
            stat = os.stat(abs_path)

            # Get relative path
            rel_path = os.path.relpath(abs_path, self.base_path)

            return {
                "id": rel_path,
                "name": os.path.basename(abs_path),
                "path": rel_path,
                "size": stat.st_size,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "type": os.path.splitext(abs_path)[1].lower().lstrip(".")
            }

        except Exception as e:
            print(f"Error getting local file info: {str(e)}")
            raise
