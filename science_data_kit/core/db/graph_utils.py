"""
Graph Utilities for Science Data Kit

This module provides utilities for working with Neo4j graphs.
It includes functions for executing queries, converting results to different formats,
and working with ontology terms and relationships.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
import pandas as pd
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import Neo4jError

# Import isatools classes through our compatibility layer
try:
    from isatools.model import OntologyAnnotation, OntologySource
    ISATOOLS_AVAILABLE = True
except ImportError:
    try:
        from science_data_kit.core.utils.isa_compatibility import get_isa_objects
        _, OntologyAnnotation, _, _, _, _, _, _ = get_isa_objects()
        OntologySource = None
        ISATOOLS_AVAILABLE = False
    except ImportError:
        OntologyAnnotation = None
        OntologySource = None
        ISATOOLS_AVAILABLE = False

class Neo4jConnection:
    """
    A robust Neo4j driver for connecting and executing queries with improved error handling and extended functionality.
    
    This class provides methods for:
    - Managing Neo4j connections
    - Executing queries and processing results
    - Working with DataFrames
    - Working with ontology terms and relationships
    
    Note: This class is provided for backward compatibility. For new code, use the Neo4jManager class instead.
    """
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """
        Initialize the Neo4jConnection instance.
        
        Args:
            uri: The URI of the Neo4j server.
            user: The username for authentication.
            password: The password for authentication.
            database: The name of the database to connect to.
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver: Optional[Driver] = None
        self._connect()
    
    def _connect(self) -> None:
        """
        Establishes a connection to the Neo4j database.
        
        Raises:
            ConnectionError: If the connection fails.
        """
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        except Neo4jError as e:
            raise ConnectionError(f"Failed to connect to Neo4j: {e}")
    
    def close(self) -> None:
        """
        Closes the Neo4j driver connection.
        """
        if self._driver:
            self._driver.close()
            self._driver = None
    
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
            RuntimeError: If the query execution fails.
        """
        if not self._driver:
            raise ConnectionError("Cannot run query. No active connection to Neo4j.")
        
        parameters = parameters or {}
        
        try:
            with self._driver.session(database=self.database) as session:
                result = session.run(query, parameters)
                return [dict(record) for record in result]
        except Neo4jError as e:
            raise RuntimeError(f"Query execution failed: {e}")
    
    def query_to_dataframe(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Executes a Cypher query and returns the results as a Pandas DataFrame.
        
        Args:
            query: The Cypher query to execute.
            parameters: Optional dictionary of parameters.
            
        Returns:
            A Pandas DataFrame containing the query results.
        """
        result = self.execute_query(query, parameters)
        return pd.DataFrame(result)
    
    def query_to_dict(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a Cypher query and returns the results as a list of dictionaries.
        
        Args:
            query: The Cypher query to execute.
            parameters: Optional dictionary of parameters.
            
        Returns:
            A list of dictionaries representing the query results.
        """
        return self.execute_query(query, parameters)
    
    def query_to_value(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Executes a Cypher query and returns a single value or a set of values.
        
        Args:
            query: The Cypher query to execute.
            parameters: Optional dictionary of parameters.
            
        Returns:
            A single value if one result is returned, or a list of values if multiple rows are returned.
        """
        result = self.execute_query(query, parameters)
        values = [list(record.values())[0] for record in result]
        return values[0] if len(values) == 1 else values
    
    def push_dataframe(self, df: pd.DataFrame, label_col: str, property_cols: List[str], match_cols: List[str]) -> None:
        """
        Pushes a DataFrame into Neo4j, using specified columns for labels, properties, and match criteria.
        
        Args:
            df: The Pandas DataFrame containing data to push.
            label_col: The column containing labels for nodes.
            property_cols: The columns to be used as properties.
            match_cols: The columns to be used for matching existing nodes.
            
        Raises:
            ValueError: If the label column is not found or no match columns are provided.
        """
        if label_col not in df.columns:
            raise ValueError(f"Label column '{label_col}' not found in DataFrame.")
        
        for _, row in df.iterrows():
            label = row[label_col]
            properties = {col: row[col] for col in property_cols if col in df.columns}
            match_criteria = {col: row[col] for col in match_cols if col in df.columns}
            
            if not match_criteria:
                raise ValueError("At least one match column must be provided.")
            
            match_string = ", ".join(f"{k}: ${k}" for k in match_criteria.keys())
            properties_string = ", ".join(f"{k}: ${k}" for k in properties.keys())
            
            query = f"""
            MERGE (n:{label} {{ {match_string} }})
            SET n += {{ {properties_string} }}
            """
            
            self.execute_query(query, {**match_criteria, **properties})
    
    def push_and_link_dataframe(
        self, 
        df: pd.DataFrame, 
        label_col: str, 
        property_cols: List[str], 
        match_cols: List[str], 
        node_match_label: str, 
        node_match_properties: List[str], 
        node_match_relationship_type: str
    ) -> None:
        """
        Pushes a DataFrame into Neo4j and links nodes based on match criteria.
        
        Args:
            df: The Pandas DataFrame containing data to push.
            label_col: The column containing labels for nodes.
            property_cols: The columns to be used as properties.
            match_cols: The columns to be used for matching existing nodes.
            node_match_label: The label of the nodes to match against.
            node_match_properties: The properties to use for matching target nodes.
            node_match_relationship_type: The type of relationship to create.
            
        Raises:
            ValueError: If the label column is not found or no match columns are provided.
        """
        if label_col not in df.columns:
            raise ValueError(f"Label column '{label_col}' not found in DataFrame.")
        
        for _, row in df.iterrows():
            label = row[label_col]
            label_match = row[node_match_label]
            properties = {col: row[col] for col in property_cols if col in df.columns}
            match_criteria = {col: row[col] for col in match_cols if col in df.columns}
            node_match_criteria = {col: row[col] for col in node_match_properties if col in df.columns}
            
            if not match_criteria or not node_match_criteria:
                raise ValueError("Both entity match columns and node match columns must be provided.")
            
            match_string = ", ".join(f"{k}: ${k}" for k in match_criteria.keys())
            properties_string = ", ".join(f"{k}: ${k}" for k in properties.keys())
            node_match_string = ", ".join(f"{k}: ${k}" for k in node_match_criteria.keys())
            
            query = f"""
            MERGE (n:{label} {{ {match_string} }})
            SET n += {{ {properties_string} }}
            WITH n
            MATCH (m:{label_match} {{ {node_match_string} }})
            MERGE (n)-[:{node_match_relationship_type}]->(m)
            """
            
            self.execute_query(query, {**match_criteria, **properties, **node_match_criteria})
    
    def test_connection(self, quiet: bool = False) -> bool:
        """
        Tests the Neo4j connection by running a simple query.
        
        Args:
            quiet: If True, suppresses success message output.
            
        Returns:
            True if the connection is successful, raises an exception otherwise.
            
        Raises:
            ConnectionError: If the connection fails.
        """
        try:
            self.execute_query("RETURN 1")
            if not quiet:
                print("Connection successful!")
            return True
        except Exception as e:
            raise ConnectionError(f"Connection failed: {e}")
    
    def summarize_ontology_terms_for_labels(self, label: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Summarizes available ontology terms used as properties for node labels in Neo4j.
        
        This function queries the Neo4j database to find properties that contain ontology terms
        (identified by having both a value and a URI) and summarizes them by label and property name.
        
        Args:
            label: Optional label to filter the summary. If None, summarizes terms for all labels.
            
        Returns:
            A dictionary with label names as keys and dictionaries of property summaries as values.
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
    
    def load_ontology_relationships(
        self, 
        ontology_annotations: List[Any], 
        create_source_nodes: bool = True,
        relationship_type: str = "HAS_TERM"
    ) -> int:
        """
        Loads ontology terms and their relationships into Neo4j.
        
        This function creates nodes for ontology terms and optionally for their sources,
        and establishes relationships between them.
        
        Args:
            ontology_annotations: List of OntologyAnnotation objects to load.
            create_source_nodes: Whether to create nodes for ontology sources.
            relationship_type: The type of relationship to create between source and term nodes.
            
        Returns:
            Number of relationships created.
        """
        if not ontology_annotations:
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

# Compatibility function to create a Neo4jConnection from a Neo4jManager
def create_connection_from_manager(manager) -> Neo4jConnection:
    """
    Creates a Neo4jConnection instance from a Neo4jManager instance.
    
    This function is provided for backward compatibility with code that expects a Neo4jConnection.
    
    Args:
        manager: A Neo4jManager instance.
        
    Returns:
        A Neo4jConnection instance with the same connection details.
    """
    return Neo4jConnection(
        uri=manager.uri,
        user=manager.user,
        password=manager.password,
        database=manager.database
    )