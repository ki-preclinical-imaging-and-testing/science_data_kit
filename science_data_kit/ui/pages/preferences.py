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


class PreferencesPage:
    """
    Preferences page for the Science Data Kit application.

    This class provides a wrapper around the preferences page functionality
    to maintain compatibility with the test suite.
    """

    def __init__(self):
        """Initialize the PreferencesPage."""
        pass

    def render(self):
        """Render the preferences page."""
        render_preferences_page()

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

def apply_theme(theme: str, custom_colors: dict = None) -> None:
    """
    Apply the selected theme to the application.

    Args:
        theme: The theme to apply ('light', 'dark', 'blue', 'green', 'purple', 'custom').
        custom_colors: Dictionary of custom colors when theme is 'custom'.
    """
    # Define theme color palettes
    theme_colors = {
        "light": {
            "background": "#ffffff",
            "text": "#31333F",
            "widget_background": "#f0f2f6",
            "widget_border": "#cccccc",
            "accent": "#1E88E5",
            "container_background": "rgba(240, 242, 246, 0.5)"
        },
        "dark": {
            "background": "#0e1117",
            "text": "#fafafa",
            "widget_background": "#262730",
            "widget_border": "#4d4d4d",
            "accent": "#4CAF50",
            "container_background": "rgba(38, 39, 48, 0.5)"
        },
        "blue": {
            "background": "#E3F2FD",
            "text": "#0D47A1",
            "widget_background": "#BBDEFB",
            "widget_border": "#64B5F6",
            "accent": "#1976D2",
            "container_background": "rgba(187, 222, 251, 0.5)"
        },
        "green": {
            "background": "#E8F5E9",
            "text": "#1B5E20",
            "widget_background": "#C8E6C9",
            "widget_border": "#81C784",
            "accent": "#388E3C",
            "container_background": "rgba(200, 230, 201, 0.5)"
        },
        "purple": {
            "background": "#F3E5F5",
            "text": "#4A148C",
            "widget_background": "#E1BEE7",
            "widget_border": "#BA68C8",
            "accent": "#7B1FA2",
            "container_background": "rgba(225, 190, 231, 0.5)"
        }
    }

    # Get colors for the selected theme or use custom colors
    if theme == "custom" and custom_colors:
        colors = custom_colors
    else:
        colors = theme_colors.get(theme, theme_colors["light"])

    # Apply the theme CSS
    st.markdown(f"""
    <style>
    :root {{
        --background-color: {colors["background"]};
        --text-color: {colors["text"]};
        --widget-background: {colors["widget_background"]};
        --widget-border: {colors["widget_border"]};
        --accent-color: {colors["accent"]};
    }}

    body {{
        background-color: var(--background-color);
        color: var(--text-color);
    }}

    .stTextInput input, .stNumberInput input, .stSelectbox, .stMultiselect {{
        background-color: var(--widget-background);
        border-color: var(--widget-border);
        color: var(--text-color);
    }}

    .stButton>button {{
        background-color: var(--accent-color);
        color: white;
    }}

    a {{
        color: var(--accent-color);
    }}

    .responsive-container {{
        background-color: {colors["container_background"]} !important;
    }}

    /* Customize tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        border-bottom-color: var(--widget-border);
    }}

    .stTabs [data-baseweb="tab"] {{
        color: var(--text-color);
    }}

    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: var(--accent-color);
        border-bottom-color: var(--accent-color);
    }}
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

    # Apply theme (with custom colors if theme is custom)
    theme = preferences.get("theme", "light")
    if theme == "custom" and "custom_colors" in preferences:
        apply_theme(theme, preferences["custom_colors"])
    else:
        apply_theme(theme)

    # Apply font size
    apply_font_size(preferences.get("font_size", "medium"))

    # Apply accessibility features
    apply_accessibility_features()

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
    tab_names = ["Appearance", "Behavior", "Data Display", "Accessibility"]
    tab_contents = [render_appearance_tab, render_behavior_tab, render_data_display_tab, render_accessibility_tab]

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
                "language": "en",
                "high_contrast": False,
                "screen_reader": False,
                "reduced_motion": False,
                "focus_indicators": False,
                "text_spacing": False,
                "custom_colors": {
                    "background": "#ffffff",
                    "text": "#31333F",
                    "widget_background": "#f0f2f6",
                    "widget_border": "#cccccc",
                    "accent": "#1E88E5",
                    "container_background": "rgba(240, 242, 246, 0.5)"
                }
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
    theme_options = ["light", "dark", "blue", "green", "purple", "custom"]
    theme_index = theme_options.index(preferences.get("theme", "light")) if preferences.get("theme") in theme_options else 0

    theme = st.selectbox(
        "Theme",
        options=theme_options,
        index=theme_index,
        key="theme_select",
        on_change=lambda: update_preference("theme", st.session_state.theme_select)
    )

    # Custom color options if custom theme is selected
    if theme == "custom":
        st.markdown("### Custom Theme Colors")

        # Initialize custom colors if not already in preferences
        if "custom_colors" not in preferences:
            preferences["custom_colors"] = {
                "background": "#ffffff",
                "text": "#31333F",
                "widget_background": "#f0f2f6",
                "widget_border": "#cccccc",
                "accent": "#1E88E5",
                "container_background": "rgba(240, 242, 246, 0.5)"
            }

        # Create columns for color pickers
        col1, col2 = st.columns(2)

        with col1:
            background_color = st.color_picker(
                "Background Color",
                preferences["custom_colors"]["background"],
                key="background_color_picker"
            )

            text_color = st.color_picker(
                "Text Color",
                preferences["custom_colors"]["text"],
                key="text_color_picker"
            )

            accent_color = st.color_picker(
                "Accent Color",
                preferences["custom_colors"]["accent"],
                key="accent_color_picker"
            )

        with col2:
            widget_bg_color = st.color_picker(
                "Widget Background",
                preferences["custom_colors"]["widget_background"],
                key="widget_bg_color_picker"
            )

            widget_border_color = st.color_picker(
                "Widget Border",
                preferences["custom_colors"]["widget_border"],
                key="widget_border_color_picker"
            )

        # Update custom colors in preferences
        custom_colors = {
            "background": background_color,
            "text": text_color,
            "widget_background": widget_bg_color,
            "widget_border": widget_border_color,
            "accent": accent_color,
            "container_background": f"rgba({int(background_color[1:3], 16)}, {int(background_color[3:5], 16)}, {int(background_color[5:7], 16)}, 0.5)"
        }

        # Apply custom colors when changed
        if (preferences["custom_colors"]["background"] != background_color or
            preferences["custom_colors"]["text"] != text_color or
            preferences["custom_colors"]["widget_background"] != widget_bg_color or
            preferences["custom_colors"]["widget_border"] != widget_border_color or
            preferences["custom_colors"]["accent"] != accent_color):

            preferences["custom_colors"] = custom_colors
            update_preference("custom_colors", custom_colors)

            # Apply theme with custom colors
            apply_theme("custom", custom_colors)

        # Preview button
        if st.button("Preview Custom Theme"):
            apply_theme("custom", custom_colors)
            st.success("Custom theme applied. Save preferences to keep these changes.")

    st.markdown("---")

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

def render_accessibility_tab() -> None:
    """Render the accessibility preferences tab."""
    create_responsive_container(lambda: _render_accessibility_content())

def _render_accessibility_content() -> None:
    """Render the content for the accessibility tab."""
    preferences = st.session_state.user_preferences

    # High contrast mode
    high_contrast = st.checkbox(
        "High Contrast Mode",
        value=preferences.get("high_contrast", False),
        key="high_contrast_check",
        on_change=lambda: update_preference("high_contrast", st.session_state.high_contrast_check)
    )

    st.caption("Increases contrast for better visibility")

    # Screen reader optimization
    screen_reader = st.checkbox(
        "Screen Reader Optimization",
        value=preferences.get("screen_reader", False),
        key="screen_reader_check",
        on_change=lambda: update_preference("screen_reader", st.session_state.screen_reader_check)
    )

    st.caption("Adds additional context for screen readers")

    # Reduced motion
    reduced_motion = st.checkbox(
        "Reduced Motion",
        value=preferences.get("reduced_motion", False),
        key="reduced_motion_check",
        on_change=lambda: update_preference("reduced_motion", st.session_state.reduced_motion_check)
    )

    st.caption("Minimizes animations and transitions")

    # Focus indicators
    focus_indicators = st.checkbox(
        "Enhanced Focus Indicators",
        value=preferences.get("focus_indicators", False),
        key="focus_indicators_check",
        on_change=lambda: update_preference("focus_indicators", st.session_state.focus_indicators_check)
    )

    st.caption("Makes keyboard focus more visible")

    # Text spacing
    text_spacing = st.checkbox(
        "Increased Text Spacing",
        value=preferences.get("text_spacing", False),
        key="text_spacing_check",
        on_change=lambda: update_preference("text_spacing", st.session_state.text_spacing_check)
    )

    st.caption("Adds more space between letters, words, and lines")

    st.markdown("---")

    st.markdown("""
    ### Accessibility Statement

    We are committed to ensuring our application is accessible to all users. 
    These settings help customize the experience for your specific needs.

    If you encounter any accessibility issues, please report them to our support team.
    """)

def apply_accessibility_features() -> None:
    """Apply accessibility features based on user preferences."""
    preferences = st.session_state.user_preferences

    # Apply high contrast mode if enabled
    if preferences.get("high_contrast", False):
        apply_high_contrast()

    # Apply screen reader optimizations if enabled
    if preferences.get("screen_reader", False):
        apply_screen_reader_optimizations()

    # Apply reduced motion if enabled
    if preferences.get("reduced_motion", False):
        apply_reduced_motion()

    # Apply enhanced focus indicators if enabled
    if preferences.get("focus_indicators", False):
        apply_focus_indicators()

    # Apply increased text spacing if enabled
    if preferences.get("text_spacing", False):
        apply_text_spacing()

def apply_high_contrast() -> None:
    """Apply high contrast mode CSS."""
    st.markdown("""
    <style>
    /* High contrast mode */
    body {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    a, a:visited {
        color: #ffff00 !important;
    }

    button, .stButton>button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
    }

    .stTextInput input, .stNumberInput input, .stSelectbox, .stMultiselect {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
    }

    .stCheckbox label {
        color: #ffffff !important;
    }

    /* Ensure good contrast for all elements */
    h1, h2, h3, h4, h5, h6, p, span, div, li {
        color: #ffffff !important;
    }

    /* Add borders to distinguish elements */
    .stTabs [data-baseweb="tab-panel"] {
        border: 1px solid #ffffff !important;
        padding: 10px !important;
    }

    .responsive-container {
        background-color: #000000 !important;
        border: 1px solid #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

def apply_screen_reader_optimizations() -> None:
    """Apply screen reader optimizations."""
    # Add ARIA attributes and screen reader only text
    st.markdown("""
    <style>
    /* Screen reader only class */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }
    </style>

    <!-- Add screen reader context -->
    <div class="sr-only" role="status" aria-live="polite">
        Science Data Kit application with navigation and content areas.
    </div>
    """, unsafe_allow_html=True)

def apply_reduced_motion() -> None:
    """Apply reduced motion CSS."""
    st.markdown("""
    <style>
    /* Reduce or eliminate animations and transitions */
    * {
        animation-duration: 0.001s !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.001s !important;
        scroll-behavior: auto !important;
    }
    </style>
    """, unsafe_allow_html=True)

def apply_focus_indicators() -> None:
    """Apply enhanced focus indicators CSS."""
    st.markdown("""
    <style>
    /* Enhanced focus indicators */
    *:focus {
        outline: 3px solid #ffff00 !important;
        outline-offset: 3px !important;
    }

    /* Ensure focus is visible on all interactive elements */
    a:focus, button:focus, input:focus, select:focus, textarea:focus {
        outline: 3px solid #ffff00 !important;
        outline-offset: 3px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def apply_text_spacing() -> None:
    """Apply increased text spacing CSS."""
    st.markdown("""
    <style>
    /* Increased text spacing for better readability */
    body, p, div, span, li, a, button, input, select, textarea {
        letter-spacing: 0.12em !important;
        word-spacing: 0.16em !important;
        line-height: 1.5 !important;
    }

    p {
        margin-bottom: 1.5em !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
            "language": "en",
            "high_contrast": False,
            "screen_reader": False,
            "reduced_motion": False,
            "focus_indicators": False,
            "text_spacing": False,
            "custom_colors": {
                "background": "#ffffff",
                "text": "#31333F",
                "widget_background": "#f0f2f6",
                "widget_border": "#cccccc",
                "accent": "#1E88E5",
                "container_background": "rgba(240, 242, 246, 0.5)"
            }
        }

    render_preferences_page()
