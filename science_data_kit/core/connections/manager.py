"""
Connection manager for Science Data Kit.

This module provides a central manager for all connections in the Science Data Kit,
allowing for unified connection management, lifecycle control, and connection pooling.
"""

import logging
import time
import threading
from typing import Any, Dict, List, Optional, Type, Union, cast, Tuple, Set
from collections import defaultdict, deque

from .protocols.base import ConnectionProtocol
from .registry import PluginCategory, PluginRegistry, registry

# Set up logging
logger = logging.getLogger(__name__)


class ConnectionPoolConfig:
    """Configuration for connection pooling."""

    def __init__(
        self,
        max_pool_size: int = 10,
        min_idle: int = 1,
        max_idle: int = 5,
        idle_timeout: float = 300.0,  # 5 minutes
        max_lifetime: float = 3600.0,  # 1 hour
        connection_timeout: float = 30.0,
        validation_interval: float = 60.0,  # 1 minute
    ):
        """
        Initialize connection pool configuration.

        Args:
            max_pool_size: Maximum number of connections in the pool
            min_idle: Minimum number of idle connections to maintain
            max_idle: Maximum number of idle connections to keep
            idle_timeout: Time in seconds after which idle connections are closed
            max_lifetime: Maximum lifetime of a connection in seconds
            connection_timeout: Timeout in seconds for connection acquisition
            validation_interval: Interval in seconds for validating connections
        """
        self.max_pool_size = max_pool_size
        self.min_idle = min_idle
        self.max_idle = max_idle
        self.idle_timeout = idle_timeout
        self.max_lifetime = max_lifetime
        self.connection_timeout = connection_timeout
        self.validation_interval = validation_interval


class PooledConnection:
    """A connection in the connection pool."""

    def __init__(self, connection: ConnectionProtocol, config: Dict[str, Any]):
        """
        Initialize a pooled connection.

        Args:
            connection: The connection instance
            config: The connection configuration
        """
        self.connection = connection
        self.config = config
        self.created_at = time.time()
        self.last_used_at = time.time()
        self.in_use = False

    def is_expired(self, max_lifetime: float) -> bool:
        """
        Check if the connection has exceeded its maximum lifetime.

        Args:
            max_lifetime: Maximum lifetime in seconds

        Returns:
            True if the connection has expired, False otherwise
        """
        return (time.time() - self.created_at) > max_lifetime

    def is_idle_timeout(self, idle_timeout: float) -> bool:
        """
        Check if the connection has been idle for too long.

        Args:
            idle_timeout: Idle timeout in seconds

        Returns:
            True if the connection has been idle for too long, False otherwise
        """
        return not self.in_use and (time.time() - self.last_used_at) > idle_timeout

    def validate(self) -> bool:
        """
        Validate that the connection is still valid.

        Returns:
            True if the connection is valid, False otherwise
        """
        try:
            return self.connection.test_connection()
        except Exception:
            return False


