"""
cBioPortal Browser Page Module for Science Data Kit

This module provides the cBioPortal Browser page for the Science Data Kit application.
The cBioPortal Browser page handles browsing and managing ontology terms from cBioPortal and OncoTree.
"""

import streamlit as st
import pandas as pd
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from io import BytesIO

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.sidebar import render_database_sidebar
from science_data_kit.core.db.db_manager import db_manager

# Import OntologyAnnotation from our compatibility layer
try:
    from isatools.model import OntologyAnnotation
except ImportError:
    from science_data_kit.core.utils.isa_compatibility import OntologyAnnotation

# Constants
CBIOPORTAL_API_URL = "https://www.cbioportal.org/api"
ONCOTREE_API_URL = "http://oncotree.mskcc.org/api"

class CbioportalBrowserPage(BasePage):
    """
    cBioPortal Browser page for browsing and managing ontology terms.

    This page provides functionality for:
    - Fetching cancer types from cBioPortal API
    - Fetching tumor types from OncoTree API
    - Converting data to OntologyAnnotation objects
    - Loading study data from cBioPortal API
    - Managing and exporting ontology terms
    """

    def __init__(self):
        """Initialize the cBioPortal Browser page."""
        super().__init__("cBioPortal Browser", "🧬")
        self._setup_sidebar()
        self.db_manager = db_manager

        # Initialize session state variables
        if "terms" not in st.session_state:
            st.session_state.terms = []

    def _setup_sidebar(self):
        """Set up the sidebar items for the cBioPortal Browser page."""
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

    def _get_cancer_types(self) -> List[Dict[str, Any]]:
        """
        Get the list of cancer types from cBioPortal API.

        Returns:
            List of dictionaries containing cancer type information.
        """
        try:
            response = requests.get(f"{CBIOPORTAL_API_URL}/cancer-types")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching cancer types: {e}")
            return []

    def _get_oncotree_tumor_types(self) -> List[Dict[str, Any]]:
        """
        Get the list of tumor types from OncoTree API.

        Returns:
            List of dictionaries containing tumor type information.
        """
        try:
            response = requests.get(f"{ONCOTREE_API_URL}/tumorTypes")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching tumor types: {e}")
            return []

    def _convert_to_ontology_annotations(self, data: List[Dict[str, Any]], 
                                       term_key: str, 
                                       accession_key: str, 
                                       source: str) -> List[OntologyAnnotation]:
        """
        Convert cBioPortal or OncoTree data to OntologyAnnotation objects.

        Args:
            data: List of dictionaries containing term information
            term_key: Key in the dictionary for the term name
            accession_key: Key in the dictionary for the term accession/ID
            source: Source of the ontology (e.g., "cBioPortal", "OncoTree")

        Returns:
            List of OntologyAnnotation objects
        """
        annotations = []
        for item in data:
            if term_key in item and accession_key in item:
                annotation = OntologyAnnotation(
                    term=item[term_key],
                    term_accession=item[accession_key],
                    term_source=source
                )
                annotations.append(annotation)
        return annotations

    def _load_cbioportal_study_data(self, study_id: str) -> Dict[str, Any]:
        """
        Load study data from cBioPortal API.

        Args:
            study_id: The ID of the study to load

        Returns:
            Dictionary containing study data
        """
        try:
            response = requests.get(f"{CBIOPORTAL_API_URL}/studies/{study_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching study data: {e}")
            return {}

    def _get_cbioportal_studies(self) -> List[Dict[str, Any]]:
        """
        Get the list of studies from cBioPortal API.

        Returns:
            List of dictionaries containing study information.
        """
        try:
            response = requests.get(f"{CBIOPORTAL_API_URL}/studies")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching studies: {e}")
            return []

    def render_content(self) -> None:
        """Render the cBioPortal Browser page content."""
        st.write("Browse and manage ontology terms from cBioPortal and OncoTree.")

        # Sidebar for term management
        st.sidebar.subheader("Ontology Terms Management")

        # cBioPortal Cancer Types
        st.sidebar.subheader("cBioPortal Cancer Types")
        if st.sidebar.button("Load Cancer Types"):
            cancer_types = self._get_cancer_types()
            if cancer_types:
                new_terms = self._convert_to_ontology_annotations(
                    cancer_types, 
                    "name", 
                    "cancerTypeId", 
                    "cBioPortal"
                )

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
                    st.sidebar.success(f"Added {added_count} cancer type terms.")
                else:
                    st.sidebar.info("All cancer type terms are already loaded.")
            else:
                st.sidebar.warning("Failed to load cancer types.")

        # OncoTree Tumor Types
        st.sidebar.subheader("OncoTree Tumor Types")
        if st.sidebar.button("Load Tumor Types"):
            tumor_types = self._get_oncotree_tumor_types()
            if tumor_types:
                new_terms = self._convert_to_ontology_annotations(
                    tumor_types, 
                    "name", 
                    "code", 
                    "OncoTree"
                )

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
                    st.sidebar.success(f"Added {added_count} tumor type terms.")
                else:
                    st.sidebar.info("All tumor type terms are already loaded.")
            else:
                st.sidebar.warning("Failed to load tumor types.")

        # cBioPortal Studies
        st.sidebar.subheader("cBioPortal Studies")
        studies = self._get_cbioportal_studies()
        if studies:
            study_names = [study.get("name", "") for study in studies]
            study_ids = [study.get("studyId", "") for study in studies]

            selected_study_index = st.sidebar.selectbox(
                "Select a study to explore",
                range(len(study_names)),
                format_func=lambda i: study_names[i]
            )

            if st.sidebar.button("Load Study Data"):
                selected_study_id = study_ids[selected_study_index]
                study_data = self._load_cbioportal_study_data(selected_study_id)

                if study_data:
                    st.success(f"Loaded study: {study_data.get('name', '')}")

                    # Extract relevant terms from study data
                    terms = []

                    # Add cancer type as a term
                    if "cancerType" in study_data:
                        terms.append(OntologyAnnotation(
                            term=study_data["cancerType"].get("name", ""),
                            term_accession=study_data["cancerType"].get("cancerTypeId", ""),
                            term_source="cBioPortal"
                        ))

                    # Add other relevant terms
                    if "referenceGenome" in study_data:
                        terms.append(OntologyAnnotation(
                            term=f"Reference Genome: {study_data['referenceGenome']}",
                            term_accession=f"genome:{study_data['referenceGenome']}",
                            term_source="cBioPortal"
                        ))

                    # Create a set of existing term accessions to avoid duplicates
                    existing_accessions = {term.term_accession for term in st.session_state.terms}

                    # Add only new terms that don't exist yet
                    added_count = 0
                    for term in terms:
                        if term.term_accession and term.term_accession not in existing_accessions:
                            st.session_state.terms.append(term)
                            existing_accessions.add(term.term_accession)
                            added_count += 1

                    if added_count > 0:
                        st.sidebar.success(f"Added {added_count} terms from study.")
                    else:
                        st.sidebar.info("No new terms found in study.")
                else:
                    st.sidebar.warning("Failed to load study data.")

        # Manual term addition
        st.sidebar.subheader("Add Term Manually")
        with st.sidebar.form("add_term_form"):
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
                if new_term.term_accession not in existing_accessions:
                    st.session_state.terms.append(new_term)
                    st.sidebar.success(f"Added term: {term_name}")
                else:
                    st.sidebar.warning(f"Term with URI {term_uri} already exists.")

        # Main content area
        st.title("cBioPortal Ontology Browser")

        # Display current terms
        if st.session_state.terms:
            with st.expander(f"📋 View Terms ({len(st.session_state.terms)})"):
                # Group terms by source
                terms_by_source = {}
                for term in st.session_state.terms:
                    source = term.term_source
                    if source not in terms_by_source:
                        terms_by_source[source] = []
                    terms_by_source[source].append(term)

                # Display terms grouped by source
                for source, terms in terms_by_source.items():
                    st.subheader(f"{source} ({len(terms)})")
                    for i, ann in enumerate(terms):
                        st.markdown(f"{i+1}. **{ann.term}** → `{ann.term_accession}`")
        else:
            st.info("No terms loaded yet. Use the sidebar to load terms from cBioPortal or add them manually.")

        # Export terms
        if st.session_state.terms:
            st.subheader("Export Terms")
            export_format = st.radio("Export Format", ["CSV", "JSON", "Excel"])

            if st.button("Export"):
                if export_format == "CSV":
                    csv_data = pd.DataFrame([
                        {"Term Name": term.term, "Term URI": term.term_accession, "Ontology Source": term.term_source}
                        for term in st.session_state.terms
                    ])
                    csv_buffer = BytesIO()
                    csv_data.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)
                    st.download_button(
                        label="Download CSV",
                        data=csv_buffer,
                        file_name="cbioportal_terms.csv",
                        mime="text/csv"
                    )
                elif export_format == "JSON":
                    json_data = json.dumps([
                        {"term": term.term, "term_accession": term.term_accession, "term_source": term.term_source}
                        for term in st.session_state.terms
                    ], indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name="cbioportal_terms.json",
                        mime="application/json"
                    )
                elif export_format == "Excel":
                    excel_data = pd.DataFrame([
                        {"Term Name": term.term, "Term URI": term.term_accession, "Ontology Source": term.term_source}
                        for term in st.session_state.terms
                    ])
                    excel_buffer = BytesIO()
                    excel_data.to_excel(excel_buffer, index=False)
                    excel_buffer.seek(0)
                    st.download_button(
                        label="Download Excel",
                        data=excel_buffer,
                        file_name="cbioportal_terms.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

def render_cbioportal_browser_page():
    """Render the cBioPortal Browser page."""
    page = CbioportalBrowserPage()
    page.render()
