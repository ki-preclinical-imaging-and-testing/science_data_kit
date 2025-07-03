"""
Test script for multiple database connections.

This script tests the ability to maintain multiple database connections,
only deactivating running ones when a new one is initialized with the
same URI and database name.
"""

import sys
import os
from typing import Dict, Any
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from science_data_kit.core.db.db_manager import Neo4jManager

def test_multiple_connections():
    """Test that multiple connections can be maintained."""
    # Create a Neo4jManager instance
    manager = Neo4jManager()

    # Define test connection parameters
    connections = [
        {
            "name": "Connection 1",
            "uri": "bolt://localhost:7687",
            "user": "neo4j",
            "password": "password",
            "database": "neo4j"
        },
        {
            "name": "Connection 2",
            "uri": "bolt://localhost:7688",  # Different port
            "user": "neo4j",
            "password": "password",
            "database": "neo4j"
        },
        {
            "name": "Connection 3",
            "uri": "bolt://localhost:7687",  # Same as Connection 1
            "user": "neo4j",
            "password": "password",
            "database": "system"  # Different database
        },
        {
            "name": "Connection 4",
            "uri": "bolt://localhost:7687",  # Same as Connection 1
            "user": "neo4j",
            "password": "password",
            "database": "neo4j"  # Same database as Connection 1
        }
    ]

    # Mock the Neo4j driver
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_result = MagicMock()

    # Configure the mocks
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_session.run.return_value = mock_result

    # Patch the GraphDatabase.driver method to return our mock driver
    with patch('neo4j.GraphDatabase.driver', return_value=mock_driver):
        # Create the connections
        for conn in connections:
            manager.uri = conn["uri"]
            manager.user = conn["user"]
            manager.password = conn["password"]
            manager.database = conn["database"]

            # Connect using the mocked driver
            manager._connect(conn["name"])
            print(f"Connected to {conn['name']}")
            # Print the connections dictionary
            print(f"Connections after connecting {conn['name']}: {manager._connections.keys()}")

    # Get all connection names
    connection_names = manager.get_connection_names()
    print(f"Connection names: {connection_names}")

    # Check if Connection 1 was closed when Connection 4 was created
    # (they have the same URI and database)
    if "Connection 1" in connection_names:
        print("ERROR: Connection 1 should have been closed when Connection 4 was created")
    else:
        print("SUCCESS: Connection 1 was correctly closed when Connection 4 was created")

    # Check if Connection 2 and Connection 3 are still active
    # (they have different URIs or databases from Connection 4)
    if "Connection 2" in connection_names and "Connection 3" in connection_names:
        print("SUCCESS: Connection 2 and Connection 3 are still active")
    else:
        print("ERROR: Connection 2 and/or Connection 3 were incorrectly closed")

    # Check if Connection 4 is active
    if "Connection 4" in connection_names:
        print("SUCCESS: Connection 4 is active")
    else:
        print("ERROR: Connection 4 is not active")

    # Test setting active connection
    for name in connection_names:
        success = manager.set_active_connection(name)
        if success:
            print(f"SUCCESS: Set {name} as active connection")
        else:
            print(f"ERROR: Failed to set {name} as active connection")

        # Check if the active connection name is correct
        active_name = manager.get_active_connection_name()
        if active_name == name:
            print(f"SUCCESS: Active connection name is {name}")
        else:
            print(f"ERROR: Active connection name is {active_name}, expected {name}")

    # Close all connections
    for name in connection_names.copy():
        manager.close(name)
        print(f"Closed {name}")

    # Check if all connections are closed
    if not manager.get_connection_names():
        print("SUCCESS: All connections are closed")
    else:
        print(f"ERROR: Some connections are still open: {manager.get_connection_names()}")

if __name__ == "__main__":
    test_multiple_connections()
