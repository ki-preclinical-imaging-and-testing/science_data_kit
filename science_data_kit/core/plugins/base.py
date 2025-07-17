"""
Base classes for the Science Data Kit plugin system.

This module provides the base classes for creating and managing plugins in the
Science Data Kit. The Plugin class defines the interface that all plugins must
implement, and the PluginManager class handles loading, registering, and managing
plugins.
"""

import abc
import logging
from enum import Enum
from typing import Dict, List, Optional, Set, Type, Any

logger = logging.getLogger(__name__)


class PluginState(Enum):
    """Enum representing the possible states of a plugin."""
    REGISTERED = "registered"  # Plugin is registered but not activated
    ACTIVE = "active"          # Plugin is active and running
    DISABLED = "disabled"      # Plugin is disabled by user or due to error
    ERROR = "error"            # Plugin encountered an error during activation


class Plugin(abc.ABC):
    """Base class for all Science Data Kit plugins.
    
    All plugins must inherit from this class and implement its abstract methods.
    """
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return the name of the plugin."""
        pass
    
    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Return the version of the plugin."""
        pass
    
    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Return a description of the plugin."""
        pass
    
    @property
    def dependencies(self) -> List[str]:
        """Return a list of plugin names that this plugin depends on.
        
        By default, a plugin has no dependencies. Override this method to
        specify dependencies.
        """
        return []
    
    @abc.abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin.
        
        This method is called when the plugin is activated. It should perform
        any setup required for the plugin to function.
        
        Raises:
            Exception: If initialization fails.
        """
        pass
    
    def shutdown(self) -> None:
        """Shut down the plugin.
        
        This method is called when the plugin is deactivated. It should perform
        any cleanup required when the plugin is no longer needed.
        
        By default, this method does nothing. Override it to implement custom
        shutdown behavior.
        """
        pass


