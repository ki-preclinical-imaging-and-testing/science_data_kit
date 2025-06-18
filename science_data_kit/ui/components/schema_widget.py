"""
Schema Widget Component for Science Data Kit

This module provides a widget for visualizing and editing database schemas.
It includes functions for rendering schema diagrams, editing schema properties,
and managing schema relationships.
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Union, Callable
import pandas as pd
import networkx as nx
from pyvis.network import Network
import json
import io
import base64
from pathlib import Path

def render_schema_diagram(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    height: int = 600,
    width: str = "100%",
    directed: bool = True,
    physics: bool = True,
    node_color: str = "#1E88E5",
    edge_color: str = "#666666",
    title: Optional[str] = None
) -> None:
    """
    Render a schema diagram using Pyvis Network.
    
    Args:
        nodes: List of node dictionaries with 'id', 'label', and optional 'title' and 'properties'.
        edges: List of edge dictionaries with 'from', 'to', 'label', and optional 'title'.
        height: Height of the diagram in pixels.
        width: Width of the diagram (can be pixels or percentage).
        directed: Whether the graph is directed.
        physics: Whether to enable physics simulation.
        node_color: Default color for nodes.
        edge_color: Default color for edges.
        title: Optional title for the diagram.
    """
    # Create a network graph
    net = Network(height=height, width=width, directed=directed, notebook=False)
    
    # Configure network options
    net.toggle_physics(physics)
    
    # Set title if provided
    if title:
        net.set_options(f'{{"title": "{title}"}}')
    
    # Add nodes to the network
    for node in nodes:
        node_id = node.get('id')
        label = node.get('label', str(node_id))
        title = node.get('title', label)
        
        # Format properties as HTML if available
        if 'properties' in node:
            props_html = "<ul>"
            for key, value in node['properties'].items():
                props_html += f"<li><b>{key}:</b> {value}</li>"
            props_html += "</ul>"
            title = f"<h3>{label}</h3>{props_html}"
        
        # Add the node to the network
        net.add_node(
            node_id, 
            label=label, 
            title=title,
            color=node.get('color', node_color)
        )
    
    # Add edges to the network
    for edge in edges:
        from_node = edge.get('from')
        to_node = edge.get('to')
        label = edge.get('label', '')
        title = edge.get('title', label)
        
        # Add the edge to the network
        net.add_edge(
            from_node, 
            to_node, 
            label=label, 
            title=title,
            color=edge.get('color', edge_color)
        )
    
    # Generate the HTML
    html = net.generate_html()
    
    # Display the network in Streamlit
    st.components.v1.html(html, height=height, width=width)

def render_schema_editor(
    schema: Dict[str, Any],
    on_save: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Render a schema editor widget.
    
    Args:
        schema: Dictionary containing the schema definition.
        on_save: Optional callback function to call when the save button is clicked.
        
    Returns:
        The updated schema dictionary.
    """
    st.subheader("Schema Editor")
    
    # Create a copy of the schema to avoid modifying the original
    updated_schema = schema.copy()
    
    # Create tabs for different aspects of the schema
    tab1, tab2, tab3 = st.tabs(["Nodes", "Relationships", "Properties"])
    
    with tab1:
        st.subheader("Node Types")
        
        # Display existing node types
        if 'nodes' in updated_schema:
            for i, node in enumerate(updated_schema['nodes']):
                with st.expander(f"Node: {node.get('label', f'Node {i}')}"):
                    # Edit node properties
                    node['label'] = st.text_input(f"Label", node.get('label', ''), key=f"node_label_{i}")
                    
                    # Edit node properties
                    if 'properties' not in node:
                        node['properties'] = {}
                    
                    st.subheader("Properties")
                    props = node['properties']
                    
                    # Display existing properties
                    for prop_key in list(props.keys()):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            new_key = st.text_input(f"Key", prop_key, key=f"prop_key_{i}_{prop_key}")
                        with col2:
                            props[prop_key] = st.text_input(f"Value", props[prop_key], key=f"prop_val_{i}_{prop_key}")
                        with col3:
                            if st.button("Delete", key=f"del_prop_{i}_{prop_key}"):
                                del props[prop_key]
                    
                    # Add new property
                    with st.expander("Add Property"):
                        new_prop_key = st.text_input("New Property Key", "", key=f"new_prop_key_{i}")
                        new_prop_val = st.text_input("New Property Value", "", key=f"new_prop_val_{i}")
                        if st.button("Add", key=f"add_prop_{i}"):
                            if new_prop_key:
                                props[new_prop_key] = new_prop_val
        
        # Add new node type
        with st.expander("Add New Node Type"):
            new_node_label = st.text_input("Node Label", "")
            if st.button("Add Node Type"):
                if new_node_label:
                    if 'nodes' not in updated_schema:
                        updated_schema['nodes'] = []
                    updated_schema['nodes'].append({
                        'id': len(updated_schema['nodes']),
                        'label': new_node_label,
                        'properties': {}
                    })
    
    with tab2:
        st.subheader("Relationships")
        
        # Display existing relationships
        if 'edges' in updated_schema:
            for i, edge in enumerate(updated_schema['edges']):
                with st.expander(f"Relationship: {edge.get('label', f'Relationship {i}')}"):
                    # Get node options
                    node_options = []
                    if 'nodes' in updated_schema:
                        node_options = [node.get('label', f"Node {j}") for j, node in enumerate(updated_schema['nodes'])]
                    
                    # Edit relationship properties
                    from_idx = 0
                    to_idx = 0
                    
                    if node_options:
                        # Find current indices
                        if 'from' in edge and edge['from'] < len(node_options):
                            from_idx = edge['from']
                        if 'to' in edge and edge['to'] < len(node_options):
                            to_idx = edge['to']
                        
                        # Edit source and target nodes
                        from_node = st.selectbox(f"From", node_options, index=from_idx, key=f"edge_from_{i}")
                        to_node = st.selectbox(f"To", node_options, index=to_idx, key=f"edge_to_{i}")
                        
                        # Update edge
                        edge['from'] = node_options.index(from_node)
                        edge['to'] = node_options.index(to_node)
                    
                    # Edit label
                    edge['label'] = st.text_input(f"Label", edge.get('label', ''), key=f"edge_label_{i}")
        
        # Add new relationship
        with st.expander("Add New Relationship"):
            # Get node options
            node_options = []
            if 'nodes' in updated_schema:
                node_options = [node.get('label', f"Node {i}") for i, node in enumerate(updated_schema['nodes'])]
            
            if node_options:
                from_node = st.selectbox("From", node_options, key="new_edge_from")
                to_node = st.selectbox("To", node_options, key="new_edge_to")
                new_edge_label = st.text_input("Relationship Label", "")
                
                if st.button("Add Relationship"):
                    if 'edges' not in updated_schema:
                        updated_schema['edges'] = []
                    updated_schema['edges'].append({
                        'from': node_options.index(from_node),
                        'to': node_options.index(to_node),
                        'label': new_edge_label
                    })
            else:
                st.warning("Add node types first before creating relationships.")
    
    with tab3:
        st.subheader("Schema Properties")
        
        # Edit schema-level properties
        if 'properties' not in updated_schema:
            updated_schema['properties'] = {}
        
        props = updated_schema['properties']
        
        # Display existing properties
        for prop_key in list(props.keys()):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                new_key = st.text_input(f"Key", prop_key, key=f"schema_prop_key_{prop_key}")
            with col2:
                props[prop_key] = st.text_input(f"Value", props[prop_key], key=f"schema_prop_val_{prop_key}")
            with col3:
                if st.button("Delete", key=f"del_schema_prop_{prop_key}"):
                    del props[prop_key]
        
        # Add new property
        with st.expander("Add Property"):
            new_prop_key = st.text_input("New Property Key", "", key="new_schema_prop_key")
            new_prop_val = st.text_input("New Property Value", "", key="new_schema_prop_val")
            if st.button("Add", key="add_schema_prop"):
                if new_prop_key:
                    props[new_prop_key] = new_prop_val
    
    # Save button
    if st.button("Save Schema"):
        if on_save:
            on_save(updated_schema)
        st.success("Schema saved successfully!")
    
    return updated_schema

