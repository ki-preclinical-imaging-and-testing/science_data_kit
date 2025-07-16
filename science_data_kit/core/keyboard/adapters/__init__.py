"""
Keyboard Adapters Module for Science Data Kit

This module provides adapters for different UI frameworks to work with the
framework-agnostic keyboard shortcut system.
"""

from science_data_kit.core.keyboard.adapters.streamlit_adapter import StreamlitKeyboardAdapter
from science_data_kit.core.keyboard.adapters.flask_adapter import FlaskKeyboardAdapter

__all__ = ['StreamlitKeyboardAdapter', 'FlaskKeyboardAdapter']