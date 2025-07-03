"""
Database Manager for Science Data Kit

This module provides a unified interface for interacting with Neo4j databases.
It combines functionality from database.py and graph_utils.py into a single,
consistent API with proper type hinting and error handling.
"""

import os
import yaml
import socket
import docker
import pandas as pd
import networkx as nx
import pickle
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import Neo4jError, ServiceUnavailable

# Import ontology classes from the new module
from science_data_kit.core.ontology import OntologyAnnotation, OntologySource

# Import query cache
from .cache import cached_query

# Set ISATOOLS_AVAILABLE for backward compatibility
ISATOOLS_AVAILABLE = True


class DatabaseError(Exception):
    """Base exception class for database-related errors."""
    pass


class ConnectionError(DatabaseError):
    """Exception raised for connection-related errors."""
    pass


class QueryError(DatabaseError):
    """Exception raised for query-related errors."""
    pass


class ConfigError(DatabaseError):
    """Exception raised for configuration-related errors."""
    pass


def load_db_config(fn: str = 'db_config.yaml') -> Dict[str, Any]:
    """
    Loads the database configuration from a YAML file.

    Args:
        fn: Path to the YAML configuration file.

    Returns:
        Dictionary containing the database configuration.

    Raises:
        ConfigError: If the configuration file cannot be loaded.
    """
    # If the file is .db_config_auto.yaml, try to load it from the app directory first
    if fn == '.db_config_auto.yaml':
        try:
            with open(f"app/{fn}", 'r') as file:
                return yaml.safe_load(file)
        except Exception:
            # Fall back to the original location
            pass

    try:
        with open(fn, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise ConfigError(f"Could not load {fn}: {e}")


def update_db_config_auto(hostname: str, port: str, username: Optional[str] = None,
                         password: Optional[str] = None, database: Optional[str] = None) -> None:
    """
    Updates the auto-generated database configuration file.

    Args:
        hostname: The hostname of the Neo4j server.
        port: The port of the Neo4j server.
        username: The username for authentication.
        password: The password for authentication.
        database: The name of the database to connect to.

    Raises:
        ConfigError: If the configuration file cannot be updated.
    """
    config_path = Path("app/.db_config_auto.yaml")

    # Create config dictionary
    config = {
        "uri": f"bolt://{hostname}:{port}",
    }

    if username:
        config["user"] = username
    if password:
        config["password"] = password
    if database:
        config["database"] = database

    # Write to file
    try:
        with open(config_path, 'w') as file:
            yaml.dump(config, file)
    except Exception as e:
        raise ConfigError(f"Could not update configuration file: {e}")


def find_free_port(start_port: int = 7687) -> int:
    """
    Finds a free port starting from the given port number.

    Args:
        start_port: The port number to start searching from.

    Returns:
        A free port number.
    """
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
            port += 1


class Neo4jManager:
    """
    A unified manager for Neo4j database operations.

    This class provides methods for:
    - Managing multiple Neo4j connections
    - Starting and stopping Neo4j containers
    - Executing queries and processing results
    - Importing and exporting data
    - Working with ontologies
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(Neo4jManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Optional[Dict[str, Any]] = None, 
                config_file: Optional[str] = None,
                use_session_state: bool = False,
                connect_on_init: bool = False):
        """
        Initialize the Neo4jManager instance.

        Args:
            config: Dictionary with database connection details.
            config_file: Path to a YAML file with database connection details.
            use_session_state: If True, use the connection from Streamlit session_state if available.
            connect_on_init: If True, attempt to connect during initialization.

        Raises:
            ConnectionError: If connect_on_init is True and the connection details are invalid or the connection fails.
        """
        # Skip initialization if already initialized (singleton pattern)
        if self._initialized:
            return

        # Dictionary to store multiple connections
        # Format: {connection_name: {
        #     "driver": Neo4j driver object,
        #     "uri": URI string,
        #     "user": username string,
        #     "password": password string,
        #     "database": database name string
        # }}
        self._connections = {}

        # Current active connection name
        self._active_connection = None

        # Default connection parameters (used for backward compatibility)
        self._driver = None
        self.uri = None
        self.user = None
        self.password = None
        self.database = None

        # Container configuration
        self.container_name = "neo4j-instance"
        self.http_port = 7474
        self.bolt_port = 7687
        self._connection_error = None

        # Try to use session_state connection if requested
        if use_session_state:
            try:
                import streamlit as st
                if hasattr(st, 'session_state') and 'connected' in st.session_state and st.session_state.connected:
                    self._driver = st.session_state.session._driver
                    self.uri = st.session_state.neo4j_uri
                    self.user = st.session_state.neo4j_user
                    self.password = st.session_state.neo4j_password
                    self.database = "neo4j"  # Default database
                    self._initialized = True
                    return
            except (ImportError, AttributeError):
                # Fall back to config if session_state is not available or not connected
                pass

        # Use config if session_state is not available or not requested
        if config is None:
            try:
                if config_file:
                    config = load_db_config(config_file)
                else:
                    # Try to load from default locations
                    try:
                        config = load_db_config('.db_config_auto.yaml')
                    except ConfigError:
                        pass

                    if not config:
                        try:
                            config = load_db_config('.db_config.yaml')
                        except ConfigError:
                            pass

                    if not config:
                        try:
                            config = load_db_config('db_config.yaml')
                        except ConfigError:
                            pass
            except Exception as e:
                self._connection_error = f"Error loading configuration: {e}"
                self._initialized = True
                return

        if not config:
            self._connection_error = "No configuration provided and no default configuration found."
            self._initialized = True
            return

        required_keys = {"uri", "user", "password"}
        if not all(key in config for key in required_keys):
            self._connection_error = f"Missing required keys in config. Expected keys: {required_keys}"
            self._initialized = True
            return

        self.uri = config["uri"]
        self.user = config["user"]
        self.password = config["password"]
        self.database = config.get("database", "neo4j")

        # Extract port from URI if possible
        try:
            # URI format: bolt://hostname:port
            self.bolt_port = int(self.uri.split(':')[-1])
        except (ValueError, IndexError):
            # Default port if URI doesn't contain a port
            self.bolt_port = 7687

        # Only connect if requested
        if connect_on_init:
            try:
                self._connect()
            except ConnectionError as e:
                self._connection_error = str(e)

        self._initialized = True

    def _connect(self, connection_name: Optional[str] = None) -> bool:
        """
        Establishes a connection to the Neo4j database.

        Args:
            connection_name: Optional name for the connection. If not provided,
                             uses the current connection parameters.

        Returns:
            True if connection was successful, False otherwise.

        Raises:
            ConnectionError: If the connection fails and raise_error is True.
        """
        # If connection_name is provided, use it to create a new named connection
        if connection_name:
            uri = self.uri
            user = self.user
            password = self.password
            database = self.database
        else:
            # Use current connection parameters
            if not self.uri or not self.user or not self.password:
                self._connection_error = "Missing connection details (uri, user, or password)"
                return False
            uri = self.uri
            user = self.user
            password = self.password
            database = self.database or "neo4j"
            # Use a default connection name if none provided
            connection_name = "default"

        # Check if we already have a connection with the same URI and database
        # If so, only close it if it's been manually disconnected or is inactive
        names_to_remove = []
        for name, conn in self._connections.items():
            # Only consider connections with the same URI and database
            if conn["uri"] == uri and conn["database"] == database and name != connection_name:
                # Check if the connection is active
                try:
                    with conn["driver"].session(database=conn["database"]) as session:
                        session.run("RETURN 1")
                    # Connection is active, keep it
                except Exception:
                    # Connection is inactive or has been manually disconnected, mark for removal
                    names_to_remove.append(name)

        # Remove inactive or manually disconnected duplicate connections
        for name in names_to_remove:
            conn = self._connections[name]
            # Close the duplicate connection
            if conn["driver"]:
                conn["driver"].close()
            # Remove it from connections
            del self._connections[name]

        try:
            # Create a new driver
            driver = GraphDatabase.driver(uri, auth=(user, password))

            # Test the connection
            with driver.session(database=database) as session:
                session.run("RETURN 1")

            # Store the connection
            self._connections[connection_name] = {
                "driver": driver,
                "uri": uri,
                "user": user,
                "password": password,
                "database": database
            }

            # Set as active connection
            self._active_connection = connection_name

            # Update the default connection parameters for backward compatibility
            self._driver = driver
            self.uri = uri
            self.user = user
            self.password = password
            self.database = database

            self._connection_error = None
            return True
        except Exception as e:
            self._connection_error = f"Failed to connect to Neo4j: {e}"
            return False

    def close(self, connection_name: Optional[str] = None) -> None:
        """
        Closes a Neo4j driver connection.

        Args:
            connection_name: Optional name of the connection to close.
                            If None, closes the active connection.
        """
        if connection_name is None:
            # Close the active connection
            if self._active_connection:
                connection_name = self._active_connection
            else:
                return

        # Close the specified connection
        if connection_name in self._connections:
            conn = self._connections[connection_name]
            if conn["driver"]:
                conn["driver"].close()

            # Remove from connections
            del self._connections[connection_name]

            # If this was the active connection, clear it
            if self._active_connection == connection_name:
                self._active_connection = None
                self._driver = None

                # If there are other connections, set one as active
                if self._connections:
                    # Get the first connection name
                    new_active = next(iter(self._connections))
                    self.set_active_connection(new_active)

        # For backward compatibility
        if self._driver and (not self._connections or not self._active_connection):
            self._driver.close()
            self._driver = None

    def is_connected(self, connection_name: Optional[str] = None) -> bool:
        """
        Checks if the manager is connected to a Neo4j database.

        Args:
            connection_name: Optional name of the connection to check.
                            If None, checks the active connection.

        Returns:
            True if connected, False otherwise.
        """
        if connection_name is None:
            # Check the active connection
            if self._active_connection:
                connection_name = self._active_connection
            else:
                # For backward compatibility
                if not self._driver:
                    return False
                try:
                    with self._driver.session(database=self.database) as session:
                        session.run("RETURN 1")
                    return True
                except Exception:
                    return False

        # Check the specified connection
        if connection_name in self._connections:
            conn = self._connections[connection_name]
            try:
                with conn["driver"].session(database=conn["database"]) as session:
                    session.run("RETURN 1")
                return True
            except Exception:
                return False

        return False

    def set_active_connection(self, connection_name: str) -> bool:
        """
        Sets the active connection.

        Args:
            connection_name: Name of the connection to set as active.

        Returns:
            True if successful, False if the connection doesn't exist.
        """
        if connection_name in self._connections:
            self._active_connection = connection_name
            conn = self._connections[connection_name]

            # Update default connection parameters for backward compatibility
            self._driver = conn["driver"]
            self.uri = conn["uri"]
            self.user = conn["user"]
            self.password = conn["password"]
            self.database = conn["database"]

            return True
        return False

    def get_connection_names(self) -> List[str]:
        """
        Gets the names of all connections.

        Returns:
            List of connection names.
        """
        return list(self._connections.keys())

    def get_active_connection_name(self) -> Optional[str]:
        """
        Gets the name of the active connection.

        Returns:
            Name of the active connection, or None if no active connection.
        """
        return self._active_connection

    @cached_query()
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None, 
                      connection_name: Optional[str] = None, enable_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Executes a Cypher query and returns the results.

        Args:
            query: The Cypher query to execute.
            parameters: Optional dictionary of parameters to include in the query.
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.
            enable_cache: Whether to use query caching for this query.

        Returns:
            List of dictionaries containing the query results.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        # If connection_name is provided, use that specific connection
        if connection_name:
            if connection_name not in self._connections:
                raise ConnectionError(f"Connection '{connection_name}' does not exist")

            conn = self._connections[connection_name]
            driver = conn["driver"]
            database = conn["database"]
        else:
            # Use the active connection
            if self._active_connection:
                conn = self._connections[self._active_connection]
                driver = conn["driver"]
                database = conn["database"]
            else:
                # Try to connect if not already connected (backward compatibility)
                if not self._driver:
                    if not self._connect():
                        raise ConnectionError(f"Cannot run query. No active connection to Neo4j. {self._connection_error}")
                driver = self._driver
                database = self.database

        parameters = parameters or {}

        try:
            with driver.session(database=database) as session:
                result = session.run(query, parameters)
                return [dict(record) for record in result]
        except Neo4jError as e:
            raise QueryError(f"Query execution failed: {e}")

    def query_to_dataframe(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                          connection_name: Optional[str] = None) -> pd.DataFrame:
        """
        Executes a Cypher query and returns the results as a Pandas DataFrame.

        Args:
            query: The Cypher query to execute.
            parameters: Optional dictionary of parameters.
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.

        Returns:
            A Pandas DataFrame containing the query results.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        results = self.execute_query(query, parameters, connection_name)
        return pd.DataFrame(results)

    def query_to_value(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                      connection_name: Optional[str] = None) -> Any:
        """
        Executes a Cypher query and returns a single value.

        Args:
            query: The Cypher query to execute.
            parameters: Optional dictionary of parameters.
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.

        Returns:
            A single value if one result is returned, or a list of values if multiple rows are returned.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        results = self.execute_query(query, parameters, connection_name)
        if not results:
            return None

        values = []
        for record in results:
            record_values = list(record.values())
            if record_values:
                values.append(record_values[0])

        return values[0] if len(values) == 1 else values

    def get_container_status(self) -> str:
        """
        Gets the status of the Neo4j container.

        Returns:
            The status of the container ("running", "stopped", or "not found").
        """
        try:
            client = docker.from_env()
            containers = client.containers.list(all=True, filters={"name": self.container_name})
            if containers:
                return containers[0].status
            return "not found"
        except Exception:
            return "not found"

    def get_hostname(self) -> str:
        """
        Gets the hostname for connecting to the Neo4j container.

        Returns:
            The hostname (either "localhost" or the container's IP address).
        """
        try:
            client = docker.from_env()
            containers = client.containers.list(filters={"name": self.container_name})
            if containers:
                container = containers[0]
                ip_address = container.attrs["NetworkSettings"]["IPAddress"]
                if ip_address:
                    return ip_address
            return "localhost"
        except Exception:
            return "localhost"

    def start_container(self, version: str = "latest") -> bool:
        """
        Starts the Neo4j container.

        Args:
            version: The Neo4j version to use.

        Returns:
            True if the container was started successfully, False otherwise.

        Raises:
            ConnectionError: If the container cannot be started.
        """
        try:
            client = docker.from_env()

            # Check if container already exists
            existing_containers = client.containers.list(all=True, filters={"name": self.container_name})
            if existing_containers:
                container = existing_containers[0]
                if container.status != "running":
                    container.start()
                return True

            # Find available ports
            self.http_port = find_free_port(7474)
            self.bolt_port = find_free_port(7687)

            # Create and start container
            container = client.containers.run(
                f"neo4j:{version}",
                name=self.container_name,
                detach=True,
                ports={
                    '7474/tcp': self.http_port,
                    '7687/tcp': self.bolt_port
                },
                environment={
                    "NEO4J_AUTH": f"neo4j/password",
                    "NEO4J_apoc_export_file_enabled": "true",
                    "NEO4J_apoc_import_file_enabled": "true",
                    "NEO4J_apoc_import_file_use__neo4j__config": "true",
                    "NEO4JLABS_PLUGINS": '["apoc"]'
                },
                volumes={
                    f"{self.container_name}-data": {"bind": "/data", "mode": "rw"},
                    f"{self.container_name}-logs": {"bind": "/logs", "mode": "rw"},
                    f"{self.container_name}-import": {"bind": "/import", "mode": "rw"},
                    f"{self.container_name}-plugins": {"bind": "/plugins", "mode": "rw"}
                }
            )

            # Update connection details
            self.uri = f"bolt://localhost:{self.bolt_port}"
            self.user = "neo4j"
            self.password = "password"

            # Update config file
            update_db_config_auto("localhost", str(self.bolt_port), self.user, self.password)

            return True
        except Exception as e:
            raise ConnectionError(f"Failed to start Neo4j container: {e}")

    def stop_container(self) -> bool:
        """
        Stops the Neo4j container.

        Returns:
            True if the container was stopped successfully, False otherwise.
        """
        try:
            client = docker.from_env()
            containers = client.containers.list(filters={"name": self.container_name})
            if containers:
                containers[0].stop()
                return True
            return False
        except Exception:
            return False

    def fetch_labels(self) -> List[str]:
        """
        Fetches all labels from the Neo4j database.

        Returns:
            List of label names.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        query = "MATCH (n) RETURN DISTINCT labels(n) as labels"
        results = self.execute_query(query)

        all_labels = []
        for result in results:
            for labels_list in result["labels"]:
                for label in labels_list:
                    if label and isinstance(label, str):
                        all_labels.append(label)

        return sorted(set(all_labels))

    def fetch_node_properties(self, label: str) -> List[str]:
        """
        Fetches all property keys for nodes with the given label.

        Args:
            label: The node label to query.

        Returns:
            List of property keys.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        query = f"""
        MATCH (n:`{label}`)
        UNWIND keys(n) AS property
        RETURN DISTINCT property
        ORDER BY property
        """
        results = self.execute_query(query)
        return [record["property"] for record in results]

    def fetch_nodes(self, label: str, properties: Optional[List[str]] = None, 
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetches nodes with the given label and returns selected properties.

        Args:
            label: The node label to query.
            properties: List of property keys to return. If None, returns all properties.
            limit: Maximum number of nodes to return.

        Returns:
            List of dictionaries containing node properties.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        if properties:
            property_string = ", ".join([f"n.{prop} AS {prop}" for prop in properties])
            query = f"""
            MATCH (n:`{label}`)
            RETURN id(n) AS id, {property_string}
            LIMIT {limit}
            """
        else:
            query = f"""
            MATCH (n:`{label}`)
            RETURN id(n) AS id, n
            LIMIT {limit}
            """

        return self.execute_query(query)

    def summarize_ontology_terms(self, label: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Summarizes available ontology terms used as properties for node labels.

        Args:
            label: Optional label to filter the summary. If None, summarizes terms for all labels.

        Returns:
            A dictionary with label names as keys and dictionaries of property summaries as values.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        # Query to find properties that might contain ontology terms
        if label:
            query = """
            MATCH (n:`{label}`)
            UNWIND keys(n) AS property
            WITH property, collect(DISTINCT n[property]) AS values
            WHERE size(values) > 0
            RETURN '{label}' AS label, property, values, count(values) AS count
            ORDER BY count DESC
            """.format(label=label)
        else:
            query = """
            MATCH (n)
            WHERE NOT n:Resource
            WITH labels(n) AS labels, keys(n) AS properties, n
            UNWIND labels AS label
            UNWIND properties AS property
            WITH label, property, collect(DISTINCT n[property]) AS values
            WHERE size(values) > 0
            RETURN label, property, values, count(values) AS count
            ORDER BY label, count DESC
            """

        results = self.execute_query(query)

        # Organize results by label and property
        summary = {}
        for record in results:
            label_name = record["label"]
            property_name = record["property"]
            values = record["values"]
            count = record["count"]

            # Initialize label entry if it doesn't exist
            if label_name not in summary:
                summary[label_name] = {}

            # Add property summary
            summary[label_name][property_name] = {
                "count": count,
                "unique_values": len(values),
                "sample_values": values[:5],  # Show up to 5 sample values
                "has_uri_pattern": any("://" in str(v) for v in values)  # Check if any value looks like a URI
            }

        return summary

    def load_ontology_relationships(self, ontology_annotations: List[Any], 
                                   create_source_nodes: bool = True,
                                   relationship_type: str = "HAS_TERM") -> int:
        """
        Loads ontology terms and their relationships into Neo4j.

        Args:
            ontology_annotations: List of OntologyAnnotation objects to load.
            create_source_nodes: Whether to create nodes for ontology sources.
            relationship_type: The type of relationship to create between source and term nodes.

        Returns:
            Number of relationships created.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        if not ontology_annotations or not ISATOOLS_AVAILABLE:
            return 0

        # Track statistics
        terms_created = 0
        sources_created = 0
        relationships_created = 0

        # Process each ontology annotation
        for annotation in ontology_annotations:
            # Skip if term is empty
            if not annotation.term:
                continue

            # Create term node
            term_query = """
            MERGE (t:OntologyTerm {term: $term})
            ON CREATE SET t.created = timestamp()
            SET t.term_accession = $term_accession,
                t.last_updated = timestamp()
            RETURN t
            """

            term_params = {
                "term": annotation.term,
                "term_accession": annotation.term_accession or ""
            }

            term_result = self.execute_query(term_query, term_params)
            if term_result:
                terms_created += 1

            # Create source node and relationship if requested
            if create_source_nodes and annotation.term_source:
                source_name = annotation.term_source
                if hasattr(annotation.term_source, 'name'):
                    source_name = annotation.term_source.name

                if source_name:
                    # Create source node
                    source_query = """
                    MERGE (s:OntologySource {name: $name})
                    ON CREATE SET s.created = timestamp()
                    SET s.last_updated = timestamp()
                    RETURN s
                    """

                    source_params = {"name": source_name}

                    # Add additional properties if available
                    if hasattr(annotation.term_source, 'file') and annotation.term_source.file:
                        source_params["file"] = annotation.term_source.file
                    if hasattr(annotation.term_source, 'version') and annotation.term_source.version:
                        source_params["version"] = annotation.term_source.version
                    if hasattr(annotation.term_source, 'description') and annotation.term_source.description:
                        source_params["description"] = annotation.term_source.description

                    source_result = self.execute_query(source_query, source_params)
                    if source_result:
                        sources_created += 1

                    # Create relationship between source and term
                    rel_query = """
                    MATCH (s:OntologySource {name: $source_name})
                    MATCH (t:OntologyTerm {term: $term})
                    MERGE (s)-[r:{rel_type}]->(t)
                    ON CREATE SET r.created = timestamp()
                    SET r.last_updated = timestamp()
                    RETURN r
                    """.format(rel_type=relationship_type)

                    rel_params = {
                        "source_name": source_name,
                        "term": annotation.term
                    }

                    rel_result = self.execute_query(rel_query, rel_params)
                    if rel_result:
                        relationships_created += 1

        return relationships_created

    def export_graph(self, file_path: str, connection_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Exports the entire graph to a file.

        Args:
            file_path: Path where the graph will be saved.
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.

        Returns:
            A tuple containing (success, message).

        Raises:
            ConnectionError: If there is no active connection.
        """
        # If connection_name is provided, use that specific connection
        if connection_name:
            if connection_name not in self._connections:
                raise ConnectionError(f"Connection '{connection_name}' does not exist")

            if not self._connections[connection_name]["connected"]:
                raise ConnectionError(f"Connection '{connection_name}' is not connected")
        else:
            # Use the active connection
            if self._active_connection:
                connection_name = self._active_connection
            else:
                # Try to use the default connection
                if not self._driver:
                    raise ConnectionError("Cannot export graph. No active connection to Neo4j.")

        try:
            # Create a NetworkX graph
            G = nx.MultiDiGraph()

            # Get all nodes
            nodes_query = "MATCH (n) RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties"
            nodes_result = self.execute_query(nodes_query, connection_name=connection_name)

            # Add nodes to the graph
            for node in nodes_result:
                node_id = node["id"]
                labels = node["labels"]
                properties = node["properties"]

                # Add node to graph with its properties
                G.add_node(node_id, labels=labels, properties=properties)

            # Get all relationships
            rels_query = """
            MATCH (a)-[r]->(b)
            RETURN id(a) AS source, id(b) AS target, type(r) AS type, 
                   id(r) AS id, properties(r) AS properties
            """
            rels_result = self.execute_query(rels_query, connection_name=connection_name)

            # Add relationships to the graph
            for rel in rels_result:
                source = rel["source"]
                target = rel["target"]
                rel_type = rel["type"]
                rel_id = rel["id"]
                properties = rel["properties"]

                # Add edge to graph with its properties
                G.add_edge(source, target, key=rel_id, type=rel_type, properties=properties)

            # Save the graph to a file
            with open(file_path, 'wb') as f:
                pickle.dump(G, f)

            return True, f"Graph exported successfully with {len(G.nodes)} nodes and {len(G.edges)} relationships"
        except Exception as e:
            return False, f"Error exporting graph: {str(e)}"

    def import_graph(self, file_path: str, connection_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Imports a graph from a file into Neo4j.

        Args:
            file_path: Path to the file containing the graph.
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.

        Returns:
            A tuple containing (success, message).

        Raises:
            ConnectionError: If there is no active connection.
        """
        # If connection_name is provided, use that specific connection
        if connection_name:
            if connection_name not in self._connections:
                raise ConnectionError(f"Connection '{connection_name}' does not exist")

            if not self._connections[connection_name]["connected"]:
                raise ConnectionError(f"Connection '{connection_name}' is not connected")
        else:
            # Use the active connection
            if self._active_connection:
                connection_name = self._active_connection
            else:
                # Try to use the default connection
                if not self._driver:
                    raise ConnectionError("Cannot import graph. No active connection to Neo4j.")

        try:
            # Load the graph from file
            with open(file_path, 'rb') as f:
                G = pickle.load(f)

            # Clear the database
            self.execute_query("MATCH (n) DETACH DELETE n", connection_name=connection_name)

            # Create nodes
            for node_id, node_data in G.nodes(data=True):
                labels = node_data.get('labels', [])
                properties = node_data.get('properties', {})

                # Create label string
                label_string = ":".join(labels)

                # Filter out None values and non-primitive types
                filtered_props = {}
                for k, v in properties.items():
                    if v is not None and isinstance(v, (str, int, float, bool, list)):
                        filtered_props[k] = v

                # Create node
                query = f"CREATE (n:{label_string}) SET n = $props RETURN id(n)"
                new_id = self.query_to_value(query, {"props": filtered_props}, connection_name=connection_name)

                # Map old ID to new ID
                G.nodes[node_id]['new_id'] = new_id

            # Create relationships
            for source, target, key, edge_data in G.edges(data=True, keys=True):
                rel_type = edge_data.get('type', 'RELATED_TO')
                properties = edge_data.get('properties', {})

                # Get new IDs
                new_source = G.nodes[source].get('new_id')
                new_target = G.nodes[target].get('new_id')

                # Filter out None values and non-primitive types
                filtered_props = {}
                for k, v in properties.items():
                    if v is not None and isinstance(v, (str, int, float, bool, list)):
                        filtered_props[k] = v

                # Create relationship
                query = f"""
                MATCH (a), (b)
                WHERE id(a) = {new_source} AND id(b) = {new_target}
                CREATE (a)-[r:{rel_type}]->(b)
                """
                if filtered_props:
                    query += " SET r = $props"

                self.execute_query(query, {"props": filtered_props}, connection_name=connection_name)

            return True, f"Graph imported successfully with {len(G.nodes)} nodes and {len(G.edges)} relationships"
        except Exception as e:
            return False, f"Error importing graph: {str(e)}"


# Singleton instance - don't connect on initialization to avoid startup errors
db_manager = Neo4jManager(connect_on_init=False)
