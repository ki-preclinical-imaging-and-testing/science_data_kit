# Science Data Kit (SDK) Streamlit to Flask Migration Roadmap - Version 14

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
| 10 | 2025-10-12 | Completed UI component enhancements: HTMX for dynamic updates, Alpine.js for client-side interactivity, rich preview capabilities, and responsive design |
| 11 | 2025-10-19 | Implemented Chat interface with retrieval-augmented generation capabilities |
| 12 | 2025-10-26 | Completed all remaining low-priority features: Feedback collection, Instructor page, Observation page, Survey page, and Workshop page |
| 13 | 2025-11-02 | Updated roadmap to reflect current status and next steps for Phase 3 (User Experience Optimization) |
| 14 | 2025-11-09 | Implemented end-to-end tests for common workflows, performance benchmarking, and usability testing plan |

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
The Science Data Kit has already begun implementing a framework-agnostic architecture with both Streamlit and Flask adapters. The core business logic has been extracted into framework-independent classes, and a Flask application structure has been established. All high-priority pages (connect, dashboard, file browser, explore, plugin connect), all medium-priority features (About page, cBioPortal browser, Dropbox integration, ISA browser, Map visualization, Microsoft Graph integration, Microsoft Graph exploration, Ontology browser, and User preferences), and all low-priority features (Analytics dashboard, Chat interface, Feedback collection, Instructor page, Observation page, Survey page, and Workshop page) have been implemented in Flask with full functionality. UI component enhancements have been completed, including HTMX for dynamic updates, Alpine.js for client-side interactivity, rich preview capabilities for various file types, and responsive design for all components.

Phase 2 (Flask Implementation Completion) has been completed, and significant progress has been made in Phase 3 (User Experience Optimization). End-to-end tests have been implemented for common workflows, including the File Explorer and Connect page workflows. Performance benchmarking has been implemented to measure page load times and API response times, and compare them with the Streamlit version. A comprehensive usability testing plan has been created to guide the User Experience Optimization phase.

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
   - Enhanced UI components with Flask-specific capabilities
   - HTMX for dynamic updates without full page reloads
   - Alpine.js for client-side interactivity
   - Rich preview capabilities for various file types
   - Responsive design for all components

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

6. **Low-Priority Pages**
   - Analytics dashboard with comprehensive tracking and visualization
   - Chat interface with retrieval-augmented generation capabilities
   - Feedback collection for gathering user feedback
   - Instructor page for workshop facilitators
   - Observation page for workshop observation and data collection
   - Survey page for scanning and analyzing file systems
   - Workshop page with guided tutorials and resources

7. **Testing**
   - Unit tests for API endpoints
   - Comprehensive test coverage for all implemented pages
   - End-to-end tests for Chat interface
   - End-to-end tests for File Explorer workflow
   - End-to-end tests for Connect page workflow
   - Performance benchmarking for page load times and API response times

8. **User Experience Optimization**
   - Usability testing plan
   - Identification of key workflows for optimization

### Streamlit Pages Inventory and Flask Implementation Status

| Streamlit Page | Description | Flask Implementation Status | Priority |
|----------------|-------------|----------------------------|----------|
| about.py | About page with project information | Implemented (about.html) | Medium |
| analytics.py | Analytics dashboard | Implemented (analytics_dashboard.html) | Low |
| base_page.py | Base page class (not a UI page) | Implemented (base.html) | N/A |
| cbioportal_browser.py | cBioPortal data browser | Implemented (cbioportal_browser.html) | Medium |
| chat.py | Chat interface | Implemented (chat.html) | Low |
| connect.py | Connection management | Implemented (connect.html) | High |
| dashboard.py | Dashboard with visualizations | Implemented (dashboard.html) | High |
| dropbox_browser.py | Dropbox file browser | Implemented (dropbox_browser.html) | Medium |
| dropbox_connect.py | Dropbox connection management | Implemented (dropbox_connect.html) | Medium |
| explore.py | Data exploration | Implemented (explore.html) | High |
| feedback.py | Feedback collection | Implemented (feedback.html) | Low |
| file_browser.py | File browser | Implemented (file_explorer.html) | High |
| instructor.py | Instructor page | Implemented (instructor.html) | Low |
| isa_browser.py | ISA browser | Implemented (isa_browser.html) | Medium |
| map.py | Map visualization | Implemented (map.html) | Medium |
| msgraph_connect.py | Microsoft Graph connection | Implemented (msgraph_connect.html) | Medium |
| msgraph_explore.py | Microsoft Graph exploration | Implemented (msgraph_explore.html) | Medium |
| observation.py | Observation page | Implemented (observation.html) | Low |
| ontology.py | Ontology browser | Implemented (ontology.html) | Medium |
| preferences.py | User preferences | Implemented (preferences.html) | Medium |
| survey.py | Survey page | Implemented (survey.html) | Low |
| workshop.py | Workshop page | Implemented (workshop.html) | Low |

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

