"""
Component Adapter Module for Science Data Kit

This module provides adapters for the UI components of the application.
It bridges between the core functionality and the UI components.
"""

import streamlit as st
from typing import Dict, Any, Optional, Callable, List, Union, Type
import importlib
import sys
from pathlib import Path

class ComponentAdapter:
    """
    Adapter for UI components.
    
    This class provides methods for loading and rendering UI components dynamically.
    """
    
    def __init__(self, components_module: str = "science_data_kit.ui.components"):
        """
        Initialize the ComponentAdapter.
        
        Args:
            components_module: The module path where components are defined.
        """
        self.components_module = components_module
        self.components = {}
        self._discover_components()
    
    def _discover_components(self) -> None:
        """
        Discover available components in the components module.
        """
        try:
            # Import the components module
            module = importlib.import_module(self.components_module)
            
            # Get all submodules
            for name in dir(module):
                if name.startswith("_"):
                    continue
                
                try:
                    # Import the submodule
                    component_module = importlib.import_module(f"{self.components_module}.{name}")
                    
                    # Check if the module has a render function
                    if hasattr(component_module, "render"):
                        # Add the component to the components dictionary
                        self.components[name] = component_module.render
                except ImportError:
                    continue
        except ImportError:
            st.warning(f"Could not import components module: {self.components_module}")
    
    def get_available_components(self) -> List[str]:
        """
        Get a list of available components.
        
        Returns:
            A list of component names.
        """
        return list(self.components.keys())
    
    def render_component(self, component_name: str, **kwargs) -> Any:
        """
        Render a component by name.
        
        Args:
            component_name: The name of the component to render.
            **kwargs: Additional arguments to pass to the component's render function.
            
        Returns:
            The return value of the component's render function.
        """
        if component_name in self.components:
            return self.components[component_name](**kwargs)
        else:
            st.error(f"Component not found: {component_name}")
            return None
    
    def register_component(self, name: str, render_func: Callable) -> None:
        """
        Register a new component.
        
        Args:
            name: The name of the component.
            render_func: The function to call to render the component.
        """
        self.components[name] = render_func

class DatabaseAdapter:
    """
    Adapter for database operations.
    
    This class provides methods for interacting with the database from UI components.
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize the DatabaseAdapter.
        
        Args:
            db_manager: The database manager instance to use.
        """
        self.db_manager = db_manager
        
        # Import the db_manager if not provided
        if self.db_manager is None:
            try:
                from science_data_kit.core.db.db_manager import db_manager
                self.db_manager = db_manager
            except ImportError:
                st.warning("Could not import db_manager. Database functionality will be limited.")
    
    def connect(self, uri: str, user: str, password: str, database: Optional[str] = None) -> bool:
        """
        Connect to the database.
        
        Args:
            uri: The URI of the database.
            user: The username for authentication.
            password: The password for authentication.
            database: The name of the database to connect to.
            
        Returns:
            True if the connection was successful, False otherwise.
        """
        if self.db_manager is None:
            st.error("Database manager not available.")
            return False
        
        try:
            # Update connection details
            self.db_manager.uri = uri
            self.db_manager.user = user
            self.db_manager.password = password
            if database:
                self.db_manager.database = database
            
            # Connect to the database
            self.db_manager._connect()
            return True
        except Exception as e:
            st.error(f"Error connecting to database: {e}")
            return False
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query on the database.
        
        Args:
            query: The query to execute.
            parameters: Optional parameters for the query.
            
        Returns:
            The results of the query.
        """
        if self.db_manager is None:
            st.error("Database manager not available.")
            return []
        
        try:
            return self.db_manager.execute_query(query, parameters)
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return []
    
    def get_labels(self) -> List[str]:
        """
        Get all labels from the database.
        
        Returns:
            A list of label names.
        """
        if self.db_manager is None:
            st.error("Database manager not available.")
            return []
        
        try:
            return self.db_manager.fetch_labels()
        except Exception as e:
            st.error(f"Error fetching labels: {e}")
            return []

def create_component_adapter() -> ComponentAdapter:
    """
    Create a new ComponentAdapter instance.
    
    Returns:
        A new ComponentAdapter instance.
    """
    return ComponentAdapter()

def create_database_adapter() -> DatabaseAdapter:
    """
    Create a new DatabaseAdapter instance.
    
    Returns:
        A new DatabaseAdapter instance.
    """
    return DatabaseAdapter()