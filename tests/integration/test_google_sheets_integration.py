"""
Integration tests for the Google Sheets integration.

This module contains tests that verify the interaction between
the Google Sheets selector UI and the underlying Google Sheets provider.
"""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
import pandas as pd
import asyncio
import os

from science_data_kit.ui.components.google_sheets_selector import render_google_sheets_selector, setup_google_sheets_provider
from science_data_kit.core.providers.storage.google_sheets_provider import GoogleSheetsProvider

@pytest.fixture
def mock_google_sheets_provider():
    """Mock the Google Sheets provider."""
    with patch('science_data_kit.ui.components.google_sheets_selector.GoogleSheetsProvider') as mock_provider_class:
        # Configure the mock provider instance
        mock_provider = MagicMock()
        mock_provider_class.return_value = mock_provider
        
        # Configure the initialize method to return True
        mock_provider.initialize = MagicMock(return_value=asyncio.Future())
        mock_provider.initialize.return_value.set_result(True)
        
        # Configure the list_spreadsheets method to return test spreadsheets
        mock_provider.list_spreadsheets = MagicMock(return_value=asyncio.Future())
        mock_provider.list_spreadsheets.return_value.set_result([
            {
                "id": "spreadsheet1",
                "name": "Test Spreadsheet 1",
                "url": "https://docs.google.com/spreadsheets/d/spreadsheet1"
            },
            {
                "id": "spreadsheet2",
                "name": "Test Spreadsheet 2",
                "url": "https://docs.google.com/spreadsheets/d/spreadsheet2"
            }
        ])
        
        # Configure the list_sheets method to return test sheets
        mock_provider.list_sheets = MagicMock(return_value=asyncio.Future())
        mock_provider.list_sheets.return_value.set_result([
            {
                "id": "sheet1",
                "name": "Sheet1",
                "rows": 100,
                "columns": 10
            },
            {
                "id": "sheet2",
                "name": "Sheet2",
                "rows": 50,
                "columns": 5
            }
        ])
        
        # Configure the get_sheet_data method to return test data
        test_df = pd.DataFrame({"X": [10, 20, 30], "Y": [40, 50, 60]})
        mock_provider.get_sheet_data = MagicMock(return_value=asyncio.Future())
        mock_provider.get_sheet_data.return_value.set_result(test_df)
        
        yield mock_provider_class

@pytest.fixture
def mock_config_loader():
    """Mock the configuration loader."""
    with patch('science_data_kit.ui.components.google_sheets_selector.load_provider_config') as mock:
        # Configure the mock to return a test configuration
        mock.return_value = {
            "spreadsheet": {
                "google_sheets": {
                    "credentials_file": "/path/to/credentials.json",
                    "token_file": "google_sheets_token.json"
                }
            }
        }
        yield mock

def test_google_sheets_provider_initialization(mock_streamlit, mock_google_sheets_provider, mock_config_loader):
    """
    Test the initialization of the Google Sheets provider.
    
    This test verifies that the Google Sheets provider is correctly initialized
    with the configuration from the config loader.
    """
    # Call the function
    render_google_sheets_selector()
    
    # Check that the provider was created with the correct configuration
    mock_google_sheets_provider.assert_called_once_with({
        "credentials_file": "/path/to/credentials.json",
        "token_file": "google_sheets_token.json"
    })
    
    # Check that the provider was initialized
    mock_google_sheets_provider.return_value.initialize.assert_called_once()
    
    # Check that the provider was stored in the session state
    assert "google_sheets_provider" in st.session_state
    assert st.session_state["google_sheets_provider"] == mock_google_sheets_provider.return_value
    assert st.session_state["google_sheets_provider_initialized"] == True

def test_google_sheets_spreadsheet_listing(mock_streamlit, mock_google_sheets_provider, mock_config_loader):
    """
    Test the listing of spreadsheets in Google Sheets.
    
    This test verifies that the Google Sheets selector correctly lists spreadsheets
    from the Google Sheets provider.
    """
    # Set up session state
    st.session_state["google_sheets_provider"] = mock_google_sheets_provider.return_value
    st.session_state["google_sheets_provider_initialized"] = True
    
    # Call the function
    render_google_sheets_selector()
    
    # Check that the list_spreadsheets method was called
    mock_google_sheets_provider.return_value.list_spreadsheets.assert_called_once()
    
    # Check that the spreadsheets were stored in the session state
    assert "google_sheets_spreadsheets" in st.session_state
    assert len(st.session_state["google_sheets_spreadsheets"]) == 2

def test_google_sheets_spreadsheet_selection(mock_streamlit, mock_google_sheets_provider, mock_config_loader):
    """
    Test the selection of a spreadsheet in Google Sheets.
    
    This test verifies that when a user selects a spreadsheet, the Google Sheets selector
    correctly lists the sheets in that spreadsheet.
    """
    # Set up session state
    st.session_state["google_sheets_provider"] = mock_google_sheets_provider.return_value
    st.session_state["google_sheets_provider_initialized"] = True
    st.session_state["google_sheets_spreadsheets"] = [
        {
            "id": "spreadsheet1",
            "name": "Test Spreadsheet 1",
            "url": "https://docs.google.com/spreadsheets/d/spreadsheet1"
        }
    ]
    
    # Configure the button to return True (clicked)
    mock_streamlit['button'].side_effect = [False, True]  # First button is Refresh, second is the spreadsheet
    
    # Call the function
    render_google_sheets_selector()
    
    # Check that the list_sheets method was called with the correct spreadsheet ID
    mock_google_sheets_provider.return_value.list_sheets.assert_called_once_with("spreadsheet1")
    
    # Check that the selected spreadsheet and sheets were stored in the session state
    assert "google_sheets_selected_spreadsheet" in st.session_state
    assert st.session_state["google_sheets_selected_spreadsheet"]["name"] == "Test Spreadsheet 1"
    assert "google_sheets_sheets" in st.session_state
    assert len(st.session_state["google_sheets_sheets"]) == 2

