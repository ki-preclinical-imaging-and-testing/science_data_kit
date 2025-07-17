# Science Data Kit (SDK) Framework-Agnostic Architecture Roadmap - Version 10

## Overview
This roadmap outlines a comprehensive plan for evolving the current render function pattern into a framework-agnostic architecture. This will allow the app to support multiple frontends (Streamlit, Flask, React) without duplicating business logic.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2025-07-20 | Initial version of Framework-Agnostic Architecture roadmap |
| 01 | 2025-07-23 | Completed Phase 1 (Core Extraction) tasks, implemented core page classes and Streamlit adapter |
| 02 | 2025-07-26 | Completed Phase 2 (Streamlit Adapter Layer) tasks, implemented core page classes for file_browser, connect, and explore pages, added comprehensive tests and documentation |
| 03 | 2025-07-30 | Completed Phase 3 (Flask API Development) tasks, implemented Flask application structure, REST API endpoints, Flask adapter layer, authentication/session management, and basic Jinja2 templates |
| 04 | 2025-08-03 | Completed initial Phase 4 (Enhanced UI Components) tasks, implemented HTMX and Alpine.js for dynamic updates and client-side interactivity, enhanced file browser component with drag-and-drop upload, file operations, rich preview capabilities, and improved multi-select functionality |
| 05 | 2025-08-07 | Improved connection management UI with API endpoints for connecting, disconnecting, and testing connections, added loading indicators, error handling, and user feedback |
| 06 | 2025-08-10 | Implemented OAuth flows for cloud services and real-time updates for dashboards using WebSockets |
| 07 | 2025-08-14 | Completed responsive design components for mobile and tablet views, implemented comprehensive UI tests, and documented component architecture and best practices |
| 08 | 2025-08-18 | Implemented unified state management system and sophisticated toast notification system that work across frameworks |
| 09 | 2025-08-22 | Implemented framework-agnostic keyboard shortcut system and began React exploration with React adapter, example components, and documentation |
| 10 | 2025-08-26 | Completed React exploration with React adapter layer for core components, data visualization prototype, and hybrid approach evaluation |

## Background
The Science Data Kit currently uses render functions (`render_dashboard_page()`, etc.) in a Streamlit-specific way. While there's already good separation between UI components and backend services, the existing pattern can be evolved rather than completely replaced to support multiple frontend frameworks. Features like file browser and remote connection would benefit from richer UI capabilities that could be provided by alternative frameworks.

## Goals
1. Create a framework-agnostic core with pluggable UI layers
2. Support multiple frontend frameworks (Streamlit, Flask+HTMX, React)
3. Maintain "Python-first" philosophy while enabling rich UI experiences
4. Allow gradual migration without disrupting existing functionality
5. Improve user experience for complex UI components

## Current Status
The Framework-Agnostic Architecture implementation has progressed significantly with the completion of Phase 1 (Core Extraction), Phase 2 (Streamlit Adapter Layer), Phase 3 (Flask API Development), Phase 4 (Enhanced UI Components), and Phase 5 (Cross-Framework Components). The following tasks have been completed:

### Phase 1 (Core Extraction) - ✅ COMPLETED
1. Created the core/pages/ directory structure
2. Defined base page data models in core/models/page.py
3. Created framework-independent page classes in core/pages/
4. Extracted business logic from existing render functions
5. Implemented unit tests for core page classes
6. Created Streamlit adapter for core page classes
7. Updated dashboard.py to use the new adapter

### Phase 2 (Streamlit Adapter Layer) - ✅ COMPLETED
1. Created ui/adapters/ directory
2. Implemented Streamlit-specific adapter classes
3. Moved all Streamlit-specific code to adapter layer
4. Updated all existing render functions to use adapters
5. Ensured all pages work through new architecture
6. Added comprehensive tests for adapter layer
7. Documented adapter pattern for future frameworks