### Phase 2: Flask Implementation Completion (4-6 weeks) - COMPLETED

**Objective**: Complete the implementation of all features in the Flask version to achieve full feature parity with the Streamlit version.

**Tasks**:
1. ✓ Implement high-priority features
   - ✓ Plugin connection management with improved UI
   - ✓ Complete any missing functionality in existing pages (connect, dashboard, file browser, explore)
   - ✓ Ensure all core functionality is available in the Flask version

2. ✓ Implement medium-priority features
   - ✓ About page with project information
   - ✓ cBioPortal data browser
   - ✓ Dropbox integration (browser and connection)
   - ✓ ISA browser
   - ✓ Map visualization
   - ✓ Microsoft Graph integration (connection)
   - ✓ Microsoft Graph exploration
   - ✓ Ontology browser
   - ✓ User preferences

3. ✓ Implement low-priority features
   - ✓ Analytics dashboard
   - ✓ Chat interface
   - ✓ Feedback collection
   - ✓ Instructor page
   - ✓ Observation page
   - ✓ Survey page
   - ✓ Workshop page

4. ✓ Enhance UI components with Flask-specific capabilities
   - ✓ Implement HTMX for dynamic updates
   - ✓ Add Alpine.js for client-side interactivity
   - ✓ Create rich preview capabilities for various file types
   - ✓ Implement responsive design for all components

5. ✓ Implement comprehensive testing
   - ✓ Unit tests for API endpoints
   - ✓ Integration tests for cBioPortal browser API routes
   - ✓ Integration tests for Dropbox integration API routes
   - ✓ Integration tests for ISA browser API routes
   - ✓ Integration tests for Map visualization API routes
   - ✓ Integration tests for Microsoft Graph integration API routes
   - ✓ Integration tests for Microsoft Graph exploration API routes
   - ✓ Integration tests for Ontology browser API routes
   - ✓ Integration tests for User preferences API routes
   - ✓ Integration tests for Analytics dashboard API routes
   - ✓ Integration tests for Chat interface API routes
   - ✓ End-to-end tests for Chat interface
   - ✓ End-to-end tests for File Explorer workflow
   - ✓ End-to-end tests for Connect page workflow
   - ✓ Performance benchmarks

### Phase 3: User Experience Optimization (2-3 weeks) - IN PROGRESS

**Objective**: Enhance the user experience of the Flask version to exceed the capabilities of the Streamlit version.

**Tasks**:
1. ✓ Conduct usability testing
   - ✓ Create usability testing plan
   - ✓ Identify key workflows for optimization
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
   - Create redirects from Streamlit URLs to Flask equivalents
   - Implement data migration tools for user settings
   - Provide compatibility layer for existing scripts

4. Remove Streamlit dependencies
   - Remove Streamlit from requirements
   - Update CI/CD pipelines
   - Update deployment scripts

5. Clean up codebase
   - Remove Streamlit-specific code
   - Refactor remaining code for clarity
   - Update imports and references

### Phase 5: Containerization and Deployment (2-3 weeks)

**Objective**: Create optimized container configurations for deploying the Flask version of the Science Data Kit.

**Tasks**:
1. Create optimized Docker configuration
   - Create Dockerfile for Flask application
   - Optimize image size and build time
   - Implement multi-stage builds
   - Create development and production configurations

2. Implement Docker Compose setup
   - Create docker-compose.yml for local development
   - Configure services (web, database, etc.)
   - Set up volume mounts for development
   - Create production-ready configuration

