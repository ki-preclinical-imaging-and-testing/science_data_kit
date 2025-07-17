"""
Plugin UI Generator for Science Data Kit.

This module provides functions for generating UI components based on plugin
configuration schemas and capabilities. It enables dynamic form generation
and capability-based feature display for plugins.
"""

import streamlit as st
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
import os
from pathlib import Path

from science_data_kit.core.plugins.config import (
    ConfigField,
    ConfigFieldType,
    PluginConfigSchema,
)
from science_data_kit.core.connections.manager import manager
from science_data_kit.core.connections.protocols.base import ConnectionProtocol
from science_data_kit.core.plugins.interfaces import PluginInterface


def generate_config_field_ui(field: ConfigField, config: Dict[str, Any]) -> Any:
    """
    Generate a UI component for a configuration field.
    
    Args:
        field: The configuration field
        config: The current configuration values
        
    Returns:
        The value from the UI component
    """
    # Get the current value or default
    current_value = config.get(field.name, field.default)
    
    # Generate the appropriate UI component based on field type
    if field.field_type == ConfigFieldType.STRING:
        return st.text_input(
            field.name,
            value=current_value or "",
            help=field.description,
            type="password" if field.secret else "default",
        )
    
    elif field.field_type == ConfigFieldType.INTEGER:
        return st.number_input(
            field.name,
            value=int(current_value) if current_value is not None else 0,
            min_value=field.min_value,
            max_value=field.max_value,
            help=field.description,
        )
    
    elif field.field_type == ConfigFieldType.FLOAT:
        return st.number_input(
            field.name,
            value=float(current_value) if current_value is not None else 0.0,
            min_value=field.min_value,
            max_value=field.max_value,
            help=field.description,
        )
    
    elif field.field_type == ConfigFieldType.BOOLEAN:
        return st.checkbox(
            field.name,
            value=bool(current_value) if current_value is not None else False,
            help=field.description,
        )
    
    elif field.field_type == ConfigFieldType.ENUM:
        return st.selectbox(
            field.name,
            options=field.enum_values or [],
            index=field.enum_values.index(current_value) if current_value in (field.enum_values or []) else 0,
            help=field.description,
        )
    
    elif field.field_type == ConfigFieldType.FILE_PATH:
        path = st.text_input(
            field.name,
            value=current_value or "",
            help=f"{field.description} (must be a valid file path)",
        )
        
        # Show validation status
        if path:
            file_path = Path(path)
            if not file_path.exists():
                st.warning(f"File does not exist: {path}")
            elif not file_path.is_file():
                st.warning(f"Path is not a file: {path}")
        
        return path
    
    elif field.field_type == ConfigFieldType.DIRECTORY_PATH:
        path = st.text_input(
            field.name,
            value=current_value or "",
            help=f"{field.description} (must be a valid directory path)",
        )
        
        # Show validation status
        if path:
            dir_path = Path(path)
            if not dir_path.exists():
                st.warning(f"Directory does not exist: {path}")
                # Add option to create directory
                if st.button(f"Create directory: {path}"):
                    try:
                        dir_path.mkdir(parents=True, exist_ok=True)
                        st.success(f"Created directory: {path}")
                    except Exception as e:
                        st.error(f"Failed to create directory: {e}")
            elif not dir_path.is_dir():
                st.warning(f"Path is not a directory: {path}")
        
        return path
    
    elif field.field_type == ConfigFieldType.SECRET:
        return st.text_input(
            field.name,
            value=current_value or "",
            help=field.description,
            type="password",
        )
    
    elif field.field_type == ConfigFieldType.OBJECT:
        st.subheader(field.name)
        st.markdown(field.description)
        
        # Create an expander for the object
        with st.expander(f"{field.name} Details", expanded=True):
            # Initialize the object if it doesn't exist
            if current_value is None:
                current_value = {}
            
            # Create UI components for each nested field
            object_value = {}
            if field.nested_fields:
                for nested_field in field.nested_fields:
                    object_value[nested_field.name] = generate_config_field_ui(
                        nested_field, current_value
                    )
            
            return object_value
    
    elif field.field_type == ConfigFieldType.ARRAY:
        st.subheader(field.name)
        st.markdown(field.description)
        
        # Initialize the array if it doesn't exist
        if current_value is None:
            current_value = []
        
        # Create an expander for the array
        with st.expander(f"{field.name} Items", expanded=True):
            # For now, just show a text area for JSON input
            # In a more advanced implementation, we could add/remove items dynamically
            import json
            
            try:
                array_json = json.dumps(current_value)
            except Exception:
                array_json = "[]"
            
            array_input = st.text_area(
                f"Enter {field.name} as JSON array",
                value=array_json,
                height=100,
            )
            
            try:
                return json.loads(array_input)
            except Exception:
                st.error("Invalid JSON array format")
                return current_value
    
    # Default case
    return current_value


