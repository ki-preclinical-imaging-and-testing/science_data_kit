"""
Dropbox Provider for Science Data Kit

This module provides a Dropbox provider for accessing CSV and Excel files
stored in Dropbox.
"""

import io
import os
import pandas as pd
from typing import Dict, List, Any, Optional
from dropbox import Dropbox
from dropbox.exceptions import AuthError, ApiError
from dropbox.files import FileMetadata, FolderMetadata

from ...providers.registry import BaseProvider


class DropboxProvider(BaseProvider):
    """Dropbox file provider for CSV/Excel data access"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Dropbox provider.
        
        Args:
            config: Configuration dictionary containing Dropbox access token
        """
        super().__init__(config)
        self.client = None
    
    async def initialize(self) -> bool:
        """
        Initialize Dropbox API connection using access token.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Get access token from config
            access_token = self.config.get("access_token")
            if not access_token:
                print("Dropbox access token not found in configuration")
                return False
            
            # Create Dropbox client
            self.client = Dropbox(access_token)
            
            # Test connection
            self.client.users_get_current_account()
            
            self.is_initialized = True
            return True
        except AuthError as e:
            print(f"Dropbox authentication error: {str(e)}")
            return False
        except ApiError as e:
            print(f"Dropbox API error: {str(e)}")
            return False
        except Exception as e:
            print(f"Error initializing Dropbox provider: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """
        Verify Dropbox connection is working.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized or not self.client:
            return False
        
        try:
            # Try to get account info to verify connection
            self.client.users_get_current_account()
            return True
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
        if not self.is_initialized or not self.client:
            raise Exception("Dropbox provider not initialized")
        
        if file_types is None:
            file_types = ["csv", "xlsx", "xls"]
        
        try:
            # Ensure folder path starts with a slash
            if folder_path and not folder_path.startswith("/"):
                folder_path = f"/{folder_path}"
            
            # List folder contents
            result = self.client.files_list_folder(folder_path)
            
            files = []
            
            # Process entries
            for entry in result.entries:
                if isinstance(entry, FileMetadata):
                    # Check if file has one of the specified extensions
                    file_ext = os.path.splitext(entry.name)[1].lower().lstrip(".")
                    if file_ext in file_types:
                        files.append({
                            "id": entry.id,
                            "name": entry.name,
                            "path": entry.path_display,
                            "size": entry.size,
                            "modified": entry.server_modified.isoformat(),
                            "type": file_ext
                        })
                elif isinstance(entry, FolderMetadata):
                    # Include folders for navigation
                    files.append({
                        "id": entry.id,
                        "name": entry.name,
                        "path": entry.path_display,
                        "type": "folder"
                    })
            
            # Handle pagination for large folders
            while result.has_more:
                result = self.client.files_list_folder_continue(result.cursor)
                
                for entry in result.entries:
                    if isinstance(entry, FileMetadata):
                        file_ext = os.path.splitext(entry.name)[1].lower().lstrip(".")
                        if file_ext in file_types:
                            files.append({
                                "id": entry.id,
                                "name": entry.name,
                                "path": entry.path_display,
                                "size": entry.size,
                                "modified": entry.server_modified.isoformat(),
                                "type": file_ext
                            })
                    elif isinstance(entry, FolderMetadata):
                        files.append({
                            "id": entry.id,
                            "name": entry.name,
                            "path": entry.path_display,
                            "type": "folder"
                        })
            
            return files
        
        except ApiError as e:
            print(f"Dropbox API error: {str(e)}")
            raise
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
        if not self.is_initialized or not self.client:
            raise Exception("Dropbox provider not initialized")
        
        try:
            # Ensure file path starts with a slash
            if not file_path.startswith("/"):
                file_path = f"/{file_path}"
            
            # Download file
            metadata, response = self.client.files_download(file_path)
            
            # Get file content
            content = response.content
            
            # Detect file type
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Parse with appropriate pandas function
            if file_ext == ".csv":
                return pd.read_csv(io.BytesIO(content))
            elif file_ext in [".xlsx", ".xls"]:
                return pd.read_excel(io.BytesIO(content))
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        
        except ApiError as e:
            print(f"Dropbox API error: {str(e)}")
            raise
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
        if not self.is_initialized or not self.client:
            raise Exception("Dropbox provider not initialized")
        
        try:
            # Ensure file path starts with a slash
            if not file_path.startswith("/"):
                file_path = f"/{file_path}"
            
            # Get file metadata
            metadata = self.client.files_get_metadata(file_path)
            
            if isinstance(metadata, FileMetadata):
                return {
                    "id": metadata.id,
                    "name": metadata.name,
                    "path": metadata.path_display,
                    "size": metadata.size,
                    "modified": metadata.server_modified.isoformat(),
                    "type": os.path.splitext(metadata.name)[1].lower().lstrip(".")
                }
            else:
                raise ValueError(f"Path does not point to a file: {file_path}")
        
        except ApiError as e:
            print(f"Dropbox API error: {str(e)}")
            raise
        except Exception as e:
            print(f"Error getting file info from Dropbox: {str(e)}")
            raise