"""
NeoDash Server integration for Science Data Kit.

This module provides functionality for managing NeoDash containers using Docker.
It allows starting, stopping, and connecting to NeoDash dashboard instances.
"""

import time
import socket
import docker
import os
from docker.errors import NotFound

# Import from streamlit conditionally to allow using this module without streamlit
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Initialize Docker client
client = docker.from_env()

def initialize_neodash_session():
    """
    Initialize NeoDash session state variables in Streamlit.
    
    This function sets default values for container name, port, and connection status
    if they don't already exist in the session state.
    """
    if not HAS_STREAMLIT:
        return
        
    if "neodash_container_name" not in st.session_state:
        st.session_state["neodash_container_name"] = "dsk-neodash-instance"
    if "neodash_port" not in st.session_state:
        st.session_state["neodash_port"] = 5005
    if "neodash_connected" not in st.session_state:
        st.session_state["neodash_connected"] = False

def is_port_available(port, host="0.0.0.0"):
    """
    Check if a port is available for binding.
    
    Args:
        port (int): The port to check
        host (str): The host to bind to
        
    Returns:
        bool: True if the port is available, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False

def find_free_port(start=5005):
    """
    Find a free port starting from the given port number.
    
    Args:
        start (int): The port number to start searching from
        
    Returns:
        int: A free port number
    """
    port = start
    while not is_port_available(port):
        port += 1
    return port

def get_container_port_binding(container, internal_port="5005/tcp"):
    """
    Get the host port binding for a container's internal port.
    
    Args:
        container: The Docker container object
        internal_port (str): The internal port specification
        
    Returns:
        int: The host port number, or None if not found
    """
    try:
        return int(container.attrs["HostConfig"]["PortBindings"][internal_port][0]["HostPort"])
    except (KeyError, IndexError, TypeError):
        return None

def get_container_ip(container):
    """
    Get the IP address of a container, defaulting to localhost if not available.
    
    Args:
        container: The Docker container object
        
    Returns:
        str: The IP address of the container
    """
    ip = container.attrs["NetworkSettings"]["IPAddress"] or "localhost"
    if HAS_STREAMLIT:
        st.session_state['neodash_host_ip'] = ip
    return ip

def start_neodash_container(neo4j_uri=None, neo4j_user=None, neo4j_password=None):
    """
    Start a NeoDash container or connect to an existing one.

    This function will:
    1. Check if a container with the configured name already exists
    2. If it exists, start it if it's not running and return the URL
    3. If it doesn't exist, create a new container and return the URL

    Args:
        neo4j_uri (str, optional): The Neo4j URI to connect to
        neo4j_user (str, optional): The Neo4j username
        neo4j_password (str, optional): The Neo4j password

    Returns:
        str: The URL to access NeoDash, or None if there was an error
    """
    if HAS_STREAMLIT:
        initialize_neodash_session()
        name = st.session_state["neodash_container_name"]
        
        # Get Neo4j connection details from session state if not provided
        if neo4j_uri is None:
            neo4j_uri = st.session_state.get("neo4j_uri", "bolt://localhost:7687")
        if neo4j_user is None:
            neo4j_user = st.session_state.get("neo4j_user", "neo4j")
        if neo4j_password is None:
            neo4j_password = st.session_state.get("neo4j_password", "neo4jiscool")
    else:
        name = "dsk-neodash-instance"
        # Use default values if not provided
        neo4j_uri = neo4j_uri or "bolt://localhost:7687"
        neo4j_user = neo4j_user or "neo4j"
        neo4j_password = neo4j_password or "neo4jiscool"
    
    try:
        # Check if container already exists
        container = client.containers.get(name)
        
        # Get the bound port
        bound_port = get_container_port_binding(container)
        if not bound_port:
            if HAS_STREAMLIT:
                st.error(f"⚠️ Container '{name}' exists but has no bound port.")
            return None
        
        if HAS_STREAMLIT:
            st.session_state["neodash_port"] = bound_port
        
        # Start container if it's not running
        if container.status != "running":
            container.start()
            if HAS_STREAMLIT:
                st.info(f"🔄 Started container '{name}'...")
            time.sleep(2)
        
        # Get container IP and create URL
        neodash_host_ip = get_container_ip(container)
        url = f"http://{neodash_host_ip}:{bound_port}"
        
        if HAS_STREAMLIT:
            st.success(f"✅ NeoDash started!")
            st.markdown(f"🔗 [Open NeoDash]({url})")
            
            # Set connected state
            st.session_state["neodash_connected"] = True
        
        return url
        
    except NotFound:
        # Container does not exist yet - create it
        port = find_free_port(5005)
        if HAS_STREAMLIT:
            st.session_state["neodash_port"] = port
        
        # Create and start the container
        try:
            container = client.containers.run(
                "neo4jlabs/neodash:latest",
                name=name,
                ports={"5005/tcp": port},
                environment={
                    "NEO4J_URI": neo4j_uri,
                    "NEO4J_USER": neo4j_user,
                    "NEO4J_PASSWORD": neo4j_password
                },
                detach=True,
                tty=True,
            )
            
            neodash_host_ip = get_container_ip(container)
            if HAS_STREAMLIT:
                st.info(f"🚀 Starting new NeoDash container on port {port}...")
            time.sleep(2)
            
            url = f"http://{neodash_host_ip}:{port}"
            if HAS_STREAMLIT:
                st.success(f"✅ NeoDash Started")
                st.markdown(f"🔗 [Open NeoDash]({url})")
                
                # Set connected state
                st.session_state["neodash_connected"] = True
            
            return url
        except Exception as e:
            error_msg = f"Failed to start NeoDash container: {e}"
            if HAS_STREAMLIT:
                st.error(f"❌ {error_msg}")
            return None
        
    except Exception as e:
        error_msg = f"Failed to start NeoDash container: {e}"
        if HAS_STREAMLIT:
            st.error(f"❌ {error_msg}")
        return None

def stop_neodash_container():
    """
    Stop a running NeoDash container.
    
    Returns:
        bool: True if the container was stopped, False otherwise
    """
    if HAS_STREAMLIT:
        initialize_neodash_session()
        name = st.session_state["neodash_container_name"]
    else:
        name = "dsk-neodash-instance"
    
    try:
        container = client.containers.get(name)
        if container.status == "running":
            container.stop()
            if HAS_STREAMLIT:
                st.session_state["neodash_connected"] = False
            return True
        return False
    except Exception as e:
        error_msg = f"Error stopping NeoDash container: {e}"
        if HAS_STREAMLIT:
            st.error(f"❌ {error_msg}")
        return False