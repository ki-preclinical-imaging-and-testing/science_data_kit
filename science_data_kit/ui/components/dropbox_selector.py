"""
Dropbox Selector Component for Science Data Kit

This module provides a Streamlit component for selecting and previewing
files from Dropbox.
"""

import os
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple

from ...core.providers.registry import ProviderType
from ...core.providers.storage.dropbox_provider import DropboxProvider
from ...core.config.providers import load_provider_config


def render_dropbox_selector() -> Optional[Dict[str, Any]]:
    """
    Render a Dropbox file selection UI component.
    
    Returns:
        Dictionary containing selected file data and metadata, or None if no file is selected
    """
    st.subheader("Dropbox Data Import")
    
    # Check if provider is configured
    config = load_provider_config()
    dropbox_config = config.get("storage", {}).get("dropbox", {})
    
    if not dropbox_config or "access_token" not in dropbox_config:
        return _render_setup_instructions()
    
    # Initialize provider if not already in session state
    if "dropbox_provider" not in st.session_state:
        _initialize_provider(dropbox_config)
    
    # If provider failed to initialize, show setup instructions
    if not st.session_state.get("dropbox_provider_initialized", False):
        return _render_setup_instructions()
    
    # Get provider from session state
    provider = st.session_state["dropbox_provider"]
    
    # Create UI for folder navigation and file selection
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Folder navigation
        current_path = st.session_state.get("dropbox_current_path", "")
        st.text_input("Folder Path", value=current_path, key="dropbox_folder_path")
        
        if st.button("Browse Folder"):
            st.session_state["dropbox_current_path"] = st.session_state["dropbox_folder_path"]
            st.session_state["dropbox_files"] = _list_files(provider, st.session_state["dropbox_folder_path"])
            st.session_state["dropbox_selected_file"] = None
            st.session_state["dropbox_preview_data"] = None
    
    # Display files and handle selection
    files = st.session_state.get("dropbox_files", [])
    
    if not files:
        st.session_state["dropbox_files"] = _list_files(provider, current_path)
        files = st.session_state.get("dropbox_files", [])
    
    with col1:
        st.write("Files:")
        
        # Group files by type
        folders = [f for f in files if f.get("type") == "folder"]
        csv_files = [f for f in files if f.get("type") == "csv"]
        excel_files = [f for f in files if f.get("type") in ["xlsx", "xls"]]
        
        # Display folders first
        for folder in folders:
            if st.button(f"📁 {folder['name']}", key=f"folder_{folder['id']}"):
                st.session_state["dropbox_current_path"] = folder["path"]
                st.session_state["dropbox_folder_path"] = folder["path"]
                st.session_state["dropbox_files"] = _list_files(provider, folder["path"])
                st.session_state["dropbox_selected_file"] = None
                st.session_state["dropbox_preview_data"] = None
                st.experimental_rerun()
        
        # Display CSV files
        for file in csv_files:
            if st.button(f"📄 {file['name']}", key=f"file_{file['id']}"):
                st.session_state["dropbox_selected_file"] = file
                st.session_state["dropbox_preview_data"] = _get_preview_data(provider, file["path"])
        
        # Display Excel files
        for file in excel_files:
            if st.button(f"📊 {file['name']}", key=f"file_{file['id']}"):
                st.session_state["dropbox_selected_file"] = file
                st.session_state["dropbox_preview_data"] = _get_preview_data(provider, file["path"])
    
    # Display file preview and import button
    with col2:
        selected_file = st.session_state.get("dropbox_selected_file")
        preview_data = st.session_state.get("dropbox_preview_data")
        
        if selected_file and preview_data is not None:
            st.write(f"Selected: **{selected_file['name']}**")
            
            # Display file metadata
            st.write(f"Size: {_format_size(selected_file.get('size', 0))}")
            st.write(f"Modified: {selected_file.get('modified', 'Unknown')}")
            
            # Display data preview
            st.write("Data Preview:")
            st.dataframe(preview_data)
            
            # Import button
            if st.button("Import Data"):
                full_data = _get_full_data(provider, selected_file["path"])
                
                if full_data is not None:
                    return {
                        "data": full_data,
                        "metadata": selected_file,
                        "source": "dropbox",
                        "path": selected_file["path"]
                    }
        else:
            st.write("Select a file to preview")
    
    return None


