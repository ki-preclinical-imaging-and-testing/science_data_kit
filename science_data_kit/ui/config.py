"""
UI Configuration Module for Science Data Kit

This module provides configuration settings for the UI components.
It includes theme settings, layout options, and other UI-related configurations.
"""

import streamlit as st
from typing import Dict, Any, Optional
from pathlib import Path

# Default theme settings
DEFAULT_THEME = {
    "primaryColor": "#1E88E5",  # Blue
    "backgroundColor": "#FFFFFF",  # White
    "secondaryBackgroundColor": "#F0F2F6",  # Light gray
    "textColor": "#262730",  # Dark gray
    "font": "sans-serif"
}

# Default page configuration
DEFAULT_PAGE_CONFIG = {
    "page_title": "Science Data Kit",
    "page_icon": "🧬",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Application paths
APP_DIR = Path(__file__).parent.parent.parent
DATA_DIR = APP_DIR / "data"
DOCS_DIR = APP_DIR / "docs"

def configure_page(title: Optional[str] = None, icon: Optional[str] = None) -> None:
    """
    Configure the Streamlit page with the specified settings.
    
    Args:
        title: Optional title to override the default.
        icon: Optional icon to override the default.
    """
    config = DEFAULT_PAGE_CONFIG.copy()
    
    if title:
        config["page_title"] = title
    
    if icon:
        config["page_icon"] = icon
    
    st.set_page_config(**config)

def apply_theme() -> None:
    """Apply the default theme to the Streamlit app."""
    # This is a placeholder for future theme customization
    # Currently, Streamlit themes are set via .streamlit/config.toml
    pass

def get_app_settings() -> Dict[str, Any]:
    """
    Get the application settings.
    
    Returns:
        A dictionary containing application settings.
    """
    return {
        "theme": DEFAULT_THEME,
        "page_config": DEFAULT_PAGE_CONFIG,
        "paths": {
            "app_dir": str(APP_DIR),
            "data_dir": str(DATA_DIR),
            "docs_dir": str(DOCS_DIR)
        }
    }