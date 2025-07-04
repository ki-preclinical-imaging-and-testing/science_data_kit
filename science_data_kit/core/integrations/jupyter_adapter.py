"""
Jupyter Adapter for Science Data Kit

This module provides backward compatibility with the old jupyter_server.py functions
by implementing them using the new JupyterManager class.
"""

import streamlit as st
import os
import re
from typing import Optional, Union
from science_data_kit.core.utils.jupyter_utils import JupyterManager, is_port_in_use, is_port_available, find_free_port, get_container_port_binding

def initialize_jupyter_session() -> None:
    """
    Initialize Jupyter session state variables if they don't exist.
    """
    if "jupyter_container_name" not in st.session_state:
        st.session_state["jupyter_container_name"] = "dsk-jupyter-instance"
    if "jupyter_port" not in st.session_state:
        st.session_state["jupyter_port"] = 8888
    if "jupyter_token" not in st.session_state:
        st.session_state["jupyter_token"] = "letmein"
    if "jupyter_host_mountpoint" not in st.session_state:
        st.session_state["jupyter_host_mountpoint"] = os.path.abspath('../')
    # Initialize multi-user settings
    if "jupyter_admin_user" not in st.session_state:
        st.session_state["jupyter_admin_user"] = "admin"
    if "jupyter_admin_password" not in st.session_state:
        st.session_state["jupyter_admin_password"] = "admin"
    if "jupyter_enable_multi_user" not in st.session_state:
        st.session_state["jupyter_enable_multi_user"] = True

def start_jupyter_container() -> Optional[str]:
    """
    Start a Jupyter Lab container or connect to an existing one.

    This function will:
    1. Check if a container with the configured name already exists
    2. If it exists, start it if it's not running and return the URL
    3. If it doesn't exist, create a new container and return the URL

    Returns:
        str: The URL to access Jupyter Lab, or None if there was an error
    """
    initialize_jupyter_session()

    # Create a JupyterManager instance with the session state values
    jupyter_manager = JupyterManager(
        container_name=st.session_state["jupyter_container_name"],
        port=st.session_state["jupyter_port"],
        token=st.session_state["jupyter_token"],
        host_mountpoint=st.session_state.get("jupyter_host_mountpoint"),
        admin_user=st.session_state["jupyter_admin_user"],
        admin_password=st.session_state["jupyter_admin_password"],
        enable_multi_user=st.session_state["jupyter_enable_multi_user"]
    )

    try:
        # Start the container using the JupyterManager
        success, message, url = jupyter_manager.start_container()

        if success and url:
            # Extract port from URL
            port_match = re.search(r':(\d+)/', url)
            if port_match:
                port = int(port_match.group(1))
                st.session_state["jupyter_port"] = port

            # Extract host from URL
            host_match = re.search(r'http://([^:]+):', url)
            if host_match:
                jupyter_host_ip = host_match.group(1)
            else:
                jupyter_host_ip = "localhost"

            st.session_state['jupyter_host_ip'] = jupyter_host_ip

            # Display success message
            if "Started new" in message:
                st.success(f"✅ Jupyter Lab started!")
            else:
                st.info(f"🔄 Connected to existing Jupyter Lab")

            st.markdown(f"🔗 [Open Jupyter Lab]({url})")
            st.code(url)

            return url
        else:
            st.error(f"❌ Failed to start Jupyter container: {message}")
            return None

    except Exception as e:
        st.error(f"❌ Failed to start Jupyter container: {e}")
        return None

def stop_jupyter_container() -> None:
    """
    Stop the Jupyter container if it's running.
    """
    initialize_jupyter_session()

    # Create a JupyterManager instance with the session state values
    jupyter_manager = JupyterManager(
        container_name=st.session_state["jupyter_container_name"]
    )

    # Stop the container using the JupyterManager
    jupyter_manager.stop_container()

# Re-export utility functions for backward compatibility
# These are already implemented in the core package