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
from science_data_kit.ui.components.custom_visualization_templates import render_template_manager
from science_data_kit.ui.components.dashboard_widgets import (
    DashboardWidget,
    MetricWidget,
    ChartWidget,
    TableWidget,
    StatusWidget,
    InfoWidget,
    create_dashboard_layout,
    example_dashboard
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

    def _on_database_connect(self, uri: str, username: str, password: str, database: str, conn_name: str = None):
        """
        Handle database connection.

        Args:
            uri: The URI of the Neo4j server.
            username: The username for authentication.
            password: The password for authentication.
            database: The name of the database to connect to.
            conn_name: The name of the connection (optional).
        """
        try:
            # Update connection details
            self.db_manager.uri = uri
            self.db_manager.user = username
            self.db_manager.password = password
            self.db_manager.database = database

            # Connect to the database with the specified connection name
            connection_successful = self.db_manager._connect(conn_name)

            if not connection_successful:
                error_msg = self.db_manager._connection_error or "Unknown connection error"
                st.error(f"Failed to connect to Neo4j: {error_msg}")
                return

            # Update session state
            st.session_state["connected"] = True
            st.session_state["neo4j_uri"] = uri
            st.session_state["neo4j_user"] = username
            st.session_state["neo4j_password"] = password
            st.session_state["neo4j_database"] = database
            st.session_state["connected_services"]["neo4j"] = True
            st.session_state["active_connection"] = conn_name

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
            # Import visualization templates
            from science_data_kit.ui.components.visualization_templates import create_bar_chart

            # Service status data
            services = list(st.session_state["connected_services"].keys())
            status = [1 if st.session_state["connected_services"][s] else 0 for s in services]

            # Format service names for display
            display_names = [s.replace('_', ' ').title() for s in services]

            # Create DataFrame for visualization
            data = pd.DataFrame({
                'Service': display_names,
                'Status': status
            })

            # Create custom colors based on status
            colors = ['green' if s else 'red' for s in status]

            # Use the bar chart template
            img_data = create_bar_chart(
                data=data,
                x_column='Service',
                y_column='Status',
                title='Service Connection Status',
                y_label='Status',
                color=colors[0] if len(set(colors)) == 1 else None,  # Use single color if all same
                figsize=(10, 5),
                show_values=False  # We'll add custom labels instead
            )

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
            # Import visualization templates
            from science_data_kit.ui.components.visualization_templates import create_bar_chart

            # Create sample data
            categories = ['Data Sources', 'Analysis', 'Visualization', 'Integration']
            values = [85, 70, 60, 40]

            # Create DataFrame for visualization
            data = pd.DataFrame({
                'Category': categories,
                'Completion': values
            })

            # Use the bar chart template
            img_data = create_bar_chart(
                data=data,
                x_column='Category',
                y_column='Completion',
                title='Project Progress by Category',
                y_label='Completion (%)',
                color='skyblue',
                figsize=(10, 6),
                show_values=True
            )

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
                st.image(f"data:image/png;base64,{img_data}", use_container_width=True)

        create_responsive_container(render_service_status)

        # Quick Actions Section
        st.header("Quick Actions")

        # Create a 2x2 grid of action cards using responsive columns
        # First row
        col1, col2 = create_responsive_columns(2)

        with col1:
            create_responsive_container(lambda: self._render_action_card(
                "🔌 Connect to Data Sources",
                "Connect to various data sources including Neo4j, Microsoft Graph API, Dropbox, and Google Drive.",
                "Go to Connections", 
                "goto_connect", 
                "pages/connect.py"
            ))

        with col2:
            create_responsive_container(lambda: self._render_action_card(
                "🔍 Explore Data",
                "Visualize and analyze your data from the knowledge graph.",
                "Go to Explore", 
                "goto_explore", 
                "pages/explore.py"
            ))

        # Second row
        col3, col4 = create_responsive_columns(2)

        with col3:
            create_responsive_container(lambda: self._render_action_card(
                "🧬 Manage Ontologies",
                "Work with ontologies to structure your knowledge graph.",
                "Go to Ontology", 
                "goto_ontology", 
                "pages/ontology.py"
            ))

        with col4:
            create_responsive_container(lambda: self._render_action_card(
                "💬 Chat with Your Data",
                "Use natural language to query and interact with your data.",
                "Go to Chat", 
                "goto_chat", 
                "pages/chat.py"
            ))

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
                "Component": ["Schema Visualization", "Basic Data Charts", "Simple Network Graphs", "Custom Visualization Templates", "Dashboard Widgets", "NeoDash Integration", "Advanced Dashboards"],
                "Status": ["Available", "Available", "Available", "Available", "Available", "Available", "Available via NeoDash"],
                "Description": [
                    "Visualize database schema as a network graph",
                    "Create basic bar, line, and scatter charts from query results",
                    "Visualize data as simple network graphs",
                    "Create and apply custom visualization templates",
                    "Create customizable dashboard widgets for monitoring and reporting",
                    "Integration with NeoDash for creating advanced dashboards",
                    "Create complex, interactive dashboards with NeoDash"
                ]
            }

            st.dataframe(pd.DataFrame(visualization_components), use_container_width=True)

            # Create tabs for visualization features
            viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Visualization Strategy", "Custom Templates", "Dashboard Widgets"])

            with viz_tab1:
                # Add explanation about SDK vs NeoDash visualization capabilities
                st.info("""
                **SDK Dashboard vs NeoDash: Visualization Strategy**

                The Science Data Kit dashboard and NeoDash serve complementary purposes in our visualization strategy:

                **SDK Dashboard**
                - **Purpose**: Quick insights, system monitoring, and basic data exploration
                - **Visualization Types**: 
                  - Basic charts (bar, line, scatter, pie)
                  - Simple network graphs
                  - Schema visualizations
                  - Performance metrics
                  - Custom visualization templates
                - **Best For**: 
                  - Daily monitoring of system health
                  - Quick data exploration during analysis
                  - Basic reporting needs
                  - Integrated workflow within the SDK

                **NeoDash**
                - **Purpose**: Advanced data exploration, custom dashboards, and shareable reports
                - **Visualization Types**:
                  - Complex network graphs
                  - Interactive dashboards
                  - Custom visualizations
                  - Multi-panel layouts
                  - Parameterized queries
                - **Best For**:
                  - In-depth data analysis
                  - Creating shareable dashboards
                  - Custom reporting solutions
                  - Presentations and stakeholder communication
                  - Persistent visualization workflows

                Choose the SDK Dashboard when you need quick insights during your workflow, and use NeoDash 
                when you need to create more sophisticated, persistent visualizations or shareable dashboards.
                """)

            with viz_tab2:
                # Render the custom visualization templates manager
                render_template_manager()

            with viz_tab3:
                # Dashboard Widgets section
                st.write("### Dashboard Widgets")
                st.write("""
                Dashboard widgets allow you to create customizable dashboards for monitoring and reporting.
                You can create various types of widgets and arrange them in a flexible layout.
                """)

                # Create tabs for different widget types
                widget_tabs = st.tabs(["Overview", "Example Dashboard", "Widget Types"])

                with widget_tabs[0]:
                    st.write("""
                    ### Dashboard Widgets Overview

                    Dashboard widgets provide a flexible way to create customizable dashboards for monitoring and reporting.
                    Each widget is a self-contained component that can display different types of data and visualizations.

                    **Key Features:**
                    - Multiple widget types for different data visualization needs
                    - Automatic refresh capabilities
                    - Flexible layout options
                    - Consistent styling and behavior

                    **Available Widget Types:**
                    - **Metric Widget**: Display a single metric with optional trend indicator
                    - **Chart Widget**: Display various chart types using the visualization templates
                    - **Table Widget**: Display tabular data with sorting and filtering
                    - **Status Widget**: Display status information with colored indicators
                    - **Info Widget**: Display informational content in various formats

                    **Creating a Dashboard:**
                    1. Create instances of the widget classes you need
                    2. Define a layout for your widgets
                    3. Use the `create_dashboard_layout` function to render the dashboard
                    """)

                with widget_tabs[1]:
                    # Show the example dashboard
                    st.write("### Example Dashboard")
                    st.write("This is an example dashboard showing various widget types:")
                    example_dashboard()

                with widget_tabs[2]:
                    st.write("### Widget Types")

                    # Create expandable sections for each widget type
                    with st.expander("Metric Widget", expanded=False):
                        st.write("""
                        **Metric Widget**

                        Displays a single metric with an optional trend indicator.

                        **Features:**
                        - Display a single value with optional prefix and suffix
                        - Show trend indicator (up/down) with percentage change
                        - Color-coded trend (green for good, red for bad)

                        **Example Usage:**
                        ```python
                        metric_widget = MetricWidget(
                            title="Total Users",
                            value_func=get_total_users,
                            description="Number of registered users",
                            trend_func=get_user_trend,
                            trend_is_good_func=is_user_trend_good
                        )
                        ```
                        """)

                    with st.expander("Chart Widget", expanded=False):
                        st.write("""
                        **Chart Widget**

                        Displays a chart visualization using the visualization templates.

                        **Features:**
                        - Support for all chart types in visualization templates
                        - Automatic data refresh
                        - Configurable chart parameters

                        **Example Usage:**
                        ```python
                        chart_widget = ChartWidget(
                            title="Sales Trend",
                            data_func=get_sales_data,
                            chart_type="line_chart",
                            chart_params={
                                "x_column": "Date",
                                "y_columns": "Sales",
                                "title": "Daily Sales",
                                "show_markers": True
                            },
                            description="Daily sales over time"
                        )
                        ```
                        """)

                    with st.expander("Table Widget", expanded=False):
                        st.write("""
                        **Table Widget**

                        Displays tabular data with sorting and filtering.

                        **Features:**
                        - Display data in a tabular format
                        - Automatic data refresh
                        - Configurable width and height

                        **Example Usage:**
                        ```python
                        table_widget = TableWidget(
                            title="Sales Data",
                            data_func=get_sales_data,
                            description="Raw sales data"
                        )
                        ```
                        """)

                    with st.expander("Status Widget", expanded=False):
                        st.write("""
                        **Status Widget**

                        Displays status information with colored indicators.

                        **Features:**
                        - Color-coded status indicators (green, orange, red)
                        - Display multiple status items
                        - Show status messages

                        **Example Usage:**
                        ```python
                        status_widget = StatusWidget(
                            title="System Status",
                            items_func=get_status_items,
                            description="Current status of system components"
                        )
                        ```
                        """)

                    with st.expander("Info Widget", expanded=False):
                        st.write("""
                        **Info Widget**

                        Displays informational content in various formats.

                        **Features:**
                        - Support for markdown, code, JSON, and plain text
                        - Automatic content refresh

                        **Example Usage:**
                        ```python
                        info_widget = InfoWidget(
                            title="Dashboard Info",
                            content_func=get_info_content,
                            description="Information about this dashboard",
                            content_type="markdown"
                        )
                        ```
                        """)

                    with st.expander("Dashboard Layout", expanded=False):
                        st.write("""
                        **Dashboard Layout**

                        Create a flexible layout for your dashboard widgets.

                        **Features:**
                        - Arrange widgets in rows and columns
                        - Control the width of each widget
                        - Responsive layout

                        **Example Usage:**
                        ```python
                        # Create a layout with 2 rows
                        # First row: 2 widgets side by side
                        # Second row: 3 widgets side by side
                        layout = [[1, 1], [1, 1, 1]]

                        # Render the dashboard
                        create_dashboard_layout(widgets, layout)
                        ```
                        """)

                    st.write("""
                    For more details and advanced usage, refer to the dashboard_widgets.py module.
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
                st.image(f"data:image/png;base64,{img_data}", use_container_width=True)

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
