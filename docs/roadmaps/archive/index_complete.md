# Science Data Kit (SDK) Complete Roadmap Index

## Overview
This document serves as a comprehensive index for all roadmaps in the Science Data Kit project, including both active and archived roadmaps. It provides links to all component-specific roadmaps and a high-level overview of the project's direction.

## Active Roadmaps

### Design/UX Phase

This roadmap outlines a comprehensive plan for the Design/UX phase of the Science Data Kit, focusing on frontend component validation, user experience optimization, backend validation through the user interface, and workshop preparation integration. This phase is critical for ensuring that the backend architecture established in previous phases is effectively integrated with frontend components and that the overall user experience is thoroughly tested, refined, and validated.

**Latest Version**: [Design/UX Phase Roadmap](../active/roadmap_DesignUX_00.md)

**Status**: Planning - The Design/UX phase roadmap has been defined and is divided into four phases:

1. **Phase 1: Core Component Validation** - Systematically testing all frontend components and their integration with backend systems.
2. **Phase 2: Integration Testing** - Validating user workflows, cross-component integration, and performance.
3. **Phase 3: User Experience Optimization** - Improving interface consistency, navigation flow, error handling, accessibility, and mobile responsiveness.
4. **Phase 4: Workshop Readiness** - Preparing documentation, training materials, feedback collection mechanisms, and demo scenarios.


## Future Roadmaps

The following roadmaps represent important strategic directions for the Science Data Kit but have been temporarily deprioritized to focus on fundamental frontend/backend integration work and user experience optimization. These roadmaps have been moved to the `future/` directory and will be revisited after the completion of the Design/UX phase and Repository Reorganization roadmap.

### Conversational Pipeline Builder

This roadmap outlines a plan for implementing a conversational interface for scientific pipeline creation that integrates with the existing SciDK platform. Users would interact through natural language to build, modify, and visualize scientific data analysis pipelines, with the system leveraging the knowledge graph and component architecture to translate conversations into working pipelines.

**Latest Version**: [Conversational Pipeline Builder Roadmap](../future/roadmap_CPB_00.md)

**Status**: Planning - The Conversational Pipeline Builder roadmap has been defined but not started yet. It is being added to the system for future consideration. The roadmap is divided into four phases:

1. **Phase 1: Foundation** - Basic conversational interface and component integration.
2. **Phase 2: Visual Representation** - Visual pipeline editing and cross-UI integration.
3. **Phase 3: Advanced Natural Language** - Sophisticated domain understanding and complex pipeline support.
4. **Phase 4: Ecosystem Integration** - Full integration with SciDK ecosystem and external tools.

### Knowledge Graph Documentation System

This roadmap outlines the plan for implementing a Knowledge Graph Documentation System that transforms the Science Data Kit into an AI-navigable scientific software platform. The system enables documentation to live naturally in the codebase while providing structured markup and linking for automatic knowledge graph generation. AI agents can query this graph to understand codebase structure and patterns, with the graph automatically rebuilding from source documentation when files change.

**Latest Version**: [Knowledge Graph Documentation System Roadmap](../future/roadmap_kg_00.md)

**Status**: Planning - The Knowledge Graph Documentation System roadmap has been defined and is divided into six phases:

1. **Phase 1: Foundation** - Establishing the core infrastructure for the knowledge graph system without disrupting existing workflows. See [Phase 1 Roadmap](../future/roadmap_kgPhase1_00.md) for details.
2. **Phase 2: Core Integration** - Integrating the knowledge graph system with existing documentation systems and tools. See [Phase 2 Roadmap](../future/roadmap_kgPhase2_00.md) for details.
3. **Phase 3: AI Navigation** - Enabling AI agents to navigate and understand the codebase through the knowledge graph. See [Phase 3 Roadmap](../future/roadmap_kgPhase3_00.md) for details.
4. **Phase 4: User Interfaces** - Creating tools for human interaction with the knowledge graph. See [Phase 4 Roadmap](../future/roadmap_kgPhase4_00.md) for details.
5. **Phase 5: Advanced Features** - Adding advanced capabilities to the knowledge graph system. See [Phase 5 Roadmap](../future/roadmap_kgPhase5_00.md) for details.
6. **Phase 6: Ecosystem** - Platform maturation and broader adoption. See [Phase 6 Roadmap](../future/roadmap_kgPhase6_00.md) for details.

