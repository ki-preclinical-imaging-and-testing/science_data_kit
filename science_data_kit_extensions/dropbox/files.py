"""
Science Data Kit - Dropbox Extension
Files Module

This module provides functionality for working with files and folders in Dropbox.
"""

import os
import io
import logging
from typing import Dict, Any, Optional, List, Union, BinaryIO, Tuple
from datetime import datetime
from pathlib import Path

from dropbox import Dropbox
from dropbox.files import (
    FileMetadata, 
    FolderMetadata, 
    ListFolderResult, 
    ListFolderError,
    SearchResult,
    SearchMatch,
    SearchMatchType,
    DeletedMetadata
)
from dropbox.exceptions import ApiError

from .connector import DropboxConnector

logger = logging.getLogger(__name__)

class DropboxFileManager:
    """
    Class for managing files and folders in Dropbox.
    
    This class provides methods for listing, navigating, downloading, and uploading
    files and folders in Dropbox.
    """
    
    def __init__(self, connector: DropboxConnector):
        """
        Initialize the file manager.
        
        Args:
            connector: DropboxConnector instance for API access
        """
        self.connector = connector
        
        # Ensure connector is connected
        if not connector.is_connected():
            raise ConnectionError("Dropbox connector is not connected")
            
        self.client = connector.client
    
    def list_folder(
        self, 
        path: str = "", 
        recursive: bool = False, 
        include_deleted: bool = False,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List files and folders in the specified path.
        
        Args:
            path: Path to list (empty for root)
            recursive: Whether to list recursively
            include_deleted: Whether to include deleted files
            limit: Maximum number of entries to return
            
        Returns:
            List of file/folder metadata dictionaries
        """
        try:
            # Ensure path starts with a slash
            if path and not path.startswith('/'):
                path = f"/{path}"
                
            result = self.client.files_list_folder(
                path,
                recursive=recursive,
                include_deleted=include_deleted,
                limit=limit
            )
            
            entries = []
            self._process_list_result(result, entries)
            
            # Continue fetching if there are more entries
            while result.has_more:
                result = self.client.files_list_folder_continue(result.cursor)
                self._process_list_result(result, entries)
                
                # Stop if we've reached the limit
                if limit and len(entries) >= limit:
                    entries = entries[:limit]
                    break
                    
            return entries
        except ApiError as e:
            logger.error(f"Error listing folder {path}: {e}")
            raise
    
    def _process_list_result(
        self, 
        result: ListFolderResult, 
        entries: List[Dict[str, Any]]
    ) -> None:
        """
        Process a list folder result and add entries to the list.
        
        Args:
            result: ListFolderResult from Dropbox API
            entries: List to add entries to
        """
        for entry in result.entries:
            if isinstance(entry, FileMetadata):
                entries.append({
                    'type': 'file',
                    'id': entry.id,
                    'name': entry.name,
                    'path': entry.path_display,
                    'size': entry.size,
                    'modified': entry.client_modified,
                    'content_hash': entry.content_hash,
                    'media_info': entry.media_info._value if hasattr(entry, 'media_info') and entry.media_info else None,
                    'sharing_info': entry.sharing_info._asdict() if hasattr(entry, 'sharing_info') and entry.sharing_info else None
                })
            elif isinstance(entry, FolderMetadata):
                entries.append({
                    'type': 'folder',
                    'id': entry.id,
                    'name': entry.name,
                    'path': entry.path_display,
                    'sharing_info': entry.sharing_info._asdict() if hasattr(entry, 'sharing_info') and entry.sharing_info else None
                })
            elif isinstance(entry, DeletedMetadata):
                entries.append({
                    'type': 'deleted',
                    'name': entry.name,
                    'path': entry.path_display
                })
    
    def get_metadata(self, path: str) -> Dict[str, Any]:
        """
        Get metadata for a file or folder.
        
        Args:
            path: Path to the file or folder
            
        Returns:
            Metadata dictionary
        """
        try:
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = f"/{path}"
                
            metadata = self.client.files_get_metadata(path)
            
            if isinstance(metadata, FileMetadata):
                return {
                    'type': 'file',
                    'id': metadata.id,
                    'name': metadata.name,
                    'path': metadata.path_display,
                    'size': metadata.size,
                    'modified': metadata.client_modified,
                    'content_hash': metadata.content_hash,
                    'media_info': metadata.media_info._value if hasattr(metadata, 'media_info') and metadata.media_info else None,
                    'sharing_info': metadata.sharing_info._asdict() if hasattr(metadata, 'sharing_info') and metadata.sharing_info else None
                }
            elif isinstance(metadata, FolderMetadata):
                return {
                    'type': 'folder',
                    'id': metadata.id,
                    'name': metadata.name,
                    'path': metadata.path_display,
                    'sharing_info': metadata.sharing_info._asdict() if hasattr(metadata, 'sharing_info') and metadata.sharing_info else None
                }
            else:
                return {
                    'type': 'unknown',
                    'name': metadata.name,
                    'path': metadata.path_display
                }
        except ApiError as e:
            logger.error(f"Error getting metadata for {path}: {e}")
            raise
    
    def download_file(self, path: str) -> Tuple[bytes, Dict[str, Any]]:
        """
        Download a file from Dropbox.
        
        Args:
            path: Path to the file
            
        Returns:
            Tuple of (file_content, metadata)
        """
        try:
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = f"/{path}"
                
            metadata, response = self.client.files_download(path)
            
            return response.content, {
                'type': 'file',
                'id': metadata.id,
                'name': metadata.name,
                'path': metadata.path_display,
                'size': metadata.size,
                'modified': metadata.client_modified,
                'content_hash': metadata.content_hash
            }
        except ApiError as e:
            logger.error(f"Error downloading file {path}: {e}")
            raise
    
    def upload_file(
        self, 
        local_path: Union[str, Path, BinaryIO], 
        dropbox_path: str,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Upload a file to Dropbox.
        
        Args:
            local_path: Path to the local file or file-like object
            dropbox_path: Path in Dropbox to upload to
            overwrite: Whether to overwrite existing files
            
        Returns:
            Metadata dictionary for the uploaded file
        """
        try:
            # Ensure dropbox_path starts with a slash
            if not dropbox_path.startswith('/'):
                dropbox_path = f"/{dropbox_path}"
                
            mode = dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add
            
            # Handle different input types
            if isinstance(local_path, (str, Path)):
                with open(local_path, 'rb') as f:
                    metadata = self.client.files_upload(f.read(), dropbox_path, mode=mode)
            else:
                # Assume it's a file-like object
                metadata = self.client.files_upload(local_path.read(), dropbox_path, mode=mode)
                
            return {
                'type': 'file',
                'id': metadata.id,
                'name': metadata.name,
                'path': metadata.path_display,
                'size': metadata.size,
                'modified': metadata.client_modified,
                'content_hash': metadata.content_hash
            }
        except ApiError as e:
            logger.error(f"Error uploading to {dropbox_path}: {e}")
            raise
    
    def create_folder(self, path: str) -> Dict[str, Any]:
        """
        Create a folder in Dropbox.
        
        Args:
            path: Path for the new folder
            
        Returns:
            Metadata dictionary for the created folder
        """
        try:
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = f"/{path}"
                
            metadata = self.client.files_create_folder_v2(path).metadata
            
            return {
                'type': 'folder',
                'id': metadata.id,
                'name': metadata.name,
                'path': metadata.path_display
            }
        except ApiError as e:
            logger.error(f"Error creating folder {path}: {e}")
            raise
    
    def delete(self, path: str) -> Dict[str, Any]:
        """
        Delete a file or folder in Dropbox.
        
        Args:
            path: Path to delete
            
        Returns:
            Metadata dictionary for the deleted item
        """
        try:
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = f"/{path}"
                
            metadata = self.client.files_delete_v2(path).metadata
            
            if isinstance(metadata, FileMetadata):
                return {
                    'type': 'file',
                    'id': metadata.id,
                    'name': metadata.name,
                    'path': metadata.path_display
                }
            elif isinstance(metadata, FolderMetadata):
                return {
                    'type': 'folder',
                    'id': metadata.id,
                    'name': metadata.name,
                    'path': metadata.path_display
                }
            else:
                return {
                    'type': 'unknown',
                    'name': metadata.name,
                    'path': metadata.path_display
                }
        except ApiError as e:
            logger.error(f"Error deleting {path}: {e}")
            raise
    
    def search(
        self, 
        query: str, 
        path: str = "", 
        max_results: int = 100,
        file_extensions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for files and folders in Dropbox.
        
        Args:
            query: Search query
            path: Path to search in (empty for root)
            max_results: Maximum number of results to return
            file_extensions: List of file extensions to filter by
            
        Returns:
            List of matching file/folder metadata dictionaries
        """
        try:
            # Ensure path starts with a slash if not empty
            if path and not path.startswith('/'):
                path = f"/{path}"
                
            result = self.client.files_search_v2(query, path, max_results=max_results)
            
            matches = []
            for match in result.matches:
                metadata = match.metadata.metadata
                
                # Skip if not matching file extension filter
                if (file_extensions and 
                    isinstance(metadata, FileMetadata) and 
                    not any(metadata.name.lower().endswith(ext.lower()) for ext in file_extensions)):
                    continue
                    
                if isinstance(metadata, FileMetadata):
                    matches.append({
                        'type': 'file',
                        'id': metadata.id,
                        'name': metadata.name,
                        'path': metadata.path_display,
                        'size': metadata.size,
                        'modified': metadata.client_modified,
                        'content_hash': metadata.content_hash,
                        'match_type': match.match_type._tag
                    })
                elif isinstance(metadata, FolderMetadata):
                    matches.append({
                        'type': 'folder',
                        'id': metadata.id,
                        'name': metadata.name,
                        'path': metadata.path_display,
                        'match_type': match.match_type._tag
                    })
                    
            return matches
        except ApiError as e:
            logger.error(f"Error searching for '{query}': {e}")
            raise