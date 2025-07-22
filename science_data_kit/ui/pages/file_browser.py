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
from science_data_kit.ui.components.file_preview_components import render_file_preview
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
        # Get the connection type from session state
        connection_type = st.session_state.get("connection_type", "local_fs")

        # Use the core implementation to navigate
        from science_data_kit.core.pages.file_browser import FileBrowserPage
        core_page = FileBrowserPage(initial_path=st.session_state.get("current_path", ""), 
                                    connection_type=connection_type)
        core_page.navigate_to(path)

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

            # Get the previous path
            previous_path = st.session_state["file_history"][-1]

            # Get the connection type from session state
            connection_type = st.session_state.get("connection_type", "local_fs")

            # Use the core implementation to navigate to the previous path
            from science_data_kit.core.pages.file_browser import FileBrowserPage
            core_page = FileBrowserPage(initial_path=st.session_state.get("current_path", ""), 
                                        connection_type=connection_type)
            core_page.navigate_to(previous_path)

            # Update current path
            st.session_state["current_path"] = previous_path

            # Clear current file
            st.session_state["current_file"] = None

            # Rerun to update UI
            st.rerun()

    def _go_up(self):
        """Go up one directory level."""
        # Get the connection type from session state
        connection_type = st.session_state.get("connection_type", "local_fs")

        # Use the core implementation to navigate up
        from science_data_kit.core.pages.file_browser import FileBrowserPage
        core_page = FileBrowserPage(initial_path=st.session_state.get("current_path", ""), 
                                    connection_type=connection_type)
        core_page.navigate_up()

        # Update current path from core page
        new_path = core_page.current_path

        # Only update if the path has changed
        if new_path and new_path != st.session_state["current_path"]:
            # Update current path
            st.session_state["current_path"] = new_path

            # Add to history if not already there
            if new_path not in st.session_state["file_history"]:
                st.session_state["file_history"].append(new_path)

            # Clear current file
            st.session_state["current_file"] = None

            # Rerun to update UI
            st.rerun()

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

        # Add search and filter options
        with st.expander("Search and Filter Options", expanded=False):
            # Simple filename filter
            st.text_input("Filter by filename", key="filename_filter", 
                          on_change=self._apply_filename_filter)

            # Metadata-based filtering
            st.subheader("Metadata Filters")

            # Initialize session state for metadata filters if not exists
            if "metadata_filters" not in st.session_state:
                st.session_state.metadata_filters = []

            # Display active metadata filters
            if st.session_state.metadata_filters:
                st.write("Active Metadata Filters:")
                for i, filter_item in enumerate(st.session_state.metadata_filters):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"{filter_item['field']} {filter_item['operator']} {filter_item['value']}")
                    with col2:
                        if st.button("Remove", key=f"remove_filter_{i}"):
                            st.session_state.metadata_filters.pop(i)
                            # Apply the updated filters
                            self._apply_metadata_filters()
                            st.rerun()

                if st.button("Clear All Filters"):
                    st.session_state.metadata_filters = []
                    # Apply the updated filters (which is now empty)
                    self._apply_metadata_filters()
                    st.rerun()

            # Add new metadata filter
            st.subheader("Add Metadata Filter")

            # Common metadata fields for different file types
            common_fields = [
                "Select a field...",
                "width", "height", "format", "mode",  # Image fields
                "crs.epsg", "resolution.x", "resolution.y",  # GeoTIFF fields
                "count", "driver",  # Raster fields
                "astronomical_metadata.TELESCOP", "astronomical_metadata.INSTRUME",  # FITS fields
                "dimensions", "variables",  # NetCDF fields
                "groups", "datasets",  # HDF5 fields
                "id3.title", "id3.artist", "id3.album",  # MP3 fields
                "length", "bitrate", "sample_rate", "channels"  # Media fields
            ]

            # Allow custom field input
            field_option = st.selectbox("Field", common_fields)
            custom_field = st.text_input("Or enter custom field (use dots for nested fields, e.g., 'crs.epsg')")

            field = custom_field if custom_field else field_option

            # Only proceed if a valid field is selected
            if field and field != "Select a field...":
                # Operator selection
                operators = ["=", "!=", ">", "<", ">=", "<=", "contains", "startswith", "endswith"]
                operator = st.selectbox("Operator", operators)

                # Value input
                value_type = st.selectbox("Value Type", ["Text", "Number"])
                if value_type == "Text":
                    value = st.text_input("Value")
                else:
                    value = st.number_input("Value", value=0)

                # Add filter button
                if st.button("Add Filter"):
                    if field and operator and value is not None:
                        # Add the filter to session state
                        st.session_state.metadata_filters.append({
                            "field": field,
                            "operator": operator,
                            "value": value
                        })
                        # Apply the filters
                        self._apply_metadata_filters()
                        st.rerun()

        # Display current directory contents
        current_path = st.session_state["current_path"]
        connection_type = st.session_state.get("connection_type", "local_fs")

        if current_path:
            try:
                # Use the core implementation to get directory contents
                from science_data_kit.core.pages.file_browser import FileBrowserPage
                core_page = FileBrowserPage(
                    initial_path=current_path, 
                    connection_type=connection_type
                )

                # Apply any active filters
                if "filename_filter" in st.session_state and st.session_state.filename_filter:
                    core_page.set_filter(st.session_state.filename_filter)

                # Apply metadata filters
                if "metadata_filters" in st.session_state and st.session_state.metadata_filters:
                    core_page.clear_metadata_filters()
                    for filter_item in st.session_state.metadata_filters:
                        core_page.set_metadata_filter(
                            filter_item["field"],
                            filter_item["operator"],
                            filter_item["value"]
                        )

                # Get page data from core implementation
                page_data = core_page.get_page_data()

                # Get files and directories from page data
                files = page_data.files
                directories = page_data.directories

                if not files and not directories:
                    st.info(f"No items found in {current_path}")
                    return

                # Format size for files
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

                # Display directories first
                if directories:
                    st.subheader("Directories")
                    for directory in directories:
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            if st.button(f"📁 {directory['name']}", key=f"dir_{directory['path']}"):
                                self._navigate_to(directory['path'])

                        with col2:
                            # Format modified time
                            modified = directory.get('modified', '')
                            if isinstance(modified, (int, float)):
                                from datetime import datetime
                                modified = datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M:%S")
                            st.write(modified)

                # Display files
                if files:
                    st.subheader("Files")
                    for file in files:
                        col1, col2, col3, col4 = st.columns([3, 1, 2, 1])

                        with col1:
                            if st.button(f"📄 {file['name']}", key=f"file_{file['path']}"):
                                self._view_file(file["path"])

                        with col2:
                            st.write(file.get("type", ""))

                        with col3:
                            # Format modified time
                            modified = file.get('modified', '')
                            if isinstance(modified, (int, float)):
                                from datetime import datetime
                                modified = datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M:%S")
                            st.write(modified)

                        with col4:
                            st.write(format_size(file.get("size", 0)))

                # Display facets if available
                if page_data.facets:
                    with st.expander("Metadata Facets", expanded=False):
                        for category, facets in page_data.facets.items():
                            st.subheader(category)
                            for field, values in facets.items():
                                st.write(f"**{field}**")
                                for value, count in values.items():
                                    st.write(f"  {value}: {count}")

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

        # Use the enhanced file preview component
        render_file_preview(current_file)

        # Add option to view as spreadsheet/table if applicable
        ext = os.path.splitext(current_file)[1].lower()
        if ext in ['.csv', '.xlsx', '.xls', '.tsv', '.json', '.xml']:
            with st.expander("View as Spreadsheet/Table", expanded=False):
                try:
                    # Get file preview using the traditional method
                    preview = get_file_preview(current_file)

                    if preview["success"]:
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
                        st.error(f"Error previewing file as spreadsheet: {preview['error']}")
                except Exception as e:
                    st.error(f"Error viewing as spreadsheet: {str(e)}")

    def _apply_filename_filter(self):
        """Apply the filename filter to the file browser."""
        # The actual filtering is now done in render_file_browser
        # This method just triggers a rerun to refresh the UI
        st.rerun()

    def _apply_metadata_filters(self):
        """Apply metadata filters to the file browser."""
        # The actual filtering is now done in render_file_browser
        # This method just triggers a rerun to refresh the UI
        st.rerun()

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
