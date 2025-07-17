"""
Plugin Connect Page Module for Science Data Kit Core

This module provides the framework-independent implementation of the plugin connect page.
It defines the core functionality for managing connections to plugins.
"""

from typing import List, Dict, Any, Optional, Tuple
import os
import uuid
import json
import time
from pathlib import Path

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import PluginConnectPageData
from science_data_kit.core.connections.manager import manager

class PluginConnectPage(BasePage):
    """
    Core implementation of the plugin connect page.

    This class provides the framework-independent functionality for managing
    connections to plugins. It returns a PluginConnectPageData object
    that can be rendered by any UI framework.
    """

    def __init__(self, db_connection=None):
        """
        Initialize the plugin connect page.

        Args:
            db_connection: Optional database connection to use for data retrieval.
        """
        super().__init__(db_connection)
        self.selected_plugin_type = None
        self.selected_plugin_name = None
        self.connection_status = {}
        self.connection_errors = {}
        self.active_connections = []

    def get_page_data(self) -> PluginConnectPageData:
        """
        Return data needed to render the plugin connect page.

        Returns:
            A PluginConnectPageData object containing the data needed to render the page.
        """
        # Get available plugin types and plugins
        plugin_types = manager.get_plugin_types()
        available_plugins = {}
        for plugin_type in plugin_types:
            available_plugins[plugin_type] = manager.get_plugins_by_type(plugin_type)

        # Get plugin info and capabilities if a plugin is selected
        plugin_info = {}
        plugin_capabilities = []
        if self.selected_plugin_type and self.selected_plugin_name:
            plugin_class = manager.get_plugin_class(self.selected_plugin_type, self.selected_plugin_name)
            if plugin_class:
                plugin_instance = plugin_class()
                plugin_info = {
                    "name": self.selected_plugin_name,
                    "type": self.selected_plugin_type,
                    "version": getattr(plugin_instance, "version", "Unknown"),
                    "description": getattr(plugin_instance, "description", "No description available")
                }
                if hasattr(plugin_instance, "capabilities"):
                    plugin_capabilities = plugin_instance.capabilities

        return PluginConnectPageData(
            title="Plugin Connection",
            available_plugin_types=plugin_types,
            available_plugins=available_plugins,
            selected_plugin_type=self.selected_plugin_type,
            selected_plugin_name=self.selected_plugin_name,
            plugin_info=plugin_info,
            plugin_capabilities=plugin_capabilities,
            connection_status=self.connection_status,
            connection_errors=self.connection_errors,
            active_connections=self.active_connections
        )

    def select_plugin(self, plugin_type: str, plugin_name: str) -> bool:
        """
        Select a plugin.

        Args:
            plugin_type: The type of plugin to select.
            plugin_name: The name of the plugin to select.

        Returns:
            True if the plugin was found and selected, False otherwise.
        """
        # Check if the plugin exists
        plugin_class = manager.get_plugin_class(plugin_type, plugin_name)
        if not plugin_class:
            return False

        # Set the selected plugin
        self.selected_plugin_type = plugin_type
        self.selected_plugin_name = plugin_name
        return True

    def connect_plugin(self, config: Dict[str, Any], connection_name: Optional[str] = None) -> bool:
        """
        Connect to a plugin.

        Args:
            config: The configuration parameters for the plugin.
            connection_name: Optional name for the connection.

        Returns:
            True if the connection was successful, False otherwise.
        """
        if not self.selected_plugin_type or not self.selected_plugin_name:
            return False

        # Generate a connection ID
        conn_id = f"{self.selected_plugin_type}_{self.selected_plugin_name}_{len(self.active_connections)}"
        conn_name = connection_name or f"{self.selected_plugin_name} Connection"

        try:
            # Get the plugin instance
            plugin_instance = manager.get_plugin_instance(self.selected_plugin_type, self.selected_plugin_name)
            if not plugin_instance:
                self.connection_errors[conn_id] = f"Failed to create plugin instance: {self.selected_plugin_type}/{self.selected_plugin_name}"
                return False

            # Connect to the plugin
            plugin_instance.connect(config)

            # Store the connection
            self.active_connections.append({
                "id": conn_id,
                "name": conn_name,
                "type": self.selected_plugin_type,
                "plugin": self.selected_plugin_name,
                "config": {k: v for k, v in config.items() if not k.startswith("password") and not k.startswith("secret")}
            })
            self.connection_status[conn_id] = True
            return True
        except Exception as e:
            self.connection_errors[conn_id] = str(e)
            self.connection_status[conn_id] = False
            return False

    def disconnect_plugin(self, connection_id: str) -> bool:
        """
        Disconnect from a plugin.

        Args:
            connection_id: The ID of the connection to disconnect.

        Returns:
            True if the disconnection was successful, False otherwise.
        """
        # Find the connection
        connection = None
        for conn in self.active_connections:
            if conn["id"] == connection_id:
                connection = conn
                break

        if not connection:
            return False

        try:
            # Get the plugin instance
            plugin_instance = manager.get_plugin_instance(connection["type"], connection["plugin"])
            if plugin_instance:
                # Disconnect from the plugin
                plugin_instance.disconnect()

            # Remove the connection
            self.active_connections = [conn for conn in self.active_connections if conn["id"] != connection_id]
            self.connection_status.pop(connection_id, None)
            self.connection_errors.pop(connection_id, None)
            return True
        except Exception as e:
            self.connection_errors[connection_id] = str(e)
            return False