import yaml
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import Neo4jError
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from collections import Counter

# Import isatools classes through our compatibility layer
try:
    from isatools.model import OntologyAnnotation, OntologySource
    ISATOOLS_AVAILABLE = True
except ImportError:
    from utils.isa_compatibility import get_isa_objects
    _, OntologyAnnotation, _, _, _, _, _, _ = get_isa_objects()
    OntologySource = None
    ISATOOLS_AVAILABLE = False

def load_db_config(fn='db_config.yaml'):
    """
    Loads the database configuration from a YAML file.

    :param fn: Path to the YAML configuration file.
    :return: Dictionary containing the database configuration.
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
        print(f"ERROR: Could not load {fn} - {e}")
        return None

class Neo4jConnection:
    """
    A robust Neo4j driver for connecting and executing queries with improved error handling and extended functionality.
    """

    def __init__(self, config=None, config_file=None, use_session_state=False):
        """
        Initialize the Neo4jConnection instance.

        :param config: Dictionary with database connection details (overrides config_file if provided).
        :param config_file: Path to a YAML file with database connection details.
        :param use_session_state: If True, use the connection from Streamlit session_state if available.
        """
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
                    return
            except (ImportError, AttributeError):
                # Fall back to config if session_state is not available or not connected
                pass

        # Use config if session_state is not available or not requested
        if config is None:
            if config_file:
                config = load_db_config(config_file)
            else:
                raise ValueError("Either a config dictionary or a config_file path must be provided.")

        required_keys = {"uri", "user", "password", "database"}
        if not all(key in config for key in required_keys):
            raise ValueError(f"Missing required keys in config. Expected keys: {required_keys}")

        self.uri = config["uri"]
        self.user = config["user"]
        self.password = config["password"]
        self.database = config.get("database", "neo4j")
        self._driver: Driver = None
        self._connect()

    def _connect(self):
        """
        Establishes a connection to the Neo4j database.
        """
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        except Neo4jError as e:
            raise ConnectionError(f"Failed to connect to Neo4j: {e}")

    def close(self):
        """
        Closes the Neo4j driver connection.
        """
        if self._driver:
            self._driver.close()
            self._driver = None

    def execute_query(self, query: str, parameters: dict = None):
        """
        Executes a Cypher query and returns the raw results.

        :param query: The Cypher query to execute.
        :param parameters: Optional dictionary of parameters to include in the query.
        :return: Neo4j result object.
        """
        if not self._driver:
            raise ConnectionError("Cannot run query. No active connection to Neo4j.")

        parameters = parameters or {}

        try:
            with self._driver.session(database=self.database) as session:
                return list(session.run(query, parameters))
        except Neo4jError as e:
            raise RuntimeError(f"Query execution failed: {e}")

    def query_to_dataframe(self, query: str, parameters: dict = None) -> pd.DataFrame:
        """
        Executes a Cypher query and returns the results as a Pandas DataFrame.

        :param query: The Cypher query to execute.
        :param parameters: Optional dictionary of parameters.
        :return: A Pandas DataFrame containing the query results.
        """
        result = self.execute_query(query, parameters)
        records = [dict(record) for record in result]
        return pd.DataFrame(records)

    def query_to_dict(self, query: str, parameters: dict = None) -> dict:
        """
        Executes a Cypher query and returns the results as a list of dictionaries.

        :param query: The Cypher query to execute.
        :param parameters: Optional dictionary of parameters.
        :return: A list of dictionaries representing the query results.
        """
        result = self.execute_query(query, parameters)
        return [dict(record) for record in result]

    def query_to_value(self, query: str, parameters: dict = None):
        """
        Executes a Cypher query and returns a single value or a set of values.

        :param query: The Cypher query to execute.
        :param parameters: Optional dictionary of parameters.
        :return: A single value if one result is returned, or a list of values if multiple rows are returned.
        """
        result = self.execute_query(query, parameters)
        values = [list(record.values())[0] for record in result]
        return values[0] if len(values) == 1 else values

    def push_dataframe(self, df: pd.DataFrame, label_col: str, property_cols: list, match_cols: list):
        """
        Pushes a DataFrame into Neo4j, using specified columns for labels, properties, and match criteria.

        :param df: The Pandas DataFrame containing data to push.
        :param label_col: The column containing labels for nodes.
        :param property_cols: The columns to be used as properties.
        :param match_cols: The columns to be used for matching existing nodes.
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

    def push_and_link_dataframe(self, df: pd.DataFrame, label_col: str, property_cols: list, match_cols: list, node_match_label: str, node_match_properties: list, node_match_relationship_type: str):
        """
        Pushes a DataFrame into Neo4j and links nodes based on match criteria.
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

        :param quiet: If True, suppresses success message output.
        :return: True if the connection is successful, raises an exception otherwise.
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

        :param label: Optional label to filter the summary. If None, summarizes terms for all labels.
        :return: A dictionary with label names as keys and dictionaries of property summaries as values.
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

    def load_ontology_relationships(self, ontology_annotations: List[OntologyAnnotation], 
                                   create_source_nodes: bool = True,
                                   relationship_type: str = "HAS_TERM") -> int:
        """
        Loads ontology terms and their relationships into Neo4j.

        This function creates nodes for ontology terms and optionally for their sources,
        and establishes relationships between them.

        :param ontology_annotations: List of OntologyAnnotation objects to load
        :param create_source_nodes: Whether to create nodes for ontology sources
        :param relationship_type: The type of relationship to create between source and term nodes
        :return: Number of relationships created
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


# Example usage:
# conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
# conn.test_connection()
# df = conn.query_to_dataframe("MATCH (n) RETURN n LIMIT 10")
# print(df)
# results = conn.query_to_dict("MATCH (n) RETURN n LIMIT 10")
# print(results)
# count = conn.query_to_value("MATCH (n) RETURN COUNT(n)")
# print(count)
# conn.close()