**Supporting Documentation**:
- [Knowledge Graph Vision](../future/knowledge_graph_vision.md) - Detailed vision document explaining the "AI-native software architecture" concept
- [Knowledge Graph Technical Specification](../future/knowledge_graph_technical_spec.md) - Technical specification covering documentation markup standards, schema design, and integration requirements
- [Knowledge Graph Examples](../future/knowledge_graph_examples.md) - Concrete examples showing before/after documentation examples, sample AI queries, and tagging examples

### Strategic Enhancements

This roadmap outlines a comprehensive plan for strategic enhancements to the Science Data Kit platform, focusing on key areas for platform maturation, community adoption, and long-term sustainability. These enhancements build upon the existing Knowledge Graph and Repository Reorganization roadmaps while addressing higher-level platform capabilities that will accelerate adoption in the scientific community.

**Latest Version**: [Strategic Enhancements Roadmap](../future/roadmap_StrategicEnhancements_00.md)

**Status**: Planning - The Strategic Enhancements roadmap has been defined and is divided into three phases:

1. **Phase 1: Foundation Enhancements** - Establishing core capabilities for documentation automation, workshop feedback integration, and domain branch templates.
2. **Phase 2: Community and Performance** - Implementing performance monitoring, AI assistant training, and community contribution frameworks.
3. **Phase 3: Platform Expansion** - Completing domain branch templates and adding cross-platform deployment and scientific workflow integration.

## Archived Roadmaps

The following roadmap sets have been completed and archived. Any remaining tasks from these roadmaps have been added to the [roadmap_later.md](../active/roadmap_later.md) file for future consideration.

### Repository Reorganization

This roadmap outlined the plan for reorganizing the Science Data Kit repository structure, with a particular focus on improving the organization of roadmap files and documentation. The reorganization prepared the repository for the implementation of the Knowledge Graph Documentation System by creating a more logical and maintainable structure for project documentation.

**Latest Version**: [Repository Reorganization Roadmap](roadmap_RepoReorg_04.md)

**Status**: Completed - The Repository Reorganization roadmap has been fully implemented:

1. **Phase 1: Documentation Reorganization** - Completed. New directory structure has been created, roadmap files have been moved to their new locations, redirect notices have been added to original files, and documentation integration has been completed.
2. **Phase 2: Repository Structure Improvements** - Completed. The tools directory has been created and development scripts have been moved to it. The config directory has been created and configuration files have been moved to it. The docker directory has been created and Docker-related files have been moved to it. Docker documentation has been updated and test organization has been improved.

### Phase 6: SDK Outreach and Feature Expansion

This roadmap focused on outreach, user adoption, and implementing high-priority features from the roadmap_later.md file. It prioritized creating workshop materials for hands-on training, enhancing user experience, expanding data source connectors, and implementing machine learning capabilities. The goal was to make the SDK more accessible to researchers and data scientists while continuing to expand its functionality.

**Latest Version**: [roadmap_phase6_20.md](roadmap_phase6_20.md)

**Status**: Complete - Phase 6 focused on outreach, user adoption, and implementing high-priority features.

Completed tasks include:
- Workshop preparation: streamlined installation guide, verification script, Docker setup, preclinical research dataset, data loading script, dataset documentation, 30-minute challenge tutorial, checkpoint verification script, workshop-specific UI configuration, common errors FAQ, research use cases guide, and next steps guide
- User experience enhancements: responsive design for mobile devices, customizable user preferences, accessibility features, theme customization
- Visualization improvements: dashboard visualization strategy, visualization templates, custom visualization templates, dashboard widgets, 3D visualizations
- Data source expansion: MongoDB, SPARQL, Elasticsearch, Cassandra, Kafka, RabbitMQ, WebSocket, and MQTT connectors
- Machine learning integration: model training pipeline, evaluation framework, serialization, cross-validation, model serving, batch inference, real-time inference, and model versioning
- Documentation enhancements: developer guides, troubleshooting guides, code examples, testing strategy documentation, additional examples and use cases (pharmaceutical data analysis workflow), video tutorials, and interactive documentation
- Deployment improvements: Docker containers, Docker Compose setup, Kubernetes configurations, optimized package structure, separate packages for optional components, dependency management, and installation verification tools

With the completion of Phase 6, the Science Data Kit is well-positioned as a comprehensive tool for scientific data analysis, with strong documentation, user-friendly interfaces, extensive data source support, and advanced analytical capabilities.

