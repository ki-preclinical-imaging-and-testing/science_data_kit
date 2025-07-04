"""
Integration tests for database operations functionality.

This module contains tests that verify the interaction between
the database operations and the Neo4j database.
"""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

from science_data_kit.core.db.graph_utils import Neo4jConnection


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver for testing."""
    with patch('neo4j.GraphDatabase.driver') as mock_driver:
        # Configure the mock driver to return a mock session
        mock_session = MagicMock()
        mock_driver.return_value.session.return_value = mock_session
        
        # Configure the mock session to return a mock result
        mock_result = MagicMock()
        mock_session.run.return_value = mock_result
        
        # Configure the mock result to return test data
        mock_result.__iter__.return_value = [
            {"name": "Node1", "type": "Person", "age": 30},
            {"name": "Node2", "type": "Person", "age": 25},
            {"name": "Node3", "type": "Organization", "age": None}
        ]
        
        yield mock_driver


def test_execute_query(mock_neo4j_driver):
    """
    Test the execute_query method of Neo4jConnection.
    
    This test verifies that the execute_query method correctly executes a Cypher query
    and returns the results as a list of dictionaries.
    """
    # Create a Neo4jConnection with test parameters
    connection = Neo4jConnection(
        uri="bolt://test-neo4j:7687",
        user="test_user",
        password="test_password",
        database="test_db"
    )
    
    # Execute a test query
    query = "MATCH (n) RETURN n.name as name, n.type as type, n.age as age"
    result = connection.execute_query(query)
    
    # Check that the driver was created with the correct parameters
    mock_neo4j_driver.assert_called_once_with(
        "bolt://test-neo4j:7687",
        auth=("test_user", "test_password")
    )
    
    # Check that the session was created with the correct database
    mock_neo4j_driver.return_value.session.assert_called_once_with(database="test_db")
    
    # Check that the query was executed
    mock_neo4j_driver.return_value.session.return_value.run.assert_called_once_with(query, {})
    
    # Check the result
    assert len(result) == 3
    assert result[0]["name"] == "Node1"
    assert result[0]["type"] == "Person"
    assert result[0]["age"] == 30
    assert result[1]["name"] == "Node2"
    assert result[1]["type"] == "Person"
    assert result[1]["age"] == 25
    assert result[2]["name"] == "Node3"
    assert result[2]["type"] == "Organization"
    assert result[2]["age"] is None


def test_query_to_dataframe(mock_neo4j_driver):
    """
    Test the query_to_dataframe method of Neo4jConnection.
    
    This test verifies that the query_to_dataframe method correctly executes a Cypher query
    and returns the results as a Pandas DataFrame.
    """
    # Create a Neo4jConnection with test parameters
    connection = Neo4jConnection(
        uri="bolt://test-neo4j:7687",
        user="test_user",
        password="test_password",
        database="test_db"
    )
    
    # Execute a test query
    query = "MATCH (n) RETURN n.name as name, n.type as type, n.age as age"
    result = connection.query_to_dataframe(query)
    
    # Check that the query was executed
    mock_neo4j_driver.return_value.session.return_value.run.assert_called_once_with(query, {})
    
    # Check the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert list(result.columns) == ["name", "type", "age"]
    assert result["name"].tolist() == ["Node1", "Node2", "Node3"]
    assert result["type"].tolist() == ["Person", "Person", "Organization"]
    assert result["age"].tolist() == [30, 25, None]


def test_query_to_value(mock_neo4j_driver):
    """
    Test the query_to_value method of Neo4jConnection.
    
    This test verifies that the query_to_value method correctly executes a Cypher query
    and returns a single value.
    """
    # Create a Neo4jConnection with test parameters
    connection = Neo4jConnection(
        uri="bolt://test-neo4j:7687",
        user="test_user",
        password="test_password",
        database="test_db"
    )
    
    # Configure the mock result to return a single value
    mock_neo4j_driver.return_value.session.return_value.run.return_value.__iter__.return_value = [
        {"count": 42}
    ]
    
    # Execute a test query
    query = "MATCH (n) RETURN count(n) as count"
    result = connection.query_to_value(query)
    
    # Check that the query was executed
    mock_neo4j_driver.return_value.session.return_value.run.assert_called_once_with(query, {})
    
    # Check the result
    assert result == 42


def test_execute_query_with_parameters(mock_neo4j_driver):
    """
    Test the execute_query method with parameters.
    
    This test verifies that the execute_query method correctly passes parameters to the query.
    """
    # Create a Neo4jConnection with test parameters
    connection = Neo4jConnection(
        uri="bolt://test-neo4j:7687",
        user="test_user",
        password="test_password",
        database="test_db"
    )
    
    # Execute a test query with parameters
    query = "MATCH (n) WHERE n.type = $type RETURN n.name as name, n.type as type, n.age as age"
    parameters = {"type": "Person"}
    connection.execute_query(query, parameters)
    
    # Check that the query was executed with the correct parameters
    mock_neo4j_driver.return_value.session.return_value.run.assert_called_once_with(query, parameters)


def test_connection_error_handling():
    """
    Test error handling when the connection fails.
    
    This test verifies that the Neo4jConnection class correctly handles connection errors.
    """
    # Mock the GraphDatabase.driver to raise an exception
    with patch('neo4j.GraphDatabase.driver', side_effect=Exception("Connection failed")):
        # Attempt to create a Neo4jConnection
        with pytest.raises(ConnectionError) as excinfo:
            Neo4jConnection(
                uri="bolt://test-neo4j:7687",
                user="test_user",
                password="test_password",
                database="test_db"
            )
        
        # Check the error message
        assert "Failed to connect to Neo4j" in str(excinfo.value)


def test_query_error_handling(mock_neo4j_driver):
    """
    Test error handling when a query fails.
    
    This test verifies that the Neo4jConnection class correctly handles query execution errors.
    """
    # Create a Neo4jConnection with test parameters
    connection = Neo4jConnection(
        uri="bolt://test-neo4j:7687",
        user="test_user",
        password="test_password",
        database="test_db"
    )
    
    # Configure the mock session to raise an exception when run is called
    mock_neo4j_driver.return_value.session.return_value.run.side_effect = Exception("Query failed")
    
    # Attempt to execute a query
    with pytest.raises(RuntimeError) as excinfo:
        connection.execute_query("MATCH (n) RETURN n")
    
    # Check the error message
    assert "Query execution failed" in str(excinfo.value)