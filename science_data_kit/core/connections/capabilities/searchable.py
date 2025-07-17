"""
Searchable capability mixin for Science Data Kit connections.

This module provides a mixin that defines the searchable capability for connections,
allowing them to search for content based on various criteria.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional


class Searchable:
    """Mixin for connections that support search functionality."""
    
    @abstractmethod
    def search(self, query: str, path: str = "/", **kwargs) -> List[Dict[str, Any]]:
        """
        Search for items matching the query.
        
        Args:
            query: Search query string
            path: Base path to search from (optional)
            **kwargs: Additional search parameters
            
        Returns:
            List of dictionaries containing metadata about matching items
        """
        pass
    
    def search_by_name(self, name: str, path: str = "/", exact_match: bool = False) -> List[Dict[str, Any]]:
        """
        Search for items by name.
        
        Args:
            name: Name to search for
            path: Base path to search from (optional)
            exact_match: Whether to require exact name match
            
        Returns:
            List of dictionaries containing metadata about matching items
        """
        if exact_match:
            return self.search(f"name:'{name}'", path=path)
        else:
            return self.search(f"name:{name}", path=path)
    
    def search_by_content(self, content: str, path: str = "/") -> List[Dict[str, Any]]:
        """
        Search for items containing specific content.
        
        Args:
            content: Content to search for
            path: Base path to search from (optional)
            
        Returns:
            List of dictionaries containing metadata about matching items
        """
        return self.search(f"content:{content}", path=path)
    
    def search_by_type(self, file_type: str, path: str = "/") -> List[Dict[str, Any]]:
        """
        Search for items of a specific type.
        
        Args:
            file_type: Type to search for (e.g., "pdf", "image", "document")
            path: Base path to search from (optional)
            
        Returns:
            List of dictionaries containing metadata about matching items
        """
        return self.search(f"type:{file_type}", path=path)
    
    def search_by_date(self, date_range: str, path: str = "/") -> List[Dict[str, Any]]:
        """
        Search for items within a date range.
        
        Args:
            date_range: Date range specification (e.g., "2023-01-01..2023-12-31")
            path: Base path to search from (optional)
            
        Returns:
            List of dictionaries containing metadata about matching items
        """
        return self.search(f"date:{date_range}", path=path)