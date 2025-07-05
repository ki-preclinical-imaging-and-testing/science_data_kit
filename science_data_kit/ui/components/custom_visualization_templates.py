"""
Custom Visualization Templates Module for Science Data Kit

This module provides functionality for creating, saving, loading, and applying
custom visualization templates. It extends the base visualization templates
with user-defined customizations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import json
import os
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
import seaborn as sns
from datetime import datetime

from science_data_kit.ui.components.visualization_templates import (
    create_bar_chart,
    create_line_chart,
    create_scatter_plot,
    create_pie_chart,
    create_network_graph,
    create_heatmap,
    create_box_plot,
    create_histogram,
    render_visualization
)

# Define the directory for storing custom templates
TEMPLATES_DIR = os.path.join(os.path.expanduser("~"), ".science_data_kit", "templates")

# Ensure the templates directory exists
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Template type definitions
TEMPLATE_TYPES = {
    "bar_chart": {
        "function": create_bar_chart,
        "required_params": ["data", "x_column", "y_column"],
        "optional_params": [
            "title", "x_label", "y_label", "color", "orientation", 
            "figsize", "show_values", "sort_values", "sort_ascending"
        ]
    },
    "line_chart": {
        "function": create_line_chart,
        "required_params": ["data", "x_column", "y_columns"],
        "optional_params": [
            "title", "x_label", "y_label", "colors", "figsize", 
            "show_markers", "show_legend", "grid"
        ]
    },
    "scatter_plot": {
        "function": create_scatter_plot,
        "required_params": ["data", "x_column", "y_column"],
        "optional_params": [
            "title", "x_label", "y_label", "color_column", "size_column", 
            "figsize", "alpha", "show_trend_line", "grid"
        ]
    },
    "pie_chart": {
        "function": create_pie_chart,
        "required_params": ["data", "label_column", "value_column"],
        "optional_params": [
            "title", "colors", "figsize", "show_percentages", 
            "show_labels", "explode", "start_angle"
        ]
    },
    "network_graph": {
        "function": create_network_graph,
        "required_params": ["nodes", "edges", "source_column", "target_column"],
        "optional_params": [
            "node_label_column", "node_size_column", "node_color_column", 
            "edge_weight_column", "title", "figsize", "node_size_default", 
            "edge_width_default", "layout"
        ]
    },
    "heatmap": {
        "function": create_heatmap,
        "required_params": ["data"],
        "optional_params": [
            "x_column", "y_column", "value_column", "title", "x_label", 
            "y_label", "figsize", "cmap", "show_values", "value_format", "center"
        ]
    },
    "box_plot": {
        "function": create_box_plot,
        "required_params": ["data", "y_column"],
        "optional_params": [
            "x_column", "title", "x_label", "y_label", "figsize", 
            "color", "notch", "grid", "orientation"
        ]
    },
    "histogram": {
        "function": create_histogram,
        "required_params": ["data", "column"],
        "optional_params": [
            "title", "x_label", "y_label", "figsize", "bins", 
            "color", "kde", "grid", "show_stats"
        ]
    }
}

def save_template(name: str, template_type: str, params: Dict[str, Any]) -> bool:
    """
    Save a custom visualization template.
    
    Args:
        name: The name of the template
        template_type: The type of visualization (bar_chart, line_chart, etc.)
        params: The parameters for the visualization
        
    Returns:
        bool: True if the template was saved successfully, False otherwise
    """
    if template_type not in TEMPLATE_TYPES:
        st.error(f"Invalid template type: {template_type}")
        return False
    
    # Create a template object
    template = {
        "name": name,
        "type": template_type,
        "params": params,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Save the template to a file
    filename = os.path.join(TEMPLATES_DIR, f"{name.lower().replace(' ', '_')}.json")
    try:
        with open(filename, 'w') as f:
            json.dump(template, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving template: {str(e)}")
        return False

def load_template(name: str) -> Optional[Dict[str, Any]]:
    """
    Load a custom visualization template.
    
    Args:
        name: The name of the template
        
    Returns:
        Optional[Dict[str, Any]]: The template if found, None otherwise
    """
    filename = os.path.join(TEMPLATES_DIR, f"{name.lower().replace(' ', '_')}.json")
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        st.error(f"Error loading template: {str(e)}")
        return None

def list_templates() -> List[str]:
    """
    List all available custom visualization templates.
    
    Returns:
        List[str]: A list of template names
    """
    try:
        files = os.listdir(TEMPLATES_DIR)
        templates = [os.path.splitext(f)[0].replace('_', ' ').title() 
                    for f in files if f.endswith('.json')]
        return templates
    except Exception as e:
        st.error(f"Error listing templates: {str(e)}")
        return []

def delete_template(name: str) -> bool:
    """
    Delete a custom visualization template.
    
    Args:
        name: The name of the template
        
    Returns:
        bool: True if the template was deleted successfully, False otherwise
    """
    filename = os.path.join(TEMPLATES_DIR, f"{name.lower().replace(' ', '_')}.json")
    try:
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False
    except Exception as e:
        st.error(f"Error deleting template: {str(e)}")
        return False

def apply_template(template: Dict[str, Any], data: pd.DataFrame) -> Optional[str]:
    """
    Apply a visualization template to data.
    
    Args:
        template: The template to apply
        data: The data to visualize
        
    Returns:
        Optional[str]: The base64-encoded image data if successful, None otherwise
    """
    template_type = template.get("type")
    params = template.get("params", {})
    
    if template_type not in TEMPLATE_TYPES:
        st.error(f"Invalid template type: {template_type}")
        return None
    
    # Get the visualization function
    viz_function = TEMPLATE_TYPES[template_type]["function"]
    
    # Prepare the parameters
    function_params = {"data": data}
    for key, value in params.items():
        if key not in ["data"]:  # Skip the data parameter as we're providing it
            function_params[key] = value
    
    try:
        # Call the visualization function
        return viz_function(**function_params)
    except Exception as e:
        st.error(f"Error applying template: {str(e)}")
        return None

def render_template_manager():
    """
    Render the template manager UI.
    
    This function provides a UI for creating, editing, and deleting custom templates.
    """
    st.subheader("Custom Visualization Templates")
    
    # Create tabs for managing templates
    tab1, tab2, tab3 = st.tabs(["Create Template", "Apply Template", "Manage Templates"])
    
    with tab1:
        st.write("Create a new custom visualization template")
        
        # Template name
        template_name = st.text_input("Template Name", key="template_name")
        
        # Template type
        template_type = st.selectbox(
            "Visualization Type",
            options=list(TEMPLATE_TYPES.keys()),
            format_func=lambda x: x.replace("_", " ").title(),
            key="template_type"
        )
        
        # Show parameters based on the selected template type
        if template_type:
            st.write("### Required Parameters")
            required_params = {}
            for param in TEMPLATE_TYPES[template_type]["required_params"]:
                if param == "data":
                    continue  # Skip data parameter as it will be provided when applying the template
                
                # For parameters that expect column names, we'll use text input
                # In a real implementation, you might want to show a dropdown of available columns
                required_params[param] = st.text_input(f"{param.replace('_', ' ').title()}", key=f"req_{param}")
            
            st.write("### Optional Parameters")
            optional_params = {}
            for param in TEMPLATE_TYPES[template_type]["optional_params"]:
                # For simplicity, we'll use text input for all parameters
                # In a real implementation, you might want to use appropriate input widgets
                # based on the parameter type (e.g., color picker for color parameters)
                optional_params[param] = st.text_input(
                    f"{param.replace('_', ' ').title()} (optional)",
                    key=f"opt_{param}"
                )
            
            # Remove empty optional parameters
            optional_params = {k: v for k, v in optional_params.items() if v}
            
            # Combine parameters
            all_params = {**required_params, **optional_params}
            
            # Save button
            if st.button("Save Template", key="save_template"):
                if not template_name:
                    st.error("Please enter a template name")
                elif not all(required_params.values()):
                    st.error("Please fill in all required parameters")
                else:
                    success = save_template(template_name, template_type, all_params)
                    if success:
                        st.success(f"Template '{template_name}' saved successfully")
                    else:
                        st.error("Failed to save template")
    
    with tab2:
        st.write("Apply a custom visualization template to your data")
        
        # List available templates
        templates = list_templates()
        if not templates:
            st.info("No custom templates available. Create a template in the 'Create Template' tab.")
        else:
            selected_template = st.selectbox(
                "Select Template",
                options=templates,
                key="apply_template"
            )
            
            if selected_template:
                # Load the template
                template = load_template(selected_template)
                if template:
                    st.write(f"Template Type: {template['type'].replace('_', ' ').title()}")
                    st.write("Parameters:")
                    for key, value in template["params"].items():
                        st.write(f"- {key.replace('_', ' ').title()}: {value}")
                    
                    # In a real implementation, you would provide a way for users to select data
                    # For now, we'll just show a message
                    st.info("To apply this template, select data from your database or upload a file.")
    
    with tab3:
        st.write("Manage your custom visualization templates")
        
        # List available templates
        templates = list_templates()
        if not templates:
            st.info("No custom templates available. Create a template in the 'Create Template' tab.")
        else:
            selected_template = st.selectbox(
                "Select Template",
                options=templates,
                key="manage_template"
            )
            
            if selected_template:
                # Load the template
                template = load_template(selected_template)
                if template:
                    st.write(f"Template Type: {template['type'].replace('_', ' ').title()}")
                    st.write("Parameters:")
                    for key, value in template["params"].items():
                        st.write(f"- {key.replace('_', ' ').title()}: {value}")
                    
                    # Delete button
                    if st.button("Delete Template", key="delete_template"):
                        success = delete_template(selected_template)
                        if success:
                            st.success(f"Template '{selected_template}' deleted successfully")
                            st.experimental_rerun()  # Refresh the page
                        else:
                            st.error("Failed to delete template")