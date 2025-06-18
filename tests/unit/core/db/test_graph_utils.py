"""
Unit tests for the graph_utils module.

This module contains tests for the Neo4jConnection class and related functions.
"""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import neo4j
from neo4j.exceptions import Neo4jError

from science_data_kit.core.db.graph_utils import Neo4jConnection, create_connection_from_manager

@pytest.fixture
def mock_driver():
    """Mock Neo4j driver for testing."""
    mock = MagicMock(spec=neo4j.Driver)
    return mock

@pytest.fixture
def mock_session():
    """Mock Neo4j session for testing."""
    mock = MagicMock(spec=neo4j.Session)
    return mock

@pytest.fixture
def mock_result():
    """Mock Neo4j result for testing."""
    mock = MagicMock(spec=neo4j.Result)
    return mock

@pytest.fixture
def mock_record():
    """Mock Neo4j record for testing."""
    mock = MagicMock(spec=neo4j.Record)
    return mock

@pytest.fixture
def mock_ontology_annotation():
    """Mock OntologyAnnotation for testing."""
    mock = MagicMock()
    mock.term = "test_term"
    mock.term_accession = "http://example.org/test_term"
    mock.term_source = "test_source"
    return mock

def test_neo4j_connection_init():
    """Test Neo4jConnection initialization."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mock
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Check that the driver was created with the correct parameters
        mock_graph_db.driver.assert_called_once_with("bolt://localhost:7687", auth=("neo4j", "password"))
        
        # Check that the connection attributes were set correctly
        assert connection.uri == "bolt://localhost:7687"
        assert connection.user == "neo4j"
        assert connection.password == "password"
        assert connection.database == "neo4j"
        assert connection._driver == mock_driver

def test_neo4j_connection_init_failure():
    """Test Neo4jConnection initialization failure."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mock to raise an exception
        mock_graph_db.driver.side_effect = Neo4jError("Connection failed")
        
        # Check that the connection raises an exception
        with pytest.raises(ConnectionError):
            Neo4jConnection("bolt://localhost:7687", "neo4j", "password")

def test_neo4j_connection_close(mock_driver):
    """Test Neo4jConnection close method."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mock
        mock_graph_db.driver.return_value = mock_driver
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Close the connection
        connection.close()
        
        # Check that the driver was closed
        mock_driver.close.assert_called_once()
        
        # Check that the driver was set to None
        assert connection._driver is None

def test_execute_query(mock_driver, mock_session, mock_result, mock_record):
    """Test execute_query method."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mocks
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value = mock_session
        mock_session.run.return_value = mock_result
        mock_record.__getitem__.side_effect = lambda key: f"value_{key}"
        mock_result.__iter__.return_value = [mock_record]
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Execute a query
        result = connection.execute_query("MATCH (n) RETURN n", {"param": "value"})
        
        # Check that the session was created with the correct database
        mock_driver.session.assert_called_once_with(database="neo4j")
        
        # Check that the query was executed with the correct parameters
        mock_session.run.assert_called_once_with("MATCH (n) RETURN n", {"param": "value"})
        
        # Check that the result was converted to a list of dictionaries
        assert result == [dict(mock_record)]

def test_execute_query_no_driver():
    """Test execute_query method with no driver."""
    # Create a connection without a driver
    connection = Neo4jConnection.__new__(Neo4jConnection)
    connection._driver = None
    
    # Check that the query raises an exception
    with pytest.raises(ConnectionError):
        connection.execute_query("MATCH (n) RETURN n")

def test_execute_query_failure(mock_driver, mock_session):
    """Test execute_query method failure."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mocks
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value = mock_session
        mock_session.run.side_effect = Neo4jError("Query failed")
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Check that the query raises an exception
        with pytest.raises(RuntimeError):
            connection.execute_query("MATCH (n) RETURN n")

def test_query_to_dataframe(mock_driver, mock_session, mock_result, mock_record):
    """Test query_to_dataframe method."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mocks
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value = mock_session
        mock_session.run.return_value = mock_result
        mock_record.__getitem__.side_effect = lambda key: f"value_{key}"
        mock_result.__iter__.return_value = [mock_record]
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Execute a query
        result = connection.query_to_dataframe("MATCH (n) RETURN n", {"param": "value"})
        
        # Check that the result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        
        # Check that the DataFrame contains the expected data
        assert result.to_dict('records') == [dict(mock_record)]

