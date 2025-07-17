"""
Tests for the API protocol class.

This module contains tests for the APIProtocol class.
"""

import unittest
import pandas as pd
from typing import Any, Dict, List, Optional

from science_data_kit.core.connections.protocols.api import APIProtocol


class MockAPIProtocol(APIProtocol):
    """Mock implementation of APIProtocol for testing."""
    
    def __init__(self, connected=False):
        self._connected = connected
        self._config = {}
        self._resources = {
            "users": [
                {"id": "1", "name": "User 1"},
                {"id": "2", "name": "User 2"}
            ],
            "posts": [
                {"id": "101", "title": "Post 1", "author_id": "1"},
                {"id": "102", "title": "Post 2", "author_id": "2"}
            ]
        }
    
    def connect(self, config: Dict[str, Any]) -> None:
        """Establish connection with the service."""
        self._config = config
        self._connected = True
    
    def disconnect(self) -> None:
        """Clean up connection."""
        self._connected = False
    
    def test_connection(self) -> bool:
        """Verify connection is working."""
        return self._connected
    
    @property
    def connection_type(self) -> str:
        """Return the type of connection."""
        return "api"
    
    @property
    def is_connected(self) -> bool:
        """Check if the connection is currently established."""
        return self._connected
    
    def list_resources(self, resource_type: str) -> List[Dict[str, Any]]:
        """List resources of a specific type."""
        if not self._connected:
            raise ConnectionError("Not connected")
        return self._resources.get(resource_type, [])
    
    def get_resource(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """Get a specific resource."""
        if not self._connected:
            raise ConnectionError("Not connected")
        resources = self._resources.get(resource_type, [])
        for resource in resources:
            if resource.get("id") == resource_id:
                return resource
        raise ValueError(f"Resource {resource_id} not found")
    
    def execute_request(self, endpoint: str, method: str = "GET", 
                       params: Optional[Dict[str, Any]] = None, 
                       data: Optional[Dict[str, Any]] = None,
                       headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute a request to the API."""
        if not self._connected:
            raise ConnectionError("Not connected")
        if endpoint == "users":
            return {"data": self._resources.get("users", [])}
        elif endpoint == "posts":
            return {"data": self._resources.get("posts", [])}
        else:
            return {"data": []}
    
    def get_data_as_dataframe(self, resource_type: str, 
                             query_params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Get data from the API as a pandas DataFrame."""
        if not self._connected:
            raise ConnectionError("Not connected")
        resources = self._resources.get(resource_type, [])
        return pd.DataFrame(resources)


class TestAPIProtocol(unittest.TestCase):
    """Tests for the APIProtocol class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.protocol = MockAPIProtocol()
        self.protocol.connect({"param": "value"})
    
    def test_connection_type(self):
        """Test connection_type property."""
        self.assertEqual(self.protocol.connection_type, "api")
    
    def test_list_resources(self):
        """Test list_resources method."""
        users = self.protocol.list_resources("users")
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]["name"], "User 1")
        
        # Test non-existent resource type
        empty = self.protocol.list_resources("non_existent")
        self.assertEqual(len(empty), 0)
        
        # Test when not connected
        self.protocol.disconnect()
        with self.assertRaises(ConnectionError):
            self.protocol.list_resources("users")
    
    def test_get_resource(self):
        """Test get_resource method."""
        user = self.protocol.get_resource("users", "1")
        self.assertEqual(user["name"], "User 1")
        
        # Test non-existent resource
        with self.assertRaises(ValueError):
            self.protocol.get_resource("users", "999")
        
        # Test when not connected
        self.protocol.disconnect()
        with self.assertRaises(ConnectionError):
            self.protocol.get_resource("users", "1")
    
    def test_execute_request(self):
        """Test execute_request method."""
        response = self.protocol.execute_request("users")
        self.assertIn("data", response)
        self.assertEqual(len(response["data"]), 2)
        
        # Test non-existent endpoint
        response = self.protocol.execute_request("non_existent")
        self.assertIn("data", response)
        self.assertEqual(len(response["data"]), 0)
        
        # Test when not connected
        self.protocol.disconnect()
        with self.assertRaises(ConnectionError):
            self.protocol.execute_request("users")
    
    def test_get_data_as_dataframe(self):
        """Test get_data_as_dataframe method."""
        df = self.protocol.get_data_as_dataframe("users")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["name"], "User 1")
        
        # Test non-existent resource type
        df = self.protocol.get_data_as_dataframe("non_existent")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 0)
        
        # Test when not connected
        self.protocol.disconnect()
        with self.assertRaises(ConnectionError):
            self.protocol.get_data_as_dataframe("users")
    
    def test_get_capabilities(self):
        """Test get_capabilities method."""
        capabilities = self.protocol.get_capabilities()
        self.assertIsInstance(capabilities, dict)
        self.assertTrue(capabilities.get("searchable"))
        self.assertIn("data_types", capabilities)
        self.assertIn("resources", capabilities.get("data_types"))


if __name__ == "__main__":
    unittest.main()