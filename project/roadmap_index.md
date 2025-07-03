# Science Data Kit (SDK) Roadmap Index

## Overview

This document serves as a master index for all roadmaps in the Science Data Kit project. It provides links to all component-specific roadmaps and a high-level overview of the project's direction.

## Active Roadmaps

### Phase 2: SDK Enhancement and Expansion

This roadmap outlines the plan for enhancing and expanding the Science Data Kit, building on the foundation established in Phase 1. It focuses on session management, multimodal data integration, advanced features, performance optimization, and user experience improvements.

**Latest Version**: [roadmap_phase2_06.md](roadmap_phase2_06.md)

**Status**: In Progress - Completed session management functionality (including session configuration format, resource registry, dependency tracking, automatic session recovery, and resource access control), data source connectors (Office 365 and Dropbox), data transformation pipelines (pipeline configuration format, tabular data mapping, file tree processing, data validation, and pipeline templates), and database enhancements (query caching and parameterized query templates).

**Next Steps**: Implement Google Drive and local storage connectors, add query logging and performance metrics, implement pagination for large result sets, begin API layer development, and write tests and documentation for the new features.

### Data Source Integration

This roadmap outlines the plan for implementing Google Sheets and Dropbox data source integrations for the Science Data Kit, following the existing provider architecture pattern established with MS Graph API integration.

**Latest Version**: [roadmap_DataSourceIntegration_02.md](roadmap_DataSourceIntegration_02.md)

**Status**: In Progress - Provider architecture, Dropbox integration, and Google Sheets integration completed. Integration phase in progress.

**Next Steps**: Create unified data source selector, register providers in the registry, create integration tests, and update documentation.

### Infrastructure GUI

This roadmap outlines the plan for enhancing the Infrastructure GUI components of the Science Data Kit application, focusing on improving server management and connection capabilities to provide a more comprehensive and user-friendly experience.

**Latest Version**: [roadmap_infrastructure_gui_07.md](roadmap_infrastructure_gui_07.md)

**Status**: In Progress - Phase 1 completed and significant progress on Phase 2. Implemented server management UI enhancements, Neo4j container management, support for multiple named database connections, persistent connections, accurate UI state reflection, Jupyter Lab with single/multi-user options, and NeoDash with Dev/Prod environment selection.

**Next Steps**: Continue Phase 2 by adding Jupyter notebook templates, implementing token-based authentication, creating dashboard templates for NeoDash, and adding integration between NeoDash and Neo4j database.

### Bug Fixes

This roadmap outlines the plan for addressing critical bugs in the Science Data Kit application to ensure it functions correctly and provides a good user experience.

**Latest Version**: [roadmap_phase01_bug_fixes_03.md](roadmap_phase01_bug_fixes_03.md)

**Status**: In Progress - Fixed UI navigation, dependency issues, container management, database connection error handling, and deprecated Streamlit API calls. Added graceful handling for missing Neo4j procedures.

**Next Steps**: Check for other deprecated Streamlit API calls, continue monitoring for issues, update tests to reflect current state, and develop comprehensive testing procedures.

### Ontology Integration

This roadmap outlines the plan for refactoring the Science Data Kit to focus on ontology integration with Neo4j as the core technology, removing isatools dependencies and implementing a more streamlined approach to ontology management using Neo4j's neosemantics (n10s) plugin.

**Latest Version**: [roadmap_ontology_04.md](roadmap_ontology_04.md)

**Status**: In Progress - Removed isatools dependencies, implemented core ontology module with Neo4j's neosemantics (n10s) plugin integration, created comprehensive tests for ontology integration, and updated documentation with comprehensive examples and best practices.

**Next Steps**: Update API documentation, remove isatools dependencies from existing tests, and enhance ontology visualization capabilities.

## Archived Roadmaps

The following roadmap sets have been completed and archived. Any remaining tasks from these roadmaps have been added to the [later_phase.md](later_phase.md) file for future consideration.

### Phase 1: General SDK Development

This roadmap outlined the plan for releasing the first version of the Science Data Kit, addressing database restructuring, code standards compliance, and installation improvements.

**Latest Version**: [archive/roadmap_phase1_07.md](archive/roadmap_phase1_07.md)

**Status**: Complete - Implementation of high-priority tasks from Phase 1 of the roadmap has been completed, including database restructuring, code standards compliance, and installation improvements.

**Achievements**: Unified database connection manager, core entity schemas with validation, comprehensive documentation, improved package structure, and robust testing infrastructure.

### Microsoft Graph API Integration

The Microsoft Graph API integration enables the SDK to access and analyze data from Microsoft 365 services, including Microsoft Teams, SharePoint, OneDrive, Outlook, and user/group information.

