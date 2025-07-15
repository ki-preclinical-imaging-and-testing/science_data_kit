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
import subprocess
import json

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

        if "ncdu_json_path" not in st.session_state:
            st.session_state["ncdu_json_path"] = str(Path.home() / "ncdu_scan.json")

        if "scan_completed" not in st.session_state:
            st.session_state["scan_completed"] = False

        if "ncdu_output" not in st.session_state:
            st.session_state["ncdu_output"] = ""

        if "scanned_files" not in st.session_state:
            st.session_state["scanned_files"] = pd.DataFrame()

        if "directory_label" not in st.session_state:
            st.session_state["directory_label"] = "Folder"

        if "file_label" not in st.session_state:
            st.session_state["file_label"] = "File"

    def _setup_sidebar(self):
        """Set up the sidebar items for the Survey page."""
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

    def _run_ncdu_scan(self, folder_path: str, output_json_path: str) -> bool:
        """
        Run an NCDU (NCurses Disk Usage) scan on the specified folder.

        Args:
            folder_path: The path to the directory to scan.
            output_json_path: The path where the JSON output will be saved.

        Returns:
            True if the scan was successful, False otherwise.
        """
        if not folder_path:
            st.error("Please select a folder first.")
            return False

        st.session_state["scan_completed"] = False
        st.session_state["ncdu_output"] = ""

        # Create a placeholder for live output
        status_box = st.empty()

        try:
            # Run NCDU command
            with subprocess.Popen(
                ["ncdu", "-o", output_json_path, folder_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            ) as process:
                # Capture and display live output
                for line in process.stdout:
                    st.session_state["ncdu_output"] += line
                    status_box.text_area("Live Output", st.session_state["ncdu_output"], height=300)

            # Check if JSON was created
            if Path(output_json_path).exists():
                st.success(f"Scan complete! Results saved to `{output_json_path}`")
                st.session_state["scan_completed"] = True

                # Run jq transformation
                jq_filter = 'def c: (arrays | .[0] + {children: [.[1:][] | c]}) // .; last | c'
                result = subprocess.run(
                    ["jq", jq_filter, output_json_path],
                    text=True,
                    capture_output=True,
                    check=True
                )

                # Load transformed JSON
                scan_data = json.loads(result.stdout)

                # Parse NCDU JSON
                parsed_files = self._parse_ncdu_json(scan_data)
                st.session_state["scanned_files"] = pd.DataFrame(parsed_files)

                return True
        except Exception as e:
            st.error(f"An error occurred while running NCDU: {e}")
            return False

        return False

    def _parse_ncdu_json(self, node, parent_path=""):
        """
        Recursively parse NCDU JSON data to extract file and directory information.

        Args:
            node: A node in the NCDU JSON structure, representing a file or directory.
            parent_path: The path of the parent directory.

        Returns:
            A list of dictionaries, each containing information about a file or directory.
        """
        path = f"{parent_path}/{node['name']}" if parent_path else node["name"]
        file_info = {
            "Path": path,
            "Size (Bytes)": node.get("asize", 0),
            "Disk Usage (Bytes)": node.get("dsize", 0),
            "Type": "Directory" if "children" in node else "File"
        }
        parsed_files = [file_info]
        if "children" in node:
            for child in node["children"]:
                parsed_files.extend(self._parse_ncdu_json(child, path))
        return parsed_files

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
            # Process folders first
            folders = scan_results[scan_results["type"] == "Folder"]
            for _, row in folders.iterrows():
                # Check if folder exists
                folder_query = "MATCH (f:Folder {filepath: $filepath}) RETURN f LIMIT 1"
                folder_result = self.db_manager.execute_query(folder_query, {"filepath": row["path"]})

                # Create folder if it doesn't exist
                if not folder_result:
                    create_folder_query = "CREATE (f:Folder {filepath: $filepath}) RETURN f"
                    self.db_manager.execute_query(create_folder_query, {"filepath": row["path"]})

                # Create parent relationship if not root
                if row["parent"] != row["path"]:
                    # Check if parent folder exists
                    parent_query = "MATCH (f:Folder {filepath: $filepath}) RETURN f LIMIT 1"
                    parent_result = self.db_manager.execute_query(parent_query, {"filepath": row["parent"]})

                    # Create parent folder if it doesn't exist
                    if not parent_result:
                        create_parent_query = "CREATE (f:Folder {filepath: $filepath}) RETURN f"
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
            for _, row in files.iterrows():
                # Check if file exists
                file_query = "MATCH (f:File {filepath: $filepath}) RETURN f LIMIT 1"
                file_result = self.db_manager.execute_query(file_query, {"filepath": row["path"]})

                # Create file if it doesn't exist
                if not file_result:
                    create_file_query = "CREATE (f:File {filepath: $filepath}) RETURN f"
                    self.db_manager.execute_query(create_file_query, {"filepath": row["path"]})

                # Check if parent folder exists
                parent_query = "MATCH (f:Folder {filepath: $filepath}) RETURN f LIMIT 1"
                parent_result = self.db_manager.execute_query(parent_query, {"filepath": row["parent"]})

                # Create parent folder if it doesn't exist
                if not parent_result:
                    create_parent_query = "CREATE (f:Folder {filepath: $filepath}) RETURN f"
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
            for path, labels in st.session_state["entity_labels"].items():
                for label in labels:
                    # Add label to node
                    query = """
                    MATCH (n {filepath: $path})
                    SET n:`{label}`
                    """.format(label=label)
                    self.db_manager.execute_query(query, {"path": path})

            return True
        except Exception as e:
            st.error(f"Error pushing to Neo4j: {e}")
            return False

    def _push_ncdu_results_to_neo4j(self, include_files: bool = False) -> bool:
        """
        Push NCDU scan results to Neo4j.

        Args:
            include_files: Whether to include files in the push (True) or just directories (False).

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

        if st.session_state["scanned_files"].empty:
            st.error("No scan results available. Please run a scan first.")
            return False

        try:
            # Progress bar
            bar_total = len(st.session_state["scanned_files"])
            my_bar = st.progress(0., text="Pushing Filetrees to Database...")

            # Process each row
            for i, row in st.session_state["scanned_files"].iterrows():
                # Update progress bar
                progress_ratio = (float(i)/bar_total)
                if progress_ratio > 1:
                    progress_ratio = 1
                if progress_ratio < 0:
                    progress_ratio = 0
                my_bar.progress(progress_ratio, f"{int(100*progress_ratio)}%")

                path = Path(row["Path"]).as_posix()
                size = row["Size (Bytes)"]
                disk_usage = row["Disk Usage (Bytes)"]
                parent_path = Path(path).parent.as_posix()

                try:
                    # Use execute_query instead of direct session access to ensure proper authentication
                    # Check if parent folder exists
                    parent_query = "MATCH (f:Folder {filepath: $filepath}) RETURN f LIMIT 1"
                    parent_result = self.db_manager.execute_query(parent_query, {"filepath": parent_path})

                    # Create parent folder if it doesn't exist
                    if not parent_result:
                        create_parent_query = "CREATE (f:Folder {filepath: $filepath}) RETURN f"
                        self.db_manager.execute_query(create_parent_query, {"filepath": parent_path})

                    # For directories, create the folder node if it doesn't exist
                    if row["Type"] == "Directory":
                        # Check if folder exists
                        folder_query = "MATCH (f:Folder {filepath: $filepath}) RETURN f LIMIT 1"
                        folder_result = self.db_manager.execute_query(folder_query, {"filepath": path})

                        # Create folder if it doesn't exist
                        if not folder_result:
                            create_folder_query = "CREATE (f:Folder {filepath: $filepath}) RETURN f"
                            self.db_manager.execute_query(create_folder_query, {"filepath": path})

                            # Create relationship to parent
                            relate_query = """
                            MATCH (child:Folder {filepath: $child_path})
                            MATCH (parent:Folder {filepath: $parent_path})
                            CREATE (child)-[:IS_IN]->(parent)
                            """
                            self.db_manager.execute_query(relate_query, {
                                "child_path": path,
                                "parent_path": parent_path
                            })

                    # For files, create the file node if include_files is True
                    if include_files and row["Type"] == "File":
                        # Check if file exists
                        file_query = "MATCH (f:File {filepath: $filepath}) RETURN f LIMIT 1"
                        file_result = self.db_manager.execute_query(file_query, {"filepath": path})

                        # Create file if it doesn't exist
                        if not file_result:
                            create_file_query = "CREATE (f:File {filepath: $filepath}) RETURN f"
                            self.db_manager.execute_query(create_file_query, {"filepath": path})

                            # Create relationship to parent
                            relate_query = """
                            MATCH (child:File {filepath: $child_path})
                            MATCH (parent:Folder {filepath: $parent_path})
                            CREATE (child)-[:IS_IN]->(parent)
                            """
                            self.db_manager.execute_query(relate_query, {
                                "child_path": path,
                                "parent_path": parent_path
                            })
                except Exception as e:
                    st.error(f"Error processing {path}: {e}")
                    raise

            return True
        except Exception as e:
            st.error(f"Error pushing NCDU results to Neo4j: {e}")
            return False

    def _prepare_for_map_page(self) -> None:
        """
        Prepare NCDU scan results for use in the Map page.

        This function adds a Label column to the scanned_files DataFrame based on the Type column
        and user-specified labels, and sets the necessary session state variables for the Map page.
        """
        if st.session_state["scanned_files"].empty:
            st.error("No scan results available. Please run a scan first.")
            return

        # Store the necessary data in session state for the map page
        st.session_state["entities_df"] = st.session_state["scanned_files"]
        st.session_state["file_uploaded"] = "Survey Scan Results"

        # Add label column based on the Type column and user-specified labels
        st.session_state["entities_df"]["Label"] = st.session_state["entities_df"]["Type"].apply(
            lambda x: st.session_state["directory_label"] if x == "Directory" else st.session_state["file_label"]
        )

        # Set the label column for the map page
        st.session_state["label_column"] = "Label"

    def render_content(self) -> None:
        """Render the Survey page content."""
        st.write("Scan and analyze your file systems.")

        # NCDU Scan section
        with st.expander("Scan Your FileTree", expanded=True):
            # Create two columns layout
            col1, col2 = st.columns(2)

            # Right column for instructions
            with col2:
                st.markdown(
                    """
                    ## Scan Your FileTree
                    1. **Locate your dataset** - Enter the directory path manually.
                    2. **Customize output location** - Choose where to save the JSON scan.
                    3. **View results directly in Streamlit** after scan completion.
                    """
                )

            # Left column for functionality
            with col1:
                # Folder selection
                st.subheader("Step 1: Select Dataset Location")

                folder_path = st.text_input(
                    "Enter folder path to scan:", 
                    value=st.session_state["folder_path"]
                )
                if folder_path:
                    st.session_state["folder_path"] = folder_path

                # Verify folder
                if st.session_state["folder_path"]:
                    dataset_path = Path(st.session_state["folder_path"])
                    if dataset_path.exists() and dataset_path.is_dir():
                        st.success(f"Folder Verified: `{dataset_path}`")
                    else:
                        st.error("Invalid folder. Please enter a valid directory path.")

                # JSON save location with simplified interface
                st.subheader("Step 2: Configure Output")

                # Use file browser-like interface
                save_dir = st.text_input("Save Directory:", value=str(Path.home()))
                save_filename = st.text_input("Filename:", value="ncdu_scan.json")

                # Combine directory and filename
                json_save_path = str(Path(save_dir) / save_filename)
                st.session_state["ncdu_json_path"] = json_save_path

                # Show the full path
                st.info(f"Output will be saved to: {json_save_path}")

        # Run Scan section
        with st.expander("Run Filesystem Scan", expanded=True):
            # Create two columns layout
            scan_col1, scan_col2 = st.columns(2)

            # Right column for instructions
            with scan_col2:
                st.markdown(
                    """
                    ## Run Filesystem Scan
                    1. **Verify your settings** - Make sure your folder path and output location are correct.
                    2. **Click the scan button** - This will start the NCDU scan process.
                    3. **Monitor progress** - Watch the live output as the scan progresses.
                    """
                )

            # Left column for scan button and status
            with scan_col1:
                st.subheader("Step 3: Scanning Filesystem with NCDU")

                # Run scan button
                if st.button("Run NCDU Scan", use_container_width=True):
                    if st.session_state["folder_path"]:
                        self._run_ncdu_scan(
                            st.session_state["folder_path"],
                            st.session_state["ncdu_json_path"]
                        )
                    else:
                        st.error("Please enter a folder path first.")

                # Show scan status if available
                if "ncdu_output" in st.session_state and st.session_state["ncdu_output"]:
                    # Use a text area with fixed height for scrollable output
                    try:
                        # Try to display the full output
                        st.text_area("Scan Output", st.session_state["ncdu_output"], height=300)
                    except Exception as e:
                        if "MessageSizeError" in str(e) or "exceeds the message size limit" in str(e):
                            # If the output is too large, show an abbreviated version
                            st.warning("The scan output is too large to display in full. Showing abbreviated version.")

                            # Create an abbreviated output (first 10000 characters)
                            abbreviated_output = st.session_state["ncdu_output"][:10000] + "...\n[Output truncated due to size]"
                            st.text_area("Scan Output (Abbreviated)", abbreviated_output, height=300)
                        else:
                            # If it's a different error, show it
                            st.error(f"Error displaying scan output: {e}")

                # Reset scan button
                if st.session_state["scan_completed"]:
                    if st.button("Reset Scan", use_container_width=True):
                        st.session_state["scan_completed"] = False
                        st.session_state["ncdu_output"] = ""
                        st.rerun()

        # Display NCDU scan results
        if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
            with st.expander("View Scan Results", expanded=True):
                # Create two columns layout
                result_col1, result_col2 = st.columns(2)

                with result_col1:
                    st.subheader("Step 4: View Results")
                    st.write("Scanned Files Preview:")

                    # Handle large dataframes that might cause MessageSizeError
                    try:
                        # Try to display the full dataframe
                        st.dataframe(st.session_state["scanned_files"])
                    except Exception as e:
                        if "MessageSizeError" in str(e) or "exceeds the message size limit" in str(e):
                            # If the dataframe is too large, show an abbreviated version
                            st.warning("The scan results are too large to display in full. Showing abbreviated version.")

                            # Create an abbreviated dataframe (first 1000 rows)
                            abbreviated_df = st.session_state["scanned_files"].head(1000)
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
                    dir_label = st.text_input("Directory Label:", value=st.session_state["directory_label"])
                    if dir_label:
                        st.session_state["directory_label"] = dir_label

                    # Default label for files
                    file_label = st.text_input("File Label:", value=st.session_state["file_label"])
                    if file_label:
                        st.session_state["file_label"] = file_label

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
                            csv_data = st.session_state["scanned_files"].to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name="scan_results.csv",
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
                        establishing relationships between them to represent the filesystem hierarchy.
                        """
                    )

                # Left column for push functionality
                with db_col1:
                    st.subheader("Step 5: Pushing Data to Neo4j")

                    include_files = st.checkbox("Include Files", value=False)
                    st.write("Total items to push:", len(st.session_state["scanned_files"]))

                    if st.button("Push to Database"):
                        if not st.session_state.get("connected", False):
                            st.error("Not connected to Neo4j. Please connect first.")
                        else:
                            with st.spinner("Pushing to Neo4j..."):
                                success = self._push_ncdu_results_to_neo4j(include_files)
                                if success:
                                    st.success("Data successfully pushed to Neo4j!")
                                else:
                                    st.error("Failed to push data to Neo4j")

        # Standard file system browser (alternative to NCDU)
        with st.expander("Standard File System Browser", expanded=False):
            st.header("File System Browser")

            # Directory input
            col1, col2 = st.columns([3, 1])
            with col1:
                folder_path = st.text_input(
                    "Directory Path",
                    value=st.session_state["folder_path"],
                    key="standard_folder_path"
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
                if st.button("Push to Neo4j", key="standard_push"):
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

def render_survey_page():
    """Render the Survey page."""
    page = SurveyPage()
    page.render()
