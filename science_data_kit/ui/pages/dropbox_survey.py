"""
Dropbox Survey Page for Science Data Kit

This module provides a Streamlit page for scanning and analyzing Dropbox files and folders.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List, Union
import os
from pathlib import Path
import json
import time

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.sidebar import render_database_sidebar
from science_data_kit.ui.components.dropbox_progress import get_progress_tracker, DropboxProgressDisplay
from science_data_kit.core.db.db_manager import db_manager
from science_data_kit.core.models.file_models import Folder, File

from science_data_kit_extensions.dropbox.connector import DropboxConnector
from science_data_kit_extensions.dropbox.files import DropboxFileManager


class DropboxSurveyPage(BasePage):
    """
    Dropbox Survey page for scanning and analyzing Dropbox files and folders.

    This page provides functionality for:
    - Browsing Dropbox files and folders
    - Scanning Dropbox directories
    - Viewing scan results
    - Labeling entities
    - Pushing data to Neo4j
    """

    def __init__(self):
        """Initialize the Dropbox Survey page."""
        super().__init__("Dropbox Survey", "☁️")
        self._setup_sidebar()
        self.db_manager = db_manager
        self.progress_tracker = get_progress_tracker()

        # Initialize session state variables
        if "dropbox_folder_path" not in st.session_state:
            st.session_state["dropbox_folder_path"] = ""

        if "dropbox_scan_results" not in st.session_state:
            st.session_state["dropbox_scan_results"] = None

        if "dropbox_selected_files" not in st.session_state:
            st.session_state["dropbox_selected_files"] = []

        if "dropbox_entity_labels" not in st.session_state:
            st.session_state["dropbox_entity_labels"] = {}

        if "dropbox_scan_completed" not in st.session_state:
            st.session_state["dropbox_scan_completed"] = False

        if "dropbox_scanned_files" not in st.session_state:
            st.session_state["dropbox_scanned_files"] = pd.DataFrame()

        if "dropbox_directory_label" not in st.session_state:
            st.session_state["dropbox_directory_label"] = "Folder"

        if "dropbox_file_label" not in st.session_state:
            st.session_state["dropbox_file_label"] = "File"

    def _setup_sidebar(self):
        """Set up the sidebar items for the Dropbox Survey page."""
        self.add_sidebar_item(
            render_database_sidebar,
            on_connect=self._on_database_connect,
            on_disconnect=self._on_database_disconnect
        )

    def _on_database_connect(self, uri: str, username: str, password: str, database: str, conn_name: str = None):
        """
        Handle database connection.

        Args:
            uri: The URI of the Neo4j server.
            username: The username for authentication.
            password: The password for authentication.
            database: The name of the database to connect to.
            conn_name: Optional name for the connection.
        """
        try:
            # Update connection details
            self.db_manager.uri = uri
            self.db_manager.user = username
            self.db_manager.password = password
            self.db_manager.database = database

            # Connect to the database with the specified connection name
            connection_successful = self.db_manager._connect(conn_name)

            if not connection_successful:
                error_msg = self.db_manager._connection_error or "Unknown connection error"
                st.error(f"Failed to connect to Neo4j: {error_msg}")
                return

            # Update session state
            st.session_state["connected"] = True
            st.session_state["neo4j_uri"] = uri
            st.session_state["neo4j_user"] = username
            st.session_state["neo4j_password"] = password
            st.session_state["neo4j_database"] = database
            st.session_state["active_connection"] = conn_name

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

    def _scan_dropbox_directory(self, folder_path: str) -> pd.DataFrame:
        """
        Scan a Dropbox directory and return the results as a DataFrame.

        Args:
            folder_path: The path to the Dropbox directory to scan.

        Returns:
            A DataFrame containing the scan results.
        """
        results = []

        # Check if connected to Dropbox
        if "dropbox_connector" not in st.session_state:
            st.error("Not connected to Dropbox. Please connect first.")
            return pd.DataFrame()

        connector = st.session_state["dropbox_connector"]
        if not connector.is_connected():
            st.error("Dropbox connection lost. Please reconnect.")
            return pd.DataFrame()

        # Initialize file manager
        file_manager = DropboxFileManager(connector)

        try:
            # Start progress tracking
            operation_id = self.progress_tracker.start_operation(
                "scan",
                folder_path if folder_path else "Dropbox root"
            )
            self.progress_tracker.add_message(f"Scanning Dropbox directory: {folder_path if folder_path else 'root'}")

            # List all files and folders recursively
            items = self._list_recursively(file_manager, folder_path)

            # Update progress
            self.progress_tracker.update_operation(operation_id, len(items))
            self.progress_tracker.add_message(f"Found {len(items)} items in Dropbox")

            # Process items
            for i, item in enumerate(items):
                # Update progress periodically
                if i % 10 == 0:
                    self.progress_tracker.update_operation(operation_id, i)

                if item["type"] == "folder":
                    results.append({
                        "type": "Folder",
                        "name": item["name"],
                        "path": item["path"],
                        "size": 0,
                        "parent": os.path.dirname(item["path"]) if item["path"] != "" else ""
                    })
                else:
                    results.append({
                        "type": "File",
                        "name": item["name"],
                        "path": item["path"],
                        "size": item["size"],
                        "parent": os.path.dirname(item["path"])
                    })

            # Complete progress tracking
            self.progress_tracker.complete_operation(operation_id, True)
            self.progress_tracker.add_message(f"Scan completed: {len(results)} items processed")

            return pd.DataFrame(results)
        except Exception as e:
            # Complete progress tracking with error
            if 'operation_id' in locals():
                self.progress_tracker.complete_operation(operation_id, False)
            self.progress_tracker.add_message(f"Error scanning Dropbox directory: {e}")
            st.error(f"Error scanning Dropbox directory: {e}")
            return pd.DataFrame()

    def _list_recursively(self, file_manager: DropboxFileManager, path: str = "") -> List[Dict[str, Any]]:
        """
        List all files and folders in a Dropbox directory recursively.

        Args:
            file_manager: DropboxFileManager instance
            path: Path to the directory to list

        Returns:
            List of dictionaries with file and folder information
        """
        all_items = []

        # List items in the current directory
        items = file_manager.list_folder(path)

        # Add items to the result
        all_items.extend(items)

        # Recursively list subdirectories
        for item in items:
            if item["type"] == "folder":
                sub_items = self._list_recursively(file_manager, item["path"])
                all_items.extend(sub_items)

        return all_items

    def _push_to_neo4j(self, scan_results: pd.DataFrame) -> bool:
        """
        Push scan results to Neo4j.

        Args:
            scan_results: DataFrame containing scan results.

        Returns:
            True if successful, False otherwise.
        """
        # Check if we're connected to Neo4j
        if not st.session_state.get("connected", False):
            st.error("Not connected to Neo4j. Please connect first.")
            return False

        # Ensure the db_manager is connected
        if not self.db_manager.is_connected():
            try:
                # Try to reconnect using the session state connection details
                self.db_manager.uri = st.session_state.get("neo4j_uri", "bolt://localhost:7687")
                self.db_manager.user = st.session_state.get("neo4j_user", "neo4j")
                self.db_manager.password = st.session_state.get("neo4j_password", "password")
                self.db_manager.database = st.session_state.get("neo4j_database", "neo4j")
                active_connection = st.session_state.get("active_connection")
                connection_successful = self.db_manager._connect(active_connection)

                if not connection_successful:
                    st.error("Failed to connect to Neo4j. Please check your connection details.")
                    return False
            except Exception as e:
                st.error(f"Error connecting to Neo4j: {e}")
                return False

        try:
            # Start progress tracking
            operation_id = self.progress_tracker.start_operation(
                "database push",
                "Dropbox data"
            )
            self.progress_tracker.add_message("Pushing Dropbox data to Neo4j")

            # Progress bar
            bar_total = len(scan_results)
            my_bar = st.progress(0., text="Pushing Dropbox data to Neo4j...")

            # Process folders first
            folders = scan_results[scan_results["type"] == "Folder"]
            for i, (_, row) in enumerate(folders.iterrows()):
                # Update progress
                progress_ratio = (float(i) / bar_total)
                if progress_ratio > 1:
                    progress_ratio = 1
                if progress_ratio < 0:
                    progress_ratio = 0
                my_bar.progress(progress_ratio, f"Processing folders: {int(100 * progress_ratio)}%")
                self.progress_tracker.update_operation(operation_id, i)

                # Check if folder exists
                folder_query = "MATCH (f:Folder {filepath: $filepath}) RETURN f LIMIT 1"
                folder_result = self.db_manager.execute_query(folder_query, {"filepath": row["path"]})

                # Create folder if it doesn't exist
                if not folder_result:
                    create_folder_query = "CREATE (f:Folder {filepath: $filepath, source: 'Dropbox'}) RETURN f"
                    self.db_manager.execute_query(create_folder_query, {"filepath": row["path"]})

                # Create parent relationship if not root
                if row["parent"] != row["path"] and row["parent"] != "":
                    # Check if parent folder exists
                    parent_query = "MATCH (f:Folder {filepath: $filepath}) RETURN f LIMIT 1"
                    parent_result = self.db_manager.execute_query(parent_query, {"filepath": row["parent"]})

                    # Create parent folder if it doesn't exist
                    if not parent_result:
                        create_parent_query = "CREATE (f:Folder {filepath: $filepath, source: 'Dropbox'}) RETURN f"
                        self.db_manager.execute_query(create_parent_query, {"filepath": row["parent"]})

                    # Create relationship
                    relate_query = """
                    MATCH (child:Folder {filepath: $child_path})
                    MATCH (parent:Folder {filepath: $parent_path})
                    MERGE (child)-[:IS_IN]->(parent)
                    """
                    self.db_manager.execute_query(relate_query, {
                        "child_path": row["path"],
                        "parent_path": row["parent"]
                    })

            # Process files
            files = scan_results[scan_results["type"] == "File"]
            for i, (_, row) in enumerate(files.iterrows()):
                # Update progress
                progress_ratio = (float(len(folders) + i) / bar_total)
                if progress_ratio > 1:
                    progress_ratio = 1
                if progress_ratio < 0:
                    progress_ratio = 0
                my_bar.progress(progress_ratio, f"Processing files: {int(100 * progress_ratio)}%")
                self.progress_tracker.update_operation(operation_id, len(folders) + i)

                # Check if file exists
                file_query = "MATCH (f:File {filepath: $filepath}) RETURN f LIMIT 1"
                file_result = self.db_manager.execute_query(file_query, {"filepath": row["path"]})

                # Create file if it doesn't exist
                if not file_result:
                    create_file_query = "CREATE (f:File {filepath: $filepath, size: $size, source: 'Dropbox'}) RETURN f"
                    self.db_manager.execute_query(create_file_query, {"filepath": row["path"], "size": row["size"]})

                # Check if parent folder exists
                parent_query = "MATCH (f:Folder {filepath: $filepath}) RETURN f LIMIT 1"
                parent_result = self.db_manager.execute_query(parent_query, {"filepath": row["parent"]})

                # Create parent folder if it doesn't exist
                if not parent_result:
                    create_parent_query = "CREATE (f:Folder {filepath: $filepath, source: 'Dropbox'}) RETURN f"
                    self.db_manager.execute_query(create_parent_query, {"filepath": row["parent"]})

                # Create relationship
                relate_query = """
                MATCH (child:File {filepath: $child_path})
                MATCH (parent:Folder {filepath: $parent_path})
                MERGE (child)-[:IS_IN]->(parent)
                """
                self.db_manager.execute_query(relate_query, {
                    "child_path": row["path"],
                    "parent_path": row["parent"]
                })

            # Apply entity labels if any
            for path, labels in st.session_state["dropbox_entity_labels"].items():
                for label in labels:
                    # Add label to node
                    query = """
                    MATCH (n {filepath: $path})
                    SET n:`{label}`
                    """.format(label=label)
                    self.db_manager.execute_query(query, {"path": path})

            # Complete progress tracking
            self.progress_tracker.complete_operation(operation_id, True)
            self.progress_tracker.add_message(f"Database push completed: {len(scan_results)} items processed")

            return True
        except Exception as e:
            # Complete progress tracking with error
            if 'operation_id' in locals():
                self.progress_tracker.complete_operation(operation_id, False)
            self.progress_tracker.add_message(f"Error pushing to Neo4j: {e}")
            st.error(f"Error pushing to Neo4j: {e}")
            return False

    def _prepare_for_map_page(self) -> None:
        """
        Prepare Dropbox scan results for use in the Map page.

        This function adds a Label column to the dropbox_scanned_files DataFrame based on the Type column
        and user-specified labels, and sets the necessary session state variables for the Map page.
        """
        if st.session_state["dropbox_scanned_files"].empty:
            st.error("No scan results available. Please run a scan first.")
            return

        # Store the necessary data in session state for the map page
        st.session_state["entities_df"] = st.session_state["dropbox_scanned_files"]
        st.session_state["file_uploaded"] = "Dropbox Survey Scan Results"

        # Add label column based on the Type column and user-specified labels
        st.session_state["entities_df"]["Label"] = st.session_state["entities_df"]["type"].apply(
            lambda x: st.session_state["dropbox_directory_label"] if x == "Folder" else st.session_state["dropbox_file_label"]
        )

        # Set the label column for the map page
        st.session_state["label_column"] = "Label"

    def render_content(self) -> None:
        """Render the Dropbox Survey page content."""
        st.write("Scan and analyze your Dropbox files and folders.")

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

        # Dropbox Scan section
        with st.expander("Scan Your Dropbox", expanded=True):
            # Create two columns layout
            col1, col2 = st.columns(2)

            # Right column for instructions
            with col2:
                st.markdown(
                    """
                    ## Scan Your Dropbox
                    1. **Locate your dataset** - Enter the Dropbox folder path.
                    2. **Run the scan** - Click the scan button to start scanning.
                    3. **View results directly in Streamlit** after scan completion.
                    """
                )

            # Left column for functionality
            with col1:
                # Folder selection
                st.subheader("Step 1: Select Dropbox Folder")

                folder_path = st.text_input(
                    "Enter Dropbox folder path to scan (leave empty for root):", 
                    value=st.session_state["dropbox_folder_path"]
                )
                st.session_state["dropbox_folder_path"] = folder_path

                # Run scan button
                if st.button("Scan Dropbox Folder", use_container_width=True):
                    with st.spinner("Scanning Dropbox folder..."):
                        scan_results = self._scan_dropbox_directory(folder_path)
                        st.session_state["dropbox_scan_results"] = scan_results
                        st.session_state["dropbox_scanned_files"] = scan_results
                        st.session_state["dropbox_scan_completed"] = True

                        if not scan_results.empty:
                            st.success(f"Found {len(scan_results)} items")
                        else:
                            st.warning("No items found")

        # Progress indicators
        with st.expander("Operation Progress", expanded=True):
            # Create progress display
            display = DropboxProgressDisplay(self.progress_tracker)
            
            # Render active operations
            display.render_active_operations()
            
            # Render completed operations
            display.render_completed_operations()
            
            # Render messages
            display.render_messages()
            
            # Add a button to clear completed operations
            if self.progress_tracker.get_completed_operations():
                if st.button("Clear Completed Operations"):
                    self.progress_tracker.clear_completed_operations()
                    st.experimental_rerun()

        # Display scan results
        if st.session_state["dropbox_scan_completed"] and not st.session_state["dropbox_scanned_files"].empty:
            with st.expander("View Scan Results", expanded=True):
                # Create two columns layout
                result_col1, result_col2 = st.columns(2)

                with result_col1:
                    st.subheader("Step 2: View Results")
                    st.write("Scanned Files Preview:")

                    # Handle large dataframes that might cause MessageSizeError
                    try:
                        # Try to display the full dataframe
                        st.dataframe(st.session_state["dropbox_scanned_files"])
                    except Exception as e:
                        if "MessageSizeError" in str(e) or "exceeds the message size limit" in str(e):
                            # If the dataframe is too large, show an abbreviated version
                            st.warning("The scan results are too large to display in full. Showing abbreviated version.")

                            # Create an abbreviated dataframe (first 1000 rows)
                            abbreviated_df = st.session_state["dropbox_scanned_files"].head(1000)
                            st.dataframe(abbreviated_df)

                            st.info("Download the complete results using the 'Download Results as CSV' button below.")
                        else:
                            # If it's a different error, show it
                            st.error(f"Error displaying results: {e}")

                with result_col2:
                    st.subheader("Entity Labeling")

                    # Add entity labeling options
                    st.markdown("""
                    ### Specify Entity Labels
                    Define how entities should be labeled when used in the map page.
                    """)

                    # Default label for directories
                    dir_label = st.text_input("Directory Label:", value=st.session_state["dropbox_directory_label"])
                    if dir_label:
                        st.session_state["dropbox_directory_label"] = dir_label

                    # Default label for files
                    file_label = st.text_input("File Label:", value=st.session_state["dropbox_file_label"])
                    if file_label:
                        st.session_state["dropbox_file_label"] = file_label

                    # Add a button to send to map page
                    st.markdown("### Send to Map Page")
                    if st.button("Use in Map Page", use_container_width=True):
                        self._prepare_for_map_page()
                        # Success message with instructions
                        st.success("Data prepared for Map page! Go to the Map page to continue.")
                        # Add a link to the map page
                        st.markdown("[Go to Map Page](/map)")

                    # Add download option
                    if st.button("Download Results as CSV", use_container_width=True):
                        try:
                            # Try to convert the dataframe to CSV and create a download button
                            csv_data = st.session_state["dropbox_scanned_files"].to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name="dropbox_scan_results.csv",
                                mime="text/csv",
                            )
                        except Exception as e:
                            if "MessageSizeError" in str(e) or "exceeds the message size limit" in str(e):
                                # If the CSV data is too large, suggest alternative approaches
                                st.warning("The scan results are too large to download directly. Consider these alternatives:")
                                st.info("""
                                1. Filter the data to reduce its size before downloading
                                2. Export in smaller batches
                                3. Use the database export functionality for very large datasets
                                """)
                            else:
                                # If it's a different error, show it
                                st.error(f"Error preparing download: {e}")

            # Database push functionality
            with st.expander("Push Data to Database", expanded=True):
                # Create two columns layout
                db_col1, db_col2 = st.columns(2)

                # Right column for instructions
                with db_col2:
                    st.markdown(
                        """
                        ## Push Data to Neo4j
                        1. **Choose what to include** - Select whether to include files or just directories.
                        2. **Push to database** - Click the button to start the process.
                        3. **Monitor progress** - Watch the progress bar as data is pushed to Neo4j.

                        This process will create nodes for each directory and optionally for each file,
                        establishing relationships between them to represent the Dropbox filesystem hierarchy.
                        """
                    )

                # Left column for push functionality
                with db_col1:
                    st.subheader("Step 3: Pushing Data to Neo4j")

                    include_files = st.checkbox("Include Files", value=True)
                    st.write("Total items to push:", len(st.session_state["dropbox_scanned_files"]))

                    if st.button("Push to Database"):
                        if not st.session_state.get("connected", False):
                            st.error("Not connected to Neo4j. Please connect first.")
                        else:
                            with st.spinner("Pushing to Neo4j..."):
                                # Filter out files if not including them
                                if not include_files:
                                    scan_results = st.session_state["dropbox_scanned_files"][
                                        st.session_state["dropbox_scanned_files"]["type"] == "Folder"
                                    ]
                                else:
                                    scan_results = st.session_state["dropbox_scanned_files"]

                                success = self._push_to_neo4j(scan_results)
                                if success:
                                    st.success("Data successfully pushed to Neo4j!")
                                else:
                                    st.error("Failed to push data to Neo4j")


def render_dropbox_survey_page():
    """Render the Dropbox Survey page."""
    page = DropboxSurveyPage()
    page.render()


if __name__ == "__main__":
    render_dropbox_survey_page()