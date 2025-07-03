"""
Google Drive Provider for Science Data Kit

This module provides a Google Drive provider for accessing CSV and Excel files
stored in Google Drive.
"""

import io
import os
import pandas as pd
from typing import Dict, List, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

from ...providers.registry import BaseProvider


class GoogleDriveProvider(BaseProvider):
    """Google Drive file provider for CSV/Excel data access"""
    
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
            
            # Test connection by listing files (limit to 1)
            self.service.files().list(pageSize=1).execute()
            
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
        if not self.is_initialized or not self.service:
            return False
        
        try:
            # Try to list files to verify connection (limit to 1)
            self.service.files().list(pageSize=1).execute()
            return True
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
        if not self.is_initialized or not self.service:
            raise Exception("Google Drive provider not initialized")
        
        if file_types is None:
            file_types = ["csv", "xlsx", "xls"]
        
        try:
            # Prepare query to find files and folders in the specified folder
            query = f"'{folder_id}' in parents and trashed = false"
            
            # List files and folders
            results = self.service.files().list(
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
                        "id": item['id'],
                        "name": item['name'],
                        "path": item['id'],  # Google Drive uses IDs, not paths
                        "type": "folder"
                    })
                else:
                    # Check if file has one of the specified extensions or is a Google Sheets file
                    file_ext = os.path.splitext(item['name'])[1].lower().lstrip(".")
                    is_google_sheet = mime_type == 'application/vnd.google-apps.spreadsheet'
                    
                    if file_ext in file_types or is_google_sheet:
                        file_type = "sheet" if is_google_sheet else file_ext
                        files.append({
                            "id": item['id'],
                            "name": item['name'],
                            "path": item['id'],  # Google Drive uses IDs, not paths
                            "size": item.get('size', 'N/A'),
                            "modified": item.get('modifiedTime', 'N/A'),
                            "type": file_type
                        })
            
            # Handle pagination for large folders
            page_token = results.get('nextPageToken')
            while page_token:
                results = self.service.files().list(
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
                            "id": item['id'],
                            "name": item['name'],
                            "path": item['id'],
                            "type": "folder"
                        })
                    else:
                        file_ext = os.path.splitext(item['name'])[1].lower().lstrip(".")
                        is_google_sheet = mime_type == 'application/vnd.google-apps.spreadsheet'
                        
                        if file_ext in file_types or is_google_sheet:
                            file_type = "sheet" if is_google_sheet else file_ext
                            files.append({
                                "id": item['id'],
                                "name": item['name'],
                                "path": item['id'],
                                "size": item.get('size', 'N/A'),
                                "modified": item.get('modifiedTime', 'N/A'),
                                "type": file_type
                            })
                
                page_token = results.get('nextPageToken')
            
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
        if not self.is_initialized or not self.service:
            raise Exception("Google Drive provider not initialized")
        
        try:
            # Get file metadata to determine file type
            file_metadata = self.service.files().get(fileId=file_id, fields="name,mimeType").execute()
            file_name = file_metadata.get('name', '')
            mime_type = file_metadata.get('mimeType', '')
            
            # Handle Google Sheets differently
            if mime_type == 'application/vnd.google-apps.spreadsheet':
                # Export Google Sheet as Excel
                request = self.service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                file_content = io.BytesIO()
                downloader = MediaIoBaseDownload(file_content, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                
                file_content.seek(0)
                return pd.read_excel(file_content)
            else:
                # Download regular file
                request = self.service.files().get_media(fileId=file_id)
                file_content = io.BytesIO()
                downloader = MediaIoBaseDownload(file_content, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                
                file_content.seek(0)
                
                # Detect file type from name
                file_ext = os.path.splitext(file_name)[1].lower()
                
                # Parse with appropriate pandas function
                if file_ext == '.csv':
                    return pd.read_csv(file_content)
                elif file_ext in ['.xlsx', '.xls']:
                    return pd.read_excel(file_content)
                else:
                    raise ValueError(f"Unsupported file type: {file_ext}")
        
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
        if not self.is_initialized or not self.service:
            raise Exception("Google Drive provider not initialized")
        
        try:
            # Get file metadata
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
        
        except Exception as e:
            print(f"Error getting file info from Google Drive: {str(e)}")
            raise