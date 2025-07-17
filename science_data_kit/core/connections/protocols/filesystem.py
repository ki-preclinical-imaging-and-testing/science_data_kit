"""
Filesystem protocol for Science Data Kit connections.

This module provides the filesystem protocol class that defines the interface
for connections to filesystem-like data sources.
"""

import pandas as pd
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Union, BinaryIO

from .base import ConnectionProtocol


class FilesystemProtocol(ConnectionProtocol):
    """Protocol for filesystem-like connections."""
    
    @property
    def connection_type(self) -> str:
        """Return the connection type."""
        return "filesystem"
    
    @abstractmethod
    def list_directory(self, path: str = "/") -> List[Dict[str, Any]]:
        """
        List contents of a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            List of dictionaries containing metadata about directory contents
        """
        pass
    
    @abstractmethod
    def get_file_metadata(self, path: str) -> Dict[str, Any]:
        """
        Get metadata for a file.
        
        Args:
            path: Path to the file
            
        Returns:
            Dictionary containing file metadata
        """
        pass
    
    @abstractmethod
    def read_file(self, path: str) -> bytes:
        """
        Read a file and return its contents as bytes.
        
        Args:
            path: Path to the file
            
        Returns:
            File contents as bytes
        """
        pass
    
    @abstractmethod
    def write_file(self, path: str, content: Union[bytes, BinaryIO]) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            path: Path to the file
            content: Content to write (bytes or file-like object)
            
        Returns:
            Dictionary containing metadata about the written file
        """
        pass
    
    @abstractmethod
    def delete_file(self, path: str) -> bool:
        """
        Delete a file.
        
        Args:
            path: Path to the file
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def create_directory(self, path: str) -> Dict[str, Any]:
        """
        Create a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            Dictionary containing metadata about the created directory
        """
        pass
    
    @abstractmethod
    def delete_directory(self, path: str, recursive: bool = False) -> bool:
        """
        Delete a directory.
        
        Args:
            path: Path to the directory
            recursive: Whether to delete recursively
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    def read_as_dataframe(self, path: str, **kwargs) -> pd.DataFrame:
        """
        Read a file and return its contents as a pandas DataFrame.
        
        Args:
            path: Path to the file
            **kwargs: Additional arguments to pass to pandas
            
        Returns:
            Pandas DataFrame containing the file data
        """
        content = self.read_file(path)
        # Determine file type from extension
        if path.endswith('.csv'):
            return pd.read_csv(content, **kwargs)
        elif path.endswith('.xlsx') or path.endswith('.xls'):
            return pd.read_excel(content, **kwargs)
        elif path.endswith('.json'):
            return pd.read_json(content, **kwargs)
        elif path.endswith('.parquet'):
            return pd.read_parquet(content, **kwargs)
        else:
            raise ValueError(f"Unsupported file format for path: {path}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this connection."""
        capabilities = super().get_capabilities()
        capabilities.update({
            "browsable": True,
            "readable": True,
            "writable": True,
            "data_types": ["files", "directories"],
        })
        return capabilities