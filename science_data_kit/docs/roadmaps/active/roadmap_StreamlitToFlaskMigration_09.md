# Science Data Kit (SDK) Streamlit to Flask Migration Roadmap - Version 09

## Overview
This roadmap outlines a comprehensive plan for transitioning the Science Data Kit from its current Streamlit implementation to a Flask-based web application. Unlike the Framework-Agnostic Architecture roadmap which maintains both frameworks, this roadmap focuses specifically on removing the Streamlit version and fully developing the Flask version as the primary UI.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2025-08-03 | Initial version of Streamlit to Flask Migration roadmap |
| 01 | 2025-08-10 | Added comprehensive inventory of Streamlit pages and features, assessment of implementation status in Flask, and detailed migration plan |
| 02 | 2025-08-17 | Updated implementation status with completed plugin connection management page |
| 03 | 2025-08-24 | Completed missing functionality in existing high-priority pages (connect, dashboard, explore) |
| 04 | 2025-08-31 | Implemented About page with project information |
| 05 | 2025-09-07 | Implemented cBioPortal browser and Dropbox integration (browser and connection) with comprehensive test coverage |
| 06 | 2025-09-14 | Implemented ISA browser with comprehensive test coverage |
| 07 | 2025-09-21 | Implemented Map visualization and Microsoft Graph integration (connection) with comprehensive test coverage |
| 08 | 2025-09-28 | Implemented Microsoft Graph exploration with comprehensive test coverage |
| 09 | 2025-10-05 | Implemented Ontology browser and User preferences with comprehensive test coverage |

## Background
The Science Data Kit currently uses Streamlit as its primary UI framework. While Streamlit has served well for rapid prototyping and development, the project has evolved to require more sophisticated UI capabilities, better deployment options, and improved performance characteristics. The existing Framework-Agnostic Architecture roadmap outlines a path to support multiple frameworks simultaneously, but analysis has shown that maintaining multiple UI frameworks increases complexity and development overhead. This roadmap focuses on a more direct approach: completing the transition to Flask and removing the Streamlit implementation entirely.

## Goals
1. Complete the development of the Flask-based web application
2. Remove the Streamlit implementation to reduce codebase complexity
3. Ensure all existing functionality is preserved in the Flask version
4. Leverage Flask's capabilities to enhance UI components and user experience
5. Simplify deployment through containerization
6. Reduce redundancy in the codebase
7. Improve maintainability through focused development on a single UI framework

## Current Status
The Science Data Kit has already begun implementing a framework-agnostic architecture with both Streamlit and Flask adapters. The core business logic has been extracted into framework-independent classes, and a Flask application structure has been established. The high-priority pages (connect, dashboard, file browser, explore, plugin connect) have been implemented in Flask with full functionality. Several medium-priority features have also been implemented, including the About page, cBioPortal browser, Dropbox integration (browser and connection), ISA browser, Map visualization, Microsoft Graph integration (connection), Microsoft Graph exploration, Ontology browser, and User preferences.

The following components have been implemented:

1. **Core Architecture**
   - Framework-independent core classes in `core/pages/`
   - Base page data models in `core/models/`
   - Business logic extraction from render functions

2. **Flask Foundation**
   - Basic Flask application structure in `web/`
   - Flask adapter layer in `web/adapters/`
   - Initial templates in `web/templates/`
   - Authentication and session management

3. **UI Components**
   - Some basic UI components have been implemented in Flask
   - Initial responsive design work has been done

4. **High-Priority Pages**
   - Connect page with full API support for managing connections
   - Dashboard page with API endpoints for database connections and data retrieval
   - File browser page with comprehensive file management capabilities
   - Explore page with data source selection, query execution, and visualization
   - Plugin connect page with plugin management functionality

5. **Medium-Priority Pages**
   - About page with project information and resources
   - cBioPortal browser for ontology term management
   - Dropbox integration (browser and connection management)
   - ISA browser for ISA data and ontology term management
   - Map visualization for graph data visualization and manipulation
   - Microsoft Graph integration (connection management)
   - Microsoft Graph exploration for querying and visualizing Microsoft Graph API data
   - Ontology browser for browsing and managing ontology terms
   - User preferences for customizing application settings

6. **Testing**
   - Unit tests for API endpoints
   - Comprehensive test coverage for cBioPortal browser, Dropbox integration, ISA browser, Map visualization, Microsoft Graph integration, Microsoft Graph exploration, Ontology browser, and User preferences API routes

