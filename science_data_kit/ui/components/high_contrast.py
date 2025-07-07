"""
High Contrast Mode for Science Data Kit

This module provides a high contrast viewing mode for users with visual impairments.
It includes functions for toggling high contrast mode, applying high contrast styles,
and persisting user preferences.
"""

import streamlit as st
from typing import Dict, Optional, List, Union

# High contrast color schemes
HIGH_CONTRAST_SCHEMES = {
    "dark": {
        "background": "#000000",
        "text": "#FFFFFF",
        "primary": "#FFFF00",
        "secondary": "#00FFFF",
        "accent": "#FF00FF",
        "border": "#FFFFFF",
        "link": "#00FFFF",
        "button": "#FFFF00",
        "button_text": "#000000",
        "input_bg": "#000000",
        "input_text": "#FFFFFF",
        "input_border": "#FFFFFF",
        "success": "#00FF00",
        "warning": "#FFFF00",
        "error": "#FF0000",
        "info": "#00FFFF"
    },
    "light": {
        "background": "#FFFFFF",
        "text": "#000000",
        "primary": "#000080",
        "secondary": "#800000",
        "accent": "#008000",
        "border": "#000000",
        "link": "#000080",
        "button": "#000080",
        "button_text": "#FFFFFF",
        "input_bg": "#FFFFFF",
        "input_text": "#000000",
        "input_border": "#000000",
        "success": "#008000",
        "warning": "#800000",
        "error": "#FF0000",
        "info": "#000080"
    }
}

def initialize_high_contrast_mode() -> None:
    """
    Initialize high contrast mode in the application.
    
    This function sets up the session state for high contrast mode and adds
    the toggle control to the sidebar.
    """
    # Initialize session state for high contrast mode if not already set
    if "high_contrast_enabled" not in st.session_state:
        st.session_state.high_contrast_enabled = False
    
    if "high_contrast_scheme" not in st.session_state:
        st.session_state.high_contrast_scheme = "dark"
    
    # Add high contrast toggle to sidebar
    with st.sidebar:
        st.markdown("### Accessibility")
        
        # High contrast toggle
        high_contrast = st.checkbox(
            "High Contrast Mode", 
            value=st.session_state.high_contrast_enabled,
            key="high_contrast_toggle"
        )
        
        # Update session state when toggle changes
        if high_contrast != st.session_state.high_contrast_enabled:
            st.session_state.high_contrast_enabled = high_contrast
            st.experimental_rerun()
        
        # Scheme selector (only shown when high contrast is enabled)
        if st.session_state.high_contrast_enabled:
            scheme = st.radio(
                "Contrast Scheme",
                options=["Dark", "Light"],
                index=0 if st.session_state.high_contrast_scheme == "dark" else 1,
                key="high_contrast_scheme_selector"
            )
            
            # Update session state when scheme changes
            new_scheme = scheme.lower()
            if new_scheme != st.session_state.high_contrast_scheme:
                st.session_state.high_contrast_scheme = new_scheme
                st.experimental_rerun()
    
    # Apply high contrast styles if enabled
    if st.session_state.high_contrast_enabled:
        apply_high_contrast_styles(st.session_state.high_contrast_scheme)

def apply_high_contrast_styles(scheme: str = "dark") -> None:
    """
    Apply high contrast styles to the application.
    
    Args:
        scheme (str): The high contrast scheme to use ('dark' or 'light')
    """
    # Get the color scheme
    colors = HIGH_CONTRAST_SCHEMES.get(scheme, HIGH_CONTRAST_SCHEMES["dark"])
    
    # Create CSS for high contrast mode
    css = f"""
    <style>
    /* High Contrast Mode - {scheme.capitalize()} Scheme */
    
    /* Base styles */
    body {{
        background-color: {colors["background"]} !important;
        color: {colors["text"]} !important;
    }}
    
    /* Text elements */
    h1, h2, h3, h4, h5, h6, p, span, div, label {{
        color: {colors["text"]} !important;
    }}
    
    /* Links */
    a, a:visited {{
        color: {colors["link"]} !important;
        text-decoration: underline !important;
    }}
    
    a:hover, a:focus {{
        color: {colors["accent"]} !important;
        text-decoration: underline !important;
    }}
    
    /* Buttons */
    button, .stButton>button {{
        background-color: {colors["button"]} !important;
        color: {colors["button_text"]} !important;
        border: 2px solid {colors["border"]} !important;
    }}
    
    button:hover, .stButton>button:hover {{
        background-color: {colors["accent"]} !important;
    }}
    
    /* Inputs */
    input, textarea, select, .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: {colors["input_bg"]} !important;
        color: {colors["input_text"]} !important;
        border: 2px solid {colors["input_border"]} !important;
    }}
    
    /* Checkboxes and radio buttons */
    .stCheckbox>div>div>label, .stRadio>div>div>label {{
        color: {colors["text"]} !important;
    }}
    
    /* Sliders */
    .stSlider>div>div>div>div {{
        background-color: {colors["primary"]} !important;
    }}
    
    /* Dataframes and tables */
    .dataframe, table {{
        border: 2px solid {colors["border"]} !important;
    }}
    
    .dataframe th, table th {{
        background-color: {colors["primary"]} !important;
        color: {colors["background"]} !important;
        border: 1px solid {colors["border"]} !important;
    }}
    
    .dataframe td, table td {{
        background-color: {colors["background"]} !important;
        color: {colors["text"]} !important;
        border: 1px solid {colors["border"]} !important;
    }}
    
    /* Sidebar */
    .sidebar .sidebar-content {{
        background-color: {colors["background"]} !important;
        border-right: 2px solid {colors["border"]} !important;
    }}
    
    /* Charts and visualizations */
    .stPlot {{
        border: 2px solid {colors["border"]} !important;
    }}
    
    /* Focus indicators */
    :focus {{
        outline: 3px solid {colors["accent"]} !important;
        outline-offset: 2px !important;
    }}
    
    /* Status messages */
    .success, .stSuccess {{
        color: {colors["success"]} !important;
        border: 1px solid {colors["success"]} !important;
    }}
    
    .warning, .stWarning {{
        color: {colors["warning"]} !important;
        border: 1px solid {colors["warning"]} !important;
    }}
    
    .error, .stError {{
        color: {colors["error"]} !important;
        border: 1px solid {colors["error"]} !important;
    }}
    
    .info, .stInfo {{
        color: {colors["info"]} !important;
        border: 1px solid {colors["info"]} !important;
    }}
    </style>
    """
    
    # Apply the CSS
    st.markdown(css, unsafe_allow_html=True)

