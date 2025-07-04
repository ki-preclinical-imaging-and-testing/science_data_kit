"""
NeoDash Adapter for Science Data Kit

This module provides backward compatibility with the old neodash_server.py functions
by implementing them using the new NeoDashManager class.
"""

import streamlit as st
from typing import Optional, Dict, Any
from science_data_kit.core.utils.neodash_utils import NeoDashManager, is_port_available, find_free_port, get_container_port_binding, get_container_ip

def initialize_neodash_session() -> None:
    """
    Initialize NeoDash session state variables if they don't exist.
    """
    if "neodash_container_name" not in st.session_state:
        st.session_state["neodash_container_name"] = "dsk-neodash-instance"
    if "neodash_port" not in st.session_state:
        st.session_state["neodash_port"] = 5005
    if "neodash_connected" not in st.session_state:
        st.session_state["neodash_connected"] = False

def start_neodash_container() -> Optional[str]:
    """
    Start a NeoDash container or connect to an existing one.

    This function will:
    1. Check if a container with the configured name already exists
    2. If it exists, start it if it's not running and return the URL
    3. If it doesn't exist, create a new container and return the URL

    Returns:
        str: The URL to access NeoDash, or None if there was an error
    """
    initialize_neodash_session()
    
    # Get Neo4j connection details from session state
    neo4j_uri = st.session_state.get("neo4j_uri", "bolt://localhost:7687")
    neo4j_user = st.session_state.get("neo4j_user", "neo4j")
    neo4j_password = st.session_state.get("neo4j_password", "neo4jiscool")
    
    # Create a NeoDashManager instance with the session state values
    neodash_manager = NeoDashManager(
        container_name=st.session_state["neodash_container_name"],
        port=st.session_state["neodash_port"],
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )
    
    try:
        # Start the container using the NeoDashManager
        container_info = neodash_manager.start_container()
        
        if container_info:
            # Update session state with the actual port used
            st.session_state["neodash_port"] = container_info.get("port")
            
            # Get the container IP
            neodash_host_ip = container_info.get("ip", "localhost")
            st.session_state['neodash_host_ip'] = neodash_host_ip
            
            # Generate and display the URL
            url = f"http://{neodash_host_ip}:{st.session_state['neodash_port']}"
            
            if container_info.get("status") == "started":
                st.success(f"✅ NeoDash started!")
            else:
                st.info(f"🔄 Connected to existing NeoDash")
                
            st.markdown(f"🔗 NeoDash ({url})")
            
            # Set connected state
            st.session_state["neodash_connected"] = True
            
            return url
        else:
            st.error("❌ Failed to start NeoDash container")
            return None
            
    except Exception as e:
        st.error(f"❌ Failed to start NeoDash container: {e}")
        return None

def stop_neodash_container() -> bool:
    """
    Stop the NeoDash container if it's running.
    
    Returns:
        bool: True if the container was successfully stopped, False otherwise
    """
    initialize_neodash_session()
    
    # Create a NeoDashManager instance with the session state values
    neodash_manager = NeoDashManager(
        container_name=st.session_state["neodash_container_name"]
    )
    
    try:
        # Stop the container using the NeoDashManager
        result = neodash_manager.stop_container()
        
        if result:
            st.session_state["neodash_connected"] = False
            return True
        return False
    except Exception as e:
        st.error(f"Error stopping NeoDash container: {e}")
        return False

# Re-export utility functions for backward compatibility
# These are already implemented in the core package