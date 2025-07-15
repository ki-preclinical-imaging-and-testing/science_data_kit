"""
Responsive Design Component for Science Data Kit

This module provides utilities for making the UI responsive on mobile devices.
It includes CSS styles and utility functions for responsive layouts.
"""

import streamlit as st
from typing import Optional, Dict, Any, List, Tuple

def apply_responsive_styles():
    """
    Apply responsive CSS styles to make the UI mobile-friendly.

    This function injects CSS that improves the layout on small screens,
    adjusts font sizes, optimizes touch targets, and improves navigation.
    """
    # CSS for responsive design
    st.markdown("""
    <style>
    /* Base responsive styles */
    @media (max-width: 768px) {
        /* Adjust font sizes for better readability on small screens */
        .main .block-container {
            padding-top: 1rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }

        /* Make headers more compact on mobile */
        h1, h2, h3 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }

        /* Adjust input fields for better touch interaction */
        .stTextInput input, .stNumberInput input, .stSelectbox, .stMultiselect {
            min-height: 2.5rem;
            font-size: 1rem;
        }

        /* Make buttons larger for touch targets */
        .stButton button {
            min-height: 2.5rem;
            min-width: 5rem;
        }

        /* Optimize tables for small screens */
        .dataframe {
            font-size: 0.8rem;
            width: 100%;
            overflow-x: auto;
            display: block;
        }

        /* Improve sidebar usability on mobile */
        .css-1d391kg, .css-12oz5g7 {
            padding-top: 2rem;
            padding-right: 1rem;
            padding-left: 1rem;
        }
    }

    /* Specific adjustments for very small screens */
    @media (max-width: 480px) {
        /* Further reduce padding */
        .main .block-container {
            padding-top: 0.5rem;
            padding-left: 0.25rem;
            padding-right: 0.25rem;
        }

        /* Stack columns vertically on very small screens */
        .row-widget.stHorizontal {
            flex-direction: column;
        }

        /* Make images responsive */
        img {
            max-width: 100%;
            height: auto;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_responsive_columns(num_columns: int = 2) -> List:
    """
    Create responsive columns that adapt to screen size.

    On mobile devices, this will create a more stacked layout
    by adjusting column widths based on screen size.

    Args:
        num_columns: Number of columns to create (default: 2)

    Returns:
        List of column objects that can be used in a with statement
    """
    # Create columns with appropriate widths
    if num_columns == 2:
        return st.columns([1, 1])
    elif num_columns == 3:
        return st.columns([1, 1, 1])
    elif num_columns == 4:
        return st.columns([1, 1, 1, 1])
    else:
        # Default to equal width columns
        return st.columns([1] * num_columns)

def create_responsive_container(content_function, key: Optional[str] = None):
    """
    Create a container with responsive styling.

    Args:
        content_function: Function that renders the content inside the container
        key: Optional key for the container

    Returns:
        A context manager for use with 'with' statements
    """
    # Create a container
    container = st.container(key=key)

    # Apply responsive styling
    container.markdown("""
    <style>
    .responsive-container {
        padding: 0.5rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
        background-color: rgba(240, 242, 246, 0.5);
    }
    @media (max-width: 768px) {
        .responsive-container {
            padding: 0.25rem;
            margin-bottom: 0.5rem;
        }
    }
    </style>
    <div class="responsive-container">
    """, unsafe_allow_html=True)

    # Call the content function to render the content inside the container
    content_function()

    # Close the container div
    container.markdown("</div>", unsafe_allow_html=True)

    # Return the container for use with 'with' statement
    return container

def create_responsive_tabs(tab_names: List[str], tab_contents: List[callable]):
    """
    Create tabs that are more touch-friendly on mobile devices.

    Args:
        tab_names: List of tab names
        tab_contents: List of functions that render the content for each tab
    """
    # Apply custom CSS for more touch-friendly tabs
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        /* Make tabs larger and more touch-friendly */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 0.75rem;
            min-height: 2.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Create the tabs
    tabs = st.tabs(tab_names)

    # Render the content for each tab
    for i, tab_content in enumerate(tab_contents):
        with tabs[i]:
            tab_content()
