"""
State Adapters for Science Data Kit

This package provides adapters for different frontend frameworks to interact with
the state management system. Each adapter implements the same interface but uses
different underlying storage mechanisms.
"""

from science_data_kit.core.state.adapters.base_adapter import StateAdapter
from science_data_kit.core.state.adapters.memory_adapter import MemoryStateAdapter
from science_data_kit.core.state.adapters.streamlit_adapter import StreamlitStateAdapter
from science_data_kit.core.state.adapters.flask_adapter import FlaskStateAdapter

__all__ = [
    'StateAdapter',
    'MemoryStateAdapter',
    'StreamlitStateAdapter',
    'FlaskStateAdapter',
]