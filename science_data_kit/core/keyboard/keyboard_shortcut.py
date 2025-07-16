"""
Keyboard Shortcut Module for Science Data Kit

This module defines the KeyboardShortcut class, which represents a keyboard shortcut
in a framework-agnostic way.
"""

from typing import Callable, Optional, Dict, Any


class KeyboardShortcut:
    """
    Class representing a keyboard shortcut in a framework-agnostic way.
    
    This class defines a keyboard shortcut with a key combination, description,
    action, and scope. It can be used across different UI frameworks.
    """
    
    def __init__(
        self, 
        key: str, 
        description: str, 
        action: Callable, 
        scope: str = "global",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a keyboard shortcut.
        
        Args:
            key: The key combination (e.g., "Ctrl+S", "Alt+F")
            description: Description of what the shortcut does
            action: Function to call when the shortcut is triggered
            scope: Scope of the shortcut (global, page, component)
            metadata: Additional metadata for the shortcut (framework-specific)
        """
        self.key = key
        self.description = description
        self.action = action
        self.scope = scope
        self.metadata = metadata or {}
        
    def __str__(self) -> str:
        """Return a string representation of the shortcut."""
        return f"{self.key}: {self.description}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the shortcut to a dictionary representation.
        
        Returns:
            Dictionary representation of the shortcut
        """
        return {
            "key": self.key,
            "description": self.description,
            "scope": self.scope,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], action: Callable) -> 'KeyboardShortcut':
        """
        Create a shortcut from a dictionary representation.
        
        Args:
            data: Dictionary representation of the shortcut
            action: Function to call when the shortcut is triggered
            
        Returns:
            A new KeyboardShortcut instance
        """
        return cls(
            key=data["key"],
            description=data["description"],
            action=action,
            scope=data.get("scope", "global"),
            metadata=data.get("metadata", {})
        )