### Phase 3 (Flask API Development) - ✅ COMPLETED
1. Set up Flask application structure in `web/`
2. Implemented REST API endpoints for each page
3. Created Flask adapter layer for core pages
4. Added authentication/session management
5. Implemented basic Jinja2 templates for testing
6. Created API documentation
7. Implemented comprehensive API tests
8. Ensured feature parity with Streamlit UI

### Phase 4 (Enhanced UI Components) - ✅ COMPLETED
1. ✅ Added HTMX for dynamic updates without full page reloads
2. ✅ Implemented Alpine.js for client-side interactivity
3. ✅ Enhanced file browser component with drag-and-drop upload
4. ✅ Added file operations (rename, delete, move, copy)
5. ✅ Created rich preview capabilities for different file types
6. ✅ Improved multi-select functionality
7. ✅ Enhanced connection management UI
8. ✅ Added loading indicators and error handling
9. ✅ Implemented OAuth flows for cloud services
10. ✅ Added real-time updates for dashboards using WebSockets
11. ✅ Created responsive design components for mobile and tablet views
12. ✅ Implemented comprehensive UI tests
13. ✅ Documented component architecture and best practices

### Phase 5: Cross-Framework Components - ✅ COMPLETED
1. ✅ Implemented unified state management system
   - ✅ Created framework-agnostic StateManager class
   - ✅ Implemented adapters for different frameworks (Memory, Streamlit, Flask)
   - ✅ Added support for different state scopes (global, user, session, request, component)
   - ✅ Implemented state persistence and serialization
   - ✅ Added callback system for state changes
2. ✅ Created sophisticated toast notification system
   - ✅ Implemented framework-agnostic NotificationManager class
   - ✅ Created notification types (toast, alert, banner, modal, snackbar)
   - ✅ Added support for different notification levels (success, info, warning, error, debug)
   - ✅ Implemented adapters for different frameworks (Streamlit, Flask)
   - ✅ Added support for notification actions and callbacks
   - ✅ Implemented notification persistence and management
3. ✅ Added keyboard shortcuts for common operations
   - ✅ Created framework-agnostic keyboard shortcut system
   - ✅ Implemented adapters for different frameworks (Streamlit, Flask)
   - ✅ Added keyboard shortcuts for navigation, file operations, and UI interactions
   - ✅ Created keyboard shortcut help dialog
   - ✅ Added support for customizable keyboard shortcuts
4. ✅ Completed React exploration
   - ✅ Created React adapter for keyboard shortcut system
   - ✅ Implemented example React components (FileBrowser)
   - ✅ Created documentation for React implementation
   - ✅ Evaluated need for full SPA implementation
   - ✅ Created React adapter layer for core components
   - ✅ Prototyped key components (data visualization)
   - ✅ Considered hybrid approach with Flask backend
   - ✅ Benchmarked performance against other implementations

The implementation maintains backward compatibility with the current Streamlit UI while providing a framework-independent core that can be used with other UI frameworks. The Flask implementation provides a web interface and REST API for the core functionality, now enhanced with HTMX and Alpine.js for a more dynamic and interactive user experience.

The roadmap is divided into five phases:

1. **Phase 1: Core Extraction** - ✅ COMPLETED
   - Extract page logic from render functions into framework-independent core classes
   - Define base page data models
   - Maintain backward compatibility with current Streamlit UI
2. **Phase 2: Streamlit Adapter Layer** - ✅ COMPLETED
   - Convert current render functions to thin Streamlit adapters
   - Move all Streamlit-specific code to adapter layer
   - Ensure all pages work through new architecture
3. **Phase 3: Flask API Development** - ✅ COMPLETED
   - Create Flask application structure
   - Implement REST API endpoints for each page
   - Add authentication/session management
   - Create simple Jinja2 templates for testing
4. **Phase 4: Enhanced UI Components** - ✅ COMPLETED
   - ✅ Implement HTMX for dynamic updates
   - ✅ Add Alpine.js for client-side interactivity
   - ✅ Focus on file browser and connection management
   - ✅ Create rich preview capabilities
   - ✅ Add real-time updates for dashboards
   - ✅ Create responsive design components
   - ✅ Implement comprehensive UI tests
   - ✅ Document component architecture
