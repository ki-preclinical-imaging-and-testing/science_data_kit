import streamlit as st
import docker
import os
import toml
from datetime import datetime
from pathlib import Path
from utils.database import (
    get_neo4j_status, get_neo4j_hostname,
    start_neo4j_container, stop_neo4j_container,
    fetch_databases, get_neo4j_session,
    export_graph_to_file, import_graph_from_file
)
from utils.jupyter_server import ( 
    initialize_jupyter_session,
    start_jupyter_container, stop_jupyter_container
)
from utils.neodash_server import (
    initialize_neodash_session,
    start_neodash_container, stop_neodash_container
)
from utils.database import manage_queries, extract_schema


# Initialize Docker client
client = docker.from_env()

def database_sidebar():

    # st.sidebar.header("📡 Server")
    # Check current container status
    status = get_neo4j_status()
    hostname = get_neo4j_hostname()  # Get hostname

    database_header = "📡 Neo4j Database"
    _exp_header = f"⚫ {database_header}"
    if status == "running":
        _exp_header = f"🟢 {database_header}"

    with st.expander(_exp_header, expanded=True):  # Set to expanded by default for better visibility

        if status == "running":
            st.write(f"""
        🔗\t    Browser: http://{hostname}:{st.session_state['http_port']}\n
         ⚡\t       Bolt: bolt://{hostname}:{st.session_state['bolt_port']}\n
        ✅\t    IP Addr:  `{hostname}`""")

            if st.button("🛑 Stop DBMS"):
                stop_neo4j_container()
                st.warning("Stopping server... Press again to update page.")
                status = "stopped"

        else:
            st.warning("⚠️ Neo4j is not running.")
            start_col, refresh_col = st.columns([3, 1])
            with start_col:
                if st.button("🚀 Start DBMS", use_container_width=True):
                    with st.spinner("Starting Neo4j container..."):
                        start_neo4j_container()
                    # Check if the container started successfully
                    new_status = get_neo4j_status()
                    if new_status == "running":
                        st.success("Neo4j server started successfully! Press the refresh button to update the page.")
                    else:
                        st.error("Failed to start Neo4j server. Check the logs below for details.")
            with refresh_col:
                if st.button("🔄", use_container_width=True):
                    st.rerun()

        # Show latest logs regardless of status
        st.subheader("📜 Database Log")
        try:
            # Try to get the container even if it's not running
            existing_containers = client.containers.list(all=True, filters={"name": st.session_state["container_name"]})
            if existing_containers:
                container = existing_containers[0]
                if container.status == "running":
                    logs = container.logs(tail=20).decode("utf-8")
                    st.text_area("Container Logs", logs, height=200)
                else:
                    # Show last logs even if container is stopped
                    try:
                        logs = container.logs(tail=20).decode("utf-8")
                        st.text_area("Last Container Logs (container is stopped)", logs, height=200)
                    except Exception:
                        st.info("No logs available for stopped container.")
            else:
                st.info("No Neo4j container found. Click 'Start DBMS' to create one.")
        except Exception as e:
            st.error(f"Error fetching logs: {e}")

    # Add Docker status information (moved outside the expander to avoid nesting)
    st.subheader("Docker Status Information")
    try:
        import subprocess
        docker_info = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if docker_info.returncode == 0:
            st.success("Docker daemon is running")
            st.code(docker_info.stdout, language="bash")
        else:
            st.error("Docker daemon is not running or not accessible")
            st.code(docker_info.stderr, language="bash")
    except Exception as e:
        st.error(f"Error checking Docker status: {e}")


