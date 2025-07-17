"""
Template implementation of a filesystem plugin.

This module provides a template implementation of a filesystem plugin
that can be used as a starting point for creating new filesystem plugins.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from science_data_kit.core.plugins.config import (
    ConfigField,
    ConfigFieldType,
    PluginConfigSchema,
    create_default_config,
)
from science_data_kit.core.plugins.interfaces import FilesystemPluginInterface


class FilesystemPluginTemplate(FilesystemPluginInterface):
    """Template implementation of a filesystem plugin."""
    
    def __init__(self):
        """Initialize the plugin."""
        self._name = "filesystem_template"
        self._version = "1.0.0"
        self._description = "Template implementation of a filesystem plugin"
        self._is_initialized = False
        self._is_connected = False
        self._config = {}
        self._root_dir = None
        
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
                    name="root_directory",
                    field_type=ConfigFieldType.DIRECTORY_PATH,
                    description="Root directory for the filesystem plugin",
                    required=True,
                ),
                ConfigField(
                    name="create_if_missing",
                    field_type=ConfigFieldType.BOOLEAN,
                    description="Create the root directory if it doesn't exist",
                    required=False,
                    default=False,
                ),
                ConfigField(
                    name="read_only",
                    field_type=ConfigFieldType.BOOLEAN,
                    description="Whether the filesystem is read-only",
                    required=False,
                    default=False,
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
            return False
            
        self._config = config
        self._root_dir = Path(config["root_directory"])
        
        # Create the root directory if it doesn't exist and create_if_missing is True
        if not self._root_dir.exists() and config.get("create_if_missing", False):
            try:
                self._root_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                return False
                
        # Check if the root directory exists
        if not self._root_dir.exists() or not self._root_dir.is_dir():
            return False
            
        self._is_initialized = True
        return True
        
    def shutdown(self) -> bool:
        """
        Shut down the plugin and release any resources.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        if self._is_connected:
            self.disconnect()
            
        self._is_initialized = False
        return True
        
    @property
    def is_initialized(self) -> bool:
        """Check if the plugin is initialized."""
        return self._is_initialized
        
    @property
    def capabilities(self) -> Set[str]:
        """Get the plugin capabilities."""
        capabilities = {"filesystem", "browsable"}
        
        if not self._config.get("read_only", False):
            capabilities.update({"writable", "deletable", "creatable"})
            
        return capabilities
        
    def connect(self, config: Dict[str, Any]) -> None:
        """
        Establish connection with the filesystem.
        
        Args:
            config: Configuration dictionary for the connection
        """
        if not self._is_initialized:
            if not self.initialize(config):
                raise RuntimeError("Failed to initialize plugin")
                
        # For a filesystem plugin, connection is just checking if the root directory exists
        if not self._root_dir.exists() or not self._root_dir.is_dir():
            raise RuntimeError(f"Root directory {self._root_dir} does not exist or is not a directory")
            
        self._is_connected = True
        
    def disconnect(self) -> None:
        """Clean up connection."""
        self._is_connected = False
        
    def test_connection(self) -> bool:
        """
        Verify connection is working.
        
        Returns:
            True if connection is working, False otherwise
        """
        return self._is_connected and self._root_dir.exists() and self._root_dir.is_dir()
        
    @property
    def is_connected(self) -> bool:
        """
        Check if the connection is currently established.
        
        Returns:
            True if connected, False otherwise
        """
        return self._is_connected
        
    def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """
        List contents of a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            List of dictionaries containing file/directory information
        """
        if not self._is_connected:
            raise RuntimeError("Not connected")
            
        full_path = self._get_full_path(path)
        
        if not full_path.exists() or not full_path.is_dir():
            raise FileNotFoundError(f"Directory {path} does not exist")
            
        result = []
        
        for item in full_path.iterdir():
            item_info = {
                "name": item.name,
                "path": str(item.relative_to(self._root_dir)),
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else None,
                "modified": item.stat().st_mtime,
            }
            result.append(item_info)
            
        return result
        
    def read_file(self, path: str) -> bytes:
        """
        Read a file.
        
        Args:
            path: Path to the file
            
        Returns:
            File contents as bytes
        """
        if not self._is_connected:
            raise RuntimeError("Not connected")
            
        full_path = self._get_full_path(path)
        
        if not full_path.exists() or not full_path.is_file():
            raise FileNotFoundError(f"File {path} does not exist")
            
        return full_path.read_bytes()
        
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
            raise RuntimeError("Not connected")
            
        if self._config.get("read_only", False):
            raise PermissionError("Filesystem is read-only")
            
        full_path = self._get_full_path(path)
        
        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            full_path.write_bytes(content)
            return True
        except Exception:
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
            raise RuntimeError("Not connected")
            
        if self._config.get("read_only", False):
            raise PermissionError("Filesystem is read-only")
            
        full_path = self._get_full_path(path)
        
        if not full_path.exists() or not full_path.is_file():
            return False
            
        try:
            full_path.unlink()
            return True
        except Exception:
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
            raise RuntimeError("Not connected")
            
        if self._config.get("read_only", False):
            raise PermissionError("Filesystem is read-only")
            
        full_path = self._get_full_path(path)
        
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
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
            raise RuntimeError("Not connected")
            
        if self._config.get("read_only", False):
            raise PermissionError("Filesystem is read-only")
            
        full_path = self._get_full_path(path)
        
        if not full_path.exists() or not full_path.is_dir():
            return False
            
        try:
            if recursive:
                import shutil
                shutil.rmtree(full_path)
            else:
                full_path.rmdir()
            return True
        except Exception:
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
            raise RuntimeError("Not connected")
            
        full_path = self._get_full_path(path)
        return full_path.exists() and full_path.is_file()
        
    def directory_exists(self, path: str) -> bool:
        """
        Check if a directory exists.
        
        Args:
            path: Path to the directory
            
        Returns:
            True if the directory exists, False otherwise
        """
        if not self._is_connected:
            raise RuntimeError("Not connected")
            
        full_path = self._get_full_path(path)
        return full_path.exists() and full_path.is_dir()
        
    def _get_full_path(self, path: str) -> Path:
        """
        Get the full path for a relative path.
        
        Args:
            path: Relative path
            
        Returns:
            Full path
        """
        # Normalize the path to prevent directory traversal attacks
        normalized_path = os.path.normpath(path)
        
        # Ensure the path doesn't start with .. to prevent escaping the root directory
        if normalized_path.startswith(".."):
            raise ValueError("Path cannot start with '..'")
            
        return self._root_dir / normalized_path