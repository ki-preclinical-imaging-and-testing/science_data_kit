"""
Database protocol for Science Data Kit connections.

This module provides the database protocol class that defines the interface
for connections to database-like data sources.
"""

import pandas as pd
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from .base import ConnectionProtocol


class DatabaseProtocol(ConnectionProtocol):
    """Protocol for database-like connections."""
    
    @property
    def connection_type(self) -> str:
        """Return the connection type."""
        return "database"
    
    @abstractmethod
    def list_tables(self) -> List[Dict[str, Any]]:
        """
        List tables in the database.
        
        Returns:
            List of dictionaries containing metadata about tables
        """
        pass
    
    @abstractmethod
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get schema for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary containing table schema
        """
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
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
    def execute_statement(self, statement: str, params: Optional[Dict[str, Any]] = None) -> int:
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
    def get_table_data(self, table_name: str, limit: int = 1000, offset: int = 0) -> pd.DataFrame:
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
    def get_table_count(self, table_name: str) -> int:
        """
        Get the number of rows in a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows in the table
        """
        pass
    
    @abstractmethod
    def import_dataframe(self, df: pd.DataFrame, table_name: str, 
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
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this connection."""
        capabilities = super().get_capabilities()
        capabilities.update({
            "queryable": True,
            "data_types": ["tables", "views"],
            "supports_transactions": False,
        })
        return capabilities