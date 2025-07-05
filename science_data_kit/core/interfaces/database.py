"""
Database Interfaces for Science Data Kit

This module defines interfaces for database managers and connectors,
providing a standardized way to interact with different database systems.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple

import pandas as pd


class DatabaseInterface(ABC):
    """
    Abstract base class for database interfaces.

    This interface defines the core methods that all database managers should implement,
    regardless of the specific database technology they interact with.
    """

    @abstractmethod
    def connect(self, connection_name: Optional[str] = None) -> bool:
        """
        Connect to the database.

        Args:
            connection_name: Optional name for the connection.

        Returns:
            True if connection was successful, False otherwise.
        """
        pass

    @abstractmethod
    def close(self, connection_name: Optional[str] = None) -> None:
        """
        Close the database connection.

        Args:
            connection_name: Optional name of the connection to close.
        """
        pass

    @abstractmethod
    def is_connected(self, connection_name: Optional[str] = None) -> bool:
        """
        Check if connected to the database.

        Args:
            connection_name: Optional name of the connection to check.

        Returns:
            True if connected, False otherwise.
        """
        pass

    @abstractmethod
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None, 
                     connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Execute a query on the database.

        Args:
            query: The query string to execute.
            parameters: Optional parameters for the query.
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing the query results.
        """
        pass

    @abstractmethod
    def query_to_dataframe(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                          connection_name: Optional[str] = None) -> pd.DataFrame:
        """
        Execute a query and return the results as a pandas DataFrame.

        Args:
            query: The query string to execute.
            parameters: Optional parameters for the query.
            connection_name: Optional name of the connection to use.

        Returns:
            A pandas DataFrame containing the query results.
        """
        pass


