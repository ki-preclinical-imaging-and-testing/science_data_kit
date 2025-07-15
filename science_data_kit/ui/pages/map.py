"""
Map Page Module for Science Data Kit

This module provides the Map page for the Science Data Kit application.
The Map page handles defining entities and relationships for knowledge graphs.
"""

import streamlit as st
import pandas as pd
import networkx as nx
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from pathlib import Path
import json

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.sidebar import render_database_sidebar
from science_data_kit.core.db.db_manager import db_manager
from science_data_kit.core.models.app_models import merge_nodes_with_existing

class MapPage(BasePage):
    """
    Map page for defining entities and relationships.

    This page provides functionality for:
    - Loading entities from files or database
    - Defining entity structure and properties
    - Creating relationships between entities
    - Building taxonomies and ontologies
    """

    def __init__(self):
        """Initialize the Map page."""
        super().__init__("Map", "🗺️")
        self._setup_sidebar()
        self.db_manager = db_manager

        # Initialize session state variables
        if "entity_data" not in st.session_state:
            st.session_state["entity_data"] = None

        if "relationship_data" not in st.session_state:
            st.session_state["relationship_data"] = None

        if "entity_structure" not in st.session_state:
            st.session_state["entity_structure"] = {}

        if "ontology_data" not in st.session_state:
            st.session_state["ontology_data"] = None

        if "taxonomy_keys" not in st.session_state:
            st.session_state["taxonomy_keys"] = []

        if "taxonomy" not in st.session_state:
            st.session_state["taxonomy"] = None

        if "property_mappings" not in st.session_state:
            st.session_state["property_mappings"] = {}

        if "target_property_mappings" not in st.session_state:
            st.session_state["target_property_mappings"] = {}

        if "original_entity_data" not in st.session_state:
            st.session_state["original_entity_data"] = None

    def _setup_sidebar(self):
        """Set up the sidebar items for the Map page."""
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
            conn_name: The name of the connection (optional).
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

    def _load_entities_from_file(self, uploaded_file, file_path: str = None, file_type: str = None, sheet_name: str = None) -> pd.DataFrame:
        """
        Load entities from a file.

        Args:
            uploaded_file: The uploaded file object.
            file_path: Path to the file if not uploaded.
            file_type: Type of file (CSV, Excel, JSON).
            sheet_name: Name of the sheet for Excel files.

        Returns:
            A DataFrame containing the entities.
        """
        try:
            if uploaded_file:
                # Determine file type from extension
                file_extension = Path(uploaded_file.name).suffix.lower()

                if file_extension == '.csv':
                    df = pd.read_csv(uploaded_file)
                elif file_extension in ['.xlsx', '.xls']:
                    if sheet_name:
                        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                    else:
                        df = pd.read_excel(uploaded_file)
                elif file_extension == '.json':
                    df = pd.DataFrame(json.loads(uploaded_file.getvalue().decode('utf-8')))
                else:
                    st.error(f"Unsupported file type: {file_extension}")
                    return pd.DataFrame()

                return df
            elif file_path:
                # Determine file type from extension or provided type
                if file_type:
                    if file_type == "CSV":
                        df = pd.read_csv(file_path)
                    elif file_type == "Excel":
                        if sheet_name:
                            df = pd.read_excel(file_path, sheet_name=sheet_name)
                        else:
                            df = pd.read_excel(file_path)
                    elif file_type == "JSON":
                        df = pd.read_json(file_path)
                    else:
                        st.error(f"Unsupported file type: {file_type}")
                        return pd.DataFrame()
                else:
                    file_extension = Path(file_path).suffix.lower()
                    if file_extension == '.csv':
                        df = pd.read_csv(file_path)
                    elif file_extension in ['.xlsx', '.xls']:
                        if sheet_name:
                            df = pd.read_excel(file_path, sheet_name=sheet_name)
                        else:
                            df = pd.read_excel(file_path)
                    elif file_extension == '.json':
                        df = pd.read_json(file_path)
                    else:
                        st.error(f"Unsupported file type: {file_extension}")
                        return pd.DataFrame()

                return df
            else:
                st.error("No file provided")
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading entities from file: {e}")
            return pd.DataFrame()

    def _load_entities_from_database(self, label: str) -> pd.DataFrame:
        """
        Load entities from the database.

        Args:
            label: The label of the entities to load.

        Returns:
            A DataFrame containing the entities.
        """
        if not self.db_manager.is_connected():
            st.error("Not connected to Neo4j. Please connect first.")
            return pd.DataFrame()

        try:
            # Get properties for the label
            properties = self.db_manager.fetch_node_properties(label)

            # Fetch nodes with properties
            nodes = self.db_manager.fetch_nodes(label, properties)

            # Convert to DataFrame
            df = pd.DataFrame(nodes)

            return df
        except Exception as e:
            st.error(f"Error loading entities from database: {e}")
            return pd.DataFrame()

    def _load_ncdu_data(self, uploaded_file=None, file_path=None) -> pd.DataFrame:
        """
        Load NCDU scan data from a file.

        Args:
            uploaded_file: The uploaded NCDU JSON file.
            file_path: Path to the NCDU JSON file if not uploaded.

        Returns:
            A DataFrame containing the parsed NCDU data.
        """
        try:
            # Load the JSON file
            if uploaded_file:
                ncdu_data = json.loads(uploaded_file.getvalue().decode('utf-8'))
                file_source = uploaded_file.name
            elif file_path:
                with open(file_path, 'r') as f:
                    ncdu_data = json.load(f)
                file_source = file_path
            else:
                st.error("No NCDU file provided")
                return pd.DataFrame()

            # Parse NCDU JSON
            def parse_ncdu_json(node, parent_path=""):
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
                        parsed_files.extend(parse_ncdu_json(child, path))
                return parsed_files

            # Transform to dataframe
            parsed_files = parse_ncdu_json(ncdu_data)
            df = pd.DataFrame(parsed_files)

            return df
        except Exception as e:
            st.error(f"Error loading NCDU file: {e}")
            return pd.DataFrame()

    def _create_entity_structure(self, entity_data: pd.DataFrame) -> Dict[str, Dict[str, str]]:
        """
        Create entity structure from entity data.

        Args:
            entity_data: DataFrame containing entity data.

        Returns:
            A dictionary mapping property names to property types.
        """
        structure = {}

        for column in entity_data.columns:
            # Skip id column
            if column == 'id':
                continue

            # Determine property type based on column data
            if entity_data[column].dtype == 'int64':
                property_type = 'Integer'
            elif entity_data[column].dtype == 'float64':
                property_type = 'Float'
            elif entity_data[column].dtype == 'bool':
                property_type = 'Boolean'
            elif entity_data[column].dtype == 'datetime64[ns]':
                property_type = 'DateTime'
            else:
                property_type = 'String'

            structure[column] = property_type

        return structure

    def _push_entities_to_neo4j(self, entity_data: pd.DataFrame, label: str, structure: Dict[str, str]) -> bool:
        """
        Push entities to Neo4j.

        Args:
            entity_data: DataFrame containing entity data.
            label: The label to assign to the entities.
            structure: Dictionary mapping property names to property types.

        Returns:
            True if successful, False otherwise.
        """
        if not self.db_manager.is_connected():
            st.error("Not connected to Neo4j. Please connect first.")
            return False

        try:
            # Create a transaction
            with self.db_manager._driver.session(database=self.db_manager.database) as session:
                # Create entities
                for _, row in entity_data.iterrows():
                    # Create property dictionary
                    properties = {}
                    for column in entity_data.columns:
                        if column != 'id' and pd.notna(row[column]):
                            properties[column] = row[column]

                    # Create entity
                    query = f"""
                    CREATE (n:{label} $props)
                    RETURN id(n)
                    """
                    session.run(query, {"props": properties})

            return True
        except Exception as e:
            st.error(f"Error pushing entities to Neo4j: {e}")
            return False

    def _create_relationships(self, source_label: str, target_label: str, relationship_type: str,
                             source_property: str, target_property: str) -> bool:
        """
        Create relationships between entities.

        Args:
            source_label: The label of the source entities.
            target_label: The label of the target entities.
            relationship_type: The type of relationship to create.
            source_property: The property of the source entities to match.
            target_property: The property of the target entities to match.

        Returns:
            True if successful, False otherwise.
        """
        if not self.db_manager.is_connected():
            st.error("Not connected to Neo4j. Please connect first.")
            return False

        try:
            # Create a transaction
            with self.db_manager._driver.session(database=self.db_manager.database) as session:
                # Create relationships
                query = f"""
                MATCH (source:{source_label}), (target:{target_label})
                WHERE source.{source_property} = target.{target_property}
                CREATE (source)-[r:{relationship_type}]->(target)
                RETURN count(r)
                """
                result = session.run(query)
                count = result.single()[0]

            return count > 0
        except Exception as e:
            st.error(f"Error creating relationships: {e}")
            return False

    def _load_ontology(self, uploaded_file) -> Dict[str, Any]:
        """
        Load ontology from a file.

        Args:
            uploaded_file: The uploaded file object.

        Returns:
            A dictionary containing the ontology data.
        """
        try:
            # Determine file type from extension
            file_extension = Path(uploaded_file.name).suffix.lower()

            if file_extension == '.json':
                ontology_data = json.loads(uploaded_file.getvalue().decode('utf-8'))
                return ontology_data
            else:
                st.error(f"Unsupported file type for ontology: {file_extension}")
                return {}
        except Exception as e:
            st.error(f"Error loading ontology from file: {e}")
            return {}

    def _push_ontology_to_neo4j(self, ontology_data: Dict[str, Any]) -> bool:
        """
        Push ontology to Neo4j.

        Args:
            ontology_data: Dictionary containing ontology data.

        Returns:
            True if successful, False otherwise.
        """
        if not self.db_manager.is_connected():
            st.error("Not connected to Neo4j. Please connect first.")
            return False

        try:
            # Create a transaction
            with self.db_manager._driver.session(database=self.db_manager.database) as session:
                # Create ontology terms
                for term_id, term_data in ontology_data.get('terms', {}).items():
                    # Create term node
                    query = """
                    MERGE (t:OntologyTerm {id: $id})
                    SET t.name = $name,
                        t.definition = $definition
                    """
                    session.run(query, {
                        "id": term_id,
                        "name": term_data.get('name', ''),
                        "definition": term_data.get('definition', '')
                    })

                # Create relationships between terms
                for term_id, term_data in ontology_data.get('terms', {}).items():
                    for rel_type, rel_targets in term_data.get('relationships', {}).items():
                        for target_id in rel_targets:
                            # Create relationship
                            query = f"""
                            MATCH (source:OntologyTerm {{id: $source_id}}),
                                  (target:OntologyTerm {{id: $target_id}})
                            MERGE (source)-[r:{rel_type}]->(target)
                            """
                            session.run(query, {
                                "source_id": term_id,
                                "target_id": target_id
                            })

            return True
        except Exception as e:
            st.error(f"Error pushing ontology to Neo4j: {e}")
            return False

    def _create_taxonomy(self, entity_data: pd.DataFrame, taxonomy_keys: List[str]) -> pd.DataFrame:
        """
        Create a taxonomy by grouping entity data by the specified keys.

        Args:
            entity_data: DataFrame containing entity data.
            taxonomy_keys: List of keys to group by.

        Returns:
            A DataFrame containing the taxonomy.
        """
        try:
            if not taxonomy_keys:
                return pd.DataFrame()

            # Group by taxonomy keys and count occurrences
            taxonomy_df = (
                entity_data.groupby(taxonomy_keys)
                .size()
                .reset_index(name="Count")
            )

            return taxonomy_df
        except Exception as e:
            st.error(f"Error creating taxonomy: {e}")
            return pd.DataFrame()

    def _push_taxonomy_to_neo4j(self, taxonomy_df: pd.DataFrame, taxonomy_keys: List[str], 
                               entity_label: str, match_columns: List[str], 
                               relationship_type: str) -> bool:
        """
        Push taxonomy to Neo4j and link to entities.

        Args:
            taxonomy_df: DataFrame containing the taxonomy.
            taxonomy_keys: List of keys that define the taxonomy levels.
            entity_label: Label of the entities to link to.
            match_columns: Columns to use for matching entities.
            relationship_type: Type of relationship to create.

        Returns:
            True if successful, False otherwise.
        """
        if not self.db_manager.is_connected():
            st.error("Not connected to Neo4j. Please connect first.")
            return False

        try:
            with self.db_manager._driver.session(database=self.db_manager.database) as session:
                for _, row in taxonomy_df.iterrows():
                    # Create path ID chain for hierarchical structure
                    path_id_chain = []
                    prev_node_id = None

                    # Create nodes for each taxonomy level
                    for col in taxonomy_keys:
                        instance_value = row[col]
                        path_id_chain.append(str(instance_value))

                        # Create or merge node for this taxonomy level
                        query = f"""
                        MERGE (f:{col} {{is: $instance_value, path_id: $path_id}})
                        RETURN id(f) as node_id
                        """
                        result = session.run(
                            query,
                            instance_value=instance_value,
                            path_id='-'.join(path_id_chain)
                        )
                        current_node_id = result.single()["node_id"]

                        # Create relationship to parent node if not the first level
                        if prev_node_id is not None:
                            session.run(
                                """
                                MATCH (prev), (curr)
                                WHERE id(prev) = $prev_id AND id(curr) = $curr_id
                                MERGE (prev)<-[:OF]-(curr)
                                """,
                                prev_id=prev_node_id,
                                curr_id=current_node_id
                            )

                        prev_node_id = current_node_id

                    # Create match conditions for linking to entities
                    if "target_property_mappings" in st.session_state and st.session_state["target_property_mappings"]:
                        # Map source properties to target properties
                        source_props = [st.session_state["property_mappings"].get(col, col) for col in match_columns]

                        target_props = []
                        for i, col in enumerate(match_columns):
                            source_prop = st.session_state["property_mappings"].get(col, col)
                            target_prop = st.session_state["target_property_mappings"].get(col, source_prop)
                            target_props.append(target_prop)

                        match_conditions = " AND ".join([f"e.{target_prop} = $col_{i}" for i, target_prop in enumerate(target_props)])
                    else:
                        # Use source property names
                        mapped_match_columns = [st.session_state["property_mappings"].get(col, col) for col in match_columns]
                        match_conditions = " AND ".join([f"e.{mapped_col} = $col_{i}" for i, mapped_col in enumerate(mapped_match_columns)])

                    # Create parameters for the match
                    match_params = {}
                    for i, col in enumerate(match_columns):
                        match_params[f"col_{i}"] = row[col]

                    # Link taxonomy node to matching entities
                    entity_query = f"""
                    MATCH (e:{entity_label}) WHERE {match_conditions}
                    MATCH (t) WHERE id(t) = $final_node_id
                    MERGE (t)-[:{relationship_type}]->(e)
                    """
                    session.run(entity_query, final_node_id=prev_node_id, **match_params)

            return True
        except Exception as e:
            st.error(f"Error pushing taxonomy to Neo4j: {e}")
            return False

    def _filter_entity_data(self, entity_data: pd.DataFrame, filter_column: str, 
                           filter_operation: str, filter_value: str) -> pd.DataFrame:
        """
        Filter entity data based on column values.

        Args:
            entity_data: DataFrame containing entity data.
            filter_column: Column to filter on.
            filter_operation: Operation to use for filtering (==, !=, >, <, etc.).
            filter_value: Value to filter by.

        Returns:
            Filtered DataFrame.
        """
        try:
            # Create a copy of the DataFrame
            filtered_df = entity_data.copy()

            # Apply the filter based on the selected operation
            if filter_operation == "==":
                filtered_df = filtered_df[filtered_df[filter_column].astype(str) == filter_value]
            elif filter_operation == "!=":
                filtered_df = filtered_df[filtered_df[filter_column].astype(str) != filter_value]
            elif filter_operation == ">":
                filtered_df = filtered_df[pd.to_numeric(filtered_df[filter_column], errors='coerce') > float(filter_value)]
            elif filter_operation == "<":
                filtered_df = filtered_df[pd.to_numeric(filtered_df[filter_column], errors='coerce') < float(filter_value)]
            elif filter_operation == ">=":
                filtered_df = filtered_df[pd.to_numeric(filtered_df[filter_column], errors='coerce') >= float(filter_value)]
            elif filter_operation == "<=":
                filtered_df = filtered_df[pd.to_numeric(filtered_df[filter_column], errors='coerce') <= float(filter_value)]
            elif filter_operation == "contains":
                filtered_df = filtered_df[filtered_df[filter_column].astype(str).str.contains(filter_value, na=False)]
            elif filter_operation == "starts with":
                filtered_df = filtered_df[filtered_df[filter_column].astype(str).str.startswith(filter_value, na=False)]
            elif filter_operation == "ends with":
                filtered_df = filtered_df[filtered_df[filter_column].astype(str).str.endswith(filter_value, na=False)]

            return filtered_df
        except Exception as e:
            st.error(f"Error filtering data: {e}")
            return entity_data

    def render_content(self) -> None:
        """Render the Map page content."""
        st.write("Define entities and relationships to create knowledge graphs.")

        # Entity management
        with st.expander("Resolve and define node labels", expanded=False):
            # Create two columns layout
            col1, col2 = st.columns(2)

            # Right column for instructions
            with col2:
                st.markdown(
                    """
                    ## Review and Edit Entities
                    1. Load entities from a file or database.
                    2. Select label and properties.
                    3. Review dataset row by row.
                    4. Define relationships and push to the database.
                    """
                )

            # Left column for functionality
            with col1:
                # Data source selection
                data_source = st.radio(
                    "Get entities from:",
                    ["File", "Database", "NCDU Scan"],
                    key="data_source_section1"
                )

                if data_source == "File":
                    # File type selection
                    file_type = st.radio(
                        "File type:",
                        ["CSV", "Excel", "JSON"],
                        key="file_type_section1"
                    )

                    if file_type in ["CSV", "JSON"]:
                        # File uploader for CSV or JSON
                        file_types = {"CSV": ["csv"], "JSON": ["json"]}
                        uploaded_file = st.file_uploader(
                            f"Upload {file_type} file:", 
                            type=file_types[file_type], 
                            key=f"file_uploader_section1_{file_type}"
                        )
                        file_path = st.text_input(f"Or enter {file_type} file path:")

                        if st.button("Load File") and file_path:
                            try:
                                entity_data = self._load_entities_from_file(None, file_path, file_type)
                                st.session_state["entity_data"] = entity_data
                                st.session_state["original_entity_data"] = entity_data.copy()
                                st.session_state["file_uploaded"] = file_path
                            except Exception as e:
                                st.error(f"Error loading file: {e}")

                        if uploaded_file:
                            try:
                                entity_data = self._load_entities_from_file(uploaded_file)
                                st.session_state["entity_data"] = entity_data
                                st.session_state["original_entity_data"] = entity_data.copy()
                                st.session_state["file_uploaded"] = uploaded_file.name
                            except Exception as e:
                                st.error(f"Error loading file: {e}")

                    elif file_type == "Excel":
                        # Excel file handling with sheet selection
                        uploaded_excel = st.file_uploader(
                            "Upload Excel file:", 
                            type=["xlsx", "xls"], 
                            key="excel_uploader_section1"
                        )
                        excel_path = st.text_input("Or enter Excel file path:")

                        excel_file = uploaded_excel if uploaded_excel else (excel_path if excel_path else None)

                        if excel_file:
                            try:
                                if isinstance(excel_file, str):  # Path provided
                                    xls = pd.ExcelFile(excel_path)
                                else:  # File uploaded
                                    xls = pd.ExcelFile(excel_file)

                                sheet_names = xls.sheet_names
                                selected_sheet = st.selectbox("Select sheet:", options=sheet_names)

                                if st.button("Load Sheet"):
                                    if isinstance(excel_file, str):  # Path provided
                                        entity_data = self._load_entities_from_file(None, excel_path, "Excel", selected_sheet)
                                        st.session_state["entity_data"] = entity_data
                                        st.session_state["original_entity_data"] = entity_data.copy()
                                        st.session_state["file_uploaded"] = f"{excel_path} (Sheet: {selected_sheet})"
                                    else:  # File uploaded
                                        entity_data = self._load_entities_from_file(excel_file, sheet_name=selected_sheet)
                                        st.session_state["entity_data"] = entity_data
                                        st.session_state["original_entity_data"] = entity_data.copy()
                                        st.session_state["file_uploaded"] = f"{uploaded_excel.name} (Sheet: {selected_sheet})"
                            except Exception as e:
                                st.error(f"Error loading Excel file: {e}")

                elif data_source == "Database":
                    # Database entity loading
                    if st.session_state.get("connected", False):
                        # Get available labels
                        labels = self.db_manager.fetch_labels()
                        entity_label = st.selectbox("Select Node Label:", labels)

                        if entity_label and st.button("Pull Entities from Database"):
                            try:
                                entity_data = self._load_entities_from_database(entity_label)
                                st.session_state["entity_data"] = entity_data
                                st.session_state["original_entity_data"] = entity_data.copy()
                                st.session_state["file_uploaded"] = f"Database: {entity_label} nodes"
                                st.success(f"Loaded {len(entity_data)} entities from database")
                            except Exception as e:
                                st.error(f"Error loading entities from database: {e}")
                    else:
                        st.warning("Please connect to a database first")

                elif data_source == "NCDU Scan":
                    # NCDU scan results handling
                    ncdu_source = st.radio(
                        "NCDU source:",
                        ["Survey Page Results", "NCDU JSON File"],
                        key="ncdu_source"
                    )

                    if ncdu_source == "Survey Page Results":
                        if "scanned_files" in st.session_state and not st.session_state["scanned_files"].empty:
                            if st.button("Load Survey Scan Results"):
                                st.session_state["entity_data"] = st.session_state["scanned_files"]
                                st.session_state["original_entity_data"] = st.session_state["scanned_files"].copy()
                                st.session_state["file_uploaded"] = "NCDU Survey Scan Results"
                        else:
                            st.warning("No scan results available. Please run a scan on the Survey page first.")

                    else:  # NCDU JSON File
                        uploaded_ncdu = st.file_uploader("Upload NCDU JSON file:", type=["json"], key="ncdu_uploader")
                        ncdu_path = st.text_input("Or enter NCDU JSON file path:")

                        if st.button("Load NCDU File") and (uploaded_ncdu or ncdu_path):
                            try:
                                entity_data = self._load_ncdu_data(uploaded_ncdu, ncdu_path)
                                st.session_state["entity_data"] = entity_data
                                st.session_state["original_entity_data"] = entity_data.copy()
                                file_source = uploaded_ncdu.name if uploaded_ncdu else ncdu_path
                                st.session_state["file_uploaded"] = f"NCDU: {file_source}"
                            except Exception as e:
                                st.error(f"Error loading NCDU file: {e}")

            # Display the dataframe if loaded
            if st.session_state["entity_data"] is not None:
                st.markdown(f"`{st.session_state.get('file_uploaded', 'Loaded Data')}`")
                st.subheader("Input DataFrame")

                # Display the DataFrame
                try:
                    # Try to display the full dataframe
                    st.dataframe(st.session_state["entity_data"], use_container_width=True)
                except Exception as e:
                    if "MessageSizeError" in str(e) or "exceeds the message size limit" in str(e):
                        # If the dataframe is too large, show an abbreviated version
                        st.warning("The data is too large to display in full. Showing abbreviated version (first 1000 rows).")

                        # Create an abbreviated dataframe
                        abbreviated_df = st.session_state["entity_data"].head(1000)
                        st.dataframe(abbreviated_df, use_container_width=True)

                        # Add download button for the full dataset
                        csv_data = st.session_state["entity_data"].to_csv(index=False)
                        st.download_button(
                            label="Download Full Dataset as CSV",
                            data=csv_data,
                            file_name="entities_data.csv",
                            mime="text/csv",
                        )
                    else:
                        # If it's a different error, show it
                        st.error(f"Error displaying data: {e}")

                # Select label column
                st.subheader("Define Entity Structure")
                label_column = st.selectbox("Select Label Column:",
                                          options=st.session_state["entity_data"].columns,
                                          key="label_column")
                property_columns = st.multiselect("Select Property Columns:",
                                                options=st.session_state["entity_data"].columns,
                                                key="property_columns")

                # Only show property mapping if properties are selected
                if property_columns:
                    st.subheader("Map Property Columns to Neo4j Property Names")
                    st.markdown("Define how selected columns should be named in Neo4j nodes.")

                    # Create a container for the property mappings
                    mapping_container = st.container()

                    with mapping_container:
                        # Create two columns for each property mapping
                        for prop in property_columns:
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.text(f"Column: {prop}")
                            with col2:
                                # Initialize with the original name if not already mapped
                                default_value = st.session_state["property_mappings"].get(prop, prop)
                                new_name = st.text_input(f"Neo4j Property Name for {prop}", 
                                                      value=default_value,
                                                      key=f"mapping_{prop}")
                                # Store the mapping
                                st.session_state["property_mappings"][prop] = new_name

                # Display individual entity view
                if st.session_state["entity_data"] is not None:
                    entity_indices = st.session_state["entity_data"].index.tolist()
                    selected_entity_index = st.selectbox(
                        "Select entity to edit:", 
                        options=entity_indices, 
                        format_func=lambda x: f"{st.session_state['entity_data'].at[x, label_column]}" if label_column else f"Entity {x}"
                    )

                    if selected_entity_index is not None:
                        st.session_state["selected_entity_index"] = selected_entity_index
                        # Get the original entity data
                        selected_entity = st.session_state["entity_data"].iloc[selected_entity_index][property_columns].to_dict()

                        # Create a new dictionary with mapped property names as keys
                        mapped_entity = {}
                        for prop, value in selected_entity.items():
                            mapped_name = st.session_state["property_mappings"].get(prop, prop)
                            mapped_entity[mapped_name] = value

                        # Create DataFrame with mapped property names
                        selected_entity_df = pd.DataFrame(list(mapped_entity.items()), columns=["Key", "Value"])

                        edited_entity_df = st.data_editor(
                            selected_entity_df,
                            key="individual_entity_editor",
                            use_container_width=True,
                            num_rows="dynamic"
                        )

                # Define relationships
                st.subheader("Define Relationships")
                st.markdown("Define relationships to connect your entities to other nodes in the database.")

                # Container for all relationship definitions
                relationship_container = st.container()

                # Initialize relationship definitions in session state if not present
                if "relationship_definitions" not in st.session_state:
                    st.session_state["relationship_definitions"] = []

                # Function to add a new relationship definition
                def add_relationship_definition():
                    st.session_state["relationship_definitions"].append({
                        "id": len(st.session_state["relationship_definitions"]),
                        "label_option": "Existing Label",
                        "target_label": "",
                        "match_columns": [],
                        "target_property_mappings": {},
                        "relationship_type": ""
                    })

                # Function to remove a relationship definition
                def remove_relationship_definition(index):
                    st.session_state["relationship_definitions"].pop(index)

                # Add relationship button
                if st.button("Add Relationship"):
                    add_relationship_definition()

                # If no relationships defined yet, add one by default
                if not st.session_state["relationship_definitions"]:
                    add_relationship_definition()

                # Create a list of property columns with their mapped names for selection
                property_options = []
                if "property_mappings" in st.session_state and st.session_state["property_mappings"]:
                    for col in st.session_state["entity_data"].columns:
                        mapped_name = st.session_state["property_mappings"].get(col, col)
                        if col == mapped_name:
                            property_options.append(f"{col}")
                        else:
                            property_options.append(f"{col} → {mapped_name}")
                else:
                    property_options = list(st.session_state["entity_data"].columns)

                # Display and edit each relationship definition
                for i, rel_def in enumerate(st.session_state["relationship_definitions"]):
                    with relationship_container:
                        st.markdown(f"#### Relationship {i+1}")

                        # Two columns for the relationship header
                        header_col1, header_col2 = st.columns([3, 1])

                        with header_col1:
                            st.markdown(f"Define relationship to {rel_def['target_label'] or 'target nodes'}")

                        with header_col2:
                            if st.button("Remove", key=f"remove_rel_{i}"):
                                remove_relationship_definition(i)
                                st.rerun()

                        # Target Node Label section
                        rel_def["label_option"] = st.radio(
                            "Target Node Label:",
                            ["Existing Label", "New Label"],
                            key=f"label_option_{i}"
                        )

                        if rel_def["label_option"] == "Existing Label":
                            if self.db_manager.is_connected():
                                labels = self.db_manager.fetch_labels()
                                rel_def["target_label"] = st.selectbox(
                                    "Select Target Node Label:",
                                    options=labels,
                                    key=f"target_label_{i}"
                                )
                            else:
                                st.error("Not connected to Neo4j. Please connect first.")
                                rel_def["target_label"] = None
                        else:
                            st.info("A new node label will be created in the database if it doesn't already exist.")
                            rel_def["target_label"] = st.text_input(
                                "New Label Name:",
                                key=f"new_label_{i}"
                            )

                        # Property matching section
                        st.markdown("##### Select Matching Properties")
                        st.markdown("Select properties to match with target nodes. Properties with mapped names show both original and mapped names.")

                        # Initialize match columns for this relationship if not present
                        if "match_columns" not in rel_def or not rel_def["match_columns"]:
                            rel_def["match_columns"] = []

                        # Transform match_columns to match the format of property_options for the default parameter
                        default_options = []
                        for col in rel_def["match_columns"]:
                            # Check if this column has a mapping
                            mapped_name = st.session_state["property_mappings"].get(col, col)
                            if col == mapped_name:
                                # No mapping, use the column name as is
                                if col in property_options:
                                    default_options.append(col)
                            else:
                                # Has mapping, use the format with arrow
                                option_with_arrow = f"{col} → {mapped_name}"
                                if option_with_arrow in property_options:
                                    default_options.append(option_with_arrow)

                        # Select matching properties
                        selected_options = st.multiselect(
                            "Select Matching Properties:",
                            options=property_options,
                            default=default_options,
                            key=f"match_columns_{i}"
                        )

                        # Extract the original column names from the selected options
                        match_columns = []
                        for option in selected_options:
                            if " → " in option:
                                # Extract the original column name (before the arrow)
                                original_col = option.split(" → ")[0]
                                match_columns.append(original_col)
                            else:
                                match_columns.append(option)

                        rel_def["match_columns"] = match_columns

                        # Property mapping section
                        if match_columns:
                            st.markdown("##### Map Properties to Target Node Properties")

                            # Initialize target property mappings for this relationship if not present
                            if "target_property_mappings" not in rel_def:
                                rel_def["target_property_mappings"] = {}

                            # For existing labels, fetch available properties
                            if rel_def["label_option"] == "Existing Label" and rel_def["target_label"]:
                                try:
                                    # Fetch available properties for the selected target label
                                    target_properties = self.db_manager.fetch_node_properties(rel_def["target_label"])

                                    st.markdown(f"Map source properties to existing properties in '{rel_def['target_label']}' nodes")

                                    # Create property mappings
                                    for prop in match_columns:
                                        col1, col2 = st.columns([1, 1])
                                        with col1:
                                            # Show the source property name (with mapped name if applicable)
                                            mapped_name = st.session_state["property_mappings"].get(prop, prop)
                                            if prop == mapped_name:
                                                st.text(f"Source: {prop}")
                                            else:
                                                st.text(f"Source: {prop} → {mapped_name}")
                                        with col2:
                                            # Default to the same property name if it exists in target properties
                                            default_value = rel_def["target_property_mappings"].get(prop, mapped_name)
                                            default_index = target_properties.index(default_value) if default_value in target_properties else 0
                                            target_prop = st.selectbox(
                                                f"Target property for {mapped_name}",
                                                options=target_properties,
                                                index=default_index,
                                                key=f"target_mapping_{i}_{prop}"
                                            )
                                            # Store the mapping
                                            rel_def["target_property_mappings"][prop] = target_prop
                                except Exception as e:
                                    st.error(f"Error fetching properties for {rel_def['target_label']}: {e}")
                            else:
                                # For new labels, provide free text input
                                st.markdown(f"Define property names for the new '{rel_def['target_label']}' nodes")

                                # Create property mappings
                                for prop in match_columns:
                                    col1, col2 = st.columns([1, 1])
                                    with col1:
                                        # Show the source property name (with mapped name if applicable)
                                        mapped_name = st.session_state["property_mappings"].get(prop, prop)
                                        if prop == mapped_name:
                                            st.text(f"Source: {prop}")
                                        else:
                                            st.text(f"Source: {prop} → {mapped_name}")
                                    with col2:
                                        # Default to the same property name
                                        default_value = rel_def["target_property_mappings"].get(prop, mapped_name)
                                        target_prop = st.text_input(
                                            f"Target property name for {mapped_name}",
                                            value=default_value,
                                            key=f"target_mapping_{i}_{prop}"
                                        )
                                        # Store the mapping
                                        rel_def["target_property_mappings"][prop] = target_prop

                        # Relationship type
                        rel_def["relationship_type"] = st.text_input(
                            "Define Relationship Type (e.g., STORED_IN):",
                            value=rel_def.get("relationship_type", ""),
                            key=f"relationship_type_{i}"
                        )

                        # Add a separator between relationships
                        st.markdown("---")

                # Submit to database
                if st.button("Push to Database"):
                    # Validate that we have at least one relationship defined
                    if not st.session_state["relationship_definitions"]:
                        st.error("Please define at least one relationship.")
                        st.stop()

                    # Validate each relationship definition
                    valid = True
                    for i, rel_def in enumerate(st.session_state["relationship_definitions"]):
                        # Validate target label
                        if rel_def["label_option"] == "New Label" and not rel_def["target_label"]:
                            st.error(f"Relationship {i+1}: Please enter a new node label name.")
                            valid = False

                        # Validate relationship type
                        if not rel_def["relationship_type"]:
                            st.error(f"Relationship {i+1}: Please enter a relationship type.")
                            valid = False

                        # Validate matching properties
                        if not rel_def["match_columns"]:
                            st.error(f"Relationship {i+1}: Please select at least one matching property.")
                            valid = False

                    if not valid:
                        st.stop()

                    with st.spinner("Pushing to database..."):
                        try:
                            # Create a copy of the DataFrame with mapped column names
                            mapped_df = st.session_state["entity_data"].copy()

                            # Create a dictionary to map original column names to new column names
                            column_mapping = {}
                            for col in property_columns:
                                new_name = st.session_state["property_mappings"].get(col, col)
                                if new_name != col:
                                    column_mapping[col] = new_name

                            # If there are any mappings, rename the columns in the DataFrame
                            if column_mapping:
                                # First, create new columns with the mapped names
                                for old_name, new_name in column_mapping.items():
                                    mapped_df[new_name] = mapped_df[old_name]

                                # Update property_columns to use the new names
                                mapped_property_columns = [st.session_state["property_mappings"].get(col, col) for col in property_columns]
                            else:
                                # If no mappings, use the original property columns
                                mapped_property_columns = property_columns

                            # Process each relationship definition
                            for i, rel_def in enumerate(st.session_state["relationship_definitions"]):
                                # Update match_columns to use the new names if they are in the property_columns
                                mapped_match_columns = []
                                for col in rel_def["match_columns"]:
                                    if col in property_columns:
                                        mapped_match_columns.append(st.session_state["property_mappings"].get(col, col))
                                    else:
                                        # For columns not in property_columns, check if they have a mapping anyway
                                        mapped_match_columns.append(st.session_state["property_mappings"].get(col, col))

                                # Create a mapping from source property names to target property names
                                target_property_map = {}
                                for col in rel_def["match_columns"]:
                                    source_prop = st.session_state["property_mappings"].get(col, col)
                                    target_prop = rel_def["target_property_mappings"].get(col, source_prop)
                                    target_property_map[source_prop] = target_prop

                                # Create a list of target property names for the match columns
                                target_match_columns = []
                                for col in mapped_match_columns:
                                    target_match_columns.append(target_property_map.get(col, col))

                                # Merge new nodes with existing nodes in the database
                                merge_nodes_with_existing(
                                    db_connection=self.db_manager,
                                    entities_df=mapped_df,
                                    label_column=label_column,
                                    property_columns=mapped_property_columns,
                                    target_label=rel_def["target_label"],
                                    match_columns=target_match_columns,
                                    relationship_type=rel_def["relationship_type"],
                                    source_to_target_map=target_property_map
                                )

                            # Success message
                            st.success(f"Entities and {len(st.session_state['relationship_definitions'])} relationships pushed successfully!")

                        except Exception as e:
                            st.error(f"Error: {e}")

        # Add filtering options if entities are loaded
        if st.session_state["entity_data"] is not None:
            with st.expander("Filter Entities", expanded=False):
                st.markdown("Filter entities based on column values")

                # Select column to filter on
                filter_column = st.selectbox(
                    "Select column to filter on:",
                    options=st.session_state["entity_data"].columns,
                    key="filter_column"
                )

                # Select filter operation
                filter_operation = st.selectbox(
                    "Filter operation:",
                    options=["==", "!=", ">", "<", ">=", "<=", "contains", "starts with", "ends with"],
                    key="filter_operation"
                )

                # Input filter value
                filter_value = st.text_input("Filter value:", key="filter_value")

                # Apply filter button
                if st.button("Apply Filter"):
                    if filter_value:
                        # Apply the filter
                        filtered_df = self._filter_entity_data(
                            st.session_state["entity_data"],
                            filter_column,
                            filter_operation,
                            filter_value
                        )

                        # Update the DataFrame in session state
                        st.session_state["entity_data"] = filtered_df
                        st.success(f"Filter applied. {len(filtered_df)} entities match the filter.")

                # Reset filter button
                if st.button("Reset Filter"):
                    if "original_entity_data" in st.session_state:
                        st.session_state["entity_data"] = st.session_state["original_entity_data"].copy()
                        st.success("Filter reset. Showing all entities.")

        # Structure/Taxonomy section
        st.header("Structure")

        with st.expander("Assemble ontology, taxonomy, or schema using properties", expanded=False):
            # Create two columns layout
            col1, col2 = st.columns(2)

            # Right column for instructions
            with col2:
                st.markdown(
                    """
                    ## Define Relationships and Build Taxonomy
                    1. Select keys to define a hierarchical taxonomy.
                    2. Rearrange or nest keys to organize the structure.
                    3. Save the taxonomy schema.
                    """
                )

            # Left column for functionality
            with col1:
                st.subheader("Select Data Source")

                data_source = st.radio(
                    "Relate entities from:",
                    ["File", "Database"],
                    key="data_source_section2"
                )

                entity_data = st.session_state.get("entity_data", None)

                if data_source == "File":
                    # File type selection
                    if entity_data is None:
                        file_type = st.radio(
                            "File type:",
                            ["CSV", "Excel", "JSON"],
                            key="file_type_section2"
                        )

                        if file_type in ["CSV", "JSON"]:
                            # File uploader for CSV or JSON
                            file_types = {"CSV": ["csv"], "JSON": ["json"]}
                            uploaded_file = st.file_uploader(
                                f"Upload {file_type} file:", 
                                type=file_types[file_type], 
                                key=f"file_uploader_section2_{file_type}"
                            )

                            if uploaded_file:
                                try:
                                    entity_data = self._load_entities_from_file(uploaded_file)
                                    st.session_state["entity_data"] = entity_data
                                    st.success(f"{file_type} file loaded successfully!")
                                except Exception as e:
                                    st.error(f"Error loading file: {e}")

                        elif file_type == "Excel":
                            # Excel file handling with sheet selection
                            uploaded_excel = st.file_uploader(
                                "Upload Excel file:", 
                                type=["xlsx", "xls"], 
                                key="excel_uploader_section2"
                            )

                            if uploaded_excel:
                                try:
                                    xls = pd.ExcelFile(uploaded_excel)
                                    sheet_names = xls.sheet_names
                                    selected_sheet = st.selectbox("Select sheet:", options=sheet_names)

                                    if st.button("Load Sheet"):
                                        entity_data = self._load_entities_from_file(uploaded_excel, sheet_name=selected_sheet)
                                        st.session_state["entity_data"] = entity_data
                                        st.success(f"Excel sheet '{selected_sheet}' loaded successfully!")
                                except Exception as e:
                                    st.error(f"Error loading Excel file: {e}")

                    entity_data = st.session_state["entity_data"]

                elif data_source == "Database":
                    # Fetch available node labels from Neo4j
                    if self.db_manager.is_connected():
                        labels = self.db_manager.fetch_labels()
                        # Allow the user to select a label type
                        entity_label = st.selectbox("Select Node Label to Use:", labels)
                        if entity_label:
                            properties = self.db_manager.fetch_node_properties(entity_label)
                            st.session_state["entity_properties"] = properties
                            entity_data = pd.DataFrame(columns=properties)
                    else:
                        st.error("Not connected to Neo4j. Please connect first.")

            # Move back to full width for the taxonomy creation
            with st.container():
                # If the dataframe is loaded, proceed with taxonomy creation
                if entity_data is not None:
                    # Create two columns for the taxonomy section
                    tax_col1, tax_col2 = st.columns(2)

                    with tax_col1:
                        st.subheader("Select Keys for Taxonomy")
                        # Display available keys
                        available_keys = entity_data.columns.tolist()
                        selected_keys = st.multiselect(
                            "Select keys to define taxonomy levels:",
                            options=available_keys,
                            default=st.session_state["taxonomy_keys"]
                        )
                        # Update session state with selected keys
                        if selected_keys:
                            st.session_state["taxonomy_keys"] = selected_keys
                        extra_keys = st.multiselect(
                            "Select keys for useful context:",
                            options=list(set(available_keys)-set(selected_keys)),
                            default=[]
                        )
                        all_selected_keys = selected_keys.copy()
                        if extra_keys:
                            all_selected_keys += extra_keys

                        # Display the selected keys as the hierarchical structure
                        if st.session_state["taxonomy_keys"]:
                            st.subheader("**Schema Hierarchy:**")
                            for i, key in enumerate(st.session_state["taxonomy_keys"], 1):
                                st.write(f"Level {i}: {key}")
                            if data_source == "Database" and st.button("Pull Entities from Database"):
                                if self.db_manager.is_connected():
                                    entity_data = self._load_entities_from_database(entity_label)
                                    st.session_state["entity_data"] = entity_data

                        taxonomy_set = st.toggle("Set Taxonomy", value=False, key="taxonomy_set")

                        # Option to save the taxonomy
                        st.subheader("Save Taxonomy")
                        save_format = st.selectbox("Select file format:", ["CSV", "JSON"])

                        if st.session_state["taxonomy"] is not None:
                            if save_format == "CSV":
                                csv_data = st.session_state["taxonomy"].to_csv(index=False)
                                st.download_button(
                                    label="Download Taxonomy as CSV",
                                    data=csv_data,
                                    file_name="taxonomy.csv",
                                    mime="text/csv",
                                )
                            elif save_format == "JSON":
                                json_data = st.session_state["taxonomy"].to_json(orient="records")
                                st.download_button(
                                    label="Download Taxonomy as JSON",
                                    data=json_data,
                                    file_name="taxonomy.json",
                                    mime="application/json",
                                )

                    with tax_col2:
                        # Create the taxonomy by grouping the dataframe
                        if st.session_state["taxonomy_keys"]:
                            try:
                                if not taxonomy_set:
                                    taxonomy_df = self._create_taxonomy(entity_data, st.session_state["taxonomy_keys"])
                                    st.session_state["taxonomy"] = taxonomy_df

                                # Display the resulting taxonomy
                                st.subheader("**Generated Taxonomy:**")
                                taxonomy_df = st.session_state["taxonomy"]

                                try:
                                    # Try to display the full taxonomy dataframe
                                    st.dataframe(taxonomy_df, use_container_width=True)
                                except Exception as e:
                                    if "MessageSizeError" in str(e) or "exceeds the message size limit" in str(e):
                                        # If the dataframe is too large, show an abbreviated version
                                        st.warning("The taxonomy is too large to display in full. Showing abbreviated version (first 1000 rows).")

                                        # Create an abbreviated dataframe
                                        abbreviated_df = taxonomy_df.head(1000)
                                        st.dataframe(abbreviated_df, use_container_width=True)

                                        # Remind user about download options
                                        st.info("Use the download options on the left to get the complete taxonomy data.")
                                    else:
                                        # If it's a different error, show it
                                        st.error(f"Error displaying taxonomy: {e}")
                            except Exception as e:
                                st.error(f"Error generating taxonomy: {e}")
                        else:
                            st.info("Select keys on the left to build a taxonomy")

                        # Option to save the taxonomy in the database
                        st.subheader("Save Taxonomy to Database")

                        # Select fields to match entities
                        available_columns = entity_data.columns.tolist() if entity_data is not None else []
                        if self.db_manager.is_connected():
                            available_labels = self.db_manager.fetch_labels()
                            entity_label = st.selectbox("Select entity label to connect to:",
                                                      options=available_labels,
                                                      key="taxonomy_entity_label")
                        else:
                            entity_label = st.text_input("Enter entity label to connect to:")

                        match_columns = st.multiselect("Select columns to match with entity nodes:",
                                                    options=available_columns,
                                                    key="taxonomy_match_columns")
                        relationship_type = st.text_input("Define Relationship Type (e.g., BELONGS_TO, PART_OF):",
                                                        key="taxonomy_relationship_type")

                        if st.button("Push Taxonomy to Database"):
                            if not self.db_manager.is_connected():
                                st.error("Not connected to Neo4j. Please connect first.")
                            elif not entity_label:
                                st.error("Please select or enter an entity label.")
                            elif not match_columns:
                                st.error("Please select at least one match column.")
                            elif not relationship_type:
                                st.error("Please enter a relationship type.")
                            elif st.session_state["taxonomy"] is None:
                                st.error("No taxonomy generated. Please select keys and generate a taxonomy first.")
                            else:
                                with st.spinner("Pushing taxonomy to database..."):
                                    success = self._push_taxonomy_to_neo4j(
                                        st.session_state["taxonomy"],
                                        st.session_state["taxonomy_keys"],
                                        entity_label,
                                        match_columns,
                                        relationship_type
                                    )

                                    if success:
                                        st.success("Taxonomy pushed to database and linked to entities successfully!")
                                    else:
                                        st.error("Failed to push taxonomy to database.")
                else:
                    st.warning("No file loaded yet. Please load a file or pull entities from the database.")


        # Ontology management
        with st.expander("Ontology Management", expanded=False):
            # Ontology file upload
            uploaded_ontology = st.file_uploader(
                "Upload ontology file (JSON)",
                type=["json"],
                key="ontology_uploader"
            )

            if uploaded_ontology is not None:
                # Load ontology from file
                ontology_data = self._load_ontology(uploaded_ontology)
                st.session_state["ontology_data"] = ontology_data

                if ontology_data:
                    st.success(f"Loaded ontology with {len(ontology_data.get('terms', {}))} terms")

                    # Display ontology summary
                    st.write("Ontology Summary:")
                    st.write(f"Terms: {len(ontology_data.get('terms', {}))}")

                    # Relationship types
                    rel_types = set()
                    for term_data in ontology_data.get('terms', {}).values():
                        rel_types.update(term_data.get('relationships', {}).keys())

                    st.write(f"Relationship Types: {', '.join(rel_types)}")

                    # Push to Neo4j button
                    if st.button("Push Ontology to Neo4j"):
                        if not self.db_manager.is_connected():
                            st.error("Not connected to Neo4j. Please connect first.")
                        else:
                            with st.spinner("Pushing ontology to Neo4j..."):
                                success = self._push_ontology_to_neo4j(ontology_data)

                                if success:
                                    st.success("Successfully pushed ontology to Neo4j")
                                else:
                                    st.error("Failed to push ontology to Neo4j")

def render_map_page():
    """Render the Map page."""
    page = MapPage()
    page.render()
