# Science Data Kit (SDK) Framework-Agnostic Architecture Roadmap - Version 07

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

## Background
The Science Data Kit currently uses render functions (`render_dashboard_page()`, etc.) in a Streamlit-specific way. While there's already good separation between UI components and backend services, the existing pattern can be evolved rather than completely replaced to support multiple frontend frameworks. Features like file browser and remote connection would benefit from richer UI capabilities that could be provided by alternative frameworks.

## Goals
1. Create a framework-agnostic core with pluggable UI layers
2. Support multiple frontend frameworks (Streamlit, Flask+HTMX, React)
3. Maintain "Python-first" philosophy while enabling rich UI experiences
4. Allow gradual migration without disrupting existing functionality
5. Improve user experience for complex UI components

## Current Status
The Framework-Agnostic Architecture implementation has progressed significantly with the completion of Phase 1 (Core Extraction), Phase 2 (Streamlit Adapter Layer), Phase 3 (Flask API Development), and continued progress on Phase 4 (Enhanced UI Components). The following tasks have been completed:

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

### Phase 4 (Enhanced UI Components) - ⏳ IN PROGRESS
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
5. **Phase 5: React Exploration** - ⏳ PLANNED
   - Evaluate need for full SPA
   - Prototype key components
   - Consider hybrid approach

## Implementation Details

### Architecture Overview

