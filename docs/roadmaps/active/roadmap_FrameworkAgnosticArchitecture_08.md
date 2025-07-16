# Science Data Kit (SDK) Framework-Agnostic Architecture Roadmap - Version 08

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

## Background
The Science Data Kit currently uses render functions (`render_dashboard_page()`, etc.) in a Streamlit-specific way. While there's already good separation between UI components and backend services, the existing pattern can be evolved rather than completely replaced to support multiple frontend frameworks. Features like file browser and remote connection would benefit from richer UI capabilities that could be provided by alternative frameworks.

## Goals
1. Create a framework-agnostic core with pluggable UI layers
2. Support multiple frontend frameworks (Streamlit, Flask+HTMX, React)
3. Maintain "Python-first" philosophy while enabling rich UI experiences
4. Allow gradual migration without disrupting existing functionality
5. Improve user experience for complex UI components

## Current Status
The Framework-Agnostic Architecture implementation has progressed significantly with the completion of Phase 1 (Core Extraction), Phase 2 (Streamlit Adapter Layer), Phase 3 (Flask API Development), and Phase 4 (Enhanced UI Components). The following tasks have been completed:

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
3. ✅ Created enhanced file browser component with:
   - ✅ Drag-and-drop file upload functionality
   - ✅ File operations (create folder, rename, delete)
   - ✅ Rich preview capabilities for various file types
   - ✅ Multi-select with keyboard shortcuts
4. ✅ Improved connection management UI with:
   - ✅ API endpoints for connecting, disconnecting, and testing connections
   - ✅ Loading indicators and status feedback
   - ✅ Error handling and user notifications
   - ✅ Form validation and submission
   - ✅ OAuth flows for cloud services
5. ✅ Adding real-time updates for dashboards
6. ✅ Creating responsive design components
   - ✅ Enhanced CSS with comprehensive media queries
   - ✅ Optimized layouts for different screen sizes
   - ✅ Added touch-friendly UI elements
   - ✅ Ensured proper spacing and readability
   - ✅ Implemented collapsible components for mobile
7. ✅ Implementing comprehensive UI tests
   - ✅ Tests for responsive meta tags
   - ✅ Tests for touch-friendly components
   - ✅ Tests for responsive layouts
   - ✅ Tests for accessibility features
8. ✅ Documenting component architecture
   - ✅ Responsive design architecture
   - ✅ Component structure
   - ✅ Best practices for mobile-first development
   - ✅ Accessibility guidelines

### Phase 5: Cross-Framework Components - ⏳ IN PROGRESS
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
3. ⏳ Add keyboard shortcuts for common operations
4. ⏳ Begin React exploration

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
5. **Phase 5: Cross-Framework Components** - ⏳ IN PROGRESS
   - ✅ Implement unified state management system
   - ✅ Create sophisticated toast notification system
   - ⏳ Add keyboard shortcuts for common operations
   - ⏳ Begin React exploration

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
│   └── notifications/     # Notification system (new) ✅
│       ├── adapters/      # Notification adapters for different frameworks ✅
├── ui/                    # Streamlit implementation
│   ├── adapters/          # Streamlit adapter layer (new) ✅
│   └── pages/             # Streamlit pages (updated) ✅
├── web/                   # Flask implementation (new) ✅
│   ├── adapters/          # Flask adapter layer (new) ✅
│   ├── api/               # REST API endpoints (new) ✅
│   ├── templates/         # Jinja2 templates (new) ✅
│   │   └── partials/      # Partial templates for HTMX (new) ✅
│   └── static/            # Static files (CSS, JS) (new) ✅
└── frontend/              # Future React implementation (planned)
```

The architecture separates the application into distinct layers:

1. **Core Layer**: Contains all business logic, data models, and page orchestration that is independent of any UI framework
2. **UI Adapters**: Framework-specific implementations that translate core data structures into UI components
3. **Framework-Specific UI Components**: Specialized components that leverage the unique capabilities of each framework

### Phase 5: Cross-Framework Components (2-4 weeks) - ⏳ IN PROGRESS

**Objective**: Implement cross-framework components that work across different UI frameworks

**Tasks**:
- ✅ Implement unified state management system
- ✅ Create sophisticated toast notification system
- ⏳ Add keyboard shortcuts for common operations
- ⏳ Begin React exploration

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

3. **Keyboard Shortcuts for Common Operations** (Planned):
   - Create a framework-agnostic keyboard shortcut system
   - Implement adapters for different frameworks
   - Add keyboard shortcuts for common operations:
     - Navigation between pages
     - File operations (upload, download, delete)
     - Form submission
     - Modal dialogs (open, close)
     - Notification management (dismiss, clear all)

4. **React Exploration** (Planned):
   - Evaluate need for full SPA implementation
   - Create React adapter layer
   - Prototype key components (file browser, data visualization)
   - Consider hybrid approach with Flask backend
   - Benchmark performance against other implementations
   - Document React integration patterns

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

## Next Steps

1. Complete Phase 5 (Cross-Framework Components):
   - Implement keyboard shortcuts for common operations
   - Begin React exploration
   - Create React adapter layer
   - Prototype key components (file browser, data visualization)
   - Consider hybrid approach with Flask backend
   - Benchmark performance against other implementations

2. Enhance existing components:
   - Implement search functionality for the file browser
   - Create a unified notification system for user feedback
   - Add file compression/extraction functionality
   - Implement file sharing and collaboration features

3. Improve mobile experience:
   - Add offline mode with service workers
   - Implement Progressive Web App (PWA) capabilities
   - Add support for mobile touch gestures
   - Create a theme system with light/dark mode toggle

4. New tasks identified during implementation:
   - Implement a unified state management system that works across frameworks ✅
   - Create a more sophisticated toast notification system ✅
   - Add keyboard shortcuts for common operations
   - Implement accessibility improvements for screen readers and keyboard navigation
   - Create a unified error handling and logging system
   - Implement a plugin system for extending the application

## Approval

- [x] Architecture review completed
- [x] Resource allocation approved
- [x] Timeline approved
- [x] Success metrics approved

## Reviewers

- [x] Lead Developer
- [x] UX Designer
- [x] Project Manager