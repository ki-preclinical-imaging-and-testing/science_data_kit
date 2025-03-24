import streamlit as st
import docker
from utils.database import (
    get_neo4j_status, get_neo4j_hostname,
    start_neo4j_container, stop_neo4j_container
)

# Initialize Docker client
client = docker.from_env()

def database_sidebar():
    st.sidebar.header("📡 Server")
    # Check current container status
    status = get_neo4j_status()
    hostname = get_neo4j_hostname()  # Get hostname

    if status == "running":
        st.sidebar.write(f"""
    🔗\t    Browser: http://{hostname}:{st.session_state['http_port']}\n
     ⚡\t       Bolt: http://{hostname}:{st.session_state['bolt_port']}\n
    ✅\t    IP Addr:  `{hostname}`""")


        if st.sidebar.button("🛑 Stop DBMS"):
            stop_neo4j_container()
            st.sidebar.warning("Stopping server... Press again to update page.")
            status = "stopped"

    else:
        st.sidebar.warning("⚠️ Neo4j is not running.")
        if st.sidebar.button("🚀 Start DBMS"):
            start_neo4j_container()
            st.sidebar.success("Starting server... Press again to update page.")

    # Show latest logs if running
    if status == "running":
        st.sidebar.subheader("📜 Database Log")
        try:
            container = client.containers.get(st.session_state["container_name"])
            logs = container.logs(tail=10).decode("utf-8")
            st.sidebar.text_area("Logs", logs, height=150)
        except Exception as e:
            st.sidebar.error(f"Error fetching logs: {e}")
