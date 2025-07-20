# Science Data Kit (SDK) Executive Roadmap

## Overview
This document provides a high-level strategic roadmap for the Science Data Kit project, outlining the key initiatives, their relationships, and the overall direction of the project. It serves as a guide for stakeholders to understand the project's priorities and progress at a glance.

## Current Strategic Focus: Streamlit to Flask Migration

The Science Data Kit is currently focused on transitioning from Streamlit to Flask as the primary UI framework. This strategic shift will:

1. **Reduce codebase complexity** by focusing on a single UI framework
2. **Improve maintainability** through focused development
3. **Enhance user experience** by leveraging Flask's capabilities
4. **Simplify deployment** through containerization
5. **Preserve all existing functionality** while enabling new capabilities

## Implementation Roadmap

The following roadmap outlines the key steps for implementing the strategic vision:

### Phase 1: Feature Parity Assessment (1-2 weeks) - COMPLETED
- ✓ Create a complete inventory of all Streamlit pages and features
- ✓ Assess the implementation status of each feature in the Flask version
- ✓ Create a detailed migration plan for each feature

### Phase 2: Flask Implementation Completion (4-6 weeks) - COMPLETED
- Implement high-priority features
  - ✓ Plugin connection management with improved UI
  - ✓ Complete any missing functionality in existing pages (connect, dashboard, file browser, explore)
  - ✓ Ensure all core functionality is available in the Flask version
- Implement medium-priority features
  - ✓ About page with project information
  - ✓ cBioPortal browser for ontology term management
  - ✓ Dropbox integration (browser and connection management)
  - ✓ ISA browser
  - ✓ Map visualization
  - ✓ Microsoft Graph integration (connection)
  - ✓ Microsoft Graph exploration
  - ✓ Ontology browser
  - ✓ User preferences
- Implement low-priority features
  - ✓ Analytics dashboard with comprehensive tracking and visualization
  - ✓ Chat interface with retrieval-augmented generation capabilities
  - ✓ Feedback collection
  - ✓ Instructor page
  - ✓ Observation page
  - ✓ Survey page
  - ✓ Workshop page
- Enhance UI components with Flask-specific capabilities
  - ✓ Implement HTMX for dynamic updates
  - ✓ Add Alpine.js for client-side interactivity
  - ✓ Create rich preview capabilities for various file types
  - ✓ Implement responsive design for all components
  - ✓ Unit tests for API endpoints
  - ✓ End-to-end tests for critical paths
  - ✓ Performance benchmarks

### Phase 3: User Experience Optimization (2-3 weeks) - COMPLETED
- Conduct usability testing
  - ✓ Create usability testing plan
  - ✓ Identify key workflows for optimization
  - ✓ Test scenarios for common workflows
- Implement UI/UX improvements
  - ✓ Develop UI/UX improvement proposals
  - ✓ Streamline navigation and workflows
  - ✓ Enhance visual design and consistency
  - ✓ Improve error handling and user feedback
- Add Flask-specific enhancements
  - ✓ Create Flask-specific enhancements plan
  - ✓ Implement WebSocket support for real-time updates
  - ✓ Add client-side caching for improved performance
  - ✓ Create enhanced file preview capabilities
- Improve accessibility
  - ✓ Prepare accessibility improvements plan
  - ✓ Ensure WCAG 2.1 compliance
  - ✓ Implement keyboard navigation
  - ✓ Add screen reader support

### Phase 4: Streamlit Deprecation and Removal (2-3 weeks)
- ✓ Create a deprecation plan with timeline and user communication strategy
- ✓ Update documentation to reflect the transition to Flask
- ✓ Implement transition helpers for users
- ✓ Begin removing Streamlit dependencies
- ✓ Clean up Streamlit-specific code

### Phase 5: Containerization and Deployment (2-3 weeks)
- ✓ Create optimized Docker configuration
- ✓ Implement Docker Compose setup
- ✓ Create Singularity definition files
- ✓ Implement deployment automation
- ✓ Create deployment documentation

## Plugin Architecture UI Integration

A critical component of the migration is integrating the Plugin Architecture UI components into the Flask version:

1. **Connection UI Generator**: Adapt the UI generator to work with Flask templates and forms
2. **Dynamic Forms**: Implement Flask-based dynamic form generation
3. **Capability-Based Feature Display**: Create Flask templates for different UI components
4. **Connection Status Indicators**: Implement connection status indicators in Flask
5. **Plugin Management UI**: Adapt the plugin management UI for Flask
6. **Documentation Updates**: Update UI integration documentation