def jupyter_sidebar():

    initialize_jupyter_session()
    container_name = st.session_state["jupyter_container_name"]
    port = st.session_state["jupyter_port"]
    token = st.session_state["jupyter_token"]
    containers = client.containers.list(all=True, filters={"name": container_name})
    status = containers[0].status if containers else "not found"

    # with st.sidebar.expander("👽 Jupyter Server", expanded=False):
    jupyter_header = "👽 Jupyter Lab"
    _exp_header = f"⚫ {jupyter_header}"
    if status == "running":
        _exp_header = f"🟢 {jupyter_header}"

    with st.expander(_exp_header, expanded=False):

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
    """
    Provides a UI for connecting to a Neo4j database and managing the connection.

    This function:
    1. Displays connection form fields (URI, username, password)
    2. Provides buttons to connect/disconnect
    3. Handles connection errors with helpful messages
    4. Displays database selection when connected
    """
    database_connection_header = "🔗 Neo4j Database Connection"
    _exp_header = f"⚫ {database_connection_header}"
    if st.session_state.connected:
        _exp_header = f"🟢 {database_connection_header}"

    with st.expander(_exp_header, expanded=False):
        # Connection Details in Sidebar
        uri = st.text_input("URI", f"{st.session_state['neo4j_uri']}")
        user = st.text_input("Username", st.session_state['neo4j_user'])
        password = st.text_input("Password", st.session_state['neo4j_password'], type="password")
        st.session_state["neo4j_uri"] = uri
        st.session_state["neo4j_user"] = user
        st.session_state["neo4j_password"] = password

        # Display connection help text
        if st.toggle("Show Connection Help", False):
            st.markdown("""
            ### Connection Troubleshooting

            - **URI Format**: Should be `bolt://hostname:port` (e.g., `bolt://localhost:7687`)
            - **Default Credentials**: Username: `neo4j`, Password: `neo4jiscool`
            - **Common Issues**:
                - Make sure the Neo4j database is running
                - Check that the port is correct and not blocked by a firewall
                - Verify that the username and password are correct
                - If using Docker, ensure the container is running

            You can start a local Neo4j database using the "Neo4j Database" section above.
            """)

        col1, col2 = st.columns(2)

        with col1:
            if not st.session_state.connected:
                if st.button("Connect", use_container_width=True):
                    with st.spinner("Connecting to Neo4j..."):
                        try:
                            # Validate URI format
                            if not uri.startswith("bolt://"):
                                st.error("URI must start with 'bolt://'")
                                st.info("Example: bolt://localhost:7687")
                            else:
                                session = get_neo4j_session(uri, user, password)
                                st.session_state.session = session
                                st.session_state.connected = True
                                st.success("Connected!")

                                # Save successful connection details to .db_config.yaml
                                try:
                                    from utils.database import update_db_config_auto
                                    # Extract hostname and port from URI
                                    import re
                                    match = re.match(r'bolt://([^:]+):(\d+)', uri)
                                    if match:
                                        hostname, port = match.groups()
                                        update_db_config_auto(hostname, port, user, password)
                                except Exception as e:
                                    st.warning(f"Could not save connection details: {e}")
                        except Exception as e:
                            error_message = str(e)
                            st.error(f"Connection failed: {error_message}")

                            # Provide more helpful error messages based on common issues
                            if "Connection refused" in error_message:
                                st.warning("The database server is not running or the port is incorrect.")
                                st.info("Try starting the Neo4j database using the 'Neo4j Database' section above.")
                            elif "authentication failure" in error_message.lower():
                                st.warning("Invalid username or password.")
                                st.info("Check your credentials and try again.")
                            elif "timed out" in error_message.lower():
                                st.warning("Connection timed out.")
                                st.info("Check that the hostname is correct and the server is running.")

                            st.session_state.connected = False
            else:
                if st.button("Disconnect", use_container_width=True):
                    with st.spinner("Disconnecting from Neo4j..."):
                        try:
                            # Close the session if it exists
                            if hasattr(st.session_state, 'session') and st.session_state.session:
                                st.session_state.session.close()
                            # Reset connection state
                            st.session_state.connected = False
                            st.session_state.selected_db = None
                            st.success("Disconnected!")
                        except Exception as e:
                            st.error(f"Error disconnecting: {e}")
                            st.info("The connection state has been reset, but there might be lingering connections.")
                            # Force reset connection state even if there was an error
                            st.session_state.connected = False
                            st.session_state.selected_db = None

        if st.session_state.connected:
            with st.spinner("Fetching available databases..."):
                databases = fetch_databases(st.session_state.session)
                selected_db = st.selectbox(
                    "Database",
                    databases,
                    index=databases.index(st.session_state.selected_db) if st.session_state.selected_db else 0
                )
                st.session_state.selected_db = selected_db

            # Database Management section
            st.divider()
            database_management_header = "💾 Neo4j Database Management"
            if st.session_state.connected:
                if st.toggle(f"**{database_management_header}**", value=False):

                    st.markdown("Save/Load Database via Connection")

                    # Create two columns for save and load functionality
                    save_col, load_col = st.columns(2)

                    with save_col:
                        st.subheader("Save Graph")

                        # Default save directory
                        default_save_dir = os.path.join(os.path.expanduser("~"), "graph_exports")
                        os.makedirs(default_save_dir, exist_ok=True)

                        # Generate default filename with timestamp
                        default_filename = f"neo4j_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"

                        # Save directory input
                        save_dir = st.text_input("Save Directory:", value=default_save_dir, key="db_save_dir")

                        # Filename input
                        if 'db_save_filename' not in st.session_state.keys():
                            st.session_state['db_save_filename'] = default_filename
                        save_filename = st.session_state['db_save_filename']
                        st.session_state['db_save_filename'] = st.text_input("Filename:", value=save_filename, key="db_save_filename_input")

                        # Combine directory and filename
                        save_path = os.path.join(save_dir, st.session_state['db_save_filename'])

                        # Save button
                        if st.button("Save Graph", use_container_width=True, key="save_graph_button"):
                            with st.spinner("Exporting graph..."):
                                success, message = export_graph_to_file(st.session_state.session, save_path)
                                if success:
                                    st.success(message)
                                    st.info(f"Graph saved to: {save_path}")
                                else:
                                    st.error(message)

                    with load_col:
                        st.subheader("Load Graph")

                        # File uploader for graph file
                        uploaded_file = st.file_uploader("Upload graph file:", type=["pkl"], key="graph_file_uploader")

                        # Or enter file path
                        load_path = st.text_input("Or enter file path:", key="graph_load_path")

                        # Warning about overwriting existing data
                        st.warning("⚠️ Loading a graph will clear the current database!")

                        # Confirmation checkbox
                        confirm_load = st.checkbox("I understand that this will overwrite the current database", key="confirm_load_checkbox")

                        # Load button
                        if st.button("Load Graph", use_container_width=True, key="load_graph_button"):
                            if not confirm_load:
                                st.error("Please confirm that you understand the consequences of loading a graph.")
                            elif uploaded_file:
                                # Save the uploaded file to a temporary location
                                temp_path = os.path.join(os.path.expanduser("~"), "temp_graph.pkl")
                                with open(temp_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())

                                # Import the graph
                                with st.spinner("Importing graph..."):
                                    success, message = import_graph_from_file(st.session_state.session, temp_path)
                                    if success:
                                        st.success(message)
                                    else:
                                        st.error(message)

                                # Clean up the temporary file
                                try:
                                    os.remove(temp_path)
                                except:
                                    pass
                            elif load_path:
                                # Import the graph from the specified path
                                with st.spinner("Importing graph..."):
                                    success, message = import_graph_from_file(st.session_state.session, load_path)
                                    if success:
                                        st.success(message)
                                    else:
                                        st.error(message)
                            else:
                                st.error("Please upload a file or enter a file path.")

