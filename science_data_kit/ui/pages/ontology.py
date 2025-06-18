"""
Ontology Page Module for Science Data Kit

This module provides the Ontology page for the Science Data Kit application.
It allows users to browse, manage, and upload ontology terms.
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Union
import pandas as pd
from pathlib import Path

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.core.db.db_manager import Neo4jManager, load_db_config
from science_data_kit.core.utils.isa_compatibility import OntologyAnnotation, OntologySource, get_isa_objects

class OntologyPage(BasePage):
    """
    Ontology page for browsing and managing ontology terms.
    """

    def __init__(self):
        """Initialize the Ontology page."""
        super().__init__(title="Ontology Browser", icon="🧬")
        
        # Initialize session state for storing terms and Neo4j connection
        if 'terms' not in st.session_state:
            st.session_state.terms = []
        if 'neo4j_manager' not in st.session_state:
            st.session_state.neo4j_manager = None
        if 'neo4j_connected' not in st.session_state:
            st.session_state.neo4j_connected = False
        if 'available_labels' not in st.session_state:
            st.session_state.available_labels = []
        if 'term_management_option' not in st.session_state:
            st.session_state.term_management_option = "Add Term Manually"

    def render_sidebar(self):
        """Render the sidebar for the Ontology page."""
        super().render_sidebar()
        
        # Sidebar for available terms and labels
        st.sidebar.subheader("Available Terms and Labels")

        # Term Table View in sidebar
        with st.sidebar.expander("Term Table View", expanded=True):
            if not st.session_state.terms:
                st.sidebar.warning("No terms available to display.")
            else:
                # Add search and filter options
                search_term = st.sidebar.text_input("Search terms", key="sidebar_table_search")

                # Multiple choice selection for search fields
                search_fields = st.sidebar.multiselect(
                    "Search in fields",
                    ["Term", "Source", "URI"],
                    default=["Term", "Source", "URI"]
                )

                # Get unique sources
                sources = sorted(set([
                    term.term_source.name if hasattr(term.term_source, 'name') else str(term.term_source) 
                    for term in st.session_state.terms
                ]))
                selected_source = st.sidebar.selectbox("Filter by source", ["All Sources"] + sources, key="sidebar_source_filter")

                # Create a dataframe from the terms
                terms_data = []
                for i, term in enumerate(st.session_state.terms):
                    source_name = term.term_source.name if hasattr(term.term_source, 'name') else str(term.term_source)
                    terms_data.append({
                        "ID": i,
                        "Term": term.term,
                        "Source": source_name,
                        "URI": term.term_accession
                    })

                df = pd.DataFrame(terms_data)
                total_terms = len(df)

                # Apply filters
                if search_term:
                    # Build filter based on selected search fields
                    filter_condition = pd.Series(False, index=df.index)
                    if "Term" in search_fields:
                        filter_condition = filter_condition | df['Term'].str.contains(search_term, case=False)
                    if "Source" in search_fields:
                        filter_condition = filter_condition | df['Source'].str.contains(search_term, case=False)
                    if "URI" in search_fields:
                        filter_condition = filter_condition | df['URI'].str.contains(search_term, case=False)

                    df = df[filter_condition]

                if selected_source != "All Sources":
                    df = df[df['Source'] == selected_source]

                # Display match information
                matches = len(df)
                st.sidebar.info(f"Found {matches} matches in {total_terms} terms.")

                # Display the dataframe
                if matches > 0:
                    st.sidebar.dataframe(df, use_container_width=True, height=300)
                else:
                    st.sidebar.warning("No terms match the current filters.")

    def render_content(self):
        """Render the main content for the Ontology page."""
        st.title("Ontology Browser")
        
        # Neo4j Connection Section
        st.subheader("Neo4j Connection")

        # Try to load config from file
        config = load_db_config('.db_config_auto.yaml')
        if not config:
            config = load_db_config('.db_config.yaml')

        # Create columns for the connection form
        col1, col2 = st.columns(2)

        with col1:
            # Connection form
            with st.form("neo4j_connection_form"):
                uri = st.text_input("Neo4j URI", value=config.get("uri", "bolt://localhost:7687") if config else "bolt://localhost:7687")
                user = st.text_input("Username", value=config.get("user", "neo4j") if config else "neo4j")
                password = st.text_input("Password", value=config.get("password", "") if config else "", type="password")
                database = st.text_input("Database", value=config.get("database", "neo4j") if config else "neo4j")

                connect_button = st.form_submit_button("Connect to Neo4j")

                if connect_button:
                    try:
                        neo4j_config = {
                            "uri": uri,
                            "user": user,
                            "password": password,
                            "database": database
                        }

                        # Create a new connection
                        manager = Neo4jManager(**neo4j_config)

                        # Test the connection
                        if manager.test_connection():
                            st.session_state.neo4j_manager = manager
                            st.session_state.neo4j_connected = True
                            st.success("Connected to Neo4j!")

                            # Fetch available labels from Neo4j
                            try:
                                labels = manager.fetch_labels()
                                st.session_state.available_labels = labels
                                
                                # Add Neo4j labels to terms as a "Local" ontology
                                self._add_labels_as_terms(labels)
                            except Exception as e:
                                st.warning(f"Connected, but couldn't fetch labels: {e}")
                        else:
                            st.error("Failed to connect to Neo4j.")
                    except Exception as e:
                        st.error(f"Error connecting to Neo4j: {e}")

        with col2:
            # Display connection status
            if st.session_state.neo4j_connected:
                st.success("✅ Connected to Neo4j")
                st.info(f"URI: {st.session_state.neo4j_manager.uri}")
                st.info(f"Database: {st.session_state.neo4j_manager.database}")

                # Display label count
                if st.session_state.available_labels:
                    st.info(f"Available Labels: {len(st.session_state.available_labels)}")

                    # Show a sample of labels
                    if len(st.session_state.available_labels) > 0:
                        with st.expander("View Labels"):
                            for label in st.session_state.available_labels[:10]:  # Show first 10 labels
                                st.write(f"- {label}")
                            if len(st.session_state.available_labels) > 10:
                                st.write(f"... and {len(st.session_state.available_labels) - 10} more")
            else:
                st.warning("❌ Not connected to Neo4j. Some features will be disabled.")
        
        # Ontology Terms Management section
        st.subheader("Ontology Terms Management")

        # Create tabs for different term sources
        term_tabs = st.tabs(["ISA Terms", "Term Management"])

        # Tab 1: ISA Terms
        with term_tabs[0]:
            st.subheader("Standard ISA Terms")
            if st.button("Load Standard ISA Terms", key="load_standard_isa_terms_button"):
                try:
                    standard_terms = self._get_standard_isa_terms()

                    # Create a set of existing term accessions to avoid duplicates
                    existing_accessions = {term.term_accession for term in st.session_state.terms}

                    # Add only new terms that don't exist yet
                    added_count = 0
                    for term in standard_terms:
                        if term.term_accession not in existing_accessions:
                            st.session_state.terms.append(term)
                            existing_accessions.add(term.term_accession)
                            added_count += 1

                    if added_count > 0:
                        st.success(f"Added {added_count} standard ISA terms.")
                    else:
                        st.info("All standard terms are already loaded.")
                except Exception as e:
                    st.error(f"Error loading standard ISA terms: {e}")

            # Upload widget for OntoMaton Terms
            st.subheader("Upload Custom Terms")
            terms_file = st.file_uploader("Upload Terms .xlsx or .tsv", type=["xlsx", "tsv", "csv"], key="custom_terms_uploader")

            if terms_file:
                try:
                    new_terms = self._load_ontomaton_terms(terms_file)

                    # Create a set of existing term accessions to avoid duplicates
                    existing_accessions = {term.term_accession for term in st.session_state.terms}

                    # Add only new terms that don't exist yet
                    added_count = 0
                    for term in new_terms:
                        if term.term_accession not in existing_accessions:
                            st.session_state.terms.append(term)
                            existing_accessions.add(term.term_accession)
                            added_count += 1

                    if added_count > 0:
                        st.success(f"Added {added_count} new terms from file.")
                    else:
                        st.info("All terms from the file are already loaded.")
                except Exception as e:
                    st.error(f"Error loading terms from file: {e}")

        # Tab 2: Term Management
        with term_tabs[1]:
            st.subheader("Add New Term")
            
            # Form for adding a new term
            with st.form("add_term_form"):
                term_name = st.text_input("Term Name")
                term_uri = st.text_input("Term URI")
                ontology_source = st.text_input("Ontology Source")
                
                submit_button = st.form_submit_button("Add Term")
                
                if submit_button and term_name and term_uri and ontology_source:
                    new_term = OntologyAnnotation(
                        term=term_name,
                        term_accession=term_uri,
                        term_source=ontology_source
                    )
                    
                    # Check if term already exists
                    existing_accessions = {term.term_accession for term in st.session_state.terms}
                    if term_uri not in existing_accessions:
                        st.session_state.terms.append(new_term)
                        st.success(f"Added new term: {term_name}")
                    else:
                        st.warning(f"Term with URI {term_uri} already exists.")
            
            # Push terms to Neo4j
            st.subheader("Push Terms to Neo4j")
            if st.button("Push Terms to Neo4j") and st.session_state.neo4j_connected:
                if not st.session_state.terms:
                    st.warning("No terms to push to Neo4j.")
                else:
                    try:
                        # Use the Neo4j manager to load ontology relationships
                        st.session_state.neo4j_manager.load_ontology_relationships(
                            st.session_state.terms,
                            create_source_nodes=True
                        )
                        st.success(f"Successfully pushed {len(st.session_state.terms)} terms to Neo4j.")
                    except Exception as e:
                        st.error(f"Error pushing terms to Neo4j: {e}")
            elif not st.session_state.neo4j_connected:
                st.warning("Connect to Neo4j first to push terms.")

    def _add_labels_as_terms(self, labels: List[str]):
        """
        Add Neo4j labels to terms as a "Local" ontology.
        
        Args:
            labels: List of Neo4j labels
        """
        try:
            # Create a proper OntologySource object for Neo4j labels
            local_source = None
            try:
                # Check if we already have a Local ontology source in the session state
                for term in st.session_state.terms:
                    if hasattr(term.term_source, 'name') and term.term_source.name == "Local":
                        local_source = term.term_source
                        break

                # If not found, create a new one
                if not local_source:
                    local_source = OntologySource(
                        name="Local",
                        file="",
                        version="1.0",
                        description="Neo4j database labels and local terms"
                    )
            except Exception as e:
                # Fallback to string if OntologySource creation fails
                local_source = "Local"

            # Add Neo4j labels to terms as a "Local" ontology
            local_terms = []
            for label in labels:
                if label and isinstance(label, str):
                    local_terms.append(OntologyAnnotation(
                        term=label,
                        term_accession=f"neo4j:label:{label}",
                        term_source=local_source
                    ))

            # Add local terms to session state if they don't exist yet
            existing_accessions = {term.term_accession for term in st.session_state.terms}
            added_count = 0
            for term in local_terms:
                if term.term_accession not in existing_accessions:
                    st.session_state.terms.append(term)
                    existing_accessions.add(term.term_accession)
                    added_count += 1
        except Exception as e:
            st.error(f"Error creating Local ontology terms: {e}")

    def _get_standard_isa_terms(self) -> List[OntologyAnnotation]:
        """
        Get standard ISA terms.
        
        Returns:
            List of OntologyAnnotation objects
        """
        # Create OBI ontology source
        obi_source = OntologySource(
            name="OBI",
            file="http://purl.obolibrary.org/obo/obi.owl",
            version="2021-10-11",
            description="Ontology for Biomedical Investigations"
        )
        
        # Create PATO ontology source
        pato_source = OntologySource(
            name="PATO",
            file="http://purl.obolibrary.org/obo/pato.owl",
            version="2021-10-11",
            description="Phenotype And Trait Ontology"
        )
        
        # Create standard terms
        terms = [
            # Study design terms
            OntologyAnnotation(term="intervention design", term_accession="http://purl.obolibrary.org/obo/OBI_0000115", term_source=obi_source),
            OntologyAnnotation(term="observational design", term_accession="http://purl.obolibrary.org/obo/OBI_0000071", term_source=obi_source),
            OntologyAnnotation(term="cross-over design", term_accession="http://purl.obolibrary.org/obo/OBI_0000684", term_source=obi_source),
            OntologyAnnotation(term="parallel group design", term_accession="http://purl.obolibrary.org/obo/OBI_0000685", term_source=obi_source),
            
            # Material type terms
            OntologyAnnotation(term="organism", term_accession="http://purl.obolibrary.org/obo/OBI_0100026", term_source=obi_source),
            OntologyAnnotation(term="specimen", term_accession="http://purl.obolibrary.org/obo/OBI_0100051", term_source=obi_source),
            OntologyAnnotation(term="extract", term_accession="http://purl.obolibrary.org/obo/OBI_0000423", term_source=obi_source),
            
            # Characteristic categories
            OntologyAnnotation(term="age", term_accession="http://purl.obolibrary.org/obo/PATO_0000011", term_source=pato_source),
            OntologyAnnotation(term="sex", term_accession="http://purl.obolibrary.org/obo/PATO_0000047", term_source=pato_source),
            OntologyAnnotation(term="organism part", term_accession="http://purl.obolibrary.org/obo/OBI_0000066", term_source=obi_source),
            
            # Protocol type terms
            OntologyAnnotation(term="sample collection", term_accession="http://purl.obolibrary.org/obo/OBI_0000659", term_source=obi_source),
        ]
        
        return terms

    def _load_ontomaton_terms(self, file_path_or_buffer) -> List[OntologyAnnotation]:
        """
        Load OntoMaton 'Terms' table (TSV or XLSX) into OntologyAnnotation objects.
        
        Args:
            file_path_or_buffer: Path to the file or file-like object
            
        Returns:
            List of OntologyAnnotation objects
        """
        # Determine file type and read accordingly
        if hasattr(file_path_or_buffer, 'name'):
            file_name = file_path_or_buffer.name.lower()
            if file_name.endswith('.xlsx'):
                df = pd.read_excel(file_path_or_buffer)
            else:  # Assume TSV/CSV
                df = pd.read_csv(file_path_or_buffer, sep='\t' if file_name.endswith('.tsv') else ',')
        else:
            # Assume TSV for string paths
            df = pd.read_csv(file_path_or_buffer, sep='\t')
            
        # Expected columns:
        # "Term Name", "Term URI", "Ontology Source", "Ontology URI", "Ontology Full Name"
        
        terms = []
        for _, row in df.iterrows():
            annotation = OntologyAnnotation(
                term=row["Term Name"],
                term_accession=row["Term URI"],
                term_source=row["Ontology Source"]
            )
            terms.append(annotation)
            
        return terms

def render_ontology_page():
    """Render the Ontology page."""
    page = OntologyPage()
    page.render()