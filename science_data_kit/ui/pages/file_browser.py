"""
File Browser Page Module for Science Data Kit

This module provides the File Browser page for the Science Data Kit application.
The File Browser page allows users to browse files and view spreadsheets/tables
from different connection types.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
import os
import json

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.sidebar import render_file_connections_sidebar
from science_data_kit.core.utils.file_utils import (
    get_directory_contents,
    get_file_info,
    read_file_as_dataframe,
    get_file_preview
)

class FileBrowserPage(BasePage):
    """
    File Browser page for browsing files and viewing spreadsheets/tables.

    This page provides functionality for:
    - Browsing files from different connection types
    - Viewing file information
    - Reading spreadsheets and tables
    """

    def __init__(self):
        """Initialize the File Browser page."""
        super().__init__("File Browser", "📁")
        self._setup_sidebar()

        # Initialize session state variables
        if "current_path" not in st.session_state:
            st.session_state["current_path"] = ""

        if "file_history" not in st.session_state:
            st.session_state["file_history"] = []

        if "current_file" not in st.session_state:
            st.session_state["current_file"] = None

        if "connection_type" not in st.session_state:
            st.session_state["connection_type"] = None

    def _setup_sidebar(self):
        """Set up the sidebar items for the File Browser page."""
        self.add_sidebar_item(
            render_file_connections_sidebar,
            on_connect=self._on_file_connect,
            on_disconnect=self._on_file_disconnect
        )

    def _on_file_connect(self, path: str, connection_name: str = None):
        """
        Handle file connection.

        Args:
            path: The path to connect to.
            connection_name: Optional name for the connection.
        """
        # Determine connection type from session state
        connection_type = st.session_state.get("file_conn_selected")

        if connection_type == "local_fs":
            # Set current path
            st.session_state["current_path"] = path
            st.session_state["connection_type"] = "local_fs"
            st.session_state["file_history"] = [path]
            st.session_state["current_file"] = None
            st.success(f"Connected to local filesystem at {path}")
        elif connection_type == "sharepoint":
            # Handle Sharepoint connection
            st.session_state["connection_type"] = "sharepoint"
            st.session_state["current_file"] = None
            st.success(f"Connected to Sharepoint")
        elif connection_type == "dropbox":
            # Handle Dropbox connection
            st.session_state["connection_type"] = "dropbox"
            st.session_state["current_file"] = None
            st.info("Dropbox connection not fully implemented yet")
        elif connection_type == "gdrive":
            # Handle Google Drive connection
            st.session_state["connection_type"] = "gdrive"
            st.session_state["current_file"] = None
            st.info("Google Drive connection not fully implemented yet")
        else:
            st.error(f"Unknown connection type: {connection_type}")

    def _on_file_disconnect(self):
        """Handle file disconnection."""
        connection_type = st.session_state.get("connection_type")

        if connection_type == "local_fs":
            st.session_state["local_fs_connected"] = False
            st.session_state["current_path"] = ""
            st.session_state["file_history"] = []
            st.session_state["current_file"] = None
            st.session_state["connection_type"] = None
            st.success("Disconnected from local filesystem")
        elif connection_type == "sharepoint":
            st.session_state["sharepoint_connected"] = False
            st.session_state["current_path"] = ""
            st.session_state["file_history"] = []
            st.session_state["current_file"] = None
            st.session_state["connection_type"] = None
            st.success("Disconnected from Sharepoint")
        elif connection_type == "dropbox":
            st.session_state["dropbox_connected"] = False
            st.session_state["current_path"] = ""
            st.session_state["file_history"] = []
            st.session_state["current_file"] = None
            st.session_state["connection_type"] = None
            st.success("Disconnected from Dropbox")
        elif connection_type == "gdrive":
            st.session_state["gdrive_connected"] = False
            st.session_state["current_path"] = ""
            st.session_state["file_history"] = []
            st.session_state["current_file"] = None
            st.session_state["connection_type"] = None
            st.success("Disconnected from Google Drive")
        else:
            st.error(f"Unknown connection type: {connection_type}")

    def _navigate_to(self, path: str):
        """
        Navigate to a directory.

        Args:
            path: The path to navigate to.
        """
        # Update current path
        st.session_state["current_path"] = path

        # Add to history if not already there
        if path not in st.session_state["file_history"]:
            st.session_state["file_history"].append(path)

        # Clear current file
        st.session_state["current_file"] = None

        # Rerun to update UI
        st.rerun()

    def _view_file(self, file_path: str):
        """
        View a file.

        Args:
            file_path: The path to the file to view.
        """
        # Update current file
        st.session_state["current_file"] = file_path

        # Rerun to update UI
        st.rerun()

    def _go_back(self):
        """Go back to the previous directory."""
        if len(st.session_state["file_history"]) > 1:
            # Remove current path from history
            st.session_state["file_history"].pop()

            # Set current path to previous path
            st.session_state["current_path"] = st.session_state["file_history"][-1]

            # Clear current file
            st.session_state["current_file"] = None

            # Rerun to update UI
            st.rerun()

    def _go_up(self):
        """Go up one directory level."""
        current_path = st.session_state["current_path"]
        parent_path = os.path.dirname(current_path)

        if parent_path and parent_path != current_path:
            self._navigate_to(parent_path)

    def render_file_browser(self):
        """Render the file browser section."""
        st.header("File Browser")

        # Check if connected
        connection_type = st.session_state.get("connection_type")
        if not connection_type:
            st.info("Please connect to a file source using the sidebar")
            return

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("⬅️ Back"):
                self._go_back()

        with col2:
            if st.button("⬆️ Up"):
                self._go_up()

        with col3:
            st.write(f"Current path: {st.session_state['current_path']}")

        # Display current directory contents
        current_path = st.session_state["current_path"]
        if current_path:
            try:
                contents = get_directory_contents(current_path)

                if not contents:
                    st.info(f"No items found in {current_path}")
                    return

                # Create a DataFrame for display
                df = pd.DataFrame(contents)

                # Format size column
                def format_size(size):
                    if size is None:
                        return ""
                    elif size < 1024:
                        return f"{size} B"
                    elif size < 1024 * 1024:
                        return f"{size / 1024:.1f} KB"
                    elif size < 1024 * 1024 * 1024:
                        return f"{size / (1024 * 1024):.1f} MB"
                    else:
                        return f"{size / (1024 * 1024 * 1024):.1f} GB"

                df["size_formatted"] = df["size"].apply(format_size)

                # Display as a table with clickable links
                for _, row in df.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 1, 2, 1])

                    with col1:
                        if row["type"] == "directory":
                            if st.button(f"📁 {row['name']}", key=f"dir_{row['path']}"):
                                self._navigate_to(row["path"])
                        else:
                            if st.button(f"📄 {row['name']}", key=f"file_{row['path']}"):
                                self._view_file(row["path"])

                    with col2:
                        st.write(row["type"])

                    with col3:
                        st.write(row["modified"])

                    with col4:
                        st.write(row["size_formatted"])

            except Exception as e:
                st.error(f"Error browsing directory: {e}")

    def render_file_viewer(self):
        """Render the file viewer section."""
        st.header("File Viewer")

        # Check if a file is selected
        current_file = st.session_state.get("current_file")
        if not current_file:
            st.info("Select a file to view")
            return

        # Get file info
        file_info = get_file_info(current_file)

        # Display file info
        st.subheader(file_info["name"])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"Type: {file_info['type']}")
        with col2:
            st.write(f"Size: {file_info['size']} bytes")
        with col3:
            st.write(f"Modified: {file_info['modified']}")

        # Check if file is readable as a spreadsheet or table
        if file_info["is_readable"]:
            # Get file preview
            preview = get_file_preview(current_file)

            if preview["success"]:
                # Display preview
                st.subheader("Preview")

                # Create DataFrame from preview data
                preview_df = pd.DataFrame(
                    preview["data"]["data"],
                    columns=preview["data"]["columns"]
                )

                # Display DataFrame
                st.dataframe(preview_df)

                # Show total rows
                st.write(f"Showing {preview['data']['preview_rows']} of {preview['data']['total_rows']} rows")

                # Option to load full data
                if st.button("Load Full Data"):
                    df, error = read_file_as_dataframe(current_file)
                    if df is not None:
                        st.subheader("Full Data")
                        st.dataframe(df)
                    else:
                        st.error(f"Error loading full data: {error}")
            else:
                st.error(f"Error previewing file: {preview['error']}")
        else:
            # For non-readable files, show a message
            st.info("This file type cannot be previewed as a spreadsheet or table")

            # For text files, try to display content
            ext = os.path.splitext(current_file)[1].lower()
            if ext in ['.txt', '.md', '.py', '.json', '.csv', '.html', '.xml', '.yml', '.yaml']:
                try:
                    with open(current_file, 'r') as f:
                        content = f.read()
                    st.subheader("File Content")
                    st.text(content)
                except Exception as e:
                    st.error(f"Error reading file: {e}")

    def render_content(self) -> None:
        """Render the File Browser page content."""
        st.write("Browse files and view spreadsheets/tables from different connection types.")

        # Create two columns: file browser and file viewer
        col1, col2 = st.columns(2)

        with col1:
            self.render_file_browser()

        with col2:
            self.render_file_viewer()

def render_file_browser_page():
    """Render the File Browser page using the framework-agnostic implementation."""
    from science_data_kit.ui.adapters.streamlit_adapter import render_file_browser_page as render_core_file_browser
    render_core_file_browser()
