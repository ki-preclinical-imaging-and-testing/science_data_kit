"""
Integration tests for the data source selector component.

This module contains tests that verify the interaction between
the data source selector UI and the underlying data source providers.
"""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
import pandas as pd

from science_data_kit.ui.components.data_source_selector import render_data_source_selector
from science_data_kit.core.providers.registry import ProviderType

@pytest.fixture
def mock_dropbox_selector():
    """Mock the Dropbox selector component."""
    with patch('science_data_kit.ui.components.data_source_selector.render_dropbox_selector') as mock:
        # Configure the mock to return test data
        mock.return_value = {
            "data": pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}),
            "file_path": "/test/path/file.csv",
            "file_name": "file.csv",
            "file_type": "csv"
        }
        yield mock

@pytest.fixture
def mock_google_sheets_selector():
    """Mock the Google Sheets selector component."""
    with patch('science_data_kit.ui.components.data_source_selector.render_google_sheets_selector') as mock:
        # Configure the mock to return test data
        mock.return_value = {
            "data": pd.DataFrame({"X": [10, 20, 30], "Y": [40, 50, 60]}),
            "spreadsheet_id": "test_spreadsheet_id",
            "spreadsheet_name": "Test Spreadsheet",
            "sheet_name": "Sheet1"
        }
        yield mock

def test_data_source_selector_dropbox_integration(mock_streamlit, mock_dropbox_selector, mock_google_sheets_selector):
    """
    Test the integration between the data source selector and the Dropbox selector.
    
    This test verifies that when a user selects data from Dropbox, the data source
    selector correctly returns the data with the appropriate metadata.
    """
    # Configure the mock tabs
    mock_tabs = [MagicMock(), MagicMock()]
    mock_streamlit['tabs'].return_value = mock_tabs
    
    # Configure the mock context managers for tabs
    mock_streamlit['tabs'].return_value[0].__enter__ = MagicMock()
    mock_streamlit['tabs'].return_value[0].__exit__ = MagicMock()
    mock_streamlit['tabs'].return_value[1].__enter__ = MagicMock()
    mock_streamlit['tabs'].return_value[1].__exit__ = MagicMock()
    
    # Call the function
    result = render_data_source_selector()
    
    # Check that the Dropbox selector was called
    mock_dropbox_selector.assert_called_once()
    
    # Check that the Google Sheets selector was not called (since Dropbox returned data)
    mock_google_sheets_selector.assert_not_called()
    
    # Check that the result has the correct structure
    assert result is not None
    assert result["source"] == "dropbox"
    assert isinstance(result["data"], pd.DataFrame)
    assert result["metadata"]["file_path"] == "/test/path/file.csv"
    assert result["metadata"]["file_name"] == "file.csv"
    assert result["metadata"]["file_type"] == "csv"

def test_data_source_selector_google_sheets_integration(mock_streamlit, mock_dropbox_selector, mock_google_sheets_selector):
    """
    Test the integration between the data source selector and the Google Sheets selector.
    
    This test verifies that when a user selects data from Google Sheets, the data source
    selector correctly returns the data with the appropriate metadata.
    """
    # Configure the mock tabs
    mock_tabs = [MagicMock(), MagicMock()]
    mock_streamlit['tabs'].return_value = mock_tabs
    
    # Configure the mock context managers for tabs
    mock_streamlit['tabs'].return_value[0].__enter__ = MagicMock()
    mock_streamlit['tabs'].return_value[0].__exit__ = MagicMock()
    mock_streamlit['tabs'].return_value[1].__enter__ = MagicMock()
    mock_streamlit['tabs'].return_value[1].__exit__ = MagicMock()
    
    # Configure the Dropbox selector to return None (no data selected)
    mock_dropbox_selector.return_value = None
    
    # Call the function
    result = render_data_source_selector()
    
    # Check that both selectors were called
    mock_dropbox_selector.assert_called_once()
    mock_google_sheets_selector.assert_called_once()
    
    # Check that the result has the correct structure
    assert result is not None
    assert result["source"] == "google_sheets"
    assert isinstance(result["data"], pd.DataFrame)
    assert result["metadata"]["spreadsheet_id"] == "test_spreadsheet_id"
    assert result["metadata"]["spreadsheet_name"] == "Test Spreadsheet"
    assert result["metadata"]["sheet_name"] == "Sheet1"

def test_data_source_selector_no_selection(mock_streamlit, mock_dropbox_selector, mock_google_sheets_selector):
    """
    Test the data source selector when no data is selected.
    
    This test verifies that when a user doesn't select any data, the data source
    selector correctly returns None.
    """
    # Configure the mock tabs
    mock_tabs = [MagicMock(), MagicMock()]
    mock_streamlit['tabs'].return_value = mock_tabs
    
    # Configure the mock context managers for tabs
    mock_streamlit['tabs'].return_value[0].__enter__ = MagicMock()
    mock_streamlit['tabs'].return_value[0].__exit__ = MagicMock()
    mock_streamlit['tabs'].return_value[1].__enter__ = MagicMock()
    mock_streamlit['tabs'].return_value[1].__exit__ = MagicMock()
    
    # Configure both selectors to return None (no data selected)
    mock_dropbox_selector.return_value = None
    mock_google_sheets_selector.return_value = None
    
    # Call the function
    result = render_data_source_selector()
    
    # Check that both selectors were called
    mock_dropbox_selector.assert_called_once()
    mock_google_sheets_selector.assert_called_once()
    
    # Check that the result is None
    assert result is None
"""