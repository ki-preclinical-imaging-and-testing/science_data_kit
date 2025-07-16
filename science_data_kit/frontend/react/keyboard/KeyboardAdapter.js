/**
 * React Keyboard Adapter for Science Data Kit
 * 
 * This module provides a React-specific implementation of the keyboard adapter interface.
 */

import React, { useEffect, useState, useCallback, createContext, useContext } from 'react';

/**
 * Context for keyboard shortcuts
 */
export const KeyboardContext = createContext({
  shortcuts: {},
  registerShortcut: () => {},
  unregisterShortcut: () => {},
  showHelp: () => {},
});

/**
 * Hook to use keyboard shortcuts
 */
export const useKeyboard = () => useContext(KeyboardContext);

/**
 * Keyboard shortcut component
 * 
 * This component provides a React implementation of the keyboard shortcut system.
 * It listens for keyboard events and triggers the appropriate actions.
 */
export const KeyboardProvider = ({ children }) => {
  const [shortcuts, setShortcuts] = useState({});
  const [showHelpDialog, setShowHelpDialog] = useState(false);
  
  /**
   * Register a keyboard shortcut
   * 
   * @param {string} key - The key combination (e.g., "Ctrl+S", "Alt+F")
   * @param {string} description - Description of what the shortcut does
   * @param {function} action - Function to call when the shortcut is triggered
   * @param {string} scope - Scope of the shortcut (global, page, component)
   */
  const registerShortcut = useCallback((key, description, action, scope = "global") => {
    setShortcuts(prev => ({
      ...prev,
      [key]: { key, description, action, scope }
    }));
  }, []);
  
  /**
   * Unregister a keyboard shortcut
   * 
   * @param {string} key - The key combination to unregister
   */
  const unregisterShortcut = useCallback((key) => {
    setShortcuts(prev => {
      const newShortcuts = { ...prev };
      delete newShortcuts[key];
      return newShortcuts;
    });
  }, []);
  
  /**
   * Show the help dialog
   */
  const showHelp = useCallback(() => {
    setShowHelpDialog(true);
  }, []);
  
  /**
   * Handle keyboard events
   */
  const handleKeyDown = useCallback((event) => {
    // Prevent handling if the event originated in an input field
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
      return;
    }
    
    // Create a key string (e.g., "Ctrl+S")
    let keyString = '';
    if (event.ctrlKey) keyString += 'Ctrl+';
    if (event.altKey) keyString += 'Alt+';
    if (event.shiftKey) keyString += 'Shift+';
    if (event.metaKey) keyString += 'Meta+';
    
    // Add the key itself
    if (event.key === ' ') {
      keyString += 'Space';
    } else if (event.key.length === 1) {
      keyString += event.key.toUpperCase();
    } else {
      keyString += event.key;
    }
    
    // Check if this is a registered shortcut
    if (shortcuts[keyString]) {
      event.preventDefault();
      shortcuts[keyString].action();
    }
    
    // Show help dialog when ? is pressed
    if (keyString === '?') {
      event.preventDefault();
      showHelp();
    }
  }, [shortcuts, showHelp]);
  
  // Add event listener for keyboard events
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);
  
  // Register the help shortcut
  useEffect(() => {
    registerShortcut('?', 'Show keyboard shortcuts', showHelp);
  }, [registerShortcut, showHelp]);
  
  return (
    <KeyboardContext.Provider value={{ shortcuts, registerShortcut, unregisterShortcut, showHelp }}>
      {children}
      {showHelpDialog && (
        <KeyboardHelpDialog 
          shortcuts={shortcuts} 
          onClose={() => setShowHelpDialog(false)} 
        />
      )}
    </KeyboardContext.Provider>
  );
};

/**
 * Keyboard help dialog component
 * 
 * This component displays a dialog with all registered keyboard shortcuts.
 */
const KeyboardHelpDialog = ({ shortcuts, onClose }) => {
  // Close dialog when Escape is pressed
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);
  
  return (
    <div className="keyboard-help-overlay" onClick={onClose}>
      <div className="keyboard-help-dialog" onClick={e => e.stopPropagation()}>
        <h2>Keyboard Shortcuts</h2>
        <table>
          <thead>
            <tr>
              <th>Shortcut</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {Object.keys(shortcuts).length > 0 ? (
              Object.values(shortcuts).map(shortcut => (
                <tr key={shortcut.key}>
                  <td><kbd>{shortcut.key}</kbd></td>
                  <td>{shortcut.description}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="2">No shortcuts registered</td>
              </tr>
            )}
          </tbody>
        </table>
        <p>Press <kbd>Esc</kbd> to close this dialog.</p>
        <button onClick={onClose}>Close</button>
      </div>
      <style jsx>{`
        .keyboard-help-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        
        .keyboard-help-dialog {
          background: white;
          padding: 20px;
          border-radius: 5px;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
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
        
        button {
          margin-top: 10px;
          padding: 5px 10px;
          background: #2196F3;
          color: white;
          border: none;
          border-radius: 3px;
          cursor: pointer;
        }
        
        button:hover {
          background: #0b7dda;
        }
      `}</style>
    </div>
  );
};

/**
 * Hook to register a keyboard shortcut
 * 
 * @param {string} key - The key combination (e.g., "Ctrl+S", "Alt+F")
 * @param {string} description - Description of what the shortcut does
 * @param {function} action - Function to call when the shortcut is triggered
 * @param {string} scope - Scope of the shortcut (global, page, component)
 */
export const useKeyboardShortcut = (key, description, action, scope = "global") => {
  const { registerShortcut, unregisterShortcut } = useKeyboard();
  
  useEffect(() => {
    registerShortcut(key, description, action, scope);
    return () => {
      unregisterShortcut(key);
    };
  }, [key, description, action, scope, registerShortcut, unregisterShortcut]);
};

export default KeyboardProvider;