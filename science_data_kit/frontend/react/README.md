# Science Data Kit - React Implementation

This directory contains a React implementation of the Science Data Kit's framework-agnostic keyboard shortcut system. It demonstrates how to use the keyboard shortcut system in a React application.

## Overview

The React implementation consists of:

1. **KeyboardAdapter**: A React-specific implementation of the keyboard adapter interface
2. **FileBrowser**: A simple file browser component that demonstrates the use of keyboard shortcuts
3. **App**: An example application that shows how to use the keyboard shortcut system

## Keyboard Shortcut System

The keyboard shortcut system is implemented using React's Context API and hooks. It provides:

- A `KeyboardProvider` component that manages keyboard shortcuts and provides a context for accessing them
- A `useKeyboardShortcut` hook for easily registering keyboard shortcuts in React components
- A `useKeyboard` hook for accessing the keyboard context
- A `KeyboardHelpDialog` component that displays a dialog with all registered keyboard shortcuts

## Usage

### Basic Setup

To use the keyboard shortcut system in your React application, wrap your app with the `KeyboardProvider` component:

```jsx
import React from 'react';
import KeyboardProvider from './keyboard/KeyboardAdapter';

const App = () => {
  return (
    <div>
      {/* Your app content */}
    </div>
  );
};

const AppWithKeyboard = () => (
  <KeyboardProvider>
    <App />
  </KeyboardProvider>
);

export default AppWithKeyboard;
```

### Registering Keyboard Shortcuts

You can register keyboard shortcuts using the `useKeyboardShortcut` hook:

```jsx
import React from 'react';
import { useKeyboardShortcut } from './keyboard/KeyboardAdapter';

const MyComponent = () => {
  // Register a keyboard shortcut
  useKeyboardShortcut('Ctrl+S', 'Save', () => {
    console.log('Saving...');
  });

  return (
    <div>
      {/* Your component content */}
    </div>
  );
};
```

### Accessing the Keyboard Context

You can access the keyboard context using the `useKeyboard` hook:

```jsx
import React from 'react';
import { useKeyboard } from './keyboard/KeyboardAdapter';

const MyComponent = () => {
  const { shortcuts, showHelp } = useKeyboard();

  return (
    <div>
      <button onClick={showHelp}>Show Keyboard Shortcuts</button>
      <p>Number of registered shortcuts: {Object.keys(shortcuts).length}</p>
    </div>
  );
};
```

## Example Application

The example application demonstrates how to use the keyboard shortcut system in a React application. It includes:

- A file browser component with keyboard navigation
- Global keyboard shortcuts for toggling dark mode and showing help
- A notification system to provide feedback to the user

### Keyboard Shortcuts

The example application includes the following keyboard shortcuts:

- **?**: Show keyboard shortcuts help
- **Ctrl+D**: Toggle dark mode
- **Ctrl+H**: Show help
- **Ctrl+N**: Create new file
- **F2**: Rename selected file
- **Delete**: Delete selected file
- **Arrow Up/Down**: Navigate through files
- **Enter**: Open selected file

## Integration with Science Data Kit

This React implementation is designed to work with the Science Data Kit's framework-agnostic keyboard shortcut system. It can be used alongside the Streamlit and Flask implementations to provide a consistent keyboard shortcut experience across different UI frameworks.

## Future Enhancements

Future enhancements to the React implementation could include:

- Integration with React Router for navigation shortcuts
- Support for more complex keyboard shortcuts (e.g., sequences, combos)
- Customizable keyboard shortcut themes
- Persistence of user-defined keyboard shortcuts
- Accessibility improvements