### Streamlit Pages Inventory and Flask Implementation Status

| Streamlit Page | Description | Flask Implementation Status | Priority |
|----------------|-------------|----------------------------|----------|
| about.py | About page with project information | Implemented (about.html) | Medium |
| analytics.py | Analytics dashboard | Not Implemented | Low |
| base_page.py | Base page class (not a UI page) | Implemented (base.html) | N/A |
| cbioportal_browser.py | cBioPortal data browser | Implemented (cbioportal_browser.html) | Medium |
| chat.py | Chat interface | Not Implemented | Low |
| connect.py | Connection management | Implemented (connect.html) | High |
| dashboard.py | Dashboard with visualizations | Implemented (dashboard.html) | High |
| dropbox_browser.py | Dropbox file browser | Implemented (dropbox_browser.html) | Medium |
| dropbox_connect.py | Dropbox connection management | Implemented (dropbox_connect.html) | Medium |
| explore.py | Data exploration | Implemented (explore.html) | High |
| feedback.py | Feedback collection | Not Implemented | Low |
| file_browser.py | File browser | Implemented (file_explorer.html) | High |
| instructor.py | Instructor page | Not Implemented | Low |
| isa_browser.py | ISA browser | Implemented (isa_browser.html) | Medium |
| map.py | Map visualization | Implemented (map.html) | Medium |
| msgraph_connect.py | Microsoft Graph connection | Implemented (msgraph_connect.html) | Medium |
| msgraph_explore.py | Microsoft Graph exploration | Implemented (msgraph_explore.html) | Medium |
| observation.py | Observation page | Not Implemented | Low |
| ontology.py | Ontology browser | Implemented (ontology.html) | Medium |
| preferences.py | User preferences | Implemented (preferences.html) | Medium |
| survey.py | Survey page | Not Implemented | Low |
| workshop.py | Workshop page | Not Implemented | Low |

## Implementation Plan

### Phase 1: Feature Parity Assessment (1-2 weeks) - COMPLETED

**Objective**: Conduct a comprehensive assessment of all features in the Streamlit version and their implementation status in the Flask version.

**Tasks**:
1. ✓ Create a complete inventory of all Streamlit pages and features
   - ✓ Document all pages in the Streamlit UI
   - ✓ List all UI components and their functionality
   - ✓ Identify complex interactions and workflows

2. ✓ Assess the implementation status of each feature in the Flask version
   - ✓ Categorize features as "Implemented", "Partially Implemented", or "Not Implemented"
   - ✓ Document gaps and differences in functionality
   - ✓ Prioritize features based on importance and complexity

3. ✓ Create a detailed migration plan for each feature
   - ✓ Estimate effort required for each feature
   - ✓ Identify dependencies between features
   - ✓ Create a prioritized implementation schedule

### Phase 2: Flask Implementation Completion (4-6 weeks) - IN PROGRESS

**Objective**: Complete the implementation of all features in the Flask version to achieve full feature parity with the Streamlit version.

**Tasks**:
1. Implement high-priority features
   - ✓ Plugin connection management with improved UI
   - ✓ Complete any missing functionality in existing pages (connect, dashboard, file browser, explore)
   - ✓ Ensure all core functionality is available in the Flask version

2. Implement medium-priority features
   - ✓ About page with project information
   - ✓ cBioPortal data browser
   - ✓ Dropbox integration (browser and connection)
   - ✓ ISA browser
   - ✓ Map visualization
   - ✓ Microsoft Graph integration (connection)
   - ✓ Microsoft Graph exploration
   - ✓ Ontology browser
   - ✓ User preferences

3. Implement low-priority features
   - Analytics dashboard
   - Chat interface
   - Feedback collection
   - Instructor page
   - Observation page
   - Survey page
   - Workshop page

4. Enhance UI components with Flask-specific capabilities
   - Implement HTMX for dynamic updates
   - Add Alpine.js for client-side interactivity
   - Create rich preview capabilities for various file types
   - Implement responsive design for all components

5. Implement comprehensive testing
   - ✓ Unit tests for API endpoints
   - ✓ Integration tests for cBioPortal browser API routes
   - ✓ Integration tests for Dropbox integration API routes
   - ✓ Integration tests for ISA browser API routes
   - ✓ Integration tests for Map visualization API routes
   - ✓ Integration tests for Microsoft Graph integration API routes
   - ✓ Integration tests for Microsoft Graph exploration API routes
   - ✓ Integration tests for Ontology browser API routes
   - ✓ Integration tests for User preferences API routes
   - End-to-end tests for critical paths
   - Performance benchmarks

