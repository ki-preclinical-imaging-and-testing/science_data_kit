"""
Unit tests for the chat module.

This module contains tests for the Ollama chat integration.
"""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
import requests
import json

from app.chat import get_ollama_models, initialize_graph_rag

def test_get_ollama_models_success():
    """Test get_ollama_models function with a successful API response."""
    # Mock the requests.get function
    with patch('app.chat.requests.get') as mock_get:
        # Configure the mock to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2"},
                {"name": "mistral"},
                {"name": "mixtral"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Call the function
        models = get_ollama_models()
        
        # Check that the API was called with the correct URL
        mock_get.assert_called_once_with("http://localhost:11434/api/tags")
        
        # Check that the function returned the expected models
        assert models == ["llama2", "mistral", "mixtral"]

def test_get_ollama_models_error_status():
    """Test get_ollama_models function with an error status code."""
    # Mock the requests.get function
    with patch('app.chat.requests.get') as mock_get, \
         patch('app.chat.st.warning') as mock_warning:
        # Configure the mock to return an error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Call the function
        models = get_ollama_models()
        
        # Check that the API was called with the correct URL
        mock_get.assert_called_once_with("http://localhost:11434/api/tags")
        
        # Check that a warning was displayed
        mock_warning.assert_called_once()
        
        # Check that the function returned the default models
        assert models == ["llama2", "mistral", "mixtral", "phi"]

def test_get_ollama_models_exception():
    """Test get_ollama_models function with an exception."""
    # Mock the requests.get function
    with patch('app.chat.requests.get') as mock_get, \
         patch('app.chat.st.warning') as mock_warning:
        # Configure the mock to raise an exception
        mock_get.side_effect = Exception("Connection failed")
        
        # Call the function
        models = get_ollama_models()
        
        # Check that the API was called with the correct URL
        mock_get.assert_called_once_with("http://localhost:11434/api/tags")
        
        # Check that a warning was displayed
        mock_warning.assert_called_once()
        
        # Check that the function returned the default models
        assert models == ["llama2", "mistral", "mixtral", "phi"]

def test_initialize_graph_rag_with_ollama():
    """Test initialize_graph_rag function with Ollama LLM provider."""
    # Mock the required classes and functions
    with patch('app.chat.GraphDatabase') as mock_graph_db, \
         patch('app.chat.OllamaLLM') as mock_ollama_llm, \
         patch('app.chat.OllamaEmbeddings') as mock_ollama_embeddings, \
         patch('app.chat.GraphRAG') as mock_graph_rag, \
         patch('app.chat.VectorRetriever') as mock_vector_retriever, \
         patch('app.chat.st.session_state') as mock_session_state, \
         patch('app.chat.st.info') as mock_info:
        
        # Configure the mocks
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        mock_llm_instance = MagicMock()
        mock_ollama_llm.return_value = mock_llm_instance
        
        mock_embeddings_instance = MagicMock()
        mock_ollama_embeddings.return_value = mock_embeddings_instance
        
        mock_retriever_instance = MagicMock()
        mock_vector_retriever.return_value = mock_retriever_instance
        
        mock_graph_rag_instance = MagicMock()
        mock_graph_rag.return_value = mock_graph_rag_instance
        
        # Configure session state
        mock_session_state.get.side_effect = lambda key, default=None: {
            "ollama_base_url": "http://localhost:11434",
            "ollama_auth_enabled": True,
            "ollama_username": "test_user",
            "ollama_password": "test_password",
            "retriever_type": "Vector"
        }.get(key, default)
        
        # Call the function
        result = initialize_graph_rag(
            "bolt://localhost:7687",
            "neo4j",
            "password",
            "Ollama",
            None,
            "llama2"
        )
        
        # Check that the driver was created with the correct parameters
        mock_graph_db.driver.assert_called_once()
        
        # Check that OllamaLLM was created with the correct parameters
        mock_ollama_llm.assert_called_once_with(
            base_url="http://localhost:11434",
            model="llama2",
            auth=("test_user", "test_password")
        )
        
        # Check that OllamaEmbeddings was created with the correct parameters
        mock_ollama_embeddings.assert_called_once_with(
            model="llama2",
            base_url="http://localhost:11434"
        )
        
        # Check that GraphRAG was created with the correct parameters
        mock_graph_rag.assert_called_once_with(
            mock_retriever_instance,
            llm=mock_llm_instance,
            embeddings=mock_embeddings_instance
        )
        
        # Check that an info message was displayed
        mock_info.assert_called_once()
        
        # Check that the function returned the GraphRAG instance
        assert result == mock_graph_rag_instance

def test_initialize_graph_rag_ollama_error_handling():
    """Test initialize_graph_rag function with Ollama error handling."""
    # Mock the required classes and functions
    with patch('app.chat.GraphDatabase') as mock_graph_db, \
         patch('app.chat.OllamaLLM') as mock_ollama_llm, \
         patch('app.chat.OllamaEmbeddings') as mock_ollama_embeddings, \
         patch('app.chat.GraphRAG') as mock_graph_rag, \
         patch('app.chat.VectorRetriever') as mock_vector_retriever, \
         patch('app.chat.st.session_state') as mock_session_state, \
         patch('app.chat.st.error') as mock_error:
        
        # Configure the mocks
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Configure OllamaLLM to raise an exception
        mock_ollama_llm.side_effect = Exception("Ollama error")
        
        mock_llm_instance = MagicMock()
        mock_ollama_llm.return_value = mock_llm_instance
        
        mock_embeddings_instance = MagicMock()
        mock_ollama_embeddings.return_value = mock_embeddings_instance
        
        mock_retriever_instance = MagicMock()
        mock_vector_retriever.return_value = mock_retriever_instance
        
        mock_graph_rag_instance = MagicMock()
        mock_graph_rag.return_value = mock_graph_rag_instance
        
        # Configure session state
        mock_session_state.get.side_effect = lambda key, default=None: {
            "ollama_base_url": "http://localhost:11434",
            "ollama_auth_enabled": False,
            "retriever_type": "Vector"
        }.get(key, default)
        
        # Call the function
        result = initialize_graph_rag(
            "bolt://localhost:7687",
            "neo4j",
            "password",
            "Ollama",
            None,
            "llama2"
        )
        
        # Check that an error message was displayed
        mock_error.assert_called_once()
        
        # Check that OllamaLLM was called again with fallback parameters
        assert mock_ollama_llm.call_count == 2
        
        # Check that GraphRAG was created with the correct parameters
        mock_graph_rag.assert_called_once()