def render_schema_import_export(
    on_import: Optional[Callable[[Dict[str, Any]], None]] = None,
    schema: Optional[Dict[str, Any]] = None
) -> None:
    """
    Render schema import and export widgets.
    
    Args:
        on_import: Optional callback function to call when a schema is imported.
        schema: Optional schema to export.
    """
    st.subheader("Import/Export Schema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Import Schema")
        uploaded_file = st.file_uploader("Upload Schema JSON", type=["json"])
        
        if uploaded_file is not None:
            try:
                imported_schema = json.load(uploaded_file)
                st.success("Schema imported successfully!")
                
                if on_import:
                    on_import(imported_schema)
            except Exception as e:
                st.error(f"Error importing schema: {e}")
    
    with col2:
        st.subheader("Export Schema")
        
        if schema:
            # Convert schema to JSON
            schema_json = json.dumps(schema, indent=2)
            
            # Create a download link
            b64 = base64.b64encode(schema_json.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64}" download="schema.json">Download Schema JSON</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning("No schema available for export.")

def render_schema_widget(
    schema: Optional[Dict[str, Any]] = None,
    on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_import: Optional[Callable[[Dict[str, Any]], None]] = None,
    height: int = 600,
    width: str = "100%"
) -> Dict[str, Any]:
    """
    Render the complete schema widget with diagram, editor, and import/export.
    
    Args:
        schema: Optional dictionary containing the schema definition.
        on_save: Optional callback function to call when the save button is clicked.
        on_import: Optional callback function to call when a schema is imported.
        height: Height of the diagram in pixels.
        width: Width of the diagram (can be pixels or percentage).
        
    Returns:
        The updated schema dictionary.
    """
    st.header("Schema Widget")
    
    # Initialize schema if not provided
    if schema is None:
        schema = {
            'nodes': [],
            'edges': [],
            'properties': {}
        }
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Diagram", "Editor", "Import/Export"])
    
    with tab1:
        # Render schema diagram if nodes and edges are available
        if 'nodes' in schema and 'edges' in schema and schema['nodes']:
            render_schema_diagram(
                nodes=schema['nodes'],
                edges=schema['edges'],
                height=height,
                width=width,
                title=schema.get('properties', {}).get('title', 'Schema Diagram')
            )
        else:
            st.info("No schema data available. Use the Editor tab to create a schema.")
    
    with tab2:
        # Render schema editor
        updated_schema = render_schema_editor(schema, on_save)
    
    with tab3:
        # Render import/export widgets
        render_schema_import_export(on_import, schema)
    
    return updated_schema