5. **Phase 5: Cross-Framework Components** - ✅ COMPLETED
   - ✅ Implement unified state management system
   - ✅ Create sophisticated toast notification system
   - ✅ Add keyboard shortcuts for common operations
   - ✅ Complete React exploration

## Implementation Details

### Architecture Overview

```
science_data_kit/
├── core/                    # Framework-independent layer
│   ├── services/           # Business logic (existing)
│   ├── pages/             # Page orchestration (new) ✅
│   ├── models/            # Shared data structures (extended) ✅
│   ├── state/             # State management system (new) ✅
│   │   ├── adapters/      # State adapters for different frameworks ✅
│   ├── notifications/     # Notification system (new) ✅
│   │   ├── adapters/      # Notification adapters for different frameworks ✅
│   └── keyboard/          # Keyboard shortcut system (new) ✅
│       ├── adapters/      # Keyboard adapters for different frameworks ✅
├── ui/                    # Streamlit implementation
│   ├── adapters/          # Streamlit adapter layer (new) ✅
│   └── pages/             # Streamlit pages (updated) ✅
├── web/                   # Flask implementation (new) ✅
│   ├── adapters/          # Flask adapter layer (new) ✅
│   ├── api/               # REST API endpoints (new) ✅
│   ├── templates/         # Jinja2 templates (new) ✅
│   │   └── partials/      # Partial templates for HTMX (new) ✅
│   └── static/            # Static files (CSS, JS) (new) ✅
└── frontend/              # React implementation (new) ✅
    ├── react/             # React components and adapters (new) ✅
    │   ├── keyboard/      # React keyboard adapter (new) ✅
    │   ├── adapters/      # React adapter layer (new) ✅
    │   ├── components/    # React UI components (new) ✅
    │   └── docs/          # React documentation (new) ✅
```

The architecture separates the application into distinct layers:

1. **Core Layer**: Contains all business logic, data models, and page orchestration that is independent of any UI framework
2. **UI Adapters**: Framework-specific implementations that translate core data structures into UI components
3. **Framework-Specific UI Components**: Specialized components that leverage the unique capabilities of each framework

### Phase 5: Cross-Framework Components - ✅ COMPLETED

**Objective**: Implement cross-framework components that work across different UI frameworks

**Tasks**:
- ✅ Implement unified state management system
- ✅ Create sophisticated toast notification system
- ✅ Add keyboard shortcuts for common operations
- ✅ Complete React exploration

**Implementation Details**:

1. **Unified State Management System**:
   - Created a framework-agnostic StateManager class in core/state/state_manager.py
   - Implemented adapters for different frameworks:
     - MemoryStateAdapter: In-memory state storage for testing and fallback
     - StreamlitStateAdapter: Uses Streamlit's session_state for state storage
     - FlaskStateAdapter: Uses Flask's session object for state storage
   - Added support for different state scopes:
     - GLOBAL: Shared across all users
     - USER: User-specific state
     - SESSION: Session-specific state (default)
     - REQUEST: Request-specific state
     - COMPONENT: Component-specific state
   - Implemented state persistence and serialization
   - Added callback system for state changes

2. **Sophisticated Toast Notification System**:
   - Created a framework-agnostic NotificationManager class in core/notifications/notification_manager.py
   - Implemented notification types:
     - TOAST: Temporary popup notification
     - ALERT: Inline alert that stays visible
     - BANNER: Full-width banner at the top of the page
     - MODAL: Modal dialog
     - SNACKBAR: Small notification at the bottom of the screen
   - Added support for different notification levels:
     - SUCCESS: Success messages
     - INFO: Informational messages
     - WARNING: Warning messages
     - ERROR: Error messages
     - DEBUG: Debug messages
   - Implemented adapters for different frameworks:
     - StreamlitNotificationAdapter: Uses Streamlit's UI components
     - FlaskNotificationAdapter: Uses Flask's flash messages and JavaScript
   - Added support for notification actions and callbacks
   - Implemented notification persistence and management

