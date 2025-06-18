"""
Configuration file for pytest.

This file contains fixtures and configuration settings for pytest.
"""

import pytest
import streamlit as st
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_streamlit():
    """
    Fixture to mock Streamlit functions for testing UI components.
    
    Returns:
        MagicMock: A mock object for the streamlit module.
    """
    with patch('streamlit.text') as mock_text, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.header') as mock_header, \
         patch('streamlit.subheader') as mock_subheader, \
         patch('streamlit.sidebar') as mock_sidebar, \
         patch('streamlit.columns') as mock_columns, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.selectbox') as mock_selectbox, \
         patch('streamlit.checkbox') as mock_checkbox, \
         patch('streamlit.radio') as mock_radio, \
         patch('streamlit.text_input') as mock_text_input, \
         patch('streamlit.number_input') as mock_number_input, \
         patch('streamlit.slider') as mock_slider, \
         patch('streamlit.expander') as mock_expander, \
         patch('streamlit.container') as mock_container, \
         patch('streamlit.session_state') as mock_session_state:
        
        # Create a mock for session_state that behaves like a dict
        mock_session_state.__getitem__.side_effect = lambda x: None
        mock_session_state.__setitem__ = MagicMock()
        
        # Return all mocks as a dictionary
        yield {
            'text': mock_text,
            'markdown': mock_markdown,
            'header': mock_header,
            'subheader': mock_subheader,
            'sidebar': mock_sidebar,
            'columns': mock_columns,
            'button': mock_button,
            'selectbox': mock_selectbox,
            'checkbox': mock_checkbox,
            'radio': mock_radio,
            'text_input': mock_text_input,
            'number_input': mock_number_input,
            'slider': mock_slider,
            'expander': mock_expander,
            'container': mock_container,
            'session_state': mock_session_state
        }

@pytest.fixture
def mock_neo4j_connection():
    """
    Fixture to mock Neo4j connection for testing database interactions.
    
    Returns:
        MagicMock: A mock object for the Neo4jConnection class.
    """
    mock_conn = MagicMock()
    mock_conn.execute_query.return_value = []
    mock_conn.test_connection.return_value = True
    return mock_conn