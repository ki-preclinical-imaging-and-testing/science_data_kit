import docker
import streamlit as st
import socket
from neomodel import config
import pandas as pd
from neo4j import GraphDatabase
from pathlib import Path
import json
from pyvis.network import Network


client = docker.from_env()

def initialize_session():
    config.DATABASE_URL = f"bolt://{st.session_state['username']}:{st.session_state['password']}@localhost:{st.session_state['bolt_port']}"  # Change as needed

initialize_session()  # Ensure variables are set
QUERIES_FILE = Path("saved_queries.json")


def get_neo4j_status():
    """Check Neo4j container status."""
    try:
        initialize_session()
        existing_containers = client.containers.list(all=True, filters={"name": st.session_state["container_name"]})
        if existing_containers:
            return existing_containers[0].status
    except docker.errors.DockerException:
        return None
    return "not found"


def get_neo4j_hostname():
    """Retrieve Neo4j's hostname or IP address."""
    try:
        initialize_session()
        container = client.containers.get(st.session_state["container_name"])
        if container.status == "running":
            return container.attrs["NetworkSettings"]["IPAddress"] or "localhost"
    except Exception:
        return "localhost"  # Fallback


def find_free_port(start_port):
    """Finds a free port starting from `start_port`."""
    initialize_session()
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:  # Port is free
                return port
        port += 1


def start_neo4j_container():
    """Start the Neo4j container with user-defined credentials."""
    initialize_session()
    container_name = st.session_state["container_name"]
    try:
        # Lock credentials after first startup
        st.session_state["credentials_locked"] = True

        # Find free ports dynamically
        st.session_state["http_port"] = find_free_port(7474)
        st.session_state["bolt_port"] = find_free_port(7687)

        # Check if the container already exists
        existing_containers = client.containers.list(all=True, filters={"name": container_name})
        for container in existing_containers:
            if container.name == container_name:
                if container.status != "running":
                    container.start()
                st.session_state["container_status"] = "running"
                return

        # Start a new container
        client.containers.run(
            "neo4j:latest",
            name=container_name,
            ports={
                "7474/tcp": st.session_state["http_port"],
                "7687/tcp": st.session_state["bolt_port"]
            },
            environment={
                "NEO4J_AUTH": f"{st.session_state['username']}/{st.session_state['password']}",
            },
            detach=True,
            tty=True,
        )
        st.session_state["container_status"] = "running"
    except docker.errors.DockerException as e:
        st.sidebar.error(f"Error starting Neo4j: {e}")


def stop_neo4j_container():
    """Stop the Neo4j container."""
    try:
        initialize_session()
        existing_containers = client.containers.list(all=True, filters={"name": st.session_state["container_name"]})
        for container in existing_containers:
            if container.name == st.session_state["container_name"] and container.status == "running":
                container.stop()
                st.session_state["container_status"] = "stopped"
                return
    except docker.errors.DockerException as e:
        st.sidebar.error(f"Error stopping Neo4j: {e}")


# Function to fetch available labels from Neo4j
def fetch_available_labels():
    with st.session_state["db_connection"].session() as session:
        result = session.run("CALL db.labels()")
        labels = [record[0] for record in result]
        return labels

def fetch_entity_labels(session):
    """Fetch all node labels from the Neo4j database."""
    result = session.run("CALL db.labels()")
    return [record[0] for record in result]


def fetch_node_properties(session, label):
    """Fetch all property keys for a given label."""
    result = session.run(f"""
        MATCH (n:{label})
        UNWIND keys(n) AS property
        RETURN DISTINCT property
    """)
    return [record["property"] for record in result]


def fetch_nodes_with_properties(session, label, selected_properties):
    """Fetch all nodes with selected properties for a given label."""
    if not selected_properties:
        return pd.DataFrame(columns=["No properties selected"])

    properties_query = ", ".join([f"n.{prop} AS `{prop}`" for prop in selected_properties])

    result = session.run(f"""
        MATCH (n:{label})
        RETURN {properties_query}
    """)
    nodes = [record.data() for record in result]
    return pd.DataFrame(nodes) if nodes else pd.DataFrame(columns=selected_properties)

# Utility Functions
def load_saved_queries():
    """Load saved queries from the JSON file."""
    if QUERIES_FILE.exists():
        with open(QUERIES_FILE, "r") as file:
            return json.load(file)
    return {}

def save_queries(queries):
    """Save queries to the JSON file."""
    with open(QUERIES_FILE, "w") as file:
        json.dump(queries, file, indent=4)

# Streamlit Query Management Section
def manage_queries(recall_query):
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


# Neo4j Connection
def get_neo4j_session(uri, user, password, database=None):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    session = driver.session(database=database) if database else driver.session()
    return session


# Fetch available databases
def fetch_databases(session):
    query = "SHOW DATABASES"
    results = session.run(query)
    return [record["name"] for record in results]


# Schema Extraction Algorithm
def extract_schema(results):
    triples = set()
    for record in results:
        triples.add((record["subjectLabel"], record["predicateType"], record["objectLabel"]))
    nodes = {label for triple in triples for label in (triple[0], triple[2])}
    return triples, nodes


# Pyvis Graph Creation with Layout Options
def create_pyvis_graph(triples, layout, physics_enabled):
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
                    "springLength": 170,  # Ideal edge length
                    "springConstant": 0.05,  # Spring stiffness
                    "damping": 0.09  # Motion damping factor
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

def fetch_nodes_by_label(session, label, with_clause):
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
    return pd.DataFrame(nodes).drop_duplicates()

