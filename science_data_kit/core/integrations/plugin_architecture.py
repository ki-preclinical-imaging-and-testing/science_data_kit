"""
Plugin Architecture for Science Data Kit Integrations

This module provides a comprehensive plugin architecture for integrations in the Science Data Kit,
enabling dynamic discovery, loading, and management of integration plugins.

The architecture includes:
1. Base classes and interfaces for different types of integrations
2. A plugin registry system with metadata and categorization
3. Plugin discovery and loading mechanisms
4. Standardized error handling and lifecycle management

This architecture allows for a more extensible and maintainable integration system,
making it easier to add new integrations and manage existing ones.
"""

import importlib
import inspect
import logging
import os
import pkgutil
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, cast

# Type variable for generic plugin types
T = TypeVar('T', bound='PluginBase')

# Set up logging
logger = logging.getLogger(__name__)


class PluginCategory(Enum):
    """Categories of plugins supported by the system."""
    DATA_SOURCE = "data_source"
    ANALYSIS_TOOL = "analysis_tool"
    VISUALIZATION = "visualization"
    EXPORT = "export"
    IMPORT = "import"
    PLATFORM = "platform"
    UTILITY = "utility"
    OTHER = "other"


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str
    author: str
    category: PluginCategory
    dependencies: List[str] = field(default_factory=list)
    website: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    enabled: bool = True


class PluginBase(ABC):
    """
    Base class for all integration plugins.
    
    All plugins must inherit from this class and implement its abstract methods.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """
        Shut down the plugin and release any resources.
        
        Returns:
            True if shutdown was successful, False otherwise.
        """
        pass
    
    def is_compatible(self) -> bool:
        """
        Check if the plugin is compatible with the current environment.
        
        Returns:
            True if the plugin is compatible, False otherwise.
        """
        # Default implementation assumes compatibility
        return True


class DataSourcePlugin(PluginBase):
    """
    Base class for data source integration plugins.
    
    Data source plugins provide access to external data sources like APIs,
    databases, file systems, etc.
    """
    
    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """
        Connect to the data source.
        
        Args:
            **kwargs: Connection parameters specific to the data source.
            
        Returns:
            True if connection was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the data source.
        
        Returns:
            True if disconnection was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the plugin is currently connected to the data source.
        
        Returns:
            True if connected, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_data(self, query: Any, **kwargs) -> Any:
        """
        Get data from the data source.
        
        Args:
            query: The query to execute.
            **kwargs: Additional parameters for the query.
            
        Returns:
            The retrieved data.
        """
        pass


class AnalysisToolPlugin(PluginBase):
    """
    Base class for analysis tool integration plugins.
    
    Analysis tool plugins provide integration with data analysis libraries
    and tools like pandas, scikit-learn, etc.
    """
    
    @abstractmethod
    def analyze(self, data: Any, method: str, **kwargs) -> Any:
        """
        Analyze data using the tool.
        
        Args:
            data: The data to analyze.
            method: The analysis method to use.
            **kwargs: Additional parameters for the analysis.
            
        Returns:
            The analysis results.
        """
        pass
    
    @abstractmethod
    def get_available_methods(self) -> List[str]:
        """
        Get a list of available analysis methods.
        
        Returns:
            List of method names.
        """
        pass


class VisualizationPlugin(PluginBase):
    """
    Base class for visualization integration plugins.
    
    Visualization plugins provide integration with data visualization libraries
    and tools like matplotlib, plotly, etc.
    """
    
    @abstractmethod
    def visualize(self, data: Any, visualization_type: str, **kwargs) -> Any:
        """
        Visualize data.
        
        Args:
            data: The data to visualize.
            visualization_type: The type of visualization to create.
            **kwargs: Additional parameters for the visualization.
            
        Returns:
            The visualization object.
        """
        pass
    
    @abstractmethod
    def get_available_visualizations(self) -> List[str]:
        """
        Get a list of available visualization types.
        
        Returns:
            List of visualization type names.
        """
        pass
    
    @abstractmethod
    def save_visualization(self, visualization: Any, path: str, **kwargs) -> bool:
        """
        Save a visualization to a file.
        
        Args:
            visualization: The visualization to save.
            path: The path to save the visualization to.
            **kwargs: Additional parameters for saving.
            
        Returns:
            True if saving was successful, False otherwise.
        """
        pass


