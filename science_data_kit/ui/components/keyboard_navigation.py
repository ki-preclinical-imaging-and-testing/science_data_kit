"""
Keyboard Navigation Utilities for Science Data Kit

This module provides utilities for enhancing keyboard navigation in Streamlit applications.
It includes keyboard shortcuts, focus management, and accessibility improvements.
"""

import streamlit as st
import json
from typing import Dict, List, Any, Optional, Callable, Union
import re

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


class KeyboardShortcut:
    """Class representing a keyboard shortcut."""
    
    def __init__(self, key: str, description: str, action: Callable, scope: str = "global"):
        """
        Initialize a keyboard shortcut.
        
        Args:
            key: The key combination (e.g., "Ctrl+S", "Alt+F")
            description: Description of what the shortcut does
            action: Function to call when the shortcut is triggered
            scope: Scope of the shortcut (global, page, component)
        """
        self.key = key
        self.description = description
        self.action = action
        self.scope = scope
        
    def __str__(self) -> str:
        """Return a string representation of the shortcut."""
        return f"{self.key}: {self.description}"


class KeyboardManager:
    """
    Manager for keyboard shortcuts and navigation.
    
    This class provides a centralized way to register and handle keyboard shortcuts,
    manage focus, and improve keyboard navigation in Streamlit applications.
    """
    
    def __init__(self):
        """Initialize the keyboard manager."""
        self.shortcuts: Dict[str, KeyboardShortcut] = {}
        self.focus_order: List[str] = []
        self.current_focus_index = 0
        self.is_initialized = False
        
    def register_shortcut(self, shortcut: KeyboardShortcut) -> None:
        """
        Register a keyboard shortcut.
        
        Args:
            shortcut: The keyboard shortcut to register
        """
        self.shortcuts[shortcut.key] = shortcut
        
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
        
        This method injects JavaScript code to listen for keyboard events
        and communicate with Streamlit via session state.
        """
        if self.is_initialized:
            return
            
        # Create a placeholder for keyboard events in session state
        if "keyboard_event" not in st.session_state:
            st.session_state.keyboard_event = None
            
        # Inject JavaScript to listen for keyboard events
        js_code = """
        <script>
        document.addEventListener('keydown', function(e) {
            // Prevent handling if the event originated in an input field
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }
            
            // Create a key string (e.g., "Ctrl+S")
            let keyString = '';
            if (e.ctrlKey) keyString += 'Ctrl+';
            if (e.altKey) keyString += 'Alt+';
            if (e.shiftKey) keyString += 'Shift+';
            if (e.metaKey) keyString += 'Meta+';
            
            // Add the key itself
            if (e.key === ' ') {
                keyString += 'Space';
            } else if (e.key.length === 1) {
                keyString += e.key.toUpperCase();
            } else {
                keyString += e.key;
            }
            
            // Send the key event to Streamlit
            const event = {
                key: keyString,
                timestamp: Date.now()
            };
            
            // Use Streamlit's setComponentValue to update session state
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: JSON.stringify(event)
            }, '*');
            
            // Prevent default for navigation keys to avoid scrolling
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Tab'].includes(e.key)) {
                e.preventDefault();
            }
        });
        
        // Add focus styles to interactive elements
        function addFocusStyles() {
            const style = document.createElement('style');
            style.textContent = `
                button:focus, input:focus, select:focus, textarea:focus, a:focus, [role="button"]:focus {
                    outline: 2px solid ${COLORS.focus} !important;
                    outline-offset: ${SPACING.xs} !important;
                }
            `;
            document.head.appendChild(style);
        }
        
        // Call once on load
        addFocusStyles();
        </script>
        """
        
        # Replace placeholders with actual values
        js_code = js_code.replace("${COLORS.focus}", COLORS["focus"])
        js_code = js_code.replace("${SPACING.xs}", SPACING["xs"])
        
        # Inject the JavaScript code
        st.markdown(js_code, unsafe_allow_html=True)
        
        self.is_initialized = True
        
    def handle_keyboard_events(self) -> None:
        """
        Handle keyboard events from the JavaScript listeners.
        
        This method should be called in the Streamlit app's main loop
        to process keyboard events.
        """
        if not self.is_initialized:
            self.initialize_keyboard_listeners()
            
        # Check if there's a new keyboard event
        if "keyboard_event" in st.session_state and st.session_state.keyboard_event:
            try:
                event = json.loads(st.session_state.keyboard_event)
                key = event["key"]
                
                # Handle navigation keys
                if key == "Tab":
                    self.next_focus()
                elif key == "Shift+Tab":
                    self.previous_focus()
                    
                # Handle registered shortcuts
                elif key in self.shortcuts:
                    self.shortcuts[key].action()
                    
                # Clear the event after handling
                st.session_state.keyboard_event = None
                
            except (json.JSONDecodeError, KeyError):
                # Reset on error
                st.session_state.keyboard_event = None


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
    
    # Create a list of shortcuts
    shortcuts_html = ""
    for key, shortcut in keyboard_manager.shortcuts.items():
        shortcuts_html += f"<tr><td><kbd>{key}</kbd></td><td>{shortcut.description}</td></tr>"
    
    if not shortcuts_html:
        shortcuts_html = "<tr><td colspan='2'>No shortcuts registered</td></tr>"
    
    # Create the help dialog
    help_dialog_html = f"""
    <style>
    .keyboard-help-button {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: {COLORS["secondary"]};
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 20px;
        cursor: pointer;
        z-index: 1000;
    }}
    
    .keyboard-help-dialog {{
        display: none;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        z-index: 1001;
        max-width: 80%;
        max-height: 80%;
        overflow-y: auto;
    }}
    
    .keyboard-help-dialog h2 {{
        margin-top: 0;
    }}
    
    .keyboard-help-dialog table {{
        width: 100%;
        border-collapse: collapse;
    }}
    
    .keyboard-help-dialog th, .keyboard-help-dialog td {{
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }}
    
    .keyboard-help-dialog th {{
        background-color: #f2f2f2;
    }}
    
    .keyboard-help-dialog kbd {{
        background-color: #f7f7f7;
        border: 1px solid #ccc;
        border-radius: 3px;
        box-shadow: 0 1px 0 rgba(0, 0, 0, 0.2);
        color: #333;
        display: inline-block;
        font-size: 0.85em;
        font-weight: bold;
        line-height: 1;
        padding: 2px 4px;
        white-space: nowrap;
    }}
    
    .keyboard-help-overlay {{
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
    }}
    </style>
    
    <button class="keyboard-help-button" id="keyboard-help-button" aria-label="Keyboard shortcuts help">?</button>
    
    <div class="keyboard-help-overlay" id="keyboard-help-overlay"></div>
    
    <div class="keyboard-help-dialog" id="keyboard-help-dialog" role="dialog" aria-labelledby="keyboard-help-title">
        <h2 id="keyboard-help-title">Keyboard Shortcuts</h2>
        <table>
            <thead>
                <tr>
                    <th>Shortcut</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                {shortcuts_html}
            </tbody>
        </table>
        <p>Press <kbd>Esc</kbd> to close this dialog.</p>
    </div>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const helpButton = document.getElementById('keyboard-help-button');
        const helpDialog = document.getElementById('keyboard-help-dialog');
        const helpOverlay = document.getElementById('keyboard-help-overlay');
        
        if (helpButton && helpDialog && helpOverlay) {{
            // Show dialog when button is clicked
            helpButton.addEventListener('click', function() {{
                helpDialog.style.display = 'block';
                helpOverlay.style.display = 'block';
            }});
            
            // Close dialog when overlay is clicked
            helpOverlay.addEventListener('click', function() {{
                helpDialog.style.display = 'none';
                helpOverlay.style.display = 'none';
            }});
            
            // Close dialog when Esc is pressed
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape' && helpDialog.style.display === 'block') {{
                    helpDialog.style.display = 'none';
                    helpOverlay.style.display = 'none';
                }}
            }});
        }}
    }});
    </script>
    """
    
    st.markdown(help_dialog_html, unsafe_allow_html=True)


# Create a singleton instance of the keyboard manager
_keyboard_manager = None

def get_keyboard_manager() -> KeyboardManager:
    """
    Get the singleton instance of the keyboard manager.
    
    Returns:
        The keyboard manager instance
    """
    global _keyboard_manager
    if _keyboard_manager is None:
        _keyboard_manager = KeyboardManager()
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