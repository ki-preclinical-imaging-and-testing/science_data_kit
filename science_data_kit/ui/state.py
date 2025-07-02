"""
UI State Management Module for Science Data Kit

This module provides utilities for managing the application state in Streamlit.
It includes functions for initializing, updating, and accessing session state variables.
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Callable
import yaml
from pathlib import Path

def initialize_session_state() -> None:
    """
    Initialize the Streamlit session state with default values.
    This should be called at the start of the application.
    """
    # Database connection state
    if "connected" not in st.session_state:
        st.session_state["connected"] = False

    if "neo4j_uri" not in st.session_state:
        st.session_state["neo4j_uri"] = "bolt://localhost:7687"

    if "neo4j_user" not in st.session_state:
        st.session_state["neo4j_user"] = "neo4j"

    if "neo4j_password" not in st.session_state:
        st.session_state["neo4j_password"] = "password"

    if "neo4j_database" not in st.session_state:
        st.session_state["neo4j_database"] = "neo4j"

    # Container state
    if "container_status" not in st.session_state:
        st.session_state["container_status"] = "unknown"

    if "credentials_locked" not in st.session_state:
        st.session_state["credentials_locked"] = False

    if "http_port" not in st.session_state:
        st.session_state["http_port"] = 7474

    if "bolt_port" not in st.session_state:
        st.session_state["bolt_port"] = 7687

    if "username" not in st.session_state:
        st.session_state["username"] = "neo4j"

    if "password" not in st.session_state:
        st.session_state["password"] = "password"

    if "neo4j_version" not in st.session_state:
        st.session_state["neo4j_version"] = "latest"

    # File system state
    if "folder" not in st.session_state:
        st.session_state["folder"] = None

    if "directory_label" not in st.session_state:
        st.session_state["directory_label"] = "Folder"

    # Navigation state
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Connect"

    # Jupyter state
    if "jupyter_url" not in st.session_state:
        st.session_state["jupyter_url"] = "http://localhost:8888"

    if "jupyter_token" not in st.session_state:
        st.session_state["jupyter_token"] = ""

    # Jupyter multi-user settings
    if "jupyter_admin_user" not in st.session_state:
        st.session_state["jupyter_admin_user"] = "admin"

    if "jupyter_admin_password" not in st.session_state:
        st.session_state["jupyter_admin_password"] = "admin"

    if "jupyter_enable_multi_user" not in st.session_state:
        st.session_state["jupyter_enable_multi_user"] = True

    # NeoDash state
    if "neodash_url" not in st.session_state:
        st.session_state["neodash_url"] = ""

def load_state_from_config(config_path: Path) -> None:
    """
    Load session state from a configuration file.

    Args:
        config_path: Path to the configuration file.
    """
    if not config_path.exists():
        return

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        if not config:
            return

        # Update session state with values from config
        for key, value in config.items():
            if key in st.session_state:
                st.session_state[key] = value
    except Exception as e:
        st.error(f"Error loading configuration: {e}")

def save_state_to_config(config_path: Path, keys: Optional[List[str]] = None) -> None:
    """
    Save session state to a configuration file.

    Args:
        config_path: Path to the configuration file.
        keys: Optional list of keys to save. If None, save all keys.
    """
    try:
        # Get the state to save
        state_to_save = {}
        if keys:
            for key in keys:
                if key in st.session_state:
                    state_to_save[key] = st.session_state[key]
        else:
            # Save all serializable state
            for key, value in st.session_state.items():
                # Skip functions, objects, and other non-serializable types
                if isinstance(value, (str, int, float, bool, list, dict, tuple)) or value is None:
                    state_to_save[key] = value

        # Create parent directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        with open(config_path, 'w') as file:
            yaml.dump(state_to_save, file)
    except Exception as e:
        st.error(f"Error saving configuration: {e}")

def register_state_callback(key: str, callback: Callable[[Any], None]) -> None:
    """
    Register a callback function to be called when a session state variable changes.

    Args:
        key: The session state key to watch.
        callback: The callback function to call when the value changes.
    """
    # This is a placeholder for future implementation
    # Streamlit doesn't currently support callbacks for session state changes
    pass

def get_state_snapshot() -> Dict[str, Any]:
    """
    Get a snapshot of the current session state.

    Returns:
        A dictionary containing the current session state.
    """
    return dict(st.session_state)
