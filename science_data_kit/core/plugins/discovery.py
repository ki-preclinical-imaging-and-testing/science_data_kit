"""
Plugin discovery mechanisms for the Science Data Kit.

This module provides functions for discovering and loading plugins from various
sources, such as installed packages, directories, and entry points.
"""

import importlib
import importlib.util
import inspect
import logging
import os
import pkgutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Type, Any, Callable, Iterator, Tuple

from science_data_kit.core.plugins.base import Plugin, PluginManager

logger = logging.getLogger(__name__)


def discover_plugins(
    plugin_manager: PluginManager,
    plugin_dirs: Optional[List[str]] = None,
    plugin_modules: Optional[List[str]] = None,
    plugin_entry_points: Optional[List[str]] = None,
) -> Dict[str, bool]:
    """Discover and register plugins from various sources.
    
    This function discovers plugins from the specified directories, modules, and
    entry points, registers them with the provided plugin manager, and returns
    a dictionary mapping plugin names to registration success status.
    
    Args:
        plugin_manager: The plugin manager to register discovered plugins with.
        plugin_dirs: A list of directory paths to search for plugins.
        plugin_modules: A list of module names to search for plugins.
        plugin_entry_points: A list of entry point group names to search for plugins.
        
    Returns:
        A dictionary mapping plugin names to registration success status.
    """
    results = {}
    
    # Discover plugins from directories
    if plugin_dirs:
        for plugin_dir in plugin_dirs:
            dir_results = discover_plugins_from_directory(plugin_manager, plugin_dir)
            results.update(dir_results)
    
    # Discover plugins from modules
    if plugin_modules:
        for plugin_module in plugin_modules:
            module_results = discover_plugins_from_module(plugin_manager, plugin_module)
            results.update(module_results)
    
    # Discover plugins from entry points
    if plugin_entry_points:
        for entry_point_group in plugin_entry_points:
            entry_point_results = discover_plugins_from_entry_points(
                plugin_manager, entry_point_group
            )
            results.update(entry_point_results)
    
    return results


def discover_plugins_from_directory(
    plugin_manager: PluginManager, directory: str
) -> Dict[str, bool]:
    """Discover and register plugins from a directory.
    
    This function searches the specified directory for Python modules and packages,
    imports them, and registers any Plugin subclasses found in them with the
    provided plugin manager.
    
    Args:
        plugin_manager: The plugin manager to register discovered plugins with.
        directory: The directory path to search for plugins.
        
    Returns:
        A dictionary mapping plugin names to registration success status.
    """
    results = {}
    directory_path = Path(directory)
    
    if not directory_path.exists() or not directory_path.is_dir():
        logger.warning(f"Plugin directory does not exist or is not a directory: {directory}")
        return results
    
    # Add the directory to sys.path temporarily
    sys.path.insert(0, str(directory_path))
    
    try:
        # Find all Python modules in the directory
        for finder, name, is_pkg in pkgutil.iter_modules([str(directory_path)]):
            try:
                # Import the module
                module = importlib.import_module(name)
                
                # Register plugins from the module
                module_results = register_plugins_from_module(plugin_manager, module)
                results.update(module_results)
                
                # If it's a package, search its submodules
                if is_pkg:
                    package_results = discover_plugins_from_module(plugin_manager, name)
                    results.update(package_results)
            
            except Exception as e:
                logger.error(f"Error importing module {name}: {str(e)}", exc_info=True)
    
    finally:
        # Remove the directory from sys.path
        if str(directory_path) in sys.path:
            sys.path.remove(str(directory_path))
    
    return results


