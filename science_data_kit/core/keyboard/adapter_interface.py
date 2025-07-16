"""
Keyboard Adapter Interface for Science Data Kit

This module defines the interface that all keyboard adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List

from science_data_kit.core.keyboard.keyboard_shortcut import KeyboardShortcut


class KeyboardAdapterInterface(ABC):
    """
    Interface for keyboard adapters.
    
    This abstract class defines the interface that all keyboard adapters must implement.
    Each UI framework (Streamlit, Flask, React, etc.) should have its own adapter
    implementation that conforms to this interface.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the keyboard adapter.
        
        This method should set up any necessary event listeners or other
        framework-specific initialization.
        """
        pass
    
    @abstractmethod
    def register_shortcut(self, shortcut: KeyboardShortcut) -> None:
        """
        Register a keyboard shortcut with the adapter.
        
        Args:
            shortcut: The keyboard shortcut to register
        """
        pass
    
    @abstractmethod
    def unregister_shortcut(self, key: str) -> None:
        """
        Unregister a keyboard shortcut.
        
        Args:
            key: The key combination of the shortcut to unregister
        """
        pass
    
    @abstractmethod
    def handle_events(self) -> None:
        """
        Handle keyboard events.
        
        This method should be called regularly to process any pending keyboard events.
        """
        pass
    
    @abstractmethod
    def show_help(self, shortcuts: Dict[str, KeyboardShortcut]) -> None:
        """
        Show a help dialog with the registered shortcuts.
        
        Args:
            shortcuts: Dictionary of registered shortcuts
        """
        pass
    
    @abstractmethod
    def get_current_event(self) -> Optional[Dict[str, Any]]:
        """
        Get the current keyboard event.
        
        Returns:
            Dictionary containing information about the current keyboard event,
            or None if there is no current event
        """
        pass
    
    @abstractmethod
    def clear_current_event(self) -> None:
        """
        Clear the current keyboard event.
        
        This method should be called after handling an event to prevent it
        from being processed multiple times.
        """
        pass
    
    @abstractmethod
    def on_shortcut_triggered(self, callback: Callable[[KeyboardShortcut], None]) -> None:
        """
        Register a callback to be called when a shortcut is triggered.
        
        Args:
            callback: Function to call when a shortcut is triggered
        """
        pass
    
    @abstractmethod
    def get_supported_keys(self) -> List[str]:
        """
        Get a list of keys supported by this adapter.
        
        Returns:
            List of key names supported by this adapter
        """
        pass