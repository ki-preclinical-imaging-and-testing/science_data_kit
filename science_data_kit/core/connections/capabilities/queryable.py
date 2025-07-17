"""
Queryable capability mixin for Science Data Kit connections.

This module provides a mixin that defines the queryable capability for connections,
allowing them to execute queries against structured data sources.
"""

import pandas as pd
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Union


class Queryable:
    """Mixin for connections that support query execution."""
    
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
    def get_schema(self, object_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get schema information for the data source or a specific object.
        
        Args:
            object_name: Name of the object (table, collection, etc.) to get schema for (optional)
            
        Returns:
            Dictionary containing schema information
        """
        pass
    
    def count_records(self, object_name: str, filter_condition: Optional[str] = None) -> int:
        """
        Count records in an object, optionally with a filter condition.
        
        Args:
            object_name: Name of the object (table, collection, etc.)
            filter_condition: Optional filter condition
            
        Returns:
            Number of records
        """
        query = f"SELECT COUNT(*) FROM {object_name}"
        if filter_condition:
            query += f" WHERE {filter_condition}"
        
        result = self.execute_query(query)
        return result.iloc[0, 0]
    
    def list_objects(self) -> List[str]:
        """
        List available objects (tables, collections, etc.).
        
        Returns:
            List of object names
        """
        schema = self.get_schema()
        return schema.get("objects", [])
    
    def sample_data(self, object_name: str, sample_size: int = 10) -> pd.DataFrame:
        """
        Get a sample of data from an object.
        
        Args:
            object_name: Name of the object (table, collection, etc.)
            sample_size: Number of records to sample
            
        Returns:
            Pandas DataFrame containing the sample data
        """
        query = f"SELECT * FROM {object_name} LIMIT {sample_size}"
        return self.execute_query(query)
    
    def describe_data(self, object_name: str) -> pd.DataFrame:
        """
        Get descriptive statistics for an object.
        
        Args:
            object_name: Name of the object (table, collection, etc.)
            
        Returns:
            Pandas DataFrame containing descriptive statistics
        """
        sample = self.sample_data(object_name, 1000)
        return sample.describe()