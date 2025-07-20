# Science Data Kit (SDK) Streamlit to Flask Migration Roadmap - Version 06

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
The Science Data Kit has already begun implementing a framework-agnostic architecture with both Streamlit and Flask adapters. The core business logic has been extracted into framework-independent classes, and a Flask application structure has been established. The high-priority pages (connect, dashboard, file browser, explore, plugin connect) have been implemented in Flask with full functionality. Several medium-priority features have also been implemented, including the About page, cBioPortal browser, Dropbox integration (browser and connection), and ISA browser.

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

6. **Testing**
   - Unit tests for API endpoints
   - Comprehensive test coverage for cBioPortal browser, Dropbox integration, and ISA browser API routes

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
| map.py | Map visualization | Not Implemented | Medium |
| msgraph_connect.py | Microsoft Graph connection | Not Implemented | Medium |
| msgraph_explore.py | Microsoft Graph exploration | Not Implemented | Medium |
| observation.py | Observation page | Not Implemented | Low |
| ontology.py | Ontology browser | Not Implemented | Medium |
| plugin_connect.py | Plugin connection management | Implemented (plugin_connect.html) | High |
| preferences.py | User preferences | Not Implemented | Medium |
| survey.py | Survey page | Not Implemented | Low |
| workshop.py | Workshop page | Not Implemented | Low |

### Flask Routes Inventory

| Flask Route | Description | Status |
|-------------|-------------|--------|
| index() | Main page | Implemented |
| login() | Login page | Implemented |
| logout() | Logout functionality | Implemented |
| dashboard() | Dashboard page | Implemented |
| api/dashboard/data | Dashboard data API | Implemented |
| api/dashboard/connect-database | Connect to database API | Implemented |
| api/dashboard/disconnect-database | Disconnect from database API | Implemented |
| files() | File browser page | Implemented |
| files_api() | File browser API | Implemented |
| navigate_directory() | Directory navigation | Implemented |
| filter_files() | File filtering | Implemented |
| preview_file() | File preview | Implemented |
| download_file() | File download | Implemented |
| raw_file() | Raw file access | Implemented |
| upload_file() | File upload | Implemented |
| create_folder() | Folder creation | Implemented |
| delete_files() | File deletion | Implemented |
| rename_file() | File renaming | Implemented |
| connect() | Connection management | Implemented |
| api/connect/available | Available connections API | Implemented |
| api/connect/active | Active connections API | Implemented |
| api/connect/connect | Connect to source API | Implemented |
| api/connect/disconnect | Disconnect from source API | Implemented |
| api/connect/test | Test connection API | Implemented |
| api/connect/oauth/initiate | Initiate OAuth flow API | Implemented |
| api/connect/oauth/callback | OAuth callback API | Implemented |
| explore() | Data exploration | Implemented |
| api/explore/data-sources | Data sources API | Implemented |
| api/explore/set-data-source | Set data source API | Implemented |
| api/explore/execute-query | Execute query API | Implemented |
| api/explore/schema-info | Schema info API | Implemented |
| plugin_connect() | Plugin connection management | Implemented |
| plugin_info() | Plugin info API | Implemented |
| plugin_config_schema() | Plugin config schema API | Implemented |
| connect_plugin() | Connect to plugin API | Implemented |
| disconnect_plugin() | Disconnect from plugin API | Implemented |
| test_plugin_connection() | Test plugin connection API | Implemented |
| about() | About page | Implemented |
| cbioportal_browser() | cBioPortal browser page | Implemented |
| api/cbioportal/cancer-types | Cancer types API | Implemented |
| api/cbioportal/tumor-types | Tumor types API | Implemented |
| api/cbioportal/studies | Studies API | Implemented |
| api/cbioportal/study/<study_id> | Study details API | Implemented |
| api/cbioportal/add-cancer-types | Add cancer types API | Implemented |
| api/cbioportal/add-tumor-types | Add tumor types API | Implemented |
| api/cbioportal/add-study-data | Add study data API | Implemented |
| api/cbioportal/add-term | Add term API | Implemented |
| api/cbioportal/clear-terms | Clear terms API | Implemented |
| api/cbioportal/terms | Terms API | Implemented |
| dropbox_connect() | Dropbox connection page | Implemented |
| dropbox_browser() | Dropbox browser page | Implemented |
| api/dropbox/connect | Connect to Dropbox API | Implemented |
| api/dropbox/complete-auth | Complete Dropbox OAuth API | Implemented |
| api/dropbox/disconnect | Disconnect from Dropbox API | Implemented |
| api/dropbox/status | Dropbox status API | Implemented |
| api/dropbox/load-config | Load Dropbox config API | Implemented |
| api/dropbox/save-config | Save Dropbox config API | Implemented |
| api/dropbox/files | Dropbox files API | Implemented |
| api/dropbox/file | Dropbox file details API | Implemented |
| api/dropbox/download | Download Dropbox file API | Implemented |
| api/dropbox/preview | Preview Dropbox file API | Implemented |
| api/dropbox/search | Search Dropbox files API | Implemented |
| isa_browser() | ISA browser page | Implemented |
| api/isa/connect | Connect to Neo4j API | Implemented |
| api/isa/disconnect | Disconnect from Neo4j API | Implemented |
| api/isa/standard-terms | Standard ISA terms API | Implemented |
| api/isa/cancer-types | Cancer types API | Implemented |
| api/isa/tumor-types | Tumor types API | Implemented |
| api/isa/studies | Studies API | Implemented |
| api/isa/study/<study_id> | Study details API | Implemented |
| api/isa/add-cancer-types | Add cancer types API | Implemented |
| api/isa/add-tumor-types | Add tumor types API | Implemented |
| api/isa/add-study-data | Add study data API | Implemented |
| api/isa/add-term | Add term API | Implemented |
| api/isa/clear-terms | Clear terms API | Implemented |
| api/isa/terms | Terms API | Implemented |
| api/isa/process-file | Process ISA file API | Implemented |
| api/isa/load-to-neo4j | Load terms to Neo4j API | Implemented |

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
   - Map visualization
   - Microsoft Graph integration (connection and exploration)
   - Ontology browser
   - User preferences

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

