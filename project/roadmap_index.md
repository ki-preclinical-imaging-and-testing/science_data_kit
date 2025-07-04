# Science Data Kit (SDK) Roadmap Index

## Overview

This document serves as a master index for all roadmaps in the Science Data Kit project. It provides links to all component-specific roadmaps and a high-level overview of the project's direction.

## Active Roadmaps

### Phase 3: SDK Completion and Advanced Features

This roadmap outlines the plan for completing the Science Data Kit development, building on the achievements of Phase 2. It focuses on completing documentation, implementing additional platform integrations, enhancing analysis tools integration, optimizing performance, and adding advanced features.
**Latest Version**: [roadmap_phase3_12.md](roadmap_phase3_12.md)


**Status**: In Progress - Completed all high-priority documentation tasks and platform integrations. Created comprehensive guides for data transformation, database operations, data modeling, API layer, and Jupyter notebook integration. Created interactive tutorials for session management, data source connectors, data transformation, database operations, API usage, and data visualization. Created developer documentation including architecture overview, contribution guidelines, and code style guide. Created documentation for PubMed API usage, ISA Tools ontology usage, SQL database integration, and RESTful API integration. Completed pandas, scikit-learn, matplotlib, plotly, NumPy, SciPy, and D3.js integration modules, and implemented CSV, JSON, and Excel export functionality. Implemented advanced query builder with template integration and query optimization. Completed performance profiling module with memory profiling, code optimization, and benchmarking capabilities. Implemented parallel processing utilities for data operations. Implemented Neo4j configuration optimization with workload analysis and performance monitoring. Implemented batch requests for enhanced query capabilities with BatchQueryBuilder class and execute_batch methods. Implemented data analysis pipeline integration with support for multi-step workflows, various data sources, and integration with analysis tools. Implemented SQL database connector with support for various SQL database systems (SQLite, MySQL, PostgreSQL, MSSQL, Oracle) and RESTful API connector with support for various authentication methods and content types.

**Next Steps**: Begin work on integration with reporting engine. Start implementing user interface enhancements, including customizable user preferences and responsive design. Begin work on additional data source connectors, starting with MongoDB and SPARQL endpoint connectors. Start implementing machine learning integration, beginning with the model training pipeline and evaluation framework.

### Data Source Integration

This roadmap outlines the plan for implementing Google Sheets and Dropbox data source integrations for the Science Data Kit, following the existing provider architecture pattern established with MS Graph API integration.

**Latest Version**: [archive/roadmap_DataSourceIntegration_05.md](archive/roadmap_DataSourceIntegration_05.md)

**Status**: Complete - Provider architecture, Dropbox integration, and Google Sheets integration completed. Integration phase completed with unified data source selector, provider registry, integration tests, and updated documentation.

**Next Steps**: All planned tasks have been completed. Any remaining enhancements have been added to the Phase 3 roadmap.

### Infrastructure GUI

This roadmap outlines the plan for enhancing the Infrastructure GUI components of the Science Data Kit application, focusing on improving server management and connection capabilities to provide a more comprehensive and user-friendly experience.

**Latest Version**: [archive/roadmap_infrastructure_gui_09.md](archive/roadmap_infrastructure_gui_09.md)

**Status**: Complete - Both Phase 1 and Phase 2 completed. Implemented server management UI enhancements, Neo4j container management, support for multiple named database connections, persistent connections, accurate UI state reflection, Jupyter Lab with single/multi-user options, NeoDash with Dev/Prod environment selection, Jupyter notebook templates, token-based authentication, dashboard templates for NeoDash, and integration between NeoDash and Neo4j database.

**Next Steps**: All planned tasks have been completed. Any remaining enhancements have been added to the Phase 3 roadmap.

### Bug Fixes

This roadmap outlines the plan for addressing critical bugs in the Science Data Kit application to ensure it functions correctly and provides a good user experience.

**Latest Version**: [archive/roadmap_phase01_bug_fixes_03.md](archive/roadmap_phase01_bug_fixes_03.md)

**Status**: Complete - Fixed UI navigation, dependency issues, container management, database connection error handling, and deprecated Streamlit API calls. Added graceful handling for missing Neo4j procedures. Updated tests to reflect current state and developed comprehensive testing procedures.

**Next Steps**: All planned tasks have been completed. Ongoing bug monitoring and fixes will be part of regular maintenance.

### Ontology Integration

This roadmap outlines the plan for refactoring the Science Data Kit to focus on ontology integration with Neo4j as the core technology, removing isatools dependencies and implementing a more streamlined approach to ontology management using Neo4j's neosemantics (n10s) plugin.

**Latest Version**: [archive/roadmap_ontology_04.md](archive/roadmap_ontology_04.md)

