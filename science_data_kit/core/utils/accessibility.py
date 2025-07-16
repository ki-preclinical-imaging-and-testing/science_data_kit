"""
Accessibility utilities for the Science Data Kit.

This module provides utilities for improving accessibility, including keyboard
navigation and screen reader support.
"""

from typing import Any, Callable, Dict, List, Optional, Union
import logging
import time

from science_data_kit.core.utils.error_handling import get_logger


class KeyboardNavigationManager:
    """
    Manages keyboard navigation for components.
    
    This class provides utilities for implementing keyboard navigation,
    including focus management, keyboard shortcuts, and ARIA attributes.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the KeyboardNavigationManager.
        
        Args:
            logger: Optional logger instance. If not provided, a logger will be created.
        """
        self.logger = logger or get_logger(__name__)
        self.focusable_elements: Dict[str, Dict[str, Any]] = {}
        self.focus_order: List[str] = []
        self.current_focus_index: int = -1
    
    def register_focusable_element(self, element_id: str, element_data: Dict[str, Any]) -> None:
        """
        Register a focusable element.
        
        Args:
            element_id: Unique identifier for the element.
            element_data: Data associated with the element, including callbacks for focus events.
        """
        self.focusable_elements[element_id] = element_data
        if element_id not in self.focus_order:
            self.focus_order.append(element_id)
        self.logger.debug(f"Registered focusable element: {element_id}")
    
    def set_focus_order(self, element_ids: List[str]) -> None:
        """
        Set the order in which elements should receive focus when navigating with the keyboard.
        
        Args:
            element_ids: List of element IDs in the desired focus order.
        """
        # Validate that all element IDs are registered
        for element_id in element_ids:
            if element_id not in self.focusable_elements:
                self.logger.warning(f"Element ID {element_id} is not registered as focusable")
        
        # Set the focus order
        self.focus_order = [element_id for element_id in element_ids if element_id in self.focusable_elements]
        self.logger.debug(f"Set focus order: {self.focus_order}")
    
    def focus_element(self, element_id: str) -> bool:
        """
        Focus a specific element.
        
        Args:
            element_id: ID of the element to focus.
            
        Returns:
            True if the element was focused, False otherwise.
        """
        if element_id not in self.focusable_elements:
            self.logger.warning(f"Cannot focus element {element_id}: not registered as focusable")
            return False
        
        element_data = self.focusable_elements[element_id]
        if "on_focus" in element_data and callable(element_data["on_focus"]):
            try:
                element_data["on_focus"]()
                self.current_focus_index = self.focus_order.index(element_id)
                self.logger.debug(f"Focused element: {element_id}")
                return True
            except Exception as e:
                self.logger.error(f"Error focusing element {element_id}: {str(e)}")
                return False
        else:
            self.logger.warning(f"Element {element_id} does not have an on_focus callback")
            return False
    
    def focus_next(self) -> bool:
        """
        Focus the next element in the focus order.
        
        Returns:
            True if an element was focused, False otherwise.
        """
        if not self.focus_order:
            self.logger.warning("Cannot focus next element: no focusable elements registered")
            return False
        
        next_index = (self.current_focus_index + 1) % len(self.focus_order)
        next_element_id = self.focus_order[next_index]
        return self.focus_element(next_element_id)
    
    def focus_previous(self) -> bool:
        """
        Focus the previous element in the focus order.
        
        Returns:
            True if an element was focused, False otherwise.
        """
        if not self.focus_order:
            self.logger.warning("Cannot focus previous element: no focusable elements registered")
            return False
        
        prev_index = (self.current_focus_index - 1) % len(self.focus_order)
        prev_element_id = self.focus_order[prev_index]
        return self.focus_element(prev_element_id)
    
    def handle_key_event(self, key: str, modifiers: Optional[List[str]] = None) -> bool:
        """
        Handle a keyboard event.
        
        Args:
            key: The key that was pressed.
            modifiers: Optional list of modifier keys (e.g., ["shift", "ctrl"]).
            
        Returns:
            True if the event was handled, False otherwise.
        """
        modifiers = modifiers or []
        
        # Handle Tab and Shift+Tab for focus navigation
        if key == "Tab":
            if "shift" in modifiers:
                return self.focus_previous()
            else:
                return self.focus_next()
        
        # If an element has focus, let it handle the key event
        if 0 <= self.current_focus_index < len(self.focus_order):
            element_id = self.focus_order[self.current_focus_index]
            element_data = self.focusable_elements[element_id]
            
            if "on_key" in element_data and callable(element_data["on_key"]):
                try:
                    return element_data["on_key"](key, modifiers)
                except Exception as e:
                    self.logger.error(f"Error handling key event for element {element_id}: {str(e)}")
        
        return False


