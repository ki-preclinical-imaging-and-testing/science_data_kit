"""
Tests for the base protocol class.

This module contains tests for the ConnectionProtocol class.
"""

import unittest
from typing import Any, Dict

from science_data_kit.core.connections.protocols.base import ConnectionProtocol


class MockConnectionProtocol(ConnectionProtocol):
    """Mock implementation of ConnectionProtocol for testing."""
    
    def __init__(self, connected=False):
        self._connected = connected
        self._config = {}
    
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
        return "mock"
    
    @property
    def is_connected(self) -> bool:
        """Check if the connection is currently established."""
        return self._connected
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this connection."""
        capabilities = super().get_capabilities()
        capabilities.update({
            "test_capability": True
        })
        return capabilities


class TestConnectionProtocol(unittest.TestCase):
    """Tests for the ConnectionProtocol class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.protocol = MockConnectionProtocol()
    
    def test_connect(self):
        """Test connect method."""
        config = {"param": "value"}
        self.protocol.connect(config)
        self.assertTrue(self.protocol.is_connected)
        self.assertEqual(self.protocol._config, config)
    
    def test_disconnect(self):
        """Test disconnect method."""
        self.protocol.connect({"param": "value"})
        self.assertTrue(self.protocol.is_connected)
        self.protocol.disconnect()
        self.assertFalse(self.protocol.is_connected)
    
    def test_test_connection(self):
        """Test test_connection method."""
        self.assertFalse(self.protocol.test_connection())
        self.protocol.connect({"param": "value"})
        self.assertTrue(self.protocol.test_connection())
    
    def test_connection_type(self):
        """Test connection_type property."""
        self.assertEqual(self.protocol.connection_type, "mock")
    
    def test_is_connected(self):
        """Test is_connected property."""
        self.assertFalse(self.protocol.is_connected)
        self.protocol.connect({"param": "value"})
        self.assertTrue(self.protocol.is_connected)
    
    def test_get_capabilities(self):
        """Test get_capabilities method."""
        capabilities = self.protocol.get_capabilities()
        self.assertIsInstance(capabilities, dict)
        self.assertTrue(capabilities.get("test_capability"))
    
    def test_get_metadata(self):
        """Test get_metadata method."""
        metadata = self.protocol.get_metadata()
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata.get("type"), "mock")
        self.assertIn("capabilities", metadata)
        self.assertIsInstance(metadata.get("capabilities"), dict)
        self.assertTrue(metadata.get("capabilities").get("test_capability"))


if __name__ == "__main__":
    unittest.main()