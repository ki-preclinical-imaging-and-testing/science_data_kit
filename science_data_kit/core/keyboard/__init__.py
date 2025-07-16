"""
Keyboard Shortcuts Module for Science Data Kit

This module provides a framework-agnostic keyboard shortcut system that can be used
across different UI frameworks (Streamlit, Flask, React, etc.).
"""

from science_data_kit.core.keyboard.keyboard_shortcut import KeyboardShortcut
from science_data_kit.core.keyboard.keyboard_manager import KeyboardManager
from science_data_kit.core.keyboard.adapter_interface import KeyboardAdapterInterface

__all__ = ['KeyboardShortcut', 'KeyboardManager', 'KeyboardAdapterInterface']