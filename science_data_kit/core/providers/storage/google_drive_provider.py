"""
Google Drive Provider for Science Data Kit

This module provides a Google Drive provider for accessing CSV and Excel files
stored in Google Drive.

This is a compatibility layer that uses the new GoogleDrivePlugin under the hood
while maintaining the old interface for backward compatibility.
"""

import io
import os
import pandas as pd
import warnings
from typing import Dict, List, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

from ...providers.registry import BaseProvider
from science_data_kit.core.connections.manager import manager
from science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin import GoogleDrivePlugin


class GoogleDriveProvider(BaseProvider):
    """
    Google Drive file provider for CSV/Excel data access

    This is a compatibility layer that uses the new GoogleDrivePlugin under the hood
    while maintaining the old interface for backward compatibility.
    """

    # Define the scopes needed for Google Drive access
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Google Drive provider.

        Args:
            config: Configuration dictionary containing Google Drive credentials
                   Can include token_path, credentials_path, or token_dict
        """
        super().__init__(config)
        self.service = None
        self._plugin = None

        # Emit deprecation warning
        warnings.warn(
            "GoogleDriveProvider is deprecated and will be removed in a future version. "
            "Please use the new plugin architecture instead. "
            "See docs/guides/plugin_migration_guide.md for migration instructions.",
            DeprecationWarning,
            stacklevel=2
        )

    async def initialize(self) -> bool:
        """
        Initialize Google Drive API connection using credentials.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Get credentials from config
            token_path = self.config.get("token_path")
            credentials_path = self.config.get("credentials_path")
            token_dict = self.config.get("token_dict")

            if not any([token_path, credentials_path, token_dict]):
                print("Google Drive credentials not found in configuration")
                return False

            # Initialize the plugin
            try:
                # Try to get the plugin from the manager
                self._plugin = manager.get_plugin_instance("google_drive")
            except Exception:
                # If the plugin is not registered, create a new instance
                self._plugin = GoogleDrivePlugin()

            # Convert old config format to new format
            plugin_config = {
                "token_path": token_path,
                "credentials_path": credentials_path,
                "token_dict": token_dict,
                "root_folder_id": self.config.get("root_folder_id", "root")
            }

            # Connect to the plugin
            self._plugin.connect(plugin_config)

            # For backward compatibility, also initialize the service
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
                print("Failed to obtain valid Google Drive credentials")
                return False

            # Build the Drive service
            self.service = build('drive', 'v3', credentials=creds)

            self.is_initialized = True
            return True

        except RefreshError as e:
            print(f"Google Drive token refresh error: {str(e)}")
            return False
        except Exception as e:
            print(f"Error initializing Google Drive provider: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """
        Verify Google Drive connection is working.

        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized or not self._plugin:
            return False

        try:
            # Use the plugin's test_connection method
            return self._plugin.test_connection()
        except Exception as e:
            print(f"Google Drive health check failed: {str(e)}")
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
            "max_size": "5TB"  # Google Drive file size limit for non-Google formats
        }

    async def list_files(self, folder_id: str = "root", file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        List CSV/Excel files in Google Drive folder.

        Args:
            folder_id: ID of the folder in Google Drive (use "root" for root folder)
            file_types: List of file extensions to filter by (e.g., ["csv", "xlsx"])

        Returns:
            List of file metadata dictionaries
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Google Drive provider not initialized")

        if file_types is None:
            file_types = ["csv", "xlsx", "xls"]

        try:
            # Use the plugin's list_directory method
            directory_contents = self._plugin.list_directory(folder_id)

            # Filter and convert to the old format
            files = []
            for item in directory_contents:
                if item["is_dir"]:
                    # Include directories for navigation
                    files.append({
                        "id": item["path"],
                        "name": item["name"],
                        "path": item["path"],  # Google Drive uses IDs, not paths
                        "type": "folder"
                    })
                else:
                    # Check if file has one of the specified extensions or is a Google Sheets file
                    file_ext = os.path.splitext(item["name"])[1].lower().lstrip(".")
                    is_google_sheet = "application/vnd.google-apps.spreadsheet" in item.get("mime_type", "")

                    if file_ext in file_types or is_google_sheet:
                        file_type = "sheet" if is_google_sheet else file_ext
                        files.append({
                            "id": item["path"],
                            "name": item["name"],
                            "path": item["path"],  # Google Drive uses IDs, not paths
                            "size": item.get("size", "N/A"),
                            "modified": item.get("modified", "N/A"),
                            "type": file_type
                        })

            return files

        except Exception as e:
            print(f"Error listing Google Drive files: {str(e)}")
            raise

    async def download_file_data(self, file_id: str) -> pd.DataFrame:
        """
        Download file and return as pandas DataFrame.

        Args:
            file_id: ID of the file in Google Drive

        Returns:
            Pandas DataFrame containing the file data
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Google Drive provider not initialized")

        try:
            # Use the plugin's read_file method
            content = self._plugin.read_file(file_id)

            # Get file metadata to determine file type
            if self.service:
                file_metadata = self.service.files().get(fileId=file_id, fields="name,mimeType").execute()
                file_name = file_metadata.get('name', '')
                mime_type = file_metadata.get('mimeType', '')

                # Handle Google Sheets differently
                if mime_type == 'application/vnd.google-apps.spreadsheet':
                    # Content is already in PDF format, but we need Excel for pandas
                    # For compatibility, we'll use the service directly for Google Sheets
                    request = self.service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    file_content = io.BytesIO()
                    downloader = MediaIoBaseDownload(file_content, request)

                    done = False
                    while not done:
                        status, done = downloader.next_chunk()

                    file_content.seek(0)
                    return pd.read_excel(file_content)
                else:
                    # For regular files, use the content from the plugin
                    file_content = io.BytesIO(content)

                    # Detect file type from name
                    file_ext = os.path.splitext(file_name)[1].lower()

                    # Parse with appropriate pandas function
                    if file_ext == '.csv':
                        return pd.read_csv(file_content)
                    elif file_ext in ['.xlsx', '.xls']:
                        return pd.read_excel(file_content)
                    else:
                        raise ValueError(f"Unsupported file type: {file_ext}")
            else:
                # If service is not available, try to determine file type from the file_id
                # This is less reliable but a fallback
                file_content = io.BytesIO(content)

                # Try to read as Excel first, then CSV if that fails
                try:
                    return pd.read_excel(file_content)
                except Exception:
                    file_content.seek(0)
                    try:
                        return pd.read_csv(file_content)
                    except Exception:
                        raise ValueError("Unable to determine file type")

        except Exception as e:
            print(f"Error downloading file from Google Drive: {str(e)}")
            raise

    async def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        Get file metadata without downloading.

        Args:
            file_id: ID of the file in Google Drive

        Returns:
            Dictionary containing file metadata
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Google Drive provider not initialized")

        try:
            # Check if file exists using the plugin
            if not self._plugin.file_exists(file_id):
                raise ValueError(f"File does not exist: {file_id}")

            # Get file metadata
            if self.service:
                # If service is available, use it to get detailed metadata
                file_metadata = self.service.files().get(
                    fileId=file_id,
                    fields="id,name,mimeType,size,modifiedTime"
                ).execute()

                mime_type = file_metadata.get('mimeType', '')
                file_name = file_metadata.get('name', '')

                # Determine file type
                if mime_type == 'application/vnd.google-apps.spreadsheet':
                    file_type = "sheet"
                else:
                    file_type = os.path.splitext(file_name)[1].lower().lstrip(".")

                return {
                    "id": file_metadata.get('id'),
                    "name": file_name,
                    "path": file_id,  # Google Drive uses IDs, not paths
                    "size": file_metadata.get('size', 'N/A'),
                    "modified": file_metadata.get('modifiedTime', 'N/A'),
                    "type": file_type
                }
            else:
                # If service is not available, get limited metadata from the plugin
                # Find the file in the parent directory
                parent_id = "root"  # Default to root if we can't determine parent

                # Try to list the root directory to find the file
                directory_contents = self._plugin.list_directory(parent_id)

                # Find the file in the directory contents
                for item in directory_contents:
                    if not item["is_dir"] and item["path"] == file_id:
                        file_ext = os.path.splitext(item["name"])[1].lower().lstrip(".")
                        return {
                            "id": item["path"],
                            "name": item["name"],
                            "path": item["path"],
                            "size": item.get("size", "N/A"),
                            "modified": item.get("modified", "N/A"),
                            "type": file_ext
                        }

                # If we can't find the file in the root directory, return basic info
                return {
                    "id": file_id,
                    "name": "Unknown",
                    "path": file_id,
                    "size": "N/A",
                    "modified": "N/A",
                    "type": "unknown"
                }

        except Exception as e:
            print(f"Error getting file info from Google Drive: {str(e)}")
            raise
