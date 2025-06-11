import streamlit as st
import pandas as pd
from isatools import isatab
from isatools.model import Investigation, Study, Assay, Process, Material, DataFile
from isatools.model import OntologyAnnotation
from pathlib import Path
from typing import List, Union
from io import BytesIO


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




def main():
    st.title("ISA Tools Browser for Neo4j Mapping")

    uploaded = st.file_uploader("Upload an ISA-Tab file (zipped) or select local path", type=["txt", "zip", "json"])

    
    # Upload widget for OntoMaton Terms
    st.sidebar.subheader("Upload OntoMaton Terms Table")
    terms_file = st.sidebar.file_uploader("Terms .xlsx or .tsv", type=["xlsx", "tsv", "csv"])
    
    if terms_file:
        try:
            terms = load_ontomaton_terms(terms_file)
            st.success(f"Loaded {len(terms)} ontology terms.")
            with st.expander("📋 View Terms"):
                for ann in terms:
                    st.markdown(f"- **{ann.term}** ({ann.term_source}) → `{ann.term_accession}`")
        except Exception as e:
            st.error(f"Failed to load terms: {e}")
  
    
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

