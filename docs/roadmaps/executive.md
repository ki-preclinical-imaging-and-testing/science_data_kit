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

### Phase 2: Flask Implementation Completion (4-6 weeks) - IN PROGRESS
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
- Implement low-priority features (analytics dashboard, chat interface, feedback collection, etc.)
- Enhance UI components with Flask-specific capabilities
  - ✓ Unit tests for API endpoints

### Phase 3: User Experience Optimization (2-3 weeks)
- Conduct usability testing
- Implement UI/UX improvements
- Add Flask-specific enhancements
- Improve accessibility

### Phase 4: Streamlit Deprecation and Removal (2-3 weeks)
- Create a deprecation plan
- Update documentation
- Implement transition helpers
- Remove Streamlit dependencies
- Clean up codebase

### Phase 5: Containerization and Deployment (2-3 weeks)
- Create optimized Docker configuration
- Implement Docker Compose setup
- Create Singularity definition files
- Implement deployment automation
- Create deployment documentation

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

## Next Steps

The next steps in the Streamlit to Flask Migration roadmap are:

1. **Complete implementation of low-priority features**:
   - Analytics dashboard
   - Chat interface
   - Feedback collection
   - Instructor page
   - Observation page
   - Survey page
   - Workshop page

2. **Enhance UI components with Flask-specific capabilities**:
   - Implement HTMX for dynamic updates
   - Add Alpine.js for client-side interactivity
   - Create rich preview capabilities for various file types
   - Implement responsive design for all components

3. **Implement end-to-end tests for critical paths**:
   - Create test scenarios for common workflows
   - Implement automated end-to-end tests
   - Verify functionality across different browsers and devices

4. **Conduct performance benchmarks**:
   - Measure page load times
   - Measure API response times
   - Compare performance with Streamlit version

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
   - 3 medium-priority pages have been implemented (About page with project information, cBioPortal browser for ontology term management, Dropbox integration with browser and connection management)
   - 13 pages still need to be implemented, with varying priorities
   - Core architecture and Flask foundation are in place
   - Plugin connection management has been implemented with improved UI and API endpoints
   - Unit tests have been created for all implemented API endpoints

3. **Next Steps**:
   - Continue implementing medium-priority features in Phase 2
   - Focus on ISA browser, Map visualization, and Microsoft Graph integration as the next medium-priority features
   - Enhance UI components with Flask-specific capabilities
   - Implement integration tests for workflows
   - Prepare for user experience optimization in Phase 3

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

Note: This file has been updated in place (rather than creating a new version with _v2 suffix) to keep file counts to a minimum.
