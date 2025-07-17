"""
Google Drive Plugin for Science Data Kit.

This module provides a plugin for accessing files on Google Drive.
It implements the FilesystemPluginInterface and provides methods for
file and directory operations using the Google Drive API.
"""

import io
import os
import logging
import pandas as pd
from typing import Any, Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

from science_data_kit.core.plugins.config import (
    ConfigField,
    ConfigFieldType,
    PluginConfigSchema,
    create_default_config,
)
from science_data_kit.core.plugins.interfaces import FilesystemPluginInterface
from science_data_kit.core.integrations.plugin_architecture import register_plugin

logger = logging.getLogger(__name__)


@register_plugin
class GoogleDrivePlugin(FilesystemPluginInterface):
    """
    Plugin for accessing files on Google Drive.
    
    This plugin provides access to files and directories on Google Drive,
    with authentication and connection management.
    """
    
    # Define the scopes needed for Google Drive access
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    def __init__(self):
        """Initialize the plugin."""
        self._name = "google_drive"
        self._version = "1.0.0"
        self._description = "Plugin for accessing files on Google Drive"
        self._is_initialized = False
        self._is_connected = False
        self._config = {}
        self._service = None
        self._credentials = None
        
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
                    name="token_path",
                    field_type=ConfigFieldType.FILE_PATH,
                    description="Path to the token file",
                    required=False,
                ),
                ConfigField(
                    name="credentials_path",
                    field_type=ConfigFieldType.FILE_PATH,
                    description="Path to the credentials file",
                    required=False,
                ),
                ConfigField(
                    name="token_dict",
                    field_type=ConfigFieldType.OBJECT,
                    description="Token dictionary for authentication",
                    required=False,
                ),
                ConfigField(
                    name="root_folder_id",
                    field_type=ConfigFieldType.STRING,
                    description="Root folder ID in Google Drive (use 'root' for root folder)",
                    required=False,
                    default="root",
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
        # Basic schema validation
        if not self.config_schema.validate_config(config):
            return False
            
        # Additional validation: at least one of token_path, credentials_path, or token_dict must be provided
        if not any([config.get("token_path"), config.get("credentials_path"), config.get("token_dict")]):
            logger.error("At least one of token_path, credentials_path, or token_dict must be provided")
            return False
            
        return True
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with the given configuration.
        
        Args:
            config: The configuration to use
            
        Returns:
            True if initialization was successful, False otherwise
        """
        if not self.validate_config(config):
            logger.error("Invalid configuration for Google Drive plugin")
            return False
            
        self._config = config
        
        try:
            # Get credentials from config
            token_path = config.get("token_path")
            credentials_path = config.get("credentials_path")
            token_dict = config.get("token_dict")
            
            # Get or refresh credentials
            creds = None
            
            # If token dictionary is provided directly
            if token_dict:
                creds = Credentials.from_authorized_user_info(token_dict, self.SCOPES)
            
            # If token file exists, load credentials from it
            elif token_path and os.path.exists(token_path):
                with open(token_path, 'r') as token:
                    creds = Credentials.from_authorized_user_info(eval(token.read()), self.SCOPES)
            
            # If credentials need to be refreshed
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Save refreshed credentials if token_path is provided
                if token_path:
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
            
            # If no valid credentials available and credentials_path is provided, run the OAuth flow
            elif not creds and credentials_path:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
                # Save credentials if token_path is provided
                if token_path:
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
            
            # If we still don't have valid credentials, return False
            if not creds or not creds.valid:
                logger.error("Failed to obtain valid Google Drive credentials")
                return False
                
            self._credentials = creds
            self._is_initialized = True
            logger.info("Google Drive plugin initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Google Drive plugin: {e}")
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
            
        self._service = None
        self._credentials = None
        self._is_initialized = False
        logger.info("Google Drive plugin shut down")
        return True
        
    @property
    def is_initialized(self) -> bool:
        """Check if the plugin is initialized."""
        return self._is_initialized
        
    @property
    def capabilities(self) -> Set[str]:
        """Get the plugin capabilities."""
        capabilities = {"filesystem", "browsable", "readable"}
        return capabilities
        
    def connect(self, config: Dict[str, Any]) -> None:
        """
        Establish connection with Google Drive.
        
        Args:
            config: Configuration dictionary for the connection
        """
        if not self._is_initialized:
            if not self.initialize(config):
                raise RuntimeError("Failed to initialize Google Drive plugin")
                
        try:
            # Build the Drive service
            self._service = build('drive', 'v3', credentials=self._credentials)
            
            # Test connection by listing files (limit to 1)
            self._service.files().list(pageSize=1).execute()
            
            self._is_connected = True
            logger.info("Connected to Google Drive API")
        except Exception as e:
            logger.error(f"Error connecting to Google Drive: {e}")
            self._is_connected = False
            raise RuntimeError(f"Failed to connect to Google Drive: {e}")
        
    def disconnect(self) -> None:
        """Clean up connection."""
        self._service = None
        self._is_connected = False
        logger.info("Disconnected from Google Drive API")
        
    def test_connection(self) -> bool:
        """
        Verify connection is working.
        
        Returns:
            True if connection is working, False otherwise
        """
        if not self._is_connected or not self._service:
            return False
            
        try:
            # Try to list files to verify connection (limit to 1)
            self._service.files().list(pageSize=1).execute()
            return True
        except Exception:
            return False
        
    @property
    def is_connected(self) -> bool:
        """
        Check if the connection is currently established.
        
        Returns:
            True if connected, False otherwise
        """
        return self._is_connected and self._service is not None
        
    def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """
        List contents of a directory.
        
        Args:
            path: Path to the directory (folder ID in Google Drive)
            
        Returns:
            List of dictionaries containing file/directory information
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Google Drive")
            
        try:
            # In Google Drive, path is actually a folder ID
            folder_id = path if path else self._config.get("root_folder_id", "root")
            
            # Prepare query to find files and folders in the specified folder
            query = f"'{folder_id}' in parents and trashed = false"
            
            # List files and folders
            results = self._service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            
            items = results.get('files', [])
            files = []
            
            # Process items
            for item in items:
                mime_type = item.get('mimeType', '')
                
                if mime_type == 'application/vnd.google-apps.folder':
                    # Include folders for navigation
                    files.append({
                        "name": item['name'],
                        "path": item['id'],  # Google Drive uses IDs, not paths
                        "is_dir": True,
                        "size": None,
                        "modified": item.get('modifiedTime'),
                    })
                else:
                    # Include files
                    files.append({
                        "name": item['name'],
                        "path": item['id'],  # Google Drive uses IDs, not paths
                        "is_dir": False,
                        "size": item.get('size'),
                        "modified": item.get('modifiedTime'),
                    })
            
            # Handle pagination for large folders
            page_token = results.get('nextPageToken')
            while page_token:
                results = self._service.files().list(
                    q=query,
                    pageSize=100,
                    fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)",
                    pageToken=page_token
                ).execute()
                
                items = results.get('files', [])
                
                for item in items:
                    mime_type = item.get('mimeType', '')
                    
                    if mime_type == 'application/vnd.google-apps.folder':
                        files.append({
                            "name": item['name'],
                            "path": item['id'],
                            "is_dir": True,
                            "size": None,
                            "modified": item.get('modifiedTime'),
                        })
                    else:
                        files.append({
                            "name": item['name'],
                            "path": item['id'],
                            "is_dir": False,
                            "size": item.get('size'),
                            "modified": item.get('modifiedTime'),
                        })
                
                page_token = results.get('nextPageToken')
            
            return files
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            raise
        
    def read_file(self, path: str) -> bytes:
        """
        Read a file.
        
        Args:
            path: Path to the file (file ID in Google Drive)
            
        Returns:
            File contents as bytes
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Google Drive")
            
        try:
            # In Google Drive, path is actually a file ID
            file_id = path
            
            # Get file metadata to determine file type
            file_metadata = self._service.files().get(fileId=file_id, fields="name,mimeType").execute()
            mime_type = file_metadata.get('mimeType', '')
            
            # Handle Google Docs differently
            if mime_type.startswith('application/vnd.google-apps.'):
                # Export Google Docs as PDF
                request = self._service.files().export_media(fileId=file_id, mimeType='application/pdf')
            else:
                # Download regular file
                request = self._service.files().get_media(fileId=file_id)
                
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            return file_content.read()
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
        # Google Drive plugin is read-only with the current scope
        raise PermissionError("Google Drive plugin is read-only with the current scope")
        
    def delete_file(self, path: str) -> bool:
        """
        Delete a file.
        
        Args:
            path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        # Google Drive plugin is read-only with the current scope
        raise PermissionError("Google Drive plugin is read-only with the current scope")
        
    def create_directory(self, path: str) -> bool:
        """
        Create a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            True if successful, False otherwise
        """
        # Google Drive plugin is read-only with the current scope
        raise PermissionError("Google Drive plugin is read-only with the current scope")
        
    def delete_directory(self, path: str, recursive: bool = False) -> bool:
        """
        Delete a directory.
        
        Args:
            path: Path to the directory
            recursive: Whether to delete recursively
            
        Returns:
            True if successful, False otherwise
        """
        # Google Drive plugin is read-only with the current scope
        raise PermissionError("Google Drive plugin is read-only with the current scope")
        
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            path: Path to the file (file ID in Google Drive)
            
        Returns:
            True if the file exists, False otherwise
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Google Drive")
            
        try:
            # In Google Drive, path is actually a file ID
            file_id = path
            
            # Get file metadata to check if file exists
            file_metadata = self._service.files().get(fileId=file_id, fields="mimeType").execute()
            mime_type = file_metadata.get('mimeType', '')
            
            # Check if it's not a folder
            return mime_type != 'application/vnd.google-apps.folder'
        except Exception:
            return False
        
    def directory_exists(self, path: str) -> bool:
        """
        Check if a directory exists.
        
        Args:
            path: Path to the directory (folder ID in Google Drive)
            
        Returns:
            True if the directory exists, False otherwise
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Google Drive")
            
        try:
            # In Google Drive, path is actually a folder ID
            folder_id = path
            
            # Get folder metadata to check if folder exists
            folder_metadata = self._service.files().get(fileId=folder_id, fields="mimeType").execute()
            mime_type = folder_metadata.get('mimeType', '')
            
            # Check if it's a folder
            return mime_type == 'application/vnd.google-apps.folder'
        except Exception:
            return False