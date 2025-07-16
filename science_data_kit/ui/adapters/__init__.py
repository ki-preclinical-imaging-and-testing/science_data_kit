"""
UI Adapters Package for Science Data Kit

This package provides adapter modules that bridge between the core functionality
and the UI components. Adapters help maintain separation of concerns and make
the UI components more reusable.
"""

from science_data_kit.ui.adapters.page_adapter import PageAdapter, create_page_adapter, load_page_from_file
from science_data_kit.ui.adapters.streamlit_adapter import render_page, render_dashboard_page

# Version information
__version__ = "0.1.0"

__all__ = [
    'PageAdapter',
    'create_page_adapter',
    'load_page_from_file',
    'render_page',
    'render_dashboard_page'
]
