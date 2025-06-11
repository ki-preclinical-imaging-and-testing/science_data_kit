import streamlit as st
import pandas as pd
import requests
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from io import BytesIO

# Import OntologyAnnotation from our compatibility layer
try:
    from isatools.model import OntologyAnnotation
except ImportError:
    from utils.isa_compatibility import OntologyAnnotation

# Constants
CBIOPORTAL_API_URL = "https://www.cbioportal.org/api"
ONCOTREE_API_URL = "http://oncotree.mskcc.org/api"

def get_cancer_types() -> List[Dict[str, Any]]:
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

def get_oncotree_tumor_types() -> List[Dict[str, Any]]:
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

def convert_to_ontology_annotations(data: List[Dict[str, Any]], 
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

def load_cbioportal_study_data(study_id: str) -> Dict[str, Any]:
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

def get_cbioportal_studies() -> List[Dict[str, Any]]:
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

def main():
    st.title("cBioPortal Ontology Browser")

    # Initialize session state for storing terms
    if 'terms' not in st.session_state:
        st.session_state.terms = []

    # Sidebar for term management
    st.sidebar.subheader("Ontology Terms Management")

    # cBioPortal Cancer Types
    st.sidebar.subheader("cBioPortal Cancer Types")
    if st.sidebar.button("Load Cancer Types"):
        cancer_types = get_cancer_types()
        if cancer_types:
            new_terms = convert_to_ontology_annotations(
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
        tumor_types = get_oncotree_tumor_types()
        if tumor_types:
            new_terms = convert_to_ontology_annotations(
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
    studies = get_cbioportal_studies()
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
            study_data = load_cbioportal_study_data(selected_study_id)

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

if __name__ == "__main__":
    main()
