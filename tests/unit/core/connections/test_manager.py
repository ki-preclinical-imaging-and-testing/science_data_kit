"""
Unit tests for the connection manager.

This module contains tests for the connection manager functionality,
including basic connection management, connection pooling, error handling,
and integration with the plugin architecture.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
from typing import Dict, Any, Optional

from science_data_kit.core.connections.manager import (
    ConnectionManager,
    ConnectionPoolConfig,
    PooledConnection,
    ConnectionPool,
    manager,
)
from science_data_kit.core.connections.protocols.base import ConnectionProtocol
from science_data_kit.core.connections.registry import PluginCategory


class MockConnection(ConnectionProtocol):
    """Mock connection for testing."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.is_connected_value = False
        self.connect_called = False
        self.disconnect_called = False
        self.test_connection_called = False
        self.config = config or {}
        self.capabilities = {}
        
    def connect(self, config: Dict[str, Any]) -> None:
        """Connect to the service."""
        self.connect_called = True
        self.is_connected_value = True
        self.config = config
        
    def disconnect(self) -> None:
        """Disconnect from the service."""
        self.disconnect_called = True
        self.is_connected_value = False
        
    def test_connection(self) -> bool:
        """Test the connection."""
        self.test_connection_called = True
        return self.is_connected_value
        
    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.is_connected_value
        
    @property
    def connection_type(self) -> str:
        """Get the connection type."""
        return "mock"
        
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the connection capabilities."""
        return self.capabilities


class TestConnectionManager(unittest.TestCase):
    """Tests for the ConnectionManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry_mock = Mock()
        self.manager = ConnectionManager(registry=self.registry_mock)
        
    def test_create_connection(self):
        """Test creating a connection."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Create a connection
        config = {"key": "value"}
        connection = self.manager.create_connection("test", PluginCategory.API, "test_plugin", config)
        
        # Verify the connection was created
        self.assertEqual(connection, mock_connection)
        self.assertEqual(self.manager.get_connection("test"), mock_connection)
        self.assertEqual(self.manager.get_connection_config("test"), config)
        
        # Verify the registry was called correctly
        self.registry_mock.create_plugin.assert_called_once_with(PluginCategory.API, "test_plugin", config)
        
    def test_create_connection_with_string_type(self):
        """Test creating a connection with a string plugin type."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Create a connection
        config = {"key": "value"}
        connection = self.manager.create_connection("test", "api", "test_plugin", config)
        
        # Verify the connection was created
        self.assertEqual(connection, mock_connection)
        self.assertEqual(self.manager.get_connection("test"), mock_connection)
        self.assertEqual(self.manager.get_connection_config("test"), config)
        
        # Verify the registry was called correctly
        self.registry_mock.create_plugin.assert_called_once()
        
    def test_create_connection_duplicate_name(self):
        """Test creating a connection with a duplicate name."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Create a connection
        config = {"key": "value"}
        connection = self.manager.create_connection("test", PluginCategory.API, "test_plugin", config)
        
        # Try to create another connection with the same name
        connection2 = self.manager.create_connection("test", PluginCategory.API, "test_plugin", config)
        
        # Verify the second connection was not created
        self.assertIsNone(connection2)
        
    def test_create_connection_registry_failure(self):
        """Test creating a connection when the registry fails."""
        # Mock the registry to return None
        self.registry_mock.create_plugin.return_value = None
        
        # Create a connection
        config = {"key": "value"}
        connection = self.manager.create_connection("test", PluginCategory.API, "test_plugin", config)
        
        # Verify the connection was not created
        self.assertIsNone(connection)
        self.assertIsNone(self.manager.get_connection("test"))
        self.assertIsNone(self.manager.get_connection_config("test"))
        
    def test_connect(self):
        """Test connecting to a service."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Create a connection
        config = {"key": "value"}
        self.manager.create_connection("test", PluginCategory.API, "test_plugin", config)
        
        # Connect
        result = self.manager.connect("test")
        
        # Verify the connection was established
        self.assertTrue(result)
        self.assertTrue(mock_connection.connect_called)
        self.assertTrue(mock_connection.is_connected_value)
        self.assertEqual(mock_connection.config, config)
        
    def test_connect_nonexistent(self):
        """Test connecting to a nonexistent connection."""
        # Connect to a nonexistent connection
        result = self.manager.connect("nonexistent")
        
        # Verify the connection failed
        self.assertFalse(result)
        
    def test_connect_failure(self):
        """Test connecting when the connection fails."""
        # Mock the registry
        mock_connection = MockConnection()
        mock_connection.connect = Mock(side_effect=Exception("Connection failed"))
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Create a connection
        config = {"key": "value"}
        self.manager.create_connection("test", PluginCategory.API, "test_plugin", config)
        
        # Connect
        result = self.manager.connect("test")
        
        # Verify the connection failed
        self.assertFalse(result)
        
    def test_disconnect(self):
        """Test disconnecting from a service."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Create a connection
        config = {"key": "value"}
        self.manager.create_connection("test", PluginCategory.API, "test_plugin", config)
        
        # Connect
        self.manager.connect("test")
        
        # Disconnect
        result = self.manager.disconnect("test")
        
        # Verify the connection was disconnected
        self.assertTrue(result)
        self.assertTrue(mock_connection.disconnect_called)
        self.assertFalse(mock_connection.is_connected_value)
        
    def test_disconnect_nonexistent(self):
        """Test disconnecting from a nonexistent connection."""
        # Disconnect from a nonexistent connection
        result = self.manager.disconnect("nonexistent")
        
        # Verify the disconnection failed
        self.assertFalse(result)
        
    def test_disconnect_failure(self):
        """Test disconnecting when the connection fails."""
        # Mock the registry
        mock_connection = MockConnection()
        mock_connection.disconnect = Mock(side_effect=Exception("Disconnection failed"))
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Create a connection
        config = {"key": "value"}
        self.manager.create_connection("test", PluginCategory.API, "test_plugin", config)
        
        # Connect
        self.manager.connect("test")
        
        # Disconnect
        result = self.manager.disconnect("test")
        
        # Verify the disconnection failed
        self.assertFalse(result)
        
    def test_remove_connection(self):
        """Test removing a connection."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Create a connection
        config = {"key": "value"}
        self.manager.create_connection("test", PluginCategory.API, "test_plugin", config)
        
        # Remove the connection
        result = self.manager.remove_connection("test")
        
        # Verify the connection was removed
        self.assertTrue(result)
        self.assertIsNone(self.manager.get_connection("test"))
        self.assertIsNone(self.manager.get_connection_config("test"))
        
    def test_remove_connection_nonexistent(self):
        """Test removing a nonexistent connection."""
        # Remove a nonexistent connection
        result = self.manager.remove_connection("nonexistent")
        
        # Verify the removal failed
        self.assertFalse(result)
        
    def test_list_connections(self):
        """Test listing connections."""
        # Mock the registry
        mock_connection1 = MockConnection()
        mock_connection1.connection_type = "api"
        mock_connection1.is_connected_value = True
        mock_connection1.capabilities = {"search": True, "browse": False}
        
        mock_connection2 = MockConnection()
        mock_connection2.connection_type = "filesystem"
        mock_connection2.is_connected_value = False
        mock_connection2.capabilities = {"read": True, "write": True}
        
        self.registry_mock.create_plugin.side_effect = [mock_connection1, mock_connection2]
        
        # Create connections
        self.manager.create_connection("test1", PluginCategory.API, "test_plugin1", {})
        self.manager.create_connection("test2", PluginCategory.FILESYSTEM, "test_plugin2", {})
        
        # List connections
        connections = self.manager.list_connections()
        
        # Verify the connections were listed
        self.assertEqual(len(connections), 2)
        self.assertEqual(connections[0]["name"], "test1")
        self.assertEqual(connections[0]["type"], "api")
        self.assertTrue(connections[0]["connected"])
        self.assertEqual(connections[0]["capabilities"], {"search": True, "browse": False})
        self.assertEqual(connections[1]["name"], "test2")
        self.assertEqual(connections[1]["type"], "filesystem")
        self.assertFalse(connections[1]["connected"])
        self.assertEqual(connections[1]["capabilities"], {"read": True, "write": True})
        
    def test_get_connection_by_capability(self):
        """Test getting connections by capability."""
        # Mock the registry
        mock_connection1 = MockConnection()
        mock_connection1.capabilities = {"search": True, "browse": False}
        
        mock_connection2 = MockConnection()
        mock_connection2.capabilities = {"read": True, "write": True}
        
        self.registry_mock.create_plugin.side_effect = [mock_connection1, mock_connection2]
        
        # Create connections
        self.manager.create_connection("test1", PluginCategory.API, "test_plugin1", {})
        self.manager.create_connection("test2", PluginCategory.FILESYSTEM, "test_plugin2", {})
        
        # Get connections by capability
        search_connections = self.manager.get_connection_by_capability("search")
        read_connections = self.manager.get_connection_by_capability("read")
        write_connections = self.manager.get_connection_by_capability("write")
        nonexistent_connections = self.manager.get_connection_by_capability("nonexistent")
        
        # Verify the connections were found
        self.assertEqual(search_connections, ["test1"])
        self.assertEqual(read_connections, ["test2"])
        self.assertEqual(write_connections, ["test2"])
        self.assertEqual(nonexistent_connections, [])
        
    def test_disconnect_all(self):
        """Test disconnecting all connections."""
        # Mock the registry
        mock_connection1 = MockConnection()
        mock_connection2 = MockConnection()
        self.registry_mock.create_plugin.side_effect = [mock_connection1, mock_connection2]
        
        # Create connections
        self.manager.create_connection("test1", PluginCategory.API, "test_plugin1", {})
        self.manager.create_connection("test2", PluginCategory.FILESYSTEM, "test_plugin2", {})
        
        # Connect
        self.manager.connect("test1")
        self.manager.connect("test2")
        
        # Disconnect all
        self.manager.disconnect_all()
        
        # Verify all connections were disconnected
        self.assertTrue(mock_connection1.disconnect_called)
        self.assertTrue(mock_connection2.disconnect_called)
        self.assertFalse(mock_connection1.is_connected_value)
        self.assertFalse(mock_connection2.is_connected_value)