def neodash_sidebar():
    initialize_neodash_session()
    container_name = st.session_state["neodash_container_name"]
    port = st.session_state["neodash_port"]
    containers = client.containers.list(all=True, filters={"name": container_name})
    status = containers[0].status if containers else "not found"

    neodash_header = "📊 NeoDash"
    _exp_header = f"⚫ {neodash_header}"
    if status == "running":
        _exp_header = f"🟢 {neodash_header}"

    with st.expander(_exp_header, expanded=False):
        if status == "running":
            st.success("NeoDash is running.")
            neodash_host_ip = containers[0].attrs["NetworkSettings"]["IPAddress"] or "localhost"
            st.session_state['neodash_host_ip'] = neodash_host_ip
            url = f"http://{neodash_host_ip}:{port}"
            st.markdown(f"[🔗 Open NeoDash in browser]({url})")
            if st.button("🛑 Stop NeoDash"):
                stop_neodash_container()
                st.warning("Stopping NeoDash...")
        else:
            st.warning("NeoDash is not running.")
            if st.button("🚀 Start NeoDash"):
                start_neodash_container()
                st.success("Starting NeoDash... click again in a moment to get the link.")

def schema_sample_widget():
    with st.sidebar.expander("🕸️ Schema Recall", expanded=False):
        # Initialize recall_query in session_state
        if "recall_query" not in st.session_state:
            st.session_state.recall_query = "MATCH (n)-[r]->(m)\nWITH DISTINCT n, r, m "

        # Callback function to handle query updates
        def update_recall_query():
            st.session_state.recall_query = st.session_state.recall_query_input

        st.text_area(
            "Recall Query",
            value=st.session_state.recall_query,
            key="recall_query_input",
            on_change=update_recall_query,
        )

        recall_query = manage_queries(st.session_state.recall_query)

        if st.button('Update'):
            st.session_state.recall_query = recall_query
            st.success(f"Updated.'")
            st.rerun()

    with st.sidebar.expander("🕷️ Schema Sampling", expanded=False):
        uri = st.session_state['neo4j_uri']
        user = st.session_state['neo4j_user']
        password = st.session_state['neo4j_password']

        st.text("Summarize schema of recall query")
        sample_mag = st.number_input("Order (1E??)", min_value=1, value=3, step=1)
        sample_size = 10**sample_mag
        st.text(f"Randomly sampling {sample_size} nodes")
        include_all = st.checkbox("Include All (No Limit)", value=False)
        st.session_state.cached_layout = st.radio("Schema Layout", ["Hierarchical", "Force-Directed"], index=1)
        st.session_state.cached_physics_enabled = st.checkbox("Elasticity", value=False)

        if st.button("Pull Schema"):
            session = get_neo4j_session(uri, user, password, database=st.session_state.selected_db)
            limit_clause = "" if include_all else f"LIMIT {sample_size}"
            with_clause = recall_query.strip() if recall_query.strip() else ""