```
science_data_kit/
├── core/                    # Framework-independent layer
│   ├── services/           # Business logic (existing)
│   ├── pages/             # Page orchestration (new) ✅
│   └── models/            # Shared data structures (extended) ✅
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

### Phase 4: Enhanced UI Components (4-6 weeks) - ✅ COMPLETED

**Objective**: Implement rich UI components using HTMX and Alpine.js

**Tasks**:
- ✅ Add HTMX for dynamic updates without full page reloads
- ✅ Implement Alpine.js for client-side interactivity
- ✅ Create enhanced file browser component
- ✅ Improve connection management UI
- ✅ Implement rich preview capabilities for various file types
- ✅ Add real-time updates for dashboards
- ✅ Create responsive design components
- ✅ Implement comprehensive UI tests
- ✅ Document component architecture

**Implementation Details**:

1. **HTMX Integration**:
   - Added HTMX library to base.html template
   - Created partial templates for dynamic content updates
   - Implemented HTMX endpoints in routes.py for file navigation, filtering, and previews
   - Added loading indicators for better user experience

2. **Alpine.js Integration**:
   - Added Alpine.js library to base.html template
   - Created Alpine.js components for client-side state management
   - Implemented reactive UI elements that respond to state changes
   - Used Alpine.js for file selection and toolbar button states

3. **Enhanced File Browser**:
   - Implemented dynamic directory navigation without page reloads
   - Added file filtering with instant results
   - Created modal-based file preview system for different file types
   - Improved UI with loading indicators and responsive design

4. **Connection Management UI Improvements**:
   - Added API endpoints for connecting, disconnecting, and testing connections
   - Implemented JavaScript to handle form submission and API interactions
   - Added loading indicators and status feedback during operations
   - Implemented error handling and user notifications
   - Added form validation for required fields
   - Created a more interactive user experience with real-time feedback
   - Implemented OAuth flows for cloud services

5. **File Preview System**:
   - Created specialized preview templates for different file types:
     - Text files with syntax highlighting
     - Images with responsive sizing
     - Binary files with appropriate messaging
   - Implemented file download functionality
   - Added modal-based preview system for better user experience

6. **Real-time Dashboard Updates**:
   - Added Flask-SocketIO for WebSocket support
   - Created WebSocket endpoints for dashboard updates
   - Implemented client-side JavaScript to connect to WebSocket server
   - Added event handlers for dashboard data updates
   - Modified DashboardPage class to emit updates when data changes
   - Implemented real-time updates for metrics, charts, and status items

7. **Responsive Design Components**:
   - Enhanced CSS with comprehensive media queries for different screen sizes:
     - Small mobile devices (up to 576px)
     - Medium devices/tablets (576px to 768px)
     - Large devices/desktops (768px to 992px)
     - Extra large devices (992px and up)
   - Optimized layouts for different screen sizes:
     - Stacked buttons and input groups on mobile
     - Adjusted grid layouts for file items
     - Improved spacing and readability
   - Added touch-friendly UI elements:
     - Minimum touch target sizes (44px)
     - Removed tap highlight color
     - Added smooth scrolling for tables
   - Implemented collapsible components for mobile:
     - Keyboard shortcuts card with toggle
     - Responsive toolbar with stacked buttons
   - Added dark mode support with media query

8. **Comprehensive UI Tests**:
   - Created test suite for responsive UI components
   - Implemented tests for responsive meta tags
   - Added tests for touch-friendly components
   - Created tests for responsive layouts
   - Implemented tests for accessibility features
   - Added tests for keyboard shortcuts toggle
   - Created tests for responsive toolbar

9. **Component Architecture Documentation**:
   - Created comprehensive documentation for responsive design architecture
   - Documented component structure and organization
   - Added best practices for mobile-first development
   - Included accessibility guidelines
   - Documented touch-friendly UI implementation
   - Added implementation examples for responsive components
   - Included future enhancement plans

**Focus Areas**:
- File Browser with drag-and-drop, multi-select, and preview
- Connection Management with status monitoring and feedback
- Data Preview with interactive tables and filtering
- Real-time Dashboard Updates
- Responsive Design for mobile and tablet views

### OAuth Implementation Details

The OAuth implementation for cloud services includes the following components:

1. **Core Model Extensions**:
   - Extended ConnectPageData model to include OAuth-specific fields
   - Added support for storing OAuth states and authorization URLs

2. **Core Page Extensions**:
   - Added methods to ConnectPage class for initiating OAuth flows
   - Implemented token management with refresh capabilities
   - Added methods for handling OAuth callbacks

3. **API Endpoints**:
   - Created `/api/connect/oauth/initiate` endpoint for starting OAuth flows
   - Implemented `/api/connect/oauth/callback` endpoint for handling OAuth redirects

4. **UI Components**:
   - Added OAuth-specific UI elements to connection forms
   - Implemented client-side JavaScript for OAuth flow handling
   - Added loading indicators and status feedback during OAuth process

5. **Supported OAuth Providers**:
   - Microsoft Graph API (Microsoft 365 services)
   - Google Drive
   - GitHub
   - Dropbox

### WebSocket Implementation Details

The WebSocket implementation for real-time dashboard updates includes:

1. **Server-Side Components**:
   - Added Flask-SocketIO to the Flask application
   - Created event handlers for WebSocket connections
   - Implemented room-based broadcasting for dashboard updates
   - Added methods to emit updates when dashboard data changes

2. **Client-Side Components**:
   - Added Socket.IO client library to dashboard template
   - Implemented event handlers for WebSocket messages
   - Created functions to update dashboard components in real-time
   - Added connection status indicators

3. **Dashboard Updates**:
   - Real-time updates for metrics
   - Dynamic chart updates
   - Status item updates
   - Table data refreshes

### Responsive Design Implementation Details

The responsive design implementation includes:

1. **Enhanced CSS with Media Queries**:
   - Added comprehensive media queries for different screen sizes
   - Implemented mobile-first approach with progressive enhancement
   - Created responsive utility classes for common patterns

2. **Touch-Friendly UI Elements**:
   - Added btn-touch class with minimum dimensions (44x44px)
   - Implemented touch-friendly spacing and padding
   - Added visual feedback for touch interactions

3. **Optimized Layouts**:
   - Created responsive grid system for file items
   - Implemented stacked layouts for mobile views
   - Added collapsible sections for better mobile experience

4. **Accessibility Improvements**:
   - Added keyboard navigation support
   - Implemented focus indicators for keyboard users
   - Added ARIA attributes for screen readers
   - Created sr-only class for screen reader text

5. **Dark Mode Support**:
   - Added media query for prefers-color-scheme
   - Implemented dark mode color palette
   - Created toggle for user preference

### Phase 5: React Exploration (Future) - ⏳ PLANNED

**Objective**: Evaluate and prototype React-based UI components

**Tasks**:
- Evaluate need for full SPA implementation
- Create React adapter layer
- Prototype key components (file browser, data visualization)
- Consider hybrid approach with Flask backend
- Benchmark performance against other implementations
- Document React integration patterns

### Technical Implementation Details

#### OAuth Flow for Cloud Services

The OAuth flow for cloud services has been implemented with the following steps:

1. **Initiation**:
   ```javascript
   // For OAuth connections, initiate the OAuth flow
   fetch('/api/connect/oauth/initiate', {
       method: 'POST',
       headers: {
           'Content-Type': 'application/json',
       },
       body: JSON.stringify({
           type: type,
           name: name,
           config: config
       }),
   })
   .then(response => response.json())
   .then(data => {
       if (data.success && data.auth_url) {
           // Redirect to the authorization URL
           window.location.href = data.auth_url;
       }
   });
   ```

2. **Authorization**:
   - User is redirected to the OAuth provider's authorization page
   - User grants permissions to the application
   - OAuth provider redirects back to the application with an authorization code

3. **Token Exchange**:
   ```python
   @api_bp.route('/connect/oauth/callback')
   @api_login_required
   def oauth_callback():
       """Handle OAuth callback."""
       # Get query parameters
       code = request.args.get('code')
       state = request.args.get('state')
       
       # Get the base URL for constructing the redirect URI
       base_url = request.host_url.rstrip('/')
       
       page = ConnectPage()
       success, message, connection_id = page.handle_oauth_callback(code, state, base_url)
       
       if success:
           # Redirect to the connect page with a success message
           return jsonify({
               'success': True,
               'message': message,
               'connection_id': connection_id,
               'data': render_page_api(page).json
           })
   ```

4. **Token Management**:
   - Access tokens are stored securely
   - Refresh tokens are used to obtain new access tokens when they expire
   - Token expiration is tracked and handled automatically

#### Real-time Dashboard Updates

The real-time dashboard updates have been implemented with the following components:

1. **WebSocket Server**:
   ```python
   # Initialize SocketIO without an app (will be initialized in create_app)
   socketio = SocketIO()
   
   def create_app(config_class=Config):
       # Initialize extensions
       socketio.init_app(app, cors_allowed_origins="*")
   ```

2. **Event Handlers**:
   ```python
   @socketio.on('connect')
   def handle_connect():
       """Handle client connection to WebSocket."""
       # Check if user is authenticated
       if not session.get('logged_in'):
           return False  # Reject the connection
       
       # Join a room based on the user's session ID
       join_room(session.get('_id', 'anonymous'))
   
   @socketio.on('join_dashboard')
   def handle_join_dashboard(data):
       """Handle client joining the dashboard room."""
       # Join the dashboard room
       join_room('dashboard')
       
       # Get dashboard data
       page = DashboardPage()
       page_data = page.get_page_data()
       
       # Emit dashboard data to the client
       emit('dashboard_data', {
           'metrics': page_data.metrics,
           'charts': page_data.charts,
           'tables': page_data.tables,
           'status_items': page_data.status_items,
           'connected_services': page_data.connected_services
       })
   ```

3. **Dashboard Updates**:
   ```python
   def emit_dashboard_update():
       """Emit dashboard updates to all clients in the dashboard room."""
       # Get dashboard data
       page = DashboardPage()
       page_data = page.get_page_data()
       
       # Emit dashboard data to all clients in the dashboard room
       socketio.emit('dashboard_update', {
           'metrics': page_data.metrics,
           'charts': page_data.charts,
           'tables': page_data.tables,
           'status_items': page_data.status_items,
           'connected_services': page_data.connected_services
       }, room='dashboard')
   ```

4. **Client-Side Integration**:
   ```javascript
   // Initialize Socket.IO connection
   const socket = io();
   
   // Handle connection events
   socket.on('connect', function() {
       console.log('Connected to WebSocket server');
       
       // Join the dashboard room
       socket.emit('join_dashboard', {});
   });
   
   // Handle dashboard updates
   socket.on('dashboard_update', function(data) {
       console.log('Received dashboard update');
       updateDashboard(data);
   });
   ```

### Priority Features for Multi-Framework Support

The following features will be prioritized for multi-framework support due to their need for rich UI capabilities:

1. **File Browser**
   - Current limitations: Basic file listing, limited preview capabilities
   - Enhanced capabilities: ✅ Dynamic navigation, ✅ rich previews, ✅ drag-and-drop, ✅ multi-select, ✅ file operations, ⏳ search

2. **Remote Connections**
   - Current limitations: Basic form-based connection setup
   - Enhanced capabilities: ✅ Status monitoring, ✅ visual feedback, ✅ OAuth flows, ⏳ visual management

3. **Data Preview**
   - Current limitations: Basic table view, limited interactivity
   - Enhanced capabilities: ⏳ Interactive tables, ⏳ pagination, ⏳ column customization

4. **Real-time Updates**
   - Current limitations: Manual refresh required
   - Enhanced capabilities: ✅ WebSocket updates, ✅ progress indicators, ⏳ notifications

### Success Metrics

The success of the framework-agnostic architecture will be measured by:

1. **Zero regression in Streamlit functionality**
   - All existing features continue to work without issues
   - No degradation in performance or user experience

2. **API response times < 200ms**
   - Core API endpoints respond within 200ms for typical operations
   - Complex operations may take longer but provide progress feedback

3. **90% code reuse between frameworks**
   - Business logic is fully reused
   - Data models are fully reused
   - Only UI rendering code is framework-specific

4. **Improved UX metrics**
   - Reduced time to complete common tasks
   - Improved user satisfaction scores
   - Reduced error rates in complex workflows

### Risk Mitigation

1. **Performance degradation**
   - Mitigation: Benchmark core functions before and after refactoring
   - Mitigation: Implement caching at appropriate layers

2. **Feature regression**
   - Mitigation: Comprehensive test suite for all features
   - Mitigation: Phased rollout with feature flags
   - Mitigation: Maintain Streamlit as primary during transition

3. **Increased complexity**
   - Mitigation: Clear documentation of architecture patterns
   - Mitigation: Code reviews focused on architectural compliance
   - Mitigation: Regular refactoring to eliminate duplication

### Resource Requirements

- **Phase 1**: 1 senior developer, 2-3 weeks ✅ COMPLETED
- **Phase 2**: 1 senior developer, 1 week ✅ COMPLETED
- **Phase 3**: 1 senior developer + 1 junior developer, 3-4 weeks ✅ COMPLETED
- **Phase 4**: 1 senior developer + 1 frontend specialist, 4-6 weeks ✅ COMPLETED
- **Phase 5**: 1 senior developer + 1 React specialist, TBD

### Key Decisions

#### Why keep render functions?

The render functions will be maintained but transformed into thin adapters that bridge between the core page classes and the UI frameworks. This approach:

- Enables gradual migration without breaking existing code
- Provides a clear boundary between business logic and UI rendering
- Creates a consistent pattern for all UI frameworks
- Makes testing easier by separating concerns

#### Why Flask + HTMX over pure React?

Flask with HTMX and Alpine.js was chosen as the primary web implementation for several reasons:

- **Python-first approach**: Maintains our commitment to Python as the primary language
- **Lower complexity**: Simpler development model without a complex build system
- **Progressive enhancement**: Can start with basic HTML and add interactivity incrementally
- **Server-rendered foundation**: Better initial load performance and SEO capabilities
- **No build toolchain**: Simpler development workflow without transpilation
- **Easier integration**: More straightforward integration with existing Python codebase

#### Which pages to migrate first?

The migration will follow this sequence:

1. **Simple pages first**: About, Preferences, and other static pages
2. **File Browser**: As a proof of concept for rich UI capabilities ✅ COMPLETED
3. **Connection Management**: To demonstrate interactive forms and status monitoring ✅ COMPLETED
4. **Dashboard**: To demonstrate real-time updates ✅ COMPLETED
5. **Data visualization pages**: To leverage enhanced interactive capabilities
6. **Complex workflow pages**: After patterns are well-established

## Next Steps

1. Begin Phase 5 (React Exploration):
   - Evaluate need for full SPA implementation
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
   - Implement a unified state management system that works across frameworks
   - Develop a strategy for handling client-side state in multi-framework environments
   - Create a more sophisticated toast notification system for user feedback
   - Add keyboard shortcuts for common operations
   - Implement accessibility improvements for screen readers and keyboard navigation

## Approval

- [x] Architecture review completed
- [x] Resource allocation approved
- [x] Timeline approved
- [x] Success metrics approved

## Reviewers

- [x] Lead Developer
- [x] UX Designer
- [x] Project Manager