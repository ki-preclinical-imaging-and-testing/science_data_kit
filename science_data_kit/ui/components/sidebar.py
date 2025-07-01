"""
Sidebar Component for Science Data Kit

This module provides the sidebar component for the Science Data Kit application.
It includes functions for rendering the sidebar and its various sections.
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path

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
    # Check if connected
    is_connected = st.session_state.get("connected", False)

    # Render the section header with status indicator
    expanded = render_sidebar_section("Database Connection", is_connected)

    # Only show the content if the section is expanded
    if expanded:
        # Connection status
        if is_connected:
            st.sidebar.success("Connected to Neo4j")
        else:
            st.sidebar.warning("Not connected to Neo4j")

        # Connection form
        with st.sidebar.form("neo4j_connection_form"):
            # URI input
            uri = st.text_input(
                "Neo4j URI",
                value=st.session_state.get("neo4j_uri", "bolt://localhost:7687"),
                disabled=is_connected
            )

            # Username input
            username = st.text_input(
                "Username",
                value=st.session_state.get("neo4j_user", "neo4j"),
                disabled=is_connected
            )

            # Password input
            password = st.text_input(
                "Password",
                value=st.session_state.get("neo4j_password", "password"),
                type="password",
                disabled=is_connected
            )

            # Database input
            database = st.text_input(
                "Database",
                value=st.session_state.get("neo4j_database", "neo4j"),
                disabled=is_connected
            )

            # Connect/Disconnect button
            if is_connected:
                if st.form_submit_button("Disconnect"):
                    if on_disconnect:
                        on_disconnect()
            else:
                if st.form_submit_button("Connect"):
                    # Update session state
                    st.session_state["neo4j_uri"] = uri
                    st.session_state["neo4j_user"] = username
                    st.session_state["neo4j_password"] = password
                    st.session_state["neo4j_database"] = database

                    if on_connect:
                        on_connect(uri, username, password, database)

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
    # Check if Jupyter is running
    jupyter_token = st.session_state.get("jupyter_token", "")
    is_running = jupyter_token != ""

    # Render the section header with status indicator
    expanded = render_sidebar_section("Jupyter Lab", is_running)

    # Only show the content if the section is expanded
    if expanded:
        # Jupyter URL
        jupyter_url = st.session_state.get("jupyter_url", "http://localhost:8888")

        if is_running:
            st.sidebar.success("Jupyter Lab is running")
            st.sidebar.markdown(f"[Open Jupyter Lab]({jupyter_url})")
        else:
            st.sidebar.warning("Jupyter Lab is not running")

        # Jupyter management form
        with st.sidebar.form("jupyter_form"):
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
                        on_start(port)

            with col2:
                if st.form_submit_button("Stop Jupyter", disabled=not is_running):
                    if on_stop:
                        on_stop()

    # This section is now handled within the expanded section

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
    # Check if NeoDash is running
    neodash_url = st.session_state.get("neodash_url", "")
    is_running = neodash_url != ""

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
                        on_start(port)

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
                    st.experimental_rerun()
        else:
            st.sidebar.warning("Not connected to Microsoft Graph API")

            # Connect button
            if st.sidebar.button("Connect to Microsoft Graph API"):
                if on_connect:
                    on_connect()
                else:
                    # Redirect to Microsoft Graph API connection page
                    st.experimental_set_query_params(page="msgraph_connect")
                    st.experimental_rerun()

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
