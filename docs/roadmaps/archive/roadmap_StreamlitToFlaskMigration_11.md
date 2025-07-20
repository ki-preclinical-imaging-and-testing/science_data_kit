# Science Data Kit (SDK) Streamlit to Flask Migration Roadmap - Version 11

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
The Science Data Kit has already begun implementing a framework-agnostic architecture with both Streamlit and Flask adapters. The core business logic has been extracted into framework-independent classes, and a Flask application structure has been established. The high-priority pages (connect, dashboard, file browser, explore, plugin connect) have been implemented in Flask with full functionality. All medium-priority features have been implemented, including the About page, cBioPortal browser, Dropbox integration (browser and connection), ISA browser, Map visualization, Microsoft Graph integration (connection), Microsoft Graph exploration, Ontology browser, and User preferences. Two low-priority features have been implemented: Analytics dashboard and Chat interface. UI component enhancements have been completed, including HTMX for dynamic updates, Alpine.js for client-side interactivity, rich preview capabilities for various file types, and responsive design for all components.

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

7. **Testing**
   - Unit tests for API endpoints
   - Comprehensive test coverage for cBioPortal browser, Dropbox integration, ISA browser, Map visualization, Microsoft Graph integration, Microsoft Graph exploration, Ontology browser, and User preferences API routes

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
   - ✓ Analytics dashboard
   - ✓ Chat interface
   - Feedback collection
   - Instructor page
   - Observation page
   - Survey page
   - Workshop page

4. Enhance UI components with Flask-specific capabilities
   - ✓ Implement HTMX for dynamic updates
   - ✓ Add Alpine.js for client-side interactivity
   - ✓ Create rich preview capabilities for various file types
   - ✓ Implement responsive design for all components

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
   - ✓ Integration tests for Analytics dashboard API routes
   - ✓ Integration tests for Chat interface API routes
   - ✓ End-to-end tests for Chat interface
   - End-to-end tests for other critical paths
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

## Implementation Details

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

### Chat Interface Implementation

The Chat interface has been implemented with retrieval-augmented generation capabilities:

1. **Core Functionality**:
   - Chatting with data using retrieval-augmented generation (GraphRAG)
   - Connecting to Neo4j for knowledge graph access
   - Supporting multiple LLM providers (OpenAI, Anthropic, Ollama)
   - Configurable LLM settings (model, temperature, max tokens)
   - Ollama integration for local LLM usage
   - Chat history management

2. **Implementation Details**:
   - Core page class in `core/pages/chat.py`
   - Data model in `core/models/page.py` (ChatPageData)
   - HTML template in `web/templates/chat.html`
   - API routes for connecting to Neo4j, initializing GraphRAG, updating LLM settings, updating Ollama settings, refreshing Ollama models, sending messages, and clearing chat history
   - Integration with Neo4j for knowledge graph access
   - Integration with GraphRAG for retrieval-augmented generation

3. **User Interface**:
   - LLM connection settings with support for multiple providers
   - Neo4j connection settings
   - Chat interface with message history
   - Responsive design for all screen sizes
   - Real-time feedback during message processing

## Next Steps

The next steps in the Streamlit to Flask Migration roadmap are:

1. **Complete implementation of remaining low-priority features**:
   - Feedback collection
   - Instructor page
   - Observation page
   - Survey page
   - Workshop page

2. **Implement end-to-end tests for remaining critical paths**:
   - ✓ Create end-to-end tests for Chat interface
   - Create test scenarios for other common workflows
   - Implement automated end-to-end tests for remaining features
   - Verify functionality across different browsers and devices

3. **Conduct performance benchmarks**:
   - Measure page load times
   - Measure API response times
   - Compare performance with Streamlit version

4. **Prepare for User Experience Optimization phase**:
   - Create usability testing plan
   - Identify key workflows for optimization
   - Develop UI/UX improvement proposals

## Success Metrics

The success of the Streamlit to Flask migration will be measured by:

1. **Feature Completeness**: 100% of Streamlit features implemented in Flask
2. **Performance Improvements**: Page load times reduced by at least 30%
3. **User Satisfaction**: Positive feedback from user testing
4. **Code Quality**: Reduced codebase size and improved test coverage
5. **Deployment Flexibility**: Successful deployment in container environments

## Conclusion

The Streamlit to Flask Migration roadmap provides a clear path for transitioning the Science Data Kit from Streamlit to Flask. The completion of Phase 1 (Feature Parity Assessment) and significant progress in Phase 2 (Flask Implementation Completion) demonstrate the project's commitment to this transition. The implementation of all high-priority and medium-priority features, along with two low-priority features (Analytics dashboard and Chat interface), has established a solid foundation for the Flask version of the application.

The Chat interface implementation represents a significant milestone, providing users with a powerful way to interact with their data using retrieval-augmented generation. The integration with Neo4j and support for multiple LLM providers, including local LLMs through Ollama, makes this feature particularly valuable for scientific users working with complex datasets.

The enhanced UI components with HTMX for dynamic updates, Alpine.js for client-side interactivity, rich preview capabilities for various file types, and responsive design for all components have significantly improved the user experience and set the stage for further enhancements in Phase 3 (User Experience Optimization).

The next steps focus on completing the remaining low-priority features, implementing end-to-end tests for other critical paths, conducting performance benchmarks, and preparing for the User Experience Optimization phase. The implementation of end-to-end tests for the Chat interface represents significant progress in ensuring the reliability and functionality of this important feature. With continued progress, the Science Data Kit will achieve a more maintainable, user-friendly, and deployment-ready application that better serves the needs of scientific users.
