"""
Server Page Module for Science Data Kit

This module provides the Server page for the Science Data Kit application.
The Server page handles server management, connections to data sources, and infrastructure management.
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.sidebar import render_database_sidebar, render_neo4j_container_sidebar
from science_data_kit.ui.components.sidebar import render_jupyter_sidebar, render_neodash_sidebar
from science_data_kit.core.db.db_manager import Neo4jManager, db_manager

class ServerPage(BasePage):
    """
    Server page for managing infrastructure and connections to data sources.

    This page provides functionality for:
    - Managing containerized servers (Neo4j, Jupyter, NeoDash, Ollama)
    - Connecting to databases (Neo4j, PostgreSQL, etc.)
    - Managing filesystem integrations
    - Starting and stopping services
    """

    def __init__(self):
        """Initialize the Server page."""
        super().__init__("Server", "🖥️")
        self._setup_sidebar()
        self.db_manager = db_manager

    def _setup_sidebar(self):
        """Set up the sidebar items for the Server page."""
        self.add_sidebar_item(
            render_database_sidebar,
            on_connect=self._on_database_connect,
            on_disconnect=self._on_database_disconnect
        )

        # Re-enable Neo4j container management
        self.add_sidebar_item(
            render_neo4j_container_sidebar,
            on_start=self._on_neo4j_start,
            on_stop=self._on_neo4j_stop
        )

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

    def _on_database_connect(self, uri: str, username: str, password: str, database: str, connection_name: str):
        """
        Handle database connection.

        Args:
            uri: The URI of the Neo4j server.
            username: The username for authentication.
            password: The password for authentication.
            database: The name of the database to connect to.
            connection_name: The name of the connection.
        """
        try:
            # Update connection details
            self.db_manager.uri = uri
            self.db_manager.user = username
            self.db_manager.password = password
            self.db_manager.database = database

            # Connect to the database with the specified connection name
            connection_success = self.db_manager._connect(connection_name)

            if not connection_success:
                st.error(f"Failed to connect to Neo4j: {self.db_manager._connection_error}")
                return

            # Update session state
            st.session_state["active_connection"] = connection_name

            # Store connection details in session state
            if "db_connections" not in st.session_state:
                st.session_state["db_connections"] = {}

            # Update connection statuses in session state based on backend state
            self._sync_connection_statuses()

            # Update or create the connection in session state
            st.session_state["db_connections"][connection_name] = {
                "uri": uri,
                "user": username,
                "password": password,
                "database": database,
                "connected": True
            }

            st.success(f"Connected to Neo4j database '{connection_name}' at {uri}")
        except Exception as e:
            st.error(f"Failed to connect to Neo4j: {e}")

    def _sync_connection_statuses(self):
        """
        Synchronize connection statuses in session state with backend state.

        This ensures that the UI accurately reflects the actual connection status.
        """
        if "db_connections" not in st.session_state:
            return

        # Get all connection names from the backend
        backend_connections = set(self.db_manager.get_connection_names())

        # Update connection statuses in session state
        for name, details in st.session_state["db_connections"].items():
            # Check if the connection exists in the backend
            if name in backend_connections:
                # Check if the connection is actually connected
                is_connected = self.db_manager.is_connected(name)
                details["connected"] = is_connected
            else:
                # Connection doesn't exist in the backend
                details["connected"] = False

    def _on_database_disconnect(self):
        """Handle database disconnection."""
        try:
            # Get the active connection name
            active_connection = st.session_state.get("active_connection")

            # Close the connection
            self.db_manager.close(active_connection)

            # Update connection statuses in session state
            self._sync_connection_statuses()

            st.session_state["active_connection"] = None

            st.success(f"Disconnected from Neo4j database")
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
        """Render the Server page content."""
        st.write("Manage your servers and connect to data sources.")

        # Server status overview
        st.header("Server Status")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Database Servers")

            # Neo4j status
            if st.session_state.get("container_status", "stopped") == "running":
                st.success("Neo4j: Running")
            else:
                st.warning("Neo4j: Stopped")

            # PostgreSQL status (placeholder for future implementation)
            st.info("PostgreSQL: Not configured")

        with col2:
            st.subheader("Analysis Servers")

            # Jupyter status (placeholder)
            st.warning("Jupyter Lab: Not running")

            # NeoDash status (placeholder)
            st.warning("NeoDash: Not running")

            # Ollama status (placeholder)
            st.info("Ollama: Not configured")

        # Database connection section
        st.header("Database Connections")

        # Synchronize connection statuses with backend state
        self._sync_connection_statuses()

        # Get all connections from session state
        connections = st.session_state.get("db_connections", {})
        active_connection = st.session_state.get("active_connection")

        if not connections:
            st.info("No database connections configured. Use the sidebar to create a connection.")
        else:
            # Display a table of all connections
            connection_data = []
            for name, details in connections.items():
                # Show green status for all connected connections, not just the active one
                status = "🟢 Connected" if details.get("connected", False) else "⚫ Disconnected"
                # Add an indicator for the active connection
                if name == active_connection:
                    status += " (Active)"
                connection_data.append({
                    "Name": name,
                    "Status": status,
                    "URI": details.get("uri", ""),
                    "Database": details.get("database", "")
                })

            st.dataframe(connection_data)

            # Display information about the active connection
            if active_connection and self.db_manager.is_connected(active_connection):
                st.subheader(f"Active Connection: {active_connection}")
                st.success(f"Connected to Neo4j database at {connections[active_connection].get('uri', '')}")

                try:
                    # Get database information
                    with st.expander("Database Information", expanded=True):
                        info = self.db_manager.execute_query(
                            "CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition",
                            connection_name=active_connection
                        )
                        if info:
                            st.write(f"Name: {info[0]['name']}")
                            st.write(f"Version: {info[0]['versions'][0]}")
                            st.write(f"Edition: {info[0]['edition']}")

                        # Get database size
                        try:
                            size = self.db_manager.execute_query(
                                "CALL dbms.database.size() YIELD database, totalSize RETURN database, totalSize",
                                connection_name=active_connection
                            )
                            if size:
                                st.write(f"Database: {size[0]['database']}")
                                st.write(f"Size: {size[0]['totalSize']}")
                        except Exception as e:
                            # Handle the case when dbms.database.size() procedure is not available
                            if "Neo.ClientError.Procedure.ProcedureNotFound" in str(e):
                                st.info("Database size information not available in this Neo4j version")
                            else:
                                # Re-raise if it's a different error
                                raise e

                        # Get node and relationship counts
                        counts = self.db_manager.execute_query(
                            "MATCH (n) RETURN count(n) as nodes",
                            connection_name=active_connection
                        )
                        if counts:
                            st.write(f"Nodes: {counts[0]['nodes']}")

                        rel_counts = self.db_manager.execute_query(
                            "MATCH ()-[r]->() RETURN count(r) as relationships",
                            connection_name=active_connection
                        )
                        if rel_counts:
                            st.write(f"Relationships: {rel_counts[0]['relationships']}")
                except Exception as e:
                    st.error(f"Error fetching database information: {e}")
            elif not active_connection:
                st.info("No active connection. Use the sidebar to connect to a database.")

        # Information about features in development
        st.header("Features in Development")
        st.info("""
        The following features are currently under development:

        - **Jupyter Lab Integration**: Will be available in a future update.
        - **NeoDash Integration**: Will be available in a future update.
        - **Ollama Integration**: Will be available in a future update.
        - **PostgreSQL Connection**: Will be available in a future update.
        - **Filesystem Integrations**: Will be available in a future update.

        Neo4j container management is now available in the sidebar.
        """)

def render_server_page():
    """Render the Server page."""
    page = ServerPage()
    page.render()