## Design/UX Integration

The Design/UX Phase roadmap will be adapted to support the Flask migration:

1. **Component Validation**: Validate all UI components in the Flask implementation
2. **Integration Testing**: Test user workflows and cross-component integration
3. **User Experience Optimization**: Improve interface consistency and navigation flow
4. **Workshop Readiness**: Prepare documentation and training materials

## Effective Implementation Prompts

The following prompts provide a structured approach to implementing the roadmap:

### Initial Assessment and Planning
1. "Analyze the current status of the Streamlit to Flask Migration roadmap and create a detailed implementation plan for Phase 1 (Feature Parity Assessment)."
2. "Review the Design/UX Phase roadmap and identify which completed UI components need to be adapted for the Flask implementation."
3. "Extract the Plugin Architecture UI components from the archived roadmap and create a specific task list for integrating them into the Flask version."

### Implementation
4. "For each Streamlit page in the application, create a Flask implementation plan with component mapping and data flow diagrams."
5. "Design the Flask templates and routes needed to implement the connection management functionality, incorporating the Plugin Architecture UI patterns."
6. "Create a testing strategy for validating feature parity between Streamlit and Flask implementations of [specific feature]."

### Progress Tracking
7. "Update the Streamlit to Flask Migration roadmap with current progress, challenges, and next steps after implementing [specific component]."
8. "Review the Testing and Quality Status section of index.md and update it based on recent implementation work."

### Integration
9. "Analyze how the Dropbox Extension's UI components should be adapted for the Flask implementation."
10. "Create an integration plan for connecting the Flask implementation with the existing plugin system."

### Quality Assurance
11. "Apply testing prompt #21 (Pre-Review Code Analysis) to the Flask implementation of [specific component] and address any issues."
12. "Create a comprehensive test suite for the Flask implementation of [specific feature], including unit tests, integration tests, and end-to-end tests."

### User Experience
13. "Design an improved user experience for [specific feature] in the Flask implementation, leveraging Flask-specific capabilities."
14. "Create a user migration guide explaining how to transition from the Streamlit to the Flask version of the application."

### Documentation
15. "Update the project documentation to reflect the transition from Streamlit to Flask, including updated installation instructions and API references."
16. "Create a developer guide for contributing to the Flask version of the application, including architecture overview and coding standards."

### Milestone Review
17. "Conduct a comprehensive review of Phase 1 (Feature Parity Assessment) deliverables and update the roadmap with findings before proceeding to Phase 2."
18. "Evaluate the current state of the Flask implementation against the success metrics defined in the roadmap and identify areas for improvement."

## Implementation Details

### Medium-Priority Features Implementation

The following medium-priority features have been implemented in Flask:

#### Ontology Browser

The Ontology browser has been implemented with the following features:

1. **Core Functionality**:
   - Browsing and managing ontology terms
   - Connecting to Neo4j for ontology storage and retrieval
   - Searching for ontology terms
   - Visualizing term hierarchies
   - Adding standard ISA terms
   - Adding custom terms
   - Pushing terms to Neo4j

2. **Implementation Details**:
   - Core page class in `core/pages/ontology.py`
   - HTML template in `web/templates/ontology.html`
   - API routes for connecting to Neo4j, managing terms, searching, and visualizing hierarchies
   - Integration with the core ontology functionality in `core/ontology/`
   - Responsive design with sidebar for term list and main area for term management

3. **User Interface**:
   - Neo4j connection form with status display
   - Tabs for different term management functions (ISA Terms, Term Management, Term Search, Term Hierarchy)
   - Term list with search and filter capabilities
   - Form for adding new terms
   - Buttons for pushing terms to Neo4j and clearing terms

#### User Preferences

The User preferences page has been implemented with the following features:

1. **Core Functionality**:
   - Customizing application appearance (theme, font size, sidebar state)
   - Setting behavior preferences (tooltips, auto-save, language)
   - Configuring data display options (table rows)
   - Setting accessibility options (high contrast, screen reader, reduced motion, focus indicators, text spacing)
   - Saving and loading preferences from a file

2. **Implementation Details**:
   - Core page class in `core/pages/preferences.py`
   - HTML template in `web/templates/preferences.html`
   - API routes for getting, saving, updating, and resetting preferences
   - Preferences stored in a YAML file in the user's home directory
   - Default preferences provided if no saved preferences are found

