"""
Streamlit Adapter Module for Science Data Kit

This module provides Streamlit-specific adapters for the core page classes.
It bridges between the framework-independent core functionality and the Streamlit UI.
"""

import streamlit as st
from typing import Type, Dict, Any, List, Optional

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import PageData, DashboardPageData
from science_data_kit.core.pages.dashboard import DashboardPage
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