def _render_setup_instructions() -> None:
    """Render instructions for setting up Dropbox integration."""
    st.warning("Dropbox integration is not configured.")
    
    st.write("""
    ### Setup Instructions
    
    To connect to Dropbox, you need to provide an access token:
    
    1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
    2. Create a new app with "Scoped access" and "Full Dropbox" access
    3. Generate an access token in the app settings
    4. Enter the access token below
    """)
    
    access_token = st.text_input("Dropbox Access Token", type="password")
    
    if st.button("Connect to Dropbox") and access_token:
        setup_dropbox_provider(access_token)
        st.experimental_rerun()
    
    return None


def setup_dropbox_provider(access_token: str) -> bool:
    """
    Set up the Dropbox provider with the provided access token.
    
    Args:
        access_token: Dropbox access token
        
    Returns:
        True if setup was successful, False otherwise
    """
    # Create configuration
    config = {
        "storage": {
            "dropbox": {
                "access_token": access_token
            }
        }
    }
    
    # Initialize provider
    return _initialize_provider(config["storage"]["dropbox"])


def _initialize_provider(config: Dict[str, Any]) -> bool:
    """
    Initialize the Dropbox provider.
    
    Args:
        config: Dropbox configuration dictionary
        
    Returns:
        True if initialization was successful, False otherwise
    """
    try:
        # Create provider
        provider = DropboxProvider(config)
        
        # Initialize provider (run async function in sync context)
        import asyncio
        success = asyncio.run(provider.initialize())
        
        if success:
            # Store provider in session state
            st.session_state["dropbox_provider"] = provider
            st.session_state["dropbox_provider_initialized"] = True
            st.session_state["dropbox_current_path"] = ""
            st.session_state["dropbox_files"] = []
            st.session_state["dropbox_selected_file"] = None
            st.session_state["dropbox_preview_data"] = None
            return True
        else:
            st.error("Failed to initialize Dropbox provider. Please check your access token.")
            st.session_state["dropbox_provider_initialized"] = False
            return False
    
    except Exception as e:
        st.error(f"Error initializing Dropbox provider: {str(e)}")
        st.session_state["dropbox_provider_initialized"] = False
        return False


def _list_files(provider: DropboxProvider, folder_path: str) -> List[Dict[str, Any]]:
    """
    List files in a Dropbox folder.
    
    Args:
        provider: Dropbox provider
        folder_path: Path to the folder in Dropbox
        
    Returns:
        List of file metadata dictionaries
    """
    try:
        # Run async function in sync context
        import asyncio
        return asyncio.run(provider.list_files(folder_path))
    except Exception as e:
        st.error(f"Error listing files: {str(e)}")
        return []


def _get_preview_data(provider: DropboxProvider, file_path: str) -> Optional[pd.DataFrame]:
    """
    Get a preview of the file data.
    
    Args:
        provider: Dropbox provider
        file_path: Path to the file in Dropbox
        
    Returns:
        Pandas DataFrame containing a preview of the file data
    """
    try:
        # Run async function in sync context
        import asyncio
        df = asyncio.run(provider.download_file_data(file_path))
        
        # Return first 10 rows for preview
        return df.head(10)
    except Exception as e:
        st.error(f"Error getting file preview: {str(e)}")
        return None


def _get_full_data(provider: DropboxProvider, file_path: str) -> Optional[pd.DataFrame]:
    """
    Get the full file data.
    
    Args:
        provider: Dropbox provider
        file_path: Path to the file in Dropbox
        
    Returns:
        Pandas DataFrame containing the full file data
    """
    try:
        # Run async function in sync context
        import asyncio
        return asyncio.run(provider.download_file_data(file_path))
    except Exception as e:
        st.error(f"Error downloading file: {str(e)}")
        return None


def _format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Human-readable file size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024 or unit == 'GB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024