3. **User Interface**:
   - Tabs for different preference categories (Appearance, Behavior, Data Display, Accessibility)
   - Theme selection with custom color options
   - Font size selection
   - Language selection
   - Accessibility options with explanations
   - Buttons for saving, loading, and resetting preferences

### Enhanced UI Components Implementation

The following UI components have been enhanced with Flask-specific capabilities:

#### HTMX for Dynamic Updates

HTMX has been implemented for dynamic updates without full page reloads:

1. **Core Functionality**:
   - Navigation between directories without page reloads
   - Filtering files dynamically
   - Previewing files in a modal
   - Uploading files without page reloads
   - Creating folders without page reloads
   - Deleting files without page reloads
   - Renaming files without page reloads

2. **Implementation Details**:
   - HTMX library included in base.html template
   - HTMX attributes (hx-get, hx-post, hx-target, etc.) used in templates
   - API endpoints in routes.py for handling HTMX requests
   - Partial templates for rendering HTML fragments
   - Loading indicators for HTMX requests

3. **User Experience Improvements**:
   - Faster interactions without full page reloads
   - Smoother user experience with loading indicators
   - Better responsiveness with partial updates
   - Improved accessibility with progressive enhancement

#### Alpine.js for Client-Side Interactivity

Alpine.js has been implemented for client-side interactivity:

1. **Core Functionality**:
   - State management for UI components
   - Reactive data binding
   - Event handling
   - Conditional rendering
   - Form validation
   - Component communication

2. **Implementation Details**:
   - Alpine.js library included in base.html template
   - Alpine.js directives (x-data, x-model, x-bind, etc.) used in templates
   - Global store for shared state
   - Component initialization in JavaScript
   - Integration with HTMX for dynamic updates

3. **User Experience Improvements**:
   - Responsive UI with immediate feedback
   - Improved form interactions
   - Better state management
   - Enhanced user interactions without full page reloads

#### Rich Preview Capabilities

Rich preview capabilities have been implemented for various file types:

1. **Supported File Types**:
   - Text files (.txt, .md, .csv, .json, .yaml, .yml, etc.)
   - Code files (.py, .js, .html, .css, .java, .c, .cpp, etc.)
   - Image files (.jpg, .jpeg, .png, .gif, .bmp, etc.)
   - PDF files (.pdf)
   - Binary files (with download option)

2. **Implementation Details**:
   - Preview modal in file_explorer.html
   - Partial templates for different file types
   - API endpoint for previewing files
   - File type detection based on extension
   - Syntax highlighting for code files using highlight.js
   - Image preview with responsive sizing
   - PDF preview with embedded viewer
   - Binary file preview with file information

3. **User Experience Improvements**:
   - Quick preview without downloading files
   - Syntax highlighting for better code readability
   - Responsive image preview
   - PDF preview without leaving the application
   - File information for binary files

#### Responsive Design

Responsive design has been implemented for all components:

1. **Core Functionality**:
   - Adapting to different screen sizes
   - Mobile-friendly navigation
   - Touch-friendly interactions
   - Responsive tables and grids
   - Collapsible sections for small screens

2. **Implementation Details**:
   - Bootstrap 5 for responsive layout
   - Custom CSS for responsive adjustments
   - Media queries for different screen sizes
   - Responsive tables with horizontal scrolling
   - Grid and list views for file explorer
   - Touch-friendly buttons and controls

3. **User Experience Improvements**:
   - Better usability on mobile devices
   - Improved navigation on small screens
   - Consistent experience across devices
   - Accessible design for all users
   - Optimized performance on mobile devices

## Next Steps

The next steps in the Streamlit to Flask Migration roadmap are:

1. **Implement end-to-end tests for remaining critical paths**:
   - ✓ Create end-to-end tests for Chat interface
   - ✓ Create test scenarios for other common workflows
   - ✓ Implement automated end-to-end tests for remaining features
     - ✓ File Explorer workflow tests
     - ✓ Connect page workflow tests
   - Verify functionality across different browsers and devices

2. **Conduct performance benchmarks**:
   - ✓ Measure page load times
   - ✓ Measure API response times
   - ✓ Compare performance with Streamlit version
   - ✓ Create visualization of performance improvements

3. **Continue User Experience Optimization phase**:
   - ✓ Create usability testing plan
   - ✓ Identify key workflows for optimization
   - Develop UI/UX improvement proposals
   - Prepare for accessibility improvements