### Phase 5: SDK Completion and Documentation

This roadmap focused on completing the remaining high-priority tasks from Phase 4 and further enhancing the platform's documentation, testing infrastructure, and code quality. It outlined a comprehensive plan for finalizing the improvements started in Phase 4 and preparing the platform for wider adoption.

**Latest Version**: [roadmap_phase5_05.md](roadmap_phase5_05.md)

**Status**: Complete - Implemented dependency injection system with container, providers, and decorators. Implemented interfaces for core components including database interfaces, API interfaces, and container interfaces. Added type checking with mypy, implemented code formatting with black, generated API documentation from docstrings, created end-to-end tests, added architecture diagrams, and enhanced the caching mechanism with TTL, LRU, and statistics tracking capabilities. Set up code coverage reporting with HTML and XML reports, applied module template to parallel_processing.py, enhanced migration guides with specific examples for legacy components, and updated user guides to match current functionality. All tasks in the Phase 5 roadmap have been completed, preparing the platform for wider adoption.

### Phase 4: SDK Enhancement and Optimization

This roadmap focused on enhancing the maintainability, performance, and user experience of the Science Data Kit. It outlined a comprehensive plan for code organization, quality assurance, documentation improvements, performance optimization, and architecture enhancements.

**Latest Version**: [roadmap_phase4_20.md](roadmap_phase4_20.md)

**Status**: Complete - Implemented background processing functionality, module template with standardized docstring format, linting with flake8, centralized error handling, abstract base classes for providers, abstract base classes for database connectors, Sphinx documentation system, migration from `app/` to `science_data_kit/ui/`, query profiling, streaming data processing, memory profiling, unit tests for core modules, breaking down large modules, GitHub Actions workflow for continuous integration, Neo4j query optimization with proper indexing, automated dependency updates, security scanning, deprecation plan for legacy components, design decisions documentation, plugin architecture for integrations, shared utility functions for common operations, and integration tests for database and API integrations. Remaining tasks have been moved to Phase 5 or to the roadmap_later.md file for future implementation.

### Data Source Integration

This roadmap outlined the plan for implementing Google Sheets and Dropbox data source integrations for the Science Data Kit, following the existing provider architecture pattern established with MS Graph API integration.

**Latest Version**: [roadmap_DataSourceIntegration_05.md](roadmap_DataSourceIntegration_05.md)

**Status**: Complete - Implemented provider architecture, Dropbox integration, and Google Sheets integration with unified data source selector, provider registry, integration tests, and updated documentation.

### Infrastructure GUI

This roadmap outlined the plan for enhancing the Infrastructure GUI components of the Science Data Kit application, focusing on improving server management and connection capabilities.

**Latest Version**: [roadmap_infrastructure_gui_09.md](roadmap_infrastructure_gui_09.md)

**Status**: Complete - Implemented server management UI enhancements, Neo4j container management, support for multiple named database connections, persistent connections, Jupyter Lab with single/multi-user options, NeoDash integration, and token-based authentication.

### Bug Fixes

This roadmap outlined the plan for addressing critical bugs in the Science Data Kit application to ensure it functions correctly and provides a good user experience.

**Latest Version**: [roadmap_phase01_bug_fixes_03.md](roadmap_phase01_bug_fixes_03.md)

**Status**: Complete - Fixed UI navigation, dependency issues, container management, database connection error handling, and deprecated Streamlit API calls. Added graceful handling for missing Neo4j procedures and developed comprehensive testing procedures.

### Ontology Integration

This roadmap outlined the plan for refactoring the Science Data Kit to focus on ontology integration with Neo4j as the core technology, using Neo4j's neosemantics (n10s) plugin.

**Latest Version**: [roadmap_ontology_04.md](roadmap_ontology_04.md)

**Status**: Complete - Removed isatools dependencies, implemented core ontology module with Neo4j's neosemantics plugin, created comprehensive tests, updated documentation, and enhanced ontology visualization capabilities.

### Phase 3: SDK Completion and Advanced Features

This roadmap outlined the plan for completing the Science Data Kit development, building on the achievements of Phase 2. It focused on completing documentation, implementing additional platform integrations, enhancing analysis tools integration, optimizing performance, and adding advanced features.

**Latest Version**: [roadmap_phase3_13.md](roadmap_phase3_13.md)

