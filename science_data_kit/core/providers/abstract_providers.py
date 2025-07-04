"""
Abstract Provider Classes for Science Data Kit

This module provides abstract base classes for different types of providers,
defining the interfaces that specific provider implementations must follow.
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple

from .registry import BaseProvider


class StorageProvider(BaseProvider, ABC):
    """
    Abstract base class for storage providers.
    
    This class defines the interface that all storage providers must implement,
    including methods for listing files, downloading file data, and getting file info.
    """
    
    @abstractmethod
    async def list_files(self, folder_path: str = "", file_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List files in a folder.
        
        Args:
            folder_path: Path to the folder
            file_types: List of file extensions to filter by (e.g., ["csv", "xlsx"])
            
        Returns:
            List of file metadata dictionaries
        """
        pass
    
    @abstractmethod
    async def download_file_data(self, file_path: str) -> pd.DataFrame:
        """
        Download file and return as pandas DataFrame.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Pandas DataFrame containing the file data
        """
        pass
    
    @abstractmethod
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata without downloading.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file metadata
        """
        pass


class DatabaseProvider(BaseProvider, ABC):
    """
    Abstract base class for database providers.
    
    This class defines the interface that all database providers must implement,
    including methods for listing tables, executing queries, and working with table data.
    """
    
    @abstractmethod
    async def list_tables(self) -> List[Dict[str, Any]]:
        """
        List tables in the database.
        
        Returns:
            List of table metadata dictionaries
        """
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a query and return results as a DataFrame.
        
        Args:
            query: Query to execute
            params: Parameters for the query (optional)
            
        Returns:
            Pandas DataFrame containing the query results
        """
        pass
    
    @abstractmethod
    async def execute_statement(self, statement: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute a statement (INSERT, UPDATE, DELETE) and return affected rows.
        
        Args:
            statement: Statement to execute
            params: Parameters for the statement (optional)
            
        Returns:
            Number of affected rows
        """
        pass
    
    @abstractmethod
    async def get_table_data(self, table_name: str, limit: int = 1000, offset: int = 0) -> pd.DataFrame:
        """
        Get data from a table.
        
        Args:
            table_name: Name of the table
            limit: Maximum number of rows to return
            offset: Number of rows to skip
            
        Returns:
            Pandas DataFrame containing the table data
        """
        pass
    
    @abstractmethod
    async def get_table_count(self, table_name: str) -> int:
        """
        Get the number of rows in a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows in the table
        """
        pass
    
    @abstractmethod
    async def export_table_to_dataframe(self, table_name: str) -> pd.DataFrame:
        """
        Export a table to a pandas DataFrame.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Pandas DataFrame containing the table data
        """
        pass
    
    @abstractmethod
    async def import_dataframe_to_table(self, df: pd.DataFrame, table_name: str, 
                                       if_exists: str = 'fail', index: bool = False) -> bool:
        """
        Import a pandas DataFrame to a database table.
        
        Args:
            df: Pandas DataFrame to import
            table_name: Name of the target table
            if_exists: Action if table exists ('fail', 'replace', or 'append')
            index: Whether to include DataFrame index as a column
            
        Returns:
            True if import was successful, False otherwise
        """
        pass


class APIProvider(BaseProvider, ABC):
    """
    Abstract base class for API providers.
    
    This class defines the interface that all API providers must implement,
    including methods for listing resources and retrieving data from the API.
    """
    
    @abstractmethod
    async def list_resources(self, resource_type: str) -> List[Dict[str, Any]]:
        """
        List resources of a specific type.
        
        Args:
            resource_type: Type of resources to list
            
        Returns:
            List of resource metadata dictionaries
        """
        pass
    
    @abstractmethod
    async def get_resource(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
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
    async def execute_api_request(self, endpoint: str, method: str = "GET", 
                                 params: Optional[Dict[str, Any]] = None, 
                                 data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a request to the API.
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method to use
            params: Query parameters (optional)
            data: Request body data (optional)
            
        Returns:
            Dictionary containing the API response
        """
        pass
    
    @abstractmethod
    async def get_data_as_dataframe(self, resource_type: str, 
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