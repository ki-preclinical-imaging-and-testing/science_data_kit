"""
Connect Page Module for Science Data Kit

This module provides the Connect page for the Science Data Kit application.
The Connect page handles connections to data sources and infrastructure management.
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.sidebar import render_database_sidebar, render_neo4j_container_sidebar
from science_data_kit.ui.components.sidebar import render_jupyter_sidebar, render_neodash_sidebar
from science_data_kit.core.db.db_manager import Neo4jManager, db_manager

class ConnectPage(BasePage):
    """
    Connect page for setting up and managing connections to data sources.

    This page provides functionality for:
    - Connecting to Neo4j databases
    - Managing Docker containers
    - Starting and stopping services
    """

    def __init__(self):
        """Initialize the Connect page."""
        super().__init__("Connect", "🌐")
        self._setup_sidebar()
        self.db_manager = db_manager

    def _setup_sidebar(self):
        """Set up the sidebar items for the Connect page."""
        self.add_sidebar_item(
            render_database_sidebar,
            on_connect=self._on_database_connect,
            on_disconnect=self._on_database_disconnect
        )

        # Neo4j container management is currently disabled
        # self.add_sidebar_item(
        #     render_neo4j_container_sidebar,
        #     on_start=self._on_neo4j_start,
        #     on_stop=self._on_neo4j_stop
        # )

        # Jupyter and NeoDash functionality is not yet implemented
        # self.add_sidebar_item(
        #     render_jupyter_sidebar,
        #     on_start=self._on_jupyter_start,
        #     on_stop=self._on_jupyter_stop
        # )
        # 
        # self.add_sidebar_item(
        #     render_neodash_sidebar,
        #     on_start=self._on_neodash_start,
        #     on_stop=self._on_neodash_stop
        # )

    def _on_database_connect(self, uri: str, username: str, password: str, database: str):
        """
        Handle database connection.

        Args:
            uri: The URI of the Neo4j server.
            username: The username for authentication.
            password: The password for authentication.
            database: The name of the database to connect to.
        """
        try:
            # Update connection details
            self.db_manager.uri = uri
            self.db_manager.user = username
            self.db_manager.password = password
            self.db_manager.database = database

            # Connect to the database
            self.db_manager._connect()

            # Update session state
            st.session_state["connected"] = True
            st.session_state["neo4j_uri"] = uri
            st.session_state["neo4j_user"] = username
            st.session_state["neo4j_password"] = password
            st.session_state["neo4j_database"] = database

            st.success(f"Connected to Neo4j database at {uri}")
        except Exception as e:
            st.error(f"Failed to connect to Neo4j: {e}")

    def _on_database_disconnect(self):
        """Handle database disconnection."""
        try:
            # Close the connection
            self.db_manager.close()

            # Update session state
            st.session_state["connected"] = False

            st.success("Disconnected from Neo4j database")
        except Exception as e:
            st.error(f"Failed to disconnect from Neo4j: {e}")

    def _on_neo4j_start(self):
        """Handle Neo4j container start."""
        try:
            # Get version from session state
            version = st.session_state.get("neo4j_version", "latest")

            # Start the container
            success = self.db_manager.start_container(version)

            if success:
                st.session_state["container_status"] = "running"
                st.success("Neo4j container started successfully")
            else:
                st.error("Failed to start Neo4j container")
        except Exception as e:
            st.error(f"Error starting Neo4j container: {e}")

    def _on_neo4j_stop(self):
        """Handle Neo4j container stop."""
        try:
            # Stop the container
            success = self.db_manager.stop_container()

            if success:
                st.session_state["container_status"] = "stopped"
                st.success("Neo4j container stopped successfully")
            else:
                st.error("Failed to stop Neo4j container")
        except Exception as e:
            st.error(f"Error stopping Neo4j container: {e}")

    def _on_jupyter_start(self, port: int):
        """
        Handle Jupyter Lab start.

        Args:
            port: The port to use for Jupyter Lab.
        """
        try:
            # This is a placeholder for actual Jupyter Lab start logic
            # In a real implementation, this would start a Jupyter Lab container

            # Update session state
            st.session_state["jupyter_url"] = f"http://localhost:{port}"
            st.session_state["jupyter_token"] = "demo-token"

            st.success(f"Jupyter Lab started at http://localhost:{port}")
        except Exception as e:
            st.error(f"Error starting Jupyter Lab: {e}")

    def _on_jupyter_stop(self):
        """Handle Jupyter Lab stop."""
        try:
            # This is a placeholder for actual Jupyter Lab stop logic
            # In a real implementation, this would stop the Jupyter Lab container

            # Update session state
            st.session_state["jupyter_token"] = ""

            st.success("Jupyter Lab stopped")
        except Exception as e:
            st.error(f"Error stopping Jupyter Lab: {e}")

    def _on_neodash_start(self, port: int):
        """
        Handle NeoDash start.

        Args:
            port: The port to use for NeoDash.
        """
        try:
            # This is a placeholder for actual NeoDash start logic
            # In a real implementation, this would start a NeoDash container

            # Update session state
            st.session_state["neodash_url"] = f"http://localhost:{port}"

            st.success(f"NeoDash started at http://localhost:{port}")
        except Exception as e:
            st.error(f"Error starting NeoDash: {e}")

    def _on_neodash_stop(self):
        """Handle NeoDash stop."""
        try:
            # This is a placeholder for actual NeoDash stop logic
            # In a real implementation, this would stop the NeoDash container

            st.success("NeoDash stopped")
        except Exception as e:
            st.error(f"Error stopping NeoDash: {e}")

    def render_content(self) -> None:
        """Render the Connect page content."""
        st.write("Connect to data sources and manage your database connections.")

        # Database connection section
        st.header("Database Connection")
        if st.session_state.get("connected", False):
            st.success(f"Connected to Neo4j database at {st.session_state.get('neo4j_uri', '')}")

            # Display database information
            if self.db_manager.is_connected():
                try:
                    # Get database information
                    with st.expander("Database Information"):
                        info = self.db_manager.execute_query("CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition")
                        if info:
                            st.write(f"Name: {info[0]['name']}")
                            st.write(f"Version: {info[0]['versions'][0]}")
                            st.write(f"Edition: {info[0]['edition']}")

                        # Get database size
                        size = self.db_manager.execute_query("CALL dbms.database.size() YIELD database, totalSize RETURN database, totalSize")
                        if size:
                            st.write(f"Database: {size[0]['database']}")
                            st.write(f"Size: {size[0]['totalSize']}")
                except Exception as e:
                    st.error(f"Error fetching database information: {e}")
        else:
            st.info("Not connected to a Neo4j database. Use the sidebar to connect.")

        # Information about disabled features
        st.header("Additional Features")
        st.info("""
        The following features are currently disabled or under development:

        - **Neo4j Container Management**: Direct container management is temporarily disabled.
        - **Jupyter Lab Integration**: This feature is still under development.
        - **NeoDash Integration**: This feature is still under development.

        Please check back in future updates for these features.
        """)

def render_connect_page():
    """Render the Connect page."""
    page = ConnectPage()
    page.render()
