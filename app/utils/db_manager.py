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

# Import isatools classes through our compatibility layer
try:
    from isatools.model import OntologyAnnotation, OntologySource
    ISATOOLS_AVAILABLE = True
except ImportError:
    try:
        from utils.isa_compatibility import get_isa_objects
        _, OntologyAnnotation, _, _, _, _, _, _ = get_isa_objects()
        OntologySource = None
        ISATOOLS_AVAILABLE = False
    except ImportError:
        OntologyAnnotation = None
        OntologySource = None
        ISATOOLS_AVAILABLE = False


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
    - Managing Neo4j connections
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
                use_session_state: bool = False):
        """
        Initialize the Neo4jManager instance.

        Args:
            config: Dictionary with database connection details.
            config_file: Path to a YAML file with database connection details.
            use_session_state: If True, use the connection from Streamlit session_state if available.

        Raises:
            ConnectionError: If the connection details are invalid or the connection fails.
        """
        # Skip initialization if already initialized (singleton pattern)
        if self._initialized:
            return
            
        self._driver = None
        self.uri = None
        self.user = None
        self.password = None
        self.database = None
        self.container_name = "neo4j-instance"
        self.http_port = 7474
        self.bolt_port = 7687
        
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
            if config_file:
                config = load_db_config(config_file)
            else:
                # Try to load from default locations
                config = load_db_config('.db_config_auto.yaml')
                if not config:
                    config = load_db_config('.db_config.yaml')
                if not config:
                    config = load_db_config('db_config.yaml')
                    
        if not config:
            raise ConnectionError("No configuration provided and no default configuration found.")

        required_keys = {"uri", "user", "password"}
        if not all(key in config for key in required_keys):
            raise ConnectionError(f"Missing required keys in config. Expected keys: {required_keys}")

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
            
        self._connect()
        self._initialized = True
    
    def _connect(self) -> None:
        """
        Establishes a connection to the Neo4j database.

        Raises:
            ConnectionError: If the connection fails.
        """
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test the connection
            with self._driver.session(database=self.database) as session:
                session.run("RETURN 1")
        except Exception as e:
            self._driver = None
            raise ConnectionError(f"Failed to connect to Neo4j: {e}")
    
    def close(self) -> None:
        """
        Closes the Neo4j driver connection.
        """
        if self._driver:
            self._driver.close()
            self._driver = None
    
    def is_connected(self) -> bool:
        """
        Checks if the manager is connected to a Neo4j database.

        Returns:
            True if connected, False otherwise.
        """
        if not self._driver:
            return False
            
        try:
            with self._driver.session(database=self.database) as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a Cypher query and returns the results.

        Args:
            query: The Cypher query to execute.
            parameters: Optional dictionary of parameters to include in the query.

        Returns:
            List of dictionaries containing the query results.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        if not self._driver:
            raise ConnectionError("Cannot run query. No active connection to Neo4j.")

        parameters = parameters or {}

        try:
            with self._driver.session(database=self.database) as session:
                result = session.run(query, parameters)
                return [dict(record) for record in result]
        except Neo4jError as e:
            raise QueryError(f"Query execution failed: {e}")
    
    def query_to_dataframe(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Executes a Cypher query and returns the results as a Pandas DataFrame.

        Args:
            query: The Cypher query to execute.
            parameters: Optional dictionary of parameters.

        Returns:
            A Pandas DataFrame containing the query results.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        results = self.execute_query(query, parameters)
        return pd.DataFrame(results)
    
    def query_to_value(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Executes a Cypher query and returns a single value.

        Args:
            query: The Cypher query to execute.
            parameters: Optional dictionary of parameters.

        Returns:
            A single value if one result is returned, or a list of values if multiple rows are returned.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        results = self.execute_query(query, parameters)
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
    
    def export_graph(self, file_path: str) -> Tuple[bool, str]:
        """
        Exports the entire graph to a file.

        Args:
            file_path: Path where the graph will be saved.

        Returns:
            A tuple containing (success, message).

        Raises:
            ConnectionError: If there is no active connection.
        """
        if not self._driver:
            raise ConnectionError("Cannot export graph. No active connection to Neo4j.")
            
        try:
            # Create a NetworkX graph
            G = nx.MultiDiGraph()
            
            # Get all nodes
            nodes_query = "MATCH (n) RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties"
            nodes_result = self.execute_query(nodes_query)
            
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
            rels_result = self.execute_query(rels_query)
            
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
    
    def import_graph(self, file_path: str) -> Tuple[bool, str]:
        """
        Imports a graph from a file into Neo4j.

        Args:
            file_path: Path to the file containing the graph.

        Returns:
            A tuple containing (success, message).

        Raises:
            ConnectionError: If there is no active connection.
        """
        if not self._driver:
            raise ConnectionError("Cannot import graph. No active connection to Neo4j.")
            
        try:
            # Load the graph from file
            with open(file_path, 'rb') as f:
                G = pickle.load(f)
                
            # Clear the database
            self.execute_query("MATCH (n) DETACH DELETE n")
            
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
                new_id = self.query_to_value(query, {"props": filtered_props})
                
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
                    
                self.execute_query(query, {"props": filtered_props})
                
            return True, f"Graph imported successfully with {len(G.nodes)} nodes and {len(G.edges)} relationships"
        except Exception as e:
            return False, f"Error importing graph: {str(e)}"


# Singleton instance
db_manager = Neo4jManager()