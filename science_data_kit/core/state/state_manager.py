"""
State Manager for Science Data Kit

This module provides a framework-agnostic state management system that can be used
with different frontend frameworks (Streamlit, Flask, React, etc.).
"""

import logging
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union, cast

from science_data_kit.core.state.state_types import (
    StateValue, StateChangeCallback, SerializableState, StateScope
)

logger = logging.getLogger(__name__)

class StateManager:
    """
    A framework-agnostic state manager that provides a unified API for state management
    across different frontend frameworks.
    
    This class uses adapters to interact with the underlying state storage mechanism
    of each framework (e.g., Streamlit's session_state, Flask's session, etc.).
    """
    
    def __init__(self, adapter=None, default_scope: str = StateScope.SESSION):
        """
        Initialize the state manager with a specific adapter.
        
        Args:
            adapter: The adapter to use for state storage. If None, a memory adapter will be used.
            default_scope: The default scope for state variables.
        """
        self._adapter = adapter
        self._callbacks: Dict[str, List[StateChangeCallback]] = {}
        self._default_scope = default_scope
        
        # If no adapter is provided, use an in-memory adapter
        if self._adapter is None:
            from science_data_kit.core.state.adapters.memory_adapter import MemoryStateAdapter
            self._adapter = MemoryStateAdapter()
    
    def initialize(self, defaults: Dict[str, StateValue], scope: Optional[str] = None) -> None:
        """
        Initialize the state with default values.
        
        Args:
            defaults: A dictionary of default values.
            scope: The scope for the state variables. If None, the default scope is used.
        """
        scope = scope or self._default_scope
        for key, value in defaults.items():
            if not self.has(key, scope):
                self.set(key, value, scope)
    
    def get(self, key: str, default: Any = None, scope: Optional[str] = None) -> StateValue:
        """
        Get a value from the state.
        
        Args:
            key: The key to get.
            default: The default value to return if the key doesn't exist.
            scope: The scope for the state variable. If None, the default scope is used.
            
        Returns:
            The value associated with the key, or the default value if the key doesn't exist.
        """
        scope = scope or self._default_scope
        return self._adapter.get(key, default, scope)
    
    def set(self, key: str, value: StateValue, scope: Optional[str] = None) -> None:
        """
        Set a value in the state.
        
        Args:
            key: The key to set.
            value: The value to set.
            scope: The scope for the state variable. If None, the default scope is used.
        """
        scope = scope or self._default_scope
        old_value = self.get(key, scope=scope)
        self._adapter.set(key, value, scope)
        
        # Trigger callbacks
        if key in self._callbacks:
            for callback in self._callbacks[key]:
                try:
                    callback(key, old_value, value)
                except Exception as e:
                    logger.error(f"Error in state change callback for key {key}: {e}")
    
    def delete(self, key: str, scope: Optional[str] = None) -> None:
        """
        Delete a value from the state.
        
        Args:
            key: The key to delete.
            scope: The scope for the state variable. If None, the default scope is used.
        """
        scope = scope or self._default_scope
        self._adapter.delete(key, scope)
    
    def has(self, key: str, scope: Optional[str] = None) -> bool:
        """
        Check if a key exists in the state.
        
        Args:
            key: The key to check.
            scope: The scope for the state variable. If None, the default scope is used.
            
        Returns:
            True if the key exists, False otherwise.
        """
        scope = scope or self._default_scope
        return self._adapter.has(key, scope)
    
    def clear(self, scope: Optional[str] = None) -> None:
        """
        Clear all values in the state.
        
        Args:
            scope: The scope for the state variables. If None, the default scope is used.
        """
        scope = scope or self._default_scope
        self._adapter.clear(scope)
    
    def keys(self, scope: Optional[str] = None) -> List[str]:
        """
        Get all keys in the state.
        
        Args:
            scope: The scope for the state variables. If None, the default scope is used.
            
        Returns:
            A list of all keys in the state.
        """
        scope = scope or self._default_scope
        return self._adapter.keys(scope)
    
    def items(self, scope: Optional[str] = None) -> Dict[str, StateValue]:
        """
        Get all key-value pairs in the state.
        
        Args:
            scope: The scope for the state variables. If None, the default scope is used.
            
        Returns:
            A dictionary of all key-value pairs in the state.
        """
        scope = scope or self._default_scope
        return self._adapter.items(scope)
    
    def on_change(self, key: str, callback: StateChangeCallback) -> None:
        """
        Register a callback to be called when a state variable changes.
        
        Args:
            key: The key to watch.
            callback: The callback function to call when the value changes.
        """
        if key not in self._callbacks:
            self._callbacks[key] = []
        self._callbacks[key].append(callback)
    
    def remove_callback(self, key: str, callback: StateChangeCallback) -> None:
        """
        Remove a callback for a state variable.
        
        Args:
            key: The key to watch.
            callback: The callback function to remove.
        """
        if key in self._callbacks:
            self._callbacks[key].remove(callback)
            if not self._callbacks[key]:
                del self._callbacks[key]
    
    def save_to_file(self, file_path: Union[str, Path], keys: Optional[List[str]] = None, 
                    scope: Optional[str] = None) -> None:
        """
        Save the state to a file.
        
        Args:
            file_path: The path to the file.
            keys: Optional list of keys to save. If None, save all keys.
            scope: The scope for the state variables. If None, the default scope is used.
        """
        scope = scope or self._default_scope
        file_path = Path(file_path)
        
        # Get the state to save
        state_to_save: Dict[str, StateValue] = {}
        if keys:
            for key in keys:
                if self.has(key, scope):
                    state_to_save[key] = self.get(key, scope=scope)
        else:
            state_to_save = self.items(scope)
        
        # Create parent directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        try:
            with open(file_path, 'w') as f:
                json.dump(state_to_save, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state to file: {e}")
    
    def load_from_file(self, file_path: Union[str, Path], scope: Optional[str] = None) -> None:
        """
        Load the state from a file.
        
        Args:
            file_path: The path to the file.
            scope: The scope for the state variables. If None, the default scope is used.
        """
        scope = scope or self._default_scope
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"State file does not exist: {file_path}")
            return
        
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)
            
            for key, value in state.items():
                self.set(key, value, scope)
        except Exception as e:
            logger.error(f"Error loading state from file: {e}")
    
    def get_adapter(self):
        """
        Get the current adapter.
        
        Returns:
            The current adapter.
        """
        return self._adapter
    
    def set_adapter(self, adapter) -> None:
        """
        Set a new adapter.
        
        Args:
            adapter: The new adapter to use.
        """
        self._adapter = adapter