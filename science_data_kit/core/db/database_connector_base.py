"""
Database Connector Base Classes for Science Data Kit

This module provides abstract base classes for database connectors, defining
the interfaces that specific database connector implementations must follow.
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple

class DatabaseConnectorBase(ABC):
    """
    Abstract base class for all database connectors.
    
    This class defines the common interface that all database connectors must implement,
    including methods for connection management, query execution, and data retrieval.
    """
    
    @abstractmethod
    def __init__(self, config: Optional[Dict[str, Any]] = None, config_file: Optional[str] = None):
        """
        Initialize the database connector with configuration.
        
        Args:
            config: Configuration dictionary for the connector
            config_file: Path to a configuration file
        """
        pass
    
    @abstractmethod
    def _connect(self, connection_name: Optional[str] = None):
        """
        Establish a connection to the database.
        
        Args:
            connection_name: Name of the connection to establish
        """
        pass
    
    @abstractmethod
    def close(self, connection_name: Optional[str] = None):
        """
        Close the database connection.
        
        Args:
            connection_name: Name of the connection to close
        """
        pass
    
    @abstractmethod
    def is_connected(self, connection_name: Optional[str] = None) -> bool:
        """
        Check if the database connection is active.
        
        Args:
            connection_name: Name of the connection to check
            
        Returns:
            True if the connection is active, False otherwise
        """
        pass
    
    @abstractmethod
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None, 
                     connection_name: Optional[str] = None) -> Any:
        """
        Execute a query on the database.
        
        Args:
            query: Query to execute
            parameters: Parameters for the query
            connection_name: Name of the connection to use
            
        Returns:
            Query results
        """
        pass
    
    @abstractmethod
    def query_to_dataframe(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                          connection_name: Optional[str] = None) -> pd.DataFrame:
        """
        Execute a query and return results as a pandas DataFrame.
        
        Args:
            query: Query to execute
            parameters: Parameters for the query
            connection_name: Name of the connection to use
            
        Returns:
            Pandas DataFrame containing the query results
        """
        pass
    
    @abstractmethod
    def query_to_value(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                      connection_name: Optional[str] = None) -> Any:
        """
        Execute a query and return a single value.
        
        Args:
            query: Query to execute
            parameters: Parameters for the query
            connection_name: Name of the connection to use
            
        Returns:
            Single value from the query result
        """
        pass


class GraphDatabaseConnector(DatabaseConnectorBase):
    """
    Abstract base class for graph database connectors.
    
    This class extends the DatabaseConnectorBase with methods specific to graph databases,
    such as node and relationship operations.
    """
    
    @abstractmethod
    def fetch_nodes(self, label: str, properties: Optional[List[str]] = None, 
                   limit: int = 100, connection_name: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch nodes with a specific label from the graph database.
        
        Args:
            label: Node label to fetch
            properties: List of properties to include
            limit: Maximum number of nodes to fetch
            connection_name: Name of the connection to use
            
        Returns:
            Pandas DataFrame containing the nodes
        """
        pass
    
    @abstractmethod
    def fetch_relationships(self, source_label: str, relationship_type: str, target_label: str,
                           limit: int = 100, connection_name: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch relationships between nodes from the graph database.
        
        Args:
            source_label: Label of the source nodes
            relationship_type: Type of relationship to fetch
            target_label: Label of the target nodes
            limit: Maximum number of relationships to fetch
            connection_name: Name of the connection to use
            
        Returns:
            Pandas DataFrame containing the relationships
        """
        pass
    
    @abstractmethod
    def create_node(self, label: str, properties: Dict[str, Any], 
                   connection_name: Optional[str] = None) -> str:
        """
        Create a new node in the graph database.
        
        Args:
            label: Label for the new node
            properties: Properties for the new node
            connection_name: Name of the connection to use
            
        Returns:
            ID of the created node
        """
        pass
    
    @abstractmethod
    def create_relationship(self, source_id: str, target_id: str, relationship_type: str,
                           properties: Optional[Dict[str, Any]] = None,
                           connection_name: Optional[str] = None) -> str:
        """
        Create a new relationship between nodes in the graph database.
        
        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            relationship_type: Type of relationship to create
            properties: Properties for the new relationship
            connection_name: Name of the connection to use
            
        Returns:
            ID of the created relationship
        """
        pass


class RelationalDatabaseConnector(DatabaseConnectorBase):
    """
    Abstract base class for relational database connectors.
    
    This class extends the DatabaseConnectorBase with methods specific to relational databases,
    such as table operations and transactions.
    """
    
    @abstractmethod
    def list_tables(self, schema: str = "public", 
                   connection_name: Optional[str] = None) -> List[str]:
        """
        List tables in the database.
        
        Args:
            schema: Schema to list tables from
            connection_name: Name of the connection to use
            
        Returns:
            List of table names
        """
        pass
    
    @abstractmethod
    def get_table_schema(self, table_name: str, schema: str = "public",
                        connection_name: Optional[str] = None) -> pd.DataFrame:
        """
        Get the schema of a table.
        
        Args:
            table_name: Name of the table
            schema: Schema the table belongs to
            connection_name: Name of the connection to use
            
        Returns:
            Pandas DataFrame containing the table schema
        """
        pass
    
    @abstractmethod
    def execute_statement(self, statement: str, parameters: Optional[Dict[str, Any]] = None,
                         connection_name: Optional[str] = None) -> int:
        """
        Execute a SQL statement (INSERT, UPDATE, DELETE).
        
        Args:
            statement: SQL statement to execute
            parameters: Parameters for the statement
            connection_name: Name of the connection to use
            
        Returns:
            Number of affected rows
        """
        pass
    
    @abstractmethod
    def begin_transaction(self, connection_name: Optional[str] = None) -> Any:
        """
        Begin a new transaction.
        
        Args:
            connection_name: Name of the connection to use
            
        Returns:
            Transaction object
        """
        pass
    
    @abstractmethod
    def commit_transaction(self, transaction: Any, 
                          connection_name: Optional[str] = None) -> bool:
        """
        Commit a transaction.
        
        Args:
            transaction: Transaction to commit
            connection_name: Name of the connection to use
            
        Returns:
            True if the transaction was committed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def rollback_transaction(self, transaction: Any,
                            connection_name: Optional[str] = None) -> bool:
        """
        Rollback a transaction.
        
        Args:
            transaction: Transaction to rollback
            connection_name: Name of the connection to use
            
        Returns:
            True if the transaction was rolled back successfully, False otherwise
        """
        pass