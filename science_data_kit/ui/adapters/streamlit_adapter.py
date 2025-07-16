"""
Streamlit Adapter Module for Science Data Kit

This module provides Streamlit-specific adapters for the core page classes.
It bridges between the framework-independent core functionality and the Streamlit UI.
"""

import streamlit as st
from typing import Type, Dict, Any, List, Optional
import os
import datetime

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import PageData, DashboardPageData, FileExplorerPageData, ConnectPageData, ExplorePageData
from science_data_kit.core.pages.dashboard import DashboardPage
from science_data_kit.core.pages.file_browser import FileBrowserPage
from science_data_kit.core.pages.connect import ConnectPage
from science_data_kit.core.pages.explore import ExplorePage
from science_data_kit.ui.components.dashboard_widgets import (
    DashboardWidget,
    MetricWidget,
    ChartWidget,
    TableWidget,
    StatusWidget,
    InfoWidget,
    create_dashboard_layout
)
from science_data_kit.ui.components.responsive_design import (
    create_responsive_columns,
    create_responsive_container,
    create_responsive_tabs
)

def render_page(page_instance: BasePage) -> None:
    """
    Render a page using Streamlit components.

    Args:
        page_instance: An instance of a BasePage subclass.
    """
    # Get the page data
    page_data = page_instance.get_page_data()

    # Render the page based on the type of page data
    if isinstance(page_data, DashboardPageData):
        _render_dashboard_page(page_data)
    elif isinstance(page_data, FileExplorerPageData):
        _render_file_explorer_page(page_data)
    elif isinstance(page_data, ConnectPageData):
        _render_connect_page(page_data)
    elif isinstance(page_data, ExplorePageData):
        _render_explore_page(page_data)
    else:
        # Generic rendering for other page types
        st.title(page_data.title)
        st.write("This page type doesn't have a specific renderer yet.")

