"""
Integration tests for the Dropbox integration.

This module contains tests that verify the interaction between
the Dropbox selector UI and the underlying Dropbox provider.
"""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
import pandas as pd
import asyncio

from science_data_kit.ui.components.dropbox_selector import render_dropbox_selector, setup_dropbox_provider
from science_data_kit.core.providers.storage.dropbox_provider import DropboxProvider

@pytest.fixture
def mock_dropbox_provider():
    """Mock the Dropbox provider."""
    with patch('science_data_kit.ui.components.dropbox_selector.DropboxProvider') as mock_provider_class:
        # Configure the mock provider instance
        mock_provider = MagicMock()
        mock_provider_class.return_value = mock_provider
        
        # Configure the initialize method to return True
        mock_provider.initialize = MagicMock(return_value=asyncio.Future())
        mock_provider.initialize.return_value.set_result(True)
        
        # Configure the list_files method to return test files
        mock_provider.list_files = MagicMock(return_value=asyncio.Future())
        mock_provider.list_files.return_value.set_result([
            {
                "id": "folder1",
                "name": "Test Folder",
                "path": "/Test Folder",
                "type": "folder",
                "size": 0,
                "modified": "2023-07-30"
            },
            {
                "id": "file1",
                "name": "test.csv",
                "path": "/test.csv",
                "type": "csv",
                "size": 1024,
                "modified": "2023-07-30"
            },
            {
                "id": "file2",
                "name": "test.xlsx",
                "path": "/test.xlsx",
                "type": "xlsx",
                "size": 2048,
                "modified": "2023-07-30"
            }
        ])
        
        # Configure the download_file_data method to return test data
        test_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        mock_provider.download_file_data = MagicMock(return_value=asyncio.Future())
        mock_provider.download_file_data.return_value.set_result(test_df)
        
        yield mock_provider_class

@pytest.fixture
def mock_config_loader():
    """Mock the configuration loader."""
    with patch('science_data_kit.ui.components.dropbox_selector.load_provider_config') as mock:
        # Configure the mock to return a test configuration
        mock.return_value = {
            "storage": {
                "dropbox": {
                    "access_token": "test_token"
                }
            }
        }
        yield mock

def test_dropbox_provider_initialization(mock_streamlit, mock_dropbox_provider, mock_config_loader):
    """
    Test the initialization of the Dropbox provider.
    
    This test verifies that the Dropbox provider is correctly initialized
    with the configuration from the config loader.
    """
    # Call the function
    render_dropbox_selector()
    
    # Check that the provider was created with the correct configuration
    mock_dropbox_provider.assert_called_once_with({"access_token": "test_token"})
    
    # Check that the provider was initialized
    mock_dropbox_provider.return_value.initialize.assert_called_once()
    
    # Check that the provider was stored in the session state
    assert "dropbox_provider" in st.session_state
    assert st.session_state["dropbox_provider"] == mock_dropbox_provider.return_value
    assert st.session_state["dropbox_provider_initialized"] == True

def test_dropbox_file_listing(mock_streamlit, mock_dropbox_provider, mock_config_loader):
    """
    Test the listing of files in Dropbox.
    
    This test verifies that the Dropbox selector correctly lists files
    from the Dropbox provider.
    """
    # Set up session state
    st.session_state["dropbox_provider"] = mock_dropbox_provider.return_value
    st.session_state["dropbox_provider_initialized"] = True
    st.session_state["dropbox_current_path"] = ""
    
    # Call the function
    render_dropbox_selector()
    
    # Check that the list_files method was called with the correct path
    mock_dropbox_provider.return_value.list_files.assert_called_once_with("")
    
    # Check that the files were stored in the session state
    assert "dropbox_files" in st.session_state
    assert len(st.session_state["dropbox_files"]) == 3

def test_dropbox_file_selection(mock_streamlit, mock_dropbox_provider, mock_config_loader):
    """
    Test the selection of a file in Dropbox.
    
    This test verifies that when a user selects a file, the Dropbox selector
    correctly gets a preview of the file data.
    """
    # Set up session state
    st.session_state["dropbox_provider"] = mock_dropbox_provider.return_value
    st.session_state["dropbox_provider_initialized"] = True
    st.session_state["dropbox_current_path"] = ""
    st.session_state["dropbox_files"] = [
        {
            "id": "file1",
            "name": "test.csv",
            "path": "/test.csv",
            "type": "csv",
            "size": 1024,
            "modified": "2023-07-30"
        }
    ]
    
    # Configure the button to return True (clicked)
    mock_streamlit['button'].side_effect = [False, True]  # First button is Browse Folder, second is the file
    
    # Call the function
    render_dropbox_selector()
    
    # Check that the download_file_data method was called with the correct path
    mock_dropbox_provider.return_value.download_file_data.assert_called_once_with("/test.csv")
    
    # Check that the selected file and preview data were stored in the session state
    assert "dropbox_selected_file" in st.session_state
    assert st.session_state["dropbox_selected_file"]["name"] == "test.csv"
    assert "dropbox_preview_data" in st.session_state
    assert isinstance(st.session_state["dropbox_preview_data"], pd.DataFrame)

def test_dropbox_file_import(mock_streamlit, mock_dropbox_provider, mock_config_loader):
    """
    Test the import of a file from Dropbox.
    
    This test verifies that when a user imports a file, the Dropbox selector
    correctly returns the file data and metadata.
    """
    # Set up session state
    st.session_state["dropbox_provider"] = mock_dropbox_provider.return_value
    st.session_state["dropbox_provider_initialized"] = True
    st.session_state["dropbox_current_path"] = ""
    st.session_state["dropbox_files"] = [
        {
            "id": "file1",
            "name": "test.csv",
            "path": "/test.csv",
            "type": "csv",
            "size": 1024,
            "modified": "2023-07-30"
        }
    ]
    st.session_state["dropbox_selected_file"] = {
        "id": "file1",
        "name": "test.csv",
        "path": "/test.csv",
        "type": "csv",
        "size": 1024,
        "modified": "2023-07-30"
    }
    st.session_state["dropbox_preview_data"] = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    
    # Configure the buttons to return False (not clicked) for navigation and file selection,
    # and True (clicked) for the import button
    mock_streamlit['button'].side_effect = [False, False, True]
    
    # Call the function
    result = render_dropbox_selector()
    
    # Check that the download_file_data method was called with the correct path
    mock_dropbox_provider.return_value.download_file_data.assert_called_with("/test.csv")
    
    # Check that the result has the correct structure
    assert result is not None
    assert result["source"] == "dropbox"
    assert isinstance(result["data"], pd.DataFrame)
    assert result["metadata"]["name"] == "test.csv"
    assert result["path"] == "/test.csv"

def test_dropbox_setup(mock_streamlit):
    """
    Test the setup of the Dropbox provider.
    
    This test verifies that when a user enters an access token, the Dropbox provider
    is correctly set up with that token.
    """
    # Mock the _initialize_provider function
    with patch('science_data_kit.ui.components.dropbox_selector._initialize_provider') as mock_init:
        # Configure the mock to return True
        mock_init.return_value = True
        
        # Call the function
        result = setup_dropbox_provider("test_token")
        
        # Check that the _initialize_provider function was called with the correct configuration
        mock_init.assert_called_once_with({"access_token": "test_token"})
        
        # Check that the function returned True
        assert result == True
"""