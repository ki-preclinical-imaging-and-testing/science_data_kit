"""
User Preferences Page for Science Data Kit

This module provides a page for users to customize their preferences for the application.
It allows users to set theme, font size, and other UI preferences.
"""

import streamlit as st
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import os

from science_data_kit.ui.components.responsive_design import (
    apply_responsive_styles,
    create_responsive_columns,
    create_responsive_container,
    create_responsive_tabs
)
from science_data_kit.ui.state import save_state_to_config, load_state_from_config

def get_preferences_path() -> Path:
    """
    Get the path to the user preferences file.
    
    Returns:
        Path to the user preferences file.
    """
    # Create preferences directory in user's home directory
    preferences_dir = Path.home() / ".science_data_kit"
    preferences_dir.mkdir(parents=True, exist_ok=True)
    return preferences_dir / "user_preferences.yaml"

def save_preferences() -> None:
    """Save user preferences to a file."""
    preferences_path = get_preferences_path()
    
    try:
        # Save only the user_preferences key
        with open(preferences_path, 'w') as file:
            yaml.dump({"user_preferences": st.session_state.user_preferences}, file)
        
        if st.session_state.user_preferences.get("auto_save", True):
            st.success("Preferences saved successfully!")
    except Exception as e:
        st.error(f"Error saving preferences: {e}")

def load_preferences() -> None:
    """Load user preferences from a file."""
    preferences_path = get_preferences_path()
    
    if not preferences_path.exists():
        return
    
    try:
        with open(preferences_path, 'r') as file:
            data = yaml.safe_load(file)
        
        if data and "user_preferences" in data:
            st.session_state.user_preferences = data["user_preferences"]
            st.success("Preferences loaded successfully!")
    except Exception as e:
        st.error(f"Error loading preferences: {e}")