def discover_plugins_from_module(
    plugin_manager: PluginManager, module_name: str
) -> Dict[str, bool]:
    """Discover and register plugins from a module and its submodules.
    
    This function imports the specified module and its submodules, and registers
    any Plugin subclasses found in them with the provided plugin manager.
    
    Args:
        plugin_manager: The plugin manager to register discovered plugins with.
        module_name: The name of the module to search for plugins.
        
    Returns:
        A dictionary mapping plugin names to registration success status.
    """
    results = {}
    
    try:
        # Import the module
        module = importlib.import_module(module_name)
        
        # Register plugins from the module
        module_results = register_plugins_from_module(plugin_manager, module)
        results.update(module_results)
        
        # Search submodules
        if hasattr(module, "__path__"):
            for finder, name, is_pkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
                try:
                    # Import the submodule
                    submodule = importlib.import_module(name)
                    
                    # Register plugins from the submodule
                    submodule_results = register_plugins_from_module(plugin_manager, submodule)
                    results.update(submodule_results)
                
                except Exception as e:
                    logger.error(f"Error importing submodule {name}: {str(e)}", exc_info=True)
    
    except Exception as e:
        logger.error(f"Error importing module {module_name}: {str(e)}", exc_info=True)
    
    return results


def discover_plugins_from_entry_points(
    plugin_manager: PluginManager, entry_point_group: str
) -> Dict[str, bool]:
    """Discover and register plugins from entry points.
    
    This function searches for entry points in the specified group and registers
    any Plugin subclasses found with the provided plugin manager.
    
    Args:
        plugin_manager: The plugin manager to register discovered plugins with.
        entry_point_group: The entry point group name to search for plugins.
        
    Returns:
        A dictionary mapping plugin names to registration success status.
    """
    results = {}
    
    try:
        import importlib.metadata as metadata
    except ImportError:
        # Python < 3.8
        import importlib_metadata as metadata
    
    try:
        for entry_point in metadata.entry_points(group=entry_point_group):
            try:
                # Load the entry point
                plugin_class = entry_point.load()
                
                # Check if it's a Plugin subclass
                if (inspect.isclass(plugin_class) and
                    issubclass(plugin_class, Plugin) and
                    plugin_class is not Plugin):
                    
                    # Create an instance of the plugin
                    plugin = plugin_class()
                    
                    # Register the plugin
                    try:
                        plugin_manager.register_plugin(plugin)
                        results[plugin.name] = True
                    except Exception as e:
                        logger.error(
                            f"Error registering plugin {plugin.name} from entry point "
                            f"{entry_point.name}: {str(e)}",
                            exc_info=True
                        )
                        results[entry_point.name] = False
            
            except Exception as e:
                logger.error(
                    f"Error loading entry point {entry_point.name}: {str(e)}",
                    exc_info=True
                )
                results[entry_point.name] = False
    
    except Exception as e:
        logger.error(
            f"Error discovering plugins from entry point group {entry_point_group}: {str(e)}",
            exc_info=True
        )
    
    return results


def register_plugins_from_module(
    plugin_manager: PluginManager, module: Any
) -> Dict[str, bool]:
    """Register Plugin subclasses from a module with a plugin manager.
    
    This function finds all Plugin subclasses in the specified module and registers
    them with the provided plugin manager.
    
    Args:
        plugin_manager: The plugin manager to register discovered plugins with.
        module: The module to search for Plugin subclasses.
        
    Returns:
        A dictionary mapping plugin names to registration success status.
    """
    results = {}
    
    # Find all Plugin subclasses in the module
    for name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) and
            issubclass(obj, Plugin) and
            obj.__module__ == module.__name__ and
            obj is not Plugin):
            
            try:
                # Create an instance of the plugin
                plugin = obj()
                
                # Register the plugin
                plugin_manager.register_plugin(plugin)
                results[plugin.name] = True
                logger.info(f"Registered plugin {plugin.name} from module {module.__name__}")
            
            except Exception as e:
                logger.error(
                    f"Error registering plugin class {obj.__name__} from module "
                    f"{module.__name__}: {str(e)}",
                    exc_info=True
                )
                results[obj.__name__] = False
    
    return results