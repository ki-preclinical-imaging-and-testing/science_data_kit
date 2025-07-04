"""
Jupyter Server integration for Science Data Kit.

This module provides functionality for managing Jupyter Lab containers using Docker.
It allows starting, stopping, and connecting to Jupyter Lab instances.
"""

import docker
import socket
import os
import time
from docker.errors import NotFound

# Import from streamlit conditionally to allow using this module without streamlit
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Initialize Docker client
client = docker.from_env()

def initialize_jupyter_session():
    """
    Initialize Jupyter session state variables in Streamlit.
    
    This function sets default values for container name, port, and token
    if they don't already exist in the session state.
    """
    if not HAS_STREAMLIT:
        return
        
    if "jupyter_container_name" not in st.session_state:
        st.session_state["jupyter_container_name"] = "dsk-jupyter-instance"
    if "jupyter_port" not in st.session_state:
        st.session_state["jupyter_port"] = 8888
    if "jupyter_token" not in st.session_state:
        st.session_state["jupyter_token"] = "letmein"

def is_port_in_use(port, host='localhost'):
    """
    Check if a port is in use.
    
    Args:
        port (int): The port to check
        host (str): The host to check against
        
    Returns:
        bool: True if the port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

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

def find_free_port(start=8888):
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

def get_container_port_binding(container, internal_port="8888/tcp"):
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
        st.session_state['jupyter_host_ip'] = ip
    return ip

def start_jupyter_container():
    """
    Start a Jupyter Lab container or connect to an existing one.

    This function will:
    1. Check if a container with the configured name already exists
    2. If it exists, start it if it's not running and return the URL
    3. If it doesn't exist, create a new container and return the URL

    Returns:
        str: The URL to access Jupyter Lab, or None if there was an error
    """
    if HAS_STREAMLIT:
        initialize_jupyter_session()
        name = st.session_state["jupyter_container_name"]
        token = st.session_state["jupyter_token"]
    else:
        name = "dsk-jupyter-instance"
        token = "letmein"

    try:
        # Try to get an existing container
        container = client.containers.get(name)
        port = find_free_port(8888)
        jupyter_host_ip = get_container_ip(container)
        bound_port = get_container_port_binding(container)

        if not bound_port:
            if HAS_STREAMLIT:
                st.error(f"⚠️ Container '{name}' exists but has no bound port.")
            return None

        if HAS_STREAMLIT:
            st.session_state["jupyter_port"] = bound_port

        # Start the container if it's not running
        if container.status != "running":
            container.start()
            if HAS_STREAMLIT:
                st.info(f"🔄 Started container '{name}'...")
            time.sleep(2)

        # Generate and display the URL
        url = f"http://{jupyter_host_ip}:{bound_port}/?token={token}"
        if HAS_STREAMLIT:
            st.success(f"✅ Jupyter Lab started!")
            st.markdown(f"🔗 [Open Jupyter Lab]({url})")
            st.code(url)

        return url

    except NotFound:
        # Container does not exist yet — create a new one
        port = find_free_port(8888)
        if HAS_STREAMLIT:
            st.session_state["jupyter_port"] = port
            host_mountpoint = os.path.abspath('../')
            st.session_state['jupyter_host_mountpoint'] = host_mountpoint
        else:
            host_mountpoint = os.path.abspath('../')

        # Create and start the container
        container = client.containers.run(
            "jupyter/base-notebook",
            name=name,
            ports={"8888/tcp": port},
            environment={"JUPYTER_TOKEN": token},
            volumes={
                host_mountpoint: {
                    "bind": "/home/jovyan/work",
                    "mode": "rw"
                }
            },
            detach=True,
            tty=True,
        )

        jupyter_host_ip = get_container_ip(container)
        if HAS_STREAMLIT:
            st.info(f"🚀 Starting new Jupyter container on port {port}...")
        time.sleep(2)

        # Generate and display the URL
        url = f"http://{jupyter_host_ip}:{port}/?token={token}"
        if HAS_STREAMLIT:
            st.success(f"✅ Jupyter Lab Started")
            st.markdown(f"🔗 [Open Jupyter Lab]({url})")
            st.code(url)

        return url

    except Exception as e:
        error_msg = f"Failed to start Jupyter container: {e}"
        if HAS_STREAMLIT:
            st.error(f"❌ {error_msg}")
        return None

def stop_jupyter_container():
    """
    Stop a running Jupyter container.
    
    Returns:
        bool: True if the container was stopped, False otherwise
    """
    if HAS_STREAMLIT:
        initialize_jupyter_session()
        name = st.session_state["jupyter_container_name"]
    else:
        name = "dsk-jupyter-instance"
        
    try:
        existing = client.containers.list(all=True, filters={"name": name})
        for container in existing:
            if container.name == name and container.status == "running":
                container.stop()
                return True
        return False
    except Exception as e:
        error_msg = f"Failed to stop Jupyter container: {e}"
        if HAS_STREAMLIT:
            st.error(f"❌ {error_msg}")
        return False