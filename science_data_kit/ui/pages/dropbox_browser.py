"""
Dropbox File Browser Page for Science Data Kit

This module provides a Streamlit page for browsing Dropbox files and folders.
"""

import os
import io
import streamlit as st
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime
import base64
import tempfile
from streamlit import components

from science_data_kit_extensions.dropbox.connector import DropboxConnector
from science_data_kit_extensions.dropbox.files import DropboxFileManager


def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_datetime(dt: datetime) -> str:
    """
    Format datetime in human-readable format.

    Args:
        dt: Datetime object

    Returns:
        Formatted datetime string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def dropbox_browser_page():
    """
    Render the Dropbox file browser page.
    """
    st.title("Dropbox File Browser")

    # Check if connected to Dropbox
    if "dropbox_connector" not in st.session_state:
        st.warning("Not connected to Dropbox. Please connect first.")
        st.info("Go to the Dropbox Connect page to set up your connection.")
        return

    connector = st.session_state["dropbox_connector"]
    if not connector.is_connected():
        st.error("Dropbox connection lost. Please reconnect.")
        st.info("Go to the Dropbox Connect page to set up your connection.")
        return

    # Initialize file manager
    file_manager = DropboxFileManager(connector)

    # Initialize session state for current path if not exists
    if "dropbox_current_path" not in st.session_state:
        st.session_state["dropbox_current_path"] = ""

    # Create sidebar for navigation and actions
    with st.sidebar:
        st.header("Navigation")

        # Breadcrumb navigation
        current_path = st.session_state["dropbox_current_path"]
        path_parts = [""] + [p for p in current_path.split("/") if p]

        # Create breadcrumb navigation
        breadcrumb = st.empty()
        breadcrumb_html = '<div style="display: flex; flex-wrap: wrap; align-items: center;">'

        for i, part in enumerate(path_parts):
            path_so_far = "/" + "/".join([p for p in path_parts[1:i+1] if p])
            display_name = "Home" if i == 0 else part

            if i > 0:
                breadcrumb_html += '<span style="margin: 0 5px;">/</span>'

            breadcrumb_html += f'<a href="#" id="path_{i}" style="text-decoration: none;">{display_name}</a>'

        breadcrumb_html += '</div>'
        breadcrumb.markdown(breadcrumb_html, unsafe_allow_html=True)

        # Handle breadcrumb clicks with buttons instead
        cols = st.columns(min(len(path_parts), 4))
        for i, part in enumerate(path_parts[:4]):  # Limit to 4 parts to avoid too many columns
            path_so_far = "/" + "/".join([p for p in path_parts[1:i+1] if p])
            display_name = "Home" if i == 0 else part

            if cols[i].button(display_name, key=f"breadcrumb_{i}"):
                st.session_state["dropbox_current_path"] = path_so_far
                st.experimental_rerun()

        # Go up button
        if current_path:
            parent_path = os.path.dirname(current_path)
            if st.button("⬆️ Go Up"):
                st.session_state["dropbox_current_path"] = parent_path
                st.experimental_rerun()

        # Search
        st.header("Search")
        search_query = st.text_input("Search files", key="dropbox_search_query")
        search_path = st.text_input("Search in path", value=current_path, key="dropbox_search_path")
        search_extensions = st.text_input("File extensions (comma-separated)", key="dropbox_search_extensions")

        if st.button("Search"):
            if search_query:
                extensions = [ext.strip() for ext in search_extensions.split(",")] if search_extensions else None
                try:
                    search_results = file_manager.search(
                        query=search_query,
                        path=search_path,
                        max_results=100,
                        file_extensions=extensions
                    )
                    st.session_state["dropbox_search_results"] = search_results
                    st.success(f"Found {len(search_results)} results")
                except Exception as e:
                    st.error(f"Search error: {str(e)}")
            else:
                st.warning("Please enter a search query")

    # Main content area
    current_path = st.session_state["dropbox_current_path"]

    # Display search results if available
    if "dropbox_search_results" in st.session_state and st.session_state["dropbox_search_results"]:
        st.header("Search Results")

        search_results = st.session_state["dropbox_search_results"]

        # Convert to DataFrame for display
        results_data = []
        for item in search_results:
            results_data.append({
                "Type": "📁" if item["type"] == "folder" else "📄",
                "Name": item["name"],
                "Path": item["path"],
                "Size": format_size(item["size"]) if "size" in item else "",
                "Modified": format_datetime(item["modified"]) if "modified" in item else ""
            })

        if results_data:
            results_df = pd.DataFrame(results_data)
            st.dataframe(results_df, use_container_width=True)

            # Clear search results button
            if st.button("Clear Search Results"):
                del st.session_state["dropbox_search_results"]
                st.experimental_rerun()
        else:
            st.info("No search results found")

    # Display current folder contents
    st.header(f"Contents of {current_path or 'Home'}")

    try:
        # List folder contents
        items = file_manager.list_folder(current_path)

        # Separate folders and files
        folders = [item for item in items if item["type"] == "folder"]
        files = [item for item in items if item["type"] == "file"]

        # Sort by name
        folders.sort(key=lambda x: x["name"].lower())
        files.sort(key=lambda x: x["name"].lower())

        # Display folders
        if folders:
            st.subheader("Folders")

            # Create a grid of folder buttons
            cols = st.columns(3)
            for i, folder in enumerate(folders):
                col_idx = i % 3
                if cols[col_idx].button(f"📁 {folder['name']}", key=f"folder_{i}"):
                    st.session_state["dropbox_current_path"] = folder["path"]
                    st.experimental_rerun()

        # Display files
        if files:
            st.subheader("Files")

            # Convert to DataFrame for display
            files_data = []
            for item in files:
                files_data.append({
                    "Name": item["name"],
                    "Size": format_size(item["size"]) if "size" in item else "",
                    "Modified": format_datetime(item["modified"]) if "modified" in item else "",
                    "Path": item["path"]
                })

            files_df = pd.DataFrame(files_data)
            st.dataframe(files_df, use_container_width=True)

            # File selection for details
            selected_file = st.selectbox("Select a file for details", 
                                        [file["name"] for file in files],
                                        key="dropbox_selected_file")

            if selected_file:
                selected_file_data = next((f for f in files if f["name"] == selected_file), None)

                if selected_file_data:
                    st.subheader("File Details")

                    # Display file details
                    col1, col2 = st.columns(2)
                    col1.write(f"**Name:** {selected_file_data['name']}")
                    col1.write(f"**Path:** {selected_file_data['path']}")
                    col1.write(f"**Size:** {format_size(selected_file_data['size'])}")
                    col2.write(f"**Modified:** {format_datetime(selected_file_data['modified'])}")
                    col2.write(f"**ID:** {selected_file_data['id']}")

                    # Preview button for common file types
                    file_ext = os.path.splitext(selected_file_data['name'])[1].lower()
                    previewable_extensions = [
                        '.txt', '.csv', '.md', '.json', '.jpg', '.jpeg', '.png', '.gif',
                        '.pdf', '.xlsx', '.xls', '.html', '.htm', '.xml', '.py', '.js'
                    ]

                    if file_ext in previewable_extensions:
                        if st.button("Preview File"):
                            try:
                                file_content, _ = file_manager.download_file(selected_file_data['path'])

                                # Display based on file type
                                if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                                    st.image(file_content)
                                elif file_ext == '.csv':
                                    df = pd.read_csv(io.BytesIO(file_content))
                                    st.dataframe(df)
                                elif file_ext in ['.xlsx', '.xls']:
                                    df = pd.read_excel(io.BytesIO(file_content))
                                    st.dataframe(df)
                                elif file_ext == '.pdf':
                                    # Display PDF using base64 encoding
                                    base64_pdf = base64.b64encode(file_content).decode('utf-8')
                                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
                                    st.markdown(pdf_display, unsafe_allow_html=True)
                                elif file_ext in ['.html', '.htm']:
                                    # Display HTML content
                                    html_content = file_content.decode('utf-8')
                                    components.html(html_content, height=500, scrolling=True)
                                elif file_ext == '.md':
                                    # Render markdown properly
                                    md_content = file_content.decode('utf-8')
                                    st.markdown(md_content)
                                elif file_ext in ['.xml', '.py', '.js']:
                                    # Display code with syntax highlighting
                                    code_content = file_content.decode('utf-8')
                                    st.code(code_content, language=file_ext[1:])  # Remove the dot from extension
                                elif file_ext in ['.txt', '.json']:
                                    st.text_area("File Content", file_content.decode('utf-8'), height=300)
                            except Exception as e:
                                st.error(f"Error previewing file: {str(e)}")

                    # Download button
                    if st.button("Download File"):
                        try:
                            file_content, _ = file_manager.download_file(selected_file_data['path'])
                            st.download_button(
                                label="Save File",
                                data=file_content,
                                file_name=selected_file_data['name'],
                                mime="application/octet-stream"
                            )
                        except Exception as e:
                            st.error(f"Error downloading file: {str(e)}")

        if not folders and not files:
            st.info("This folder is empty")

    except Exception as e:
        st.error(f"Error listing folder contents: {str(e)}")


def render_dropbox_browser_page():
    """Render the Dropbox file browser page."""
    dropbox_browser_page()

if __name__ == "__main__":
    render_dropbox_browser_page()
