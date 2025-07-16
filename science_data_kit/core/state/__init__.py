"""
Framework-Agnostic State Management Module for Science Data Kit

This module provides a unified state management system that works across different
frontend frameworks (Streamlit, Flask, React, etc.). It includes a core StateManager
class and framework-specific adapters.
"""

from science_data_kit.core.state.state_manager import StateManager
from science_data_kit.core.state.state_types import StateValue, StateChangeCallback

__all__ = ['StateManager', 'StateValue', 'StateChangeCallback']