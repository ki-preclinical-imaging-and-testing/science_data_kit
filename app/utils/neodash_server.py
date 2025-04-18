import time
import socket
import docker
import streamlit as st
from docker.errors import NotFound
import os

client = docker.from_env()

def initialize_neodash_session():
    if "neodash_container_name" not in st.session_state:
        st.session_state["neodash_container_name"] = "dsk-neodash-instance"
    if "neodash_port" not in st.session_state:
        st.session_state["neodash_port"] = 5005
    if "neodash_connected" not in st.session_state:
        st.session_state["neodash_connected"] = False

# Initialize session state variables when the module is imported
initialize_neodash_session()

def is_port_available(port, host="0.0.0.0"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False

def find_free_port(start=5005):
    port = start
    while not is_port_available(port):
        port += 1
    return port

def get_container_port_binding(container, internal_port="5005/tcp"):
    try:
        return int(container.attrs["HostConfig"]["PortBindings"][internal_port][0]["HostPort"])
    except (KeyError, IndexError, TypeError):
        return None

def get_container_ip(container):
    st.session_state['neodash_host_ip'] = container.attrs["NetworkSettings"]["IPAddress"] or "localhost"
    return st.session_state['neodash_host_ip']

def start_neodash_container():
    initialize_neodash_session()
    name = st.session_state["neodash_container_name"]
    
    try:
        # Check if container already exists
        container = client.containers.get(name)
        
        # Get the bound port
        bound_port = get_container_port_binding(container)
        if not bound_port:
            st.error(f"⚠️ Container '{name}' exists but has no bound port.")
            return
        
        st.session_state["neodash_port"] = bound_port
        
        # Start container if it's not running
        if container.status != "running":
            container.start()
            st.info(f"🔄 Started container '{name}'...")
            time.sleep(2)
        
        # Get container IP and create URL
        neodash_host_ip = get_container_ip(container)
        url = f"http://{neodash_host_ip}:{bound_port}"
        
        st.success(f"✅ NeoDash started!")
        st.markdown(f"🔗 NeoDash ({url})")
        
        # Set connected state
        st.session_state["neodash_connected"] = True
        
        return url
        
    except NotFound:
        # Container does not exist yet - create it
        port = find_free_port(5005)
        st.session_state["neodash_port"] = port
        
        # Get Neo4j connection details from session state
        neo4j_uri = st.session_state.get("neo4j_uri", "bolt://localhost:7687")
        neo4j_user = st.session_state.get("neo4j_user", "neo4j")
        neo4j_password = st.session_state.get("neo4j_password", "neo4jiscool")
        
        # Create and start the container
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
        st.info(f"🚀 Starting new NeoDash container on port {port}...")
        time.sleep(2)
        
        url = f"http://{neodash_host_ip}:{port}"
        st.success(f"✅ NeoDash Started")
        st.markdown(f"🔗 NeoDash ({url})")
        
        # Set connected state
        st.session_state["neodash_connected"] = True
        
        return url
        
    except Exception as e:
        st.error(f"❌ Failed to start NeoDash container: {e}")
        return None

def stop_neodash_container():
    initialize_neodash_session()
    name = st.session_state["neodash_container_name"]
    
    try:
        container = client.containers.get(name)
        if container.status == "running":
            container.stop()
            st.session_state["neodash_connected"] = False
            return True
    except Exception as e:
        st.error(f"Error stopping NeoDash container: {e}")
        return False