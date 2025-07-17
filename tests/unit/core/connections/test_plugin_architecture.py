"""
Unit tests for the plugin architecture.

This module contains tests for the plugin architecture components,
including protocols, capabilities, and the connection manager.
"""

import unittest
from unittest.mock import MagicMock, patch

from science_data_kit.core.connections.protocols.base import ConnectionProtocol
from science_data_kit.core.connections.capabilities.browsable import Browsable
from science_data_kit.core.connections.capabilities.searchable import Searchable
from science_data_kit.core.connections.auth.oauth2 import OAuth2Mixin
from science_data_kit.core.connections.registry import PluginCategory, PluginRegistry
from science_data_kit.core.connections.manager import ConnectionManager


class TestConnectionProtocol(unittest.TestCase):
    """Tests for the ConnectionProtocol class."""
    
    def test_connection_protocol_interface(self):
        """Test that ConnectionProtocol defines the expected interface."""
        # Check that ConnectionProtocol has the expected abstract methods
        self.assertTrue(hasattr(ConnectionProtocol, 'connect'))
        self.assertTrue(hasattr(ConnectionProtocol, 'disconnect'))
        self.assertTrue(hasattr(ConnectionProtocol, 'test_connection'))
        self.assertTrue(hasattr(ConnectionProtocol, 'connection_type'))
        
        # Check that ConnectionProtocol has the expected non-abstract methods
        self.assertTrue(hasattr(ConnectionProtocol, 'is_connected'))
        self.assertTrue(hasattr(ConnectionProtocol, 'get_capabilities'))
        self.assertTrue(hasattr(ConnectionProtocol, 'get_metadata'))


class TestCapabilities(unittest.TestCase):
    """Tests for the capability mixins."""
    
    def test_browsable_interface(self):
        """Test that Browsable defines the expected interface."""
        # Check that Browsable has the expected abstract methods
        self.assertTrue(hasattr(Browsable, 'list_contents'))
        self.assertTrue(hasattr(Browsable, 'get_metadata'))
        
        # Check that Browsable has the expected non-abstract methods
        self.assertTrue(hasattr(Browsable, 'is_directory'))
        self.assertTrue(hasattr(Browsable, 'is_file'))
        self.assertTrue(hasattr(Browsable, 'get_parent_path'))
    
    def test_searchable_interface(self):
        """Test that Searchable defines the expected interface."""
        # Check that Searchable has the expected abstract methods
        self.assertTrue(hasattr(Searchable, 'search'))
        
        # Check that Searchable has the expected non-abstract methods
        self.assertTrue(hasattr(Searchable, 'search_by_name'))
        self.assertTrue(hasattr(Searchable, 'search_by_content'))
        self.assertTrue(hasattr(Searchable, 'search_by_type'))
        self.assertTrue(hasattr(Searchable, 'search_by_date'))


class TestAuth(unittest.TestCase):
    """Tests for the authentication mixins."""
    
    def test_oauth2_interface(self):
        """Test that OAuth2Mixin defines the expected interface."""
        # Check that OAuth2Mixin has the expected abstract methods
        self.assertTrue(hasattr(OAuth2Mixin, 'get_auth_url'))
        self.assertTrue(hasattr(OAuth2Mixin, 'exchange_code_for_token'))
        self.assertTrue(hasattr(OAuth2Mixin, 'refresh_token'))
        
        # Check that OAuth2Mixin has the expected non-abstract methods
        self.assertTrue(hasattr(OAuth2Mixin, 'get_valid_token'))
        self.assertTrue(hasattr(OAuth2Mixin, 'is_authenticated'))


class TestPluginRegistry(unittest.TestCase):
    """Tests for the PluginRegistry class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = PluginRegistry()
    
    def test_plugin_registration(self):
        """Test plugin registration and retrieval."""
        # Create a mock plugin class
        mock_plugin_class = MagicMock(spec=ConnectionProtocol)
        mock_plugin_class.connection_type = "filesystem"
        
        # Register the plugin
        self.registry.register_plugin(PluginCategory.FILESYSTEM, "MockPlugin", mock_plugin_class)
        
        # Check that the plugin was registered
        self.assertIn("MockPlugin", self.registry.get_plugin_names(PluginCategory.FILESYSTEM))
        
        # Get the plugin class
        retrieved_class = self.registry.get_plugin_class(PluginCategory.FILESYSTEM, "MockPlugin")
        self.assertEqual(retrieved_class, mock_plugin_class)
        
        # Unregister the plugin
        result = self.registry.unregister_plugin(PluginCategory.FILESYSTEM, "MockPlugin")
        self.assertTrue(result)
        
        # Check that the plugin was unregistered
        self.assertNotIn("MockPlugin", self.registry.get_plugin_names(PluginCategory.FILESYSTEM))


class TestConnectionManager(unittest.TestCase):
    """Tests for the ConnectionManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = PluginRegistry()
        self.manager = ConnectionManager(self.registry)
    
    def test_connection_lifecycle(self):
        """Test connection creation, connection, and disconnection."""
        # Create a mock plugin class
        mock_plugin_class = MagicMock(spec=ConnectionProtocol)
        mock_plugin_class.connection_type = "filesystem"
        
        # Create a mock plugin instance
        mock_plugin = MagicMock(spec=ConnectionProtocol)
        mock_plugin.connection_type = "filesystem"
        mock_plugin.is_connected = False
        mock_plugin.get_capabilities.return_value = {"browsable": True}
        
        # Mock the create_plugin method to return our mock plugin
        self.registry.create_plugin = MagicMock(return_value=mock_plugin)
        
        # Create a connection
        connection = self.manager.create_connection(
            "test_connection",
            PluginCategory.FILESYSTEM,
            "MockPlugin",
            {"param": "value"}
        )
        
        # Check that the connection was created
        self.assertEqual(connection, mock_plugin)
        
        # Connect
        mock_plugin.connect = MagicMock()
        result = self.manager.connect("test_connection")
        self.assertTrue(result)
        mock_plugin.connect.assert_called_once()
        
        # Disconnect
        mock_plugin.disconnect = MagicMock()
        result = self.manager.disconnect("test_connection")
        self.assertTrue(result)
        mock_plugin.disconnect.assert_called_once()
        
        # Remove connection
        result = self.manager.remove_connection("test_connection")
        self.assertTrue(result)
        
        # Check that the connection was removed
        self.assertIsNone(self.manager.get_connection("test_connection"))


if __name__ == '__main__':
    unittest.main()