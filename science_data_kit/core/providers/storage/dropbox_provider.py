"""
Dropbox Provider for Science Data Kit

This module provides a Dropbox provider for accessing CSV and Excel files
stored in Dropbox.

This is a compatibility layer that uses the new DropboxPlugin under the hood
while maintaining the old interface for backward compatibility.
"""

import io
import os
import pandas as pd
import warnings
from typing import Dict, List, Any, Optional
from dropbox import Dropbox
from dropbox.exceptions import AuthError, ApiError
from dropbox.files import FileMetadata, FolderMetadata

from ...providers.registry import BaseProvider
from science_data_kit.core.connections.manager import manager
from science_data_kit.plugins.cloud_storage.dropbox.dropbox_plugin import DropboxPlugin


class DropboxProvider(BaseProvider):
    """
    Dropbox file provider for CSV/Excel data access

    This is a compatibility layer that uses the new DropboxPlugin under the hood
    while maintaining the old interface for backward compatibility.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Dropbox provider.

        Args:
            config: Configuration dictionary containing Dropbox access token
        """
        super().__init__(config)
        self.client = None
        self._plugin = None

        # Emit deprecation warning
        warnings.warn(
            "DropboxProvider is deprecated and will be removed in a future version. "
            "Please use the new plugin architecture instead. "
            "See docs/guides/plugin_migration_guide.md for migration instructions.",
            DeprecationWarning,
            stacklevel=2
        )

    async def initialize(self) -> bool:
        """
        Initialize Dropbox API connection using access token.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Get access token from config
            access_token = self.config.get("access_token")
            app_key = self.config.get("app_key")
            app_secret = self.config.get("app_secret")
            refresh_token = self.config.get("refresh_token")

            # Check if we have the required credentials
            if not access_token and not (app_key and app_secret and refresh_token):
                print("Dropbox credentials not found in configuration")
                return False

            # Initialize the plugin
            try:
                # Try to get the plugin from the manager
                self._plugin = manager.get_plugin_instance("dropbox")
            except Exception:
                # If the plugin is not registered, create a new instance
                self._plugin = DropboxPlugin()

            # Convert old config format to new format
            plugin_config = {
                "app_key": app_key or self.config.get("app_key", ""),
                "app_secret": app_secret or self.config.get("app_secret", ""),
                "refresh_token": refresh_token or self.config.get("refresh_token", ""),
                "root_path": self.config.get("root_path", "")
            }

            # Connect to the plugin
            self._plugin.connect(plugin_config)

            # For backward compatibility, create a client if access_token is provided
            if access_token:
                self.client = Dropbox(access_token)

            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Error initializing Dropbox provider: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """
        Verify Dropbox connection is working.

        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized or not self._plugin:
            return False

        try:
            # Use the plugin's test_connection method
            return self._plugin.test_connection()
        except Exception as e:
            print(f"Dropbox health check failed: {str(e)}")
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return provider capabilities.

        Returns:
            Dictionary of provider capabilities
        """
        return {
            "data_types": ["files", "csv", "excel"],
            "real_time": False,
            "formats": ["csv", "xlsx", "xls"],
            "max_size": "350GB"  # Dropbox file size limit
        }

    async def list_files(self, folder_path: str = "", file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        List CSV/Excel files in Dropbox folder.

        Args:
            folder_path: Path to the folder in Dropbox
            file_types: List of file extensions to filter by (e.g., ["csv", "xlsx"])

        Returns:
            List of file metadata dictionaries
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Dropbox provider not initialized")

        if file_types is None:
            file_types = ["csv", "xlsx", "xls"]

        try:
            # Ensure folder path starts with a slash
            if folder_path and not folder_path.startswith("/"):
                folder_path = f"/{folder_path}"

            # Use the plugin's list_directory method
            directory_contents = self._plugin.list_directory(folder_path)

            # Filter and convert to the old format
            files = []
            for item in directory_contents:
                if item["is_dir"]:
                    # Include directories for navigation
                    files.append({
                        "id": item["path"],  # Use path as ID since we don't have the actual ID
                        "name": item["name"],
                        "path": item["path"],
                        "type": "folder"
                    })
                else:
                    # Check if file has one of the specified extensions
                    file_ext = os.path.splitext(item["name"])[1].lower().lstrip(".")
                    if file_ext in file_types:
                        files.append({
                            "id": item["path"],  # Use path as ID since we don't have the actual ID
                            "name": item["name"],
                            "path": item["path"],
                            "size": item["size"],
                            "modified": item["modified"],
                            "type": file_ext
                        })

            return files

        except Exception as e:
            print(f"Error listing Dropbox files: {str(e)}")
            raise

    async def download_file_data(self, file_path: str) -> pd.DataFrame:
        """
        Download file and return as pandas DataFrame.

        Args:
            file_path: Path to the file in Dropbox

        Returns:
            Pandas DataFrame containing the file data
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Dropbox provider not initialized")

        try:
            # Ensure file path starts with a slash
            if not file_path.startswith("/"):
                file_path = f"/{file_path}"

            # Use the plugin's read_file method
            content = self._plugin.read_file(file_path)

            # Detect file type
            file_ext = os.path.splitext(file_path)[1].lower()

            # Parse with appropriate pandas function
            if file_ext == ".csv":
                return pd.read_csv(io.BytesIO(content))
            elif file_ext in [".xlsx", ".xls"]:
                return pd.read_excel(io.BytesIO(content))
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

        except Exception as e:
            print(f"Error downloading file from Dropbox: {str(e)}")
            raise

    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata without downloading.

        Args:
            file_path: Path to the file in Dropbox

        Returns:
            Dictionary containing file metadata
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Dropbox provider not initialized")

        try:
            # Ensure file path starts with a slash
            if not file_path.startswith("/"):
                file_path = f"/{file_path}"

            # Check if file exists using the plugin
            if not self._plugin.file_exists(file_path):
                raise ValueError(f"Path does not point to a file: {file_path}")

            # Get directory listing to find the file
            directory_path = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)

            directory_contents = self._plugin.list_directory(directory_path)

            # Find the file in the directory contents
            for item in directory_contents:
                if not item["is_dir"] and item["name"] == file_name:
                    file_ext = os.path.splitext(item["name"])[1].lower().lstrip(".")
                    return {
                        "id": item["path"],  # Use path as ID since we don't have the actual ID
                        "name": item["name"],
                        "path": item["path"],
                        "size": item["size"],
                        "modified": item["modified"],
                        "type": file_ext
                    }

            raise ValueError(f"File not found: {file_path}")

        except Exception as e:
            print(f"Error getting file info from Dropbox: {str(e)}")
            raise
