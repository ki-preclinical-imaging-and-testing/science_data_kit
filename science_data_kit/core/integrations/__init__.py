"""
Science Data Kit - Integrations Package

This package provides integration with various external platforms and services,
allowing users to access and analyze data from these sources within the Science Data Kit environment.

The package uses a plugin architecture for managing integrations, enabling dynamic discovery,
loading, and management of integration plugins. See the plugin_architecture module for details.
"""

from typing import Dict, Any, List, Optional, Type, cast
import logging
import warnings

# Import the plugin architecture
from .plugin_architecture import (
    PluginBase, DataSourcePlugin, AnalysisToolPlugin, VisualizationPlugin, PlatformPlugin,
    PluginCategory, PluginMetadata, PluginRegistry,
    register_plugin, get_plugin, get_plugins_by_category, get_all_plugins,
    discover_plugins, initialize_plugins, shutdown_plugins
)

# Set up logging
logger = logging.getLogger(__name__)

# Dictionary to store available integration providers (for backward compatibility)
INTEGRATION_PROVIDERS: Dict[str, Any] = {}

def register_provider(name: str, provider_class: Any) -> None:
    """
    Register an integration provider.

    Args:
        name: The name of the provider.
        provider_class: The provider class.

    Note:
        This function is maintained for backward compatibility.
        New code should use the plugin architecture instead.
    """
    warnings.warn(
        "register_provider is deprecated, use register_plugin instead",
        DeprecationWarning, stacklevel=2
    )
    INTEGRATION_PROVIDERS[name] = provider_class

def get_provider(name: str) -> Any:
    """
    Get an integration provider by name.

    Args:
        name: The name of the provider.

    Returns:
        The provider class if found, None otherwise.

    Note:
        This function is maintained for backward compatibility.
        New code should use the plugin architecture instead.
    """
    warnings.warn(
        "get_provider is deprecated, use get_plugin instead",
        DeprecationWarning, stacklevel=2
    )
    # First try to get from the plugin registry
    plugin = get_plugin(name)
    if plugin:
        return plugin

    # Fall back to the old registry
    return INTEGRATION_PROVIDERS.get(name)

def list_providers() -> List[str]:
    """
    List all available integration providers.

    Returns:
        A list of provider names.

    Note:
        This function is maintained for backward compatibility.
        New code should use the plugin architecture instead.
    """
    warnings.warn(
        "list_providers is deprecated, use get_all_plugins instead",
        DeprecationWarning, stacklevel=2
    )
    # Combine plugins from both registries
    return list(set(get_all_plugins() + list(INTEGRATION_PROVIDERS.keys())))

# Import and register providers using the legacy approach (for backward compatibility)
try:
    from .nextsee_provider import NExtSEEKProvider
    register_provider("nextsee", NExtSEEKProvider)
except ImportError:
    pass

try:
    from .fairdom_provider import FAIRDOMProvider
    register_provider("fairdom", FAIRDOMProvider)
except ImportError:
    pass

try:
    from .nc3rs_provider import NC3RsEDAProvider
    register_provider("nc3rs", NC3RsEDAProvider)
except ImportError:
    pass

try:
    from .pubmed_provider import PubMedProvider
    register_provider("pubmed", PubMedProvider)
except ImportError:
    pass

try:
    from .isa_tools_provider import ISAToolsProvider
    register_provider("isa", ISAToolsProvider)
except ImportError:
    pass

# Discover plugins using the new plugin architecture
try:
    num_plugins = discover_plugins()
    logger.info(f"Discovered {num_plugins} plugins")
except Exception as e:
    logger.error(f"Failed to discover plugins: {str(e)}")

# Export the plugin architecture classes and functions
__all__ = [
    # Plugin base classes
    'PluginBase', 'DataSourcePlugin', 'AnalysisToolPlugin', 'VisualizationPlugin', 'PlatformPlugin',

    # Plugin metadata and categories
    'PluginCategory', 'PluginMetadata',

    # Plugin registry functions
    'register_plugin', 'get_plugin', 'get_plugins_by_category', 'get_all_plugins',
    'discover_plugins', 'initialize_plugins', 'shutdown_plugins',

    # Legacy functions (for backward compatibility)
    'register_provider', 'get_provider', 'list_providers'
]
