import streamlit as st
import pandas as pd
from pathlib import Path
from typing import List, Union
from io import BytesIO

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


def main():
    st.title("ISA Tools Browser for Neo4j Mapping")

    # Initialize session state for storing terms
    if 'terms' not in st.session_state:
        st.session_state.terms = []

    # Display a warning if isatools is not available
    if not ISATOOLS_AVAILABLE:
        st.warning(
            "⚠️ The isatools package is not available in this Python environment. "
            "Some functionality will be limited. "
            "For full functionality, please use Python 3.9 with isatools installed."
        )

    uploaded = st.file_uploader("Upload an ISA-Tab file (zipped) or select local path", type=["txt", "zip", "json"])

    # Sidebar for term management
    st.sidebar.subheader("Ontology Terms Management")

    # Standard ISA terms button
    st.sidebar.subheader("Standard ISA Terms")
    if st.sidebar.button("Load Standard ISA Terms"):
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
            st.sidebar.success(f"Added {added_count} standard ISA terms.")
        else:
            st.sidebar.info("All standard terms are already loaded.")

    # Upload widget for OntoMaton Terms
    st.sidebar.subheader("Upload Custom Terms")
    terms_file = st.sidebar.file_uploader("Upload Terms .xlsx or .tsv", type=["xlsx", "tsv", "csv"])

    if terms_file:
        try:
            new_terms = load_ontomaton_terms(terms_file)

            # Option to append or replace existing terms
            action = st.sidebar.radio(
                "What would you like to do with these terms?",
                ["Add to existing terms", "Replace existing terms"]
            )

            if st.sidebar.button("Process Terms"):
                if action == "Replace existing terms":
                    st.session_state.terms = new_terms
                else:  # Add to existing terms
                    # Create a set of existing term accessions to avoid duplicates
                    existing_accessions = {term.term_accession for term in st.session_state.terms}

                    # Add only new terms that don't exist yet
                    for term in new_terms:
                        if term.term_accession not in existing_accessions:
                            st.session_state.terms.append(term)
                            existing_accessions.add(term.term_accession)

                st.success(f"Now managing {len(st.session_state.terms)} ontology terms.")
        except Exception as e:
            st.error(f"Failed to load terms: {e}")

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
            for i, ann in enumerate(st.session_state.terms):
                st.markdown(f"{i+1}. **{ann.term}** ({ann.term_source}) → `{ann.term_accession}`")
    else:
        st.info("No terms loaded yet. Upload a terms file or add terms manually.")

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
