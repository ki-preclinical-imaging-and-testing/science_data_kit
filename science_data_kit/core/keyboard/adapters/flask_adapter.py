"""
Flask Keyboard Adapter for Science Data Kit

This module provides a Flask-specific implementation of the keyboard adapter interface.
"""

from typing import Dict, List, Any, Optional, Callable, Set
import logging
import json
from flask import request, session, g, current_app

from science_data_kit.core.keyboard.adapter_interface import KeyboardAdapterInterface
from science_data_kit.core.keyboard.keyboard_shortcut import KeyboardShortcut

logger = logging.getLogger(__name__)


class FlaskKeyboardAdapter(KeyboardAdapterInterface):
    """
    Flask-specific implementation of the keyboard adapter interface.
    
    This adapter uses Flask's session and JavaScript to handle keyboard shortcuts
    in Flask web applications.
    """
    
    def __init__(self):
        """Initialize the Flask keyboard adapter."""
        self.is_initialized = False
        self.callbacks: Set[Callable[[KeyboardShortcut], None]] = set()
        self.registered_shortcuts: Dict[str, KeyboardShortcut] = {}
        
    def initialize(self) -> None:
        """
        Initialize the keyboard adapter.
        
        This method sets up the necessary JavaScript and session state
        for handling keyboard events in Flask.
        """
        if self.is_initialized:
            return
            
        # Nothing to do here - the JavaScript will be injected when show_help is called
        # or when the keyboard_js template is included in a page
        
        self.is_initialized = True
        logger.debug("Flask keyboard adapter initialized")
        
    def register_shortcut(self, shortcut: KeyboardShortcut) -> None:
        """
        Register a keyboard shortcut with the adapter.
        
        Args:
            shortcut: The keyboard shortcut to register
        """
        self.registered_shortcuts[shortcut.key] = shortcut
        logger.debug(f"Registered shortcut in Flask adapter: {shortcut}")
        
    def unregister_shortcut(self, key: str) -> None:
        """
        Unregister a keyboard shortcut.
        
        Args:
            key: The key combination of the shortcut to unregister
        """
        if key in self.registered_shortcuts:
            del self.registered_shortcuts[key]
            logger.debug(f"Unregistered shortcut in Flask adapter: {key}")
        
    def handle_events(self) -> None:
        """
        Handle keyboard events.
        
        This method processes any pending keyboard events in Flask's request.
        """
        if not self.is_initialized:
            self.initialize()
            
        # Check if there's a keyboard event in the request
        event = self.get_current_event()
        if event:
            key = event.get("key")
            if key and key in self.registered_shortcuts:
                shortcut = self.registered_shortcuts[key]
                for callback in self.callbacks:
                    try:
                        callback(shortcut)
                    except Exception as e:
                        logger.error(f"Error in shortcut callback: {e}")
                
                # Clear the event after handling
                self.clear_current_event()
        
    def show_help(self, shortcuts: Dict[str, KeyboardShortcut]) -> None:
        """
        Show a help dialog with the registered shortcuts.
        
        Args:
            shortcuts: Dictionary of registered shortcuts
        """
        # This method doesn't actually show the help dialog directly,
        # but it provides the JavaScript that will be included in the page
        # to show the help dialog when the user presses the help key.
        # The actual dialog is shown by the JavaScript.
        pass
        
    def get_keyboard_js(self, shortcuts: Dict[str, KeyboardShortcut] = None) -> str:
        """
        Get the JavaScript code for handling keyboard shortcuts.
        
        Args:
            shortcuts: Dictionary of registered shortcuts to include in the help dialog
            
        Returns:
            JavaScript code for handling keyboard shortcuts
        """
        if shortcuts is None:
            shortcuts = self.registered_shortcuts
            
        # Create a list of shortcuts for the help dialog
        shortcuts_json = []
        for key, shortcut in shortcuts.items():
            shortcuts_json.append({
                "key": key,
                "description": shortcut.description
            })
            
        # Create the JavaScript code
        js_code = """
        <script>
        // Keyboard shortcut handling
        (function() {
            // Shortcuts data
            const shortcuts = %s;
            
            // Register keyboard event listener
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
                
                // Check if this is a registered shortcut
                const shortcut = shortcuts.find(s => s.key === keyString);
                if (shortcut) {
                    // Send the key event to the server
                    fetch('/api/keyboard_event', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            key: keyString,
                            timestamp: Date.now()
                        }),
                    });
                    
                    // Prevent default browser behavior
                    e.preventDefault();
                }
                
                // Show help dialog when ? is pressed
                if (keyString === '?') {
                    showHelpDialog();
                    e.preventDefault();
                }
            });
            
            // Help dialog
            function showHelpDialog() {
                // Create dialog if it doesn't exist
                let dialog = document.getElementById('keyboard-help-dialog');
                let overlay = document.getElementById('keyboard-help-overlay');
                
                if (!dialog) {
                    // Create overlay
                    overlay = document.createElement('div');
                    overlay.id = 'keyboard-help-overlay';
                    overlay.className = 'keyboard-help-overlay';
                    document.body.appendChild(overlay);
                    
                    // Create dialog
                    dialog = document.createElement('div');
                    dialog.id = 'keyboard-help-dialog';
                    dialog.className = 'keyboard-help-dialog';
                    dialog.setAttribute('role', 'dialog');
                    dialog.setAttribute('aria-labelledby', 'keyboard-help-title');
                    
                    // Create dialog content
                    let html = `
                        <h2 id="keyboard-help-title">Keyboard Shortcuts</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>Shortcut</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    // Add shortcuts
                    if (shortcuts.length > 0) {
                        for (const shortcut of shortcuts) {
                            html += `<tr><td><kbd>${shortcut.key}</kbd></td><td>${shortcut.description}</td></tr>`;
                        }
                    } else {
                        html += `<tr><td colspan="2">No shortcuts registered</td></tr>`;
                    }
                    
                    html += `
                            </tbody>
                        </table>
                        <p>Press <kbd>Esc</kbd> to close this dialog.</p>
                    `;
                    
                    dialog.innerHTML = html;
                    document.body.appendChild(dialog);
                    
                    // Add styles
                    const style = document.createElement('style');
                    style.textContent = `
                        .keyboard-help-overlay {
                            display: none;
                            position: fixed;
                            top: 0;
                            left: 0;
                            right: 0;
                            bottom: 0;
                            background: rgba(0, 0, 0, 0.5);
                            z-index: 1000;
                        }
                        
                        .keyboard-help-dialog {
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
                        }
                        
                        .keyboard-help-dialog h2 {
                            margin-top: 0;
                        }
                        
                        .keyboard-help-dialog table {
                            width: 100%;
                            border-collapse: collapse;
                        }
                        
                        .keyboard-help-dialog th, .keyboard-help-dialog td {
                            padding: 8px;
                            text-align: left;
                            border-bottom: 1px solid #ddd;
                        }
                        
                        .keyboard-help-dialog th {
                            background-color: #f2f2f2;
                        }
                        
                        .keyboard-help-dialog kbd {
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
                        }
                    `;
                    document.head.appendChild(style);
                }
                
                // Show dialog and overlay
                dialog.style.display = 'block';
                overlay.style.display = 'block';
                
                // Close dialog when overlay is clicked
                overlay.onclick = function() {
                    dialog.style.display = 'none';
                    overlay.style.display = 'none';
                };
                
                // Close dialog when Esc is pressed
                document.addEventListener('keydown', function closeDialog(e) {
                    if (e.key === 'Escape') {
                        dialog.style.display = 'none';
                        overlay.style.display = 'none';
                        document.removeEventListener('keydown', closeDialog);
                    }
                });
            }
        })();
        </script>
        """ % json.dumps(shortcuts_json)
        
        return js_code
        
    def get_current_event(self) -> Optional[Dict[str, Any]]:
        """
        Get the current keyboard event.
        
        Returns:
            Dictionary containing information about the current keyboard event,
            or None if there is no current event
        """
        # Check if there's a keyboard event in the request
        if request.method == 'POST' and request.path == '/api/keyboard_event':
            try:
                return request.json
            except Exception as e:
                logger.error(f"Error parsing keyboard event: {e}")
                return None
                
        # Check if there's a keyboard event in the session
        if 'keyboard_event' in session:
            event = session['keyboard_event']
            if event:
                return event
                
        return None
        
    def clear_current_event(self) -> None:
        """
        Clear the current keyboard event.
        
        This method clears the keyboard event in Flask's session.
        """
        if 'keyboard_event' in session:
            session['keyboard_event'] = None
        
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