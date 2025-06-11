import streamlit as st
import pandas as pd
from pathlib import Path
from typing import List, Union, Dict, Any
from io import BytesIO
import json
import requests

# Import Neo4j connection
from utils.graph_utils import Neo4jConnection, load_db_config

# Import isatools classes through our compatibility layer
try:
    from isatools import isatab
    from isatools.model import Investigation, Study, Assay, Process, Material, DataFile
    from isatools.model import OntologyAnnotation
    ISATOOLS_AVAILABLE = True
except ImportError:
    from utils.isa_compatibility import get_isa_objects
    isatab, OntologyAnnotation, Investigation, Study, Assay, Process, Material, DataFile = get_isa_objects()
    ISATOOLS_AVAILABLE = False

# Constants for external APIs
CBIOPORTAL_API_URL = "https://www.cbioportal.org/api"
ONCOTREE_API_URL = "http://oncotree.mskcc.org/api"


def extract_node_classes(inv: Investigation):
    """Collect ISA node types (Materials, DataFiles, etc.)"""
    node_classes = set()
    for study in inv.studies:
        for proc in study.process_sequence:
            for inp in proc.inputs:
                node_classes.add(type(inp).__name__)
            for out in proc.outputs:
                node_classes.add(type(out).__name__)
    return sorted(node_classes)


def extract_relationships(inv: Investigation):
    """Infer relationships from process steps (input → process → output)"""
    relationships = []
    for study in inv.studies:
        for proc in study.process_sequence:
            for inp in proc.inputs:
                for out in proc.outputs:
                    relationships.append((type(inp).__name__, "USED_IN", type(out).__name__))
    return sorted(set(relationships))


def extract_properties(inv: Investigation, class_name: str):
    """Gather sample properties for a given node class"""
    props = []
    for study in inv.studies:
        for proc in study.process_sequence:
            objs = proc.inputs + proc.outputs
            for obj in objs:
                if type(obj).__name__ == class_name:
                    props.extend(obj.characteristics + obj.comments)
    return [f"{p.category.term}: {p.value}" for p in props if hasattr(p, 'category')]


def load_ontomaton_terms(file_path_or_buffer):
    """
    Load OntoMaton 'Terms' table (TSV or XLSX) into OntologyAnnotation objects.
    """
    if hasattr(file_path_or_buffer, "name") and file_path_or_buffer.name.endswith(".xlsx"):
        df = pd.read_excel(file_path_or_buffer)
    else:
        df = pd.read_csv(file_path_or_buffer, sep="\t", engine="python")  # force tab-delimited

    required_columns = [
        "Term Name", "Term URI", "Ontology Source", "Ontology URI", "Ontology Full Name"
    ]
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Missing required columns in the Terms table.")

    annotations = []
    for _, row in df.iterrows():
        annotation = OntologyAnnotation(
            term=row["Term Name"],
            term_accession=row["Term URI"],
            term_source=row["Ontology Source"]
        )
        annotations.append(annotation)

    return annotations