3. Create Singularity definition files
   - Create Singularity definition for HPC deployment
   - Optimize for performance on HPC systems
   - Configure for different HPC environments
   - Test on target HPC systems

4. Implement deployment automation
   - Create CI/CD pipelines for automated builds
   - Implement automated testing in containers
   - Create deployment scripts for different environments
   - Set up monitoring and logging

5. Create deployment documentation
   - Document deployment options
   - Create step-by-step deployment guides
   - Document configuration options
   - Create troubleshooting guides

## Next Steps

The next steps in the Streamlit to Flask Migration roadmap are:

1. **Complete User Experience Optimization phase**:
   - Conduct usability testing sessions using the created plan
   - Analyze usability testing results
   - Implement UI/UX improvements based on findings
   - Add Flask-specific enhancements
   - Improve accessibility

2. **Prepare for Streamlit Deprecation and Removal phase**:
   - Create a detailed deprecation plan
   - Begin updating documentation
   - Design transition helpers

3. **Continue testing and quality assurance**:
   - Verify functionality across different browsers and devices
   - Conduct additional performance testing under load
   - Implement automated accessibility testing

## Success Metrics

The success of the Streamlit to Flask migration will be measured by:

1. **Feature Completeness**: 100% of Streamlit features implemented in Flask
2. **Performance Improvements**: Page load times reduced by at least 30%
3. **User Satisfaction**: Positive feedback from user testing
4. **Code Quality**: Reduced codebase size and improved test coverage
5. **Deployment Flexibility**: Successful deployment in container environments

## Implementation Details

### End-to-End Testing Implementation

A comprehensive end-to-end testing framework has been implemented to verify the functionality of critical workflows:

1. **File Explorer Workflow Tests**:
   - Testing page loading
   - Testing directory navigation
   - Testing file operations (create, upload, delete, rename)
   - Testing file preview and download
   - Testing complete workflows combining multiple operations

2. **Connect Page Workflow Tests**:
   - Testing page loading
   - Testing connection management (available and active connections)
   - Testing database connections (SQLite, Neo4j)
   - Testing cloud service connections (Dropbox)
   - Testing connection testing and disconnection
   - Testing complete workflows combining multiple operations

3. **Performance Benchmarking**:
   - Measuring page load times for all Flask pages
   - Measuring API response times for critical endpoints
   - Comparing performance with the Streamlit version
   - Creating visualizations of performance improvements
   - Generating comprehensive reports with statistics

### Usability Testing Plan

A comprehensive usability testing plan has been created to guide the User Experience Optimization phase:

1. **Test Objectives**:
   - Evaluate overall usability of the Flask implementation
   - Identify pain points and areas for improvement
   - Validate that common workflows are intuitive and efficient
   - Compare the user experience with the Streamlit implementation

2. **Test Methodology**:
   - Task-based testing with think-aloud protocol
   - Post-task questionnaires
   - Semi-structured interviews
   - System Usability Scale (SUS) assessment

3. **Task Scenarios**:
   - Core workflows (connection management, file exploration, data exploration, plugin management)
   - Medium-priority features (ontology browser, user preferences, Dropbox integration)
   - Low-priority features (chat interface, analytics dashboard)

4. **Analysis and Reporting**:
   - Quantitative metrics (task success rate, time on task, error rate)
   - Qualitative feedback (pain points, positive feedback, suggestions)
   - Prioritization framework for addressing issues
   - Integration with development cycle

## Conclusion

The Streamlit to Flask Migration roadmap has made significant progress, with the completion of Phase 1 (Feature Parity Assessment) and Phase 2 (Flask Implementation Completion), and substantial progress in Phase 3 (User Experience Optimization). All high-priority, medium-priority, and low-priority features have been implemented in the Flask version, and comprehensive testing has been implemented to ensure functionality and performance.

The implementation of end-to-end tests for common workflows, performance benchmarking, and the creation of a usability testing plan represent significant milestones in the migration process. These tools will help ensure that the Flask implementation not only maintains feature parity with the Streamlit version but also provides an improved user experience.

The next steps focus on completing the User Experience Optimization phase by conducting usability testing, implementing UI/UX improvements, adding Flask-specific enhancements, and improving accessibility. This will be followed by the Streamlit Deprecation and Removal phase, and finally the Containerization and Deployment phase.