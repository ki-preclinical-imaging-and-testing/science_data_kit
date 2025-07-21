"""
Science Data Kit - Microsoft Graph Extension
File Manager Module

This module provides the MSGraphFileManager class, which handles file operations
for Microsoft Graph API.
"""

import os
import io
import logging
from typing import Dict, Any, Optional, List, Union, BinaryIO, Tuple
from datetime import datetime
from pathlib import Path

from msgraph.core import GraphClient

from .connector import MSGraphConnector

logger = logging.getLogger(__name__)

class MSGraphFileManager:
    """
    File manager class for Microsoft Graph API.
    
    This class handles file operations for Microsoft Graph API, including
    listing files, getting metadata, downloading and uploading files, etc.
    """
    
    def __init__(self, connector: MSGraphConnector):
        """
        Initialize the Microsoft Graph file manager.
        
        Args:
            connector: Microsoft Graph connector instance
        """
        self.connector = connector
        if not connector.is_connected():
            raise ValueError("Connector is not connected to Microsoft Graph API")
    
    def list_folder(self, path: str = "", recursive: bool = False, include_deleted: bool = False, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List files and folders in a OneDrive folder.
        
        Args:
            path: Path to the folder (empty for root)
            recursive: Whether to list recursively
            include_deleted: Whether to include deleted items (not supported by Microsoft Graph)
            limit: Maximum number of items to return
            
        Returns:
            List of dictionaries containing file/folder metadata
        """
        try:
            # Normalize path
            path = self._normalize_path(path)
            
            # Handle root folder
            if path == "/":
                endpoint = "/me/drive/root/children"
            else:
                # Remove leading slash for OneDrive paths
                onedrive_path = path[1:] if path.startswith("/") else path
                endpoint = f"/me/drive/root:/{onedrive_path}:/children"
            
            # Add limit if specified
            params = {}
            if limit:
                params["$top"] = limit
            
            # Get items
            response = self.connector.request("GET", endpoint, params=params)
            entries = []
            
            # Process results
            if "value" in response:
                for item in response["value"]:
                    entry = self._process_item(item)
                    entries.append(entry)
                    
                    # Handle recursive listing
                    if recursive and entry["type"] == "folder":
                        folder_path = entry["path"]
                        folder_entries = self.list_folder(folder_path, recursive=True, limit=limit)
                        entries.extend(folder_entries)
            
            return entries
        except Exception as e:
            logger.error(f"Error listing folder {path}: {e}")
            raise
    
    def _process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an item from Microsoft Graph API.
        
        Args:
            item: Item from Microsoft Graph API
            
        Returns:
            Dictionary containing processed metadata
        """
        is_folder = "folder" in item
        
        # Build path
        parent_path = item.get("parentReference", {}).get("path", "")
        if parent_path.startswith("/drive/root:"):
            parent_path = parent_path[len("/drive/root:"):]
        
        if parent_path and not parent_path.endswith("/"):
            parent_path += "/"
            
        path = f"{parent_path}{item['name']}"
        
        # Build entry
        entry = {
            "id": item.get("id"),
            "name": item.get("name"),
            "path": path,
            "type": "folder" if is_folder else "file",
            "size": item.get("size", 0),
            "modified": item.get("lastModifiedDateTime"),
            "created": item.get("createdDateTime"),
            "web_url": item.get("webUrl"),
        }
        
        # Add folder-specific fields
        if is_folder:
            entry["child_count"] = item.get("folder", {}).get("childCount", 0)
        
        # Add file-specific fields
        if not is_folder:
            entry["mime_type"] = item.get("file", {}).get("mimeType")
            entry["hash"] = item.get("file", {}).get("hashes", {}).get("quickXorHash")
            
        return entry
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize a path for Microsoft Graph API.
        
        Args:
            path: Path to normalize
            
        Returns:
            Normalized path
        """
        # Ensure path starts with /
        if not path.startswith("/"):
            path = f"/{path}"
            
        # Remove trailing slash except for root
        if path != "/" and path.endswith("/"):
            path = path[:-1]
            
        return path
    
    def get_metadata(self, path: str) -> Dict[str, Any]:
        """
        Get metadata for a file or folder.
        
        Args:
            path: Path to the file or folder
            
        Returns:
            Dictionary containing metadata
        """
        try:
            # Normalize path
            path = self._normalize_path(path)
            
            # Handle root folder
            if path == "/":
                endpoint = "/me/drive/root"
            else:
                # Remove leading slash for OneDrive paths
                onedrive_path = path[1:] if path.startswith("/") else path
                endpoint = f"/me/drive/root:/{onedrive_path}"
            
            # Get item
            response = self.connector.request("GET", endpoint)
            
            # Process item
            return self._process_item(response)
        except Exception as e:
            logger.error(f"Error getting metadata for {path}: {e}")
            raise
    
    def download_file(self, path: str) -> bytes:
        """
        Download a file.
        
        Args:
            path: Path to the file
            
        Returns:
            File contents as bytes
        """
        try:
            # Normalize path
            path = self._normalize_path(path)
            
            # Get file metadata to ensure it exists and is a file
            metadata = self.get_metadata(path)
            if metadata["type"] != "file":
                raise ValueError(f"Path {path} is not a file")
            
            # Get file content
            file_id = metadata["id"]
            endpoint = f"/me/drive/items/{file_id}/content"
            
            # Make request directly with client to get binary content
            response = self.connector.client.get(endpoint)
            if response.status_code == 200:
                return response.content
            else:
                raise ValueError(f"Failed to download file: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Error downloading file {path}: {e}")
            raise
    
    def upload_file(self, local_path: Union[str, Path, BinaryIO], onedrive_path: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Upload a file.
        
        Args:
            local_path: Path to the local file or file-like object
            onedrive_path: Path to the destination in OneDrive
            overwrite: Whether to overwrite existing file
            
        Returns:
            Dictionary containing metadata of the uploaded file
        """
        try:
            # Normalize path
            onedrive_path = self._normalize_path(onedrive_path)
            
            # Get content
            if isinstance(local_path, (str, Path)):
                with open(local_path, "rb") as f:
                    content = f.read()
            else:
                content = local_path.read()
                
            # Check if file exists
            try:
                existing = self.get_metadata(onedrive_path)
                if not overwrite:
                    raise ValueError(f"File {onedrive_path} already exists and overwrite is False")
            except Exception:
                # File doesn't exist, which is fine
                pass
            
            # Handle parent folder
            parent_path = str(Path(onedrive_path).parent)
            if parent_path != "/":
                try:
                    self.get_metadata(parent_path)
                except Exception:
                    # Parent folder doesn't exist, create it
                    self.create_folder(parent_path)
            
            # Get file name
            file_name = Path(onedrive_path).name
            
            # For small files (< 4MB), use simple upload
            if len(content) < 4 * 1024 * 1024:
                # Remove leading slash for OneDrive paths
                parent_onedrive_path = parent_path[1:] if parent_path.startswith("/") else parent_path
                
                if parent_path == "/":
                    endpoint = f"/me/drive/root:/{file_name}:/content"
                else:
                    endpoint = f"/me/drive/root:/{parent_onedrive_path}/{file_name}:/content"
                
                # Make request directly with client to upload binary content
                headers = {"Content-Type": "application/octet-stream"}
                response = self.connector.client.put(endpoint, data=content, headers=headers)
                
                if response.status_code >= 200 and response.status_code < 300:
                    return self._process_item(response.json())
                else:
                    raise ValueError(f"Failed to upload file: {response.status_code} {response.text}")
            else:
                # For larger files, we would use upload session
                # This is a simplified implementation
                raise NotImplementedError("Upload of files larger than 4MB is not implemented yet")
        except Exception as e:
            logger.error(f"Error uploading file to {onedrive_path}: {e}")
            raise
    
    def create_folder(self, path: str) -> Dict[str, Any]:
        """
        Create a folder.
        
        Args:
            path: Path to the folder
            
        Returns:
            Dictionary containing metadata of the created folder
        """
        try:
            # Normalize path
            path = self._normalize_path(path)
            
            # Check if folder already exists
            try:
                existing = self.get_metadata(path)
                return existing  # Folder already exists
            except Exception:
                # Folder doesn't exist, which is fine
                pass
            
            # Handle parent folder
            parent_path = str(Path(path).parent)
            if parent_path != "/":
                try:
                    self.get_metadata(parent_path)
                except Exception:
                    # Parent folder doesn't exist, create it
                    self.create_folder(parent_path)
            
            # Get folder name
            folder_name = Path(path).name
            
            # Create folder
            if parent_path == "/":
                endpoint = "/me/drive/root/children"
            else:
                # Remove leading slash for OneDrive paths
                parent_onedrive_path = parent_path[1:] if parent_path.startswith("/") else parent_path
                endpoint = f"/me/drive/root:/{parent_onedrive_path}:/children"
            
            data = {
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "fail"
            }
            
            response = self.connector.request("POST", endpoint, data=data)
            return self._process_item(response)
        except Exception as e:
            logger.error(f"Error creating folder {path}: {e}")
            raise
    
    def delete(self, path: str) -> bool:
        """
        Delete a file or folder.
        
        Args:
            path: Path to the file or folder
            
        Returns:
            True if deletion was successful
        """
        try:
            # Normalize path
            path = self._normalize_path(path)
            
            # Get item metadata to ensure it exists
            metadata = self.get_metadata(path)
            
            # Delete item
            item_id = metadata["id"]
            endpoint = f"/me/drive/items/{item_id}"
            
            # Make request directly with client to handle 204 response
            response = self.connector.client.delete(endpoint)
            
            if response.status_code == 204:
                return True
            else:
                raise ValueError(f"Failed to delete item: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")
            raise
    
    def search(self, query: str, path: str = "", max_results: int = 100, file_extensions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for files and folders.
        
        Args:
            query: Search query
            path: Path to search in (empty for all)
            max_results: Maximum number of results to return
            file_extensions: List of file extensions to filter by
            
        Returns:
            List of dictionaries containing file/folder metadata
        """
        try:
            # Normalize path
            path = self._normalize_path(path)
            
            # Build query
            params = {
                "q": query,
                "$top": max_results
            }
            
            # Handle path
            if path != "/":
                # Remove leading slash for OneDrive paths
                onedrive_path = path[1:] if path.startswith("/") else path
                endpoint = f"/me/drive/root:/{onedrive_path}:/search"
            else:
                endpoint = "/me/drive/root/search"
            
            # Get search results
            response = self.connector.request("GET", endpoint, params=params)
            entries = []
            
            # Process results
            if "value" in response:
                for item in response["value"]:
                    entry = self._process_item(item)
                    
                    # Filter by file extension if specified
                    if file_extensions and entry["type"] == "file":
                        file_ext = Path(entry["name"]).suffix.lower()
                        if file_ext and file_ext[1:] in file_extensions:
                            entries.append(entry)
                    else:
                        entries.append(entry)
            
            return entries
        except Exception as e:
            logger.error(f"Error searching for {query}: {e}")
            raise