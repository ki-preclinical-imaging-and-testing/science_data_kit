"""
Science Data Kit - Microsoft Graph Extension
SharePoint File Manager Module

This module provides the SharePointFileManager class, which handles file operations
for SharePoint document libraries via Microsoft Graph API.
"""

import os
import io
import logging
from typing import Dict, Any, Optional, List, Union, BinaryIO, Tuple
from datetime import datetime
from pathlib import Path

from .connector import MSGraphConnector

logger = logging.getLogger(__name__)

class SharePointFileManager:
    """
    SharePoint file manager class for Microsoft Graph API.
    
    This class handles file operations for SharePoint document libraries via Microsoft Graph API,
    including listing files, getting metadata, downloading and uploading files, etc.
    """
    
    def __init__(self, connector: MSGraphConnector, site_id: str, drive_id: str):
        """
        Initialize the SharePoint file manager.
        
        Args:
            connector: Microsoft Graph connector instance
            site_id: ID of the SharePoint site
            drive_id: ID of the SharePoint drive (document library)
        """
        self.connector = connector
        if not connector.is_connected():
            raise ValueError("Connector is not connected to Microsoft Graph API")
        
        self.site_id = site_id
        self.drive_id = drive_id
        
        # Validate site and drive
        try:
            # Get site info to validate site_id
            self.site_info = self._get_site_info()
            
            # Get drive info to validate drive_id
            self.drive_info = self._get_drive_info()
            
            logger.info(f"Initialized SharePoint file manager for site '{self.site_info.get('displayName')}' "
                       f"and document library '{self.drive_info.get('name')}'")
        except Exception as e:
            logger.error(f"Error initializing SharePoint file manager: {e}")
            raise ValueError(f"Invalid site_id or drive_id: {e}")
    
    def _get_site_info(self) -> Dict[str, Any]:
        """
        Get information about the SharePoint site.
        
        Returns:
            Dict[str, Any]: Site information
        """
        return self.connector.request("GET", f"/sites/{self.site_id}")
    
    def _get_drive_info(self) -> Dict[str, Any]:
        """
        Get information about the SharePoint drive (document library).
        
        Returns:
            Dict[str, Any]: Drive information
        """
        return self.connector.request("GET", f"/sites/{self.site_id}/drives/{self.drive_id}")
    
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
    
    def list_folder(self, folder_id: str = "root", recursive: bool = False, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List files and folders in a SharePoint document library folder.
        
        Args:
            folder_id: ID of the folder (default: "root")
            recursive: Whether to list recursively
            limit: Maximum number of items to return
            
        Returns:
            List of dictionaries containing file/folder metadata
        """
        try:
            # Add limit if specified
            params = {}
            if limit:
                params["$top"] = limit
            
            # Get items
            response = self.connector.request(
                "GET", 
                f"/sites/{self.site_id}/drives/{self.drive_id}/items/{folder_id}/children",
                params=params
            )
            entries = []
            
            # Process results
            if "value" in response:
                for item in response["value"]:
                    entry = self._process_item(item)
                    entries.append(entry)
                    
                    # Handle recursive listing
                    if recursive and entry["type"] == "folder":
                        folder_entries = self.list_folder(entry["id"], recursive=True, limit=limit)
                        entries.extend(folder_entries)
            
            return entries
        except Exception as e:
            logger.error(f"Error listing folder {folder_id}: {e}")
            raise
    
    def get_metadata(self, item_id: str) -> Dict[str, Any]:
        """
        Get metadata for a file or folder.
        
        Args:
            item_id: ID of the file or folder
            
        Returns:
            Dictionary containing metadata
        """
        try:
            # Get item
            response = self.connector.get_sharepoint_drive_item(self.site_id, self.drive_id, item_id)
            
            # Process item
            return self._process_item(response)
        except Exception as e:
            logger.error(f"Error getting metadata for item {item_id}: {e}")
            raise
    
    def download_file(self, item_id: str) -> bytes:
        """
        Download a file.
        
        Args:
            item_id: ID of the file
            
        Returns:
            File contents as bytes
        """
        try:
            # Get file metadata to ensure it exists and is a file
            metadata = self.get_metadata(item_id)
            if metadata["type"] != "file":
                raise ValueError(f"Item {item_id} is not a file")
            
            # Download file
            return self.connector.download_sharepoint_file(self.site_id, self.drive_id, item_id)
        except Exception as e:
            logger.error(f"Error downloading file {item_id}: {e}")
            raise
    
    def upload_file(self, local_path: Union[str, Path, BinaryIO], folder_id: str = "root", file_name: Optional[str] = None, overwrite: bool = False) -> Dict[str, Any]:
        """
        Upload a file to a SharePoint document library.
        
        Args:
            local_path: Path to the local file or file-like object
            folder_id: ID of the destination folder (default: "root")
            file_name: Name to use for the uploaded file (default: derived from local_path)
            overwrite: Whether to overwrite existing file
            
        Returns:
            Dictionary containing metadata of the uploaded file
        """
        try:
            # Get content
            if isinstance(local_path, (str, Path)):
                with open(local_path, "rb") as f:
                    content = f.read()
                # Use filename from path if not specified
                if file_name is None:
                    file_name = Path(local_path).name
            else:
                content = local_path.read()
                # Require filename for file-like objects
                if file_name is None:
                    raise ValueError("file_name must be specified when uploading from a file-like object")
            
            # For small files (< 4MB), use simple upload
            if len(content) < 4 * 1024 * 1024:
                # Create the upload URL
                endpoint = f"/sites/{self.site_id}/drives/{self.drive_id}/items/{folder_id}:/{file_name}:/content"
                
                # Set conflict behavior
                params = {}
                if overwrite:
                    params["@microsoft.graph.conflictBehavior"] = "replace"
                else:
                    params["@microsoft.graph.conflictBehavior"] = "fail"
                
                # Make request directly with client to upload binary content
                headers = {"Content-Type": "application/octet-stream"}
                response = self.connector.client.put(endpoint, params=params, data=content, headers=headers)
                
                if response.status_code >= 200 and response.status_code < 300:
                    return self._process_item(response.json())
                else:
                    raise ValueError(f"Failed to upload file: {response.status_code} {response.text}")
            else:
                # For larger files, we would use upload session
                # This is a simplified implementation
                raise NotImplementedError("Upload of files larger than 4MB is not implemented yet")
        except Exception as e:
            logger.error(f"Error uploading file {file_name} to folder {folder_id}: {e}")
            raise
    
    def create_folder(self, folder_name: str, parent_id: str = "root") -> Dict[str, Any]:
        """
        Create a folder in a SharePoint document library.
        
        Args:
            folder_name: Name of the folder to create
            parent_id: ID of the parent folder (default: "root")
            
        Returns:
            Dictionary containing metadata of the created folder
        """
        try:
            # Create folder
            endpoint = f"/sites/{self.site_id}/drives/{self.drive_id}/items/{parent_id}/children"
            
            data = {
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "fail"
            }
            
            response = self.connector.request("POST", endpoint, data=data)
            return self._process_item(response)
        except Exception as e:
            logger.error(f"Error creating folder {folder_name} in {parent_id}: {e}")
            raise
    
    def delete(self, item_id: str) -> bool:
        """
        Delete a file or folder.
        
        Args:
            item_id: ID of the file or folder
            
        Returns:
            True if deletion was successful
        """
        try:
            # Delete item
            endpoint = f"/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}"
            
            # Make request directly with client to handle 204 response
            response = self.connector.client.delete(endpoint)
            
            if response.status_code == 204:
                return True
            else:
                raise ValueError(f"Failed to delete item: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Error deleting item {item_id}: {e}")
            raise
    
    def search(self, query: str, max_results: int = 100, file_extensions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for files and folders in the SharePoint document library.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            file_extensions: List of file extensions to filter by
            
        Returns:
            List of dictionaries containing file/folder metadata
        """
        try:
            # Build query
            params = {
                "q": query,
                "$top": max_results
            }
            
            # Get search results
            endpoint = f"/sites/{self.site_id}/drives/{self.drive_id}/root/search"
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