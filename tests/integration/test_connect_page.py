"""
Integration tests for the Connect page.

This module contains tests that verify the interaction between
the Connect page UI and the underlying functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st

from science_data_kit.ui.pages.connect import ConnectPage
from science_data_kit.core.db.db_manager import Neo4jManager

@pytest.fixture
def mock_db_manager():
    """Mock Neo4j database manager for testing."""
    mock_manager = MagicMock(spec=Neo4jManager)
    mock_manager.is_connected.return_value = False
    return mock_manager

def test_connect_page_initialization():
    """Test that the Connect page initializes correctly."""
    with patch('science_data_kit.ui.pages.connect.db_manager') as mock_manager:
        # Create the page
        page = ConnectPage()
        
        # Check that the page was initialized correctly
        assert page.title == "Connect"
        assert page.icon == "🌐"
        assert page.db_manager == mock_manager

def test_database_connect_success(mock_streamlit, mock_db_manager):
    """Test successful database connection."""
    # Configure the mock database manager
    mock_db_manager._connect.return_value = True
    mock_db_manager.is_connected.return_value = True
    
    with patch('science_data_kit.ui.pages.connect.db_manager', mock_db_manager):
        # Create the page
        page = ConnectPage()
        
        # Call the connect method
        page._on_database_connect("bolt://localhost:7687", "neo4j", "password", "neo4j")
        
        # Check that the database manager was called correctly
        assert mock_db_manager.uri == "bolt://localhost:7687"
        assert mock_db_manager.user == "neo4j"
        assert mock_db_manager.password == "password"
        assert mock_db_manager.database == "neo4j"
        mock_db_manager._connect.assert_called_once()
        
        # Check that the session state was updated
        assert st.session_state["connected"] == True
        assert st.session_state["neo4j_uri"] == "bolt://localhost:7687"
        assert st.session_state["neo4j_user"] == "neo4j"
        assert st.session_state["neo4j_password"] == "password"
        assert st.session_state["neo4j_database"] == "neo4j"
        
        # Check that a success message was displayed
        mock_streamlit['success'].assert_called_once_with("Connected to Neo4j database at bolt://localhost:7687")

def test_database_connect_failure(mock_streamlit, mock_db_manager):
    """Test database connection failure."""
    # Configure the mock database manager to raise an exception
    mock_db_manager._connect.side_effect = Exception("Connection failed")
    
    with patch('science_data_kit.ui.pages.connect.db_manager', mock_db_manager):
        # Create the page
        page = ConnectPage()
        
        # Call the connect method
        page._on_database_connect("bolt://localhost:7687", "neo4j", "password", "neo4j")
        
        # Check that the database manager was called correctly
        assert mock_db_manager.uri == "bolt://localhost:7687"
        assert mock_db_manager.user == "neo4j"
        assert mock_db_manager.password == "password"
        assert mock_db_manager.database == "neo4j"
        mock_db_manager._connect.assert_called_once()
        
        # Check that an error message was displayed
        mock_streamlit['error'].assert_called_once_with("Failed to connect to Neo4j: Connection failed")

def test_database_disconnect(mock_streamlit, mock_db_manager):
    """Test database disconnection."""
    with patch('science_data_kit.ui.pages.connect.db_manager', mock_db_manager):
        # Create the page
        page = ConnectPage()
        
        # Call the disconnect method
        page._on_database_disconnect()
        
        # Check that the database manager was called correctly
        mock_db_manager.close.assert_called_once()
        
        # Check that the session state was updated
        assert st.session_state["connected"] == False
        
        # Check that a success message was displayed
        mock_streamlit['success'].assert_called_once_with("Disconnected from Neo4j database")

def test_neo4j_container_start_success(mock_streamlit, mock_db_manager):
    """Test successful Neo4j container start."""
    # Configure the mock database manager
    mock_db_manager.start_container.return_value = True
    
    with patch('science_data_kit.ui.pages.connect.db_manager', mock_db_manager), \
         patch.object(st.session_state, 'get', return_value="latest"):
        # Create the page
        page = ConnectPage()
        
        # Call the start method
        page._on_neo4j_start()
        
        # Check that the database manager was called correctly
        mock_db_manager.start_container.assert_called_once_with("latest")
        
        # Check that the session state was updated
        assert st.session_state["container_status"] == "running"
        
        # Check that a success message was displayed
        mock_streamlit['success'].assert_called_once_with("Neo4j container started successfully")

def test_neo4j_container_start_failure(mock_streamlit, mock_db_manager):
    """Test Neo4j container start failure."""
    # Configure the mock database manager
    mock_db_manager.start_container.return_value = False
    
    with patch('science_data_kit.ui.pages.connect.db_manager', mock_db_manager), \
         patch.object(st.session_state, 'get', return_value="latest"):
        # Create the page
        page = ConnectPage()
        
        # Call the start method
        page._on_neo4j_start()
        
        # Check that the database manager was called correctly
        mock_db_manager.start_container.assert_called_once_with("latest")
        
        # Check that an error message was displayed
        mock_streamlit['error'].assert_called_once_with("Failed to start Neo4j container")

def test_neo4j_container_stop_success(mock_streamlit, mock_db_manager):
    """Test successful Neo4j container stop."""
    # Configure the mock database manager
    mock_db_manager.stop_container.return_value = True
    
    with patch('science_data_kit.ui.pages.connect.db_manager', mock_db_manager):
        # Create the page
        page = ConnectPage()
        
        # Call the stop method
        page._on_neo4j_stop()
        
        # Check that the database manager was called correctly
        mock_db_manager.stop_container.assert_called_once()
        
        # Check that the session state was updated
        assert st.session_state["container_status"] == "stopped"
        
        # Check that a success message was displayed
        mock_streamlit['success'].assert_called_once_with("Neo4j container stopped successfully")

def test_render_content_connected(mock_streamlit, mock_db_manager):
    """Test rendering the Connect page content when connected."""
    # Configure the mock database manager
    mock_db_manager.is_connected.return_value = True
    mock_db_manager.execute_query.side_effect = [
        [{'name': 'Neo4j', 'versions': ['4.4.0'], 'edition': 'community'}],
        [{'database': 'neo4j', 'totalSize': '10MB'}]
    ]
    
    with patch('science_data_kit.ui.pages.connect.db_manager', mock_db_manager), \
         patch.object(st.session_state, 'get', side_effect=lambda key, default=None: {
             'connected': True,
             'neo4j_uri': 'bolt://localhost:7687',
             'container_status': 'running',
             'http_port': 7474,
             'bolt_port': 7687,
             'jupyter_url': 'http://localhost:8888',
             'jupyter_token': 'test-token',
             'neodash_url': 'http://localhost:5005'
         }.get(key, default)):
        # Create the page
        page = ConnectPage()
        
        # Call the render_content method
        page.render_content()
        
        # Check that the page content was rendered correctly
        mock_streamlit['write'].assert_any_call("Connect to data sources and spin up necessary infrastructure.")
        mock_streamlit['header'].assert_any_call("Database Connection")
        mock_streamlit['success'].assert_any_call("Connected to Neo4j database at bolt://localhost:7687")
        
        # Check that the database information was displayed
        mock_db_manager.execute_query.assert_any_call("CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition")
        mock_db_manager.execute_query.assert_any_call("CALL dbms.database.size() YIELD database, totalSize RETURN database, totalSize")
        
        # Check that the container information was displayed
        mock_streamlit['header'].assert_any_call("Neo4j Container")
        mock_streamlit['success'].assert_any_call("Neo4j container is running")
        
        # Check that the Jupyter Lab information was displayed
        mock_streamlit['header'].assert_any_call("Jupyter Lab")
        mock_streamlit['success'].assert_any_call("Jupyter Lab is running at http://localhost:8888")
        
        # Check that the NeoDash information was displayed
        mock_streamlit['header'].assert_any_call("NeoDash")
        mock_streamlit['success'].assert_any_call("NeoDash is running at http://localhost:5005")

def test_render_content_not_connected(mock_streamlit, mock_db_manager):
    """Test rendering the Connect page content when not connected."""
    # Configure the mock database manager
    mock_db_manager.is_connected.return_value = False
    
    with patch('science_data_kit.ui.pages.connect.db_manager', mock_db_manager), \
         patch.object(st.session_state, 'get', side_effect=lambda key, default=None: {
             'connected': False,
             'container_status': 'stopped',
             'jupyter_url': '',
             'jupyter_token': '',
             'neodash_url': ''
         }.get(key, default)):
        # Create the page
        page = ConnectPage()
        
        # Call the render_content method
        page.render_content()
        
        # Check that the page content was rendered correctly
        mock_streamlit['write'].assert_any_call("Connect to data sources and spin up necessary infrastructure.")
        mock_streamlit['header'].assert_any_call("Database Connection")
        mock_streamlit['info'].assert_any_call("Not connected to a Neo4j database. Use the sidebar to connect.")
        
        # Check that the container information was displayed
        mock_streamlit['header'].assert_any_call("Neo4j Container")
        mock_streamlit['warning'].assert_any_call("Neo4j container is stopped")
        
        # Check that the Jupyter Lab information was displayed
        mock_streamlit['header'].assert_any_call("Jupyter Lab")
        mock_streamlit['info'].assert_any_call("Jupyter Lab is not running. Use the sidebar to start it.")
        
        # Check that the NeoDash information was displayed
        mock_streamlit['header'].assert_any_call("NeoDash")
        mock_streamlit['info'].assert_any_call("NeoDash is not running. Use the sidebar to start it.")