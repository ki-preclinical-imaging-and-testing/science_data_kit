"""
Base protocol class for Science Data Kit connections.

This module provides the base protocol class that all connection protocols must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ConnectionProtocol(ABC):
    """Base protocol all connections must implement."""
    
    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> None:
        """
        Establish connection with the service.
        
        Args:
            config: Configuration dictionary for the connection
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Clean up connection."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Verify connection is working.
        
        Returns:
            True if connection is working, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def connection_type(self) -> str:
        """
        Return the type of connection (filesystem, api, database, etc.).
        
        Returns:
            String representing the connection type
        """
        pass
    
    @property
    def is_connected(self) -> bool:
        """
        Check if the connection is currently established.
        
        Returns:
            True if connected, False otherwise
        """
        return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this connection.
        
        Returns:
            Dictionary of capabilities
        """
        return {}
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this connection.
        
        Returns:
            Dictionary of metadata
        """
        return {
            "type": self.connection_type,
            "capabilities": self.get_capabilities(),
        }