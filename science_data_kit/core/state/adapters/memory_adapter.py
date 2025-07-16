"""
Memory State Adapter for Science Data Kit

This module provides an in-memory state adapter that stores state in Python dictionaries.
It is used as a fallback when no specific adapter is provided.
"""

from typing import Any, Dict, List, Optional

from science_data_kit.core.state.adapters.base_adapter import StateAdapter
from science_data_kit.core.state.state_types import StateValue

class MemoryStateAdapter(StateAdapter):
    """
    An in-memory state adapter that stores state in Python dictionaries.
    
    This adapter is used as a fallback when no specific adapter is provided.
    It stores state in memory using nested dictionaries for different scopes.
    """
    
    def __init__(self):
        """Initialize the memory state adapter."""
        self._state: Dict[str, Dict[str, StateValue]] = {
            "global": {},
            "user": {},
            "session": {},
            "request": {},
            "component": {},
        }
    
    def get(self, key: str, default: Any = None, scope: str = "session") -> StateValue:
        """
        Get a value from the state.
        
        Args:
            key: The key to get.
            default: The default value to return if the key doesn't exist.
            scope: The scope for the state variable.
            
        Returns:
            The value associated with the key, or the default value if the key doesn't exist.
        """
        return self._state.get(scope, {}).get(key, default)
    
    def set(self, key: str, value: StateValue, scope: str = "session") -> None:
        """
        Set a value in the state.
        
        Args:
            key: The key to set.
            value: The value to set.
            scope: The scope for the state variable.
        """
        if scope not in self._state:
            self._state[scope] = {}
        self._state[scope][key] = value
    
    def delete(self, key: str, scope: str = "session") -> None:
        """
        Delete a value from the state.
        
        Args:
            key: The key to delete.
            scope: The scope for the state variable.
        """
        if scope in self._state and key in self._state[scope]:
            del self._state[scope][key]
    
    def has(self, key: str, scope: str = "session") -> bool:
        """
        Check if a key exists in the state.
        
        Args:
            key: The key to check.
            scope: The scope for the state variable.
            
        Returns:
            True if the key exists, False otherwise.
        """
        return scope in self._state and key in self._state[scope]
    
    def clear(self, scope: str = "session") -> None:
        """
        Clear all values in the state.
        
        Args:
            scope: The scope for the state variables.
        """
        if scope in self._state:
            self._state[scope] = {}
    
    def keys(self, scope: str = "session") -> List[str]:
        """
        Get all keys in the state.
        
        Args:
            scope: The scope for the state variables.
            
        Returns:
            A list of all keys in the state.
        """
        return list(self._state.get(scope, {}).keys())
    
    def items(self, scope: str = "session") -> Dict[str, StateValue]:
        """
        Get all key-value pairs in the state.
        
        Args:
            scope: The scope for the state variables.
            
        Returns:
            A dictionary of all key-value pairs in the state.
        """
        return dict(self._state.get(scope, {}))