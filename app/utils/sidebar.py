import streamlit as st
import docker
from utils.database import (
    get_neo4j_status, get_neo4j_hostname,
    start_neo4j_container, stop_neo4j_container,
    fetch_databases, get_neo4j_session
)
from utils.jupyter_server import ( 
    initialize_jupyter_session,
    start_jupyter_container, stop_jupyter_container
)


# Initialize Docker client
client = docker.from_env()

def database_sidebar():

    # st.sidebar.header("📡 Server")
    # Check current container status
    status = get_neo4j_status()
    hostname = get_neo4j_hostname()  # Get hostname

    # with st.sidebar.expander("📡 DB Server", expanded=False):
    with st.expander("📡 DB Server", expanded=True):

        if status == "running":
            st.write(f"""
        🔗\t    Browser: http://{hostname}:{st.session_state['http_port']}\n
         ⚡\t       Bolt: http://{hostname}:{st.session_state['bolt_port']}\n
        ✅\t    IP Addr:  `{hostname}`""")
    
    
            if st.button("🛑 Stop DBMS"):
                stop_neo4j_container()
                st.warning("Stopping server... Press again to update page.")
                status = "stopped"
    
        else:
            st.warning("⚠️ Neo4j is not running.")
            if st.button("🚀 Start DBMS"):
                start_neo4j_container()
                st.success("Starting server... Press again to update page.")
    
        # Show latest logs if running
        if status == "running":
            st.subheader("📜 Database Log")
            try:
                container = client.containers.get(st.session_state["container_name"])
                logs = container.logs(tail=10).decode("utf-8")
                st.text_area("Logs", logs, height=150)
            except Exception as e:
                st.error(f"Error fetching logs: {e}")

def jupyter_sidebar():
    
    initialize_jupyter_session()
    container_name = st.session_state["jupyter_container_name"]
    port = st.session_state["jupyter_port"]
    token = st.session_state["jupyter_token"]

    # with st.sidebar.expander("👽 Jupyter Server", expanded=False):
    with st.expander("👽 Jupyter Server", expanded=False):
        containers = client.containers.list(all=True, filters={"name": container_name})
        status = containers[0].status if containers else "not found"
        if status == "running":
            st.success("Jupyter is running.")
            jupyter_host_ip = containers[0].attrs["NetworkSettings"]["IPAddress"] or "localhost"
            st.session_state['jupyter_host_ip'] = jupyter_host_ip
            url = f"http://{jupyter_host_ip}:{port}/?token={token}"
            st.markdown(f"[🔗 Open Jupyter in browser]({url})")
            if st.button("🛑 Stop Jupyter"):
                stop_jupyter_container()
                st.warning("Stopping Jupyter...")
        else:
            st.warning("Jupyter is not running.")
            if st.button("🚀 Start Jupyter"):
                start_jupyter_container()
                st.success("Starting Jupyter... click again in a moment to get the link.")

def neo4j_connector():
    with st.expander("🔗 DB Link", expanded=False):
        # Connection Details in Sidebar
        uri = st.text_input("URI", f"{st.session_state['neo4j_uri']}")
        user = st.text_input("Username", st.session_state['neo4j_user'])
        password = st.text_input("Password", st.session_state['neo4j_password'], type="password")
        st.session_state["neo4j_uri"] = uri
        st.session_state["neo4j_user"] = user
        st.session_state["neo4j_password"] = password

        if st.button("Connect"):
            with st.spinner("Connecting to Neo4j..."):
                try:
                    session = get_neo4j_session(uri, user, password)
                    st.session_state.session = session
                    st.session_state.connected = True
                    st.success("Connected!")
                except Exception as e:
                    st.sidebar.error(f"Connection failed: {e}")
                    st.session_state.connected = False
        if st.session_state.connected:
            with st.spinner("Fetching available databases..."):
                databases = fetch_databases(st.session_state.session)
                selected_db = st.selectbox(
                    "Database",
                    databases,
                    index=databases.index(st.session_state.selected_db) if st.session_state.selected_db else 0
                )
                st.session_state.selected_db = selected_db

