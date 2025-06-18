"""
Unit tests for the schema widget component.

This module contains tests for the schema widget component functions.
"""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
import json
import base64

from science_data_kit.ui.components.schema_widget import (
    render_schema_diagram,
    render_schema_editor,
    render_schema_import_export,
    render_schema_widget
)

def test_render_schema_diagram(mock_streamlit):
    """Test that the schema diagram is rendered correctly."""
    # Create test data
    nodes = [
        {'id': 1, 'label': 'Person'},
        {'id': 2, 'label': 'Movie'}
    ]
    edges = [
        {'from': 1, 'to': 2, 'label': 'ACTED_IN'}
    ]
    
    # Mock the Network class
    with patch('science_data_kit.ui.components.schema_widget.Network') as mock_network:
        # Configure the mock
        mock_network_instance = mock_network.return_value
        mock_network_instance.generate_html.return_value = "<html>Test</html>"
        
        # Call the function
        render_schema_diagram(nodes, edges)
        
        # Check that the Network was created with the correct parameters
        mock_network.assert_called_once()
        
        # Check that nodes were added
        assert mock_network_instance.add_node.call_count == 2
        mock_network_instance.add_node.assert_any_call(1, label='Person', title='Person', color='#1E88E5')
        mock_network_instance.add_node.assert_any_call(2, label='Movie', title='Movie', color='#1E88E5')
        
        # Check that edges were added
        mock_network_instance.add_edge.assert_called_once_with(1, 2, label='ACTED_IN', title='ACTED_IN', color='#666666')
        
        # Check that the HTML was generated and displayed
        mock_network_instance.generate_html.assert_called_once()
        mock_streamlit['components'].v1.html.assert_called_once_with("<html>Test</html>", height=600, width="100%")

def test_render_schema_editor_empty_schema(mock_streamlit):
    """Test that the schema editor handles an empty schema correctly."""
    # Create an empty schema
    schema = {}
    
    # Mock the tabs
    mock_tab1 = MagicMock()
    mock_tab2 = MagicMock()
    mock_tab3 = MagicMock()
    mock_streamlit['tabs'].return_value = (mock_tab1, mock_tab2, mock_tab3)
    
    # Call the function
    updated_schema = render_schema_editor(schema)
    
    # Check that the schema was initialized correctly
    assert 'nodes' in updated_schema
    assert 'edges' in updated_schema
    assert 'properties' in updated_schema
    
    # Check that the tabs were created
    mock_streamlit['tabs'].assert_called_once_with(["Nodes", "Relationships", "Properties"])
    
    # Check that the save button was created
    mock_streamlit['button'].assert_called_with("Save Schema")

def test_render_schema_editor_with_callback(mock_streamlit):
    """Test that the schema editor calls the callback when save is clicked."""
    # Create a schema
    schema = {
        'nodes': [{'id': 1, 'label': 'Person'}],
        'edges': [],
        'properties': {}
    }
    
    # Create a mock callback
    mock_callback = MagicMock()
    
    # Mock the tabs
    mock_tab1 = MagicMock()
    mock_tab2 = MagicMock()
    mock_tab3 = MagicMock()
    mock_streamlit['tabs'].return_value = (mock_tab1, mock_tab2, mock_tab3)
    
    # Mock the button to return True (clicked)
    mock_streamlit['button'].return_value = True
    
    # Call the function
    updated_schema = render_schema_editor(schema, on_save=mock_callback)
    
    # Check that the callback was called with the updated schema
    mock_callback.assert_called_once_with(updated_schema)
    
    # Check that a success message was displayed
    mock_streamlit['success'].assert_called_once_with("Schema saved successfully!")

def test_render_schema_import_export_no_schema(mock_streamlit):
    """Test that the import/export widget handles no schema correctly."""
    # Mock the columns
    mock_col1 = MagicMock()
    mock_col2 = MagicMock()
    mock_streamlit['columns'].return_value = (mock_col1, mock_col2)
    
    # Call the function
    render_schema_import_export()
    
    # Check that the file uploader was created
    mock_streamlit['file_uploader'].assert_called_once_with("Upload Schema JSON", type=["json"])
    
    # Check that a warning was displayed
    mock_streamlit['warning'].assert_called_once_with("No schema available for export.")