class PluginManager:
    """Manager for Science Data Kit plugins.
    
    The PluginManager handles loading, registering, activating, and deactivating
    plugins. It ensures that plugins are activated in the correct order based on
    their dependencies.
    """
    
    def __init__(self):
        """Initialize a new PluginManager."""
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_states: Dict[str, PluginState] = {}
        self._plugin_errors: Dict[str, str] = {}
    
    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin with the manager.
        
        Args:
            plugin: The plugin to register.
            
        Raises:
            ValueError: If a plugin with the same name is already registered.
        """
        if plugin.name in self._plugins:
            raise ValueError(f"A plugin with name '{plugin.name}' is already registered.")
        
        self._plugins[plugin.name] = plugin
        self._plugin_states[plugin.name] = PluginState.REGISTERED
        logger.info(f"Registered plugin: {plugin.name} (version {plugin.version})")
    
    def activate_plugin(self, plugin_name: str) -> bool:
        """Activate a registered plugin.
        
        This method activates the specified plugin and all its dependencies.
        
        Args:
            plugin_name: The name of the plugin to activate.
            
        Returns:
            bool: True if the plugin was activated successfully, False otherwise.
            
        Raises:
            ValueError: If the plugin is not registered.
        """
        if plugin_name not in self._plugins:
            raise ValueError(f"Plugin '{plugin_name}' is not registered.")
        
        # If the plugin is already active, return True
        if self._plugin_states.get(plugin_name) == PluginState.ACTIVE:
            return True
        
        # If the plugin is in an error state, return False
        if self._plugin_states.get(plugin_name) == PluginState.ERROR:
            return False
        
        # Activate dependencies first
        plugin = self._plugins[plugin_name]
        for dependency in plugin.dependencies:
            if dependency not in self._plugins:
                error_msg = f"Plugin '{plugin_name}' depends on '{dependency}', which is not registered."
                self._plugin_states[plugin_name] = PluginState.ERROR
                self._plugin_errors[plugin_name] = error_msg
                logger.error(error_msg)
                return False
            
            if not self.activate_plugin(dependency):
                error_msg = f"Failed to activate dependency '{dependency}' for plugin '{plugin_name}'."
                self._plugin_states[plugin_name] = PluginState.ERROR
                self._plugin_errors[plugin_name] = error_msg
                logger.error(error_msg)
                return False
        
        # Activate the plugin
        try:
            plugin.initialize()
            self._plugin_states[plugin_name] = PluginState.ACTIVE
            logger.info(f"Activated plugin: {plugin_name}")
            return True
        except Exception as e:
            error_msg = f"Failed to activate plugin '{plugin_name}': {str(e)}"
            self._plugin_states[plugin_name] = PluginState.ERROR
            self._plugin_errors[plugin_name] = error_msg
            logger.error(error_msg, exc_info=True)
            return False
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate an active plugin.
        
        Args:
            plugin_name: The name of the plugin to deactivate.
            
        Returns:
            bool: True if the plugin was deactivated successfully, False otherwise.
            
        Raises:
            ValueError: If the plugin is not registered.
        """
        if plugin_name not in self._plugins:
            raise ValueError(f"Plugin '{plugin_name}' is not registered.")
        
        # If the plugin is not active, return True
        if self._plugin_states.get(plugin_name) != PluginState.ACTIVE:
            return True
        
        # Check if any active plugins depend on this one
        for name, plugin in self._plugins.items():
            if (self._plugin_states.get(name) == PluginState.ACTIVE and
                plugin_name in plugin.dependencies):
                logger.warning(
                    f"Cannot deactivate plugin '{plugin_name}' because "
                    f"plugin '{name}' depends on it."
                )
                return False
        
        # Deactivate the plugin
        try:
            self._plugins[plugin_name].shutdown()
            self._plugin_states[plugin_name] = PluginState.REGISTERED
            logger.info(f"Deactivated plugin: {plugin_name}")
            return True
        except Exception as e:
            error_msg = f"Error during deactivation of plugin '{plugin_name}': {str(e)}"
            self._plugin_states[plugin_name] = PluginState.ERROR
            self._plugin_errors[plugin_name] = error_msg
            logger.error(error_msg, exc_info=True)
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a registered plugin by name.
        
        Args:
            plugin_name: The name of the plugin to get.
            
        Returns:
            The plugin if found, None otherwise.
        """
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, Plugin]:
        """Get all registered plugins.
        
        Returns:
            A dictionary mapping plugin names to plugin instances.
        """
        return self._plugins.copy()
    
    def get_active_plugins(self) -> Dict[str, Plugin]:
        """Get all active plugins.
        
        Returns:
            A dictionary mapping plugin names to plugin instances for all active plugins.
        """
        return {
            name: plugin
            for name, plugin in self._plugins.items()
            if self._plugin_states.get(name) == PluginState.ACTIVE
        }
    
    def get_plugin_state(self, plugin_name: str) -> Optional[PluginState]:
        """Get the state of a plugin.
        
        Args:
            plugin_name: The name of the plugin.
            
        Returns:
            The state of the plugin if found, None otherwise.
        """
        return self._plugin_states.get(plugin_name)
    
    def get_plugin_error(self, plugin_name: str) -> Optional[str]:
        """Get the error message for a plugin in the ERROR state.
        
        Args:
            plugin_name: The name of the plugin.
            
        Returns:
            The error message if the plugin is in the ERROR state, None otherwise.
        """
        if self._plugin_states.get(plugin_name) == PluginState.ERROR:
            return self._plugin_errors.get(plugin_name)
        return None
    
    def activate_all_plugins(self) -> Dict[str, bool]:
        """Activate all registered plugins.
        
        Returns:
            A dictionary mapping plugin names to activation success status.
        """
        results = {}
        for plugin_name in self._plugins:
            results[plugin_name] = self.activate_plugin(plugin_name)
        return results
    
    def deactivate_all_plugins(self) -> Dict[str, bool]:
        """Deactivate all active plugins.
        
        Returns:
            A dictionary mapping plugin names to deactivation success status.
        """
        results = {}
        # Deactivate in reverse dependency order
        active_plugins = list(self.get_active_plugins().keys())
        for plugin_name in reversed(active_plugins):
            results[plugin_name] = self.deactivate_plugin(plugin_name)
        return results