import docker
import streamlit as st
import socket
from neomodel import config
import pandas as pd
from neo4j import GraphDatabase


client = docker.from_env()

def initialize_session():
    """Ensure all session state variables are properly initialized."""
    if "container_status" not in st.session_state:
        st.session_state["container_status"] = None
    if "container_name" not in st.session_state:
        st.session_state["container_name"] = "neo4j-instance"
    if "http_port" not in st.session_state:
        st.session_state["http_port"] = 7474
    if "bolt_port" not in st.session_state:
        st.session_state["bolt_port"] = 7687
    if "username" not in st.session_state:
        st.session_state["username"] = "neo4j"
    if "password" not in st.session_state:
        st.session_state["password"] = "neo4jiscool"
    if "credentials_locked" not in st.session_state:
        st.session_state["credentials_locked"] = False  # Prevent changes after start
    if "db_connection" not in st.session_state:
        st.session_state["db_connection"] = GraphDatabase.driver(
            f"bolt://localhost:{st.session_state['bolt_port']}",
            auth=(st.session_state['username'],
                  st.session_state['password'])
        )

    config.DATABASE_URL = f"bolt://{st.session_state['username']}:{st.session_state['password']}@localhost:{st.session_state['bolt_port']}"  # Change as needed

initialize_session()  # Ensure variables are set


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
