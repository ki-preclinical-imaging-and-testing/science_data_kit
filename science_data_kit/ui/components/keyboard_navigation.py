"""
Keyboard Navigation Utilities for Science Data Kit

This module provides utilities for enhancing keyboard navigation in Streamlit applications.
It includes keyboard shortcuts, focus management, and accessibility improvements.

This module now uses the framework-agnostic keyboard shortcut system from the core module.
"""

import streamlit as st
import json
from typing import Dict, List, Any, Optional, Callable, Union
import re
import logging

# Import the framework-agnostic keyboard shortcut system
from science_data_kit.core.keyboard import KeyboardShortcut, KeyboardManager
from science_data_kit.core.keyboard.adapters.streamlit_adapter import StreamlitKeyboardAdapter

# Try to import UI constants
try:
    from science_data_kit.ui.components.ui_constants import COLORS, SPACING
    HAS_UI_CONSTANTS = True
except ImportError:
    HAS_UI_CONSTANTS = False
    # Define fallback constants
    COLORS = {
        "primary": "#4CAF50",
        "secondary": "#2196F3",
        "accent": "#FF9800",
        "focus": "#FFEB3B"
    }
    SPACING = {
        "xs": "0.25rem",
        "sm": "0.5rem",
        "md": "1rem",
        "lg": "1.5rem",
        "xl": "2rem"
    }

logger = logging.getLogger(__name__)

# For backward compatibility, re-export the KeyboardShortcut class
# This allows existing code to continue using the old class
class LegacyKeyboardManager:
    """
    Legacy manager for keyboard shortcuts and navigation.

    This class provides backward compatibility with the old keyboard manager.
    It delegates to the new framework-agnostic KeyboardManager.
    """

    def __init__(self):
        """Initialize the legacy keyboard manager."""
        self.adapter = StreamlitKeyboardAdapter()
        self.manager = KeyboardManager(adapter=self.adapter)
        self.focus_order: List[str] = []
        self.current_focus_index = 0
        self.is_initialized = False

    def register_shortcut(self, shortcut: KeyboardShortcut) -> None:
        """
        Register a keyboard shortcut.

        Args:
            shortcut: The keyboard shortcut to register
        """
        self.manager.register_shortcut(shortcut)

    def register_focus_element(self, element_id: str) -> None:
        """
        Register an element in the focus order.

        Args:
            element_id: ID of the element to register
        """
        if element_id not in self.focus_order:
            self.focus_order.append(element_id)

    def set_focus_order(self, element_ids: List[str]) -> None:
        """
        Set the focus order for the current page.

        Args:
            element_ids: List of element IDs in the desired focus order
        """
        self.focus_order = element_ids
        self.current_focus_index = 0

    def next_focus(self) -> Optional[str]:
        """
        Move focus to the next element in the focus order.

        Returns:
            ID of the next element, or None if there are no elements
        """
        if not self.focus_order:
            return None

        self.current_focus_index = (self.current_focus_index + 1) % len(self.focus_order)
        return self.focus_order[self.current_focus_index]

    def previous_focus(self) -> Optional[str]:
        """
        Move focus to the previous element in the focus order.

        Returns:
            ID of the previous element, or None if there are no elements
        """
        if not self.focus_order:
            return None

        self.current_focus_index = (self.current_focus_index - 1) % len(self.focus_order)
        return self.focus_order[self.current_focus_index]

    def get_current_focus(self) -> Optional[str]:
        """
        Get the currently focused element.

        Returns:
            ID of the currently focused element, or None if there are no elements
        """
        if not self.focus_order:
            return None

        return self.focus_order[self.current_focus_index]

    def initialize_keyboard_listeners(self) -> None:
        """
        Initialize keyboard event listeners.

        This method initializes the keyboard manager and adapter.
        """
        if self.is_initialized:
            return

        self.manager.initialize()
        self.is_initialized = True
        logger.debug("Legacy keyboard manager initialized")

    def handle_keyboard_events(self) -> None:
        """
        Handle keyboard events from the JavaScript listeners.

        This method should be called in the Streamlit app's main loop
        to process keyboard events.
        """
        if not self.is_initialized:
            self.initialize_keyboard_listeners()

        # Handle events using the new manager
        self.manager.handle_events()

        # Handle focus navigation
        event = self.adapter.get_current_event()
        if event:
            key = event.get("key")

            # Handle navigation keys
            if key == "Tab":
                self.next_focus()
            elif key == "Shift+Tab":
                self.previous_focus()


def make_focusable(element_id: str, label: str = "", tooltip: str = "") -> None:
    """
    Make an element focusable with keyboard navigation.

    Args:
        element_id: ID of the element to make focusable
        label: Accessible label for the element
        tooltip: Tooltip text for the element
    """
    # Add ARIA attributes and tabindex
    attributes = f'id="{element_id}" tabindex="0"'

    if label:
        attributes += f' aria-label="{label}"'

    if tooltip:
        attributes += f' title="{tooltip}"'

    # Inject the attributes using HTML
    html = f"""
    <script>
    (function() {{
        // Find the element by ID or create a query selector based on the ID
        let element = document.getElementById('{element_id}');
        if (!element) {{
            // Try to find by a class that might contain the ID
            const possibleClasses = [
                '.{element_id}',
                '[data-testid="{element_id}"]',
                '[data-baseweb="{element_id}"]'
            ];

            for (const selector of possibleClasses) {{
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {{
                    element = elements[0];
                    break;
                }}
            }}
        }}

        if (element) {{
            // Add the attributes
            element.setAttribute('tabindex', '0');
            element.setAttribute('id', '{element_id}');
            {f"element.setAttribute('aria-label', '{label}');" if label else ""}
            {f"element.setAttribute('title', '{tooltip}');" if tooltip else ""}

            // Add focus styles
            element.addEventListener('focus', function() {{
                this.style.outline = '2px solid {COLORS["focus"]}';
                this.style.outlineOffset = '{SPACING["xs"]}';
            }});

            element.addEventListener('blur', function() {{
                this.style.outline = '';
                this.style.outlineOffset = '';
            }});
        }}
    }})();
    </script>
    """

    st.markdown(html, unsafe_allow_html=True)


