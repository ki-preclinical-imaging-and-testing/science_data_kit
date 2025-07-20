# Science Data Kit (SDK) Streamlit to Flask Migration Roadmap - Version 18

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
| 15 | 2025-11-16 | Developed UI/UX improvement proposals, prepared accessibility improvements plan, and created Flask-specific enhancements plan |
| 16 | 2025-11-23 | Implemented WebSocket support for real-time dashboard updates |
| 17 | 2025-11-30 | Completed all remaining UI/UX improvements and Flask-specific enhancements: test scenarios for common workflows, streamlined navigation and workflows, enhanced visual design and consistency, improved error handling and user feedback, client-side caching, and enhanced file preview capabilities |
| 18 | 2025-12-07 | Completed accessibility improvements: WCAG 2.1 compliance, keyboard navigation, and screen reader support |

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

All UI/UX improvements and Flask-specific enhancements have been completed, including test scenarios for common workflows, streamlined navigation and workflows, enhanced visual design and consistency, improved error handling and user feedback, client-side caching, and enhanced file preview capabilities.

In the latest development cycle, all accessibility improvements have been completed:

1. **WCAG 2.1 Compliance**: The application now meets the Web Content Accessibility Guidelines (WCAG) 2.1 Level AA standards. This includes:
   - Proper semantic HTML structure with appropriate heading levels
   - Sufficient color contrast for text and UI elements
   - Text alternatives for non-text content
   - Keyboard accessibility for all interactive elements
   - Proper form labels and error messages
   - Responsive design that works at different zoom levels

2. **Keyboard Navigation**: The application now supports comprehensive keyboard navigation:
   - Skip link to bypass navigation and go directly to main content
   - Logical tab order for all interactive elements
   - Visible focus indicators for all interactive elements
   - Keyboard shortcuts for common actions (Alt+1 through Alt+5 for navigation, Alt+S for search, Alt+H for help, Alt+P for preferences)
   - Keyboard access to dropdown menus and modal dialogs
   - Escape key support for closing dialogs and panels

3. **Screen Reader Support**: The application now provides proper support for screen readers:
   - ARIA roles, states, and properties for all interactive elements
   - ARIA live regions for dynamic content updates
   - Proper labeling of form controls and buttons
   - Descriptive link text and button labels
   - Announcements for state changes (e.g., when a panel is opened or closed)
   - Proper heading structure for document outline

These accessibility improvements ensure that the application is usable by people with disabilities, including those who use screen readers, keyboard-only navigation, or high contrast mode. A comprehensive test suite has been created to verify the accessibility features, including tests for skip links, keyboard navigation, ARIA attributes, focus indicators, and high contrast mode.

The following components have been implemented:

### High-Priority Pages

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
   - Real-time updates via WebSockets

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

All medium-priority pages have been implemented in Flask with full functionality:

1. **About Page**
2. **cBioPortal Browser**
3. **Dropbox Integration** (browser and connection)
4. **ISA Browser**
5. **Map Visualization**
6. **Microsoft Graph Integration** (connection)
7. **Microsoft Graph Exploration**
8. **Ontology Browser**
9. **User Preferences**

### Low-Priority Features

All low-priority features have been implemented in Flask with full functionality:

1. **Analytics Dashboard**
2. **Chat Interface**
3. **Feedback Collection**
4. **Instructor Page**
5. **Observation Page**
6. **Survey Page**
7. **Workshop Page**

### UI Component Enhancements

The following UI component enhancements have been implemented:

1. **HTMX for Dynamic Updates**
2. **Alpine.js for Client-Side Interactivity**
3. **Rich Preview Capabilities**
4. **Responsive Design**

### User Experience Optimization

The following user experience optimizations have been implemented:

1. **Test Scenarios for Common Workflows**
2. **Streamlined Navigation and Workflows**
3. **Enhanced Visual Design and Consistency**
4. **Improved Error Handling and User Feedback**
5. **Client-Side Caching for Improved Performance**
6. **Enhanced File Preview Capabilities**
7. **Accessibility Improvements**

## Next Steps

The next steps in the Streamlit to Flask Migration roadmap are:

1. **Begin Phase 4: Streamlit Deprecation and Removal**:
   - Create a deprecation plan with timeline and user communication strategy
   - Update documentation to reflect the transition to Flask
   - Implement transition helpers for users (e.g., URL redirects, feature mapping guide)
   - Begin removing Streamlit dependencies from the codebase
   - Clean up codebase by removing Streamlit-specific code

2. **Prepare for Phase 5: Containerization and Deployment**:
   - Evaluate current Docker configuration for optimization opportunities
   - Plan Docker Compose setup for different deployment scenarios
   - Research Singularity requirements for HPC environments
   - Design deployment automation workflows
   - Outline deployment documentation structure

## Success Metrics

The success of the Streamlit to Flask migration will be measured by:

1. **Feature Completeness**: 100% of Streamlit features implemented in Flask
2. **Performance Improvements**: Page load times reduced by at least 30%
3. **User Satisfaction**: Positive feedback from user testing
4. **Code Quality**: Reduced codebase size and improved test coverage
5. **Deployment Flexibility**: Successful deployment in container environments

## Conclusion

The Streamlit to Flask Migration roadmap has made significant progress, with all high-priority, medium-priority, and low-priority features now implemented in Flask with full functionality. The UI component enhancements have been completed, providing a more dynamic, interactive, and responsive user experience. The User Experience Optimization phase has been completed, with all planned improvements implemented, including accessibility features that ensure the application is usable by people with disabilities.

The next phase will focus on deprecating and removing the Streamlit implementation, followed by containerization and deployment optimization. These final phases will complete the transition to Flask as the primary UI framework for the Science Data Kit, resulting in a more maintainable, user-friendly, and deployment-ready application.