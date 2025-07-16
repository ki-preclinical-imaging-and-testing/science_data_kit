"""
Type definitions for the state management system.

This module defines the types used in the state management system, including
the StateValue type and the StateChangeCallback type.
"""

from typing import Any, Callable, Dict, List, Optional, Union, TypeVar, Generic

# Define the possible types for state values
StateValue = Union[str, int, float, bool, List[Any], Dict[str, Any], None]

# Define the type for state change callbacks
StateChangeCallback = Callable[[str, StateValue, StateValue], None]

# Define a type for serializable state
SerializableState = Dict[str, StateValue]

# Define a type for state adapters
StateAdapterT = TypeVar('StateAdapterT')

class StateScope:
    """Enum-like class for state scopes."""
    # Global state shared across all users
    GLOBAL = "global"
    # User-specific state
    USER = "user"
    # Session-specific state (default)
    SESSION = "session"
    # Request-specific state (for web frameworks)
    REQUEST = "request"
    # Component-specific state (for UI components)
    COMPONENT = "component"