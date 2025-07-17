# Science Data Kit (SDK) Streamlit to Flask Migration Roadmap - Version 01

## Overview
This roadmap outlines a comprehensive plan for transitioning the Science Data Kit from its current Streamlit implementation to a Flask-based web application. Unlike the Framework-Agnostic Architecture roadmap which maintains both frameworks, this roadmap focuses specifically on removing the Streamlit version and fully developing the Flask version as the primary UI.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2025-08-03 | Initial version of Streamlit to Flask Migration roadmap |
| 01 | 2025-08-10 | Added comprehensive inventory of Streamlit pages and features, assessment of implementation status in Flask, and detailed migration plan |

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
The Science Data Kit has already begun implementing a framework-agnostic architecture with both Streamlit and Flask adapters. The core business logic has been extracted into framework-independent classes, and a Flask application structure has been established. However, the Streamlit implementation is still the primary UI, and some features are not yet fully implemented in the Flask version.

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

### Streamlit Pages Inventory and Flask Implementation Status

| Streamlit Page | Description | Flask Implementation Status | Priority |
|----------------|-------------|----------------------------|----------|
| about.py | About page with project information | Not Implemented | Medium |
| analytics.py | Analytics dashboard | Not Implemented | Low |
| base_page.py | Base page class (not a UI page) | Implemented (base.html) | N/A |
| cbioportal_browser.py | cBioPortal data browser | Not Implemented | Medium |
| chat.py | Chat interface | Not Implemented | Low |
| connect.py | Connection management | Implemented (connect.html) | High |
| dashboard.py | Dashboard with visualizations | Implemented (dashboard.html) | High |
| dropbox_browser.py | Dropbox file browser | Not Implemented | Medium |
| dropbox_connect.py | Dropbox connection management | Not Implemented | Medium |
| explore.py | Data exploration | Implemented (explore.html) | High |
| feedback.py | Feedback collection | Not Implemented | Low |
| file_browser.py | File browser | Implemented (file_explorer.html) | High |
| instructor.py | Instructor page | Not Implemented | Low |
| isa_browser.py | ISA browser | Not Implemented | Medium |
| map.py | Map visualization | Not Implemented | Medium |
| msgraph_connect.py | Microsoft Graph connection | Not Implemented | Medium |
| msgraph_explore.py | Microsoft Graph exploration | Not Implemented | Medium |
| observation.py | Observation page | Not Implemented | Low |
| ontology.py | Ontology browser | Not Implemented | Medium |
| plugin_connect.py | Plugin connection management | Not Implemented | High |
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
| explore() | Data exploration | Implemented |

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

### Phase 2: Flask Implementation Completion (4-6 weeks)

**Objective**: Complete the implementation of all features in the Flask version to achieve full feature parity with the Streamlit version.

**Tasks**:
1. Implement high-priority features
   - Plugin connection management with improved UI
   - Complete any missing functionality in existing pages (connect, dashboard, file browser, explore)
   - Ensure all core functionality is available in the Flask version

2. Implement medium-priority features
   - About page with project information
   - cBioPortal data browser
   - Dropbox integration (browser and connection)
   - ISA browser
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
   - Unit tests for all components
   - Integration tests for workflows
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

## Migration Plan Details

### High-Priority Features (Phase 2, Weeks 1-2)

1. **Plugin Connection Management**
   - Effort: Medium (1 week)
   - Dependencies: Existing connect page
   - Tasks:
     - Create plugin_connect.html template
     - Implement plugin connection form
     - Add plugin management UI
     - Implement plugin status indicators
     - Add plugin configuration options

2. **Complete Existing Pages**
   - Effort: Medium (1 week)
   - Dependencies: None
   - Tasks:
     - Review existing Flask pages (connect, dashboard, file browser, explore)
     - Identify missing functionality compared to Streamlit versions
     - Implement missing features
     - Ensure consistent UI/UX across pages

### Medium-Priority Features (Phase 2, Weeks 3-4)