def test_query_to_dict(mock_driver, mock_session, mock_result, mock_record):
    """Test query_to_dict method."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mocks
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value = mock_session
        mock_session.run.return_value = mock_result
        mock_record.__getitem__.side_effect = lambda key: f"value_{key}"
        mock_result.__iter__.return_value = [mock_record]
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Execute a query
        result = connection.query_to_dict("MATCH (n) RETURN n", {"param": "value"})
        
        # Check that the result is a list of dictionaries
        assert result == [dict(mock_record)]

def test_query_to_value_single(mock_driver, mock_session, mock_result, mock_record):
    """Test query_to_value method with a single value."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mocks
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value = mock_session
        mock_session.run.return_value = mock_result
        mock_record.values.return_value = ["value"]
        mock_result.__iter__.return_value = [mock_record]
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Execute a query
        result = connection.query_to_value("MATCH (n) RETURN n", {"param": "value"})
        
        # Check that the result is a single value
        assert result == "value"

def test_query_to_value_multiple(mock_driver, mock_session, mock_result, mock_record):
    """Test query_to_value method with multiple values."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mocks
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value = mock_session
        mock_session.run.return_value = mock_result
        
        # Create multiple records
        record1 = MagicMock()
        record1.values.return_value = ["value1"]
        record2 = MagicMock()
        record2.values.return_value = ["value2"]
        mock_result.__iter__.return_value = [record1, record2]
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Execute a query
        result = connection.query_to_value("MATCH (n) RETURN n", {"param": "value"})
        
        # Check that the result is a list of values
        assert result == ["value1", "value2"]

def test_push_dataframe(mock_driver, mock_session, mock_result):
    """Test push_dataframe method."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mocks
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value = mock_session
        mock_session.run.return_value = mock_result
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Create a DataFrame
        df = pd.DataFrame({
            "label": ["Person", "Movie"],
            "name": ["John", "The Matrix"],
            "year": [1990, 1999]
        })
        
        # Push the DataFrame
        connection.push_dataframe(df, "label", ["name", "year"], ["name"])
        
        # Check that the query was executed twice (once for each row)
        assert mock_session.run.call_count == 2
        
        # Check that the queries were executed with the correct parameters
        mock_session.run.assert_any_call(
            "\n            MERGE (n:Person { name: $name })\n            SET n += { name: $name, year: $year }\n            ",
            {"name": "John", "year": 1990}
        )
        mock_session.run.assert_any_call(
            "\n            MERGE (n:Movie { name: $name })\n            SET n += { name: $name, year: $year }\n            ",
            {"name": "The Matrix", "year": 1999}
        )

def test_push_dataframe_missing_label_column():
    """Test push_dataframe method with a missing label column."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mocks
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Create a DataFrame without the label column
        df = pd.DataFrame({
            "name": ["John", "The Matrix"],
            "year": [1990, 1999]
        })
        
        # Check that pushing the DataFrame raises an exception
        with pytest.raises(ValueError):
            connection.push_dataframe(df, "label", ["name", "year"], ["name"])

def test_push_dataframe_no_match_columns():
    """Test push_dataframe method with no match columns."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mocks
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Create a DataFrame
        df = pd.DataFrame({
            "label": ["Person", "Movie"],
            "name": ["John", "The Matrix"],
            "year": [1990, 1999]
        })
        
        # Check that pushing the DataFrame with no match columns raises an exception
        with pytest.raises(ValueError):
            connection.push_dataframe(df, "label", ["name", "year"], [])

def test_test_connection_success(mock_driver, mock_session, mock_result):
    """Test test_connection method success."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mocks
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value = mock_session
        mock_session.run.return_value = mock_result
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Test the connection
        result = connection.test_connection(quiet=True)
        
        # Check that the result is True
        assert result is True
        
        # Check that the query was executed
        mock_session.run.assert_called_once_with("RETURN 1", None)

def test_test_connection_failure(mock_driver, mock_session):
    """Test test_connection method failure."""
    with patch('science_data_kit.core.db.graph_utils.GraphDatabase') as mock_graph_db:
        # Configure the mocks
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value = mock_session
        mock_session.run.side_effect = Neo4jError("Connection failed")
        
        # Create a connection
        connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
        
        # Check that testing the connection raises an exception
        with pytest.raises(ConnectionError):
            connection.test_connection()

def test_create_connection_from_manager():
    """Test create_connection_from_manager function."""
    with patch('science_data_kit.core.db.graph_utils.Neo4jConnection') as mock_connection_class:
        # Create a mock manager
        mock_manager = MagicMock()
        mock_manager.uri = "bolt://localhost:7687"
        mock_manager.user = "neo4j"
        mock_manager.password = "password"
        mock_manager.database = "neo4j"
        
        # Create a connection from the manager
        create_connection_from_manager(mock_manager)
        
        # Check that the connection was created with the correct parameters
        mock_connection_class.assert_called_once_with(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
            database="neo4j"
        )