"""
Plugin Connection Page for Science Data Kit.

This page provides a UI for connecting to plugins and interacting with them
based on their capabilities.
"""

import streamlit as st
from typing import Dict, Any, Optional

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.plugin_ui_generator import (
    render_plugin_selector,
    render_plugin_ui,
)
from science_data_kit.core.connections.manager import manager


class PluginConnectPage(BasePage):
    """Page for connecting to plugins."""
    
    def __init__(self):
        """Initialize the page."""
        super().__init__(
            title="Plugin Connection",
            description="Connect to plugins and interact with them based on their capabilities.",
            icon="🔌",
        )
    
    def render(self):
        """Render the page."""
        st.title("Plugin Connection")
        st.write(
            """
            This page allows you to connect to plugins and interact with them based on their capabilities.
            Select a plugin type and plugin from the sidebar to get started.
            """
        )
        
        # Initialize session state for selected plugin
        if "selected_plugin_type" not in st.session_state:
            st.session_state["selected_plugin_type"] = None
        if "selected_plugin_name" not in st.session_state:
            st.session_state["selected_plugin_name"] = None
        
        # Render plugin selector in sidebar
        selected_type, selected_plugin = render_plugin_selector(
            on_select=self._on_plugin_selected
        )
        
        # If a plugin is selected, render its UI
        if (
            st.session_state["selected_plugin_type"] and
            st.session_state["selected_plugin_name"]
        ):
            plugin_type = st.session_state["selected_plugin_type"]
            plugin_name = st.session_state["selected_plugin_name"]
            
            # Show plugin information
            plugin_class = manager.get_plugin_class(plugin_type, plugin_name)
            if plugin_class:
                plugin_instance = plugin_class()
                
                st.header(f"{plugin_name} Plugin")
                st.write(f"**Type:** {plugin_type}")
                st.write(f"**Version:** {plugin_instance.version}")
                st.write(f"**Description:** {plugin_instance.description}")
                
                # Show capabilities
                if hasattr(plugin_instance, "capabilities"):
                    capabilities = plugin_instance.capabilities
                    if capabilities:
                        st.subheader("Capabilities")
                        for capability in sorted(capabilities):
                            st.write(f"- {capability}")
                
                # Render the plugin UI
                render_plugin_ui(
                    plugin_type,
                    plugin_name,
                    on_connect=self._on_plugin_connected,
                    on_disconnect=self._on_plugin_disconnected,
                )
            else:
                st.error(f"Plugin not found: {plugin_type}/{plugin_name}")
        else:
            # Show instructions
            st.info("Select a plugin type and plugin from the sidebar to get started.")
            
            # Show available plugins
            st.subheader("Available Plugins")
            plugin_types = manager.get_plugin_types()
            
            for plugin_type in plugin_types:
                st.write(f"**{plugin_type}**")
                plugins = manager.get_plugins_by_type(plugin_type)
                for plugin_name in plugins:
                    st.write(f"- {plugin_name}")
    
    def _on_plugin_selected(self, plugin_type: str, plugin_name: str):
        """
        Handle plugin selection.
        
        Args:
            plugin_type: The type of plugin
            plugin_name: The name of the plugin
        """
        st.session_state["selected_plugin_type"] = plugin_type
        st.session_state["selected_plugin_name"] = plugin_name
    
    def _on_plugin_connected(self, config: Dict[str, Any], connection_name: str):
        """
        Handle plugin connection.
        
        Args:
            config: The plugin configuration
            connection_name: The name of the connection
        """
        plugin_type = st.session_state["selected_plugin_type"]
        plugin_name = st.session_state["selected_plugin_name"]
        
        # Store the configuration in session state
        st.session_state[f"{plugin_type}_{plugin_name}_config"] = config
        st.session_state[f"{plugin_type}_{plugin_name}_connected"] = True
        
        # Store the connection name if provided
        if connection_name:
            st.session_state[f"{plugin_type}_{plugin_name}_name"] = connection_name
        else:
            st.session_state[f"{plugin_type}_{plugin_name}_name"] = plugin_name
        
        # Try to connect to the plugin
        try:
            plugin_instance = manager.get_plugin_instance(plugin_type, plugin_name)
            plugin_instance.connect(config)
            st.sidebar.success(f"Connected to {plugin_name}")
        except Exception as e:
            st.sidebar.error(f"Failed to connect to {plugin_name}: {e}")
            st.session_state[f"{plugin_type}_{plugin_name}_connected"] = False
        
        st.rerun()
    
    def _on_plugin_disconnected(self):
        """Handle plugin disconnection."""
        plugin_type = st.session_state["selected_plugin_type"]
        plugin_name = st.session_state["selected_plugin_name"]
        
        # Remove connection from session state
        st.session_state[f"{plugin_type}_{plugin_name}_connected"] = False
        
        # Try to disconnect from the plugin
        try:
            plugin_instance = manager.get_plugin_instance(plugin_type, plugin_name)
            plugin_instance.disconnect()
            st.sidebar.success(f"Disconnected from {plugin_name}")
        except Exception as e:
            st.sidebar.error(f"Failed to disconnect from {plugin_name}: {e}")
        
        st.rerun()


def render_plugin_connect_page():
    """Render the plugin connect page."""
    page = PluginConnectPage()
    page.render()


if __name__ == "__main__":
    render_plugin_connect_page()