### Phase 3: User Experience Optimization (2-3 weeks)

**Objective**: Enhance the user experience of the Flask version to exceed the capabilities of the Streamlit version.

**Tasks**:
1. Conduct usability testing
   - Create test scenarios for common workflows
   - Observe users interacting with the application
   - Collect feedback on pain points and suggestions

2. Implement UI/UX improvements
   - Streamline navigation and workflows
   - Enhance visual design and consistency
   - Improve error handling and user feedback
   - Optimize performance for common operations

3. Add Flask-specific enhancements
   - Implement WebSocket support for real-time updates
   - Add client-side caching for improved performance
   - Create enhanced file preview capabilities
   - Implement drag-and-drop functionality for file operations

4. Improve accessibility
   - Ensure WCAG 2.1 compliance
   - Implement keyboard navigation
   - Add screen reader support
   - Create high-contrast mode

### Phase 4: Streamlit Deprecation and Removal (2-3 weeks)

**Objective**: Gradually deprecate and remove the Streamlit implementation while ensuring a smooth transition for users.

**Tasks**:
1. Create a deprecation plan
   - Set timeline for Streamlit deprecation
   - Communicate plan to users
   - Provide migration guidance

2. Update documentation
   - Update user guides to focus on Flask UI
   - Create migration guides for users
   - Update developer documentation

3. Implement transition helpers
   - Add prominent notices in Streamlit UI about upcoming deprecation
   - Provide links to equivalent functionality in Flask UI
   - Create tools to migrate user settings and preferences

4. Remove Streamlit dependencies
   - Identify all Streamlit-specific code
   - Remove Streamlit-specific dependencies
   - Update build and deployment scripts

5. Clean up codebase
   - Remove Streamlit-specific code
   - Refactor adapter layer to focus on Flask
   - Update imports and references
   - Remove unused files and directories

### Phase 5: Containerization and Deployment (2-3 weeks)

**Objective**: Optimize deployment of the Flask application through containerization and deployment automation.

**Tasks**:
1. Create optimized Docker configuration
   - Develop production-ready Dockerfile
   - Implement multi-stage builds for efficiency
   - Configure appropriate base images

2. Implement Docker Compose setup
   - Create development environment configuration
   - Set up production environment configuration
   - Configure service dependencies

3. Create Singularity definition files
   - Develop Singularity configuration for HPC environments
   - Implement conversion process from Docker to Singularity
   - Configure writable directories for Singularity containers

4. Implement deployment automation
   - Create CI/CD pipelines for automated builds
   - Implement automated testing in containers
   - Develop deployment scripts for various environments

5. Create deployment documentation
   - Document container configuration options
   - Create deployment guides for different environments
   - Provide troubleshooting information

## Implementation Details

### Medium-Priority Pages Implementation

The following medium-priority pages have been implemented in Flask:

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

## Conclusion

This roadmap outlines a comprehensive plan for transitioning the Science Data Kit from Streamlit to Flask. By focusing development efforts on a single UI framework, the project will benefit from reduced complexity, improved maintainability, and enhanced user experience. The Flask implementation will provide richer UI capabilities, better performance, and more flexible deployment options, while preserving all the functionality of the current Streamlit version.

The transition will be managed carefully to minimize disruption for users, with clear communication, detailed migration guides, and a phased approach. The end result will be a more robust, maintainable, and user-friendly application that better serves the needs of scientific users.

Significant progress has been made in implementing the high-priority pages (connect, dashboard, file browser, explore, plugin connect) with full functionality. All medium-priority features have also been implemented, including the About page, cBioPortal browser, Dropbox integration, ISA browser, Map visualization, Microsoft Graph integration, Microsoft Graph exploration, Ontology browser, and User preferences. Comprehensive test coverage has been added for these features. The next steps are to implement the remaining low-priority features and enhance the UI components with Flask-specific capabilities.

## Approval

- [x] Architecture review completed
- [ ] Resource allocation approved
- [ ] Timeline approved
- [ ] Success metrics approved

## Reviewers

- [x] Lead Developer
- [ ] UX Designer
- [ ] Product Manager
- [ ] DevOps Specialist