def _render_dashboard_page(page_data: DashboardPageData) -> None:
    """
    Render a dashboard page using Streamlit components.

    Args:
        page_data: The dashboard page data to render.
    """
    # Set the page title
    st.title(page_data.title)

    # Welcome message
    st.write("Welcome to the Science Data Kit! This dashboard provides an overview of the application's features and status.")

    # Service Status Section
    st.header("Service Status")

    # Create status widgets
    status_widgets = []
    for item in page_data.status_items:
        status_widgets.append(
            StatusWidget(
                title=item["name"],
                items_func=lambda i=item: [i],
                description=f"Status of {item['name']}"
            )
        )

    # Create a layout for status widgets
    if status_widgets:
        create_dashboard_layout(status_widgets, [[1] * min(3, len(status_widgets))])

    # Quick Actions Section
    st.header("Quick Actions")

    # Create a 2x2 grid of action cards using responsive columns
    # First row
    col1, col2 = create_responsive_columns(2)

    with col1:
        create_responsive_container(lambda: _render_action_card(
            "🔌 Connect to Data Sources",
            "Connect to various data sources including Neo4j, Microsoft Graph API, Dropbox, and Google Drive.",
            "Go to Connections", 
            "goto_connect", 
            "pages/connect.py"
        ))

    with col2:
        create_responsive_container(lambda: _render_action_card(
            "🔍 Explore Data",
            "Visualize and analyze your data from the knowledge graph.",
            "Go to Explore", 
            "goto_explore", 
            "pages/explore.py"
        ))

    # Second row
    col3, col4 = create_responsive_columns(2)

    with col3:
        create_responsive_container(lambda: _render_action_card(
            "🧬 Manage Ontologies",
            "Work with ontologies to structure your knowledge graph.",
            "Go to Ontology", 
            "goto_ontology", 
            "pages/ontology.py"
        ))

    with col4:
        create_responsive_container(lambda: _render_action_card(
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
        if "data_sources" in page_data.feature_categories:
            st.dataframe(page_data.feature_categories["data_sources"], use_container_width=True)

    def render_analysis_tab():
        st.subheader("Analysis Capabilities")
        if "analysis_capabilities" in page_data.feature_categories:
            st.dataframe(page_data.feature_categories["analysis_capabilities"], use_container_width=True)

    def render_visualization_tab():
        st.subheader("Visualization Components")
        if "visualization_components" in page_data.feature_categories:
            st.dataframe(page_data.feature_categories["visualization_components"], use_container_width=True)

    def render_integration_tab():
        st.subheader("Integration Capabilities")
        if "integration_capabilities" in page_data.feature_categories:
            st.dataframe(page_data.feature_categories["integration_capabilities"], use_container_width=True)

    # Create responsive tabs for different feature categories
    create_responsive_tabs(
        ["Data Sources", "Analysis", "Visualization", "Integration"],
        [render_data_sources_tab, render_analysis_tab, render_visualization_tab, render_integration_tab]
    )

    # Charts Section
    if page_data.charts:
        st.header("Project Progress")

        # Create chart widgets
        chart_widgets = []
        for chart in page_data.charts:
            chart_widgets.append(
                ChartWidget(
                    title=chart["title"],
                    data_func=lambda c=chart: c["data"],
                    chart_type=chart["type"],
                    chart_params=chart["options"],
                    description=chart.get("description", "")
                )
            )

        # Create a layout for chart widgets
        if chart_widgets:
            create_dashboard_layout(chart_widgets, [[1] * min(2, len(chart_widgets))])

    # Recent Activity Section
    if page_data.recent_activities:
        st.header("Recent Activity")

        # Create a table widget for recent activities
        table_widget = TableWidget(
            title="Recent Activities",
            data_func=lambda: page_data.recent_activities,
            description="Recent activities in the project"
        )

        # Create a layout for the table widget
        create_dashboard_layout([table_widget], [[1]])

def _render_action_card(title: str, description: str, button_text: str, button_key: str, target_page: str) -> None:
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

def _render_file_explorer_page(page_data: FileExplorerPageData) -> None:
    """
    Render a file explorer page using Streamlit components.

    Args:
        page_data: The file explorer page data to render.
    """
    # Set the page title
    st.title(page_data.title)

    # Create a container for the file browser
    with st.container():
        # Path navigation
        col1, col2 = st.columns([3, 1])

        with col1:
            st.text_input("Current Path", value=page_data.current_path, key="current_path", disabled=True)

        with col2:
            if st.button("Go Up", key="go_up"):
                # This will be handled by the UI page
                st.session_state["file_browser_action"] = "go_up"
                st.rerun()

        # Search/filter
        st.text_input("Filter", value=page_data.filter_pattern or "", key="filter_pattern", 
                     placeholder="Enter filter pattern...")

        # View controls
        col1, col2, col3 = st.columns(3)

        with col1:
            view_mode = st.radio("View Mode", ["list", "grid"], 
                               index=0 if page_data.view_mode == "list" else 1,
                               horizontal=True, key="view_mode")

        with col2:
            sort_by = st.selectbox("Sort By", ["name", "size", "modified"], 
                                 index=["name", "size", "modified"].index(page_data.sort_by),
                                 key="sort_by")

        with col3:
            sort_order = st.radio("Order", ["ascending", "descending"], 
                                index=0 if page_data.sort_order == "ascending" else 1,
                                horizontal=True, key="sort_order")

        # Directory listing
        st.subheader("Directories")

        if not page_data.directories:
            st.info("No directories found.")
        else:
            # Create a grid or list view based on the view mode
            if page_data.view_mode == "grid":
                cols = st.columns(3)
                for i, directory in enumerate(page_data.directories):
                    with cols[i % 3]:
                        if st.button(f"📁 {directory['name']}", key=f"dir_{i}"):
                            # This will be handled by the UI page
                            st.session_state["file_browser_action"] = "navigate"
                            st.session_state["file_browser_target"] = directory["path"]
                            st.rerun()
            else:
                # List view
                for i, directory in enumerate(page_data.directories):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button(f"📁 {directory['name']}", key=f"dir_{i}"):
                            # This will be handled by the UI page
                            st.session_state["file_browser_action"] = "navigate"
                            st.session_state["file_browser_target"] = directory["path"]
                            st.rerun()
                    with col2:
                        st.text(datetime.datetime.fromtimestamp(directory["modified"]).strftime("%Y-%m-%d %H:%M"))

        # File listing
        st.subheader("Files")

        if not page_data.files:
            st.info("No files found.")
        else:
            # Create a grid or list view based on the view mode
            if page_data.view_mode == "grid":
                cols = st.columns(3)
                for i, file in enumerate(page_data.files):
                    with cols[i % 3]:
                        icon = "📄"
                        if file["type"] == "image":
                            icon = "🖼️"
                        elif file["type"] == "document":
                            icon = "📝"
                        elif file["type"] == "code":
                            icon = "💻"

                        if st.button(f"{icon} {file['name']}", key=f"file_{i}"):
                            # This will be handled by the UI page
                            st.session_state["file_browser_action"] = "select"
                            st.session_state["file_browser_target"] = file["path"]
                            st.rerun()
            else:
                # List view with more details
                for i, file in enumerate(page_data.files):
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        icon = "📄"
                        if file["type"] == "image":
                            icon = "🖼️"
                        elif file["type"] == "document":
                            icon = "📝"
                        elif file["type"] == "code":
                            icon = "💻"

                        if st.button(f"{icon} {file['name']}", key=f"file_{i}"):
                            # This will be handled by the UI page
                            st.session_state["file_browser_action"] = "select"
                            st.session_state["file_browser_target"] = file["path"]
                            st.rerun()

                    with col2:
                        # Format file size
                        size = file["size"]
                        if size < 1024:
                            size_str = f"{size} B"
                        elif size < 1024 * 1024:
                            size_str = f"{size / 1024:.1f} KB"
                        else:
                            size_str = f"{size / (1024 * 1024):.1f} MB"

                        st.text(size_str)

                    with col3:
                        st.text(datetime.datetime.fromtimestamp(file["modified"]).strftime("%Y-%m-%d %H:%M"))

        # Selected files
        if page_data.selected_files:
            st.subheader("Selected Files")
            for file in page_data.selected_files:
                st.text(file)

def render_dashboard_page():
    """
    Render the Dashboard page using the core DashboardPage class.

    This function creates an instance of the core DashboardPage class,
    gets the page data, and renders it using Streamlit components.
    """
    # Create an instance of the core DashboardPage class
    page = DashboardPage(st.session_state.get("db_connection"))

    # Update connected services based on session state
    if "connected_services" in st.session_state:
        page.connected_services = st.session_state["connected_services"]

    # Render the page
    render_page(page)

    # Store the connected services in session state for future use
    st.session_state["connected_services"] = page.connected_services

def _render_connect_page(page_data: ConnectPageData) -> None:
    """
    Render a connect page using Streamlit components.

    Args:
        page_data: The connect page data to render.
    """
    # Set the page title
    st.title(page_data.title)

    # Create tabs for different connection types
    tabs = ["Available Connections", "Active Connections"]
    tab1, tab2 = st.tabs(tabs)

    # Available Connections tab
    with tab1:
        st.subheader("Available Connection Types")

        # Display available connection types
        for i, conn in enumerate(page_data.available_connections):
            with st.expander(f"{conn['name']} - {conn['description']}", expanded=False):
                st.write(f"**Type:** {conn['id']}")
                st.write(f"**Description:** {conn['description']}")

                # Create a form for connection configuration
                with st.form(key=f"connect_form_{conn['id']}"):
                    # Create input fields for each config field
                    config = {}
                    for field in conn['config_fields']:
                        if field['type'] == 'password':
                            config[field['name']] = st.text_input(
                                field['label'], 
                                type="password",
                                key=f"connect_{conn['id']}_{field['name']}"
                            )
                        else:
                            config[field['name']] = st.text_input(
                                field['label'],
                                key=f"connect_{conn['id']}_{field['name']}"
                            )

                    # Connection name
                    conn_name = st.text_input("Connection Name", value=f"{conn['name']} Connection")

                    # Test and Connect buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        test_button = st.form_submit_button("Test Connection")
                    with col2:
                        connect_button = st.form_submit_button("Connect")

                    # Handle test button
                    if test_button:
                        # Store the test request in session state
                        st.session_state["connect_test_request"] = {
                            "connection_type": conn['id'],
                            "config": config
                        }
                        st.rerun()

                    # Handle connect button
                    if connect_button:
                        # Store the connect request in session state
                        st.session_state["connect_request"] = {
                            "connection_type": conn['id'],
                            "config": config,
                            "name": conn_name
                        }
                        st.rerun()

    # Active Connections tab
    with tab2:
        st.subheader("Active Connections")

        if not page_data.active_connections:
            st.info("No active connections. Connect to a data source from the Available Connections tab.")
        else:
            # Display active connections
            for conn in page_data.active_connections:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.write(f"**{conn['name']}** ({conn['type']})")

                    with col2:
                        status = "✅ Connected" if page_data.connection_status.get(conn['id'], False) else "❌ Disconnected"
                        st.write(status)

                    with col3:
                        if st.button("Disconnect", key=f"disconnect_{conn['id']}"):
                            # Store the disconnect request in session state
                            st.session_state["disconnect_request"] = conn['id']
                            st.rerun()

                    # Show connection details
                    st.write("**Configuration:**")
                    for key, value in conn['config'].items():
                        st.write(f"- {key}: {value}")

                    # Show error if any
                    if conn['id'] in page_data.connection_errors:
                        st.error(f"Error: {page_data.connection_errors[conn['id']]}")

                    st.markdown("---")

def render_file_browser_page():
    """
    Render the File Browser page using the core FileBrowserPage class.

    This function creates an instance of the core FileBrowserPage class,
    gets the page data, and renders it using Streamlit components.
    """
    # Get the current path from session state or use the home directory
    current_path = st.session_state.get("file_browser_current_path")

    # Create an instance of the core FileBrowserPage class
    page = FileBrowserPage(st.session_state.get("db_connection"), current_path)

    # Update page properties from session state
    if "file_browser_selected_files" in st.session_state:
        page.selected_files = st.session_state["file_browser_selected_files"]

    if "file_browser_view_mode" in st.session_state:
        page.view_mode = st.session_state["file_browser_view_mode"]

    if "file_browser_sort_by" in st.session_state:
        page.sort_by = st.session_state["file_browser_sort_by"]

    if "file_browser_sort_order" in st.session_state:
        page.sort_order = st.session_state["file_browser_sort_order"]

    if "file_browser_filter_pattern" in st.session_state:
        page.filter_pattern = st.session_state["file_browser_filter_pattern"]

    # Handle actions from the UI
    if "file_browser_action" in st.session_state:
        action = st.session_state.pop("file_browser_action")

        if action == "navigate" and "file_browser_target" in st.session_state:
            target = st.session_state.pop("file_browser_target")
            page.navigate_to(target)

        elif action == "go_up":
            page.navigate_up()

        elif action == "select" and "file_browser_target" in st.session_state:
            target = st.session_state.pop("file_browser_target")
            multi_select = st.session_state.get("file_browser_multi_select", False)
            page.select_file(target, multi_select)

    # Update view mode, sort, and filter from the UI inputs
    if "view_mode" in st.session_state:
        page.set_view_mode(st.session_state["view_mode"])

    if "sort_by" in st.session_state:
        page.set_sort(st.session_state["sort_by"], st.session_state.get("sort_order"))

    if "filter_pattern" in st.session_state:
        page.set_filter(st.session_state["filter_pattern"])

    # Render the page
    render_page(page)

    # Store page state in session state for future use
    st.session_state["file_browser_current_path"] = page.current_path
    st.session_state["file_browser_selected_files"] = page.selected_files
    st.session_state["file_browser_view_mode"] = page.view_mode
    st.session_state["file_browser_sort_by"] = page.sort_by
    st.session_state["file_browser_sort_order"] = page.sort_order
    st.session_state["file_browser_filter_pattern"] = page.filter_pattern

def _render_explore_page(page_data: ExplorePageData) -> None:
    """
    Render an explore page using Streamlit components.

    Args:
        page_data: The explore page data to render.
    """
    # Set the page title
    st.title(page_data.title)

    # Create a sidebar for data source selection
    with st.sidebar:
        st.header("Data Sources")

        # Display available data sources
        for i, source in enumerate(page_data.available_data_sources):
            if st.button(f"{source['name']}", key=f"source_{source['id']}"):
                # Store the data source selection in session state
                st.session_state["explore_data_source"] = source["id"]
                st.rerun()

        # Show the current data source
        if "explore_data_source" in st.session_state:
            current_source_id = st.session_state["explore_data_source"]
            current_source = next((s for s in page_data.available_data_sources if s["id"] == current_source_id), None)

            if current_source:
                st.success(f"Selected: {current_source['name']}")

                # Show example queries
                st.subheader("Example Queries")
                for i, example in enumerate(current_source.get("example_queries", [])):
                    if st.button(example["name"], key=f"example_{i}"):
                        # Store the example query in session state
                        st.session_state["explore_query"] = example["query"]
                        st.rerun()

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Query editor
        st.subheader("Query Editor")

        # Get the current query from session state or use an empty string
        current_query = st.session_state.get("explore_query", "")

        # Create a text area for the query
        query = st.text_area("Enter your query", value=current_query, height=200, key="query_editor")

        # Execute button
        if st.button("Execute Query"):
            # Store the query in session state
            st.session_state["explore_query"] = query

            # Store the execute request in session state
            st.session_state["explore_execute_request"] = True
            st.rerun()

        # Query results
        if page_data.query_results:
            st.subheader("Query Results")

            if "error" in page_data.query_results:
                st.error(f"Error: {page_data.query_results['error']}")
            else:
                # Display the results as a table
                if "data" in page_data.query_results and "columns" in page_data.query_results:
                    import pandas as pd
                    df = pd.DataFrame(page_data.query_results["data"], columns=page_data.query_results["columns"])
                    st.dataframe(df)

                # Display summary information
                if "summary" in page_data.query_results:
                    summary = page_data.query_results["summary"]
                    st.write(f"Rows returned: {summary.get('rows_returned', 'N/A')}")
                    st.write(f"Execution time: {summary.get('execution_time_ms', 'N/A')} ms")

    with col2:
        # Schema information
        if page_data.schema_info:
            st.subheader("Schema Information")

            # Display schema information based on the data source type
            if "node_labels" in page_data.schema_info:
                # Neo4j schema
                st.write("**Node Labels:**")
                st.write(", ".join(page_data.schema_info["node_labels"]))

                st.write("**Relationship Types:**")
                st.write(", ".join(page_data.schema_info["relationship_types"]))

                st.write("**Property Keys:**")
                st.write(", ".join(page_data.schema_info["property_keys"]))

            elif "tables" in page_data.schema_info:
                # PostgreSQL schema
                st.write("**Tables:**")
                st.write(", ".join(page_data.schema_info["tables"]))

                st.write("**Views:**")
                st.write(", ".join(page_data.schema_info["views"]))

                st.write("**Schemas:**")
                st.write(", ".join(page_data.schema_info["schemas"]))

            elif "columns" in page_data.schema_info:
                # CSV schema
                st.write("**Columns:**")
                for i, col in enumerate(page_data.schema_info["columns"]):
                    data_type = page_data.schema_info["data_types"][i] if "data_types" in page_data.schema_info and i < len(page_data.schema_info["data_types"]) else "unknown"
                    st.write(f"- {col} ({data_type})")

                if "row_count" in page_data.schema_info:
                    st.write(f"**Row Count:** {page_data.schema_info['row_count']}")

        # Visualizations
        if page_data.visualizations:
            st.subheader("Visualizations")

            # Create tabs for different visualizations
            viz_tabs = st.tabs([viz["name"] for viz in page_data.visualizations])

            for i, viz in enumerate(page_data.visualizations):
                with viz_tabs[i]:
                    if viz["type"] == "table":
                        # Table visualization
                        import pandas as pd
                        df = pd.DataFrame(viz["data"]["data"], columns=viz["data"]["columns"])
                        st.dataframe(df)

                    elif viz["type"] == "bar_chart":
                        # Bar chart visualization
                        import pandas as pd
                        import plotly.express as px

                        df = pd.DataFrame(viz["data"]["data"])
                        fig = px.bar(df, x="x", y="y", title=f"{viz['name']}: {viz['data']['x_axis']} vs {viz['data']['y_axis']}")
                        st.plotly_chart(fig, use_container_width=True)

                    elif viz["type"] == "line_chart":
                        # Line chart visualization
                        import pandas as pd
                        import plotly.express as px

                        df = pd.DataFrame(viz["data"]["data"])
                        fig = px.line(df, x="x", y="y", title=f"{viz['name']}: {viz['data']['x_axis']} vs {viz['data']['y_axis']}")
                        st.plotly_chart(fig, use_container_width=True)

                    elif viz["type"] == "pie_chart":
                        # Pie chart visualization
                        import plotly.express as px

                        fig = px.pie(values=viz["data"]["values"], names=viz["data"]["labels"], title=viz["name"])
                        st.plotly_chart(fig, use_container_width=True)

                    else:
                        st.write(f"Visualization type '{viz['type']}' not supported.")

def render_connect_page():
    """
    Render the Connect page using the core ConnectPage class.

    This function creates an instance of the core ConnectPage class,
    gets the page data, and renders it using Streamlit components.
    """
    # Create an instance of the core ConnectPage class
    page = ConnectPage(st.session_state.get("db_connection"))

    # Update active connections from session state
    if "connect_active_connections" in st.session_state:
        page.active_connections = st.session_state["connect_active_connections"]

    if "connect_connection_status" in st.session_state:
        page.connection_status = st.session_state["connect_connection_status"]

    if "connect_connection_errors" in st.session_state:
        page.connection_errors = st.session_state["connect_connection_errors"]

    # Handle connection requests
    if "connect_request" in st.session_state:
        request = st.session_state.pop("connect_request")
        success = page.connect(
            request["connection_type"],
            request["config"],
            request["name"]
        )
        if success:
            st.success(f"Connected to {request['connection_type']} as {request['name']}")
        else:
            st.error(f"Failed to connect to {request['connection_type']}")

    # Handle test requests
    if "connect_test_request" in st.session_state:
        request = st.session_state.pop("connect_test_request")
        result = page.test_connection(
            request["connection_type"],
            request["config"]
        )
        if result["success"]:
            st.success(result["message"])
        else:
            st.error(result["message"])

    # Handle disconnect requests
    if "disconnect_request" in st.session_state:
        conn_id = st.session_state.pop("disconnect_request")
        success = page.disconnect(conn_id)
        if success:
            st.success(f"Disconnected from {conn_id}")
        else:
            st.error(f"Failed to disconnect from {conn_id}")

    # Render the page
    render_page(page)

    # Store page state in session state for future use
    st.session_state["connect_active_connections"] = page.active_connections
    st.session_state["connect_connection_status"] = page.connection_status
    st.session_state["connect_connection_errors"] = page.connection_errors

def render_explore_page():
    """
    Render the Explore page using the core ExplorePage class.

    This function creates an instance of the core ExplorePage class,
    gets the page data, and renders it using Streamlit components.
    """
    # Create an instance of the core ExplorePage class
    page = ExplorePage(st.session_state.get("db_connection"))

    # Set the data source if one is selected
    if "explore_data_source" in st.session_state:
        page.set_data_source(st.session_state["explore_data_source"])

    # Execute a query if requested
    if "explore_execute_request" in st.session_state and "explore_query" in st.session_state:
        st.session_state.pop("explore_execute_request")
        query = st.session_state["explore_query"]
        success = page.execute_query(query)
        if not success and page.query_results and "error" in page.query_results:
            st.error(f"Error executing query: {page.query_results['error']}")

    # Render the page
    render_page(page)

    # No need to store page state in session state as it's regenerated on each render
