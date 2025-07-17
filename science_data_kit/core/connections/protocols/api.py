"""
API protocol for Science Data Kit connections.

This module provides the API protocol class that defines the interface
for connections to API-based data sources.
"""

import pandas as pd
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Union

from .base import ConnectionProtocol


class APIProtocol(ConnectionProtocol):
    """Protocol for API-based connections."""
    
    @property
    def connection_type(self) -> str:
        """Return the connection type."""
        return "api"
    
    @abstractmethod
    def list_resources(self, resource_type: str) -> List[Dict[str, Any]]:
        """
        List resources of a specific type.
        
        Args:
            resource_type: Type of resources to list
            
        Returns:
            List of dictionaries containing metadata about resources
        """
        pass
    
    @abstractmethod
    def get_resource(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """
        Get a specific resource.
        
        Args:
            resource_type: Type of the resource
            resource_id: ID of the resource
            
        Returns:
            Dictionary containing the resource data
        """
        pass
    
    @abstractmethod
    def execute_request(self, endpoint: str, method: str = "GET", 
                       params: Optional[Dict[str, Any]] = None, 
                       data: Optional[Dict[str, Any]] = None,
                       headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Execute a request to the API.
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method to use
            params: Query parameters (optional)
            data: Request body data (optional)
            headers: Request headers (optional)
            
        Returns:
            Dictionary containing the API response
        """
        pass
    
    @abstractmethod
    def get_data_as_dataframe(self, resource_type: str, 
                             query_params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Get data from the API as a pandas DataFrame.
        
        Args:
            resource_type: Type of resource to query
            query_params: Query parameters (optional)
            
        Returns:
            Pandas DataFrame containing the data
        """
        pass
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this connection."""
        capabilities = super().get_capabilities()
        capabilities.update({
            "searchable": True,
            "data_types": ["resources", "endpoints"],
            "supports_pagination": False,
            "supports_filtering": False,
        })
        return capabilities