"""
Integration tests for the chat page.

This module contains integration tests for the chat page component,
verifying its behavior when interacting with a database manager.
"""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st

from science_data_kit.ui.pages.chat import ChatPage
from science_data_kit.core.db.db_manager import Neo4jManager

@pytest.fixture
def mock_db_manager():
    """Create a mock database manager for testing."""
    db_manager = MagicMock(spec=Neo4jManager)
    db_manager.is_connected.return_value = True
    db_manager.get_uri.return_value = "bolt://localhost:7687"
    db_manager.get_username.return_value = "neo4j"
    db_manager.get_password.return_value = "password"
    db_manager.run_query.return_value = [{"count": 42}]
    return db_manager

@pytest.fixture
def mock_session_state(mock_db_manager):
    """Create a mock session state with a database manager."""
    mock_state = MagicMock()
    mock_state.db_manager = mock_db_manager
    mock_state.chat_messages = []
    mock_state.chat_history = {}
    return mock_state

def test_chat_page_initialization(mock_streamlit, mock_session_state):
    """Test that the chat page is initialized correctly."""
    # Create the chat page
    chat_page = ChatPage(mock_streamlit['st'], mock_session_state)
    
    # Check that the title is set correctly
    assert chat_page.title == "Chat with Your Data"
    
    # Check that the session state is set correctly
    assert chat_page.session_state == mock_session_state

@patch('science_data_kit.ui.pages.chat.GraphRAG', autospec=True)
def test_chat_with_database_connected(mock_graph_rag, mock_streamlit, mock_session_state):
    """Test that the chat page works correctly when connected to a database."""
    # Set up the mock GraphRAG
    mock_graph_rag_instance = MagicMock()
    mock_graph_rag.return_value = mock_graph_rag_instance
    mock_graph_rag_instance.generate.return_value = "This is a response from the LLM."
    
    # Create the chat page
    chat_page = ChatPage(mock_streamlit['st'], mock_session_state)
    
    # Mock the _initialize_graph_rag method to return the mock GraphRAG instance
    chat_page._initialize_graph_rag = MagicMock(return_value=mock_graph_rag_instance)
    
    # Render the content
    chat_page.render_content()
    
    # Check that the correct Streamlit functions were called
    mock_streamlit['st'].title.assert_called_with("Chat with Your Data")
    mock_streamlit['st'].chat_input.assert_called_once()
    
    # Simulate a user message
    mock_streamlit['st'].chat_input.return_value = "What data do you have?"
    
    # Render the content again to process the user message
    chat_page.render_content()
    
    # Check that the message was added to the chat history
    assert len(mock_session_state.chat_messages) > 0
    
    # Check that the GraphRAG generate method was called
    mock_graph_rag_instance.generate.assert_called_once()

def test_chat_with_database_not_connected(mock_streamlit, mock_session_state):
    """Test that the chat page shows a warning when not connected to a database."""
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
def test_chat_with_different_llm_providers(mock_graph_rag, mock_streamlit, mock_session_state):
    """Test that the chat page works with different LLM providers."""
    # Set up the mock GraphRAG
    mock_graph_rag_instance = MagicMock()
    mock_graph_rag.return_value = mock_graph_rag_instance
    mock_graph_rag_instance.generate.return_value = "This is a response from the LLM."
    
    # Create the chat page
    chat_page = ChatPage(mock_streamlit['st'], mock_session_state)
    
    # Mock the _initialize_graph_rag method to return the mock GraphRAG instance
    chat_page._initialize_graph_rag = MagicMock(return_value=mock_graph_rag_instance)
    
    # Test with OpenAI provider
    mock_session_state.llm_provider = "openai"
    mock_session_state.openai_api_key = "test_api_key"
    mock_session_state.openai_model = "gpt-4"
    
    # Render the content
    chat_page.render_content()
    
    # Check that _initialize_graph_rag was called with the correct parameters
    chat_page._initialize_graph_rag.assert_called_with(
        "bolt://localhost:7687", "neo4j", "password", 
        llm_provider="openai", llm_api_key="test_api_key", llm_model="gpt-4"
    )
    
    # Test with Ollama provider
    mock_session_state.llm_provider = "ollama"
    mock_session_state.ollama_model = "llama2"
    
    # Render the content
    chat_page.render_content()
    
    # Check that _initialize_graph_rag was called with the correct parameters
    chat_page._initialize_graph_rag.assert_called_with(
        "bolt://localhost:7687", "neo4j", "password", 
        llm_provider="ollama", llm_api_key=None, llm_model="llama2"
    )

@patch('science_data_kit.ui.pages.chat.requests.get')
def test_ollama_models_integration(mock_get, mock_streamlit, mock_session_state):
    """Test the integration with Ollama models."""
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
    
    # Create the chat page
    chat_page = ChatPage(mock_streamlit['st'], mock_session_state)
    
    # Set up session state for Ollama
    mock_session_state.llm_provider = "ollama"
    
    # Render the sidebar
    chat_page.render_sidebar()
    
    # Check that the Ollama models were fetched
    mock_get.assert_called_once_with("http://localhost:11434/api/tags")
    
    # Check that the selectbox for Ollama models was called with the correct options
    mock_streamlit['sidebar'].selectbox.assert_any_call(
        "Ollama Model", ["llama2", "mistral"], key="ollama_model"
    )