def get_standard_isa_terms():
    """
    Returns a list of standard ISA ontology terms from the isatools library.
    These are common terms used in ISA-Tab files.
    """
    standard_terms = [
        # Study design terms
        OntologyAnnotation(term="intervention design", term_accession="http://purl.obolibrary.org/obo/OBI_0000115", term_source="OBI"),
        OntologyAnnotation(term="observational design", term_accession="http://purl.obolibrary.org/obo/OBI_0000071", term_source="OBI"),
        OntologyAnnotation(term="cross-over design", term_accession="http://purl.obolibrary.org/obo/OBI_0000296", term_source="OBI"),
        OntologyAnnotation(term="parallel group design", term_accession="http://purl.obolibrary.org/obo/OBI_0000471", term_source="OBI"),

        # Material types
        OntologyAnnotation(term="organism", term_accession="http://purl.obolibrary.org/obo/OBI_0100026", term_source="OBI"),
        OntologyAnnotation(term="specimen", term_accession="http://purl.obolibrary.org/obo/OBI_0100051", term_source="OBI"),
        OntologyAnnotation(term="extract", term_accession="http://purl.obolibrary.org/obo/OBI_0000423", term_source="OBI"),

        # Common characteristics
        OntologyAnnotation(term="age", term_accession="http://purl.obolibrary.org/obo/PATO_0000011", term_source="PATO"),
        OntologyAnnotation(term="sex", term_accession="http://purl.obolibrary.org/obo/PATO_0000047", term_source="PATO"),
        OntologyAnnotation(term="organism part", term_accession="http://purl.obolibrary.org/obo/OBI_0000066", term_source="OBI"),

        # Common protocols
        OntologyAnnotation(term="sample collection", term_accession="http://purl.obolibrary.org/obo/OBI_0000659", term_source="OBI"),
        OntologyAnnotation(term="extraction", term_accession="http://purl.obolibrary.org/obo/OBI_0302884", term_source="OBI"),
        OntologyAnnotation(term="nucleic acid sequencing", term_accession="http://purl.obolibrary.org/obo/OBI_0000626", term_source="OBI"),

        # Common factors
        OntologyAnnotation(term="time", term_accession="http://purl.obolibrary.org/obo/PATO_0000165", term_source="PATO"),
        OntologyAnnotation(term="dose", term_accession="http://purl.obolibrary.org/obo/PATO_0000470", term_source="PATO"),
        OntologyAnnotation(term="compound", term_accession="http://purl.obolibrary.org/obo/CHEBI_23367", term_source="CHEBI"),
    ]

    return standard_terms

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


