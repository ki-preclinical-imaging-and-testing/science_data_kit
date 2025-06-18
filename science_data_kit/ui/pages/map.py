"""
Map Page Module for Science Data Kit

This module provides the Map page for the Science Data Kit application.
The Map page handles defining entities and relationships for knowledge graphs.
"""

import streamlit as st
import pandas as pd
import networkx as nx
from typing import Dict, Any, Optional, List, Union, Callable
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
    
    def _setup_sidebar(self):
        """Set up the sidebar items for the Map page."""
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
    
    def _load_entities_from_file(self, uploaded_file) -> pd.DataFrame:
        """
        Load entities from a file.
        
        Args:
            uploaded_file: The uploaded file object.
            
        Returns:
            A DataFrame containing the entities.
        """
        try:
            # Determine file type from extension
            file_extension = Path(uploaded_file.name).suffix.lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(uploaded_file)
            elif file_extension == '.xlsx':
                df = pd.read_excel(uploaded_file)
            elif file_extension == '.json':
                df = pd.DataFrame(json.loads(uploaded_file.getvalue().decode('utf-8')))
            else:
                st.error(f"Unsupported file type: {file_extension}")
                return pd.DataFrame()
            
            return df
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
    
    def render_content(self) -> None:
        """Render the Map page content."""
        st.write("Define entities and relationships to create knowledge graphs.")
        
        # Entity management
        st.header("Entity Management")
        
        # Entity source selection
        entity_source = st.radio(
            "Entity Source",
            options=["File", "Database"],
            horizontal=True
        )
        
        if entity_source == "File":
            # File upload
            uploaded_file = st.file_uploader(
                "Upload entity file (CSV, Excel, or JSON)",
                type=["csv", "xlsx", "json"]
            )
            
            if uploaded_file is not None:
                # Load entities from file
                entity_data = self._load_entities_from_file(uploaded_file)
                st.session_state["entity_data"] = entity_data
                
                if not entity_data.empty:
                    st.success(f"Loaded {len(entity_data)} entities from file")
                    
                    # Display entity data
                    st.write("Entity Data:")
                    st.dataframe(entity_data)
                    
                    # Create entity structure
                    structure = self._create_entity_structure(entity_data)
                    st.session_state["entity_structure"] = structure
                    
                    # Display entity structure
                    st.write("Entity Structure:")
                    structure_df = pd.DataFrame([
                        {"Property": prop, "Type": type_}
                        for prop, type_ in structure.items()
                    ])
                    st.dataframe(structure_df)
                    
                    # Entity label input
                    label = st.text_input("Enter label for entities")
                    
                    # Push to Neo4j button
                    if st.button("Push Entities to Neo4j"):
                        if not label:
                            st.error("Please enter a label for the entities")
                        elif not st.session_state.get("connected", False):
                            st.error("Not connected to Neo4j. Please connect first.")
                        else:
                            with st.spinner("Pushing entities to Neo4j..."):
                                success = self._push_entities_to_neo4j(entity_data, label, structure)
                                
                                if success:
                                    st.success(f"Successfully pushed {len(entity_data)} entities to Neo4j")
                                else:
                                    st.error("Failed to push entities to Neo4j")
        else:  # Database
            # Label selection
            if self.db_manager.is_connected():
                # Get available labels
                labels = self.db_manager.fetch_labels()
                
                if labels:
                    selected_label = st.selectbox(
                        "Select entity label",
                        options=labels
                    )
                    
                    if st.button("Load Entities"):
                        # Load entities from database
                        entity_data = self._load_entities_from_database(selected_label)
                        st.session_state["entity_data"] = entity_data
                        
                        if not entity_data.empty:
                            st.success(f"Loaded {len(entity_data)} entities from database")
                            
                            # Display entity data
                            st.write("Entity Data:")
                            st.dataframe(entity_data)
                else:
                    st.info("No labels found in the database")
            else:
                st.error("Not connected to Neo4j. Please connect first.")
        
        # Relationship management
        st.header("Relationship Management")
        
        # Check if entity data is available
        if st.session_state["entity_data"] is not None and not st.session_state["entity_data"].empty:
            # Source and target label selection
            col1, col2 = st.columns(2)
            
            with col1:
                source_label = st.text_input("Source Label")
            
            with col2:
                target_label = st.text_input("Target Label")
            
            # Relationship type
            relationship_type = st.text_input("Relationship Type")
            
            # Property matching
            col1, col2 = st.columns(2)
            
            with col1:
                source_property = st.selectbox(
                    "Source Property",
                    options=[col for col in st.session_state["entity_data"].columns if col != 'id']
                )
            
            with col2:
                target_property = st.selectbox(
                    "Target Property",
                    options=[col for col in st.session_state["entity_data"].columns if col != 'id']
                )
            
            # Create relationships button
            if st.button("Create Relationships"):
                if not source_label or not target_label:
                    st.error("Please enter source and target labels")
                elif not relationship_type:
                    st.error("Please enter a relationship type")
                elif not st.session_state.get("connected", False):
                    st.error("Not connected to Neo4j. Please connect first.")
                else:
                    with st.spinner("Creating relationships..."):
                        success = self._create_relationships(
                            source_label, target_label, relationship_type,
                            source_property, target_property
                        )
                        
                        if success:
                            st.success("Successfully created relationships")
                        else:
                            st.error("Failed to create relationships")
        else:
            st.info("No entity data available. Please load entities first.")
        
        # Ontology management
        st.header("Ontology Management")
        
        # Ontology file upload
        uploaded_ontology = st.file_uploader(
            "Upload ontology file (JSON)",
            type=["json"]
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
                    if not st.session_state.get("connected", False):
                        st.error("Not connected to Neo4j. Please connect first.")
                    else:
                        with st.spinner("Pushing ontology to Neo4j..."):
                            success = self._push_ontology_to_neo4j(ontology_data)
                            
                            if success:
                                st.success("Successfully pushed ontology to Neo4j")
                            else:
                                st.error("Failed to push ontology to Neo4j")

def render():
    """Render the Map page."""
    page = MapPage()
    page.render()