def add_skip_link() -> None:
    """
    Add a skip navigation link for accessibility.

    This adds a link at the top of the page that allows keyboard users
    to skip the navigation and go directly to the main content.
    """
    skip_link_html = f"""
    <style>
    .skip-link {{
        position: absolute;
        top: -40px;
        left: 0;
        background: {COLORS["primary"]};
        color: white;
        padding: 8px;
        z-index: 100;
        transition: top 0.3s;
    }}

    .skip-link:focus {{
        top: 0;
    }}
    </style>

    <a href="#main-content" class="skip-link">Skip to main content</a>

    <script>
    // Add an ID to the main content area
    document.addEventListener('DOMContentLoaded', function() {{
        // Try to find the main content area
        const mainContent = document.querySelector('.main');
        if (mainContent) {{
            mainContent.setAttribute('id', 'main-content');
            mainContent.setAttribute('tabindex', '-1');
        }}
    }});
    </script>
    """

    st.markdown(skip_link_html, unsafe_allow_html=True)


def add_keyboard_shortcuts_help() -> None:
    """
    Add a help dialog showing available keyboard shortcuts.

    This adds a button that, when clicked, shows a dialog with all
    registered keyboard shortcuts.
    """
    # Get the keyboard manager instance
    keyboard_manager = get_keyboard_manager()

    # Show help using the adapter
    shortcuts = keyboard_manager.manager.get_shortcuts()
    keyboard_manager.adapter.show_help(shortcuts)


# Create a singleton instance of the keyboard manager
_keyboard_manager = None

def get_keyboard_manager() -> LegacyKeyboardManager:
    """
    Get the singleton instance of the keyboard manager.

    Returns:
        The keyboard manager instance
    """
    global _keyboard_manager
    if _keyboard_manager is None:
        _keyboard_manager = LegacyKeyboardManager()
    return _keyboard_manager


# Register common keyboard shortcuts
def register_common_shortcuts() -> None:
    """Register common keyboard shortcuts for the application."""
    keyboard_manager = get_keyboard_manager()

    # Navigation shortcuts
    keyboard_manager.register_shortcut(
        KeyboardShortcut("Alt+H", "Go to home page", lambda: st.experimental_set_query_params(page="home"))
    )

    keyboard_manager.register_shortcut(
        KeyboardShortcut("Alt+D", "Go to dashboard", lambda: st.experimental_set_query_params(page="dashboard"))
    )

    keyboard_manager.register_shortcut(
        KeyboardShortcut("Alt+E", "Go to explore page", lambda: st.experimental_set_query_params(page="explore"))
    )

    keyboard_manager.register_shortcut(
        KeyboardShortcut("Alt+C", "Go to connect page", lambda: st.experimental_set_query_params(page="connect"))
    )

    # Help shortcut
    keyboard_manager.register_shortcut(
        KeyboardShortcut("?", "Show keyboard shortcuts", lambda: st.session_state.update({"show_keyboard_help": True}))
    )

    # Focus management shortcuts
    keyboard_manager.register_shortcut(
        KeyboardShortcut("Alt+1", "Focus sidebar", lambda: st.session_state.update({"focus_element": "sidebar"}))
    )

    keyboard_manager.register_shortcut(
        KeyboardShortcut("Alt+2", "Focus main content", lambda: st.session_state.update({"focus_element": "main-content"}))
    )

    # File operations shortcuts
    keyboard_manager.register_shortcut(
        KeyboardShortcut("Ctrl+O", "Open file", lambda: st.session_state.update({"open_file_dialog": True}))
    )

    keyboard_manager.register_shortcut(
        KeyboardShortcut("Ctrl+S", "Save file", lambda: st.session_state.update({"save_file_dialog": True}))
    )

    keyboard_manager.register_shortcut(
        KeyboardShortcut("Ctrl+N", "New file", lambda: st.session_state.update({"new_file_dialog": True}))
    )

    # Edit operations shortcuts
    keyboard_manager.register_shortcut(
        KeyboardShortcut("Ctrl+Z", "Undo", lambda: st.session_state.update({"undo_action": True}))
    )

    keyboard_manager.register_shortcut(
        KeyboardShortcut("Ctrl+Y", "Redo", lambda: st.session_state.update({"redo_action": True}))
    )

    # View operations shortcuts
    keyboard_manager.register_shortcut(
        KeyboardShortcut("Ctrl+Plus", "Zoom in", lambda: st.session_state.update({"zoom_in": True}))
    )

    keyboard_manager.register_shortcut(
        KeyboardShortcut("Ctrl+Minus", "Zoom out", lambda: st.session_state.update({"zoom_out": True}))
    )

    keyboard_manager.register_shortcut(
        KeyboardShortcut("Ctrl+0", "Reset zoom", lambda: st.session_state.update({"reset_zoom": True}))
    )

    # Initialize keyboard listeners
    keyboard_manager.initialize_keyboard_listeners()


# Initialize keyboard navigation
def initialize_keyboard_navigation() -> None:
    """Initialize keyboard navigation for the application."""
    # Register common shortcuts
    register_common_shortcuts()

    # Add skip link
    add_skip_link()

    # Add keyboard shortcuts help
    add_keyboard_shortcuts_help()

    # Handle keyboard events
    get_keyboard_manager().handle_keyboard_events()