class PlatformPlugin(PluginBase):
    """
    Base class for platform integration plugins.
    
    Platform plugins provide integration with external platforms and services
    like ISA Tools, NC3Rs EDA, etc.
    """
    
    @abstractmethod
    def authenticate(self, **kwargs) -> bool:
        """
        Authenticate with the platform.
        
        Args:
            **kwargs: Authentication parameters.
            
        Returns:
            True if authentication was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if the plugin is currently authenticated with the platform.
        
        Returns:
            True if authenticated, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_resources(self, resource_type: str, **kwargs) -> Any:
        """
        Get resources from the platform.
        
        Args:
            resource_type: The type of resources to get.
            **kwargs: Additional parameters for the request.
            
        Returns:
            The retrieved resources.
        """
        pass


class PluginRegistry:
    """
    Registry for managing integration plugins.
    
    This class provides methods for registering, discovering, loading,
    and managing plugins.
    """
    
    def __init__(self):
        """Initialize the plugin registry."""
        self._plugins: Dict[str, Type[PluginBase]] = {}
        self._instances: Dict[str, PluginBase] = {}
        self._categories: Dict[PluginCategory, Set[str]] = {
            category: set() for category in PluginCategory
        }
        self._initialized = False
    
    def register_plugin(self, plugin_class: Type[PluginBase]) -> bool:
        """
        Register a plugin class.
        
        Args:
            plugin_class: The plugin class to register.
            
        Returns:
            True if registration was successful, False otherwise.
        """
        try:
            # Create a temporary instance to get metadata
            temp_instance = plugin_class()
            metadata = temp_instance.metadata
            
            # Check if a plugin with this name is already registered
            if metadata.name in self._plugins:
                logger.warning(f"Plugin '{metadata.name}' is already registered")
                return False
            
            # Register the plugin
            self._plugins[metadata.name] = plugin_class
            self._categories[metadata.category].add(metadata.name)
            
            logger.info(f"Registered plugin '{metadata.name}' (version {metadata.version})")
            return True
        except Exception as e:
            logger.error(f"Failed to register plugin: {str(e)}")
            return False
    
    def unregister_plugin(self, name: str) -> bool:
        """
        Unregister a plugin.
        
        Args:
            name: The name of the plugin to unregister.
            
        Returns:
            True if unregistration was successful, False otherwise.
        """
        if name not in self._plugins:
            logger.warning(f"Plugin '{name}' is not registered")
            return False
        
        # Shutdown the plugin instance if it exists
        if name in self._instances:
            try:
                self._instances[name].shutdown()
                del self._instances[name]
            except Exception as e:
                logger.error(f"Failed to shutdown plugin '{name}': {str(e)}")
        
        # Get the category and remove the plugin from it
        for category, plugins in self._categories.items():
            if name in plugins:
                plugins.remove(name)
                break
        
        # Remove the plugin from the registry
        del self._plugins[name]
        
        logger.info(f"Unregistered plugin '{name}'")
        return True
    
    def get_plugin_class(self, name: str) -> Optional[Type[PluginBase]]:
        """
        Get a plugin class by name.
        
        Args:
            name: The name of the plugin.
            
        Returns:
            The plugin class if found, None otherwise.
        """
        return self._plugins.get(name)
    
    def get_plugin_instance(self, name: str, initialize: bool = True) -> Optional[PluginBase]:
        """
        Get a plugin instance by name.
        
        If the plugin is not already instantiated, it will be instantiated and initialized.
        
        Args:
            name: The name of the plugin.
            initialize: Whether to initialize the plugin if it's not already instantiated.
            
        Returns:
            The plugin instance if found and successfully instantiated, None otherwise.
        """
        # Return existing instance if available
        if name in self._instances:
            return self._instances[name]
        
        # Get the plugin class
        plugin_class = self.get_plugin_class(name)
        if not plugin_class:
            logger.warning(f"Plugin '{name}' not found")
            return None
        
        # Create a new instance
        try:
            instance = plugin_class()
            
            # Initialize the plugin if requested
            if initialize and not instance.initialize():
                logger.error(f"Failed to initialize plugin '{name}'")
                return None
            
            # Store the instance
            self._instances[name] = instance
            
            return instance
        except Exception as e:
            logger.error(f"Failed to instantiate plugin '{name}': {str(e)}")
            return None
    
    def get_plugins_by_category(self, category: PluginCategory) -> List[str]:
        """
        Get a list of plugin names in a specific category.
        
        Args:
            category: The category to get plugins for.
            
        Returns:
            List of plugin names.
        """
        return list(self._categories.get(category, set()))
    
    def get_all_plugins(self) -> List[str]:
        """
        Get a list of all registered plugin names.
        
        Returns:
            List of plugin names.
        """
        return list(self._plugins.keys())
    
    def get_plugin_metadata(self, name: str) -> Optional[PluginMetadata]:
        """
        Get metadata for a plugin.
        
        Args:
            name: The name of the plugin.
            
        Returns:
            The plugin metadata if found, None otherwise.
        """
        plugin_class = self.get_plugin_class(name)
        if not plugin_class:
            return None
        
        try:
            # Create a temporary instance to get metadata
            temp_instance = plugin_class()
            return temp_instance.metadata
        except Exception as e:
            logger.error(f"Failed to get metadata for plugin '{name}': {str(e)}")
            return None
    
    def discover_plugins(self, package_name: str) -> int:
        """
        Discover plugins in a package.
        
        This method recursively searches for plugin classes in the specified package
        and its subpackages, and registers them.
        
        Args:
            package_name: The name of the package to search in.
            
        Returns:
            The number of plugins discovered and registered.
        """
        count = 0
        
        try:
            package = importlib.import_module(package_name)
            package_path = getattr(package, '__path__', [])
            
            for _, name, is_pkg in pkgutil.iter_modules(package_path):
                full_name = f"{package_name}.{name}"
                
                try:
                    module = importlib.import_module(full_name)
                    
                    # If it's a package, recursively discover plugins
                    if is_pkg:
                        count += self.discover_plugins(full_name)
                    
                    # Find plugin classes in the module
                    for item_name, item in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(item, PluginBase) and 
                            item is not PluginBase and 
                            item is not DataSourcePlugin and 
                            item is not AnalysisToolPlugin and 
                            item is not VisualizationPlugin and 
                            item is not PlatformPlugin):
                            
                            if self.register_plugin(item):
                                count += 1
                
                except Exception as e:
                    logger.error(f"Failed to import module '{full_name}': {str(e)}")
        
        except Exception as e:
            logger.error(f"Failed to discover plugins in package '{package_name}': {str(e)}")
        
        return count
    
    def initialize_all(self) -> bool:
        """
        Initialize all registered plugins.
        
        Returns:
            True if all plugins were successfully initialized, False otherwise.
        """
        if self._initialized:
            logger.warning("Plugins are already initialized")
            return True
        
        success = True
        
        for name in self.get_all_plugins():
            if not self.get_plugin_instance(name):
                success = False
        
        self._initialized = success
        return success
    
    def shutdown_all(self) -> bool:
        """
        Shut down all plugin instances.
        
        Returns:
            True if all plugins were successfully shut down, False otherwise.
        """
        if not self._initialized:
            logger.warning("Plugins are not initialized")
            return True
        
        success = True
        
        for name, instance in list(self._instances.items()):
            try:
                if not instance.shutdown():
                    logger.error(f"Failed to shutdown plugin '{name}'")
                    success = False
                
                del self._instances[name]
            except Exception as e:
                logger.error(f"Error shutting down plugin '{name}': {str(e)}")
                success = False
        
        self._initialized = False
        return success


# Create a global plugin registry instance
plugin_registry = PluginRegistry()


def register_plugin(plugin_class: Type[PluginBase]) -> bool:
    """
    Register a plugin class with the global registry.
    
    This function can be used as a decorator.
    
    Args:
        plugin_class: The plugin class to register.
        
    Returns:
        True if registration was successful, False otherwise.
    """
    return plugin_registry.register_plugin(plugin_class)


def get_plugin(name: str) -> Optional[PluginBase]:
    """
    Get a plugin instance by name from the global registry.
    
    Args:
        name: The name of the plugin.
        
    Returns:
        The plugin instance if found, None otherwise.
    """
    return plugin_registry.get_plugin_instance(name)


def get_plugins_by_category(category: PluginCategory) -> List[str]:
    """
    Get a list of plugin names in a specific category from the global registry.
    
    Args:
        category: The category to get plugins for.
        
    Returns:
        List of plugin names.
    """
    return plugin_registry.get_plugins_by_category(category)


def get_all_plugins() -> List[str]:
    """
    Get a list of all registered plugin names from the global registry.
    
    Returns:
        List of plugin names.
    """
    return plugin_registry.get_all_plugins()


def discover_plugins(package_name: str = "science_data_kit.core.integrations") -> int:
    """
    Discover plugins in a package using the global registry.
    
    Args:
        package_name: The name of the package to search in.
        
    Returns:
        The number of plugins discovered and registered.
    """
    return plugin_registry.discover_plugins(package_name)


def initialize_plugins() -> bool:
    """
    Initialize all registered plugins using the global registry.
    
    Returns:
        True if all plugins were successfully initialized, False otherwise.
    """
    return plugin_registry.initialize_all()


def shutdown_plugins() -> bool:
    """
    Shut down all plugin instances using the global registry.
    
    Returns:
        True if all plugins were successfully shut down, False otherwise.
    """
    return plugin_registry.shutdown_all()