"""
Local Storage Provider for Science Data Kit

This module provides a local storage provider for accessing CSV and Excel files
stored on the local file system or network mountpoints.
"""

import os
import io
import pandas as pd
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from ...providers.registry import BaseProvider


class LocalStorageProvider(BaseProvider):
    """Local storage file provider for CSV/Excel data access"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the local storage provider.
        
        Args:
            config: Configuration dictionary containing base_path and optional allowed_paths
                   base_path: Root directory for file access
                   allowed_paths: List of allowed paths (for security)
        """
        super().__init__(config)
        self.base_path = None
        self.allowed_paths = []
    
    async def initialize(self) -> bool:
        """
        Initialize local storage access.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Get base path from config
            base_path = self.config.get("base_path")
            if not base_path:
                print("Base path not found in configuration")
                return False
            
            # Convert to absolute path and check if it exists
            base_path = os.path.abspath(os.path.expanduser(base_path))
            if not os.path.exists(base_path):
                print(f"Base path does not exist: {base_path}")
                return False
            
            self.base_path = base_path
            
            # Get allowed paths (optional)
            allowed_paths = self.config.get("allowed_paths", [])
            if allowed_paths:
                self.allowed_paths = [os.path.abspath(os.path.expanduser(p)) for p in allowed_paths]
            
            self.is_initialized = True
            return True
        
        except Exception as e:
            print(f"Error initializing local storage provider: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """
        Verify local storage access is working.
        
        Returns:
            True if the access is healthy, False otherwise
        """
        if not self.is_initialized or not self.base_path:
            return False
        
        try:
            # Check if base path exists and is readable
            return os.path.exists(self.base_path) and os.access(self.base_path, os.R_OK)
        except Exception as e:
            print(f"Local storage health check failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return provider capabilities.
        
        Returns:
            Dictionary of provider capabilities
        """
        return {
            "data_types": ["files", "csv", "excel"],
            "real_time": True,
            "formats": ["csv", "xlsx", "xls"],
            "max_size": "system-dependent"
        }
    
    def _is_path_allowed(self, path: str) -> bool:
        """
        Check if a path is allowed based on security settings.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is allowed, False otherwise
        """
        # Always allow paths under base_path
        if os.path.commonpath([path, self.base_path]) == self.base_path:
            return True
        
        # Check against allowed_paths if specified
        if self.allowed_paths:
            for allowed_path in self.allowed_paths:
                if os.path.commonpath([path, allowed_path]) == allowed_path:
                    return True
            return False
        
        # If no allowed_paths specified, only allow paths under base_path
        return False
    
    def _get_absolute_path(self, relative_path: str) -> str:
        """
        Convert a relative path to an absolute path.
        
        Args:
            relative_path: Path relative to base_path
            
        Returns:
            Absolute path
        """
        # If path is empty, use base_path
        if not relative_path:
            return self.base_path
        
        # Join with base_path if not already absolute
        if os.path.isabs(relative_path):
            path = relative_path
        else:
            path = os.path.join(self.base_path, relative_path)
        
        # Normalize path
        return os.path.abspath(path)
    
    async def list_files(self, folder_path: str = "", file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        List CSV/Excel files in local folder.
        
        Args:
            folder_path: Path to the folder (relative to base_path)
            file_types: List of file extensions to filter by (e.g., ["csv", "xlsx"])
            
        Returns:
            List of file metadata dictionaries
        """
        if not self.is_initialized or not self.base_path:
            raise Exception("Local storage provider not initialized")
        
        if file_types is None:
            file_types = ["csv", "xlsx", "xls"]
        
        try:
            # Get absolute path
            abs_path = self._get_absolute_path(folder_path)
            
            # Check if path is allowed
            if not self._is_path_allowed(abs_path):
                raise PermissionError(f"Access to path not allowed: {abs_path}")
            
            # Check if path exists
            if not os.path.exists(abs_path):
                raise FileNotFoundError(f"Path does not exist: {abs_path}")
            
            # Check if path is a directory
            if not os.path.isdir(abs_path):
                raise NotADirectoryError(f"Path is not a directory: {abs_path}")
            
            files = []
            
            # List directory contents
            for entry in os.scandir(abs_path):
                if entry.is_dir():
                    # Include directories for navigation
                    rel_path = os.path.relpath(entry.path, self.base_path)
                    files.append({
                        "id": rel_path,
                        "name": entry.name,
                        "path": rel_path,
                        "type": "folder"
                    })
                elif entry.is_file():
                    # Check if file has one of the specified extensions
                    file_ext = os.path.splitext(entry.name)[1].lower().lstrip(".")
                    if file_ext in file_types:
                        rel_path = os.path.relpath(entry.path, self.base_path)
                        stat = entry.stat()
                        files.append({
                            "id": rel_path,
                            "name": entry.name,
                            "path": rel_path,
                            "size": stat.st_size,
                            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "type": file_ext
                        })
            
            return files
        
        except Exception as e:
            print(f"Error listing local files: {str(e)}")
            raise
    
    async def download_file_data(self, file_path: str) -> pd.DataFrame:
        """
        Read file and return as pandas DataFrame.
        
        Args:
            file_path: Path to the file (relative to base_path)
            
        Returns:
            Pandas DataFrame containing the file data
        """
        if not self.is_initialized or not self.base_path:
            raise Exception("Local storage provider not initialized")
        
        try:
            # Get absolute path
            abs_path = self._get_absolute_path(file_path)
            
            # Check if path is allowed
            if not self._is_path_allowed(abs_path):
                raise PermissionError(f"Access to file not allowed: {abs_path}")
            
            # Check if file exists
            if not os.path.exists(abs_path):
                raise FileNotFoundError(f"File does not exist: {abs_path}")
            
            # Check if path is a file
            if not os.path.isfile(abs_path):
                raise IsADirectoryError(f"Path is not a file: {abs_path}")
            
            # Detect file type
            file_ext = os.path.splitext(abs_path)[1].lower()
            
            # Parse with appropriate pandas function
            if file_ext == '.csv':
                return pd.read_csv(abs_path)
            elif file_ext in ['.xlsx', '.xls']:
                return pd.read_excel(abs_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        
        except Exception as e:
            print(f"Error reading local file: {str(e)}")
            raise
    
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata without reading the file.
        
        Args:
            file_path: Path to the file (relative to base_path)
            
        Returns:
            Dictionary containing file metadata
        """
        if not self.is_initialized or not self.base_path:
            raise Exception("Local storage provider not initialized")
        
        try:
            # Get absolute path
            abs_path = self._get_absolute_path(file_path)
            
            # Check if path is allowed
            if not self._is_path_allowed(abs_path):
                raise PermissionError(f"Access to file not allowed: {abs_path}")
            
            # Check if file exists
            if not os.path.exists(abs_path):
                raise FileNotFoundError(f"File does not exist: {abs_path}")
            
            # Check if path is a file
            if not os.path.isfile(abs_path):
                raise IsADirectoryError(f"Path is not a file: {abs_path}")
            
            # Get file stats
            stat = os.stat(abs_path)
            
            # Get relative path
            rel_path = os.path.relpath(abs_path, self.base_path)
            
            return {
                "id": rel_path,
                "name": os.path.basename(abs_path),
                "path": rel_path,
                "size": stat.st_size,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "type": os.path.splitext(abs_path)[1].lower().lstrip(".")
            }
        
        except Exception as e:
            print(f"Error getting local file info: {str(e)}")
            raise