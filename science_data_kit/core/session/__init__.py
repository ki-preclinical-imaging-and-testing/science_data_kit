"""
Session Management Module for Science Data Kit

This package provides session management functionality for the Science Data Kit,
including session configuration, resource registry, and session state management.
"""

from .config import load_session_config, save_session_config, SessionConfig
from .registry import ResourceRegistry, Resource

__all__ = [
    'load_session_config', 'save_session_config', 'SessionConfig',
    'ResourceRegistry', 'Resource'
]