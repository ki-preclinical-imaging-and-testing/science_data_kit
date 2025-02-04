import streamlit as st
import socket
import docker

st.set_page_config(
    page_title="Science Data Toolkit",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://adam-patch.mit.edu',
        'Report a bug': "https://adam-patch.mit.edu",
        'About': "# Science Data for Data Science!"
    }

)

st.title("Get started...")
st.markdown(
    """
    *... simplifying FAIR+ data in your lab.*

    ### What is this?
    **Science Data Toolkit** helps you index, curate, and integrate multimodal research data. 

    ### Science Data Toolkit helps you...
    |  |  |
    | ---: | --- |
    |  **start** | *using this toolkit* |
    |  **index** | *filetree metadata* |
    |  **resolve** | *data entities* |
    |  **relate** | *entities via schema* |
    |  **explore** | *data in context* |
    |  **integrate** | *other workflows* |
    |  **ground** | *large language models* |
    |  **learn** | *more about this toolkit* |

    ## FAIR+ Data
    The FAIR(+) Data Principles have been established (and appended). 

    Let's follow them. We can have *nice things*.

    Science data that is...

    - **F**indable
    - **A**ccessible
    - **I**nteroperable
    - **R**eusable
    - **+** (Computable)

    ... is *nice things* science data. Let's have it!
    """

    # TODO: Make an infographic for this description
    #### Getting Started
    #Using the navigation menu on the left:
    #1. Go to **Scan** to analyze your filesystem.
    #2. Visit **Edit** to review metadata.
    #3. Proceed to **Curate** for organizing datasets.
    #4. Explore schema and data relationships under **Explore**.
    #5. Finally, use **Integrate** to export or connect your work.
    #For **Learn** for detailed documentation about each step!
)
#st.image("static/logo.png", width=300)  # Replace with your logo path if needed


st.sidebar.success("Welcome!")

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