def apply_theme(theme: str) -> None:
    """
    Apply the selected theme to the application.
    
    Args:
        theme: The theme to apply ('light' or 'dark').
    """
    if theme == "dark":
        # Apply dark theme CSS
        st.markdown("""
        <style>
        :root {
            --background-color: #0e1117;
            --text-color: #fafafa;
            --widget-background: #262730;
            --widget-border: #4d4d4d;
        }
        
        body {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .stTextInput input, .stNumberInput input, .stSelectbox, .stMultiselect {
            background-color: var(--widget-background);
            border-color: var(--widget-border);
            color: var(--text-color);
        }
        
        .responsive-container {
            background-color: rgba(38, 39, 48, 0.5) !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Apply light theme CSS (default)
        st.markdown("""
        <style>
        :root {
            --background-color: #ffffff;
            --text-color: #31333F;
            --widget-background: #f0f2f6;
            --widget-border: #cccccc;
        }
        
        body {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .stTextInput input, .stNumberInput input, .stSelectbox, .stMultiselect {
            background-color: var(--widget-background);
            border-color: var(--widget-border);
            color: var(--text-color);
        }
        
        .responsive-container {
            background-color: rgba(240, 242, 246, 0.5) !important;
        }
        </style>
        """, unsafe_allow_html=True)

def apply_font_size(font_size: str) -> None:
    """
    Apply the selected font size to the application.
    
    Args:
        font_size: The font size to apply ('small', 'medium', or 'large').
    """
    font_sizes = {
        "small": {
            "base": "0.8rem",
            "h1": "1.5rem",
            "h2": "1.3rem",
            "h3": "1.1rem"
        },
        "medium": {
            "base": "1rem",
            "h1": "1.8rem",
            "h2": "1.5rem",
            "h3": "1.3rem"
        },
        "large": {
            "base": "1.2rem",
            "h1": "2.1rem",
            "h2": "1.8rem",
            "h3": "1.5rem"
        }
    }
    
    sizes = font_sizes.get(font_size, font_sizes["medium"])
    
    st.markdown(f"""
    <style>
    body, p, div, span, li {{
        font-size: {sizes["base"]};
    }}
    
    h1 {{
        font-size: {sizes["h1"]};
    }}
    
    h2 {{
        font-size: {sizes["h2"]};
    }}
    
    h3 {{
        font-size: {sizes["h3"]};
    }}
    </style>
    """, unsafe_allow_html=True)

def apply_preferences() -> None:
    """Apply all user preferences to the application."""
    preferences = st.session_state.user_preferences
    
    # Apply theme
    apply_theme(preferences.get("theme", "light"))
    
    # Apply font size
    apply_font_size(preferences.get("font_size", "medium"))
    
    # Apply other preferences as needed
    if preferences.get("sidebar_collapsed", False):
        # This is a placeholder - Streamlit doesn't directly support programmatically
        # collapsing the sidebar, but we could add custom JS for this in the future
        pass

def on_preference_change() -> None:
    """Handle preference changes."""
    # Apply the updated preferences
    apply_preferences()
    
    # Save preferences if auto-save is enabled
    if st.session_state.user_preferences.get("auto_save", True):
        save_preferences()

def render_preferences_page() -> None:
    """Render the preferences page."""
    st.title("User Preferences")
    
    # Apply current preferences
    apply_preferences()
    
    # Create tabs for different preference categories
    tab_names = ["Appearance", "Behavior", "Data Display"]
    tab_contents = [render_appearance_tab, render_behavior_tab, render_data_display_tab]
    
    create_responsive_tabs(tab_names, tab_contents)
    
    # Add buttons for saving and loading preferences
    cols = create_responsive_columns(3)
    
    with cols[0]:
        if st.button("Save Preferences", use_container_width=True):
            save_preferences()
    
    with cols[1]:
        if st.button("Load Preferences", use_container_width=True):
            load_preferences()
            apply_preferences()
    
    with cols[2]:
        if st.button("Reset to Defaults", use_container_width=True):
            # Reset to default preferences
            st.session_state.user_preferences = {
                "theme": "light",
                "font_size": "medium",
                "sidebar_collapsed": False,
                "show_tooltips": True,
                "data_table_rows": 10,
                "auto_save": True,
                "language": "en"
            }
            apply_preferences()
            st.success("Preferences reset to defaults!")

def render_appearance_tab() -> None:
    """Render the appearance preferences tab."""
    create_responsive_container(lambda: _render_appearance_content())

def _render_appearance_content() -> None:
    """Render the content for the appearance tab."""
    preferences = st.session_state.user_preferences
    
    # Theme selection
    theme = st.selectbox(
        "Theme",
        options=["light", "dark"],
        index=0 if preferences.get("theme") == "light" else 1,
        key="theme_select",
        on_change=lambda: update_preference("theme", st.session_state.theme_select)
    )
    
    # Font size selection
    font_size = st.selectbox(
        "Font Size",
        options=["small", "medium", "large"],
        index=["small", "medium", "large"].index(preferences.get("font_size", "medium")),
        key="font_size_select",
        on_change=lambda: update_preference("font_size", st.session_state.font_size_select)
    )
    
    # Sidebar collapsed state
    sidebar_collapsed = st.checkbox(
        "Collapse Sidebar by Default",
        value=preferences.get("sidebar_collapsed", False),
        key="sidebar_collapsed_check",
        on_change=lambda: update_preference("sidebar_collapsed", st.session_state.sidebar_collapsed_check)
    )

def render_behavior_tab() -> None:
    """Render the behavior preferences tab."""
    create_responsive_container(lambda: _render_behavior_content())

def _render_behavior_content() -> None:
    """Render the content for the behavior tab."""
    preferences = st.session_state.user_preferences
    
    # Show tooltips
    show_tooltips = st.checkbox(
        "Show Tooltips",
        value=preferences.get("show_tooltips", True),
        key="show_tooltips_check",
        on_change=lambda: update_preference("show_tooltips", st.session_state.show_tooltips_check)
    )
    
    # Auto-save preferences
    auto_save = st.checkbox(
        "Auto-save Preferences",
        value=preferences.get("auto_save", True),
        key="auto_save_check",
        on_change=lambda: update_preference("auto_save", st.session_state.auto_save_check)
    )
    
    # Language selection
    language = st.selectbox(
        "Language",
        options=["en", "es", "fr", "de", "zh"],
        index=["en", "es", "fr", "de", "zh"].index(preferences.get("language", "en")),
        key="language_select",
        on_change=lambda: update_preference("language", st.session_state.language_select)
    )
    
    # Display language names
    language_names = {
        "en": "English",
        "es": "Español (Spanish)",
        "fr": "Français (French)",
        "de": "Deutsch (German)",
        "zh": "中文 (Chinese)"
    }
    
    st.caption(f"Selected language: {language_names.get(language, language)}")
    st.info("Note: Language support is limited to English in the current version.")

def render_data_display_tab() -> None:
    """Render the data display preferences tab."""
    create_responsive_container(lambda: _render_data_display_content())

def _render_data_display_content() -> None:
    """Render the content for the data display tab."""
    preferences = st.session_state.user_preferences
    
    # Data table rows
    data_table_rows = st.slider(
        "Default Number of Rows in Data Tables",
        min_value=5,
        max_value=100,
        value=preferences.get("data_table_rows", 10),
        step=5,
        key="data_table_rows_slider",
        on_change=lambda: update_preference("data_table_rows", st.session_state.data_table_rows_slider)
    )

def update_preference(key: str, value: Any) -> None:
    """
    Update a specific preference and apply changes.
    
    Args:
        key: The preference key to update.
        value: The new value for the preference.
    """
    st.session_state.user_preferences[key] = value
    on_preference_change()

if __name__ == "__main__":
    # For testing the page in isolation
    st.set_page_config(page_title="User Preferences", layout="wide")
    
    # Initialize session state if not already initialized
    if "user_preferences" not in st.session_state:
        st.session_state.user_preferences = {
            "theme": "light",
            "font_size": "medium",
            "sidebar_collapsed": False,
            "show_tooltips": True,
            "data_table_rows": 10,
            "auto_save": True,
            "language": "en"
        }
    
    render_preferences_page()
"""