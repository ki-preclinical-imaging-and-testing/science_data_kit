"""
Database Adapter for Science Data Kit

This module provides adapter functions that bridge the old database.py functions
with the new Neo4jManager class from science_data_kit.core.db.db_manager.
"""

import streamlit as st
import os
import yaml
import json
from typing import Dict, Any, List, Tuple, Optional, Union
from pathlib import Path
import pandas as pd
import networkx as nx
from pyvis.network import Network

from science_data_kit.core.db.db_manager import (
    Neo4jManager, load_db_config, update_db_config_auto, find_free_port
)

# Initialize the Neo4jManager instance
db_manager = Neo4jManager()

def get_neo4j_status() -> str:
    """Check Neo4j container status."""
    return db_manager.get_container_status()

def get_neo4j_hostname() -> str:
    """Retrieve Neo4j's hostname or IP address."""
    return db_manager.get_hostname()

def start_neo4j_container() -> bool:
    """Start the Neo4j container with user-defined credentials."""
    # Check if password is the default 'neo4j' and change it if needed
    if st.session_state["password"] == "neo4j":
        st.session_state["password"] = "neo4jiscool"  # Set to a non-default password
        # Update the config file with the new password
        try:
            update_db_config_auto(
                "localhost", 
                str(st.session_state["bolt_port"]),
                st.session_state["username"],
                st.session_state["password"]
            )
        except Exception as e:
            st.warning(f"Could not update config with new password: {e}")

    try:
        # Lock credentials after first startup
        st.session_state["credentials_locked"] = True

        # Find free ports dynamically
        st.session_state["http_port"] = find_free_port(7474)
        st.session_state["bolt_port"] = find_free_port(7687)

        # Start the container using Neo4jManager
        version = st.session_state.get('neo4j_version', 'latest')
        success = db_manager.start_container(version)

        if success:
            st.session_state["container_status"] = "running"

            # Update the .db_config_auto.yaml file with the container's IP address
            hostname = get_neo4j_hostname()
            update_db_config_auto(
                hostname,
                str(st.session_state["bolt_port"]),
                st.session_state["username"],
                st.session_state["password"]
            )
            return True
        else:
            st.error("Failed to start Neo4j container.")
            return False
    except Exception as e:
        st.error(f"Error starting Neo4j container: {e}")
        return False

def stop_neo4j_container() -> bool:
    """Stop the Neo4j container."""
    success = db_manager.stop_container()
    if success:
        st.session_state["container_status"] = "stopped"
    return success

def get_neo4j_session(uri: str, user: str, password: str, database: Optional[str] = None):
    """
    Get a Neo4j session using the Neo4jManager.

    Args:
        uri: The URI of the Neo4j server.
        user: The username for authentication.
        password: The password for authentication.
        database: The name of the database to connect to.

    Returns:
        A Neo4j session object.
    """
    # Update the Neo4jManager with the provided credentials
    db_manager.uri = uri
    db_manager.user = user
    db_manager.password = password
    db_manager.database = database or "neo4j"

    # Connect to the database
    db_manager._connect()

    # Return the driver's session
    return db_manager._driver.session(database=db_manager.database)

def fetch_databases(session) -> List[str]:
    """
    Fetch available databases from Neo4j.

    Args:
        session: A Neo4j session object.

    Returns:
        A list of database names.
    """
    query = "SHOW DATABASES"
    results = session.run(query)
    return [record["name"] for record in results]

def fetch_available_labels() -> List[str]:
    """
    Fetch available labels from Neo4j.

    Returns:
        A list of label names.
    """
    return db_manager.fetch_labels()

def fetch_entity_labels(session) -> List[str]:
    """
    Fetch all node labels from the Neo4j database.

    Args:
        session: A Neo4j session object.

    Returns:
        A list of label names.
    """
    return db_manager.fetch_labels()

def fetch_node_properties(session, label: str) -> List[str]:
    """
    Fetch all property keys for a given label.

    Args:
        session: A Neo4j session object.
        label: The node label to query.

    Returns:
        A list of property keys.
    """
    return db_manager.fetch_node_properties(label)

def fetch_nodes_with_properties(session, label: str, selected_properties: List[str]) -> pd.DataFrame:
    """
    Fetch all nodes with selected properties for a given label.

    Args:
        session: A Neo4j session object.
        label: The node label to query.
        selected_properties: List of property keys to return.

    Returns:
        A pandas DataFrame containing the nodes with selected properties.
    """
    if not selected_properties:
        return pd.DataFrame(columns=["No properties selected"])

    nodes = db_manager.fetch_nodes(label, selected_properties)
    return pd.DataFrame(nodes) if nodes else pd.DataFrame(columns=selected_properties)

def export_graph_to_file(session, file_path: str) -> Tuple[bool, str]:
    """
    Export the entire Neo4j graph to a file.

    Args:
        session: A Neo4j session object.
        file_path: Path where the graph will be saved.

    Returns:
        A tuple containing (success, message).
    """
    return db_manager.export_graph(file_path)

def import_graph_from_file(session, file_path: str) -> Tuple[bool, str]:
    """
    Import a graph from a file into Neo4j.

    Args:
        session: A Neo4j session object.
        file_path: Path to the file containing the graph.

    Returns:
        A tuple containing (success, message).
    """
    return db_manager.import_graph(file_path)

