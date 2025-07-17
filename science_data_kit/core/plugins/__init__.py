"""
Plugin system for the Science Data Kit.

This module provides a framework for extending the Science Data Kit with plugins.
Plugins can add new functionality, modify existing behavior, or integrate with
external systems.
"""

from science_data_kit.core.plugins.base import Plugin, PluginManager
from science_data_kit.core.plugins.discovery import discover_plugins

__all__ = ['Plugin', 'PluginManager', 'discover_plugins']