**Status**: Complete - Implemented comprehensive documentation, platform integrations (NC3Rs EDA tool, PubMed, ISA Tools), analysis tools integration (pandas, scikit-learn, matplotlib, plotly, NumPy, SciPy, D3.js), performance optimization features, and advanced query capabilities. Added SQL database and RESTful API connectors with support for various systems and authentication methods.

### Phase 2: SDK Enhancement and Expansion

This roadmap outlined the plan for enhancing and expanding the Science Data Kit, building on the foundation established in Phase 1. It focused on session management, multimodal data integration, advanced features, performance optimization, and user experience improvements.

**Latest Version**: [roadmap_phase2_24.md](roadmap_phase2_24.md)

**Status**: Complete - Implemented comprehensive session management system, connectors for Office 365, Dropbox, Google Drive, and local storage, data transformation pipelines, query optimization, data modeling enhancements, API layer with client libraries, redesigned dashboard, and integrations with NExtSEEK and FAIRDOM-Hub.

### Phase 1: General SDK Development

This roadmap outlined the plan for releasing the first version of the Science Data Kit, addressing database restructuring, code standards compliance, and installation improvements.

**Latest Version**: [roadmap_phase1_07.md](roadmap_phase1_07.md)

**Status**: Complete - Implemented unified database connection manager, core entity schemas with validation, comprehensive documentation, improved package structure, and robust testing infrastructure.

### Microsoft Graph API Integration

This roadmap enabled the SDK to access and analyze data from Microsoft 365 services, including Microsoft Teams, SharePoint, OneDrive, Outlook, and user/group information.

**Latest Version**: [roadmap_MSGraphAPI_04.md](roadmap_MSGraphAPI_04.md)

**Status**: Complete - Implemented core functionality, UI components, integration with existing components, testing, documentation, and advanced features for Microsoft Graph API integration.

### Codebase Organization and Documentation

This roadmap improved the organization, reduced redundancy, and enhanced documentation in the Science Data Kit codebase.

**Latest Version**: [roadmap_CodebaseOrganization_03.md](roadmap_CodebaseOrganization_03.md)

**Status**: Complete - Implemented documentation organization, roadmap standardization, code structure improvements, dependency management, and documentation cross-referencing.

### Application Refactoring

This roadmap refactored the Science Data Kit application to improve its architecture, maintainability, and user experience.

**Latest Version**: [roadmap_refactor_app_17.md](roadmap_refactor_app_17.md)

**Status**: Complete - Implemented UI Framework improvements, resolved Node Class Definition conflicts, refactored core functionality, fixed navigation system, enhanced chat features, implemented testing framework, and updated documentation.

## Project Direction

The Science Data Kit has evolved into a comprehensive tool for data analysis and visualization. With the completion of all six development phases, the platform has established robust capabilities with strong documentation, testing infrastructure, code quality, and user-focused features. The new Knowledge Graph Documentation System roadmap represents the next evolution in scientific software architecture, transforming the SDK into an AI-navigable platform.

### Current Capabilities

- **Data Management**: Unified database connection manager, comprehensive session management, and data transformation pipelines
- **Integrations**: Support for Microsoft 365, Dropbox, Google Sheets, NC3Rs EDA tool, PubMed, and ISA Tools
- **Analysis Tools**: Integration with pandas, scikit-learn, matplotlib, plotly, NumPy, SciPy, and D3.js
- **Data Sources**: Support for Neo4j, SQL databases, RESTful APIs, MongoDB, SPARQL endpoints, Elasticsearch, Cassandra, Kafka, RabbitMQ, WebSocket streaming, and MQTT
- **Performance Features**: Query optimization, parallel processing, background task management, streaming data processing, memory profiling, and enhanced caching mechanism with TTL, LRU, and statistics tracking
- **Architecture**: Plugin architecture for integrations, abstract base classes for providers and database connectors, centralized error handling, dependency injection system with container, providers, and decorators, and interfaces for core components
- **Testing**: Comprehensive unit tests, integration tests, end-to-end tests, and code coverage reporting
- **Documentation**: Sphinx documentation system, design decisions documentation, user guides, API documentation from docstrings, architecture diagrams, migration guides for legacy components, developer guides, troubleshooting guides, code examples, testing strategy documentation, and video tutorials
- **Code Quality**: Type checking with mypy, code formatting with black, and standardized module structure
- **User Experience**: Responsive design for mobile devices, customizable user preferences, accessibility features, theme customization, dashboard visualization strategy, visualization templates, custom visualization templates, dashboard widgets, and 3D visualizations
- **Machine Learning**: Model training pipeline, evaluation framework, serialization, cross-validation, model serving, batch inference, real-time inference, and model versioning
- **Deployment**: Docker containers, Docker Compose setup, Kubernetes configurations, optimized package structure, separate packages for optional components, dependency management, and installation verification tools
- **Workshop Materials**: Streamlined installation guide, verification script, Docker setup, preclinical research dataset, data loading script, dataset documentation, 30-minute challenge tutorial, checkpoint verification script, workshop-specific UI configuration, common errors FAQ, research use cases guide, and next steps guide

