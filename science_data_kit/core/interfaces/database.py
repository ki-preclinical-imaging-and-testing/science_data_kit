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


class SPARQLDatabaseInterface(GraphDatabaseInterface):
    """
    Interface for SPARQL endpoint managers.

    This interface extends the GraphDatabaseInterface with methods specific to SPARQL endpoints.
    """

    @abstractmethod
    def execute_sparql_query(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                           connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Execute a SPARQL query on the endpoint.

        Args:
            query: The SPARQL query string to execute.
            parameters: Optional parameters for the query.
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing the query results.
        """
        pass

    @abstractmethod
    def sparql_query_to_dataframe(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                                connection_name: Optional[str] = None) -> pd.DataFrame:
        """
        Execute a SPARQL query and return the results as a pandas DataFrame.

        Args:
            query: The SPARQL query string to execute.
            parameters: Optional parameters for the query.
            connection_name: Optional name of the connection to use.

        Returns:
            A pandas DataFrame containing the query results.
        """
        pass

    @abstractmethod
    def get_endpoint_info(self, connection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about the SPARQL endpoint.

        Args:
            connection_name: Optional name of the connection to use.

        Returns:
            Dictionary containing endpoint information.
        """
        pass

    @abstractmethod
    def list_graphs(self, connection_name: Optional[str] = None) -> List[str]:
        """
        List all named graphs in the SPARQL endpoint.

        Args:
            connection_name: Optional name of the connection to use.

        Returns:
            List of graph URIs.
        """
        pass

    @abstractmethod
    def count_triples(self, graph_uri: Optional[str] = None, 
                     connection_name: Optional[str] = None) -> int:
        """
        Count triples in the SPARQL endpoint.

        Args:
            graph_uri: Optional URI of the named graph to count triples in.
            connection_name: Optional name of the connection to use.

        Returns:
            Number of triples.
        """
        pass

    @abstractmethod
    def list_classes(self, graph_uri: Optional[str] = None,
                    connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all classes in the SPARQL endpoint.

        Args:
            graph_uri: Optional URI of the named graph to list classes from.
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing class information.
        """
        pass

    @abstractmethod
    def list_properties(self, class_uri: Optional[str] = None, graph_uri: Optional[str] = None,
                       connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all properties in the SPARQL endpoint.

        Args:
            class_uri: Optional URI of the class to list properties for.
            graph_uri: Optional URI of the named graph to list properties from.
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing property information.
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


class CassandraDatabaseInterface(DocumentDatabaseInterface):
    """
    Interface for Cassandra database managers.

    This interface extends the DocumentDatabaseInterface with methods specific to Cassandra.
    """

    @abstractmethod
    def start_container(self, version: str = "latest", workload_type: Optional[str] = None) -> bool:
        """
        Start a Cassandra container.

        Args:
            version: Cassandra version to use.
            workload_type: Optional workload type for configuration.

        Returns:
            True if container was started successfully, False otherwise.
        """
        pass

    @abstractmethod
    def stop_container(self) -> bool:
        """
        Stop the Cassandra container.

        Returns:
            True if container was stopped successfully, False otherwise.
        """
        pass

    @abstractmethod
    def get_container_status(self) -> Dict[str, Any]:
        """
        Get the status of the Cassandra container.

        Returns:
            Dictionary containing container status information.
        """
        pass

    @abstractmethod
    def list_keyspaces(self, connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all keyspaces in the Cassandra cluster.

        Args:
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing keyspace information.
        """
        pass

    @abstractmethod
    def create_keyspace(self, keyspace_name: str, replication_strategy: str = 'SimpleStrategy',
                       replication_factor: int = 1, connection_name: Optional[str] = None) -> bool:
        """
        Create a new keyspace.

        Args:
            keyspace_name: Name of the keyspace to create.
            replication_strategy: Replication strategy to use.
            replication_factor: Replication factor for the keyspace.
            connection_name: Optional name of the connection to use.

        Returns:
            True if keyspace was created successfully, False otherwise.
        """
        pass

    @abstractmethod
    def create_table(self, table_name: str, columns: Dict[str, str], primary_key: List[str],
                    keyspace: Optional[str] = None, connection_name: Optional[str] = None) -> bool:
        """
        Create a new table in a keyspace.

        Args:
            table_name: Name of the table to create.
            columns: Dictionary mapping column names to CQL types.
            primary_key: List of column names to use as primary key.
            keyspace: Optional keyspace name (uses current keyspace if not provided).
            connection_name: Optional name of the connection to use.

        Returns:
            True if table was created successfully, False otherwise.
        """
        pass

    @abstractmethod
    def batch_operation(self, statements: List[str], parameters: List[Dict[str, Any]] = None,
                       connection_name: Optional[str] = None) -> bool:
        """
        Execute a batch of CQL statements.

        Args:
            statements: List of CQL statements to execute.
            parameters: Optional list of parameter dictionaries for each statement.
            connection_name: Optional name of the connection to use.

        Returns:
            True if batch operation was successful, False otherwise.
        """
        pass


class ElasticsearchDatabaseInterface(DocumentDatabaseInterface):
    """
    Interface for Elasticsearch database managers.

    This interface extends the DocumentDatabaseInterface with methods specific to Elasticsearch.
    """

    @abstractmethod
    def start_container(self, version: str = "latest", workload_type: Optional[str] = None) -> bool:
        """
        Start an Elasticsearch container.

        Args:
            version: Elasticsearch version to use.
            workload_type: Optional workload type for configuration.

        Returns:
            True if container was started successfully, False otherwise.
        """
        pass

    @abstractmethod
    def stop_container(self) -> bool:
        """
        Stop the Elasticsearch container.

        Returns:
            True if container was stopped successfully, False otherwise.
        """
        pass

    @abstractmethod
    def get_container_status(self) -> Dict[str, Any]:
        """
        Get the status of the Elasticsearch container.

        Returns:
            Dictionary containing container status information.
        """
        pass

    @abstractmethod
    def search(self, index: str, query: Dict[str, Any], 
              size: int = 10, from_: int = 0,
              connection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a search query on an index.

        Args:
            index: Name of the index.
            query: Elasticsearch query DSL.
            size: Maximum number of documents to return.
            from_: Starting offset for results.
            connection_name: Optional name of the connection to use.

        Returns:
            Dictionary containing the search results.
        """
        pass

    @abstractmethod
    def create_index(self, index: str, mappings: Dict[str, Any], 
                    settings: Optional[Dict[str, Any]] = None,
                    connection_name: Optional[str] = None) -> bool:
        """
        Create an index in Elasticsearch.

        Args:
            index: Name of the index.
            mappings: Index mappings.
            settings: Optional index settings.
            connection_name: Optional name of the connection to use.

        Returns:
            True if index was created successfully, False otherwise.
        """
        pass

    @abstractmethod
    def get_indices(self, connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get information about indices.

        Args:
            connection_name: Optional name of the connection to use.

        Returns:
            List of dictionaries containing index information.
        """
        pass

    @abstractmethod
    def get_cluster_health(self, connection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Elasticsearch cluster health.

        Args:
            connection_name: Optional name of the connection to use.

        Returns:
            Dictionary containing cluster health information.
        """
        pass

    @abstractmethod
    def bulk_index(self, index: str, documents: List[Dict[str, Any]], 
                  id_field: Optional[str] = None,
                  connection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Bulk index documents into Elasticsearch.

        Args:
            index: Name of the index.
            documents: List of documents to index.
            id_field: Optional field to use as document ID.
            connection_name: Optional name of the connection to use.

        Returns:
            Dictionary containing bulk indexing results.
        """
        pass