class TestConnectionPool(unittest.TestCase):
    """Tests for the ConnectionPool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager_mock = Mock()
        self.plugin_type = PluginCategory.API
        self.plugin_name = "test_plugin"
        self.config = {"key": "value"}
        self.pool_config = ConnectionPoolConfig(
            max_pool_size=5,
            min_idle=1,
            max_idle=3,
            idle_timeout=60.0,
            max_lifetime=300.0,
            connection_timeout=1.0,
            validation_interval=30.0,
        )
        
    def test_initialize_pool(self):
        """Test initializing a connection pool."""
        # Mock the manager
        mock_connection = MockConnection()
        self.manager_mock._create_plugin_instance.return_value = mock_connection
        
        # Create a pool
        pool = ConnectionPool(
            self.manager_mock,
            self.plugin_type,
            self.plugin_name,
            self.config,
            self.pool_config,
        )
        
        # Verify the pool was initialized
        self.assertEqual(len(pool._idle_connections), 1)
        self.assertEqual(len(pool._active_connections), 0)
        self.assertEqual(pool._idle_connections[0].connection, mock_connection)
        self.assertEqual(pool._idle_connections[0].config, self.config)
        self.assertFalse(pool._idle_connections[0].in_use)
        
    def test_get_connection(self):
        """Test getting a connection from the pool."""
        # Mock the manager
        mock_connection = MockConnection()
        self.manager_mock._create_plugin_instance.return_value = mock_connection
        
        # Create a pool
        pool = ConnectionPool(
            self.manager_mock,
            self.plugin_type,
            self.plugin_name,
            self.config,
            self.pool_config,
        )
        
        # Get a connection
        connection = pool.get_connection()
        
        # Verify the connection was returned
        self.assertIsNotNone(connection)
        self.assertEqual(connection.connection, mock_connection)
        self.assertEqual(connection.config, self.config)
        self.assertTrue(connection.in_use)
        self.assertEqual(len(pool._idle_connections), 0)
        self.assertEqual(len(pool._active_connections), 1)
        
    def test_return_connection(self):
        """Test returning a connection to the pool."""
        # Mock the manager
        mock_connection = MockConnection()
        self.manager_mock._create_plugin_instance.return_value = mock_connection
        
        # Create a pool
        pool = ConnectionPool(
            self.manager_mock,
            self.plugin_type,
            self.plugin_name,
            self.config,
            self.pool_config,
        )
        
        # Get a connection
        connection = pool.get_connection()
        
        # Return the connection
        pool.return_connection(connection)
        
        # Verify the connection was returned
        self.assertFalse(connection.in_use)
        self.assertEqual(len(pool._idle_connections), 1)
        self.assertEqual(len(pool._active_connections), 0)
        self.assertEqual(pool._idle_connections[0], connection)
        
    def test_validate_connections_if_needed(self):
        """Test validating connections."""
        # Mock the manager
        mock_connection = MockConnection()
        self.manager_mock._create_plugin_instance.return_value = mock_connection
        
        # Create a pool with a short validation interval
        pool_config = ConnectionPoolConfig(
            max_pool_size=5,
            min_idle=1,
            max_idle=3,
            idle_timeout=60.0,
            max_lifetime=300.0,
            connection_timeout=1.0,
            validation_interval=0.1,  # Short interval for testing
        )
        
        pool = ConnectionPool(
            self.manager_mock,
            self.plugin_type,
            self.plugin_name,
            self.config,
            pool_config,
        )
        
        # Get a connection
        connection = pool.get_connection()
        
        # Return the connection
        pool.return_connection(connection)
        
        # Wait for the validation interval to pass
        time.sleep(0.2)
        
        # Trigger validation
        pool._validate_connections_if_needed()
        
        # Verify the connection was validated
        self.assertTrue(mock_connection.test_connection_called)
        
    def test_close(self):
        """Test closing a connection pool."""
        # Mock the manager
        mock_connection1 = MockConnection()
        mock_connection2 = MockConnection()
        self.manager_mock._create_plugin_instance.side_effect = [mock_connection1, mock_connection2]
        
        # Create a pool
        pool = ConnectionPool(
            self.manager_mock,
            self.plugin_type,
            self.plugin_name,
            self.config,
            self.pool_config,
        )
        
        # Get a connection
        connection1 = pool.get_connection()
        
        # Create another connection
        connection2 = pool.get_connection()
        
        # Return one connection
        pool.return_connection(connection1)
        
        # Close the pool
        pool.close()
        
        # Verify all connections were closed
        self.assertTrue(mock_connection1.disconnect_called)
        self.assertTrue(mock_connection2.disconnect_called)
        self.assertEqual(len(pool._idle_connections), 0)
        self.assertEqual(len(pool._active_connections), 0)
        
    def test_get_stats(self):
        """Test getting pool statistics."""
        # Mock the manager
        mock_connection = MockConnection()
        self.manager_mock._create_plugin_instance.return_value = mock_connection
        
        # Create a pool
        pool = ConnectionPool(
            self.manager_mock,
            self.plugin_type,
            self.plugin_name,
            self.config,
            self.pool_config,
        )
        
        # Get stats
        stats = pool.get_stats()
        
        # Verify the stats
        self.assertEqual(stats["idle_connections"], 1)
        self.assertEqual(stats["active_connections"], 0)
        self.assertEqual(stats["max_pool_size"], 5)
        self.assertEqual(stats["min_idle"], 1)
        self.assertEqual(stats["max_idle"], 3)


class TestConnectionPooling(unittest.TestCase):
    """Tests for connection pooling in the ConnectionManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry_mock = Mock()
        self.manager = ConnectionManager(registry=self.registry_mock)
        self.plugin_type = PluginCategory.API
        self.plugin_name = "test_plugin"
        self.config = {"key": "value"}
        self.pool_config = ConnectionPoolConfig(
            max_pool_size=5,
            min_idle=1,
            max_idle=3,
            idle_timeout=60.0,
            max_lifetime=300.0,
            connection_timeout=1.0,
            validation_interval=30.0,
        )
        
    def test_configure_pool(self):
        """Test configuring a connection pool."""
        # Configure a pool
        self.manager.configure_pool(self.plugin_type, self.plugin_name, self.pool_config)
        
        # Verify the pool configuration was stored
        key = (self.plugin_type.value, self.plugin_name)
        self.assertEqual(self.manager._pool_configs[key], self.pool_config)
        
    def test_configure_pool_with_string_type(self):
        """Test configuring a connection pool with a string plugin type."""
        # Configure a pool
        self.manager.configure_pool("api", self.plugin_name, self.pool_config)
        
        # Verify the pool configuration was stored
        key = ("api", self.plugin_name)
        self.assertEqual(self.manager._pool_configs[key], self.pool_config)
        
    def test_get_pooled_connection(self):
        """Test getting a connection from a pool."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Get a pooled connection
        connection = self.manager.get_pooled_connection(self.plugin_type, self.plugin_name, self.config)
        
        # Verify the connection was returned
        self.assertEqual(connection, mock_connection)
        
        # Verify the pool was created
        key = (self.plugin_type.value, self.plugin_name)
        self.assertIn(key, self.manager._pools)
        
    def test_get_pooled_connection_with_string_type(self):
        """Test getting a connection from a pool with a string plugin type."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Get a pooled connection
        connection = self.manager.get_pooled_connection("api", self.plugin_name, self.config)
        
        # Verify the connection was returned
        self.assertEqual(connection, mock_connection)
        
        # Verify the pool was created
        key = ("api", self.plugin_name)
        self.assertIn(key, self.manager._pools)
        
    def test_return_pooled_connection(self):
        """Test returning a connection to a pool."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Get a pooled connection
        connection = self.manager.get_pooled_connection(self.plugin_type, self.plugin_name, self.config)
        
        # Return the connection
        self.manager.return_pooled_connection(self.plugin_type, self.plugin_name, connection)
        
        # Verify the connection was returned to the pool
        key = (self.plugin_type.value, self.plugin_name)
        pool = self.manager._pools[key]
        self.assertEqual(len(pool._idle_connections), 1)
        self.assertEqual(len(pool._active_connections), 0)
        
    def test_return_pooled_connection_with_string_type(self):
        """Test returning a connection to a pool with a string plugin type."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Get a pooled connection
        connection = self.manager.get_pooled_connection("api", self.plugin_name, self.config)
        
        # Return the connection
        self.manager.return_pooled_connection("api", self.plugin_name, connection)
        
        # Verify the connection was returned to the pool
        key = ("api", self.plugin_name)
        pool = self.manager._pools[key]
        self.assertEqual(len(pool._idle_connections), 1)
        self.assertEqual(len(pool._active_connections), 0)
        
    def test_get_pool_stats(self):
        """Test getting pool statistics."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Configure a pool
        self.manager.configure_pool(self.plugin_type, self.plugin_name, self.pool_config)
        
        # Get a pooled connection
        connection = self.manager.get_pooled_connection(self.plugin_type, self.plugin_name, self.config)
        
        # Get pool stats
        stats = self.manager.get_pool_stats(self.plugin_type, self.plugin_name)
        
        # Verify the stats
        self.assertEqual(stats["idle_connections"], 0)
        self.assertEqual(stats["active_connections"], 1)
        self.assertEqual(stats["max_pool_size"], 5)
        self.assertEqual(stats["min_idle"], 1)
        self.assertEqual(stats["max_idle"], 3)
        
    def test_get_pool_stats_with_string_type(self):
        """Test getting pool statistics with a string plugin type."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Configure a pool
        self.manager.configure_pool("api", self.plugin_name, self.pool_config)
        
        # Get a pooled connection
        connection = self.manager.get_pooled_connection("api", self.plugin_name, self.config)
        
        # Get pool stats
        stats = self.manager.get_pool_stats("api", self.plugin_name)
        
        # Verify the stats
        self.assertEqual(stats["idle_connections"], 0)
        self.assertEqual(stats["active_connections"], 1)
        self.assertEqual(stats["max_pool_size"], 5)
        self.assertEqual(stats["min_idle"], 1)
        self.assertEqual(stats["max_idle"], 3)
        
    def test_close_pool(self):
        """Test closing a connection pool."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Get a pooled connection
        connection = self.manager.get_pooled_connection(self.plugin_type, self.plugin_name, self.config)
        
        # Close the pool
        self.manager.close_pool(self.plugin_type, self.plugin_name)
        
        # Verify the pool was closed
        key = (self.plugin_type.value, self.plugin_name)
        self.assertNotIn(key, self.manager._pools)
        
    def test_close_pool_with_string_type(self):
        """Test closing a connection pool with a string plugin type."""
        # Mock the registry
        mock_connection = MockConnection()
        self.registry_mock.create_plugin.return_value = mock_connection
        
        # Get a pooled connection
        connection = self.manager.get_pooled_connection("api", self.plugin_name, self.config)
        
        # Close the pool
        self.manager.close_pool("api", self.plugin_name)
        
        # Verify the pool was closed
        key = ("api", self.plugin_name)
        self.assertNotIn(key, self.manager._pools)


if __name__ == "__main__":
    unittest.main()