# Additional functions from database.py that don't have direct equivalents in Neo4jManager
# These functions are implemented using the Neo4jManager's execute_query method

def extract_schema(results: List[Dict[str, Any]]) -> Tuple[set, set]:
    """
    Extract schema from query results.

    Args:
        results: List of dictionaries containing query results.

    Returns:
        A tuple containing (triples, nodes).
    """
    triples = set()
    for record in results:
        triples.add((record["subjectLabel"], f'{record["predicateType"][1]} ({record["predicateType"][0]})', record["objectLabel"]))
    nodes = {label for triple in triples for label in (triple[0], triple[2])}
    return triples, nodes

def create_pyvis_graph(triples: set, layout: str, physics_enabled: bool) -> Network:
    """
    Create a Pyvis network graph from a set of triples.

    Args:
        triples: Set of triples (subject, predicate, object).
        layout: Layout type ("Hierarchical" or "Force-Directed").
        physics_enabled: Whether to enable physics simulation.

    Returns:
        A Pyvis Network object.
    """
    net = Network(notebook=False, height="750px", width="100%")

    # Common node and edge settings
    common_options = {
        "nodes": {
            "font": {
                "size": 16,
                "bold": True,
                "align": "center",
            },  # Font size for node labels
        },
        "edges": {
            "arrows": {"to": {"enabled": True}},  # Add arrows for directionality
            "smooth": {"enabled": True},  # Enable smooth edges
            "font": {
                "size": 12,
                "align": "middle"
            }
        },
        "interaction": {
            "hover": True,  # Enable hover effects
            "navigationButtons": True  # Add zoom and pan buttons
        },
        "physics": {
            "enabled": physics_enabled
        }
    }

    # Layout-specific settings
    if layout == "Hierarchical":
        layout_options = {
            "layout": {
                "hierarchical": {
                    "enabled": True,
                    "levelSeparation": 150,  # Distance between levels
                    "nodeSpacing": 100,  # Horizontal spacing
                    "treeSpacing": 200,  # Spacing between subtrees
                    "direction": "UD",  # Up-to-Down layout
                    "sortMethod": "directed"  # Sort by hub size: "hubsize"
                }
            }
        }
    else:  # Force-Directed Layout
        layout_options = {
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -4000,  # Strength of gravity
                    "centralGravity": 0.5,  # Pull toward center
                    "springLength": 200,  # Ideal edge length
                    "springConstant": 0.013,  # Spring stiffness
                    "damping": 0.1  # Motion damping factor
                }
            },
            "layout": {"improvedLayout": True}  # Optimize node positioning
        }

    # Combine common options with layout-specific options
    options = {**common_options, **layout_options}

    # Apply options to the network
    net.set_options(json.dumps(options))

    # Add nodes and edges from triples
    for subject, predicate, object_ in triples:
        net.add_node(subject, label=subject)
        net.add_node(object_, label=object_)
        net.add_edge(subject, object_, label=predicate, arrows="to")  # Directionality

    return net

def fetch_nodes_by_label(session, label: str, with_clause: str) -> pd.DataFrame:
    """
    Fetch nodes with a specific label, optionally filtered by a WITH clause.

    Args:
        session: A Neo4j session object.
        label: The node label to query.
        with_clause: Optional WITH clause for filtering.

    Returns:
        A pandas DataFrame containing the nodes.
    """
    query = f"""
    {with_clause}
    MATCH (n:{label})
    RETURN n AS node
    UNION
    {with_clause}
    MATCH (m:{label})
    RETURN m AS node
    """
    results = session.run(query)

    # Collect unique nodes from both queries
    nodes = [dict(record["node"]) for record in results]

    # Convert lists to tuples in the dictionaries to make them hashable
    for node in nodes:
        for key, value in node.items():
            if isinstance(value, list):
                node[key] = tuple(value) if value else None

    return pd.DataFrame(nodes).drop_duplicates()

# Function to manage saved queries
QUERIES_FILE = Path("saved_queries.json")

def manage_queries(recall_query: str) -> str:
    """
    Manage saved queries.

    Args:
        recall_query: The current query.

    Returns:
        The updated query.
    """
    import json

    # Load saved queries
    def load_saved_queries():
        if QUERIES_FILE.exists():
            with open(QUERIES_FILE, "r") as file:
                return json.load(file)
        return {}

    def save_queries(queries):
        with open(QUERIES_FILE, "w") as file:
            json.dump(queries, file, indent=4)

    # Load saved queries
    saved_queries = load_saved_queries()

    # Save current query
    query_name = st.text_input("Save Current Query As")
    if st.button("Save Query"):
        if query_name:
            saved_queries[query_name] = recall_query
            save_queries(saved_queries)
            st.success(f"Query '{query_name}' saved successfully!")
        else:
            st.error("Please provide a name for the query.")

    # Load a query
    if saved_queries:
        selected_query_name = st.selectbox("Load Saved Query", [""]
                                           + list(saved_queries.keys()), label_visibility="visible")
        if selected_query_name:
            recall_query = saved_queries[selected_query_name]

    # Delete a query
    if saved_queries:
        delete_query_name = st.selectbox("Delete Saved Query",
                                         [""] + list(saved_queries.keys()), label_visibility="visible",
                                         key="delete_query")
        if delete_query_name and st.button(f"Delete Query '{delete_query_name}'"):
            saved_queries.pop(delete_query_name, None)
            save_queries(saved_queries)

    return recall_query
