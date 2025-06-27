"""
Microsoft Graph API Advanced Query Builder Component for Science Data Kit

This module provides a Streamlit component for building complex Microsoft Graph API queries.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List, Union, Callable, Tuple

from science_data_kit.core.utils.msgraph_utils import build_msgraph_query


class MSGraphQueryBuilder:
    """
    Advanced query builder for Microsoft Graph API.
    
    This component provides a user-friendly interface for building complex
    Microsoft Graph API queries with support for all OData query parameters.
    """
    
    def __init__(self, key: str = "msgraph_query_builder"):
        """
        Initialize the Microsoft Graph API query builder.
        
        Args:
            key: A unique key for the component to use in session state.
        """
        self.key = key
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """
        Initialize session state variables for the query builder.
        """
        if f"{self.key}_resource_path" not in st.session_state:
            st.session_state[f"{self.key}_resource_path"] = "/me"
        
        if f"{self.key}_select_fields" not in st.session_state:
            st.session_state[f"{self.key}_select_fields"] = []
        
        if f"{self.key}_filter_conditions" not in st.session_state:
            st.session_state[f"{self.key}_filter_conditions"] = []
        
        if f"{self.key}_expand_relations" not in st.session_state:
            st.session_state[f"{self.key}_expand_relations"] = []
        
        if f"{self.key}_orderby_fields" not in st.session_state:
            st.session_state[f"{self.key}_orderby_fields"] = []
        
        if f"{self.key}_top" not in st.session_state:
            st.session_state[f"{self.key}_top"] = 10
        
        if f"{self.key}_skip" not in st.session_state:
            st.session_state[f"{self.key}_skip"] = 0
    
    def _render_resource_path_section(self):
        """
        Render the resource path section of the query builder.
        """
        st.subheader("Resource Path")
        
        # Common resource paths
        common_paths = [
            "/me",
            "/users",
            "/groups",
            "/me/messages",
            "/me/events",
            "/me/drive/root/children",
            "/users/{user-id}",
            "/groups/{group-id}",
            "/users/{user-id}/messages",
            "/users/{user-id}/events",
            "/users/{user-id}/drive/root/children"
        ]
        
        # Resource path input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            resource_path = st.text_input(
                "Resource Path",
                value=st.session_state[f"{self.key}_resource_path"],
                key=f"{self.key}_resource_path_input"
            )
            st.session_state[f"{self.key}_resource_path"] = resource_path
        
        with col2:
            selected_path = st.selectbox(
                "Common Paths",
                ["Custom"] + common_paths,
                key=f"{self.key}_common_paths"
            )
            
            if selected_path != "Custom":
                st.session_state[f"{self.key}_resource_path"] = selected_path
                st.experimental_rerun()
    
    def _render_select_section(self):
        """
        Render the $select section of the query builder.
        """
        st.subheader("Select Fields")
        
        # Add new field
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_field = st.text_input(
                "Add Field",
                key=f"{self.key}_new_select_field"
            )
        
        with col2:
            if st.button("Add", key=f"{self.key}_add_select_field"):
                if new_field and new_field not in st.session_state[f"{self.key}_select_fields"]:
                    st.session_state[f"{self.key}_select_fields"].append(new_field)
        
        # Display selected fields
        if st.session_state[f"{self.key}_select_fields"]:
            for i, field in enumerate(st.session_state[f"{self.key}_select_fields"]):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.text(field)
                
                with col2:
                    if st.button("Remove", key=f"{self.key}_remove_select_field_{i}"):
                        st.session_state[f"{self.key}_select_fields"].pop(i)
                        st.experimental_rerun()
        else:
            st.info("No fields selected. All fields will be returned.")
    
    def _render_filter_section(self):
        """
        Render the $filter section of the query builder.
        """
        st.subheader("Filter Conditions")
        
        # Add new condition
        col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
        
        with col1:
            field = st.text_input(
                "Field",
                key=f"{self.key}_filter_field"
            )
        
        with col2:
            operator = st.selectbox(
                "Operator",
                ["eq", "ne", "gt", "ge", "lt", "le", "contains", "startswith", "endswith"],
                key=f"{self.key}_filter_operator"
            )
        
        with col3:
            value = st.text_input(
                "Value",
                key=f"{self.key}_filter_value"
            )
        
        with col4:
            if st.button("Add", key=f"{self.key}_add_filter"):
                if field and value:
                    condition = f"{field} {operator} '{value}'"
                    st.session_state[f"{self.key}_filter_conditions"].append(condition)
        
        # Display filter conditions
        if st.session_state[f"{self.key}_filter_conditions"]:
            for i, condition in enumerate(st.session_state[f"{self.key}_filter_conditions"]):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.text(condition)
                
                with col2:
                    if st.button("Remove", key=f"{self.key}_remove_filter_{i}"):
                        st.session_state[f"{self.key}_filter_conditions"].pop(i)
                        st.experimental_rerun()
        else:
            st.info("No filter conditions added.")
    
    def _render_expand_section(self):
        """
        Render the $expand section of the query builder.
        """
        st.subheader("Expand Relations")
        
        # Add new relation
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_relation = st.text_input(
                "Add Relation",
                key=f"{self.key}_new_expand_relation"
            )
        
        with col2:
            if st.button("Add", key=f"{self.key}_add_expand_relation"):
                if new_relation and new_relation not in st.session_state[f"{self.key}_expand_relations"]:
                    st.session_state[f"{self.key}_expand_relations"].append(new_relation)
        
        # Display expanded relations
        if st.session_state[f"{self.key}_expand_relations"]:
            for i, relation in enumerate(st.session_state[f"{self.key}_expand_relations"]):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.text(relation)
                
                with col2:
                    if st.button("Remove", key=f"{self.key}_remove_expand_relation_{i}"):
                        st.session_state[f"{self.key}_expand_relations"].pop(i)
                        st.experimental_rerun()
        else:
            st.info("No relations expanded.")
    
    def _render_orderby_section(self):
        """
        Render the $orderby section of the query builder.
        """
        st.subheader("Order By")
        
        # Add new field
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            field = st.text_input(
                "Field",
                key=f"{self.key}_orderby_field"
            )
        
        with col2:
            direction = st.selectbox(
                "Direction",
                ["asc", "desc"],
                key=f"{self.key}_orderby_direction"
            )
        
        with col3:
            if st.button("Add", key=f"{self.key}_add_orderby"):
                if field:
                    orderby = f"{field} {direction}"
                    st.session_state[f"{self.key}_orderby_fields"].append(orderby)
        
        # Display orderby fields
        if st.session_state[f"{self.key}_orderby_fields"]:
            for i, orderby in enumerate(st.session_state[f"{self.key}_orderby_fields"]):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.text(orderby)
                
                with col2:
                    if st.button("Remove", key=f"{self.key}_remove_orderby_{i}"):
                        st.session_state[f"{self.key}_orderby_fields"].pop(i)
                        st.experimental_rerun()
        else:
            st.info("No ordering specified.")
    
    def _render_pagination_section(self):
        """
        Render the $top and $skip section of the query builder.
        """
        st.subheader("Pagination")
        
        col1, col2 = st.columns(2)
        
        with col1:
            top = st.number_input(
                "Top (max items)",
                min_value=1,
                max_value=1000,
                value=st.session_state[f"{self.key}_top"],
                key=f"{self.key}_top_input"
            )
            st.session_state[f"{self.key}_top"] = top
        
        with col2:
            skip = st.number_input(
                "Skip (offset)",
                min_value=0,
                value=st.session_state[f"{self.key}_skip"],
                key=f"{self.key}_skip_input"
            )
            st.session_state[f"{self.key}_skip"] = skip
    
    def _build_query(self) -> Tuple[str, Dict[str, Any]]:
        """
        Build the Microsoft Graph API query from the query builder state.
        
        Returns:
            A tuple containing the resource path and query parameters.
        """
        # Get resource path
        resource_path = st.session_state[f"{self.key}_resource_path"]
        
        # Build query parameters
        query_parameters = {}
        
        # Add select fields
        if st.session_state[f"{self.key}_select_fields"]:
            query_parameters["select"] = ",".join(st.session_state[f"{self.key}_select_fields"])
        
        # Add filter conditions
        if st.session_state[f"{self.key}_filter_conditions"]:
            query_parameters["filter"] = " and ".join(st.session_state[f"{self.key}_filter_conditions"])
        
        # Add expand relations
        if st.session_state[f"{self.key}_expand_relations"]:
            query_parameters["expand"] = ",".join(st.session_state[f"{self.key}_expand_relations"])
        
        # Add orderby fields
        if st.session_state[f"{self.key}_orderby_fields"]:
            query_parameters["orderby"] = ",".join(st.session_state[f"{self.key}_orderby_fields"])
        
        # Add top and skip
        query_parameters["top"] = str(st.session_state[f"{self.key}_top"])
        if st.session_state[f"{self.key}_skip"] > 0:
            query_parameters["skip"] = str(st.session_state[f"{self.key}_skip"])
        
        return resource_path, query_parameters
    
    def _render_preview_section(self):
        """
        Render the query preview section of the query builder.
        """
        st.subheader("Query Preview")
        
        # Build query
        resource_path, query_parameters = self._build_query()
        
        # Display resource path
        st.text(f"Resource Path: {resource_path}")
        
        # Display query parameters
        if query_parameters:
            st.text("Query Parameters:")
            for key, value in query_parameters.items():
                st.text(f"  ${key}: {value}")
        else:
            st.text("No query parameters specified.")
    
    def render(self) -> Tuple[str, Dict[str, Any]]:
        """
        Render the Microsoft Graph API query builder.
        
        Returns:
            A tuple containing the resource path and query parameters.
        """
        st.header("Advanced Query Builder")
        
        # Render sections
        self._render_resource_path_section()
        
        # Create tabs for different query parameters
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Select", "Filter", "Expand", "Order By", "Pagination"])
        
        with tab1:
            self._render_select_section()
        
        with tab2:
            self._render_filter_section()
        
        with tab3:
            self._render_expand_section()
        
        with tab4:
            self._render_orderby_section()
        
        with tab5:
            self._render_pagination_section()
        
        # Render preview
        self._render_preview_section()
        
        # Build and return query
        return self._build_query()