**Status**: Complete - Removed isatools dependencies, implemented core ontology module with Neo4j's neosemantics (n10s) plugin integration, created comprehensive tests for ontology integration, updated documentation with comprehensive examples and best practices, updated API documentation, removed isatools dependencies from existing tests, and enhanced ontology visualization capabilities.

**Next Steps**: All planned tasks have been completed. Any remaining enhancements have been added to the Phase 3 roadmap.

## Archived Roadmaps

The following roadmap sets have been completed and archived. Any remaining tasks from these roadmaps have been added to the [later_phase.md](later_phase.md) file for future consideration.

### Phase 2: SDK Enhancement and Expansion

This roadmap outlined the plan for enhancing and expanding the Science Data Kit, building on the foundation established in Phase 1. It focused on session management, multimodal data integration, advanced features, performance optimization, and user experience improvements.

**Latest Version**: [archive/roadmap_phase2_24.md](archive/roadmap_phase2_24.md)

**Status**: Complete - Implemented session management functionality, data source connectors, data transformation pipelines, database enhancements, data modeling enhancements, API layer development, user experience improvements, platform integrations, and Jupyter notebook integration.

**Achievements**: Comprehensive session management system, connectors for Office 365, Dropbox, Google Drive, and local storage, data transformation pipelines, query optimization, data modeling enhancements, API layer with client libraries, redesigned dashboard, integrations with NExtSEEK and FAIRDOM-Hub, and Jupyter notebook templates.

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

1. **Complete Documentation**: Finishing the comprehensive user guide, developing interactive tutorials, and creating developer documentation to make the SDK more accessible and easier to use.

2. **Additional Platform Integrations**: Implementing integrations with NC3Rs EDA tool, PubMed, and ISA Tools to expand the SDK's capabilities for scientific data analysis.

3. **Enhanced Analysis Tools Integration**: Adding support for common data science libraries, implementing export to common formats, and adding support for visualization libraries to make data analysis more powerful and flexible.

4. **Performance Optimization**: Profiling and optimizing critical code paths, implementing parallel processing, optimizing memory usage, and improving database performance to make the SDK more efficient and scalable.

5. **Advanced Features**: Implementing advanced features such as advanced query builder, batch requests, data analysis pipeline integration, caching mechanism, and integration with reporting engine to enhance the SDK's capabilities.

6. **User Interface Enhancements**: Adding customizable user preferences, implementing responsive design for mobile devices, and adding accessibility features to improve the user experience.

7. **Additional Data Sources**: Adding support for SQL databases, file system integration, RESTful APIs, SPARQL endpoints, and streaming data sources to expand the SDK's data integration capabilities.

8. **Machine Learning Integration**: Implementing machine learning model integration for data analysis and prediction to enable advanced analytics capabilities.

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

The Science Data Kit project has made significant progress towards its goal of becoming a comprehensive data analysis and visualization tool. Both Phase 1 and Phase 2 of development have been completed, with several major roadmaps successfully implemented and archived:

1. **Phase 1: General SDK Development**: Established the foundation with database restructuring, code standards compliance, and installation improvements.
2. **Microsoft Graph API Integration**: Enables the SDK to access and analyze data from Microsoft 365 services.
3. **Codebase Organization and Documentation**: Improves the organization, reduces redundancy, and enhances documentation in the codebase.
4. **Application Refactoring**: Refactors the application to improve its architecture, maintainability, and user experience.
5. **Phase 2: SDK Enhancement and Expansion**: Implemented session management, multimodal data integration, advanced database features, API layer enhancement, and user experience improvements.

Work is now transitioning to Phase 3, which will focus on completing documentation, implementing additional platform integrations, enhancing analysis tools integration, optimizing performance, and adding advanced features. Current active roadmaps include:

1. **Phase 3: SDK Completion and Advanced Features**: Completing documentation, implementing additional platform integrations, enhancing analysis tools integration, optimizing performance, and adding advanced features.
2. **Data Source Integration**: Implementing Google Sheets and Dropbox data source integrations.
3. **Infrastructure GUI**: Enhancing server management and connection capabilities for containerized services.
4. **Ontology Integration**: Refactoring the SDK to focus on ontology integration with Neo4j as the core technology.

These roadmaps address key areas of functionality that will make the Science Data Kit more versatile and user-friendly. Any remaining tasks from the completed roadmaps have been collected in the later_phase.md file for future consideration.

The project continues to evolve with a focus on documentation, platform integrations, analysis tools, performance optimization, advanced features, user interface enhancements, additional data sources, and machine learning integration, ensuring that the Science Data Kit remains a valuable tool for scientific data management and analysis. Phase 3 will build upon the solid foundation established in Phase 1 and the enhanced functionality developed in Phase 2, taking the SDK to its final form as a comprehensive and powerful tool for scientific data analysis and visualization.