#            query = f"""
#            {with_clause}
#            MATCH (n)-[r]->(m)
#            RETURN labels(n)[0] AS subjectLabel, type(r) AS predicateType, labels(m)[0] AS objectLabel
#            {limit_clause}
#            """

            query = f"""
            {with_clause}
            RETURN DISTINCT 
                labels(n)[0] AS subjectLabel, 
                [r.id, r.name] AS predicateType, 
                labels(m)[0] AS objectLabel
            {limit_clause}
            """
            with st.spinner("Sampling schema..."):
                results = session.run(query)
                results_list = [record.data() for record in results]
                st.success(f"Sampled {len(results_list)} rows from the schema!")
                triples, nodes = extract_schema(results_list)
                st.session_state.cached_triples = triples
                st.session_state.cached_labels = sorted(nodes)  # Ensure this is updated

def settings_sidebar():
    """
    Provides a UI for changing Streamlit configuration settings, including theme colors.

    This function:
    1. Reads the current settings from config.toml
    2. Displays color pickers for theme colors
    3. Updates config.toml when settings are changed
    4. Provides a button to reset to default colors
    """
    settings_header = "⚙️ App Settings"

    with st.expander(settings_header, expanded=False):
        st.subheader("Theme Settings")

        # Path to config.toml
        config_path = Path(".streamlit/config.toml")

        # Read current config
        try:
            config = toml.load(config_path)
        except Exception as e:
            st.error(f"Error loading config file: {e}")
            return

        # Get current theme settings with defaults
        theme = config.get("theme", {})
        primary_color = theme.get("primaryColor", "#4CAF50")
        background_color = theme.get("backgroundColor", "#1E3B2C")
        secondary_background_color = theme.get("secondaryBackgroundColor", "#004D40")
        text_color = theme.get("textColor", "#FFFFFF")

        # Display color pickers
        st.markdown("### Choose Theme Colors")

        new_primary_color = st.color_picker("Primary Color (buttons, links)", primary_color, key="primary_color")
        new_background_color = st.color_picker("Background Color", background_color, key="background_color")
        new_secondary_background_color = st.color_picker("Sidebar Color", secondary_background_color, key="secondary_background_color")
        new_text_color = st.color_picker("Text Color", text_color, key="text_color")

        # Check if any colors have changed
        colors_changed = (
            new_primary_color != primary_color or
            new_background_color != background_color or
            new_secondary_background_color != secondary_background_color or
            new_text_color != text_color
        )

        # Save button
        if colors_changed:
            st.info("Theme colors have changed. Click 'Save Changes' to apply.")

            if st.button("Save Changes", use_container_width=True):
                try:
                    # Update config
                    if "theme" not in config:
                        config["theme"] = {}

                    config["theme"]["primaryColor"] = new_primary_color
                    config["theme"]["backgroundColor"] = new_background_color
                    config["theme"]["secondaryBackgroundColor"] = new_secondary_background_color
                    config["theme"]["textColor"] = new_text_color

                    # Write to file
                    with open(config_path, "w") as f:
                        toml.dump(config, f)

                    st.success("Theme settings saved! Refresh the page to see changes.")
                except Exception as e:
                    st.error(f"Error saving config file: {e}")

        # Reset to defaults button
        if st.button("Reset to Defaults", use_container_width=True):
            try:
                # Set default colors
                if "theme" not in config:
                    config["theme"] = {}

                config["theme"]["primaryColor"] = "#4CAF50"
                config["theme"]["backgroundColor"] = "#1E3B2C"
                config["theme"]["secondaryBackgroundColor"] = "#004D40"
                config["theme"]["textColor"] = "#FFFFFF"

                # Write to file
                with open(config_path, "w") as f:
                    toml.dump(config, f)

                st.success("Theme settings reset to defaults! Refresh the page to see changes.")
            except Exception as e:
                st.error(f"Error resetting config file: {e}")

        # Server settings
        st.subheader("Server Settings")

        # Get current server settings with defaults
        server = config.get("server", {})
        max_message_size = server.get("maxMessageSize", 500)

        # Display server settings
        new_max_message_size = st.number_input(
            "Max Message Size (MB)", 
            min_value=100, 
            max_value=1000, 
            value=int(max_message_size),
            step=50,
            help="Maximum message size in MB. Increase this value if you encounter 'MessageSizeError'."
        )

        # Check if server settings have changed
        server_changed = new_max_message_size != max_message_size

        # Save server settings
        if server_changed:
            st.info("Server settings have changed. Click 'Save Server Settings' to apply.")

            if st.button("Save Server Settings", use_container_width=True):
                try:
                    # Update config
                    if "server" not in config:
                        config["server"] = {}

                    config["server"]["maxMessageSize"] = new_max_message_size

                    # Write to file
                    with open(config_path, "w") as f:
                        toml.dump(config, f)

                    st.success("Server settings saved! Restart the application to apply changes.")
                except Exception as e:
                    st.error(f"Error saving config file: {e}")

        # Information about config file
        if st.toggle("About Configuration", value=False):
            st.markdown("""
            ### Configuration Information

            The Streamlit configuration is stored in `app/.streamlit/config.toml`. This file contains settings for:

            - **Theme**: Colors and appearance of the application
            - **Server**: Performance and behavior settings

            Changes to these settings require a page refresh or application restart to take effect.

            For more information, see the [Streamlit configuration documentation](https://docs.streamlit.io/library/advanced-features/configuration).
            """)
