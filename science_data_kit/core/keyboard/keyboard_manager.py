"""
Keyboard Manager Module for Science Data Kit

This module defines the KeyboardManager class, which provides a framework-agnostic
way to manage keyboard shortcuts across different UI frameworks.
"""

from typing import Dict, List, Any, Optional, Callable, Set
import logging

from science_data_kit.core.keyboard.keyboard_shortcut import KeyboardShortcut
from science_data_kit.core.keyboard.adapter_interface import KeyboardAdapterInterface


logger = logging.getLogger(__name__)


class KeyboardManager:
    """
    Framework-agnostic keyboard shortcut manager.
    
    This class provides a centralized way to register and handle keyboard shortcuts
    across different UI frameworks. It uses adapters to interact with specific
    frameworks like Streamlit, Flask, or React.
    """
    
    def __init__(self, adapter: KeyboardAdapterInterface):
        """
        Initialize the keyboard manager.
        
        Args:
            adapter: The adapter for the specific UI framework
        """
        self.adapter = adapter
        self.shortcuts: Dict[str, KeyboardShortcut] = {}
        self.callbacks: Set[Callable[[KeyboardShortcut], None]] = set()
        self.is_initialized = False
        
    def initialize(self) -> None:
        """
        Initialize the keyboard manager.
        
        This method initializes the adapter and sets up event handling.
        """
        if self.is_initialized:
            return
            
        self.adapter.initialize()
        self.adapter.on_shortcut_triggered(self._on_shortcut_triggered)
        self.is_initialized = True
        logger.debug("Keyboard manager initialized")
        
    def register_shortcut(self, shortcut: KeyboardShortcut) -> None:
        """
        Register a keyboard shortcut.
        
        Args:
            shortcut: The keyboard shortcut to register
        """
        if not self.is_initialized:
            self.initialize()
            
        self.shortcuts[shortcut.key] = shortcut
        self.adapter.register_shortcut(shortcut)
        logger.debug(f"Registered shortcut: {shortcut}")
        
    def unregister_shortcut(self, key: str) -> None:
        """
        Unregister a keyboard shortcut.
        
        Args:
            key: The key combination of the shortcut to unregister
        """
        if key in self.shortcuts:
            del self.shortcuts[key]
            self.adapter.unregister_shortcut(key)
            logger.debug(f"Unregistered shortcut: {key}")
        
    def get_shortcut(self, key: str) -> Optional[KeyboardShortcut]:
        """
        Get a registered shortcut by its key.
        
        Args:
            key: The key combination of the shortcut
            
        Returns:
            The shortcut, or None if not found
        """
        return self.shortcuts.get(key)
        
    def get_shortcuts(self, scope: Optional[str] = None) -> Dict[str, KeyboardShortcut]:
        """
        Get all registered shortcuts, optionally filtered by scope.
        
        Args:
            scope: The scope to filter by, or None for all shortcuts
            
        Returns:
            Dictionary of registered shortcuts
        """
        if scope is None:
            return self.shortcuts
            
        return {k: v for k, v in self.shortcuts.items() if v.scope == scope}
        
    def handle_events(self) -> None:
        """
        Handle keyboard events.
        
        This method should be called regularly to process any pending keyboard events.
        """
        if not self.is_initialized:
            self.initialize()
            
        self.adapter.handle_events()
        
    def show_help(self, scope: Optional[str] = None) -> None:
        """
        Show a help dialog with the registered shortcuts.
        
        Args:
            scope: The scope to filter by, or None for all shortcuts
        """
        shortcuts = self.get_shortcuts(scope)
        self.adapter.show_help(shortcuts)
        
    def on_shortcut_triggered(self, callback: Callable[[KeyboardShortcut], None]) -> None:
        """
        Register a callback to be called when a shortcut is triggered.
        
        Args:
            callback: Function to call when a shortcut is triggered
        """
        self.callbacks.add(callback)
        
    def _on_shortcut_triggered(self, shortcut: KeyboardShortcut) -> None:
        """
        Internal callback for when a shortcut is triggered.
        
        Args:
            shortcut: The shortcut that was triggered
        """
        for callback in self.callbacks:
            try:
                callback(shortcut)
            except Exception as e:
                logger.error(f"Error in shortcut callback: {e}")
        
        try:
            shortcut.action()
        except Exception as e:
            logger.error(f"Error executing shortcut action: {e}")
            
    def get_supported_keys(self) -> List[str]:
        """
        Get a list of keys supported by the current adapter.
        
        Returns:
            List of key names supported by the current adapter
        """
        return self.adapter.get_supported_keys()