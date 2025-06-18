"""
Survey Page Module for Science Data Kit

This module provides the Survey page for the Science Data Kit application.
The Survey page handles scanning and analyzing file systems.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
import os

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.sidebar import render_database_sidebar
from science_data_kit.core.db.db_manager import db_manager
from science_data_kit.core.models.file_models import Folder, File

class SurveyPage(BasePage):
    """
    Survey page for scanning and analyzing file systems.
    
    This page provides functionality for:
    - Locating and scanning datasets
    - Viewing scan results
    - Labeling entities
    - Pushing data to Neo4j
    """
    
    def __init__(self):
        """Initialize the Survey page."""
        super().__init__("Survey", "🔭")
        self._setup_sidebar()
        self.db_manager = db_manager
        
        # Initialize session state variables
        if "folder_path" not in st.session_state:
            st.session_state["folder_path"] = ""
        
        if "scan_results" not in st.session_state:
            st.session_state["scan_results"] = None
        
        if "selected_files" not in st.session_state:
            st.session_state["selected_files"] = []
        
        if "entity_labels" not in st.session_state:
            st.session_state["entity_labels"] = {}
    
    def _setup_sidebar(self):
        """Set up the sidebar items for the Survey page."""
        self.add_sidebar_item(
            render_database_sidebar,
            on_connect=self._on_database_connect,
            on_disconnect=self._on_database_disconnect
        )
    
    def _on_database_connect(self, uri: str, username: str, password: str, database: str):
        """
        Handle database connection.
        
        Args:
            uri: The URI of the Neo4j server.
            username: The username for authentication.
            password: The password for authentication.
            database: The name of the database to connect to.
        """
        try:
            # Update connection details
            self.db_manager.uri = uri
            self.db_manager.user = username
            self.db_manager.password = password
            self.db_manager.database = database
            
            # Connect to the database
            self.db_manager._connect()
            
            # Update session state
            st.session_state["connected"] = True
            st.session_state["neo4j_uri"] = uri
            st.session_state["neo4j_user"] = username
            st.session_state["neo4j_password"] = password
            st.session_state["neo4j_database"] = database
            
            st.success(f"Connected to Neo4j database at {uri}")
        except Exception as e:
            st.error(f"Failed to connect to Neo4j: {e}")
    
    def _on_database_disconnect(self):
        """Handle database disconnection."""
        try:
            # Close the connection
            self.db_manager.close()
            
            # Update session state
            st.session_state["connected"] = False
            
            st.success("Disconnected from Neo4j database")
        except Exception as e:
            st.error(f"Failed to disconnect from Neo4j: {e}")
    
    def _scan_directory(self, folder_path: str) -> pd.DataFrame:
        """
        Scan a directory and return the results as a DataFrame.
        
        Args:
            folder_path: The path to the directory to scan.
            
        Returns:
            A DataFrame containing the scan results.
        """
        results = []
        
        try:
            # Walk through the directory
            for root, dirs, files in os.walk(folder_path):
                # Add directories
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    results.append({
                        "type": "Folder",
                        "name": dir_name,
                        "path": dir_path,
                        "size": 0,
                        "parent": root
                    })
                
                # Add files
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    try:
                        file_size = os.path.getsize(file_path)
                    except:
                        file_size = 0
                    
                    results.append({
                        "type": "File",
                        "name": file_name,
                        "path": file_path,
                        "size": file_size,
                        "parent": root
                    })
        except Exception as e:
            st.error(f"Error scanning directory: {e}")
        
        return pd.DataFrame(results)
    
    def _push_to_neo4j(self, scan_results: pd.DataFrame) -> bool:
        """
        Push scan results to Neo4j.
        
        Args:
            scan_results: DataFrame containing scan results.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.db_manager.is_connected():
            st.error("Not connected to Neo4j. Please connect first.")
            return False
        
        try:
            # Create a transaction
            with self.db_manager._driver.session(database=self.db_manager.database) as session:
                # Create folders first
                folders = scan_results[scan_results["type"] == "Folder"]
                for _, row in folders.iterrows():
                    # Create folder node
                    folder = Folder(filepath=row["path"]).save()
                    
                    # Create parent relationship if not root
                    if row["parent"] != row["path"]:
                        parent_folder = Folder.nodes.get_or_none(filepath=row["parent"])
                        if parent_folder:
                            folder.is_in.connect(parent_folder)
                
                # Create files
                files = scan_results[scan_results["type"] == "File"]
                for _, row in files.iterrows():
                    # Create file node
                    file = File(filepath=row["path"]).save()
                    
                    # Create parent relationship
                    parent_folder = Folder.nodes.get_or_none(filepath=row["parent"])
                    if parent_folder:
                        file.is_in.connect(parent_folder)
                
                # Apply entity labels if any
                for path, labels in st.session_state["entity_labels"].items():
                    for label in labels:
                        # Add label to node
                        query = """
                        MATCH (n {filepath: $path})
                        SET n:`{label}`
                        """.format(label=label)
                        session.run(query, {"path": path})
            
            return True
        except Exception as e:
            st.error(f"Error pushing to Neo4j: {e}")
            return False
    
    def render_content(self) -> None:
        """Render the Survey page content."""
        st.write("Scan and analyze your file systems.")
        
        # File system browser
        st.header("File System Browser")
        
        # Directory input
        col1, col2 = st.columns([3, 1])
        with col1:
            folder_path = st.text_input(
                "Directory Path",
                value=st.session_state["folder_path"]
            )
        
        with col2:
            if st.button("Scan Directory"):
                if folder_path:
                    # Update session state
                    st.session_state["folder_path"] = folder_path
                    
                    # Scan directory
                    with st.spinner("Scanning directory..."):
                        scan_results = self._scan_directory(folder_path)
                        st.session_state["scan_results"] = scan_results
                        
                        if not scan_results.empty:
                            st.success(f"Found {len(scan_results)} items")
                        else:
                            st.warning("No items found")
                else:
                    st.error("Please enter a directory path")
        
        # Scan results
        st.header("Scan Results")
        scan_results = st.session_state["scan_results"]
        
        if scan_results is not None and not scan_results.empty:
            # Display summary
            st.write("Summary:")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Total items: {len(scan_results)}")
                st.write(f"Folders: {len(scan_results[scan_results['type'] == 'Folder'])}")
                st.write(f"Files: {len(scan_results[scan_results['type'] == 'File'])}")
            
            with col2:
                # Calculate total size
                total_size = scan_results["size"].sum()
                st.write(f"Total size: {total_size / (1024 * 1024):.2f} MB")
            
            # Display results table
            st.write("Results:")
            st.dataframe(scan_results)
            
            # Allow selection of files
            selected_indices = st.multiselect(
                "Select items for labeling",
                options=list(range(len(scan_results))),
                format_func=lambda i: f"{scan_results.iloc[i]['type']}: {scan_results.iloc[i]['name']}"
            )
            
            if selected_indices:
                st.session_state["selected_files"] = [
                    scan_results.iloc[i]["path"] for i in selected_indices
                ]
        else:
            st.info("No scan results available. Please scan a directory first.")
        
        # Entity labeling
        st.header("Entity Labeling")
        
        if st.session_state["selected_files"]:
            st.write(f"Selected {len(st.session_state['selected_files'])} items for labeling")
            
            # Label input
            label = st.text_input("Enter label for selected items")
            
            if st.button("Apply Label") and label:
                # Update entity labels
                for file_path in st.session_state["selected_files"]:
                    if file_path not in st.session_state["entity_labels"]:
                        st.session_state["entity_labels"][file_path] = []
                    
                    if label not in st.session_state["entity_labels"][file_path]:
                        st.session_state["entity_labels"][file_path].append(label)
                
                st.success(f"Applied label '{label}' to {len(st.session_state['selected_files'])} items")
            
            # Display current labels
            if st.session_state["entity_labels"]:
                st.write("Current labels:")
                
                for file_path, labels in st.session_state["entity_labels"].items():
                    if file_path in st.session_state["selected_files"]:
                        st.write(f"{os.path.basename(file_path)}: {', '.join(labels)}")
        else:
            st.info("No items selected for labeling")
        
        # Push to Neo4j
        st.header("Push to Neo4j")
        
        if scan_results is not None and not scan_results.empty:
            if st.button("Push to Neo4j"):
                if not st.session_state.get("connected", False):
                    st.error("Not connected to Neo4j. Please connect first.")
                else:
                    with st.spinner("Pushing to Neo4j..."):
                        success = self._push_to_neo4j(scan_results)
                        
                        if success:
                            st.success("Successfully pushed to Neo4j")
                        else:
                            st.error("Failed to push to Neo4j")
        else:
            st.info("No scan results available. Please scan a directory first.")

def render():
    """Render the Survey page."""
    page = SurveyPage()
    page.render()