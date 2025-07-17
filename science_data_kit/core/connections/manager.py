"""
Connection manager for Science Data Kit.

This module provides a central manager for all connections in the Science Data Kit,
allowing for unified connection management and lifecycle control.
"""

import logging
from typing import Any, Dict, List, Optional, Type, Union, cast

from .protocols.base import ConnectionProtocol
from .registry import PluginCategory, PluginRegistry, registry

# Set up logging
logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Central manager for all connections.
    
    This class provides a high-level interface for managing connections,
    including creation, configuration, and lifecycle management.
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
        # Convert string plugin type to enum if necessary
        if isinstance(plugin_type, str):
            try:
                plugin_type = next(pt for pt in PluginCategory if pt.value == plugin_type)
            except StopIteration:
                logger.error(f"Invalid plugin type: {plugin_type}")
                return None
        
        # Check if connection with this name already exists
        if name in self._connections:
            logger.warning(f"Connection with name '{name}' already exists")
            return None
        
        # Create plugin instance
        plugin = self._registry.create_plugin(plugin_type, plugin_name, config)
        if plugin is None:
            logger.error(f"Failed to create plugin: {plugin_name} ({plugin_type})")
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


# Create a singleton instance of the connection manager
manager = ConnectionManager()