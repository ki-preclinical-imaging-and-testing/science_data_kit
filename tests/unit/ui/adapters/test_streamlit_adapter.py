"""
Unit tests for the Streamlit adapter.

This module contains tests for the Streamlit adapter functions that render
framework-agnostic page data using Streamlit components.
"""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
import pandas as pd

from science_data_kit.core.models.page import (
    PageData,
    DashboardPageData,
    FileExplorerPageData,
    ConnectPageData,
    ExplorePageData
)
from science_data_kit.core.pages.base import BasePage
from science_data_kit.ui.adapters.streamlit_adapter import (
    render_page,
    _render_dashboard_page,
    _render_file_explorer_page,
    _render_connect_page,
    _render_explore_page,
    render_dashboard_page,
    render_file_browser_page,
    render_connect_page,
    render_explore_page
)

class MockBasePage(BasePage):
    """Mock implementation of BasePage for testing."""
    
    def __init__(self, page_data):
        """Initialize with specific page data for testing."""
        super().__init__()
        self._page_data = page_data
    
    def get_page_data(self):
        """Return the page data."""
        return self._page_data

def test_render_page_dashboard(mock_streamlit):
    """Test that render_page correctly renders a dashboard page."""
    # Create mock page data
    page_data = DashboardPageData(
        title="Test Dashboard",
        metrics=[{"title": "Test Metric", "value": 42, "trend": 5}],
        charts=[{"name": "Test Chart", "type": "bar"}],
        tables=[{"name": "Test Table", "data": pd.DataFrame({"A": [1, 2, 3]})}],
        status_items=[{"name": "Test Status", "status": "OK"}]
    )
    
    # Create mock page instance
    page = MockBasePage(page_data)
    
    # Mock the _render_dashboard_page function
    with patch('science_data_kit.ui.adapters.streamlit_adapter._render_dashboard_page') as mock_render:
        # Call the function
        render_page(page)
        
        # Check that the correct render function was called with the page data
        mock_render.assert_called_once_with(page_data)

def test_render_page_file_explorer(mock_streamlit):
    """Test that render_page correctly renders a file explorer page."""
    # Create mock page data
    page_data = FileExplorerPageData(
        title="Test File Explorer",
        current_path="/test/path",
        files=[{"name": "test.txt", "path": "/test/path/test.txt", "size": 100, "modified": 1625097600}],
        directories=[{"name": "test_dir", "path": "/test/path/test_dir"}]
    )
    
    # Create mock page instance
    page = MockBasePage(page_data)
    
    # Mock the _render_file_explorer_page function
    with patch('science_data_kit.ui.adapters.streamlit_adapter._render_file_explorer_page') as mock_render:
        # Call the function
        render_page(page)
        
        # Check that the correct render function was called with the page data
        mock_render.assert_called_once_with(page_data)

def test_render_page_connect(mock_streamlit):
    """Test that render_page correctly renders a connect page."""
    # Create mock page data
    page_data = ConnectPageData(
        title="Test Connect",
        available_connections=[{"id": "test", "name": "Test Connection", "description": "Test Description", "config_fields": []}],
        active_connections=[{"id": "test", "name": "Test Connection", "type": "test"}],
        connection_status={"test": True}
    )
    
    # Create mock page instance
    page = MockBasePage(page_data)
    
    # Mock the _render_connect_page function
    with patch('science_data_kit.ui.adapters.streamlit_adapter._render_connect_page') as mock_render:
        # Call the function
        render_page(page)
        
        # Check that the correct render function was called with the page data
        mock_render.assert_called_once_with(page_data)

def test_render_page_explore(mock_streamlit):
    """Test that render_page correctly renders an explore page."""
    # Create mock page data
    page_data = ExplorePageData(
        title="Test Explore",
        available_data_sources=[{"id": "test", "name": "Test Source"}],
        query_results={"data": pd.DataFrame({"A": [1, 2, 3]})},
        visualizations=[{"name": "Test Visualization", "type": "bar"}]
    )
    
    # Create mock page instance
    page = MockBasePage(page_data)
    
    # Mock the _render_explore_page function
    with patch('science_data_kit.ui.adapters.streamlit_adapter._render_explore_page') as mock_render:
        # Call the function
        render_page(page)
        
        # Check that the correct render function was called with the page data
        mock_render.assert_called_once_with(page_data)

def test_render_page_unknown(mock_streamlit):
    """Test that render_page handles unknown page types gracefully."""
    # Create mock page data with a custom class
    class CustomPageData(PageData):
        pass
    
    page_data = CustomPageData(title="Test Custom")
    
    # Create mock page instance
    page = MockBasePage(page_data)
    
    # Call the function
    render_page(page)
    
    # Check that a title was rendered
    mock_streamlit['title'].assert_called_once_with("Test Custom")
    # Check that a warning was displayed
    mock_streamlit['write'].assert_called_with("This page type doesn't have a specific renderer yet.")