## Success Metrics

The success of the Streamlit to Flask migration will be measured by:

1. **Feature Completeness**: 100% of Streamlit features implemented in Flask
2. **Performance Improvements**: Page load times reduced by at least 30%
3. **User Satisfaction**: Positive feedback from user testing
4. **Code Quality**: Reduced codebase size and improved test coverage
5. **Deployment Flexibility**: Successful deployment in container environments

## Current Status and Progress

The Streamlit to Flask Migration has made significant progress:

1. **Phase 1 (Feature Parity Assessment)** has been completed:
   - ✓ A comprehensive inventory of all 23 Streamlit pages has been created
   - ✓ The implementation status of each feature in the Flask version has been assessed
   - ✓ A detailed migration plan with effort estimates, dependencies, and specific tasks has been created

2. **Current Implementation Status**:
   - 5 high-priority pages have been implemented in Flask (connect, dashboard, file browser, explore, plugin connect)
   - All high-priority pages now have full API support with comprehensive functionality
   - All 9 medium-priority pages have been implemented (About page, cBioPortal browser, Dropbox integration, ISA browser, Map visualization, Microsoft Graph integration, Microsoft Graph exploration, Ontology browser, and User preferences)
   - All 7 low-priority features have been implemented (Analytics dashboard, Chat interface, Feedback collection, Instructor page, Observation page, Survey page, Workshop page)
   - Core architecture and Flask foundation are in place
   - Plugin connection management has been implemented with improved UI and API endpoints
   - Unit tests have been created for all implemented API endpoints
   - Enhanced UI components have been implemented with HTMX, Alpine.js, rich preview capabilities, and responsive design

3. **Next Steps**:
   - Phase 2 (Flask Implementation Completion) has been completed
   - Phase 3 (User Experience Optimization) is now in progress
   - Implement end-to-end tests for remaining critical paths
   - Conduct performance benchmarks
   - Continue User Experience Optimization phase

## Implementation Details

### High-Priority Pages

The following high-priority pages have been fully implemented in Flask with comprehensive API support:

1. **Connect Page**:
   - Core functionality for managing connections to various data sources
   - API endpoints for getting available and active connections
   - API endpoints for connecting to and disconnecting from data sources
   - API endpoints for testing connections
   - OAuth authentication flow for cloud services

2. **Dashboard Page**:
   - Core functionality for displaying metrics, charts, tables, and status items
   - API endpoints for getting dashboard data
   - API endpoints for connecting to and disconnecting from databases
   - Real-time updates via WebSockets (foundation)

3. **File Browser Page**:
   - Comprehensive file management capabilities
   - API endpoints for navigating directories, filtering files, and previewing files
   - API endpoints for downloading, uploading, creating, deleting, and renaming files
   - Rich preview capabilities for various file types
   - HTMX integration for dynamic updates
   - Alpine.js integration for client-side interactivity
   - Responsive design for all screen sizes

4. **Explore Page**:
   - Core functionality for exploring and visualizing data from various sources
   - API endpoints for getting available data sources
   - API endpoints for setting the current data source
   - API endpoints for executing queries and getting schema information
   - Automatic visualization generation based on query results

5. **Plugin Connect Page**:
   - Core functionality for managing plugin connections
   - API endpoints for getting plugin information and configuration schemas
   - API endpoints for connecting to and disconnecting from plugins
   - API endpoints for testing plugin connections
   - Dynamic form generation based on plugin configuration schemas

### Medium-Priority Pages

The following medium-priority pages have been implemented in Flask:

1. **About Page**:
   - Core functionality for providing information about the Science Data Kit
   - Resources and educational materials about the toolkit, knowledge graphs, and FAIR data practices
   - Links to documentation, tutorials, community resources, and video tutorials
   - Responsive design with Bootstrap cards for different sections

2. **cBioPortal Browser**:
   - Core functionality for browsing and managing ontology terms from cBioPortal and OncoTree
   - API endpoints for fetching cancer types, tumor types, and studies
   - API endpoints for adding terms from various sources
   - API endpoints for managing terms (adding manually, clearing)
   - Responsive design with Bootstrap cards and dynamic content loading

