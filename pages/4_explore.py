import streamlit as st
import docker

# Initialize Docker client
client = docker.from_env()

# Initialize session state for the container
if "container_status" not in st.session_state:
    st.session_state["container_status"] = None
if "container_name" not in st.session_state:
    st.session_state["container_name"] = "neo4j-instance"

container_name = st.session_state["container_name"]

def start_neo4j_container():
    """Start the Neo4j container."""
    try:
        # Check if the container already exists
        existing_containers = client.containers.list(all=True, filters={"name": container_name})
        if existing_containers:
            container = existing_containers[0]
            if container.status != "running":
                container.start()
            st.session_state["container_status"] = "running"
            st.success(f"Neo4j container '{container_name}' started successfully.")
        else:
            # Start a new container
            container = client.containers.run(
                "neo4j:5.8",
                name=container_name,
                ports={"7474/tcp": 7474, "7687/tcp": 7687},
                environment={
                    "NEO4J_AUTH": "neo4j/your_secure_password",
                },
                detach=True,
                tty=True,
            )
            st.session_state["container_status"] = "running"
            st.success(f"New Neo4j container '{container_name}' started successfully.")
    except docker.errors.DockerException as e:
        st.error(f"Error starting Neo4j container: {e}")


def stop_neo4j_container():
    """Stop the Neo4j container."""
    try:
        # Check if the container exists
        existing_containers = client.containers.list(all=True, filters={"name": container_name})
        if existing_containers:
            container = existing_containers[0]
            if container.status == "running":
                container.stop()
                st.session_state["container_status"] = "stopped"
                st.success(f"Neo4j container '{container_name}' stopped successfully.")
            else:
                st.info(f"Neo4j container '{container_name}' is not running.")
        else:
            st.warning(f"No container named '{container_name}' found.")
    except docker.errors.DockerException as e:
        st.error(f"Error stopping Neo4j container: {e}")


# Check the current status of the container
try:
    existing_containers = client.containers.list(all=True, filters={"name": container_name})
    if existing_containers:
        container = existing_containers[0]
        st.session_state["container_status"] = container.status
except docker.errors.DockerException as e:
    st.error(f"Error checking container status: {e}")

# Display container controls
st.title("Neo4j Container Management")

if st.session_state["container_status"] == "running":
    st.success(f"Neo4j container '{container_name}' is running.")
    if st.button("Stop Container"):
        stop_neo4j_container()
else:
    st.info(f"Neo4j container '{container_name}' is not running.")
    if st.button("Start Container"):
        start_neo4j_container()

# Show container logs (optional)
if st.session_state["container_status"] == "running":
    #st.subheader("Container Logs")
    try:
        logs = container.logs(tail=10).decode("utf-8")
        st.text_area("Container Logs", logs, height=200)
    except Exception as e:
        st.error(f"Error fetching logs: {e}")

