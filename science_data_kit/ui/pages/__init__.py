"""
UI Pages Package for Science Data Kit

This package provides the page components for the Science Data Kit application.
Pages are organized by functionality and represent different views in the application.
"""

# Import common modules for easier access
import streamlit as st
from typing import Dict, Any, Optional, List, Union, Callable

# Import page render functions for easier access
from science_data_kit.ui.pages.dashboard import render_dashboard_page
from science_data_kit.ui.pages.connect import render_server_page
from science_data_kit.ui.pages.survey import render_survey_page
from science_data_kit.ui.pages.map import render_map_page
from science_data_kit.ui.pages.explore import render_explore_page
from science_data_kit.ui.pages.ontology import render_ontology_page
from science_data_kit.ui.pages.chat import render_chat_page
from science_data_kit.ui.pages.file_browser import render_file_browser_page
from science_data_kit.ui.pages.about import render_about_page
from science_data_kit.ui.pages.preferences import render_preferences_page

# Version information
__version__ = "0.1.0"

# Export page render functions
__all__ = [
    'render_dashboard_page',
    'render_server_page',
    'render_survey_page',
    'render_map_page',
    'render_explore_page',
    'render_ontology_page',
    'render_chat_page',
    'render_file_browser_page',
    'render_about_page',
    'render_preferences_page',
]