def toggle_high_contrast_mode() -> None:
    """
    Toggle high contrast mode on or off.
    
    This function toggles the high contrast mode and triggers a rerun of the app.
    """
    if "high_contrast_enabled" in st.session_state:
        st.session_state.high_contrast_enabled = not st.session_state.high_contrast_enabled
        st.experimental_rerun()
    else:
        st.session_state.high_contrast_enabled = True
        st.session_state.high_contrast_scheme = "dark"
        st.experimental_rerun()

def set_high_contrast_scheme(scheme: str) -> None:
    """
    Set the high contrast color scheme.
    
    Args:
        scheme (str): The high contrast scheme to use ('dark' or 'light')
    """
    if scheme not in HIGH_CONTRAST_SCHEMES:
        scheme = "dark"
    
    st.session_state.high_contrast_scheme = scheme
    
    # Enable high contrast mode if it's not already enabled
    if not st.session_state.get("high_contrast_enabled", False):
        st.session_state.high_contrast_enabled = True
    
    st.experimental_rerun()

def get_high_contrast_status() -> Dict[str, Union[bool, str]]:
    """
    Get the current status of high contrast mode.
    
    Returns:
        Dict: Dictionary with 'enabled' (bool) and 'scheme' (str) keys
    """
    return {
        "enabled": st.session_state.get("high_contrast_enabled", False),
        "scheme": st.session_state.get("high_contrast_scheme", "dark")
    }

def apply_high_contrast_to_chart(fig, scheme: Optional[str] = None) -> None:
    """
    Apply high contrast colors to a matplotlib or plotly figure.
    
    Args:
        fig: The matplotlib or plotly figure to modify
        scheme (str, optional): The high contrast scheme to use. If None, uses the current scheme.
    """
    if scheme is None and "high_contrast_scheme" in st.session_state:
        scheme = st.session_state.high_contrast_scheme
    else:
        scheme = "dark"
    
    colors = HIGH_CONTRAST_SCHEMES.get(scheme, HIGH_CONTRAST_SCHEMES["dark"])
    
    # Check if it's a matplotlib figure
    if hasattr(fig, 'set_facecolor'):
        # It's a matplotlib figure
        fig.set_facecolor(colors["background"])
        
        # Update axes
        for ax in fig.get_axes():
            ax.set_facecolor(colors["background"])
            ax.spines['bottom'].set_color(colors["border"])
            ax.spines['top'].set_color(colors["border"])
            ax.spines['left'].set_color(colors["border"])
            ax.spines['right'].set_color(colors["border"])
            
            # Update text colors
            ax.title.set_color(colors["text"])
            ax.xaxis.label.set_color(colors["text"])
            ax.yaxis.label.set_color(colors["text"])
            
            # Update tick colors
            ax.tick_params(axis='x', colors=colors["text"])
            ax.tick_params(axis='y', colors=colors["text"])
            
            # Update legend
            legend = ax.get_legend()
            if legend:
                legend.set_facecolor(colors["background"])
                for text in legend.get_texts():
                    text.set_color(colors["text"])
    
    # Check if it's a plotly figure
    elif hasattr(fig, 'update_layout'):
        # It's a plotly figure
        fig.update_layout(
            paper_bgcolor=colors["background"],
            plot_bgcolor=colors["background"],
            font=dict(color=colors["text"]),
            title=dict(font=dict(color=colors["text"])),
            legend=dict(
                font=dict(color=colors["text"]),
                bgcolor=colors["background"],
                bordercolor=colors["border"]
            )
        )
        
        # Update axes
        fig.update_xaxes(
            color=colors["text"],
            linecolor=colors["border"],
            gridcolor=colors["border"]
        )
        
        fig.update_yaxes(
            color=colors["text"],
            linecolor=colors["border"],
            gridcolor=colors["border"]
        )