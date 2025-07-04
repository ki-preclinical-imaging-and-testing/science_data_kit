"""
Session Management Module for Science Data Kit

This package provides session management functionality for the Science Data Kit,
including session configuration, resource registry, and session state management.
"""

from .config import load_session_config, save_session_config, SessionConfig
from .registry import ResourceRegistry, Resource
from .session import Session, create_session, load_session, list_sessions, set_active_session, recover_last_session

__all__ = [
    'load_session_config', 'save_session_config', 'SessionConfig',
    'ResourceRegistry', 'Resource',
    'Session', 'create_session', 'load_session', 'list_sessions', 'set_active_session', 'recover_last_session'
]
