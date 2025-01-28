import streamlit as st
import docker
import socket

# Initialize Docker client
client = docker.from_env()

# Initialize session state for the container
if "container_status" not in st.session_state:
    st.session_state["container_status"] = None
if "container_name" not in st.session_state:
    st.session_state["container_name"] = "neo4j-instance"
if "http_port" not in st.session_state:
    st.session_state["http_port"] = None
if "bolt_port" not in st.session_state:
    st.session_state["bolt_port"] = None

container_name = st.session_state["container_name"]

def find_free_port(start_port):
    """Finds a free port starting from `start_port`."""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:  # Port is free
                return port
        port += 1  # Increment port and try again

def start_neo4j_container():
    """Start the Neo4j container."""
    try:
        # Find free ports for HTTP and Bolt
        st.session_state["http_port"] = find_free_port(7474)
        st.session_state["bolt_port"] = find_free_port(7687)

        # Check if the container already exists
        existing_containers = client.containers.list(all=True, filters={"name": container_name})
        for container in existing_containers:
            if container.name == container_name:
                if container.status != "running":
                    container.start()
                st.session_state["container_status"] = "running"
                st.success(f"Neo4j container '{container_name}' started successfully on ports {st.session_state['http_port']} (HTTP) and {st.session_state['bolt_port']} (Bolt).")
                return

        # Start a new container with dynamically assigned ports
        container = client.containers.run(
            "neo4j:latest",
            name=container_name,
            ports={
                "7474/tcp": st.session_state["http_port"],
                "7687/tcp": st.session_state["bolt_port"]
            },
            environment={
                "NEO4J_AUTH": "neo4j/neo4jiscool",
            },
            detach=True,
            tty=True,
        )
        st.session_state["container_status"] = "running"
        st.success(f"New Neo4j container '{container_name}' started successfully on ports {st.session_state['http_port']} (HTTP) and {st.session_state['bolt_port']} (Bolt).")
    except docker.errors.DockerException as e:
        st.error(f"Error starting Neo4j container: {e}")

def stop_neo4j_container():
    """Stop the Neo4j container."""
    try:
        # Check if the container exists
        existing_containers = client.containers.list(all=True, filters={"name": container_name})
        for container in existing_containers:
            if container.name == container_name:
                if container.status == "running":
                    container.stop()
                    st.session_state["container_status"] = "stopped"
                    st.session_state["http_port"] = None
                    st.session_state["bolt_port"] = None
                    st.success(f"Neo4j container '{container_name}' stopped successfully.")
                    return
                else:
                    st.info(f"Neo4j container '{container_name}' is not running.")
                    return
        st.warning(f"No container named '{container_name}' found.")
    except docker.errors.DockerException as e:
        st.error(f"Error stopping Neo4j container: {e}")

# Check the current status of the container
try:
    existing_containers = client.containers.list(all=True, filters={"name": container_name})
    for container in existing_containers:
        if container.name == container_name:
            st.session_state["container_status"] = container.status
except docker.errors.DockerException as e:
    st.error(f"Error checking container status: {e}")

# Display container controls
st.title("Neo4j Container Management")

if st.session_state["container_status"] == "running":
    st.success(f"Neo4j container '{container_name}' is running on ports {st.session_state['http_port']} (HTTP) and {st.session_state['bolt_port']} (Bolt).")
    if st.button("Stop Container"):
        stop_neo4j_container()
else:
    st.info(f"Neo4j container '{container_name}' is not running.")
    if st.button("Start Container"):
        start_neo4j_container()

# Show container logs (optional)
if st.session_state["container_status"] == "running":
    st.subheader("Container Logs")
    try:
        logs = container.logs(tail=10).decode("utf-8")
        st.text_area("Container Logs", logs, height=200)
    except Exception as e:
        st.error(f"Error fetching logs: {e}")

