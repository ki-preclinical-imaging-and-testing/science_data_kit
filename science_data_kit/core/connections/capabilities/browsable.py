"""
Browsable capability mixin for Science Data Kit connections.

This module provides a mixin that defines the browsable capability for connections,
allowing them to list contents and navigate through hierarchical structures.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional


class Browsable:
    """Mixin for connections that support directory/content listing."""
    
    @abstractmethod
    def list_contents(self, path: str = "/") -> List[Dict[str, Any]]:
        """
        List contents at the given path.
        
        Args:
            path: Path to list contents from
            
        Returns:
            List of dictionaries containing metadata about items
        """
        pass
    
    @abstractmethod
    def get_metadata(self, path: str) -> Dict[str, Any]:
        """
        Get metadata for a specific item.
        
        Args:
            path: Path to the item
            
        Returns:
            Dictionary containing item metadata
        """
        pass
    
    def is_directory(self, path: str) -> bool:
        """
        Check if the path points to a directory/folder.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is a directory, False otherwise
        """
        metadata = self.get_metadata(path)
        return metadata.get("type") == "directory" or metadata.get("type") == "folder"
    
    def is_file(self, path: str) -> bool:
        """
        Check if the path points to a file.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is a file, False otherwise
        """
        metadata = self.get_metadata(path)
        return metadata.get("type") == "file"
    
    def get_parent_path(self, path: str) -> str:
        """
        Get the parent path of the given path.
        
        Args:
            path: Path to get parent for
            
        Returns:
            Parent path
        """
        if path == "/" or path == "":
            return "/"
        
        if path.endswith("/"):
            path = path[:-1]
            
        last_slash = path.rfind("/")
        if last_slash == 0:
            return "/"
        elif last_slash > 0:
            return path[:last_slash]
        else:
            return "/"