class ConnectionPool:
    """
    A pool of connections for a specific plugin type and name.

    This class manages a pool of connections for a specific plugin type and name,
    allowing for connection reuse and lifecycle management.
    """

    def __init__(
        self,
        manager: 'ConnectionManager',
        plugin_type: Union[str, PluginCategory],
        plugin_name: str,
        config: Dict[str, Any],
        pool_config: ConnectionPoolConfig
    ):
        """
        Initialize the connection pool.

        Args:
            manager: The connection manager
            plugin_type: Type of the plugin
            plugin_name: Name of the plugin
            config: Configuration for the connections
            pool_config: Configuration for the pool
        """
        self._manager = manager
        self._plugin_type = plugin_type
        self._plugin_name = plugin_name
        self._config = config
        self._pool_config = pool_config

        self._idle_connections: deque[PooledConnection] = deque()
        self._active_connections: Set[PooledConnection] = set()
        self._lock = threading.RLock()

        self._last_validation = time.time()

        # Initialize the pool with min_idle connections
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """Initialize the pool with min_idle connections."""
        with self._lock:
            for _ in range(self._pool_config.min_idle):
                connection = self._create_connection()
                if connection:
                    self._idle_connections.append(connection)

    def _create_connection(self) -> Optional[PooledConnection]:
        """
        Create a new connection.

        Returns:
            A new pooled connection if successful, None otherwise
        """
        try:
            connection = self._manager._create_plugin_instance(
                self._plugin_type, self._plugin_name, self._config
            )
            if connection:
                return PooledConnection(connection, self._config.copy())
            return None
        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            return None

    def get_connection(self) -> Optional[PooledConnection]:
        """
        Get a connection from the pool.

        Returns:
            A pooled connection if available, None otherwise
        """
        # Validate connections if needed
        self._validate_connections_if_needed()

        with self._lock:
            # Try to get an idle connection
            while self._idle_connections:
                connection = self._idle_connections.popleft()

                # Check if the connection is still valid
                if connection.is_expired(self._pool_config.max_lifetime) or not connection.validate():
                    # Connection is expired or invalid, discard it
                    continue

                # Mark the connection as in use
                connection.in_use = True
                connection.last_used_at = time.time()
                self._active_connections.add(connection)
                return connection

            # No idle connections available, create a new one if possible
            if len(self._active_connections) < self._pool_config.max_pool_size:
                connection = self._create_connection()
                if connection:
                    connection.in_use = True
                    self._active_connections.add(connection)
                    return connection

            # Pool is full, wait for a connection to become available
            start_time = time.time()
            while time.time() - start_time < self._pool_config.connection_timeout:
                # Release the lock while waiting
                self._lock.release()
                try:
                    time.sleep(0.1)
                finally:
                    self._lock.acquire()

                # Try again to get an idle connection
                if self._idle_connections:
                    connection = self._idle_connections.popleft()
                    if connection.is_expired(self._pool_config.max_lifetime) or not connection.validate():
                        continue

                    connection.in_use = True
                    connection.last_used_at = time.time()
                    self._active_connections.add(connection)
                    return connection

            # Timeout waiting for a connection
            logger.error("Timeout waiting for a connection from the pool")
            return None

    def return_connection(self, connection: PooledConnection) -> None:
        """
        Return a connection to the pool.

        Args:
            connection: The connection to return
        """
        with self._lock:
            if connection in self._active_connections:
                self._active_connections.remove(connection)

                # Check if the connection is still valid
                if (not connection.is_expired(self._pool_config.max_lifetime) and 
                    connection.validate() and 
                    len(self._idle_connections) < self._pool_config.max_idle):
                    # Return the connection to the idle pool
                    connection.in_use = False
                    connection.last_used_at = time.time()
                    self._idle_connections.append(connection)
                else:
                    # Connection is expired or invalid, or we have too many idle connections
                    # Discard it
                    try:
                        connection.connection.disconnect()
                    except Exception:
                        pass

    def _validate_connections_if_needed(self) -> None:
        """Validate connections if the validation interval has passed."""
        current_time = time.time()
        if current_time - self._last_validation > self._pool_config.validation_interval:
            with self._lock:
                self._last_validation = current_time

                # Validate idle connections
                valid_connections = deque()
                while self._idle_connections:
                    connection = self._idle_connections.popleft()

                    # Check if the connection is still valid
                    if (connection.is_expired(self._pool_config.max_lifetime) or 
                        connection.is_idle_timeout(self._pool_config.idle_timeout) or 
                        not connection.validate()):
                        # Connection is expired, idle timeout, or invalid, discard it
                        try:
                            connection.connection.disconnect()
                        except Exception:
                            pass
                    else:
                        # Connection is still valid
                        valid_connections.append(connection)

                # Update the idle connections
                self._idle_connections = valid_connections

                # Ensure we have at least min_idle connections
                while len(self._idle_connections) < self._pool_config.min_idle:
                    connection = self._create_connection()
                    if connection:
                        self._idle_connections.append(connection)
                    else:
                        break

    def close(self) -> None:
        """Close all connections in the pool."""
        with self._lock:
            # Close idle connections
            while self._idle_connections:
                connection = self._idle_connections.popleft()
                try:
                    connection.connection.disconnect()
                except Exception:
                    pass

            # Close active connections
            for connection in list(self._active_connections):
                try:
                    connection.connection.disconnect()
                except Exception:
                    pass

            self._active_connections.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the connection pool.

        Returns:
            Dictionary containing pool statistics
        """
        with self._lock:
            return {
                "idle_connections": len(self._idle_connections),
                "active_connections": len(self._active_connections),
                "max_pool_size": self._pool_config.max_pool_size,
                "min_idle": self._pool_config.min_idle,
                "max_idle": self._pool_config.max_idle,
            }


class ConnectionManager:
    """
    Central manager for all connections.

    This class provides a high-level interface for managing connections,
    including creation, configuration, lifecycle management, and connection pooling.
    """

    def __init__(self, registry: Optional[PluginRegistry] = None):
        """
        Initialize the connection manager.

        Args:
            registry: Plugin registry to use (optional, uses global registry by default)
        """
        self._registry = registry or registry
        self._connections: Dict[str, ConnectionProtocol] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}

        # Connection pooling
        self._pools: Dict[Tuple[str, str], ConnectionPool] = {}
        self._pool_configs: Dict[Tuple[str, str], ConnectionPoolConfig] = {}
        self._default_pool_config = ConnectionPoolConfig()

    def _create_plugin_instance(self, plugin_type: Union[str, PluginCategory],
                              plugin_name: str, config: Dict[str, Any]) -> Optional[ConnectionProtocol]:
        """
        Create a plugin instance.

        Args:
            plugin_type: Type of the plugin (can be string or PluginCategory)
            plugin_name: Name of the plugin
            config: Configuration for the plugin

        Returns:
            Plugin instance if created successfully, None otherwise
        """
        # Convert string plugin type to enum if necessary
        if isinstance(plugin_type, str):
            try:
                plugin_type = next(pt for pt in PluginCategory if pt.value == plugin_type)
            except StopIteration:
                logger.error(f"Invalid plugin type: {plugin_type}")
                return None

        # Create plugin instance
        plugin = self._registry.create_plugin(plugin_type, plugin_name, config)
        if plugin is None:
            logger.error(f"Failed to create plugin: {plugin_name} ({plugin_type})")
            return None

        return plugin

    def create_connection(self, name: str, plugin_type: Union[str, PluginCategory], 
                         plugin_name: str, config: Dict[str, Any]) -> Optional[ConnectionProtocol]:
        """
        Create and register a new connection.

        Args:
            name: Name for the connection
            plugin_type: Type of the plugin (can be string or PluginCategory)
            plugin_name: Name of the plugin
            config: Configuration for the connection

        Returns:
            Connection instance if created successfully, None otherwise
        """
        # Check if connection with this name already exists
        if name in self._connections:
            logger.warning(f"Connection with name '{name}' already exists")
            return None

        # Create plugin instance
        plugin = self._create_plugin_instance(plugin_type, plugin_name, config)
        if plugin is None:
            return None

        # Store connection and config
        self._connections[name] = plugin
        self._configs[name] = config

        logger.info(f"Created connection: {name} using {plugin_name} ({plugin_type})")
        return plugin

    def get_connection(self, name: str) -> Optional[ConnectionProtocol]:
        """
        Get a connection by name.

        Args:
            name: Name of the connection

        Returns:
            Connection instance if found, None otherwise
        """
        return self._connections.get(name)

    def get_connection_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a connection.

        Args:
            name: Name of the connection

        Returns:
            Configuration dictionary if found, None otherwise
        """
        return self._configs.get(name)

    def connect(self, name: str) -> bool:
        """
        Establish a connection.

        Args:
            name: Name of the connection

        Returns:
            True if connection was established, False otherwise
        """
        connection = self.get_connection(name)
        if connection is None:
            logger.warning(f"Connection not found: {name}")
            return False

        config = self.get_connection_config(name)
        if config is None:
            logger.warning(f"Configuration not found for connection: {name}")
            return False

        try:
            connection.connect(config)
            logger.info(f"Connected: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {name}: {e}")
            return False

    def disconnect(self, name: str) -> bool:
        """
        Disconnect a connection.

        Args:
            name: Name of the connection

        Returns:
            True if disconnection was successful, False otherwise
        """
        connection = self.get_connection(name)
        if connection is None:
            logger.warning(f"Connection not found: {name}")
            return False

        try:
            connection.disconnect()
            logger.info(f"Disconnected: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect: {name}: {e}")
            return False

    def remove_connection(self, name: str) -> bool:
        """
        Remove a connection from the manager.

        Args:
            name: Name of the connection

        Returns:
            True if removal was successful, False otherwise
        """
        if name not in self._connections:
            logger.warning(f"Connection not found: {name}")
            return False

        # Try to disconnect first
        try:
            self.disconnect(name)
        except Exception:
            pass

        # Remove connection and config
        del self._connections[name]
        if name in self._configs:
            del self._configs[name]

        logger.info(f"Removed connection: {name}")
        return True

    def list_connections(self) -> List[Dict[str, Any]]:
        """
        List all connections.

        Returns:
            List of dictionaries containing connection information
        """
        result = []
        for name, connection in self._connections.items():
            result.append({
                "name": name,
                "type": connection.connection_type,
                "connected": connection.is_connected,
                "capabilities": connection.get_capabilities(),
            })
        return result

    def get_connection_by_capability(self, capability: str) -> List[str]:
        """
        Get connections that have a specific capability.

        Args:
            capability: Capability to look for

        Returns:
            List of connection names
        """
        result = []
        for name, connection in self._connections.items():
            capabilities = connection.get_capabilities()
            if capability in capabilities or capabilities.get(capability, False):
                result.append(name)
        return result

    def disconnect_all(self) -> None:
        """Disconnect all connections."""
        for name in list(self._connections.keys()):
            try:
                self.disconnect(name)
            except Exception as e:
                logger.error(f"Failed to disconnect {name}: {e}")

        # Close all connection pools
        for pool in list(self._pools.values()):
            try:
                pool.close()
            except Exception as e:
                logger.error(f"Failed to close connection pool: {e}")

        self._pools.clear()

    # Connection pooling methods

    def configure_pool(self, plugin_type: Union[str, PluginCategory], plugin_name: str,
                      pool_config: ConnectionPoolConfig) -> None:
        """
        Configure a connection pool for a specific plugin type and name.

        Args:
            plugin_type: Type of the plugin
            plugin_name: Name of the plugin
            pool_config: Configuration for the pool
        """
        # Convert string plugin type to enum if necessary
        if isinstance(plugin_type, str):
            try:
                plugin_type = next(pt for pt in PluginCategory if pt.value == plugin_type)
            except StopIteration:
                logger.error(f"Invalid plugin type: {plugin_type}")
                return

        # Store the pool configuration
        key = (plugin_type.value, plugin_name)
        self._pool_configs[key] = pool_config

        # Update existing pool if it exists
        if key in self._pools:
            # Close the existing pool
            self._pools[key].close()
            # Create a new pool with the updated configuration
            self._pools[key] = ConnectionPool(
                self, plugin_type, plugin_name, 
                self._pools[key]._config, pool_config
            )

    def get_pooled_connection(self, plugin_type: Union[str, PluginCategory], plugin_name: str,
                             config: Dict[str, Any]) -> Optional[ConnectionProtocol]:
        """
        Get a connection from a pool.

        Args:
            plugin_type: Type of the plugin
            plugin_name: Name of the plugin
            config: Configuration for the connection

        Returns:
            Connection instance if available, None otherwise
        """
        # Convert string plugin type to enum if necessary
        if isinstance(plugin_type, str):
            try:
                plugin_type = next(pt for pt in PluginCategory if pt.value == plugin_type)
            except StopIteration:
                logger.error(f"Invalid plugin type: {plugin_type}")
                return None

        # Get or create the pool
        key = (plugin_type.value, plugin_name)
        if key not in self._pools:
            # Get the pool configuration
            pool_config = self._pool_configs.get(key, self._default_pool_config)

            # Create a new pool
            self._pools[key] = ConnectionPool(
                self, plugin_type, plugin_name, config, pool_config
            )

        # Get a connection from the pool
        pooled_connection = self._pools[key].get_connection()
        if pooled_connection:
            return pooled_connection.connection

        return None

    def return_pooled_connection(self, plugin_type: Union[str, PluginCategory], plugin_name: str,
                                connection: ConnectionProtocol) -> None:
        """
        Return a connection to a pool.

        Args:
            plugin_type: Type of the plugin
            plugin_name: Name of the plugin
            connection: Connection to return
        """
        # Convert string plugin type to enum if necessary
        if isinstance(plugin_type, str):
            try:
                plugin_type = next(pt for pt in PluginCategory if pt.value == plugin_type)
            except StopIteration:
                logger.error(f"Invalid plugin type: {plugin_type}")
                return

        # Get the pool
        key = (plugin_type.value, plugin_name)
        if key in self._pools:
            # Find the pooled connection
            for pooled_connection in list(self._pools[key]._active_connections):
                if pooled_connection.connection == connection:
                    # Return the connection to the pool
                    self._pools[key].return_connection(pooled_connection)
                    return

        # If we get here, the connection wasn't found in any pool
        # Just disconnect it
        try:
            connection.disconnect()
        except Exception:
            pass

    def get_pool_stats(self, plugin_type: Union[str, PluginCategory], plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics about a connection pool.

        Args:
            plugin_type: Type of the plugin
            plugin_name: Name of the plugin

        Returns:
            Dictionary containing pool statistics if the pool exists, None otherwise
        """
        # Convert string plugin type to enum if necessary
        if isinstance(plugin_type, str):
            try:
                plugin_type = next(pt for pt in PluginCategory if pt.value == plugin_type)
            except StopIteration:
                logger.error(f"Invalid plugin type: {plugin_type}")
                return None

        # Get the pool
        key = (plugin_type.value, plugin_name)
        if key in self._pools:
            return self._pools[key].get_stats()

        return None

    def close_pool(self, plugin_type: Union[str, PluginCategory], plugin_name: str) -> None:
        """
        Close a connection pool.

        Args:
            plugin_type: Type of the plugin
            plugin_name: Name of the plugin
        """
        # Convert string plugin type to enum if necessary
        if isinstance(plugin_type, str):
            try:
                plugin_type = next(pt for pt in PluginCategory if pt.value == plugin_type)
            except StopIteration:
                logger.error(f"Invalid plugin type: {plugin_type}")
                return

        # Close the pool
        key = (plugin_type.value, plugin_name)
        if key in self._pools:
            self._pools[key].close()
            del self._pools[key]


# Create a singleton instance of the connection manager
manager = ConnectionManager()
