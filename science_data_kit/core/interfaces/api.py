"""
API Interfaces for Science Data Kit

This module defines interfaces for API managers and connectors,
providing a standardized way to interact with different API systems.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple

import pandas as pd


class APIInterface(ABC):
    """
    Abstract base class for API interfaces.
    
    This interface defines the core methods that all API managers should implement,
    regardless of the specific API they interact with.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the API service.
        
        Returns:
            True if connection was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def execute_query(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None, 
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute a query on the API.
        
        Args:
            resource_path: The API endpoint or resource path.
            query_parameters: Optional parameters for the query.
            use_cache: Whether to use cached results if available.
            
        Returns:
            Dictionary containing the API response.
        """
        pass
    
    @abstractmethod
    def query_to_dataframe(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None,
                          use_cache: bool = True) -> pd.DataFrame:
        """
        Execute a query and return the results as a pandas DataFrame.
        
        Args:
            resource_path: The API endpoint or resource path.
            query_parameters: Optional parameters for the query.
            use_cache: Whether to use cached results if available.
            
        Returns:
            A pandas DataFrame containing the query results.
        """
        pass
    
    @abstractmethod
    def build_query(self, resource_path: str, **kwargs) -> str:
        """
        Build a query string for the API.
        
        Args:
            resource_path: The API endpoint or resource path.
            **kwargs: Additional parameters for the query.
            
        Returns:
            The constructed query string.
        """
        pass


class MSGraphAPIInterface(APIInterface):
    """
    Interface for Microsoft Graph API managers.
    
    This interface extends the base APIInterface with methods specific to Microsoft Graph API.
    """
    
    @abstractmethod
    def get_users(self, query_parameters: Optional[Dict[str, Any]] = None, 
                 use_cache: bool = True) -> Dict[str, Any]:
        """
        Get users from Microsoft Graph API.
        
        Args:
            query_parameters: Optional parameters for the query.
            use_cache: Whether to use cached results if available.
            
        Returns:
            Dictionary containing user data.
        """
        pass
    
    @abstractmethod
    def get_groups(self, query_parameters: Optional[Dict[str, Any]] = None, 
                  use_cache: bool = True) -> Dict[str, Any]:
        """
        Get groups from Microsoft Graph API.
        
        Args:
            query_parameters: Optional parameters for the query.
            use_cache: Whether to use cached results if available.
            
        Returns:
            Dictionary containing group data.
        """
        pass
    
    @abstractmethod
    def get_me(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get current user information from Microsoft Graph API.
        
        Args:
            use_cache: Whether to use cached results if available.
            
        Returns:
            Dictionary containing current user data.
        """
        pass
    
    @abstractmethod
    def get_my_messages(self, query_parameters: Optional[Dict[str, Any]] = None, 
                       use_cache: bool = True) -> Dict[str, Any]:
        """
        Get messages for the current user from Microsoft Graph API.
        
        Args:
            query_parameters: Optional parameters for the query.
            use_cache: Whether to use cached results if available.
            
        Returns:
            Dictionary containing message data.
        """
        pass
    
    @abstractmethod
    def get_my_events(self, query_parameters: Optional[Dict[str, Any]] = None, 
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        Get events for the current user from Microsoft Graph API.
        
        Args:
            query_parameters: Optional parameters for the query.
            use_cache: Whether to use cached results if available.
            
        Returns:
            Dictionary containing event data.
        """
        pass
    
    @abstractmethod
    def get_my_files(self, query_parameters: Optional[Dict[str, Any]] = None, 
                    use_cache: bool = True) -> Dict[str, Any]:
        """
        Get files for the current user from Microsoft Graph API.
        
        Args:
            query_parameters: Optional parameters for the query.
            use_cache: Whether to use cached results if available.
            
        Returns:
            Dictionary containing file data.
        """
        pass