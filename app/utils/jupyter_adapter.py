"""
Jupyter Adapter for Science Data Kit

This module provides backward compatibility with the old jupyter_server.py functions
by implementing them using the new JupyterManager class.
"""

import streamlit as st
import os
import time
from science_data_kit.core.utils.jupyter_utils import JupyterManager, is_port_in_use, is_port_available, find_free_port, get_container_port_binding

def initialize_jupyter_session():
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

def start_jupyter_container():
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
        host_mountpoint=st.session_state.get("jupyter_host_mountpoint")
    )
    
    try:
        # Start the container using the JupyterManager
        container_info = jupyter_manager.start_container()
        
        if container_info:
            # Update session state with the actual port used
            st.session_state["jupyter_port"] = container_info.get("port")
            
            # Get the container IP
            jupyter_host_ip = container_info.get("ip", "localhost")
            st.session_state['jupyter_host_ip'] = jupyter_host_ip
            
            # Generate and display the URL
            url = f"http://{jupyter_host_ip}:{st.session_state['jupyter_port']}/?token={st.session_state['jupyter_token']}"
            
            if container_info.get("status") == "started":
                st.success(f"✅ Jupyter Lab started!")
            else:
                st.info(f"🔄 Connected to existing Jupyter Lab")
                
            st.markdown(f"🔗 [Open Jupyter Lab]({url})")
            st.code(url)
            
            return url
        else:
            st.error("❌ Failed to start Jupyter container")
            return None
            
    except Exception as e:
        st.error(f"❌ Failed to start Jupyter container: {e}")
        return None

def stop_jupyter_container():
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