def generate_plugin_config_form(
    plugin_type: str,
    plugin_name: str,
    on_connect: Optional[Callable] = None,
    on_disconnect: Optional[Callable] = None,
) -> Dict[str, Any]:
    """
    Generate a configuration form for a plugin.
    
    Args:
        plugin_type: The type of plugin (e.g., 'filesystem', 'database')
        plugin_name: The name of the plugin
        on_connect: Callback function to call when the plugin is connected
        on_disconnect: Callback function to call when the plugin is disconnected
        
    Returns:
        The configuration values from the form
    """
    # Get the plugin class
    plugin_class = manager.get_plugin_class(plugin_type, plugin_name)
    if not plugin_class:
        st.error(f"Plugin not found: {plugin_type}/{plugin_name}")
        return {}
    
    # Create an instance to get the config schema
    plugin_instance = plugin_class()
    config_schema = plugin_instance.config_schema
    
    # Check if the plugin is already connected
    connection_key = f"{plugin_type}_{plugin_name}_connected"
    config_key = f"{plugin_type}_{plugin_name}_config"
    
    is_connected = st.session_state.get(connection_key, False)
    
    if is_connected:
        # Show connection status
        st.sidebar.success(f"Connected to {plugin_name}")
        
        # Show plugin capabilities
        if hasattr(plugin_instance, "capabilities"):
            capabilities = plugin_instance.capabilities
            if capabilities:
                st.sidebar.write("Capabilities:")
                for capability in sorted(capabilities):
                    st.sidebar.write(f"- {capability}")
        
        # Show current configuration (masked for secrets)
        st.sidebar.write("Current Configuration:")
        current_config = st.session_state.get(config_key, {})
        for key, value in current_config.items():
            # Check if this is a secret field
            is_secret = False
            for field in config_schema.fields:
                if field.name == key and (field.secret or field.field_type == ConfigFieldType.SECRET):
                    is_secret = True
                    break
            
            if is_secret:
                st.sidebar.write(f"- {key}: ********")
            else:
                st.sidebar.write(f"- {key}: {value}")
        
        # Disconnect button
        if st.sidebar.button(f"Disconnect from {plugin_name}"):
            if on_disconnect:
                on_disconnect()
            else:
                # Remove connection from session state
                st.session_state[connection_key] = False
                st.rerun()
        
        return st.session_state.get(config_key, {})
    else:
        # Show connection status
        st.sidebar.warning(f"Not connected to {plugin_name}")
        
        # Create a form for the plugin configuration
        with st.sidebar.form(f"{plugin_type}_{plugin_name}_form"):
            # Connection name
            connection_name = st.text_input(
                "Connection Name",
                value="",
                placeholder=f"Enter a name for this {plugin_name} connection"
            )
            
            # Generate UI components for each field in the schema
            config = {}
            for field in config_schema.fields:
                config[field.name] = generate_config_field_ui(field, {})
            
            # Connect button
            if st.form_submit_button(f"Connect to {plugin_name}"):
                # Validate the configuration
                if config_schema.validate_config(config):
                    # Connect to the plugin
                    if on_connect:
                        on_connect(config, connection_name)
                    else:
                        # Store the configuration in session state
                        st.session_state[config_key] = config
                        st.session_state[connection_key] = True
                        
                        # Store the connection name if provided
                        if connection_name:
                            st.session_state[f"{plugin_type}_{plugin_name}_name"] = connection_name
                        else:
                            st.session_state[f"{plugin_type}_{plugin_name}_name"] = plugin_name
                        
                        # Try to connect to the plugin
                        try:
                            plugin_instance.connect(config)
                            st.sidebar.success(f"Connected to {plugin_name}")
                        except Exception as e:
                            st.sidebar.error(f"Failed to connect to {plugin_name}: {e}")
                            st.session_state[connection_key] = False
                        
                        st.rerun()
                else:
                    st.sidebar.error("Invalid configuration. Please check the values.")
            
            return config


def render_plugin_selector(
    on_select: Optional[Callable] = None,
) -> None:
    """
    Render a selector for available plugins.
    
    Args:
        on_select: Callback function to call when a plugin is selected
    """
    # Get all available plugins
    plugin_types = manager.get_plugin_types()
    
    # Create a selectbox for plugin types
    selected_type = st.sidebar.selectbox(
        "Plugin Type",
        options=["Select a type..."] + list(plugin_types),
    )
    
    if selected_type and selected_type != "Select a type...":
        # Get plugins of the selected type
        plugins = manager.get_plugins_by_type(selected_type)
        
        # Create a selectbox for plugins
        selected_plugin = st.sidebar.selectbox(
            "Plugin",
            options=["Select a plugin..."] + list(plugins),
        )
        
        if selected_plugin and selected_plugin != "Select a plugin...":
            # Call the callback if provided
            if on_select:
                on_select(selected_type, selected_plugin)
            
            # Return the selected plugin
            return selected_type, selected_plugin
    
    return None, None