def main():
    st.title("ISA Tools Browser for Neo4j Mapping")

    # Initialize session state for storing terms and Neo4j connection
    if 'terms' not in st.session_state:
        st.session_state.terms = []
    if 'neo4j_connection' not in st.session_state:
        st.session_state.neo4j_connection = None
    if 'neo4j_connected' not in st.session_state:
        st.session_state.neo4j_connected = False
    if 'available_labels' not in st.session_state:
        st.session_state.available_labels = []
    if 'term_management_option' not in st.session_state:
        st.session_state.term_management_option = "Add Term Manually"

    # Display a warning if isatools is not available
    if not ISATOOLS_AVAILABLE:
        st.warning(
            "⚠️ The isatools package is not available in this Python environment. "
            "Some functionality will be limited. "
            "For full functionality, please use Python 3.9 with isatools installed."
        )

    # Main content area
    uploaded = st.file_uploader("Upload an ISA-Tab file (zipped) or select local path", type=["txt", "zip", "json"], key="main_isa_file_uploader")

    # Neo4j Connection Section (moved from sidebar to main panel)
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
                    connection = Neo4jConnection(config=neo4j_config)

                    # Test the connection
                    if connection.test_connection(quiet=True):
                        st.session_state.neo4j_connection = connection
                        st.session_state.neo4j_connected = True
                        st.success("Connected to Neo4j!")

                        # Fetch available labels from Neo4j
                        try:
                            # Query to get all distinct labels
                            all_labels_query = "MATCH (n) RETURN DISTINCT labels(n) as labels"
                            label_results = connection.execute_query(all_labels_query)

                            # Extract and flatten the labels
                            all_labels = []
                            for result in label_results:
                                for label in result["labels"]:
                                    if label and isinstance(label, str):
                                        all_labels.append(label)

                            # Sort and store the labels
                            st.session_state.available_labels = sorted(set(all_labels))

                            # Log the labels for debugging
                            print(f"Fetched labels: {st.session_state.available_labels}")
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
            st.info(f"URI: {st.session_state.neo4j_connection.uri}")
            st.info(f"Database: {st.session_state.neo4j_connection.database}")

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

    # Display available terms and labels
    # First, display Neo4j labels as a "Local" ontology
    if st.session_state.available_labels:
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
                print(f"Error creating OntologySource: {e}")
                # Fallback to string if OntologySource creation fails
                local_source = "Local"

            # Add Neo4j labels to terms as a "Local" ontology
            local_terms = []
            for label in st.session_state.available_labels:
                if label and isinstance(label, str):
                    local_terms.append(OntologyAnnotation(
                        term=label,
                        term_accession=f"neo4j:label:{label}",
                        term_source=local_source
                    ))

            # Log the local terms for debugging
            print(f"Created {len(local_terms)} Local ontology terms from Neo4j labels")

            # Add local terms to session state if they don't exist yet
            existing_accessions = {term.term_accession for term in st.session_state.terms}
            added_count = 0
            for term in local_terms:
                if term.term_accession not in existing_accessions:
                    st.session_state.terms.append(term)
                    existing_accessions.add(term.term_accession)
                    added_count += 1

            # Log the number of terms added
            if added_count > 0:
                print(f"Added {added_count} new Local ontology terms to session state")
        except Exception as e:
            print(f"Error creating Local ontology terms: {e}")

    # Display available terms
    if st.session_state.terms:
        # Add search functionality
        search_term = st.sidebar.text_input("Search terms", key="term_search")

        # Group terms by source
        terms_by_source = {}
        for term in st.session_state.terms:
            source = term.term_source
            source_name = source.name if hasattr(source, 'name') else str(source)
            if source_name not in terms_by_source:
                terms_by_source[source_name] = []
            terms_by_source[source_name].append(term)

        # Create a selectbox to choose the source
        source_options = list(terms_by_source.keys())
        if source_options:
            selected_source = st.sidebar.selectbox("Select Source", source_options)

            # Display terms for the selected source
            terms = terms_by_source[selected_source]
            sorted_terms = sorted(terms, key=lambda x: x.term)

            # Filter terms based on search
            if search_term:
                filtered_terms = [term for term in sorted_terms if search_term.lower() in term.term.lower()]
            else:
                filtered_terms = sorted_terms

            # Display the terms in a simple list
            if not filtered_terms:
                st.sidebar.info(f"No matching terms in {selected_source}")
            else:
                st.sidebar.markdown(f"**{selected_source}** ({len(filtered_terms)} terms)")
                for term in filtered_terms:
                    st.sidebar.markdown(f"- {term.term}")
    else:
        st.sidebar.info("No terms loaded yet.")

    # Main content area
    uploaded = st.file_uploader("Upload an ISA-Tab file (zipped) or select local path", type=["txt", "zip", "json"], key="isa_file_uploader")

    # Ontology Terms Management section in main content
    st.subheader("Ontology Terms Management")

    # Create tabs for different term sources
    term_tabs = st.tabs(["ISA Terms", "cBioPortal Terms", "Term Management"])

    # Tab 1: ISA Terms
    with term_tabs[0]:
        st.subheader("Standard ISA Terms")
        if st.button("Load Standard ISA Terms", key="load_standard_isa_terms_button"):
            try:
                standard_terms = get_standard_isa_terms()

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
                new_terms = load_ontomaton_terms(terms_file)

                # Option to append or replace existing terms
                action = st.radio(
                    "What would you like to do with these terms?",
                    ["Add to existing terms", "Replace existing terms"]
                )

                if st.button("Process Terms", key="process_custom_terms_button"):
                    try:
                        if action == "Replace existing terms":
                            st.session_state.terms = new_terms
                        else:  # Add to existing terms
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
                                st.success(f"Added {added_count} custom terms.")
                            else:
                                st.info("No new terms were added.")

                        st.success(f"Now managing {len(st.session_state.terms)} ontology terms.")
                    except Exception as e:
                        st.error(f"Error processing custom terms: {e}")
            except Exception as e:
                st.error(f"Failed to load terms: {e}")

    # Tab 2: cBioPortal Terms
    with term_tabs[1]:
        st.subheader("cBioPortal Cancer Types")
        if st.button("Load Cancer Types", key="load_cancer_types_button"):
            try:
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
                        st.success(f"Added {added_count} cancer type terms.")
                    else:
                        st.info("All cancer type terms are already loaded.")
                else:
                    st.warning("Failed to load cancer types.")
            except Exception as e:
                st.error(f"Error loading cancer types: {e}")

        # OncoTree Tumor Types
        st.subheader("OncoTree Tumor Types")
        if st.button("Load Tumor Types", key="load_tumor_types_button"):
            try:
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
                        st.success(f"Added {added_count} tumor type terms.")
                    else:
                        st.info("All tumor type terms are already loaded.")
                else:
                    st.warning("Failed to load tumor types.")
            except Exception as e:
                st.error(f"Error loading tumor types: {e}")

        # cBioPortal Studies
        st.subheader("cBioPortal Studies")
        studies = get_cbioportal_studies()
        if studies:
            study_names = [study.get("name", "") for study in studies]
            study_ids = [study.get("studyId", "") for study in studies]

            selected_study_index = st.selectbox(
                "Select a study to explore",
                range(len(study_names)),
                format_func=lambda i: study_names[i]
            )

            if st.button("Load Study Data", key="load_study_data_button"):
                try:
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
                            st.success(f"Added {added_count} terms from study.")
                        else:
                            st.info("No new terms found in study.")
                    else:
                        st.warning("Failed to load study data.")
                except Exception as e:
                    st.error(f"Error loading study data: {e}")

    # Tab 3: Term Management
    with term_tabs[2]:
        # Create subtabs for different term management views
        term_subtabs = st.tabs(["Add Term", "Edit/Remove Term"])

        # Tab 1: Add Term
        with term_subtabs[0]:
            st.subheader("Add New Term")

            with st.form("add_term_form_main"):
                term_name = st.text_input("Term Name")
                term_uri = st.text_input("Term URI")

                # Source selection with option to create new source
                source_options = ["Create New Source"] + sorted(set([
                    term.term_source.name if hasattr(term.term_source, 'name') else str(term.term_source) 
                    for term in st.session_state.terms
                ]))
                selected_source_option = st.selectbox("Ontology Source", source_options)

                if selected_source_option == "Create New Source":
                    source_name = st.text_input("Source Name")
                    source_file = st.text_input("Source File (optional)")
                    source_version = st.text_input("Source Version (optional)")
                    source_description = st.text_area("Source Description (optional)")
                else:
                    source_name = selected_source_option

                submit_button = st.form_submit_button("Add Term")

                if submit_button and term_name and term_uri:
                    try:
                        # Create or find the ontology source
                        if selected_source_option == "Create New Source" and source_name:
                            # Create a new OntologySource
                            term_source = OntologySource(
                                name=source_name,
                                file=source_file,
                                version=source_version,
                                description=source_description
                            )
                        else:
                            # Find existing source
                            term_source = None
                            for term in st.session_state.terms:
                                if (hasattr(term.term_source, 'name') and term.term_source.name == source_name) or str(term.term_source) == source_name:
                                    term_source = term.term_source
                                    break

                            # If not found, use the name as a string
                            if term_source is None:
                                term_source = source_name

                        # Create the new term
                        new_term = OntologyAnnotation(
                            term=term_name,
                            term_accession=term_uri,
                            term_source=term_source
                        )

                        # Check if term already exists
                        existing_accessions = {term.term_accession for term in st.session_state.terms}
                        if new_term.term_accession not in existing_accessions:
                            st.session_state.terms.append(new_term)
                            st.success(f"Added term: {term_name}")
                        else:
                            st.warning(f"Term with URI {term_uri} already exists.")
                    except Exception as e:
                        st.error(f"Error adding term: {e}")

        # Tab 2: Edit/Remove Term
        with term_subtabs[1]:
            st.subheader("Edit or Remove Terms")

            # Term management options
            term_management_option = st.radio(
                "Select Action",
                ["Edit Term", "Remove Term"]
            )

            if not st.session_state.terms:
                st.warning("No terms available to edit or remove.")
            else:
                # Create a list of term names with their sources for the selectbox
                term_options = []
                for i, term in enumerate(st.session_state.terms):
                    source_name = term.term_source.name if hasattr(term.term_source, 'name') else str(term.term_source)
                    term_options.append(f"{term.term} ({source_name})")

                selected_term_index = st.selectbox(
                    "Select Term", 
                    range(len(term_options)), 
                    format_func=lambda i: term_options[i]
                )

                selected_term = st.session_state.terms[selected_term_index]

                if term_management_option == "Remove Term":
                    if st.button("Remove Selected Term"):
                        removed_term = st.session_state.terms.pop(selected_term_index)
                        st.success(f"Removed term: {removed_term.term}")

                elif term_management_option == "Edit Term":
                    with st.form("edit_term_form"):
                        new_term_name = st.text_input("Term Name", value=selected_term.term)
                        new_term_uri = st.text_input("Term URI", value=selected_term.term_accession)

                        # Source editing
                        current_source = selected_term.term_source
                        current_source_name = current_source.name if hasattr(current_source, 'name') else str(current_source)

                        source_options = ["Keep Current Source", "Create New Source"] + sorted(set([
                            term.term_source.name if hasattr(term.term_source, 'name') else str(term.term_source) 
                            for term in st.session_state.terms
                            if (hasattr(term.term_source, 'name') and term.term_source.name != current_source_name) or 
                               (not hasattr(term.term_source, 'name') and str(term.term_source) != current_source_name)
                        ]))

                        selected_source_option = st.selectbox("Source Option", source_options)

                        if selected_source_option == "Create New Source":
                            new_source_name = st.text_input("Source Name")
                            new_source_file = st.text_input("Source File (optional)")
                            new_source_version = st.text_input("Source Version (optional)")
                            new_source_description = st.text_area("Source Description (optional)")
                        elif selected_source_option != "Keep Current Source":
                            new_source_name = selected_source_option

                        update_button = st.form_submit_button("Update Term")

                        if update_button:
                            try:
                                # Check if the new URI already exists in another term
                                if new_term_uri != selected_term.term_accession:
                                    existing_accessions = {term.term_accession for i, term in enumerate(st.session_state.terms) if i != selected_term_index}
                                    if new_term_uri in existing_accessions:
                                        st.warning(f"Term with URI {new_term_uri} already exists.")
                                        st.stop()

                                # Update the term name and URI
                                st.session_state.terms[selected_term_index].term = new_term_name
                                st.session_state.terms[selected_term_index].term_accession = new_term_uri

                                # Update the source if needed
                                if selected_source_option == "Create New Source" and new_source_name:
                                    # Create a new OntologySource
                                    new_source = OntologySource(
                                        name=new_source_name,
                                        file=new_source_file,
                                        version=new_source_version,
                                        description=new_source_description
                                    )
                                    st.session_state.terms[selected_term_index].term_source = new_source
                                elif selected_source_option != "Keep Current Source":
                                    # Find existing source
                                    for term in st.session_state.terms:
                                        if (hasattr(term.term_source, 'name') and term.term_source.name == new_source_name) or str(term.term_source) == new_source_name:
                                            st.session_state.terms[selected_term_index].term_source = term.term_source
                                            break

                                st.success(f"Updated term: {new_term_name}")
                            except Exception as e:
                                st.error(f"Error updating term: {e}")

        # Neo4j Integration
        if st.session_state.neo4j_connected:
            st.subheader("Neo4j Integration")

            # Pull terms from Neo4j
            if st.button("Pull Terms from Neo4j", key="pull_terms_from_neo4j_button"):
                try:
                    # Get all labels
                    all_labels_query = "MATCH (n) RETURN DISTINCT labels(n) as labels"
                    label_results = st.session_state.neo4j_connection.execute_query(all_labels_query)
                    all_labels = sorted(set([label for result in label_results for labels_list in result["labels"] for label in labels_list]))
                    st.session_state.available_labels = all_labels

                    # Get terms that look like ontology terms (having a URI pattern)
                    term_query = """
                    MATCH (n)
                    UNWIND keys(n) AS property
                    WITH property, n[property] AS value
                    WHERE toString(value) CONTAINS "://"
                    RETURN DISTINCT property, value
                    LIMIT 100
                    """
                    term_results = st.session_state.neo4j_connection.execute_query(term_query)

                    # Create a proper OntologySource for Neo4j terms
                    neo4j_source = None
                    try:
                        # Check if we already have a Neo4j ontology source in the session state
                        for term in st.session_state.terms:
                            if hasattr(term.term_source, 'name') and term.term_source.name == "Neo4j":
                                neo4j_source = term.term_source
                                break

                        # If not found, create a new one
                        if not neo4j_source:
                            neo4j_source = OntologySource(
                                name="Neo4j",
                                file="",
                                version="1.0",
                                description="Terms extracted from Neo4j database properties"
                            )
                    except Exception as e:
                        print(f"Error creating Neo4j OntologySource: {e}")
                        # Fallback to string if OntologySource creation fails
                        neo4j_source = "Neo4j"

                    # Convert to OntologyAnnotation objects
                    new_terms = []
                    for record in term_results:
                        prop = record["property"]
                        value = record["value"]
                        if isinstance(value, str) and "://" in value:
                            # Try to extract a term name from the URI
                            term_name = value.split("/")[-1].replace("_", " ").title()
                            # Add property name as part of the term for better context
                            full_term_name = f"{term_name} ({prop})"
                            new_term = OntologyAnnotation(
                                term=full_term_name,
                                term_accession=value,
                                term_source=neo4j_source
                            )
                            new_terms.append(new_term)

                    # Add to session state
                    existing_accessions = {term.term_accession for term in st.session_state.terms}
                    added_count = 0
                    for term in new_terms:
                        if term.term_accession not in existing_accessions:
                            st.session_state.terms.append(term)
                            existing_accessions.add(term.term_accession)
                            added_count += 1

                    if added_count > 0:
                        st.success(f"Added {added_count} terms from Neo4j.")
                    else:
                        st.info("No new terms found in Neo4j.")

                except Exception as e:
                    st.error(f"Error pulling terms from Neo4j: {e}")

            # Load terms to Neo4j
            st.subheader("Load Terms to Neo4j")
            create_sources = st.checkbox("Create Ontology Source Nodes", value=True)
            relationship_type = st.text_input("Relationship Type", value="HAS_TERM")

            if st.button("Load Ontology Terms to Neo4j", key="load_ontology_terms_to_neo4j_button"):
                if not st.session_state.terms:
                    st.warning("No ontology terms to load. Please add terms first.")
                else:
                    with st.spinner(f"Loading {len(st.session_state.terms)} ontology terms into Neo4j..."):
                        try:
                            relationships_created = st.session_state.neo4j_connection.load_ontology_relationships(
                                st.session_state.terms,
                                create_source_nodes=create_sources,
                                relationship_type=relationship_type
                            )

                            st.success(f"Successfully loaded ontology terms into Neo4j. Created {relationships_created} relationships.")

                            # Show a sample Cypher query to view the data
                            st.subheader("View the Data in Neo4j")
                            st.code(f"""
MATCH (s:OntologySource)-[r:{relationship_type}]->(t:OntologyTerm)
RETURN s, r, t LIMIT 25
                            """, language="cypher")
                        except Exception as e:
                            st.error(f"Error loading ontology terms into Neo4j: {e}")
        else:
            st.warning("Connect to Neo4j to enable term integration with the graph database.")

    # ISA-Tab file processing
    if uploaded:
        file_path = Path(uploaded.name)
        if file_path.suffix == ".json":
            inv = isatab.load(uploaded)
        else:
            inv = isatab.load(uploaded)

        st.success("ISA object loaded.")

        # Nodes
        node_classes = extract_node_classes(inv)
        st.subheader("ISA Node Types → Neo4j Labels")
        selected_node = st.selectbox("Choose a node class to inspect", node_classes)
        st.write(f"Neo4j Label: `{selected_node}`")

        props = extract_properties(inv, selected_node)
        if props:
            st.markdown("#### Example Properties")
            st.write(props[:10])
        else:
            st.info("No example properties found.")

        # Relationships
        st.subheader("ISA Relationship Types → Neo4j Relationships")
        rels = extract_relationships(inv)
        for rel in rels:
            st.write(f"{rel[0]} -[{rel[1]}]-> {rel[2]}")

    else:
        st.info("Please upload an ISA-Tab or ISA-JSON file.")

if __name__ == "__main__":
    main()
