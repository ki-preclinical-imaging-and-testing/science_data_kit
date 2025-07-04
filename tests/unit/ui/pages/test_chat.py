"""
Unit tests for the chat page.

This module contains tests for the chat page component.
"""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st

from science_data_kit.ui.pages.chat import ChatPage, get_ollama_models, render_chat_page

@pytest.fixture
def mock_session_state():
    """Create a mock session state for testing."""
    mock_state = MagicMock()
    mock_state.db_manager = MagicMock()
    mock_state.db_manager.is_connected.return_value = True
    mock_state.db_manager.get_uri.return_value = "bolt://localhost:7687"
    mock_state.db_manager.get_username.return_value = "neo4j"
    mock_state.db_manager.get_password.return_value = "password"
    return mock_state

def test_chat_page_initialization(mock_streamlit, mock_session_state):
    """Test that the chat page is initialized correctly."""
    # Create the chat page
    chat_page = ChatPage(mock_streamlit['st'], mock_session_state)
    
    # Check that the title is set correctly
    assert chat_page.title == "Chat with Your Data"
    
    # Check that the session state is set correctly
    assert chat_page.session_state == mock_session_state

def test_render_sidebar_not_connected(mock_streamlit, mock_session_state):
    """Test that the sidebar is rendered correctly when not connected."""
    # Set up session state
    mock_session_state.db_manager.is_connected.return_value = False
    
    # Create the chat page
    chat_page = ChatPage(mock_streamlit['st'], mock_session_state)
    
    # Render the sidebar
    chat_page.render_sidebar()
    
    # Check that the correct Streamlit functions were called
    mock_streamlit['sidebar'].warning.assert_called_with("Please connect to a database to use the chat feature.")

def test_render_sidebar_connected(mock_streamlit, mock_session_state):
    """Test that the sidebar is rendered correctly when connected."""
    # Create the chat page
    chat_page = ChatPage(mock_streamlit['st'], mock_session_state)
    
    # Render the sidebar
    chat_page.render_sidebar()
    
    # Check that the correct Streamlit functions were called
    mock_streamlit['sidebar'].subheader.assert_called_with("Chat Settings")

def test_render_content_not_connected(mock_streamlit, mock_session_state):
    """Test that the content is rendered correctly when not connected."""
    # Set up session state
    mock_session_state.db_manager.is_connected.return_value = False
    
    # Create the chat page
    chat_page = ChatPage(mock_streamlit['st'], mock_session_state)
    
    # Render the content
    chat_page.render_content()
    
    # Check that the correct Streamlit functions were called
    mock_streamlit['st'].title.assert_called_with("Chat with Your Data")
    mock_streamlit['st'].warning.assert_called_with("Please connect to a database to use the chat feature.")

@patch('science_data_kit.ui.pages.chat.GraphRAG', autospec=True)
def test_render_content_connected(mock_graph_rag, mock_streamlit, mock_session_state):
    """Test that the content is rendered correctly when connected."""
    # Set up session state
    mock_session_state.chat_messages = []
    
    # Create the chat page
    chat_page = ChatPage(mock_streamlit['st'], mock_session_state)
    
    # Mock the _initialize_graph_rag method
    chat_page._initialize_graph_rag = MagicMock()
    
    # Render the content
    chat_page.render_content()
    
    # Check that the correct Streamlit functions were called
    mock_streamlit['st'].title.assert_called_with("Chat with Your Data")
    mock_streamlit['st'].chat_input.assert_called_once()

@patch('science_data_kit.ui.pages.chat.requests.get')
def test_get_ollama_models_success(mock_get, mock_streamlit):
    """Test that get_ollama_models returns the correct models when successful."""
    # Set up the mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [
            {"name": "llama2"},
            {"name": "mistral"}
        ]
    }
    mock_get.return_value = mock_response
    
    # Call the function
    models = get_ollama_models()
    
    # Check the result
    assert models == ["llama2", "mistral"]
    mock_get.assert_called_once_with("http://localhost:11434/api/tags")

@patch('science_data_kit.ui.pages.chat.requests.get')
def test_get_ollama_models_failure(mock_get, mock_streamlit):
    """Test that get_ollama_models returns an empty list when the request fails."""
    # Set up the mock response to raise an exception
    mock_get.side_effect = Exception("Connection error")
    
    # Call the function
    models = get_ollama_models()
    
    # Check the result
    assert models == []
    mock_get.assert_called_once_with("http://localhost:11434/api/tags")

@patch('science_data_kit.ui.pages.chat.ChatPage')
def test_render_chat_page(mock_chat_page_class, mock_streamlit):
    """Test that render_chat_page creates and renders a ChatPage."""
    # Set up the mock
    mock_chat_page = MagicMock()
    mock_chat_page_class.return_value = mock_chat_page
    
    # Call the function
    render_chat_page()
    
    # Check that the ChatPage was created and rendered
    mock_chat_page_class.assert_called_once_with(st)
    mock_chat_page.render.assert_called_once()