def render_capability_based_ui(
    plugin_instance: Any,
    capability: str,
) -> None:
    """
    Render UI components based on a plugin's capability.
    
    Args:
        plugin_instance: The plugin instance
        capability: The capability to render UI for
    """
    if not hasattr(plugin_instance, "capabilities"):
        return
    
    capabilities = plugin_instance.capabilities
    if capability not in capabilities:
        return
    
    # Render UI based on capability
    if capability == "browsable":
        # Render a file browser
        st.subheader("File Browser")
        
        # Get the current path from session state or use root
        current_path = st.session_state.get("current_path", "")
        
        # Show the current path
        st.write(f"Current path: {current_path}")
        
        # List the directory contents
        try:
            contents = plugin_instance.list_directory(current_path)
            
            # Show directories first, then files
            directories = [item for item in contents if item.get("is_dir")]
            files = [item for item in contents if not item.get("is_dir")]
            
            # Show directories
            if directories:
                st.write("Directories:")
                for directory in directories:
                    if st.button(f"📁 {directory['name']}", key=f"dir_{directory['path']}"):
                        # Navigate to the directory
                        st.session_state["current_path"] = directory["path"]
                        st.rerun()
            
            # Show files
            if files:
                st.write("Files:")
                for file in files:
                    st.write(f"📄 {file['name']} ({file.get('size', 'N/A')} bytes)")
                    
                    # Show file actions
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View", key=f"view_{file['path']}"):
                            # Read the file
                            try:
                                content = plugin_instance.read_file(file["path"])
                                st.text_area("File Content", value=content.decode("utf-8"), height=300)
                            except Exception as e:
                                st.error(f"Failed to read file: {e}")
                    
                    with col2:
                        if "writable" in capabilities:
                            if st.button("Delete", key=f"delete_{file['path']}"):
                                # Delete the file
                                try:
                                    plugin_instance.delete_file(file["path"])
                                    st.success(f"Deleted file: {file['name']}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete file: {e}")
            
            # Show navigation controls
            st.write("Navigation:")
            if current_path:
                if st.button("⬆️ Up"):
                    # Go up one directory
                    parent_path = str(Path(current_path).parent)
                    st.session_state["current_path"] = parent_path
                    st.rerun()
            
            if st.button("🏠 Home"):
                # Go to the root directory
                st.session_state["current_path"] = ""
                st.rerun()
            
            # Show upload form if writable
            if "writable" in capabilities:
                st.write("Upload:")
                uploaded_file = st.file_uploader("Choose a file")
                if uploaded_file is not None:
                    # Create a new file
                    try:
                        file_path = str(Path(current_path) / uploaded_file.name)
                        plugin_instance.write_file(file_path, uploaded_file.getvalue())
                        st.success(f"Uploaded file: {uploaded_file.name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to upload file: {e}")
        
        except Exception as e:
            st.error(f"Failed to list directory: {e}")
    
    elif capability == "queryable":
        # Render a query interface
        st.subheader("Query Interface")
        
        # Get the query from the text area
        query = st.text_area("Enter your query", height=100)
        
        # Execute button
        if st.button("Execute Query"):
            if query:
                try:
                    # Execute the query
                    result = plugin_instance.execute_query(query)
                    
                    # Show the result
                    st.write("Query Result:")
                    st.write(result)
                except Exception as e:
                    st.error(f"Failed to execute query: {e}")
            else:
                st.warning("Please enter a query")
    
    elif capability == "searchable":
        # Render a search interface
        st.subheader("Search Interface")
        
        # Get the search query
        search_query = st.text_input("Search")
        
        # Search button
        if st.button("Search"):
            if search_query:
                try:
                    # Execute the search
                    results = plugin_instance.search(search_query)
                    
                    # Show the results
                    st.write(f"Search Results for '{search_query}':")
                    for result in results:
                        st.write(result)
                except Exception as e:
                    st.error(f"Failed to search: {e}")
            else:
                st.warning("Please enter a search query")


def render_plugin_ui(
    plugin_type: str,
    plugin_name: str,
    on_connect: Optional[Callable] = None,
    on_disconnect: Optional[Callable] = None,
) -> None:
    """
    Render the UI for a plugin.
    
    Args:
        plugin_type: The type of plugin (e.g., 'filesystem', 'database')
        plugin_name: The name of the plugin
        on_connect: Callback function to call when the plugin is connected
        on_disconnect: Callback function to call when the plugin is disconnected
    """
    # Generate the configuration form
    config = generate_plugin_config_form(
        plugin_type, plugin_name, on_connect, on_disconnect
    )
    
    # Check if the plugin is connected
    connection_key = f"{plugin_type}_{plugin_name}_connected"
    is_connected = st.session_state.get(connection_key, False)
    
    if is_connected:
        # Get the plugin instance
        plugin_instance = manager.get_plugin_instance(plugin_type, plugin_name)
        if plugin_instance:
            # Get the plugin capabilities
            if hasattr(plugin_instance, "capabilities"):
                capabilities = plugin_instance.capabilities
                
                # Render UI for each capability
                for capability in capabilities:
                    render_capability_based_ui(plugin_instance, capability)