class GraphDatabaseInterface(DatabaseInterface):
    """
    Interface for graph database managers.

    This interface extends the base DatabaseInterface with methods specific to graph databases.
    """

    @abstractmethod
    def fetch_labels(self, connection_name: Optional[str] = None) -> List[str]:
        """
        Fetch all node labels from the graph database.

        Args:
            connection_name: Optional name of the connection to use.

        Returns:
            List of node labels.
        """
        pass

    @abstractmethod
    def fetch_node_properties(self, label: str, connection_name: Optional[str] = None) -> List[str]:
        """
        Fetch all properties for a given node label.

        Args:
            label: The node label to fetch properties for.
            connection_name: Optional name of the connection to use.

        Returns:
            List of property names.
        """
        pass

    @abstractmethod
    def fetch_nodes(self, label: str, properties: Optional[List[str]] = None, 
                   limit: int = 100, connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch nodes with a given label.

        Args:
            label: The node label to fetch.
            properties: Optional list of properties to include.
            limit: Maximum number of nodes to fetch.
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing node data.
        """
        pass

    @abstractmethod
    def count_nodes_by_label(self, label: str, connection_name: Optional[str] = None) -> int:
        """
        Count nodes with a given label.

        Args:
            label: The node label to count.
            connection_name: Optional name of the connection to use.

        Returns:
            Number of nodes with the given label.
        """
        pass

    @abstractmethod
    def count_relationships(self, source_label: str, relationship_type: str, 
                           target_label: str, connection_name: Optional[str] = None) -> int:
        """
        Count relationships between nodes.

        Args:
            source_label: Label of the source nodes.
            relationship_type: Type of relationship.
            target_label: Label of the target nodes.
            connection_name: Optional name of the connection to use.

        Returns:
            Number of relationships matching the criteria.
        """
        pass


class Neo4jDatabaseInterface(GraphDatabaseInterface):
    """
    Interface for Neo4j database managers.

    This interface extends the GraphDatabaseInterface with methods specific to Neo4j.
    """

    @abstractmethod
    def start_container(self, version: str = "latest", workload_type: Optional[str] = None) -> bool:
        """
        Start a Neo4j container.

        Args:
            version: Neo4j version to use.
            workload_type: Optional workload type for configuration.

        Returns:
            True if container was started successfully, False otherwise.
        """
        pass

    @abstractmethod
    def stop_container(self) -> bool:
        """
        Stop the Neo4j container.

        Returns:
            True if container was stopped successfully, False otherwise.
        """
        pass

    @abstractmethod
    def get_container_status(self) -> Dict[str, Any]:
        """
        Get the status of the Neo4j container.

        Returns:
            Dictionary containing container status information.
        """
        pass

    @abstractmethod
    def get_existing_indexes(self, connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get existing indexes in the Neo4j database.

        Args:
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing index information.
        """
        pass

    @abstractmethod
    def create_index(self, label: str, property_name: str, 
                    index_name: Optional[str] = None, connection_name: Optional[str] = None) -> bool:
        """
        Create an index in the Neo4j database.

        Args:
            label: Node label to create index for.
            property_name: Property to index.
            index_name: Optional name for the index.
            connection_name: Optional name of the connection to use.

        Returns:
            True if index was created successfully, False otherwise.
        """
        pass

    @abstractmethod
    def get_index_recommendations(self, connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get index recommendations for the Neo4j database.

        Args:
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing index recommendations.
        """
        pass


class DocumentDatabaseInterface(DatabaseInterface):
    """
    Interface for document database managers.

    This interface extends the base DatabaseInterface with methods specific to document databases.
    """

    @abstractmethod
    def list_collections(self, connection_name: Optional[str] = None) -> List[str]:
        """
        List all collections in the database.

        Args:
            connection_name: Optional name of the connection to use.

        Returns:
            List of collection names.
        """
        pass

    @abstractmethod
    def get_collection_stats(self, collection: str, connection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a collection.

        Args:
            collection: Name of the collection.
            connection_name: Optional name of the connection to use.

        Returns:
            Dictionary containing collection statistics.
        """
        pass

    @abstractmethod
    def find_documents(self, collection: str, query: Dict[str, Any], 
                      projection: Optional[Dict[str, Any]] = None,
                      limit: int = 100, connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find documents in a collection.

        Args:
            collection: Name of the collection.
            query: Query filter.
            projection: Optional fields to include or exclude.
            limit: Maximum number of documents to return.
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing document data.
        """
        pass

    @abstractmethod
    def count_documents(self, collection: str, query: Dict[str, Any], 
                       connection_name: Optional[str] = None) -> int:
        """
        Count documents in a collection.

        Args:
            collection: Name of the collection.
            query: Query filter.
            connection_name: Optional name of the connection to use.

        Returns:
            Number of documents matching the query.
        """
        pass

    @abstractmethod
    def insert_documents(self, collection: str, documents: List[Dict[str, Any]], 
                        connection_name: Optional[str] = None) -> int:
        """
        Insert documents into a collection.

        Args:
            collection: Name of the collection.
            documents: List of documents to insert.
            connection_name: Optional name of the connection to use.

        Returns:
            Number of documents inserted.
        """
        pass


class MongoDBDatabaseInterface(DocumentDatabaseInterface):
    """
    Interface for MongoDB database managers.

    This interface extends the DocumentDatabaseInterface with methods specific to MongoDB.
    """

    @abstractmethod
    def start_container(self, version: str = "latest", workload_type: Optional[str] = None) -> bool:
        """
        Start a MongoDB container.

        Args:
            version: MongoDB version to use.
            workload_type: Optional workload type for configuration.

        Returns:
            True if container was started successfully, False otherwise.
        """
        pass

    @abstractmethod
    def stop_container(self) -> bool:
        """
        Stop the MongoDB container.

        Returns:
            True if container was stopped successfully, False otherwise.
        """
        pass

    @abstractmethod
    def get_container_status(self) -> Dict[str, Any]:
        """
        Get the status of the MongoDB container.

        Returns:
            Dictionary containing container status information.
        """
        pass

    @abstractmethod
    def aggregate(self, collection: str, pipeline: List[Dict[str, Any]], 
                 connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Execute an aggregation pipeline.

        Args:
            collection: Name of the collection.
            pipeline: Aggregation pipeline stages.
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing the aggregation results.
        """
        pass

    @abstractmethod
    def create_index(self, collection: str, keys: Dict[str, int], 
                    index_name: Optional[str] = None, unique: bool = False,
                    connection_name: Optional[str] = None) -> bool:
        """
        Create an index in the MongoDB database.

        Args:
            collection: Name of the collection.
            keys: Dictionary of field names and index directions (1 for ascending, -1 for descending).
            index_name: Optional name for the index.
            unique: Whether the index should enforce uniqueness.
            connection_name: Optional name of the connection to use.

        Returns:
            True if index was created successfully, False otherwise.
        """
        pass

    @abstractmethod
    def get_indexes(self, collection: str, connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get indexes for a collection.

        Args:
            collection: Name of the collection.
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing index information.
        """
        pass
