"""
Sidebar Component for Science Data Kit

This module provides the sidebar component for the Science Data Kit application.
It includes functions for rendering the sidebar and its various sections.
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path

# Import database manager
from science_data_kit.core.db.db_manager import db_manager

# Check if Microsoft Graph API is available
try:
    from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
    MSGRAPH_AVAILABLE = True
except ImportError:
    MSGRAPH_AVAILABLE = False

def render_sidebar_header() -> None:
    """Render the sidebar header with logo and title."""
    st.sidebar.image("https://raw.githubusercontent.com/NIEHS/science_data_kit/main/docs/images/sdk_logo.png", width=200)
    st.sidebar.title("Science Data Kit")

def render_sidebar_section(title: str, is_connected: bool = False) -> bool:
    """
    Render an expandable sidebar section with status indicator.

    Args:
        title: The title of the section.
        is_connected: Whether the section is connected/active.

    Returns:
        bool: Whether the section is expanded.
    """
    # Create a unique key for this section
    key = f"sidebar_{title.lower().replace(' ', '_')}"

    # Status indicator
    status = "🟢" if is_connected else "⚫"

    # Create the expandable section
    expanded = st.session_state.get(f"{key}_expanded", False)

    # Create the header with status indicator
    if st.sidebar.button(f"{status} {title}", key=f"{key}_button"):
        expanded = not expanded
        st.session_state[f"{key}_expanded"] = expanded

    # Add a divider
    st.sidebar.markdown("---")

    return expanded

def render_database_sidebar(
    on_connect: Optional[Callable] = None,
    on_disconnect: Optional[Callable] = None
) -> None:
    """
    Render the database connection section in the sidebar.

    Args:
        on_connect: Optional callback function to call when the connect button is clicked.
        on_disconnect: Optional callback function to call when the disconnect button is clicked.
    """
    # Initialize connections in session state if not present
    if "db_connections" not in st.session_state:
        st.session_state["db_connections"] = {}

    # Initialize active connection in session state if not present
    if "active_connection" not in st.session_state:
        st.session_state["active_connection"] = None

    # Sync connection statuses with backend state
    def sync_connection_statuses():
        """
        Synchronize connection statuses in session state with backend state.

        This ensures that the UI accurately reflects the actual connection status.
        """
        if "db_connections" not in st.session_state:
            return

        # Get all connection names from the backend
        backend_connections = set(db_manager.get_connection_names())

        # Update connection statuses in session state
        for name, details in st.session_state["db_connections"].items():
            # Check if the connection exists in the backend
            if name in backend_connections:
                # Check if the connection is actually connected
                is_connected = db_manager.is_connected(name)
                details["connected"] = is_connected
            else:
                # Connection doesn't exist in the backend
                details["connected"] = False

    # Sync connection statuses
    sync_connection_statuses()

    # Check if any connection is connected (not just the active one)
    is_connected = False
    for conn_details in st.session_state.get("db_connections", {}).values():
        if conn_details.get("connected", False):
            is_connected = True
            break

    # Render the section header with status indicator
    expanded = render_sidebar_section("Database Connections", is_connected)

    # Only show the content if the section is expanded
    if expanded:
        # Connection status
        if is_connected:
            # Count how many connections are connected
            connected_count = 0
            connected_names = []
            for name, conn_details in st.session_state.get("db_connections", {}).items():
                if conn_details.get("connected", False):
                    connected_count += 1
                    connected_names.append(name)

            # Show active connection and total connected count
            active_conn = st.session_state["active_connection"]
            if connected_count == 1:
                st.sidebar.success(f"Connected to {active_conn}")
            else:
                st.sidebar.success(f"Connected to {connected_count} databases. Active: {active_conn}")
                # Show list of connected databases
                st.sidebar.info(f"Connected databases: {', '.join(connected_names)}")
        else:
            st.sidebar.warning("Not connected to any database")

        # Connection selector
        connections = list(st.session_state["db_connections"].keys())
        if connections:
            selected_connection = st.sidebar.selectbox(
                "Saved Connections",
                ["New Connection"] + connections,
                index=0
            )
        else:
            selected_connection = "New Connection"

        # Connection form
        with st.sidebar.form("neo4j_connection_form"):
            # Connection name input (only for new connections)
            if selected_connection == "New Connection":
                connection_name = st.text_input(
                    "Connection Name",
                    value="",
                    placeholder="Enter a name for this connection"
                )
            else:
                connection_name = selected_connection

            # Load connection details if an existing connection is selected
            if selected_connection != "New Connection":
                conn_details = st.session_state["db_connections"][selected_connection]
                default_uri = conn_details.get("uri", "bolt://localhost:7687")
                default_user = conn_details.get("user", "neo4j")
                default_password = conn_details.get("password", "password")
                default_database = conn_details.get("database", "neo4j")
            else:
                default_uri = "bolt://localhost:7687"
                default_user = "neo4j"
                default_password = "password"
                default_database = "neo4j"

            # URI input
            uri = st.text_input(
                "Neo4j URI",
                value=default_uri,
                disabled=is_connected and selected_connection == st.session_state.get("active_connection")
            )

            # Username input
            username = st.text_input(
                "Username",
                value=default_user,
                disabled=is_connected and selected_connection == st.session_state.get("active_connection")
            )

            # Password input
            password = st.text_input(
                "Password",
                value=default_password,
                type="password",
                disabled=is_connected and selected_connection == st.session_state.get("active_connection")
            )

            # Database input
            database = st.text_input(
                "Database",
                value=default_database,
                disabled=is_connected and selected_connection == st.session_state.get("active_connection")
            )

            # Form buttons
            col1, col2 = st.columns(2)

            with col1:
                # Connect button
                connect_disabled = (is_connected and selected_connection == st.session_state.get("active_connection"))

                if st.form_submit_button("Connect", disabled=connect_disabled):
                    # For new connections, save the connection details
                    if selected_connection == "New Connection":
                        # Generate a default connection name if none is provided
                        if not connection_name:
                            connection_name = f"Connection {len(st.session_state['db_connections']) + 1}"

                        # Check if this connection name already exists
                        if connection_name in st.session_state["db_connections"]:
                            # Append a number to make it unique
                            base_name = connection_name
                            counter = 1
                            while f"{base_name} ({counter})" in st.session_state["db_connections"]:
                                counter += 1
                            connection_name = f"{base_name} ({counter})"

                        st.session_state["db_connections"][connection_name] = {
                            "uri": uri,
                            "user": username,
                            "password": password,
                            "database": database
                        }

                    # Update the connection details in case they were modified
                    if selected_connection != "New Connection":
                        st.session_state["db_connections"][selected_connection] = {
                            "uri": uri,
                            "user": username,
                            "password": password,
                            "database": database
                        }

                    # Set the active connection
                    conn_name = connection_name if selected_connection == "New Connection" else selected_connection

                    if on_connect:
                        on_connect(uri, username, password, database, conn_name)

            with col2:
                # Disconnect button
                if st.form_submit_button("Disconnect", disabled=not is_connected):
                    if on_disconnect:
                        on_disconnect()

        # Delete connection button (outside the form)
        if selected_connection != "New Connection":
            if st.sidebar.button("Delete Connection", key="delete_connection"):
                # Don't allow deleting an active connection
                if selected_connection == st.session_state.get("active_connection"):
                    st.sidebar.error("Cannot delete an active connection. Disconnect first.")
                else:
                    del st.session_state["db_connections"][selected_connection]
                    st.rerun()

def render_neo4j_container_sidebar(
    on_start: Optional[Callable] = None,
    on_stop: Optional[Callable] = None
) -> None:
    """
    Render the Neo4j container management section in the sidebar.

    Args:
        on_start: Optional callback function to call when the start button is clicked.
        on_stop: Optional callback function to call when the stop button is clicked.
    """
    # Check if container is running
    container_status = st.session_state.get("container_status", "unknown")
    is_running = container_status == "running"

    # Render the section header with status indicator
    expanded = render_sidebar_section("Neo4j Container", is_running)

    # Only show the content if the section is expanded
    if expanded:
        # Container status
        if container_status == "running":
            st.sidebar.success("Neo4j container is running")
        elif container_status == "stopped":
            st.sidebar.warning("Neo4j container is stopped")
        elif container_status == "not found":
            st.sidebar.error("Neo4j container not found")
        else:
            st.sidebar.info("Neo4j container status unknown")

        # Container management form
        with st.sidebar.form("neo4j_container_form"):
            # Version selection
            version = st.selectbox(
                "Neo4j Version",
                ["latest", "4.4", "5.0", "5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8", "5.9"],
                index=0,
                disabled=container_status == "running"
            )

            # Username input
            username = st.text_input(
                "Username",
                value=st.session_state.get("username", "neo4j"),
                disabled=st.session_state.get("credentials_locked", False)
            )

            # Password input
            password = st.text_input(
                "Password",
                value=st.session_state.get("password", "password"),
                type="password",
                disabled=st.session_state.get("credentials_locked", False)
            )

            # Start/Stop button
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Start Container", disabled=container_status == "running"):
                    # Update session state
                    st.session_state["neo4j_version"] = version
                    st.session_state["username"] = username
                    st.session_state["password"] = password

                    if on_start:
                        on_start()

            with col2:
                if st.form_submit_button("Stop Container", disabled=container_status != "running"):
                    if on_stop:
                        on_stop()

def render_jupyter_sidebar(
    on_start: Optional[Callable] = None,
    on_stop: Optional[Callable] = None
) -> None:
    """
    Render the Jupyter management section in the sidebar.

    Args:
        on_start: Optional callback function to call when the start button is clicked.
        on_stop: Optional callback function to call when the stop button is clicked.
    """
    # Import here to avoid circular imports
    from science_data_kit.core.utils.jupyter_utils import get_jupyter_container_status

    # Get container name from session state
    container_name = st.session_state.get("jupyter_container_name", "dsk-jupyter-instance")

    # Check if Jupyter is running by verifying container status
    jupyter_url = st.session_state.get("jupyter_url", "")
    jupyter_token = st.session_state.get("jupyter_token", "")
    container_exists, container_status = get_jupyter_container_status(container_name)

    # Check if the service is actually accessible
    is_accessible = False
    if jupyter_url and jupyter_token:
        try:
            import requests
            # Try to access the Jupyter server with a timeout
            response = requests.get(jupyter_url, timeout=2)
            is_accessible = response.status_code == 200
        except:
            is_accessible = False

    # Only consider it running if:
    # 1. The URL and token are set
    # 2. The container exists and is running
    # 3. The service is accessible at the URL (optional check)
    is_running = bool(jupyter_url) and bool(jupyter_token) and container_exists and container_status == "running"

    # If we have a URL but the container isn't running, clear the token
    if jupyter_token and (not container_exists or container_status != "running"):
        st.session_state["jupyter_token"] = ""
        is_running = False

    # Render the section header with status indicator
    expanded = render_sidebar_section("Jupyter Lab", is_running)

    # Only show the content if the section is expanded
    if expanded:
        if is_running:
            st.sidebar.success("Jupyter Lab is running")
            st.sidebar.markdown(f"[Open Jupyter Lab]({jupyter_url})")

            # Show the mode
            jupyter_mode = st.session_state.get("jupyter_mode", "Single-user")
            st.sidebar.info(f"Mode: {jupyter_mode}")
        else:
            if container_exists and container_status == "running" and not is_accessible:
                st.sidebar.warning("Jupyter Lab container is running but service is not accessible")
            else:
                st.sidebar.warning("Jupyter Lab is not running")

        # Jupyter management form
        with st.sidebar.form("jupyter_form"):
            # Mode selection
            mode = st.radio(
                "Mode",
                ["Single-user", "Multi-user"],
                index=0
            )

            # Port input
            port = st.number_input(
                "Port",
                min_value=1024,
                max_value=65535,
                value=8888
            )

            # Start/Stop button
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Start Jupyter", disabled=is_running):
                    if on_start:
                        on_start(port, mode)

            with col2:
                if st.form_submit_button("Stop Jupyter", disabled=not is_running):
                    if on_stop:
                        on_stop()

def render_neodash_sidebar(
    on_start: Optional[Callable] = None,
    on_stop: Optional[Callable] = None
) -> None:
    """
    Render the NeoDash management section in the sidebar.

    Args:
        on_start: Optional callback function to call when the start button is clicked.
        on_stop: Optional callback function to call when the stop button is clicked.
    """
    # Import here to avoid circular imports
    from science_data_kit.core.utils.neodash_utils import get_neodash_container_status, is_neodash_accessible

    # Check if NeoDash is running by verifying container status and accessibility
    neodash_url = st.session_state.get("neodash_url", "")
    container_exists, container_status = get_neodash_container_status()

    # Check if the service is actually accessible at the URL
    is_accessible = is_neodash_accessible(neodash_url)

    # Only consider it running if:
    # 1. The URL is set
    # 2. The container exists and is running
    # 3. The service is accessible at the URL
    is_running = neodash_url != "" and container_exists and container_status == "running" and is_accessible

    # If we have a URL but either the container isn't running or the service isn't accessible, clear the URL
    if neodash_url and (not container_exists or container_status != "running" or not is_accessible):
        st.session_state["neodash_url"] = ""
        is_running = False

    # Render the section header with status indicator
    expanded = render_sidebar_section("NeoDash", is_running)

    # Only show the content if the section is expanded
    if expanded:
        if is_running:
            st.sidebar.success("NeoDash is running")
            st.sidebar.markdown(f"[Open NeoDash]({neodash_url})")
        else:
            st.sidebar.warning("NeoDash is not running")

        # NeoDash management form
        with st.sidebar.form("neodash_form"):
            # Environment selection
            environment = st.radio(
                "Environment",
                ["Development", "Production"],
                index=0
            )

            # Port input
            port = st.number_input(
                "Port",
                min_value=1024,
                max_value=65535,
                value=5005
            )

            # Start/Stop button
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Start NeoDash", disabled=is_running):
                    if on_start:
                        on_start(port, environment)

            with col2:
                if st.form_submit_button("Stop NeoDash", disabled=not is_running):
                    if on_stop:
                        on_stop()

def render_msgraph_sidebar(
    on_connect: Optional[Callable] = None,
    on_disconnect: Optional[Callable] = None
) -> None:
    """
    Render the Microsoft Graph API section in the sidebar.

    Args:
        on_connect: Optional callback function to call when the connect button is clicked.
        on_disconnect: Optional callback function to call when the disconnect button is clicked.
    """
    if not MSGRAPH_AVAILABLE:
        return

    # Check if connected
    is_connected = "msgraph_connection_manager" in st.session_state and st.session_state["msgraph_connection_manager"].connected

    # Render the section header with status indicator
    expanded = render_sidebar_section("Microsoft Graph API", is_connected)

    # Only show the content if the section is expanded
    if expanded:
        # Connection status
        if is_connected:
            st.sidebar.success("Connected to Microsoft Graph API")

            # Display current user information
            try:
                me = st.session_state["msgraph_connection_manager"].get_me()
                st.sidebar.write(f"User: {me.get('displayName', 'N/A')}")
                st.sidebar.write(f"Email: {me.get('mail', 'N/A')}")
            except Exception:
                pass

            # Disconnect button
            if st.sidebar.button("Disconnect from Microsoft Graph API"):
                if on_disconnect:
                    on_disconnect()
                else:
                    # Remove connection manager from session state
                    del st.session_state["msgraph_connection_manager"]
                    if "msgraph_adapter" in st.session_state:
                        del st.session_state["msgraph_adapter"]
                    st.sidebar.success("Disconnected from Microsoft Graph API")
                    st.rerun()
        else:
            st.sidebar.warning("Not connected to Microsoft Graph API")

            # Connect button
            if st.sidebar.button("Connect to Microsoft Graph API"):
                if on_connect:
                    on_connect()
                else:
                    # Redirect to Microsoft Graph API connection page
                    st.experimental_set_query_params(page="msgraph_connect")
                    st.rerun()

        # Links to Microsoft Graph API pages
        st.sidebar.markdown("### Microsoft Graph API Pages")
        st.sidebar.markdown("[Connect](/msgraph_connect)")
        st.sidebar.markdown("[Explorer](/msgraph_explore)")


def render_settings_sidebar() -> None:
    """Render the settings section in the sidebar."""
    # Render the section header with status indicator
    expanded = render_sidebar_section("Settings", False)

    # Only show the content if the section is expanded
    if expanded:
        # Theme selection
        theme = st.sidebar.selectbox(
            "Theme",
            ["Light", "Dark"],
            index=0
        )

        # Language selection
        language = st.sidebar.selectbox(
            "Language",
            ["English", "Spanish", "French", "German"],
            index=0
        )

        # Save settings button
        if st.sidebar.button("Save Settings"):
            st.sidebar.success("Settings saved")

def render_sidebar(
    sections: Optional[List[str]] = None,
    callbacks: Optional[Dict[str, Callable]] = None
) -> None:
    """
    Render the sidebar with the specified sections.

    Args:
        sections: Optional list of section names to include in the sidebar.
            If None, all sections will be included.
        callbacks: Optional dictionary mapping callback names to callback functions.
    """
    # Default sections
    all_sections = ["header", "database", "neo4j", "jupyter", "neodash", "msgraph", "settings"]

    # Use specified sections or all sections
    sections_to_render = sections or all_sections

    # Initialize callbacks
    callbacks = callbacks or {}

    # Render sections
    for section in sections_to_render:
        if section == "header":
            render_sidebar_header()
        elif section == "database":
            render_database_sidebar(
                on_connect=callbacks.get("on_database_connect"),
                on_disconnect=callbacks.get("on_database_disconnect")
            )
        elif section == "neo4j":
            render_neo4j_container_sidebar(
                on_start=callbacks.get("on_neo4j_start"),
                on_stop=callbacks.get("on_neo4j_stop")
            )
        elif section == "jupyter":
            render_jupyter_sidebar(
                on_start=callbacks.get("on_jupyter_start"),
                on_stop=callbacks.get("on_jupyter_stop")
            )
        elif section == "neodash":
            render_neodash_sidebar(
                on_start=callbacks.get("on_neodash_start"),
                on_stop=callbacks.get("on_neodash_stop")
            )
        elif section == "msgraph":
            render_msgraph_sidebar(
                on_connect=callbacks.get("on_msgraph_connect"),
                on_disconnect=callbacks.get("on_msgraph_disconnect")
            )
        elif section == "settings":
            render_settings_sidebar()
