"""
Streamlit Keyboard Adapter for Science Data Kit

This module provides a Streamlit-specific implementation of the keyboard adapter interface.
"""

import streamlit as st
import json
from typing import Dict, List, Any, Optional, Callable, Set
import logging

from science_data_kit.core.keyboard.adapter_interface import KeyboardAdapterInterface
from science_data_kit.core.keyboard.keyboard_shortcut import KeyboardShortcut

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


class StreamlitKeyboardAdapter(KeyboardAdapterInterface):
    """
    Streamlit-specific implementation of the keyboard adapter interface.
    
    This adapter uses Streamlit's session state and UI components to handle
    keyboard shortcuts in Streamlit applications.
    """
    
    def __init__(self):
        """Initialize the Streamlit keyboard adapter."""
        self.is_initialized = False
        self.callbacks: Set[Callable[[KeyboardShortcut], None]] = set()
        self.registered_shortcuts: Dict[str, KeyboardShortcut] = {}
        
    def initialize(self) -> None:
        """
        Initialize the keyboard adapter.
        
        This method sets up the necessary event listeners and session state
        for handling keyboard events in Streamlit.
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
        logger.debug("Streamlit keyboard adapter initialized")
        
    def register_shortcut(self, shortcut: KeyboardShortcut) -> None:
        """
        Register a keyboard shortcut with the adapter.
        
        Args:
            shortcut: The keyboard shortcut to register
        """
        self.registered_shortcuts[shortcut.key] = shortcut
        logger.debug(f"Registered shortcut in Streamlit adapter: {shortcut}")
        
    def unregister_shortcut(self, key: str) -> None:
        """
        Unregister a keyboard shortcut.
        
        Args:
            key: The key combination of the shortcut to unregister
        """
        if key in self.registered_shortcuts:
            del self.registered_shortcuts[key]
            logger.debug(f"Unregistered shortcut in Streamlit adapter: {key}")
        
    def handle_events(self) -> None:
        """
        Handle keyboard events.
        
        This method processes any pending keyboard events in Streamlit's session state.
        """
        if not self.is_initialized:
            self.initialize()
            
        # Check if there's a new keyboard event
        if "keyboard_event" in st.session_state and st.session_state.keyboard_event:
            try:
                event = json.loads(st.session_state.keyboard_event)
                key = event["key"]
                
                # Handle registered shortcuts
                if key in self.registered_shortcuts:
                    shortcut = self.registered_shortcuts[key]
                    for callback in self.callbacks:
                        try:
                            callback(shortcut)
                        except Exception as e:
                            logger.error(f"Error in shortcut callback: {e}")
                    
                # Clear the event after handling
                self.clear_current_event()
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error processing keyboard event: {e}")
                # Reset on error
                self.clear_current_event()
        
    def show_help(self, shortcuts: Dict[str, KeyboardShortcut]) -> None:
        """
        Show a help dialog with the registered shortcuts.
        
        Args:
            shortcuts: Dictionary of registered shortcuts
        """
        # Create a list of shortcuts
        shortcuts_html = ""
        for key, shortcut in shortcuts.items():
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
        
    def get_current_event(self) -> Optional[Dict[str, Any]]:
        """
        Get the current keyboard event.
        
        Returns:
            Dictionary containing information about the current keyboard event,
            or None if there is no current event
        """
        if "keyboard_event" in st.session_state and st.session_state.keyboard_event:
            try:
                return json.loads(st.session_state.keyboard_event)
            except json.JSONDecodeError:
                return None
        return None
        
    def clear_current_event(self) -> None:
        """
        Clear the current keyboard event.
        
        This method clears the keyboard event in Streamlit's session state.
        """
        if "keyboard_event" in st.session_state:
            st.session_state.keyboard_event = None
        
    def on_shortcut_triggered(self, callback: Callable[[KeyboardShortcut], None]) -> None:
        """
        Register a callback to be called when a shortcut is triggered.
        
        Args:
            callback: Function to call when a shortcut is triggered
        """
        self.callbacks.add(callback)
        
    def get_supported_keys(self) -> List[str]:
        """
        Get a list of keys supported by this adapter.
        
        Returns:
            List of key names supported by this adapter
        """
        return [
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
            "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "Tab", "Enter", "Escape", "Space", "Backspace", "Delete",
            "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight",
            "Home", "End", "PageUp", "PageDown",
            "Ctrl+A", "Ctrl+B", "Ctrl+C", "Ctrl+D", "Ctrl+E", "Ctrl+F", "Ctrl+G", "Ctrl+H",
            "Ctrl+I", "Ctrl+J", "Ctrl+K", "Ctrl+L", "Ctrl+M", "Ctrl+N", "Ctrl+O", "Ctrl+P",
            "Ctrl+Q", "Ctrl+R", "Ctrl+S", "Ctrl+T", "Ctrl+U", "Ctrl+V", "Ctrl+W", "Ctrl+X",
            "Ctrl+Y", "Ctrl+Z",
            "Alt+A", "Alt+B", "Alt+C", "Alt+D", "Alt+E", "Alt+F", "Alt+G", "Alt+H",
            "Alt+I", "Alt+J", "Alt+K", "Alt+L", "Alt+M", "Alt+N", "Alt+O", "Alt+P",
            "Alt+Q", "Alt+R", "Alt+S", "Alt+T", "Alt+U", "Alt+V", "Alt+W", "Alt+X",
            "Alt+Y", "Alt+Z",
            "Shift+A", "Shift+B", "Shift+C", "Shift+D", "Shift+E", "Shift+F", "Shift+G",
            "Shift+H", "Shift+I", "Shift+J", "Shift+K", "Shift+L", "Shift+M", "Shift+N",
            "Shift+O", "Shift+P", "Shift+Q", "Shift+R", "Shift+S", "Shift+T", "Shift+U",
            "Shift+V", "Shift+W", "Shift+X", "Shift+Y", "Shift+Z",
            "?", "/", ".", ",", ";", "'", "[", "]", "\\", "-", "=", "`"
        ]