def test_render_dashboard_page(mock_streamlit):
    """Test that render_dashboard_page creates a DashboardPage and renders it."""
    # Mock the DashboardPage class
    with patch('science_data_kit.ui.adapters.streamlit_adapter.DashboardPage') as mock_dashboard_class, \
         patch('science_data_kit.ui.adapters.streamlit_adapter.render_page') as mock_render:
        
        # Set up the mock
        mock_dashboard_instance = MagicMock()
        mock_dashboard_class.return_value = mock_dashboard_instance
        
        # Call the function
        render_dashboard_page()
        
        # Check that a DashboardPage was created
        mock_dashboard_class.assert_called_once()
        
        # Check that render_page was called with the DashboardPage instance
        mock_render.assert_called_once_with(mock_dashboard_instance)

def test_render_file_browser_page(mock_streamlit):
    """Test that render_file_browser_page creates a FileBrowserPage and renders it."""
    # Mock the FileBrowserPage class
    with patch('science_data_kit.ui.adapters.streamlit_adapter.FileBrowserPage') as mock_file_browser_class, \
         patch('science_data_kit.ui.adapters.streamlit_adapter.render_page') as mock_render:
        
        # Set up the mock
        mock_file_browser_instance = MagicMock()
        mock_file_browser_class.return_value = mock_file_browser_instance
        
        # Call the function
        render_file_browser_page()
        
        # Check that a FileBrowserPage was created
        mock_file_browser_class.assert_called_once()
        
        # Check that render_page was called with the FileBrowserPage instance
        mock_render.assert_called_once_with(mock_file_browser_instance)

def test_render_connect_page(mock_streamlit):
    """Test that render_connect_page creates a ConnectPage and renders it."""
    # Mock the ConnectPage class
    with patch('science_data_kit.ui.adapters.streamlit_adapter.ConnectPage') as mock_connect_class, \
         patch('science_data_kit.ui.adapters.streamlit_adapter.render_page') as mock_render:
        
        # Set up the mock
        mock_connect_instance = MagicMock()
        mock_connect_class.return_value = mock_connect_instance
        
        # Call the function
        render_connect_page()
        
        # Check that a ConnectPage was created
        mock_connect_class.assert_called_once()
        
        # Check that render_page was called with the ConnectPage instance
        mock_render.assert_called_once_with(mock_connect_instance)

def test_render_explore_page(mock_streamlit):
    """Test that render_explore_page creates an ExplorePage and renders it."""
    # Mock the ExplorePage class
    with patch('science_data_kit.ui.adapters.streamlit_adapter.ExplorePage') as mock_explore_class, \
         patch('science_data_kit.ui.adapters.streamlit_adapter.render_page') as mock_render:
        
        # Set up the mock
        mock_explore_instance = MagicMock()
        mock_explore_class.return_value = mock_explore_instance
        
        # Call the function
        render_explore_page()
        
        # Check that an ExplorePage was created
        mock_explore_class.assert_called_once()
        
        # Check that render_page was called with the ExplorePage instance
        mock_render.assert_called_once_with(mock_explore_instance)

def test_dashboard_page_render_components(mock_streamlit):
    """Test that _render_dashboard_page renders the correct components."""
    # Create mock page data
    page_data = DashboardPageData(
        title="Test Dashboard",
        metrics=[{"title": "Test Metric", "value": 42, "trend": 5}],
        charts=[{"name": "Test Chart", "type": "bar", "data": {"data": [{"x": 1, "y": 2}], "x_axis": "X", "y_axis": "Y"}}],
        tables=[{"name": "Test Table", "data": pd.DataFrame({"A": [1, 2, 3]})}],
        status_items=[{"name": "Test Status", "status": "OK"}]
    )
    
    # Call the function
    _render_dashboard_page(page_data)
    
    # Check that the title was rendered
    mock_streamlit['title'].assert_called_with("Test Dashboard")
    
    # Check that metrics were rendered
    mock_streamlit['metric'].assert_called_with("Test Metric", 42, 5)

def test_file_explorer_page_render_components(mock_streamlit):
    """Test that _render_file_explorer_page renders the correct components."""
    # Create mock page data
    page_data = FileExplorerPageData(
        title="Test File Explorer",
        current_path="/test/path",
        files=[{"name": "test.txt", "path": "/test/path/test.txt", "size": 100, "modified": 1625097600, "type": "file"}],
        directories=[{"name": "test_dir", "path": "/test/path/test_dir", "type": "directory"}]
    )
    
    # Call the function
    _render_file_explorer_page(page_data)
    
    # Check that the title was rendered
    mock_streamlit['title'].assert_called_with("Test File Explorer")
    
    # Check that the current path was displayed
    mock_streamlit['write'].assert_any_call("Current Path: /test/path")