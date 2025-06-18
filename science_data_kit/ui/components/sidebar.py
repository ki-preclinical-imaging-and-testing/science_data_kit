"""
Sidebar Component for Science Data Kit

This module provides the sidebar component for the Science Data Kit application.
It includes functions for rendering the sidebar and its various sections.
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path

def render_sidebar_header() -> None:
    """Render the sidebar header with logo and title."""
    st.sidebar.image("https://raw.githubusercontent.com/NIEHS/science_data_kit/main/docs/images/sdk_logo.png", width=200)
    st.sidebar.title("Science Data Kit")

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
    st.sidebar.header("Database Connection")
    
    # Connection status
    if st.session_state.get("connected", False):
        st.sidebar.success("Connected to Neo4j")
    else:
        st.sidebar.warning("Not connected to Neo4j")
    
    # Connection form
    with st.sidebar.form("neo4j_connection_form"):
        # URI input
        uri = st.text_input(
            "Neo4j URI",
            value=st.session_state.get("neo4j_uri", "bolt://localhost:7687"),
            disabled=st.session_state.get("connected", False)
        )
        
        # Username input
        username = st.text_input(
            "Username",
            value=st.session_state.get("neo4j_user", "neo4j"),
            disabled=st.session_state.get("connected", False)
        )
        
        # Password input
        password = st.text_input(
            "Password",
            value=st.session_state.get("neo4j_password", "password"),
            type="password",
            disabled=st.session_state.get("connected", False)
        )
        
        # Database input
        database = st.text_input(
            "Database",
            value=st.session_state.get("neo4j_database", "neo4j"),
            disabled=st.session_state.get("connected", False)
        )
        
        # Connect/Disconnect button
        if st.session_state.get("connected", False):
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
    st.sidebar.header("Neo4j Container")
    
    # Container status
    container_status = st.session_state.get("container_status", "unknown")
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
    st.sidebar.header("Jupyter Lab")
    
    # Jupyter URL
    jupyter_url = st.session_state.get("jupyter_url", "http://localhost:8888")
    jupyter_token = st.session_state.get("jupyter_token", "")
    
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
            if st.form_submit_button("Start Jupyter"):
                if on_start:
                    on_start(port)
        
        with col2:
            if st.form_submit_button("Stop Jupyter"):
                if on_stop:
                    on_stop()
    
    # Jupyter link
    if jupyter_url and jupyter_token:
        full_url = f"{jupyter_url}/?token={jupyter_token}"
        st.sidebar.markdown(f"[Open Jupyter Lab]({full_url})")

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
    st.sidebar.header("NeoDash")
    
    # NeoDash URL
    neodash_url = st.session_state.get("neodash_url", "http://localhost:5005")
    
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
            if st.form_submit_button("Start NeoDash"):
                if on_start:
                    on_start(port)
        
        with col2:
            if st.form_submit_button("Stop NeoDash"):
                if on_stop:
                    on_stop()
    
    # NeoDash link
    if neodash_url:
        st.sidebar.markdown(f"[Open NeoDash]({neodash_url})")

def render_settings_sidebar() -> None:
    """Render the settings section in the sidebar."""
    st.sidebar.header("Settings")
    
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
    all_sections = ["header", "database", "neo4j", "jupyter", "neodash", "settings"]
    
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
        elif section == "settings":
            render_settings_sidebar()