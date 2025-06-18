"""
Unit tests for the sidebar component.

This module contains tests for the sidebar component functions.
"""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st

from science_data_kit.ui.components.sidebar import (
    render_sidebar,
    render_sidebar_header,
    render_database_sidebar
)

def test_render_sidebar_header(mock_streamlit):
    """Test that the sidebar header is rendered correctly."""
    # Call the function
    render_sidebar_header()
    
    # Check that the correct Streamlit functions were called
    mock_streamlit['sidebar'].image.assert_called_once()
    mock_streamlit['sidebar'].title.assert_called_once_with("Science Data Kit")

def test_render_database_sidebar_not_connected(mock_streamlit):
    """Test that the database sidebar is rendered correctly when not connected."""
    # Set up session state
    with patch.object(st.session_state, 'get', return_value=False):
        # Call the function
        render_database_sidebar()
        
        # Check that the correct Streamlit functions were called
        mock_streamlit['sidebar'].header.assert_called_once_with("Database Connection")
        mock_streamlit['sidebar'].warning.assert_called_once_with("Not connected to Neo4j")
        mock_streamlit['sidebar'].form.assert_called_once_with("neo4j_connection_form")

def test_render_database_sidebar_connected(mock_streamlit):
    """Test that the database sidebar is rendered correctly when connected."""
    # Set up session state
    with patch.object(st.session_state, 'get', side_effect=lambda key, default=None: True if key == "connected" else "test_value"):
        # Call the function
        render_database_sidebar()
        
        # Check that the correct Streamlit functions were called
        mock_streamlit['sidebar'].header.assert_called_once_with("Database Connection")
        mock_streamlit['sidebar'].success.assert_called_once_with("Connected to Neo4j")
        mock_streamlit['sidebar'].form.assert_called_once_with("neo4j_connection_form")

def test_render_sidebar_all_sections(mock_streamlit):
    """Test that all sidebar sections are rendered when no sections are specified."""
    # Mock the section rendering functions
    with patch('science_data_kit.ui.components.sidebar.render_sidebar_header') as mock_header, \
         patch('science_data_kit.ui.components.sidebar.render_database_sidebar') as mock_database, \
         patch('science_data_kit.ui.components.sidebar.render_neo4j_container_sidebar') as mock_neo4j, \
         patch('science_data_kit.ui.components.sidebar.render_jupyter_sidebar') as mock_jupyter, \
         patch('science_data_kit.ui.components.sidebar.render_neodash_sidebar') as mock_neodash, \
         patch('science_data_kit.ui.components.sidebar.render_settings_sidebar') as mock_settings:
        
        # Call the function
        render_sidebar()
        
        # Check that all section rendering functions were called
        mock_header.assert_called_once()
        mock_database.assert_called_once()
        mock_neo4j.assert_called_once()
        mock_jupyter.assert_called_once()
        mock_neodash.assert_called_once()
        mock_settings.assert_called_once()

def test_render_sidebar_specific_sections(mock_streamlit):
    """Test that only specified sidebar sections are rendered."""
    # Mock the section rendering functions
    with patch('science_data_kit.ui.components.sidebar.render_sidebar_header') as mock_header, \
         patch('science_data_kit.ui.components.sidebar.render_database_sidebar') as mock_database, \
         patch('science_data_kit.ui.components.sidebar.render_neo4j_container_sidebar') as mock_neo4j, \
         patch('science_data_kit.ui.components.sidebar.render_jupyter_sidebar') as mock_jupyter, \
         patch('science_data_kit.ui.components.sidebar.render_neodash_sidebar') as mock_neodash, \
         patch('science_data_kit.ui.components.sidebar.render_settings_sidebar') as mock_settings:
        
        # Call the function with specific sections
        render_sidebar(sections=["header", "database"])
        
        # Check that only the specified section rendering functions were called
        mock_header.assert_called_once()
        mock_database.assert_called_once()
        mock_neo4j.assert_not_called()
        mock_jupyter.assert_not_called()
        mock_neodash.assert_not_called()
        mock_settings.assert_not_called()

def test_render_sidebar_with_callbacks(mock_streamlit):
    """Test that callbacks are passed to the section rendering functions."""
    # Create mock callbacks
    mock_callbacks = {
        "on_database_connect": MagicMock(),
        "on_database_disconnect": MagicMock(),
        "on_neo4j_start": MagicMock(),
        "on_neo4j_stop": MagicMock()
    }
    
    # Mock the section rendering functions
    with patch('science_data_kit.ui.components.sidebar.render_sidebar_header') as mock_header, \
         patch('science_data_kit.ui.components.sidebar.render_database_sidebar') as mock_database, \
         patch('science_data_kit.ui.components.sidebar.render_neo4j_container_sidebar') as mock_neo4j, \
         patch('science_data_kit.ui.components.sidebar.render_jupyter_sidebar') as mock_jupyter, \
         patch('science_data_kit.ui.components.sidebar.render_neodash_sidebar') as mock_neodash, \
         patch('science_data_kit.ui.components.sidebar.render_settings_sidebar') as mock_settings:
        
        # Call the function with callbacks
        render_sidebar(callbacks=mock_callbacks)
        
        # Check that the callbacks were passed to the section rendering functions
        mock_database.assert_called_once_with(
            on_connect=mock_callbacks["on_database_connect"],
            on_disconnect=mock_callbacks["on_database_disconnect"]
        )
        mock_neo4j.assert_called_once_with(
            on_start=mock_callbacks["on_neo4j_start"],
            on_stop=mock_callbacks["on_neo4j_stop"]
        )