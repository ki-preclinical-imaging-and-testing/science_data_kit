"""
Microsoft Graph API Explorer Page for Science Data Kit

This module provides a Streamlit page for exploring Microsoft Graph API data.
"""

import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
import json

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter
from science_data_kit.core.utils.msgraph_utils import (
    build_msgraph_query, msgraph_to_dataframe, msgraph_to_network,
    extract_user_data, extract_group_data, extract_message_data
)
from science_data_kit.ui.components.msgraph_query_builder import MSGraphQueryBuilder


class MSGraphExplorePage(BasePage):
    """
    Page for exploring Microsoft Graph API data.

    This page provides functionality for browsing Microsoft Graph API endpoints,
    executing queries, and visualizing the results.
    """

    def __init__(self):
        """
        Initialize the Microsoft Graph API explorer page.
        """
        super().__init__(
            title="Microsoft Graph API Explorer",
            icon="🔍"
        )
        self.adapter = None
        self.connection_manager = None
        self._setup_sidebar()

    def _setup_sidebar(self):
        """
        Set up the sidebar for the Microsoft Graph API explorer page.
        """
        # Add a link to the Microsoft Graph API connection page
        self.add_sidebar_item(
            lambda: st.sidebar.markdown(
                "[Connect to Microsoft Graph API](/msgraph_connect)"
            )
        )

    def _check_connection(self):
        """
        Check if connected to Microsoft Graph API.

        Returns:
            True if connected, False otherwise.
        """
        # Get connection manager from session state
        if "msgraph_connection_manager" in st.session_state:
            self.connection_manager = st.session_state["msgraph_connection_manager"]
            if self.connection_manager.connected:
                # Get adapter from session state
                if "msgraph_adapter" in st.session_state:
                    self.adapter = st.session_state["msgraph_adapter"]
                else:
                    # Create adapter
                    self.adapter = MSGraphAdapter(connection_manager=self.connection_manager)
                    st.session_state["msgraph_adapter"] = self.adapter
                return True

        return False

    def _execute_query(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None):
        """
        Execute a query against Microsoft Graph API.

        Args:
            resource_path: The resource path to query (e.g., '/me', '/users').
            query_parameters: Optional query parameters.

        Returns:
            The response from Microsoft Graph API as a dictionary.
        """
        try:
            return self.connection_manager.execute_query(resource_path, query_parameters)
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
            return None

    def _query_to_dataframe(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None):
        """
        Execute a query and return results as a pandas DataFrame.

        Args:
            resource_path: The resource path to query (e.g., '/me', '/users').
            query_parameters: Optional query parameters.

        Returns:
            A pandas DataFrame containing the query results.
        """
        try:
            return self.connection_manager.query_to_dataframe(resource_path, query_parameters)
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
            return pd.DataFrame()

    def _export_data(self, data: pd.DataFrame, format: str):
        """
        Export data to a file.

        Args:
            data: The data to export.
            format: The format to export to (csv, json, excel).
        """
        if format == "csv":
            csv = data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="msgraph_data.csv">Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
        elif format == "json":
            json_str = data.to_json(orient="records")
            b64 = base64.b64encode(json_str.encode()).decode()
            href = f'<a href="data:file/json;base64,{b64}" download="msgraph_data.json">Download JSON</a>'
            st.markdown(href, unsafe_allow_html=True)
        elif format == "excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                data.to_excel(writer, sheet_name="Sheet1", index=False)
            b64 = base64.b64encode(output.getvalue()).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="msgraph_data.xlsx">Download Excel</a>'
            st.markdown(href, unsafe_allow_html=True)

    def _get_sample_queries(self):
        """
        Get a list of sample queries for Microsoft Graph API.

        Returns:
            A dictionary of sample queries.
        """
        return {
            "Get current user": {
                "resource_path": "/me",
                "query_parameters": {}
            },
            "Get users": {
                "resource_path": "/users",
                "query_parameters": {
                    "top": "10"
                }
            },
            "Get groups": {
                "resource_path": "/groups",
                "query_parameters": {
                    "top": "10"
                }
            },
            "Get my messages": {
                "resource_path": "/me/messages",
                "query_parameters": {
                    "top": "10"
                }
            },
            "Get my events": {
                "resource_path": "/me/events",
                "query_parameters": {
                    "top": "10"
                }
            },
            "Get my files": {
                "resource_path": "/me/drive/root/children",
                "query_parameters": {
                    "top": "10"
                }
            }
        }

    def render_content(self):
        """
        Render the content of the Microsoft Graph API explorer page.
        """
        st.title("Microsoft Graph API Explorer")

        # Check if connected to Microsoft Graph API
        if not self._check_connection():
            st.warning("Not connected to Microsoft Graph API. Please connect first.")
            st.markdown("[Connect to Microsoft Graph API](/msgraph_connect)")
            return

        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["Query Builder", "Advanced Query Builder", "Results", "Visualization"])

        with tab1:
            st.header("Query Builder")

            # Sample queries
            st.subheader("Sample Queries")
            sample_queries = self._get_sample_queries()
            selected_query = st.selectbox(
                "Select a sample query",
                list(sample_queries.keys())
            )

            # Resource path
            resource_path = st.text_input(
                "Resource Path",
                value=sample_queries[selected_query]["resource_path"]
            )

            # Query parameters
            st.subheader("Query Parameters")
            col1, col2 = st.columns(2)

            with col1:
                select_param = st.text_input(
                    "Select",
                    value=sample_queries[selected_query]["query_parameters"].get("select", ""),
                    help="Comma-separated list of properties to include in the response."
                )

            with col2:
                filter_param = st.text_input(
                    "Filter",
                    value=sample_queries[selected_query]["query_parameters"].get("filter", ""),
                    help="OData filter query."
                )

            col1, col2 = st.columns(2)

            with col1:
                expand_param = st.text_input(
                    "Expand",
                    value=sample_queries[selected_query]["query_parameters"].get("expand", ""),
                    help="Comma-separated list of relationships to expand."
                )

            with col2:
                orderby_param = st.text_input(
                    "Order By",
                    value=sample_queries[selected_query]["query_parameters"].get("orderby", ""),
                    help="Comma-separated list of properties to sort by."
                )

            col1, col2 = st.columns(2)

            with col1:
                top_param = st.text_input(
                    "Top",
                    value=sample_queries[selected_query]["query_parameters"].get("top", ""),
                    help="Maximum number of items to return."
                )

            with col2:
                skip_param = st.text_input(
                    "Skip",
                    value=sample_queries[selected_query]["query_parameters"].get("skip", ""),
                    help="Number of items to skip."
                )

            # Build query parameters
            query_parameters = {}

            if select_param:
                query_parameters["select"] = select_param

            if filter_param:
                query_parameters["filter"] = filter_param

            if expand_param:
                query_parameters["expand"] = expand_param

            if orderby_param:
                query_parameters["orderby"] = orderby_param

            if top_param:
                query_parameters["top"] = top_param

            if skip_param:
                query_parameters["skip"] = skip_param

            # Execute query button
            if st.button("Execute Query"):
                # Store query in session state
                st.session_state["msgraph_query"] = {
                    "resource_path": resource_path,
                    "query_parameters": query_parameters
                }

                # Execute query
                response = self._execute_query(resource_path, query_parameters)

                # Store response in session state
                if response:
                    st.session_state["msgraph_response"] = response
                    st.success("Query executed successfully.")

                    # Convert response to DataFrame
                    df = msgraph_to_dataframe(response)

                    # Store DataFrame in session state
                    st.session_state["msgraph_dataframe"] = df

                    # Switch to Results tab
                    st.experimental_set_query_params(tab="results")

        with tab2:
            # Create and render the advanced query builder
            query_builder = MSGraphQueryBuilder(key="msgraph_advanced_query")
            resource_path, query_parameters = query_builder.render()

            # Execute query button
            if st.button("Execute Advanced Query"):
                # Store query in session state
                st.session_state["msgraph_query"] = {
                    "resource_path": resource_path,
                    "query_parameters": query_parameters
                }

                # Execute query
                response = self._execute_query(resource_path, query_parameters)

                # Store response in session state
                if response:
                    st.session_state["msgraph_response"] = response
                    st.success("Query executed successfully.")

                    # Convert response to DataFrame
                    df = msgraph_to_dataframe(response)

                    # Store DataFrame in session state
                    st.session_state["msgraph_dataframe"] = df

                    # Switch to Results tab
                    st.experimental_set_query_params(tab="results")

        with tab3:
            st.header("Results")

            # Check if response is available
            if "msgraph_response" in st.session_state:
                response = st.session_state["msgraph_response"]

                # Display response as JSON
                st.subheader("Response")
                st.json(response)

                # Display response as DataFrame
                if "msgraph_dataframe" in st.session_state:
                    df = st.session_state["msgraph_dataframe"]

                    st.subheader("DataFrame")
                    st.dataframe(df)

                    # Export options
                    st.subheader("Export")
                    export_format = st.selectbox(
                        "Export Format",
                        ["csv", "json", "excel"]
                    )

                    if st.button("Export"):
                        self._export_data(df, export_format)
            else:
                st.info("No query results available. Please execute a query first.")

        with tab4:
            st.header("Visualization")

            # Check if response is available
            if "msgraph_response" in st.session_state:
                response = st.session_state["msgraph_response"]

                # Determine entity type
                entity_type = "unknown"
                if "msgraph_query" in st.session_state:
                    resource_path = st.session_state["msgraph_query"]["resource_path"]
                    if "/users" in resource_path:
                        entity_type = "users"
                    elif "/groups" in resource_path:
                        entity_type = "groups"
                    elif "/messages" in resource_path:
                        entity_type = "messages"
                    elif "/events" in resource_path:
                        entity_type = "events"
                    elif "/drive" in resource_path:
                        entity_type = "drive"

                # Create visualization based on entity type
                if entity_type in ["users", "groups"]:
                    st.subheader("Network Visualization")

                    # Create network
                    G = msgraph_to_network(response, entity_type)

                    # Create visualization
                    if len(G.nodes) > 0:
                        fig, ax = plt.subplots(figsize=(10, 8))
                        pos = nx.spring_layout(G)

                        # Draw nodes
                        nx.draw_networkx_nodes(
                            G, pos,
                            node_color="skyblue",
                            node_size=500,
                            alpha=0.8
                        )

                        # Draw edges
                        nx.draw_networkx_edges(
                            G, pos,
                            width=1.0,
                            alpha=0.5
                        )

                        # Draw labels
                        nx.draw_networkx_labels(
                            G, pos,
                            labels={n: G.nodes[n].get('name', n) for n in G.nodes},
                            font_size=10
                        )

                        plt.axis('off')
                        st.pyplot(fig)
                    else:
                        st.info("No nodes available for visualization.")
                else:
                    st.info("Visualization not available for this entity type.")
            else:
                st.info("No query results available. Please execute a query first.")


def render_msgraph_explore_page():
    """
    Render the Microsoft Graph API explorer page.
    """
    page = MSGraphExplorePage()
    page.render()
