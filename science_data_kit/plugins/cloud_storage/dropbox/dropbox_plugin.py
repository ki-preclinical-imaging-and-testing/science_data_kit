"""
Dropbox Plugin for Science Data Kit.

This module provides a plugin for accessing files on Dropbox.
It implements the FilesystemPluginInterface and provides methods for
file and directory operations using the Dropbox API.
"""

import os
import logging
from typing import Any, Dict, List, Optional, Set
from datetime import datetime

import dropbox
from dropbox import Dropbox
from dropbox.exceptions import AuthError, ApiError

from science_data_kit.core.plugins.config import (
    ConfigField,
    ConfigFieldType,
    PluginConfigSchema,
    create_default_config,
)
from science_data_kit.core.plugins.interfaces import FilesystemPluginInterface
from science_data_kit.core.integrations.plugin_architecture import register_plugin
from science_data_kit_extensions.dropbox.connector import DropboxConnector
from science_data_kit_extensions.dropbox.files import DropboxFileManager

logger = logging.getLogger(__name__)


@register_plugin
class DropboxPlugin(FilesystemPluginInterface):
    """
    Plugin for accessing files on Dropbox.
    
    This plugin provides access to files and directories on Dropbox,
    with authentication and connection management.
    """
    
    def __init__(self):
        """Initialize the plugin."""
        self._name = "dropbox"
        self._version = "1.0.0"
        self._description = "Plugin for accessing files on Dropbox"
        self._is_initialized = False
        self._is_connected = False
        self._config = {}
        self._connector = None
        self._file_manager = None
        
    @property
    def name(self) -> str:
        """Get the plugin name."""
        return self._name
        
    @property
    def version(self) -> str:
        """Get the plugin version."""
        return self._version
        
    @property
    def description(self) -> str:
        """Get the plugin description."""
        return self._description
        
    @property
    def config_schema(self) -> PluginConfigSchema:
        """Get the plugin configuration schema."""
        return PluginConfigSchema(
            fields=[
                ConfigField(
                    name="app_key",
                    field_type=ConfigFieldType.STRING,
                    description="Dropbox API app key",
                    required=True,
                ),
                ConfigField(
                    name="app_secret",
                    field_type=ConfigFieldType.STRING,
                    description="Dropbox API app secret",
                    required=True,
                ),
                ConfigField(
                    name="refresh_token",
                    field_type=ConfigFieldType.STRING,
                    description="OAuth2 refresh token for authentication",
                    required=True,
                ),
                ConfigField(
                    name="root_path",
                    field_type=ConfigFieldType.STRING,
                    description="Root path in Dropbox (empty for root)",
                    required=False,
                    default="",
                ),
            ],
            version="1.0",
        )
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate a configuration against this plugin's schema.
        
        Args:
            config: The configuration to validate
            
        Returns:
            True if the configuration is valid, False otherwise
        """
        return self.config_schema.validate_config(config)
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with the given configuration.
        
        Args:
            config: The configuration to use
            
        Returns:
            True if initialization was successful, False otherwise
        """
        if not self.validate_config(config):
            logger.error("Invalid configuration for Dropbox plugin")
            return False
            
        self._config = config
        
        try:
            # Create the connector
            self._connector = DropboxConnector(
                app_key=config["app_key"],
                app_secret=config["app_secret"],
                refresh_token=config["refresh_token"]
            )
            
            self._is_initialized = True
            logger.info("Dropbox plugin initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Dropbox plugin: {e}")
            self._is_initialized = False
            return False
        
    def shutdown(self) -> bool:
        """
        Shut down the plugin and release any resources.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        if self._is_connected:
            self.disconnect()
            
        self._connector = None
        self._file_manager = None
        self._is_initialized = False
        logger.info("Dropbox plugin shut down")
        return True
        
    @property
    def is_initialized(self) -> bool:
        """Check if the plugin is initialized."""
        return self._is_initialized
        
    @property
    def capabilities(self) -> Set[str]:
        """Get the plugin capabilities."""
        capabilities = {"filesystem", "browsable", "searchable", "writable", "deletable", "creatable"}
        return capabilities
        
    def connect(self, config: Dict[str, Any]) -> None:
        """
        Establish connection with Dropbox.
        
        Args:
            config: Configuration dictionary for the connection
        """
        if not self._is_initialized:
            if not self.initialize(config):
                raise RuntimeError("Failed to initialize Dropbox plugin")
                
        try:
            # Connect to Dropbox
            if not self._connector.connect():
                raise RuntimeError("Failed to connect to Dropbox API")
                
            # Create the file manager
            self._file_manager = DropboxFileManager(self._connector)
            
            self._is_connected = True
            logger.info("Connected to Dropbox API")
        except Exception as e:
            logger.error(f"Error connecting to Dropbox: {e}")
            self._is_connected = False
            raise RuntimeError(f"Failed to connect to Dropbox: {e}")
        
    def disconnect(self) -> None:
        """Clean up connection."""
        if self._connector:
            self._connector.disconnect()
            
        self._file_manager = None
        self._is_connected = False
        logger.info("Disconnected from Dropbox API")
        
    def test_connection(self) -> bool:
        """
        Verify connection is working.
        
        Returns:
            True if connection is working, False otherwise
        """
        if not self._is_connected or not self._connector:
            return False
            
        try:
            return self._connector.is_connected()
        except Exception:
            return False
        
    @property
    def is_connected(self) -> bool:
        """
        Check if the connection is currently established.
        
        Returns:
            True if connected, False otherwise
        """
        return self._is_connected and self._connector and self._connector.is_connected()
        
    def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """
        List contents of a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            List of dictionaries containing file/directory information
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Dropbox")
            
        try:
            # Combine with root_path if specified
            full_path = self._get_full_path(path)
            
            # List the directory
            entries = self._file_manager.list_folder(full_path)
            
            # Format the results to match the expected interface
            result = []
            for entry in entries:
                item_info = {
                    "name": entry["name"],
                    "path": self._strip_root_path(entry["path"]),
                    "is_dir": entry["type"] == "folder",
                    "size": entry.get("size"),
                    "modified": entry.get("modified"),
                }
                result.append(item_info)
                
            return result
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            raise
        
    def read_file(self, path: str) -> bytes:
        """
        Read a file.
        
        Args:
            path: Path to the file
            
        Returns:
            File contents as bytes
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Dropbox")
            
        try:
            # Combine with root_path if specified
            full_path = self._get_full_path(path)
            
            # Download the file
            content, _ = self._file_manager.download_file(full_path)
            return content
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            raise
        
    def write_file(self, path: str, content: bytes) -> bool:
        """
        Write to a file.
        
        Args:
            path: Path to the file
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Dropbox")
            
        try:
            # Combine with root_path if specified
            full_path = self._get_full_path(path)
            
            # Upload the file
            self._file_manager.upload_file(content, full_path, overwrite=True)
            return True
        except Exception as e:
            logger.error(f"Error writing file {path}: {e}")
            return False
        
    def delete_file(self, path: str) -> bool:
        """
        Delete a file.
        
        Args:
            path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Dropbox")
            
        try:
            # Combine with root_path if specified
            full_path = self._get_full_path(path)
            
            # Delete the file
            self._file_manager.delete(full_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting file {path}: {e}")
            return False
        
    def create_directory(self, path: str) -> bool:
        """
        Create a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Dropbox")
            
        try:
            # Combine with root_path if specified
            full_path = self._get_full_path(path)
            
            # Create the directory
            self._file_manager.create_folder(full_path)
            return True
        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")
            return False
        
    def delete_directory(self, path: str, recursive: bool = False) -> bool:
        """
        Delete a directory.
        
        Args:
            path: Path to the directory
            recursive: Whether to delete recursively
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Dropbox")
            
        try:
            # Combine with root_path if specified
            full_path = self._get_full_path(path)
            
            # Delete the directory (Dropbox API always deletes recursively)
            self._file_manager.delete(full_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting directory {path}: {e}")
            return False
        
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            path: Path to the file
            
        Returns:
            True if the file exists, False otherwise
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Dropbox")
            
        try:
            # Combine with root_path if specified
            full_path = self._get_full_path(path)
            
            # Get metadata to check if file exists
            metadata = self._file_manager.get_metadata(full_path)
            return metadata["type"] == "file"
        except Exception:
            return False
        
    def directory_exists(self, path: str) -> bool:
        """
        Check if a directory exists.
        
        Args:
            path: Path to the directory
            
        Returns:
            True if the directory exists, False otherwise
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Dropbox")
            
        try:
            # Combine with root_path if specified
            full_path = self._get_full_path(path)
            
            # Get metadata to check if directory exists
            metadata = self._file_manager.get_metadata(full_path)
            return metadata["type"] == "folder"
        except Exception:
            return False
        
    def _get_full_path(self, path: str) -> str:
        """
        Get the full path by combining with root_path if specified.
        
        Args:
            path: Path to combine
            
        Returns:
            Full path
        """
        root_path = self._config.get("root_path", "")
        
        # Normalize paths
        if root_path and not root_path.startswith("/"):
            root_path = f"/{root_path}"
            
        if path and not path.startswith("/"):
            path = f"/{path}"
            
        # Combine paths
        if not root_path:
            return path
        elif not path or path == "/":
            return root_path
        else:
            # Ensure no double slashes
            if root_path.endswith("/") and path.startswith("/"):
                return f"{root_path}{path[1:]}"
            elif not root_path.endswith("/") and not path.startswith("/"):
                return f"{root_path}/{path}"
            else:
                return f"{root_path}{path}"
                
    def _strip_root_path(self, path: str) -> str:
        """
        Strip the root_path from a full path.
        
        Args:
            path: Full path
            
        Returns:
            Path relative to root_path
        """
        root_path = self._config.get("root_path", "")
        
        # Normalize root_path
        if root_path and not root_path.startswith("/"):
            root_path = f"/{root_path}"
            
        # Strip root_path
        if root_path and path.startswith(root_path):
            relative_path = path[len(root_path):]
            if not relative_path:
                return "/"
            if not relative_path.startswith("/"):
                relative_path = f"/{relative_path}"
            return relative_path
        else:
            return path