1. **About Page**
   - Effort: Low (1 day)
   - Dependencies: None
   - Tasks:
     - Create about.html template
     - Implement project information display
     - Add team and contributor information
     - Include version and license details

2. **cBioPortal Browser**
   - Effort: High (1 week)
   - Dependencies: None
   - Tasks:
     - Create cbioportal_browser.html template
     - Implement study selection interface
     - Add data visualization components
     - Implement filtering and search functionality

3. **Dropbox Integration**
   - Effort: High (1 week)
   - Dependencies: None
   - Tasks:
     - Create dropbox_connect.html template
     - Create dropbox_browser.html template
     - Implement authentication flow
     - Add file browsing and management UI
     - Implement file preview capabilities

4. **ISA Browser**
   - Effort: Medium (3 days)
   - Dependencies: None
   - Tasks:
     - Create isa_browser.html template
     - Implement ISA model visualization
     - Add navigation and exploration features
     - Implement data import/export functionality

5. **Map Visualization**
   - Effort: Medium (3 days)
   - Dependencies: None
   - Tasks:
     - Create map.html template
     - Implement map rendering with Leaflet.js
     - Add data overlay capabilities
     - Implement interactive features (zoom, pan, select)

6. **Microsoft Graph Integration**
   - Effort: High (1 week)
   - Dependencies: None
   - Tasks:
     - Create msgraph_connect.html template
     - Create msgraph_explore.html template
     - Implement authentication flow
     - Add data browsing and visualization UI
     - Implement search and filtering functionality

7. **Ontology Browser**
   - Effort: Medium (3 days)
   - Dependencies: None
   - Tasks:
     - Create ontology.html template
     - Implement ontology visualization
     - Add search and navigation features
     - Implement term details display

8. **User Preferences**
   - Effort: Medium (2 days)
   - Dependencies: None
   - Tasks:
     - Create preferences.html template
     - Implement settings form
     - Add theme selection
     - Implement preference persistence

### Low-Priority Features (Phase 2, Weeks 5-6)

1. **Analytics Dashboard**
   - Effort: Medium (3 days)
   - Dependencies: None
   - Tasks:
     - Create analytics.html template
     - Implement usage statistics visualization
     - Add data filtering options
     - Implement export functionality

2. **Chat Interface**
   - Effort: High (1 week)
   - Dependencies: None
   - Tasks:
     - Create chat.html template
     - Implement real-time messaging with WebSockets
     - Add message history and persistence
     - Implement user presence indicators

3. **Feedback Collection**
   - Effort: Low (1 day)
   - Dependencies: None
   - Tasks:
     - Create feedback.html template
     - Implement feedback form
     - Add rating system
     - Implement feedback submission and storage

4. **Instructor Page**
   - Effort: Low (1 day)
   - Dependencies: None
   - Tasks:
     - Create instructor.html template
     - Implement course material display
     - Add student progress tracking
     - Implement assignment management

5. **Observation Page**
   - Effort: Low (1 day)
   - Dependencies: None
   - Tasks:
     - Create observation.html template
     - Implement observation form
     - Add data collection features
     - Implement observation storage and retrieval

6. **Survey Page**
   - Effort: Medium (2 days)
   - Dependencies: None
   - Tasks:
     - Create survey.html template
     - Implement survey form builder
     - Add response collection and analysis
     - Implement result visualization

7. **Workshop Page**
   - Effort: Medium (2 days)
   - Dependencies: None
   - Tasks:
     - Create workshop.html template
     - Implement workshop schedule display
     - Add material access and download
     - Implement participant management

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

## Conclusion

This roadmap outlines a comprehensive plan for transitioning the Science Data Kit from Streamlit to Flask. By focusing development efforts on a single UI framework, the project will benefit from reduced complexity, improved maintainability, and enhanced user experience. The Flask implementation will provide richer UI capabilities, better performance, and more flexible deployment options, while preserving all the functionality of the current Streamlit version.

The transition will be managed carefully to minimize disruption for users, with clear communication, detailed migration guides, and a phased approach. The end result will be a more robust, maintainable, and user-friendly application that better serves the needs of scientific users.

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