def test_google_sheets_sheet_selection(mock_streamlit, mock_google_sheets_provider, mock_config_loader):
    """
    Test the selection of a sheet in Google Sheets.
    
    This test verifies that when a user selects a sheet, the Google Sheets selector
    correctly gets a preview of the sheet data.
    """
    # Set up session state
    st.session_state["google_sheets_provider"] = mock_google_sheets_provider.return_value
    st.session_state["google_sheets_provider_initialized"] = True
    st.session_state["google_sheets_spreadsheets"] = [
        {
            "id": "spreadsheet1",
            "name": "Test Spreadsheet 1",
            "url": "https://docs.google.com/spreadsheets/d/spreadsheet1"
        }
    ]
    st.session_state["google_sheets_selected_spreadsheet"] = {
        "id": "spreadsheet1",
        "name": "Test Spreadsheet 1",
        "url": "https://docs.google.com/spreadsheets/d/spreadsheet1"
    }
    st.session_state["google_sheets_sheets"] = [
        {
            "id": "sheet1",
            "name": "Sheet1",
            "rows": 100,
            "columns": 10
        }
    ]
    
    # Configure the button to return True (clicked) for the sheet
    mock_streamlit['button'].side_effect = [False, False, True]  # Refresh, spreadsheet, sheet
    
    # Call the function
    render_google_sheets_selector()
    
    # Check that the get_sheet_data method was called with the correct parameters
    mock_google_sheets_provider.return_value.get_sheet_data.assert_called_once_with("spreadsheet1", "Sheet1")
    
    # Check that the selected sheet and preview data were stored in the session state
    assert "google_sheets_selected_sheet" in st.session_state
    assert st.session_state["google_sheets_selected_sheet"]["name"] == "Sheet1"
    assert "google_sheets_preview_data" in st.session_state
    assert isinstance(st.session_state["google_sheets_preview_data"], pd.DataFrame)

def test_google_sheets_data_import(mock_streamlit, mock_google_sheets_provider, mock_config_loader):
    """
    Test the import of data from Google Sheets.
    
    This test verifies that when a user imports data, the Google Sheets selector
    correctly returns the sheet data and metadata.
    """
    # Set up session state
    st.session_state["google_sheets_provider"] = mock_google_sheets_provider.return_value
    st.session_state["google_sheets_provider_initialized"] = True
    st.session_state["google_sheets_spreadsheets"] = [
        {
            "id": "spreadsheet1",
            "name": "Test Spreadsheet 1",
            "url": "https://docs.google.com/spreadsheets/d/spreadsheet1"
        }
    ]
    st.session_state["google_sheets_selected_spreadsheet"] = {
        "id": "spreadsheet1",
        "name": "Test Spreadsheet 1",
        "url": "https://docs.google.com/spreadsheets/d/spreadsheet1"
    }
    st.session_state["google_sheets_sheets"] = [
        {
            "id": "sheet1",
            "name": "Sheet1",
            "rows": 100,
            "columns": 10
        }
    ]
    st.session_state["google_sheets_selected_sheet"] = {
        "id": "sheet1",
        "name": "Sheet1",
        "rows": 100,
        "columns": 10
    }
    st.session_state["google_sheets_preview_data"] = pd.DataFrame({"X": [10, 20, 30], "Y": [40, 50, 60]})
    
    # Configure the buttons to return False (not clicked) for navigation and selection,
    # and True (clicked) for the import button
    mock_streamlit['button'].side_effect = [False, False, False, True]
    
    # Call the function
    result = render_google_sheets_selector()
    
    # Check that the get_sheet_data method was called with the correct parameters
    mock_google_sheets_provider.return_value.get_sheet_data.assert_called_with("spreadsheet1", "Sheet1")
    
    # Check that the result has the correct structure
    assert result is not None
    assert result["source"] == "google_sheets"
    assert isinstance(result["data"], pd.DataFrame)
    assert result["metadata"]["spreadsheet_id"] == "spreadsheet1"
    assert result["metadata"]["spreadsheet_name"] == "Test Spreadsheet 1"
    assert result["metadata"]["sheet_id"] == "sheet1"
    assert result["metadata"]["sheet_name"] == "Sheet1"
    assert result["path"] == "Test Spreadsheet 1/Sheet1"

def test_google_sheets_setup(mock_streamlit):
    """
    Test the setup of the Google Sheets provider.
    
    This test verifies that when a user enters a credentials file path, the Google Sheets provider
    is correctly set up with that file.
    """
    # Mock the os.path.exists function to return True
    with patch('os.path.exists', return_value=True):
        # Mock the _initialize_provider function
        with patch('science_data_kit.ui.components.google_sheets_selector._initialize_provider') as mock_init:
            # Configure the mock to return True
            mock_init.return_value = True
            
            # Call the function
            result = setup_google_sheets_provider("/path/to/credentials.json")
            
            # Check that the _initialize_provider function was called with the correct configuration
            mock_init.assert_called_once_with({
                "credentials_file": "/path/to/credentials.json",
                "token_file": "google_sheets_token.json"
            })
            
            # Check that the function returned True
            assert result == True
"""