3. **Keyboard Shortcuts for Common Operations**:
   - Created a framework-agnostic keyboard shortcut system in core/keyboard/
   - Implemented KeyboardShortcut class for representing keyboard shortcuts
   - Created KeyboardManager class for managing keyboard shortcuts
   - Implemented adapters for different frameworks:
     - StreamlitKeyboardAdapter: Uses Streamlit's session state and UI components
     - FlaskKeyboardAdapter: Uses Flask's session and JavaScript
   - Added keyboard shortcuts for common operations:
     - Navigation between pages
     - File operations (upload, download, delete, rename)
     - Form submission
     - Modal dialogs (open, close)
     - Notification management (dismiss, clear all)
     - View operations (zoom in, zoom out, reset zoom)
     - Edit operations (undo, redo)
   - Created keyboard shortcut help dialog
   - Added support for customizable keyboard shortcuts

4. **React Exploration**:
   - Created React adapter for keyboard shortcut system
   - Implemented React components:
     - KeyboardProvider: Context provider for keyboard shortcuts
     - FileBrowser: Example component using keyboard shortcuts
     - DataVisualization: Prototype for data visualization component
   - Created React adapter layer for core components:
     - ReactAdapter: Base adapter class
     - ReactUIAdapter: Adapter for UI components
     - ReactDataVizAdapter: Adapter for data visualization components
   - Evaluated need for full SPA implementation:
     - Analyzed benefits and drawbacks of full SPA approach
     - Recommended hybrid approach instead of full SPA
   - Considered hybrid approach with Flask backend:
     - Proposed "React Islands" pattern for embedding React components in Flask templates
     - Outlined implementation strategy for API-first design and shared state management
   - Benchmarked performance against other implementations:
     - Compared Streamlit, Flask+HTMX, React, and Flask+React implementations
     - Found hybrid approach (Flask+React) provides best balance of performance and UX
   - Created comprehensive documentation for React integration

### State Management System Implementation Details

The state management system provides a unified API for managing state across different frontend frameworks. It includes:

1. **Core StateManager Class**:
   - Provides methods for getting, setting, and deleting state values
   - Supports different state scopes (global, user, session, request, component)
   - Includes callback system for state changes
   - Supports state persistence and serialization

2. **Framework-Specific Adapters**:
   - MemoryStateAdapter: In-memory state storage for testing and fallback
   - StreamlitStateAdapter: Uses Streamlit's session_state for state storage
   - FlaskStateAdapter: Uses Flask's session object for state storage

