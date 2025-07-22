"""
Globus plugin for Science Data Kit.

This module provides a plugin for Globus, implementing the FilesystemPluginInterface
to enable seamless connectivity with Globus endpoints.
"""

import os
import logging
from typing import Any, Dict, List, Optional, Set
from datetime import datetime

# Globus SDK imports
try:
    import globus_sdk
    GLOBUS_SDK_AVAILABLE = True
except ImportError:
    GLOBUS_SDK_AVAILABLE = False
    logging.warning("Globus SDK not available. Install with 'pip install globus-sdk'")

from science_data_kit.core.plugins.config import (
    ConfigField,
    ConfigFieldType,
    PluginConfigSchema,
    create_default_config,
)
from science_data_kit.core.plugins.interfaces import FilesystemPluginInterface
from science_data_kit.core.integrations.plugin_architecture import register_plugin
from science_data_kit_extensions.globus.connector import GlobusConnector
from science_data_kit_extensions.globus.files import GlobusFileManager


class GlobusPlugin(FilesystemPluginInterface):
    """
    Plugin for Globus integration with Science Data Kit.
    
    This plugin enables connectivity with Globus endpoints, following the
    established plugin architecture patterns used for other cloud storage
    integrations.
    """
    
    def __init__(self):
        """Initialize the Globus plugin."""
        self.logger = logging.getLogger(__name__)
        self.connector = None
        self.file_manager = None
        self.config = None
        self.current_endpoint_id = None
        self.current_path = "/"
        self._initialized = False
    
    def name(self) -> str:
        """Return the name of the plugin."""
        return "globus"
    
    def version(self) -> str:
        """Return the version of the plugin."""
        return "0.1.0"
    
    def description(self) -> str:
        """Return the description of the plugin."""
        return "Globus integration for Science Data Kit"
    
    def config_schema(self) -> PluginConfigSchema:
        """
        Define the configuration schema for the plugin.
        
        Returns:
            PluginConfigSchema: Configuration schema
        """
        schema = PluginConfigSchema(
            fields=[
                ConfigField(
                    name="client_id",
                    display_name="Client ID",
                    field_type=ConfigFieldType.STRING,
                    description="Globus Client ID",
                    required=True,
                ),
                ConfigField(
                    name="client_secret",
                    display_name="Client Secret",
                    field_type=ConfigFieldType.PASSWORD,
                    description="Globus Client Secret",
                    required=False,
                ),
                ConfigField(
                    name="refresh_token",
                    display_name="Refresh Token",
                    field_type=ConfigFieldType.PASSWORD,
                    description="Globus Refresh Token",
                    required=False,
                ),
                ConfigField(
                    name="default_endpoint_id",
                    display_name="Default Endpoint ID",
                    field_type=ConfigFieldType.STRING,
                    description="Default Globus Endpoint ID",
                    required=False,
                ),
            ],
            sections=[],
        )
        return schema
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate the configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary with validation errors
        """
        errors = {}
        
        if not config.get("client_id"):
            errors["client_id"] = ["Client ID is required"]
        
        if not config.get("refresh_token") and not config.get("client_secret"):
            errors["auth"] = ["Either Refresh Token or Client Secret is required for authentication"]
        
        return errors
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with the provided configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if not GLOBUS_SDK_AVAILABLE:
            self.logger.error("Globus SDK not available. Install with 'pip install globus-sdk'")
            return False
        
        try:
            self.config = config
            
            # Create the connector
            self.connector = GlobusConnector(
                client_id=config.get("client_id"),
                client_secret=config.get("client_secret"),
                refresh_token=config.get("refresh_token"),
            )
            
            # Create the file manager
            self.file_manager = GlobusFileManager(self.connector)
            
            # Set the default endpoint if provided
            if config.get("default_endpoint_id"):
                self.current_endpoint_id = config.get("default_endpoint_id")
            
            self._initialized = True
            self.logger.info("Globus plugin initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing Globus plugin: {str(e)}")
            return False
    
    def shutdown(self) -> bool:
        """
        Shutdown the plugin.
        
        Returns:
            bool: True if shutdown was successful, False otherwise
        """
        try:
            if self.connector:
                self.connector.disconnect()
            
            self.connector = None
            self.file_manager = None
            self.config = None
            self._initialized = False
            
            self.logger.info("Globus plugin shutdown successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error shutting down Globus plugin: {str(e)}")
            return False
    
    def is_initialized(self) -> bool:
        """
        Check if the plugin is initialized.
        
        Returns:
            bool: True if initialized, False otherwise
        """
        return self._initialized
    
    def capabilities(self) -> Set[str]:
        """
        Return the capabilities of the plugin.
        
        Returns:
            Set of capability strings
        """
        return {"filesystem", "search", "transfer"}
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        Connect to Globus services.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            bool: True if connection was successful, False otherwise
        """
        if not self._initialized:
            self.logger.error("Plugin not initialized")
            return False
        
        try:
            # Update config if provided
            if config:
                self.config.update(config)
                
                # Update connector with new config
                if self.connector:
                    self.connector.client_id = self.config.get("client_id", self.connector.client_id)
                    self.connector.client_secret = self.config.get("client_secret", self.connector.client_secret)
                    self.connector.refresh_token = self.config.get("refresh_token", self.connector.refresh_token)
            
            # Connect to Globus
            connected = self.connector.connect()
            
            if connected:
                # Update file manager with new connector
                self.file_manager = GlobusFileManager(self.connector)
                
                # Set the default endpoint if provided
                if self.config.get("default_endpoint_id"):
                    self.current_endpoint_id = self.config.get("default_endpoint_id")
                
                self.logger.info("Connected to Globus services")
                return True
            else:
                self.logger.error("Failed to connect to Globus services")
                return False
        except Exception as e:
            self.logger.error(f"Error connecting to Globus: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from Globus services.
        
        Returns:
            bool: True if disconnection was successful, False otherwise
        """
        try:
            if self.connector:
                self.connector.disconnect()
            
            self.logger.info("Disconnected from Globus services")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from Globus: {str(e)}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to Globus services.
        
        Returns:
            Dictionary with connection status
        """
        if not self._initialized or not self.connector:
            return {"status": "error", "message": "Plugin not initialized"}
        
        try:
            connected = self.connector.is_connected()
            
            if connected:
                # Get account info
                account_info = self.connector.get_account_info()
                
                return {
                    "status": "success",
                    "connected": True,
                    "user_info": account_info.get("user_info", {}),
                    "message": "Connected to Globus services"
                }
            else:
                return {
                    "status": "error",
                    "connected": False,
                    "message": "Not connected to Globus services"
                }
        except Exception as e:
            return {
                "status": "error",
                "connected": False,
                "message": f"Error testing connection: {str(e)}"
            }
    
    def is_connected(self) -> bool:
        """
        Check if the plugin is connected to Globus services.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self._initialized or not self.connector:
            return False
        
        try:
            return self.connector.is_connected()
        except Exception as e:
            self.logger.error(f"Error checking connection: {str(e)}")
            return False
    
    def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """
        List contents of a directory on the current Globus endpoint.
        
        Args:
            path: Path to the directory
            
        Returns:
            List of file/directory dictionaries
        """
        if not self._initialized or not self.file_manager or not self.is_connected():
            self.logger.error("Not connected to Globus services")
            return []
        
        if not self.current_endpoint_id:
            self.logger.error("No endpoint selected")
            return []
        
        try:
            # Update current path
            self.current_path = path
            
            # List directory contents
            items = self.file_manager.list_directory(self.current_endpoint_id, path)
            
            return items
        except Exception as e:
            self.logger.error(f"Error listing directory: {str(e)}")
            return []
    
    def read_file(self, path: str) -> bytes:
        """
        Read a file from the current Globus endpoint.
        
        Args:
            path: Path to the file
            
        Returns:
            File content as bytes
        """
        if not self._initialized or not self.file_manager or not self.is_connected():
            self.logger.error("Not connected to Globus services")
            return b""
        
        if not self.current_endpoint_id:
            self.logger.error("No endpoint selected")
            return b""
        
        try:
            # Download the file
            content = self.file_manager.download_file(self.current_endpoint_id, path)
            
            if content is None:
                self.logger.error("Failed to download file")
                return b""
            
            return content if isinstance(content, bytes) else b""
        except Exception as e:
            self.logger.error(f"Error reading file: {str(e)}")
            return b""
    
    def write_file(self, path: str, content: bytes) -> bool:
        """
        Write a file to the current Globus endpoint.
        
        Note: This is not directly supported by Globus and requires a local file
        and a transfer operation. This method is provided for compatibility but
        may not work in all cases.
        
        Args:
            path: Path to the file
            content: File content
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        self.logger.warning("Direct file writing is not supported by Globus")
        self.logger.info("Use transfer_file method for transferring files between endpoints")
        return False
    
    def delete_file(self, path: str) -> bool:
        """
        Delete a file from the current Globus endpoint.
        
        Args:
            path: Path to the file
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if not self._initialized or not self.file_manager or not self.is_connected():
            self.logger.error("Not connected to Globus services")
            return False
        
        if not self.current_endpoint_id:
            self.logger.error("No endpoint selected")
            return False
        
        try:
            # Delete the file
            result = self.file_manager.delete(self.current_endpoint_id, path)
            
            if "error" in result:
                self.logger.error(f"Error deleting file: {result['error']}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def create_directory(self, path: str) -> bool:
        """
        Create a directory on the current Globus endpoint.
        
        Args:
            path: Path to the directory
            
        Returns:
            bool: True if creation was successful, False otherwise
        """
        if not self._initialized or not self.file_manager or not self.is_connected():
            self.logger.error("Not connected to Globus services")
            return False
        
        if not self.current_endpoint_id:
            self.logger.error("No endpoint selected")
            return False
        
        try:
            # Create the directory
            result = self.file_manager.create_directory(self.current_endpoint_id, path)
            
            if "error" in result:
                self.logger.error(f"Error creating directory: {result['error']}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error creating directory: {str(e)}")
            return False
    
    def delete_directory(self, path: str, recursive: bool = False) -> bool:
        """
        Delete a directory from the current Globus endpoint.
        
        Args:
            path: Path to the directory
            recursive: Whether to delete recursively
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if not self._initialized or not self.file_manager or not self.is_connected():
            self.logger.error("Not connected to Globus services")
            return False
        
        if not self.current_endpoint_id:
            self.logger.error("No endpoint selected")
            return False
        
        try:
            # Delete the directory
            result = self.file_manager.delete(self.current_endpoint_id, path, recursive=recursive)
            
            if "error" in result:
                self.logger.error(f"Error deleting directory: {result['error']}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error deleting directory: {str(e)}")
            return False
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists on the current Globus endpoint.
        
        Args:
            path: Path to the file
            
        Returns:
            bool: True if the file exists, False otherwise
        """
        if not self._initialized or not self.file_manager or not self.is_connected():
            self.logger.error("Not connected to Globus services")
            return False
        
        if not self.current_endpoint_id:
            self.logger.error("No endpoint selected")
            return False
        
        try:
            # Get the parent directory
            parent_dir = os.path.dirname(path)
            filename = os.path.basename(path)
            
            # List the parent directory
            items = self.file_manager.list_directory(self.current_endpoint_id, parent_dir)
            
            # Check if the file exists
            for item in items:
                if item["name"] == filename and item["type"] == "file":
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error checking if file exists: {str(e)}")
            return False
    
    def directory_exists(self, path: str) -> bool:
        """
        Check if a directory exists on the current Globus endpoint.
        
        Args:
            path: Path to the directory
            
        Returns:
            bool: True if the directory exists, False otherwise
        """
        if not self._initialized or not self.file_manager or not self.is_connected():
            self.logger.error("Not connected to Globus services")
            return False
        
        if not self.current_endpoint_id:
            self.logger.error("No endpoint selected")
            return False
        
        try:
            # Special case for root directory
            if path == "/" or path == "":
                return True
            
            # Get the parent directory
            parent_dir = os.path.dirname(path)
            dirname = os.path.basename(path)
            
            # List the parent directory
            items = self.file_manager.list_directory(self.current_endpoint_id, parent_dir)
            
            # Check if the directory exists
            for item in items:
                if item["name"] == dirname and item["type"] == "directory":
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error checking if directory exists: {str(e)}")
            return False
    
    def _get_full_path(self, path: str) -> str:
        """
        Get the full path for a relative path.
        
        Args:
            path: Relative path
            
        Returns:
            Full path
        """
        if path.startswith("/"):
            return path
        
        return os.path.normpath(os.path.join(self.current_path, path))


# Register the plugin
register_plugin(GlobusPlugin)