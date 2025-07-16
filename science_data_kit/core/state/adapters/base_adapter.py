"""
Base State Adapter Interface for Science Data Kit

This module defines the interface that all state adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from science_data_kit.core.state.state_types import StateValue

class StateAdapter(ABC):
    """
    Abstract base class for state adapters.
    
    All state adapters must implement these methods to provide a consistent
    interface for the state manager.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def set(self, key: str, value: StateValue, scope: str = "session") -> None:
        """
        Set a value in the state.
        
        Args:
            key: The key to set.
            value: The value to set.
            scope: The scope for the state variable.
        """
        pass
    
    @abstractmethod
    def delete(self, key: str, scope: str = "session") -> None:
        """
        Delete a value from the state.
        
        Args:
            key: The key to delete.
            scope: The scope for the state variable.
        """
        pass
    
    @abstractmethod
    def has(self, key: str, scope: str = "session") -> bool:
        """
        Check if a key exists in the state.
        
        Args:
            key: The key to check.
            scope: The scope for the state variable.
            
        Returns:
            True if the key exists, False otherwise.
        """
        pass
    
    @abstractmethod
    def clear(self, scope: str = "session") -> None:
        """
        Clear all values in the state.
        
        Args:
            scope: The scope for the state variables.
        """
        pass
    
    @abstractmethod
    def keys(self, scope: str = "session") -> List[str]:
        """
        Get all keys in the state.
        
        Args:
            scope: The scope for the state variables.
            
        Returns:
            A list of all keys in the state.
        """
        pass
    
    @abstractmethod
    def items(self, scope: str = "session") -> Dict[str, StateValue]:
        """
        Get all key-value pairs in the state.
        
        Args:
            scope: The scope for the state variables.
            
        Returns:
            A dictionary of all key-value pairs in the state.
        """
        pass