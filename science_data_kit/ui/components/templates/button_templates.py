"""
Button Templates for Science Data Kit

This module provides standardized button templates for use across the application.
"""

import streamlit as st
from typing import Optional, Callable, Any

# Import UI constants
try:
    from science_data_kit.ui.components.ui_constants import *
except ImportError:
    # Default values if constants are not available
    COLOR_PRIMARY = "#4CAF50"
    COLOR_SECONDARY = "#2196F3"
    COLOR_DANGER = "#F44336"
    COLOR_WARNING = "#FF9800"
    COLOR_INFO = "#2196F3"
    COLOR_SUCCESS = "#4CAF50"

def primary_button(label: str, key: Optional[str] = None, on_click: Optional[Callable] = None, args: tuple = (), kwargs: dict = None, help: Optional[str] = None, disabled: bool = False) -> bool:
    """
    Create a primary button with standardized styling.
    
    Args:
        label: The text to display on the button
        key: An optional key that uniquely identifies this button
        on_click: An optional callback invoked when this button is clicked
        args: Optional positional arguments to pass to the callback
        kwargs: Optional keyword arguments to pass to the callback
        help: Optional tooltip shown when the button is hovered
        disabled: Optional flag to disable the button
    
    Returns:
        True if the button was clicked, False otherwise
    """
    kwargs = kwargs or {}
    return st.button(
        label=label,
        key=key,
        on_click=on_click,
        args=args,
        kwargs=kwargs,
        help=help,
        disabled=disabled,
        use_container_width=False
    )

def secondary_button(label: str, key: Optional[str] = None, on_click: Optional[Callable] = None, args: tuple = (), kwargs: dict = None, help: Optional[str] = None, disabled: bool = False) -> bool:
    """
    Create a secondary button with standardized styling.
    
    Args:
        label: The text to display on the button
        key: An optional key that uniquely identifies this button
        on_click: An optional callback invoked when this button is clicked
        args: Optional positional arguments to pass to the callback
        kwargs: Optional keyword arguments to pass to the callback
        help: Optional tooltip shown when the button is hovered
        disabled: Optional flag to disable the button
    
    Returns:
        True if the button was clicked, False otherwise
    """
    kwargs = kwargs or {}
    return st.button(
        label=label,
        key=key,
        on_click=on_click,
        args=args,
        kwargs=kwargs,
        help=help,
        disabled=disabled,
        use_container_width=False
    )

def danger_button(label: str, key: Optional[str] = None, on_click: Optional[Callable] = None, args: tuple = (), kwargs: dict = None, help: Optional[str] = None, disabled: bool = False) -> bool:
    """
    Create a danger button with standardized styling.
    
    Args:
        label: The text to display on the button
        key: An optional key that uniquely identifies this button
        on_click: An optional callback invoked when this button is clicked
        args: Optional positional arguments to pass to the callback
        kwargs: Optional keyword arguments to pass to the callback
        help: Optional tooltip shown when the button is hovered
        disabled: Optional flag to disable the button
    
    Returns:
        True if the button was clicked, False otherwise
    """
    kwargs = kwargs or {}
    return st.button(
        label=label,
        key=key,
        on_click=on_click,
        args=args,
        kwargs=kwargs,
        help=help,
        disabled=disabled,
        use_container_width=False
    )

def full_width_button(label: str, key: Optional[str] = None, on_click: Optional[Callable] = None, args: tuple = (), kwargs: dict = None, help: Optional[str] = None, disabled: bool = False) -> bool:
    """
    Create a full-width button with standardized styling.
    
    Args:
        label: The text to display on the button
        key: An optional key that uniquely identifies this button
        on_click: An optional callback invoked when this button is clicked
        args: Optional positional arguments to pass to the callback
        kwargs: Optional keyword arguments to pass to the callback
        help: Optional tooltip shown when the button is hovered
        disabled: Optional flag to disable the button
    
    Returns:
        True if the button was clicked, False otherwise
    """
    kwargs = kwargs or {}
    return st.button(
        label=label,
        key=key,
        on_click=on_click,
        args=args,
        kwargs=kwargs,
        help=help,
        disabled=disabled,
        use_container_width=True
    )