### Future Directions

Future enhancements, as outlined in the [roadmap_later.md](../active/roadmap_later.md) file, may include:

- **Reporting Capabilities**: Integration with reporting engines and custom dashboard creation
- **Performance Optimization**: Optimized data structures for large datasets and consistent pagination
- **Advanced Collaboration**: Real-time collaboration features and shared workspaces
- **Code Organization**: Extracting common patterns into reusable components and implementing adapter pattern for backward compatibility
- **Testing and Quality Assurance**: Setting up pre-commit hooks and creating deployment pipeline
- **Additional Data Sources**: Adding support for Redis, GraphQL, SOAP API, and gRPC

## Roadmap Management

This document serves as an index for all roadmaps, but the detailed processes for updating roadmaps and archiving completed roadmaps are documented in [roadmap_memo.md](../active/roadmap_memo.md).

The roadmap_memo.md file provides comprehensive guidelines for:
- Creating new roadmaps
- Updating existing roadmaps
- Archiving completed roadmaps
- Adding remaining tasks to roadmap_later.md
- Maintaining consistent roadmap formatting and content

Please refer to roadmap_memo.md for detailed instructions on working with roadmaps in this project.

## Conclusion

The Science Data Kit project has successfully achieved its goal of becoming a comprehensive tool for scientific data analysis and visualization. Through the systematic implementation of twelve major roadmaps across six development phases, the SDK has evolved into a robust platform with extensive capabilities.

With all six initial phases now completed and archived, the project has undergone a complete development cycle from initial platform development to user adoption and outreach. Phase 6 represented a significant shift in focus, with an emphasis on creating workshop materials, enhancing user experience, expanding data source connectors, implementing machine learning capabilities, improving documentation, and optimizing deployment options. Many tasks from previous phases have been collected in the [roadmap_later.md](../active/roadmap_later.md) file for future implementation.

The project is now entering a new phase with two active roadmaps:

1. The **Design/UX Phase** roadmap, which focuses on frontend component validation, user experience optimization, backend validation through the user interface, and workshop preparation integration. This phase is critical for ensuring that the backend architecture established in previous phases is effectively integrated with frontend components and that the overall user experience is thoroughly tested, refined, and validated.

2. The **Conversational Pipeline Builder** roadmap, which outlines a future vision for a natural language interface that enables researchers to create sophisticated data analysis pipelines through conversation. This roadmap has been defined but not started yet, and is planned to begin after the completion of the Design/UX phase.

Additionally, two important strategic roadmaps have been temporarily deprioritized to focus on fundamental frontend/backend integration work and user experience optimization:

1. The **Knowledge Graph Documentation System** roadmap, which represents a fundamental shift toward "AI-native software architecture" where the codebase actively communicates its structure and patterns to both human developers and AI agents.

2. The **Strategic Enhancements** roadmap, which focuses on platform maturation, community adoption, and long-term sustainability through documentation automation, workshop feedback integration, domain customization, and other strategic capabilities.

These roadmaps will guide the transformation of the Science Data Kit into a user-friendly, well-tested scientific software platform with a well-organized repository structure and a clear path to advanced capabilities for long-term growth and sustainability.

The workshop at MIT Koch Institute has provided valuable feedback from real users, allowing the platform to be refined based on their needs. With the completion of all planned development phases, the Science Data Kit is now well-positioned as a comprehensive tool for scientific data analysis, with strong documentation, user-friendly interfaces, extensive data source support, and advanced analytical capabilities.

For detailed information about specific roadmaps, refer to the archived roadmap files linked in the "Archived Roadmaps" section above. For information about future development directions, see the "Project Direction" section.