class ScreenReaderHelper:
    """
    Provides utilities for improving screen reader support.
    
    This class helps generate appropriate ARIA attributes and manage
    announcements for screen readers.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the ScreenReaderHelper.
        
        Args:
            logger: Optional logger instance. If not provided, a logger will be created.
        """
        self.logger = logger or get_logger(__name__)
        self.announcements: List[Dict[str, Any]] = []
    
    def generate_aria_attributes(self, role: str, label: Optional[str] = None,
                                 description: Optional[str] = None,
                                 expanded: Optional[bool] = None,
                                 controls: Optional[str] = None,
                                 live: Optional[str] = None,
                                 relevant: Optional[str] = None,
                                 busy: Optional[bool] = None,
                                 hidden: Optional[bool] = None,
                                 additional_attrs: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Generate ARIA attributes for an element.
        
        Args:
            role: The ARIA role of the element.
            label: Optional accessible label for the element.
            description: Optional description for the element.
            expanded: Optional boolean indicating if the element is expanded.
            controls: Optional ID of the element controlled by this element.
            live: Optional politeness setting for live regions ("off", "polite", "assertive").
            relevant: Optional relevance setting for live regions.
            busy: Optional boolean indicating if the element is busy.
            hidden: Optional boolean indicating if the element is hidden from screen readers.
            additional_attrs: Optional dictionary of additional ARIA attributes.
            
        Returns:
            Dictionary of ARIA attributes.
        """
        aria_attrs = {"aria-role": role}
        
        if label is not None:
            aria_attrs["aria-label"] = label
        
        if description is not None:
            aria_attrs["aria-description"] = description
        
        if expanded is not None:
            aria_attrs["aria-expanded"] = "true" if expanded else "false"
        
        if controls is not None:
            aria_attrs["aria-controls"] = controls
        
        if live is not None:
            aria_attrs["aria-live"] = live
        
        if relevant is not None:
            aria_attrs["aria-relevant"] = relevant
        
        if busy is not None:
            aria_attrs["aria-busy"] = "true" if busy else "false"
        
        if hidden is not None:
            aria_attrs["aria-hidden"] = "true" if hidden else "false"
        
        if additional_attrs:
            aria_attrs.update(additional_attrs)
        
        return aria_attrs
    
    def announce(self, message: str, priority: str = "polite") -> None:
        """
        Add an announcement for screen readers.
        
        Args:
            message: The message to announce.
            priority: The priority of the announcement ("polite" or "assertive").
        """
        announcement = {
            "message": message,
            "priority": priority,
            "timestamp": time.time()
        }
        self.announcements.append(announcement)
        self.logger.debug(f"Added screen reader announcement: {message} (priority: {priority})")
    
    def get_announcements(self, clear: bool = True) -> List[Dict[str, Any]]:
        """
        Get all pending announcements.
        
        Args:
            clear: Whether to clear the announcements after retrieving them.
            
        Returns:
            List of announcement dictionaries.
        """
        announcements = self.announcements.copy()
        if clear:
            self.announcements = []
        return announcements


class AccessibilityManager:
    """
    Central manager for accessibility features.
    
    This class provides a unified interface for keyboard navigation and
    screen reader support.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the AccessibilityManager.
        
        Args:
            logger: Optional logger instance. If not provided, a logger will be created.
        """
        self.logger = logger or get_logger(__name__)
        self.keyboard_manager = KeyboardNavigationManager(logger)
        self.screen_reader_helper = ScreenReaderHelper(logger)
        self.high_contrast_mode = False
        self.text_scaling_factor = 1.0
    
    def register_focusable_element(self, element_id: str, on_focus: Callable[[], None],
                                   on_key: Optional[Callable[[str, List[str]], bool]] = None,
                                   element_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a focusable element.
        
        Args:
            element_id: Unique identifier for the element.
            on_focus: Callback to execute when the element receives focus.
            on_key: Optional callback to execute when a key is pressed while the element has focus.
            element_data: Optional additional data associated with the element.
        """
        data = element_data or {}
        data["on_focus"] = on_focus
        if on_key:
            data["on_key"] = on_key
        
        self.keyboard_manager.register_focusable_element(element_id, data)
    
    def set_focus_order(self, element_ids: List[str]) -> None:
        """
        Set the order in which elements should receive focus when navigating with the keyboard.
        
        Args:
            element_ids: List of element IDs in the desired focus order.
        """
        self.keyboard_manager.set_focus_order(element_ids)
    
    def focus_element(self, element_id: str) -> bool:
        """
        Focus a specific element.
        
        Args:
            element_id: ID of the element to focus.
            
        Returns:
            True if the element was focused, False otherwise.
        """
        return self.keyboard_manager.focus_element(element_id)
    
    def handle_key_event(self, key: str, modifiers: Optional[List[str]] = None) -> bool:
        """
        Handle a keyboard event.
        
        Args:
            key: The key that was pressed.
            modifiers: Optional list of modifier keys (e.g., ["shift", "ctrl"]).
            
        Returns:
            True if the event was handled, False otherwise.
        """
        return self.keyboard_manager.handle_key_event(key, modifiers)
    
    def generate_aria_attributes(self, role: str, **kwargs) -> Dict[str, str]:
        """
        Generate ARIA attributes for an element.
        
        Args:
            role: The ARIA role of the element.
            **kwargs: Additional ARIA attributes.
            
        Returns:
            Dictionary of ARIA attributes.
        """
        return self.screen_reader_helper.generate_aria_attributes(role, **kwargs)
    
    def announce(self, message: str, priority: str = "polite") -> None:
        """
        Add an announcement for screen readers.
        
        Args:
            message: The message to announce.
            priority: The priority of the announcement ("polite" or "assertive").
        """
        self.screen_reader_helper.announce(message, priority)
    
    def toggle_high_contrast_mode(self) -> bool:
        """
        Toggle high contrast mode.
        
        Returns:
            The new state of high contrast mode.
        """
        self.high_contrast_mode = not self.high_contrast_mode
        self.logger.info(f"High contrast mode {'enabled' if self.high_contrast_mode else 'disabled'}")
        return self.high_contrast_mode
    
    def set_text_scaling_factor(self, factor: float) -> None:
        """
        Set the text scaling factor.
        
        Args:
            factor: The scaling factor for text (1.0 = normal size).
        """
        if factor <= 0:
            self.logger.warning(f"Invalid text scaling factor: {factor}. Must be positive.")
            return
        
        self.text_scaling_factor = factor
        self.logger.info(f"Text scaling factor set to {factor}")
    
    def get_accessibility_settings(self) -> Dict[str, Any]:
        """
        Get the current accessibility settings.
        
        Returns:
            Dictionary of accessibility settings.
        """
        return {
            "high_contrast_mode": self.high_contrast_mode,
            "text_scaling_factor": self.text_scaling_factor,
            "announcements": self.screen_reader_helper.get_announcements(clear=False)
        }


# Create a singleton instance of the AccessibilityManager
accessibility_manager = AccessibilityManager()


def get_accessibility_manager() -> AccessibilityManager:
    """
    Get the singleton instance of the AccessibilityManager.
    
    Returns:
        The AccessibilityManager instance.
    """
    return accessibility_manager