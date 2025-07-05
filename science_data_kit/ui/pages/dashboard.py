"""
Dashboard Page Module for Science Data Kit

This module provides the Dashboard page for the Science Data Kit application.
The Dashboard page serves as the main entry point and provides an overview of the application's features.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Callable
import matplotlib.pyplot as plt
import io
import base64

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.sidebar import render_database_sidebar
from science_data_kit.core.db.db_manager import db_manager
from science_data_kit.ui.components.responsive_design import (
    create_responsive_columns,
    create_responsive_container,
    create_responsive_tabs
)

class DashboardPage(BasePage):
    """
    Dashboard page serving as the main entry point for the application.

    This page provides:
    - An overview of the application's features
    - Quick access to common tasks
    - Status information about connected services
    - Data visualization components
    """

    def __init__(self):
        """Initialize the Dashboard page."""
        super().__init__("Dashboard", "📊")
        self._setup_sidebar()
        self.db_manager = db_manager

        # Initialize session state variables
        if "connected_services" not in st.session_state:
            st.session_state["connected_services"] = {
                "neo4j": False,
                "jupyter": False,
                "neodash": False,
                "msgraph": False,
                "dropbox": False,
                "google_drive": False
            }

    def _setup_sidebar(self):
        """Set up the sidebar items for the Dashboard page."""
        self.add_sidebar_item(
            render_database_sidebar,
            on_connect=self._on_database_connect,
            on_disconnect=self._on_database_disconnect
        )

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
            st.session_state["connected_services"]["neo4j"] = True

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
            st.session_state["connected_services"]["neo4j"] = False

            st.success("Disconnected from Neo4j database")
        except Exception as e:
            st.error(f"Failed to disconnect from Neo4j: {e}")

    def _create_service_status_chart(self) -> str:
        """
        Create a visualization of the service status.

        Returns:
            Base64-encoded image data for the visualization.
        """
        try:
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 5))

            # Service status data
            services = list(st.session_state["connected_services"].keys())
            status = [1 if st.session_state["connected_services"][s] else 0 for s in services]

            # Format service names for display
            display_names = [s.replace('_', ' ').title() for s in services]

            # Create bar chart
            bars = ax.bar(display_names, status, color=['green' if s else 'red' for s in status])

            # Add labels
            ax.set_ylim(0, 1.2)
            ax.set_yticks([0, 1])
            ax.set_yticklabels(['Disconnected', 'Connected'])
            ax.set_title('Service Connection Status')

            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                label = 'Connected' if height > 0 else 'Disconnected'
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        label, ha='center', va='bottom', rotation=90, fontsize=8)

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha='right')

            # Adjust layout
            plt.tight_layout()

            # Save figure to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            plt.close()

            # Convert to base64
            buf.seek(0)
            img_data = base64.b64encode(buf.read()).decode("utf-8")

            return img_data
        except Exception as e:
            st.error(f"Error creating service status chart: {e}")
            return ""

    def _render_action_card(self, title: str, description: str, button_text: str, button_key: str, target_page: str) -> None:
        """
        Render an action card with a title, description, and button.

        Args:
            title: The title of the action card
            description: The description of the action card
            button_text: The text to display on the button
            button_key: The key for the button
            target_page: The page to navigate to when the button is clicked
        """
        st.subheader(title)
        st.write(description)
        if st.button(button_text, key=button_key):
            st.switch_page(target_page)

    def _create_sample_data_visualization(self) -> str:
        """
        Create a sample data visualization.

        Returns:
            Base64-encoded image data for the visualization.
        """
        try:
            # Create sample data
            categories = ['Data Sources', 'Analysis', 'Visualization', 'Integration']
            values = [85, 70, 60, 40]

            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))

            # Create bar chart
            bars = ax.bar(categories, values, color='skyblue')

            # Add labels
            ax.set_ylim(0, 100)
            ax.set_ylabel('Completion (%)')
            ax.set_title('Project Progress by Category')

            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height}%', ha='center', va='bottom')

            # Adjust layout
            plt.tight_layout()

            # Save figure to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            plt.close()

            # Convert to base64
            buf.seek(0)
            img_data = base64.b64encode(buf.read()).decode("utf-8")

            return img_data
        except Exception as e:
            st.error(f"Error creating sample data visualization: {e}")
            return ""

    def render_content(self) -> None:
        """Render the Dashboard page content."""
        st.write("Welcome to the Science Data Kit! This dashboard provides an overview of the application's features and status.")

        # Service Status Section
        st.header("Service Status")

        # Display service status chart in a responsive container
        def render_service_status():
            img_data = self._create_service_status_chart()
            if img_data:
                st.image(f"data:image/png;base64,{img_data}", use_column_width=True)

        create_responsive_container(render_service_status)

        # Quick Actions Section
        st.header("Quick Actions")

        # Create a 2x2 grid of action cards using responsive columns
        # First row
        col1, col2 = create_responsive_columns(2)

        with col1:
            with create_responsive_container(lambda: self._render_action_card(
                "🔌 Connect to Data Sources",
                "Connect to various data sources including Neo4j, Microsoft Graph API, Dropbox, and Google Drive.",
                "Go to Connections", 
                "goto_connect", 
                "pages/connect.py"
            )):
                pass

        with col2:
            with create_responsive_container(lambda: self._render_action_card(
                "🔍 Explore Data",
                "Visualize and analyze your data from the knowledge graph.",
                "Go to Explore", 
                "goto_explore", 
                "pages/explore.py"
            )):
                pass

        # Second row
        col3, col4 = create_responsive_columns(2)

        with col3:
            with create_responsive_container(lambda: self._render_action_card(
                "🧬 Manage Ontologies",
                "Work with ontologies to structure your knowledge graph.",
                "Go to Ontology", 
                "goto_ontology", 
                "pages/ontology.py"
            )):
                pass

        with col4:
            with create_responsive_container(lambda: self._render_action_card(
                "💬 Chat with Your Data",
                "Use natural language to query and interact with your data.",
                "Go to Chat", 
                "goto_chat", 
                "pages/chat.py"
            )):
                pass

        # Feature Categories Section
        st.header("Feature Categories")

        # Define tab content functions
        def render_data_sources_tab():
            st.subheader("Available Data Sources")

            # Create a table of data sources
            data_sources = {
                "Source": ["Neo4j", "Microsoft Graph API", "Dropbox", "Google Drive", "Local Storage"],
                "Status": ["Available", "Available", "Available", "Available", "Available"],
                "Description": [
                    "Graph database for storing and querying connected data",
                    "Access Microsoft 365 services including Teams, SharePoint, and OneDrive",
                    "Access files stored in Dropbox",
                    "Access files stored in Google Drive, including Google Sheets",
                    "Access files stored on the local file system"
                ]
            }

            st.dataframe(pd.DataFrame(data_sources), use_container_width=True)

        def render_analysis_tab():
            st.subheader("Analysis Capabilities")

            # Create a table of analysis capabilities
            analysis_capabilities = {
                "Capability": ["Query Execution", "Data Validation", "Schema Analysis", "Relationship Analysis", "Data Export"],
                "Status": ["Available", "Available", "Available", "Available", "Available"],
                "Description": [
                    "Execute Cypher queries against Neo4j database",
                    "Validate data against defined schemas and rules",
                    "Analyze and visualize database schema",
                    "Analyze relationships between entities",
                    "Export data to various formats (CSV, Excel, JSON)"
                ]
            }

            st.dataframe(pd.DataFrame(analysis_capabilities), use_container_width=True)

        def render_visualization_tab():
            st.subheader("Visualization Components")

            # Create a table of visualization components
            visualization_components = {
                "Component": ["Schema Visualization", "Basic Data Charts", "Simple Network Graphs", "NeoDash Integration", "Advanced Dashboards"],
                "Status": ["Available", "Available", "Available", "Available", "Available via NeoDash"],
                "Description": [
                    "Visualize database schema as a network graph",
                    "Create basic bar, line, and scatter charts from query results",
                    "Visualize data as simple network graphs",
                    "Integration with NeoDash for creating advanced dashboards",
                    "Create complex, interactive dashboards with NeoDash"
                ]
            }

            st.dataframe(pd.DataFrame(visualization_components), use_container_width=True)

            # Add explanation about SDK vs NeoDash visualization capabilities
            st.info("""
            **SDK Dashboard vs NeoDash**

            The Science Data Kit dashboard provides basic visualization capabilities for quick insights, 
            while NeoDash offers more advanced, customizable dashboards for complex data exploration.

            - **Use SDK Dashboard for**: System overview, basic charts, quick insights
            - **Use NeoDash for**: Custom dashboards, complex visualizations, interactive exploration, sharing dashboards
            """)

        def render_integration_tab():
            st.subheader("Integration Capabilities")

            # Create a table of integration capabilities
            integration_capabilities = {
                "Capability": ["Jupyter Notebook", "NExtSEEK", "FAIRDOM-Hub", "API Access", "Command-Line Interface"],
                "Status": ["Available", "Planned", "Planned", "Available", "Available"],
                "Description": [
                    "Integration with Jupyter notebooks for data analysis",
                    "Integration with NExtSEEK platform",
                    "Integration with FAIRDOM-Hub platform",
                    "Access SDK functionality through API",
                    "Access SDK functionality through command-line interface"
                ]
            }

            st.dataframe(pd.DataFrame(integration_capabilities), use_container_width=True)

        # Create responsive tabs for different feature categories
        create_responsive_tabs(
            ["Data Sources", "Analysis", "Visualization", "Integration"],
            [render_data_sources_tab, render_analysis_tab, render_visualization_tab, render_integration_tab]
        )

        # Data Visualization Section
        st.header("Project Progress")

        # Display sample data visualization in a responsive container
        def render_project_progress():
            img_data = self._create_sample_data_visualization()
            if img_data:
                st.image(f"data:image/png;base64,{img_data}", use_column_width=True)

        create_responsive_container(render_project_progress)

        # Recent Activity Section
        st.header("Recent Activity")

        # Create a table of recent activities in a responsive container
        def render_recent_activities():
            recent_activities = {
                "Date": ["2025-07-20", "2025-07-19", "2025-07-18", "2025-07-17", "2025-07-16"],
                "Activity": [
                    "Implemented data validation rules engine",
                    "Implemented data migration tools",
                    "Updated roadmap to prioritize data modeling enhancements",
                    "Implemented command-line interface",
                    "Implemented client-side caching"
                ],
                "Category": ["Data Modeling", "Data Modeling", "Planning", "API", "API"]
            }

            st.dataframe(pd.DataFrame(recent_activities), use_container_width=True)

        create_responsive_container(render_recent_activities)

def render_dashboard_page():
    """Render the Dashboard page."""
    page = DashboardPage()
    page.render()
