"""
Layout Templates for Science Data Kit

This module provides standardized layout templates for use across the application.
"""

import streamlit as st
from typing import Optional, List, Union, Dict, Any, Callable

def page_header(title: str, subtitle: Optional[str] = None, icon: Optional[str] = None) -> None:
    """
    Create a standardized page header.
    
    Args:
        title: The title of the page
        subtitle: Optional subtitle for the page
        icon: Optional icon for the page (emoji or URL)
    """
    if icon:
        st.title(f"{icon} {title}")
    else:
        st.title(title)
    
    if subtitle:
        st.markdown(f"*{subtitle}*")
    
    st.markdown("---")

def section_header(title: str, description: Optional[str] = None, level: int = 2) -> None:
    """
    Create a standardized section header.
    
    Args:
        title: The title of the section
        description: Optional description for the section
        level: The header level (2 for h2, 3 for h3, etc.)
    """
    if level == 2:
        st.header(title)
    elif level == 3:
        st.subheader(title)
    else:
        st.markdown(f"{"#" * level} {title}")
    
    if description:
        st.markdown(description)

def two_column_layout(left_content: Callable, right_content: Callable, left_width: int = 1, right_width: int = 1) -> None:
    """
    Create a standardized two-column layout.
    
    Args:
        left_content: Function that populates the left column
        right_content: Function that populates the right column
        left_width: Optional width of the left column
        right_width: Optional width of the right column
    """
    col1, col2 = st.columns([left_width, right_width])
    
    with col1:
        left_content()
    
    with col2:
        right_content()

def three_column_layout(left_content: Callable, middle_content: Callable, right_content: Callable, left_width: int = 1, middle_width: int = 1, right_width: int = 1) -> None:
    """
    Create a standardized three-column layout.
    
    Args:
        left_content: Function that populates the left column
        middle_content: Function that populates the middle column
        right_content: Function that populates the right column
        left_width: Optional width of the left column
        middle_width: Optional width of the middle column
        right_width: Optional width of the right column
    """
    col1, col2, col3 = st.columns([left_width, middle_width, right_width])
    
    with col1:
        left_content()
    
    with col2:
        middle_content()
    
    with col3:
        right_content()

def card(title: str, content: Callable, expanded: bool = True) -> None:
    """
    Create a standardized card layout using an expander.
    
    Args:
        title: The title of the card
        content: Function that populates the card content
        expanded: Whether the card should be expanded by default
    """
    with st.expander(title, expanded=expanded):
        content()

def tabs_layout(tab_contents: Dict[str, Callable]) -> None:
    """
    Create a standardized tabs layout.
    
    Args:
        tab_contents: Dictionary mapping tab names to content functions
    """
    tabs = st.tabs(list(tab_contents.keys()))
    
    for i, (tab_name, content_func) in enumerate(tab_contents.items()):
        with tabs[i]:
            content_func()