def test_render_schema_import_export_with_schema(mock_streamlit):
    """Test that the import/export widget handles a schema correctly."""
    # Create a schema
    schema = {
        'nodes': [{'id': 1, 'label': 'Person'}],
        'edges': [],
        'properties': {}
    }
    
    # Mock the columns
    mock_col1 = MagicMock()
    mock_col2 = MagicMock()
    mock_streamlit['columns'].return_value = (mock_col1, mock_col2)
    
    # Call the function
    render_schema_import_export(schema=schema)
    
    # Check that the file uploader was created
    mock_streamlit['file_uploader'].assert_called_once_with("Upload Schema JSON", type=["json"])
    
    # Check that the download link was created
    expected_json = json.dumps(schema, indent=2)
    expected_b64 = base64.b64encode(expected_json.encode()).decode()
    expected_href = f'<a href="data:application/json;base64,{expected_b64}" download="schema.json">Download Schema JSON</a>'
    mock_streamlit['markdown'].assert_called_once_with(expected_href, unsafe_allow_html=True)

def test_render_schema_import_export_with_callback(mock_streamlit):
    """Test that the import/export widget calls the callback when a file is uploaded."""
    # Create a mock callback
    mock_callback = MagicMock()
    
    # Mock the columns
    mock_col1 = MagicMock()
    mock_col2 = MagicMock()
    mock_streamlit['columns'].return_value = (mock_col1, mock_col2)
    
    # Mock the file uploader to return a file
    mock_file = MagicMock()
    mock_streamlit['file_uploader'].return_value = mock_file
    
    # Mock json.load to return a schema
    mock_schema = {'nodes': [], 'edges': []}
    with patch('json.load', return_value=mock_schema):
        # Call the function
        render_schema_import_export(on_import=mock_callback)
        
        # Check that the callback was called with the imported schema
        mock_callback.assert_called_once_with(mock_schema)
        
        # Check that a success message was displayed
        mock_streamlit['success'].assert_called_once_with("Schema imported successfully!")

def test_render_schema_widget(mock_streamlit):
    """Test that the schema widget is rendered correctly."""
    # Create a schema
    schema = {
        'nodes': [{'id': 1, 'label': 'Person'}],
        'edges': [],
        'properties': {'title': 'Test Schema'}
    }
    
    # Mock the tabs
    mock_tab1 = MagicMock()
    mock_tab2 = MagicMock()
    mock_tab3 = MagicMock()
    mock_streamlit['tabs'].return_value = (mock_tab1, mock_tab2, mock_tab3)
    
    # Mock the render functions
    with patch('science_data_kit.ui.components.schema_widget.render_schema_diagram') as mock_diagram, \
         patch('science_data_kit.ui.components.schema_widget.render_schema_editor', return_value=schema) as mock_editor, \
         patch('science_data_kit.ui.components.schema_widget.render_schema_import_export') as mock_import_export:
        
        # Call the function
        updated_schema = render_schema_widget(schema)
        
        # Check that the header was created
        mock_streamlit['header'].assert_called_once_with("Schema Widget")
        
        # Check that the tabs were created
        mock_streamlit['tabs'].assert_called_once_with(["Diagram", "Editor", "Import/Export"])
        
        # Check that the render functions were called
        mock_diagram.assert_called_once()
        mock_editor.assert_called_once()
        mock_import_export.assert_called_once()
        
        # Check that the updated schema was returned
        assert updated_schema == schema

def test_render_schema_widget_empty_schema(mock_streamlit):
    """Test that the schema widget handles an empty schema correctly."""
    # Mock the tabs
    mock_tab1 = MagicMock()
    mock_tab2 = MagicMock()
    mock_tab3 = MagicMock()
    mock_streamlit['tabs'].return_value = (mock_tab1, mock_tab2, mock_tab3)
    
    # Mock the render functions
    with patch('science_data_kit.ui.components.schema_widget.render_schema_diagram') as mock_diagram, \
         patch('science_data_kit.ui.components.schema_widget.render_schema_editor', return_value={}) as mock_editor, \
         patch('science_data_kit.ui.components.schema_widget.render_schema_import_export') as mock_import_export:
        
        # Call the function
        updated_schema = render_schema_widget()
        
        # Check that the info message was displayed
        mock_streamlit['info'].assert_called_once_with("No schema data available. Use the Editor tab to create a schema.")
        
        # Check that the render functions were called
        mock_diagram.assert_not_called()
        mock_editor.assert_called_once()
        mock_import_export.assert_called_once()