**Latest Version**: [archive/roadmap_MSGraphAPI_04.md](archive/roadmap_MSGraphAPI_04.md)

**Status**: Complete - All planned tasks have been implemented, including core functionality, UI components, integration with existing components, testing, documentation, and advanced features.

### Codebase Organization and Documentation

This roadmap focuses on improving the organization, reducing redundancy, and enhancing documentation in the Science Data Kit codebase.

**Latest Version**: [archive/roadmap_CodebaseOrganization_03.md](archive/roadmap_CodebaseOrganization_03.md)

**Status**: Complete - All planned tasks have been implemented, including documentation organization, roadmap standardization, code structure improvements, dependency management, and documentation cross-referencing.

### Application Refactoring

This roadmap focuses on refactoring the Science Data Kit application to improve its architecture, maintainability, and user experience.

**Latest Version**: [archive/roadmap_refactor_app_17.md](archive/roadmap_refactor_app_17.md)

**Status**: Complete - All planned tasks have been implemented, including UI Framework Implementation, Node Class Definition Conflicts Resolution, Core Functionality Refactoring, Navigation System Restoration and Fix, Chat Feature Enhancement, Testing Framework Implementation, and Documentation Updates.

## Project Direction

The Science Data Kit is evolving to become a comprehensive tool for data analysis and visualization, with a focus on:

1. **Session Management**: Implementing robust session management to allow users to save and restore their work environment, including server connections, data sources, and pipelines.

2. **Multimodal Data Integration**: Supporting various data sources and formats, with configurable pipelines for transforming and mapping data into the knowledge graph.

3. **Integration with Multiple Data Sources**: Adding support for various data sources, including Microsoft Graph API, Dropbox, Google Drive, and local storage.

4. **Improved Code Organization**: Ensuring the codebase remains maintainable and follows consistent patterns as it grows.

5. **Comprehensive Documentation**: Providing clear, consistent, and thorough documentation for users and contributors.

6. **Enhanced User Experience**: Developing intuitive UI components and visualization tools to make data exploration and analysis more accessible.

7. **Extensibility**: Creating a flexible architecture that allows for easy integration of new data sources and analysis tools.

8. **Infrastructure Management**: Providing robust capabilities for launching and managing containerized servers (Neo4j, Jupyter, Neodash, Ollama) and connecting to various APIs and filesystems.

## Roadmap Update Process

1. Create a new version by incrementing the version number
2. Copy content from the previous version
3. Update status of tasks and add new tasks as needed
4. Add implementation details for completed tasks
5. Update the "Current Status" and "Next Steps" sections
6. Reference the new roadmap in this master index

## Archiving Process

When a roadmap set is completed (all planned tasks have been implemented):

1. Move all files in the completed roadmap set to the `project/archive/` directory
2. Extract any remaining tasks (marked as "To Do" or in the "Next Steps" section) and add them to the `later_phase.md` file
3. Update this master index to reflect that the roadmap set has been completed and archived

For more detailed guidelines on working with roadmaps and the project directory, see [roadmap_memo.md](roadmap_memo.md).

## Conclusion

The Science Data Kit project has made significant progress towards its goal of becoming a comprehensive data analysis and visualization tool. Phase 1 of development has been completed, with several major roadmaps successfully implemented and archived:

1. **Phase 1: General SDK Development**: Established the foundation with database restructuring, code standards compliance, and installation improvements.
2. **Microsoft Graph API Integration**: Enables the SDK to access and analyze data from Microsoft 365 services.
3. **Codebase Organization and Documentation**: Improves the organization, reduces redundancy, and enhances documentation in the codebase.
4. **Application Refactoring**: Refactors the application to improve its architecture, maintainability, and user experience.

Work is now transitioning to Phase 2, which will focus on session management, multimodal data integration, advanced features, performance optimization, and improved user experience. Current active roadmaps include:

1. **Phase 2: SDK Enhancement and Expansion**: Implementing session management, multimodal data integration, advanced database features, API layer enhancement, performance optimization, and user experience improvements.
2. **Data Source Integration**: Implementing Google Sheets and Dropbox data source integrations.
3. **Infrastructure GUI**: Enhancing server management and connection capabilities for containerized services.
4. **Ontology Integration**: Refactoring the SDK to focus on ontology integration with Neo4j as the core technology.

These roadmaps address key areas of functionality that will make the Science Data Kit more versatile and user-friendly. Any remaining tasks from the completed roadmaps have been collected in the later_phase.md file for future consideration.

The project continues to evolve with a focus on maintainability, extensibility, user experience, and infrastructure management, ensuring that the Science Data Kit remains a valuable tool for scientific data management and analysis. Phase 2 will build upon the solid foundation established in Phase 1, taking the SDK to the next level of functionality and usability.