## Success Metrics

The success of the Streamlit to Flask migration will be measured by:

1. **Feature Completeness**
   - 100% of Streamlit features implemented in Flask
   - No functionality loss in the transition
   - All user workflows preserved

2. **Performance Improvements**
   - Page load times reduced by at least 30%
   - API response times under 200ms for typical operations
   - Reduced memory usage compared to Streamlit

3. **User Satisfaction**
   - Positive feedback from user testing
   - No increase in support requests related to UI
   - Successful completion of common tasks in user testing

4. **Code Quality**
   - Reduced codebase size by eliminating redundancy
   - Improved test coverage
   - Simplified dependency management
   - Cleaner architecture with single UI framework

5. **Deployment Flexibility**
   - Successful deployment in container environments
   - Support for both Docker and Singularity
   - Simplified deployment process

## Risk Mitigation

1. **Feature Regression**
   - Mitigation: Comprehensive feature inventory and testing
   - Mitigation: Phased approach with user testing at each stage
   - Mitigation: Maintain Streamlit version until Flask version is fully tested

2. **User Disruption**
   - Mitigation: Clear communication about transition timeline
   - Mitigation: Detailed migration guides for users
   - Mitigation: Overlap period where both UIs are available

3. **Performance Issues**
   - Mitigation: Performance testing throughout development
   - Mitigation: Implement caching strategies
   - Mitigation: Optimize database queries and data processing

4. **Development Delays**
   - Mitigation: Prioritize features based on importance
   - Mitigation: Allocate appropriate resources
   - Mitigation: Regular progress tracking and adjustment

## Resource Requirements

- **Phase 1**: 1 senior developer, 1-2 weeks (COMPLETED)
- **Phase 2**: 2 developers (1 senior, 1 junior), 4-6 weeks
- **Phase 3**: 1 senior developer + 1 UX specialist, 2-3 weeks
- **Phase 4**: 1 senior developer, 2-3 weeks
- **Phase 5**: 1 senior developer + 1 DevOps specialist, 2-3 weeks

## Implementation Details

### High-Priority Pages Implementation

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

### Medium-Priority Pages Implementation

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

4. **ISA Browser**:
   - Core functionality for browsing and managing ISA data and ontology terms
   - API endpoints for connecting to and disconnecting from Neo4j databases
   - API endpoints for managing ontology terms (standard ISA terms, cancer types, tumor types, etc.)
   - API endpoints for processing ISA files and extracting node classes, relationships, and properties
   - API endpoints for loading ontology terms into Neo4j
   - Responsive design with tabbed interface for different term sources and management options
   - Integration with Neo4j for graph database visualization and querying

### Testing Implementation

A comprehensive test suite has been implemented to verify the functionality of the Flask API endpoints:

1. **Unit Tests**:
   - Tests for all API endpoints
   - Mock objects to simulate core page functionality
   - Verification of response status codes and content
   - Error handling tests

2. **Integration Tests**:
   - Tests for cBioPortal browser API routes
   - Tests for Dropbox integration API routes
   - Tests for ISA browser API routes
   - Verification of data consistency across API calls
   - Session management tests

## Next Steps

The next steps in the Streamlit to Flask Migration roadmap are:

1. **Continue implementing medium-priority features**:
   - Map visualization
   - Microsoft Graph integration
   - Ontology browser
   - User preferences

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

Significant progress has been made in implementing the high-priority pages (connect, dashboard, file browser, explore, plugin connect) with full functionality. Several medium-priority features have also been implemented, including the About page, cBioPortal browser, Dropbox integration, and ISA browser. Comprehensive test coverage has been added for these features. The next steps are to implement the remaining medium-priority features and enhance the UI components with Flask-specific capabilities.

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