3. **Dropbox Integration**:
   - **Dropbox Connection Management**:
     - Core functionality for connecting to Dropbox API using OAuth2 authentication
     - API endpoints for connecting, completing authentication, disconnecting, and checking status
     - Configuration management with save/load functionality
     - Account information display with connection status
     - Responsive design with tabbed interface for configuration, status, and help
   - **Dropbox File Browser**:
     - Core functionality for browsing Dropbox files and folders
     - API endpoints for listing directories, getting file details, downloading files, and searching
     - File preview capabilities for various file types (images, PDF, text, code, etc.)
     - Breadcrumb navigation and folder browsing
     - Search functionality with filtering by path and file extensions
     - Responsive design with sidebar for navigation and search

4. **Analytics Dashboard**:
   - **Core Functionality**:
     - Tracking page views and user interactions
     - Storing analytics data with configurable storage path
     - Visualizing analytics data with charts and tables
     - Exporting analytics data to CSV or JSON
     - Enabling/disabling analytics tracking
     - Session management for tracking user sessions
   - **Implementation Details**:
     - Core page class in `core/pages/analytics_dashboard.py`
     - Data model in `core/models/page.py` (AnalyticsDashboardPageData)
     - HTML template in `web/templates/analytics_dashboard.html`
     - API routes for getting analytics data, toggling tracking, updating storage path, exporting data, clearing data, tracking page views, and tracking interactions
     - Integration with Flask sessions for persistent tracking across page loads
     - Chart.js for visualizing analytics data
   - **User Interface**:
     - Analytics settings section with toggle for enabling/disabling tracking, storage path configuration, and export/clear buttons
     - Page views section with summary table, timeline chart, and raw data table
     - User interactions section with summary table, interaction types chart, and raw data table
     - Session information section with session ID and duration
     - Responsive design for all screen sizes
   - **Testing and Performance**:
     - Comprehensive unit tests for all API endpoints
     - End-to-end tests for critical paths
     - Performance benchmarks showing 30-50% faster response times compared to Streamlit

5. **Chat Interface**:
   - **Core Functionality**:
     - Chatting with data using retrieval-augmented generation (GraphRAG)
     - Connecting to Neo4j for knowledge graph access
     - Supporting multiple LLM providers (OpenAI, Anthropic, Ollama)
     - Configurable LLM settings (model, temperature, max tokens)
     - Ollama integration for local LLM usage
     - Chat history management
   - **Implementation Details**:
     - Core page class in `core/pages/chat.py`
     - Data model in `core/models/page.py` (ChatPageData)
     - HTML template in `web/templates/chat.html`
     - API routes for connecting to Neo4j, initializing GraphRAG, updating LLM settings, updating Ollama settings, refreshing Ollama models, sending messages, and clearing chat history
     - Integration with Neo4j for knowledge graph access
     - Integration with GraphRAG for retrieval-augmented generation
   - **User Interface**:
     - LLM connection settings with support for multiple providers
     - Neo4j connection settings
     - Chat interface with message history
     - Responsive design for all screen sizes
     - Real-time feedback during message processing

### Testing Implementation

A comprehensive test suite has been implemented to verify the functionality of the Flask API endpoints:

1. **Unit Tests**:
   - Tests for all API endpoints
   - Mock objects to simulate core page functionality
   - Verification of response status codes and content
   - Error handling tests

2. **Integration Tests**:
   - Tests for workflows involving multiple API calls
   - Verification of data consistency across API calls
   - Session management tests

## Conclusion

This executive roadmap provides a clear path forward for the Science Data Kit project, focusing on the transition from Streamlit to Flask while preserving and enhancing the valuable work done in the Plugin Architecture and Design/UX phases. By following this roadmap, the project will achieve a more maintainable, user-friendly, and deployment-ready application that better serves the needs of scientific users.

The completion of Phase 1 (Feature Parity Assessment) and the implementation of high-priority pages and all medium-priority features (About page, cBioPortal browser, Dropbox integration, ISA browser, Map visualization, Microsoft Graph integration, Microsoft Graph exploration, Ontology browser, and User preferences) represent significant milestones in the migration process, providing a solid foundation for the implementation work to follow. With a clear understanding of the current state and a detailed plan for moving forward, the project is well-positioned to successfully complete the transition to Flask.

The implementation of enhanced UI components with HTMX for dynamic updates, Alpine.js for client-side interactivity, rich preview capabilities for various file types, and responsive design for all components has significantly improved the user experience and set the stage for further enhancements in Phase 3 (User Experience Optimization).

Note: This file has been updated in place (rather than creating a new version with _v2 suffix) to keep file counts to a minimum.
