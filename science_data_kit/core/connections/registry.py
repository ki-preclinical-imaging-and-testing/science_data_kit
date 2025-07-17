"""
Plugin registry for Science Data Kit connections.

This module provides a registry for connection plugins, allowing the Science Data Kit
to interact with various data sources through a unified interface.
"""

import enum
import importlib
import inspect
import logging
import pkgutil
from typing import Any, Dict, List, Optional, Type, TypeVar, cast

from .protocols.base import ConnectionProtocol

# Type variable for connection protocol classes
T = TypeVar('T', bound=ConnectionProtocol)

# Set up logging
logger = logging.getLogger(__name__)


class PluginCategory(enum.Enum):
    """Enumeration of plugin categories supported by the Science Data Kit."""
    
    FILESYSTEM = "filesystem"
    DATABASE = "database"
    API = "api"
    OBJECT_STORAGE = "object_storage"
    
    def __str__(self) -> str:
        """Return the string representation of the plugin category."""
        return self.value


class PluginRegistry:
    """
    Registry for connection plugins.
    
    This class manages the registration and retrieval of connection plugins.
    """
    
    def __init__(self):
        """Initialize the plugin registry."""
        self._plugins: Dict[PluginCategory, Dict[str, Type[ConnectionProtocol]]] = {
            category: {} for category in PluginCategory
        }
        self._instances: Dict[PluginCategory, Dict[str, ConnectionProtocol]] = {
            category: {} for category in PluginCategory
        }
    
    def register_plugin(self, plugin_type: PluginCategory, name: str, 
                       plugin_class: Type[ConnectionProtocol]) -> None:
        """
        Register a plugin class with the registry.
        
        Args:
            plugin_type: Type of the plugin
            name: Name of the plugin
            plugin_class: Plugin class to register
        """
        if not issubclass(plugin_class, ConnectionProtocol):
            raise TypeError(f"Plugin class must be a subclass of ConnectionProtocol")
        
        self._plugins[plugin_type][name] = plugin_class
        logger.info(f"Registered plugin: {name} ({plugin_type})")
    
    def unregister_plugin(self, plugin_type: PluginCategory, name: str) -> bool:
        """
        Unregister a plugin from the registry.
        
        Args:
            plugin_type: Type of the plugin
            name: Name of the plugin
            
        Returns:
            True if the plugin was unregistered, False if it wasn't registered
        """
        if name in self._plugins[plugin_type]:
            del self._plugins[plugin_type][name]
            
            # Also remove any instances
            if name in self._instances[plugin_type]:
                del self._instances[plugin_type][name]
                
            logger.info(f"Unregistered plugin: {name} ({plugin_type})")
            return True
        
        return False
    
    def get_plugin_class(self, plugin_type: PluginCategory, name: str) -> Optional[Type[ConnectionProtocol]]:
        """
        Get a plugin class from the registry.
        
        Args:
            plugin_type: Type of the plugin
            name: Name of the plugin
            
        Returns:
            Plugin class if found, None otherwise
        """
        return self._plugins[plugin_type].get(name)
    
    def create_plugin(self, plugin_type: PluginCategory, name: str, 
                     config: Dict[str, Any]) -> Optional[ConnectionProtocol]:
        """
        Create a plugin instance.
        
        Args:
            plugin_type: Type of the plugin
            name: Name of the plugin
            config: Configuration for the plugin
            
        Returns:
            Plugin instance if created successfully, None otherwise
        """
        plugin_class = self.get_plugin_class(plugin_type, name)
        if plugin_class is None:
            logger.warning(f"Plugin not found: {name} ({plugin_type})")
            return None
        
        try:
            plugin = plugin_class()
            self._instances[plugin_type][name] = plugin
            logger.info(f"Created plugin instance: {name} ({plugin_type})")
            return plugin
        except Exception as e:
            logger.error(f"Failed to create plugin instance: {name} ({plugin_type}): {e}")
            return None
    
    def get_plugin(self, plugin_type: PluginCategory, name: str) -> Optional[ConnectionProtocol]:
        """
        Get a plugin instance from the registry.
        
        Args:
            plugin_type: Type of the plugin
            name: Name of the plugin
            
        Returns:
            Plugin instance if found, None otherwise
        """
        return self._instances[plugin_type].get(name)
    
    def get_plugin_names(self, plugin_type: PluginCategory) -> List[str]:
        """
        Get a list of registered plugin names for a given type.
        
        Args:
            plugin_type: Type of the plugin
            
        Returns:
            List of plugin names
        """
        return list(self._plugins[plugin_type].keys())
    
    def get_all_plugins(self, plugin_type: Optional[PluginCategory] = None) -> Dict[str, ConnectionProtocol]:
        """
        Get all plugin instances of a given type.
        
        Args:
            plugin_type: Type of the plugin, or None for all types
            
        Returns:
            Dictionary of plugin instances
        """
        if plugin_type is None:
            # Flatten all plugin instances into a single dictionary
            result = {}
            for plugin_type in PluginCategory:
                result.update(self._instances[plugin_type])
            return result
        
        return self._instances[plugin_type]
    
    def discover_plugins(self, package_name: str) -> int:
        """
        Discover and register plugins from a package.
        
        Args:
            package_name: Name of the package to search for plugins
            
        Returns:
            Number of plugins discovered
        """
        count = 0
        try:
            package = importlib.import_module(package_name)
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
                if is_pkg:
                    # Recursively discover plugins in subpackages
                    count += self.discover_plugins(name)
                else:
                    try:
                        module = importlib.import_module(name)
                        for item_name, item in inspect.getmembers(module, inspect.isclass):
                            if (issubclass(item, ConnectionProtocol) and 
                                item != ConnectionProtocol and 
                                not inspect.isabstract(item)):
                                
                                # Determine plugin type from connection_type property
                                try:
                                    plugin_type_str = item.connection_type
                                    plugin_type = next(
                                        (pt for pt in PluginCategory if pt.value == plugin_type_str),
                                        None
                                    )
                                    
                                    if plugin_type:
                                        self.register_plugin(plugin_type, item_name, item)
                                        count += 1
                                except (AttributeError, StopIteration):
                                    logger.warning(f"Could not determine plugin type for {item_name}")
                    except Exception as e:
                        logger.error(f"Error loading module {name}: {e}")
        except Exception as e:
            logger.error(f"Error discovering plugins in {package_name}: {e}")
        
        return count


# Create a singleton instance of the plugin registry
registry = PluginRegistry()


def register_plugin(plugin_type: PluginCategory, name: str, plugin_class: Type[ConnectionProtocol]) -> None:
    """
    Register a plugin class with the registry.
    
    This is a convenience function that delegates to the singleton registry.
    
    Args:
        plugin_type: Type of the plugin
        name: Name of the plugin
        plugin_class: Plugin class to register
    """
    registry.register_plugin(plugin_type, name, plugin_class)


def get_plugin(plugin_type: PluginCategory, name: str) -> Optional[ConnectionProtocol]:
    """
    Get a plugin instance from the registry.
    
    This is a convenience function that delegates to the singleton registry.
    
    Args:
        plugin_type: Type of the plugin
        name: Name of the plugin
        
    Returns:
        Plugin instance if found, None otherwise
    """
    return registry.get_plugin(plugin_type, name)


def discover_plugins(package_name: str) -> int:
    """
    Discover and register plugins from a package.
    
    This is a convenience function that delegates to the singleton registry.
    
    Args:
        package_name: Name of the package to search for plugins
        
    Returns:
        Number of plugins discovered
    """
    return registry.discover_plugins(package_name)