3. **State Scopes**:
   - GLOBAL: Shared across all users (stored in a file)
   - USER: User-specific state (stored in a user-specific file)
   - SESSION: Session-specific state (default, stored in Streamlit's session_state or Flask's session)
   - REQUEST: Request-specific state (stored in Flask's g object)
   - COMPONENT: Component-specific state (stored in memory)

4. **Usage Example**:
   ```python
   from science_data_kit.core.state.state_manager import StateManager
   from science_data_kit.core.state.adapters.streamlit_adapter import StreamlitStateAdapter

   # Create a state manager with a Streamlit adapter
   state_manager = StateManager(adapter=StreamlitStateAdapter())

   # Initialize state with default values
   state_manager.initialize({
       "user_name": "Guest",
       "theme": "light",
       "sidebar_collapsed": False,
   })

   # Get a value from the state
   user_name = state_manager.get("user_name")

   # Set a value in the state
   state_manager.set("theme", "dark")

   # Delete a value from the state
   state_manager.delete("sidebar_collapsed")

   # Check if a key exists in the state
   if state_manager.has("user_name"):
       print(f"Hello, {state_manager.get('user_name')}!")

   # Register a callback for state changes
   def on_theme_change(key, old_value, new_value):
       print(f"Theme changed from {old_value} to {new_value}")

   state_manager.on_change("theme", on_theme_change)
   ```

### Notification System Implementation Details

The notification system provides a unified API for displaying notifications across different frontend frameworks. It includes:

1. **Core NotificationManager Class**:
   - Provides methods for creating, updating, and deleting notifications
   - Supports different notification types (toast, alert, banner, modal, snackbar)
   - Supports different notification levels (success, info, warning, error, debug)
   - Includes callback system for notification events
   - Supports notification persistence and management

2. **Framework-Specific Adapters**:
   - StreamlitNotificationAdapter: Uses Streamlit's UI components
   - FlaskNotificationAdapter: Uses Flask's flash messages and JavaScript

3. **Notification Types**:
   - TOAST: Temporary popup notification
   - ALERT: Inline alert that stays visible
   - BANNER: Full-width banner at the top of the page
   - MODAL: Modal dialog
   - SNACKBAR: Small notification at the bottom of the screen

4. **Notification Levels**:
   - SUCCESS: Success messages
   - INFO: Informational messages
   - WARNING: Warning messages
   - ERROR: Error messages
   - DEBUG: Debug messages

5. **Usage Example**:
   ```python
   from science_data_kit.core.notifications.notification_manager import NotificationManager
   from science_data_kit.core.notifications.adapters.streamlit_adapter import StreamlitNotificationAdapter

   # Create a notification manager with a Streamlit adapter
   notification_manager = NotificationManager(adapter=StreamlitNotificationAdapter())

   # Create a success notification
   notification_manager.success("Operation completed successfully!")

   # Create an error notification with a title and details
   notification_manager.error(
       message="Failed to connect to the database",
       title="Connection Error",
       details="Check your connection settings and try again.",
       duration=10000,  # 10 seconds
   )

   # Create a modal notification with actions
   notification_manager.create(
       message="Do you want to delete this file?",
       title="Confirm Deletion",
       type="modal",
       actions=[
           {
               "label": "Delete",
               "callback": lambda: delete_file(file_id),
           },
           {
               "label": "Cancel",
           },
       ],
   )

   # Register a callback for notification events
   def on_notification_create(notification):
       print(f"Notification created: {notification.title}")

   notification_manager.on("create", on_notification_create)
   ```

### Keyboard Shortcut System Implementation Details

The keyboard shortcut system provides a unified API for managing keyboard shortcuts across different frontend frameworks. It includes:

1. **Core KeyboardManager Class**:
   - Provides methods for registering and handling keyboard shortcuts
   - Supports different scopes (global, page, component)
   - Includes callback system for shortcut events
   - Supports customizable keyboard shortcuts

2. **Framework-Specific Adapters**:
   - StreamlitKeyboardAdapter: Uses Streamlit's session state and UI components
   - FlaskKeyboardAdapter: Uses Flask's session and JavaScript
   - ReactKeyboardAdapter: Uses React's Context API and hooks

3. **Usage Example (Python)**:
   ```python
   from science_data_kit.core.keyboard.keyboard_manager import KeyboardManager
   from science_data_kit.core.keyboard.adapters.streamlit_adapter import StreamlitKeyboardAdapter
   from science_data_kit.core.keyboard.keyboard_shortcut import KeyboardShortcut

   # Create a keyboard manager with a Streamlit adapter
   keyboard_manager = KeyboardManager(adapter=StreamlitKeyboardAdapter())

   # Register a keyboard shortcut
   keyboard_manager.register_shortcut(
       KeyboardShortcut("Ctrl+S", "Save", lambda: save_file())
   )

   # Register a keyboard shortcut with a scope
   keyboard_manager.register_shortcut(
       KeyboardShortcut("Alt+F", "Open file", lambda: open_file(), scope="file_browser")
   )

   # Handle keyboard events (call this in your app's main loop)
   keyboard_manager.handle_events()

   # Show help dialog
   keyboard_manager.show_help()
   ```

4. **Usage Example (React)**:
   ```jsx
   import React from 'react';
   import KeyboardProvider, { useKeyboardShortcut } from './keyboard/KeyboardAdapter';

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

   const App = () => (
     <KeyboardProvider>
       <MyComponent />
     </KeyboardProvider>
   );
   ```

### React Adapter Layer Implementation Details

The React adapter layer provides a bridge between the framework-agnostic core components and the React UI. It includes:

1. **Base ReactAdapter Class**:
   - Provides methods for registering and retrieving components and hooks
   - Supports component registration and retrieval
   - Supports hook registration and retrieval

2. **ReactUIAdapter Class**:
   - Extends the base ReactAdapter class
   - Provides React-specific implementations of core UI components
   - Includes components for buttons, inputs, selects, and cards
   - Provides render methods for each component type

3. **ReactDataVizAdapter Class**:
   - Extends the base ReactAdapter class
   - Provides React-specific implementations of data visualization components
   - Includes components for charts and tables
   - Provides render methods for each component type

4. **Usage Example**:
   ```jsx
   import React from 'react';
   import createReactAdapter from './adapters/ReactAdapter';

   // Create adapter instances
   const { ui, dataViz } = createReactAdapter();

   const MyComponent = () => {
     return (
       <div>
         {ui.renderButton({ onClick: () => console.log('Clicked!'), children: 'Click Me' })}
         {ui.renderInput({ value: 'Hello', onChange: (e) => console.log(e.target.value) })}
         {dataViz.renderChart({ data: [1, 2, 3], type: 'bar' })}
       </div>
     );
   };
   ```

### React Integration Evaluation

After evaluating the need for a full SPA implementation and considering a hybrid approach with Flask backend, the following conclusions were reached:

1. **Full SPA Implementation**:
   - Benefits: Enhanced UX, client-side state management, offline capabilities, better developer experience
   - Drawbacks: Increased complexity, initial load performance issues, potential logic duplication, maintenance overhead
   - Recommendation: A full SPA implementation is not recommended for the entire application

2. **Hybrid Approach with Flask Backend**:
   - Architecture: Flask application with Jinja templates, React islands, and REST API
   - Implementation Strategy: React islands approach, API-first design, shared state management, progressive enhancement
   - Benefits: Best of both worlds, gradual migration path, reduced complexity, better performance

3. **Performance Benchmarks**:
   - File Browser Component: Compared Streamlit, Flask+HTMX, React, and Flask+React implementations
   - Data Visualization Component: Compared render times, interaction latency, memory usage, and bundle sizes
   - Analysis: Flask+React hybrid approach provides the best balance of performance and user experience

4. **Recommendation**:
   - Adopt a hybrid approach using Flask for the application framework and React for complex UI components
   - Focus React development on data visualization, file management, and other interaction-heavy components
   - Maintain the framework-agnostic core to support multiple frontend implementations
   - Use the React adapter layer to bridge between core components and React UI
   - Implement progressive enhancement to ensure basic functionality without JavaScript

## Next Steps

1. **Phase 6: Production Readiness**
   - Implement comprehensive error handling and logging
   - Add performance monitoring and optimization
   - Create deployment documentation for different environments
   - Implement automated testing for all components
   - Add accessibility improvements for screen readers and keyboard navigation

2. **Phase 7: Advanced Features**
   - Implement search functionality for the file browser
   - Add file compression/extraction functionality
   - Implement file sharing and collaboration features
   - Create a plugin system for extending the application
   - Add support for internationalization (i18n)

3. **Phase 8: Mobile Enhancements**
   - Add offline mode with service workers
   - Implement Progressive Web App (PWA) capabilities
   - Add support for mobile touch gestures
   - Create a theme system with light/dark mode toggle
   - Optimize performance for mobile devices

4. **Phase 9: Integration Enhancements**
   - Create a unified testing framework for all UI frameworks
   - Implement CI/CD pipelines for automated testing and deployment
   - Add support for containerization (Docker)
   - Create documentation for integrating with other systems
   - Implement analytics and telemetry

## Approval

- [x] Architecture review completed
- [x] Resource allocation approved
- [x] Timeline approved
- [x] Success metrics approved

## Reviewers

- [x] Lead Developer
- [x] UX Designer
- [x] Project Manager