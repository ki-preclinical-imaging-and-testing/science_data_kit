# Science Data Kit (SDK) Roadmap Index

## Overview
This document serves as a master index for all roadmaps in the Science Data Kit project. It provides links to all active roadmaps and a high-level overview of the project's direction.

## Active Roadmaps

### Design/UX Phase

This roadmap outlines a comprehensive plan for the Design/UX phase of the Science Data Kit, focusing on frontend component validation, user experience optimization, backend validation through the user interface, and workshop preparation integration. This phase is critical for ensuring that the backend architecture established in previous phases is effectively integrated with frontend components and that the overall user experience is thoroughly tested, refined, and validated.

**Latest Version**: [Design/UX Phase Roadmap](active/roadmap_DesignUX_18.md)

**Status**: In Progress - The Design/UX phase roadmap has made significant progress in Phase 1: Core Component Validation, Phase 2: Integration Testing, Phase 3: User Experience Optimization, and Phase 4: Workshop Readiness. Sixty-five high-priority tasks have been completed.

The roadmap is divided into four phases:

1. **Phase 1: Core Component Validation** - Systematically testing all frontend components and their integration with backend systems.
2. **Phase 2: Integration Testing** - Validating user workflows, cross-component integration, and performance.
3. **Phase 3: User Experience Optimization** - Improving interface consistency, navigation flow, error handling, accessibility, and mobile responsiveness.
4. **Phase 4: Workshop Readiness** - Preparing documentation, training materials, feedback collection mechanisms, and demo scenarios.

### Streamlit to Flask Migration

This roadmap outlines a comprehensive plan for transitioning the Science Data Kit from its current Streamlit implementation to a Flask-based web application. Unlike the Framework-Agnostic Architecture roadmap which maintains both frameworks, this roadmap focuses specifically on removing the Streamlit version and fully developing the Flask version as the primary UI.

**Latest Version**: [Streamlit to Flask Migration Roadmap](active/roadmap_StreamlitToFlaskMigration_02.md)

**Status**: In Progress - The Streamlit to Flask Migration roadmap has completed Phase 1 (Feature Parity Assessment) and is now making progress in Phase 2 (Flask Implementation Completion). Key accomplishments include:

1. **Comprehensive Inventory**: A complete inventory of all 23 Streamlit pages and their features has been created.
2. **Implementation Status Assessment**: The implementation status of each feature in the Flask version has been assessed, identifying 5 high-priority pages that have been implemented and 16 pages that still need to be implemented.
3. **Detailed Migration Plan**: A detailed migration plan has been created with effort estimates, dependencies, and specific tasks for each feature.
4. **Plugin Connection Management**: The plugin connection management page has been implemented with improved UI and API endpoints.

The current implementation status shows:
- 5 high-priority pages have been implemented in Flask (connect, dashboard, file browser, explore, plugin connect)
- 16 pages still need to be implemented, with varying priorities
- Core architecture and Flask foundation are in place

The roadmap is divided into five phases:

1. **Phase 1: Feature Parity Assessment** (COMPLETED) - Conduct a comprehensive assessment of all features in the Streamlit version and their implementation status in the Flask version.
2. **Phase 2: Flask Implementation Completion** (IN PROGRESS) - Complete the implementation of all features in the Flask version to achieve full feature parity with the Streamlit version.
3. **Phase 3: User Experience Optimization** - Enhance the user experience of the Flask version to exceed the capabilities of the Streamlit version.
4. **Phase 4: Streamlit Deprecation and Removal** - Gradually deprecate and remove the Streamlit implementation while ensuring a smooth transition for users.
5. **Phase 5: Containerization and Deployment** - Optimize deployment of the Flask application through containerization and deployment automation.

### Dropbox Extension

This roadmap outlines a comprehensive plan for implementing the Dropbox extension for the Science Data Kit. The extension will enable integration with Dropbox cloud storage, including file access and synchronization, team folder management, and file sharing metadata extraction.

**Latest Version**: [Dropbox Extension Roadmap](active/roadmap_DropboxExtension_08.md)

**Status**: Progressing in Phase 3 - The Dropbox extension implementation has completed Phase 1 (Foundation) and Phase 2 (Advanced Features). Phase 3 (UI Integration) is now well underway with the implementation of both the Dropbox connection management page and the file browser component.

The roadmap is divided into four phases:

1. **Phase 1: Foundation** - Authentication and connection setup, basic file/folder operations, core integration with entity schemas, and Neo4j knowledge graph integration.
2. **Phase 2: Advanced Features** - Real-time sync capabilities, team folder management, file sharing and collaboration metadata extraction, and error handling/retry logic.
3. **Phase 3: UI Integration** - Streamlit page components for cloud connection management, progress monitoring for sync operations, and cloud data visualization.
4. **Phase 4: Enterprise Features** - Batch processing for large datasets, scheduling and automated sync, advanced security and permissions handling, and performance optimization.

## Future Roadmaps

The following roadmaps represent important strategic directions for the Science Data Kit but have been temporarily deprioritized to focus on fundamental frontend/backend integration work and user experience optimization. These roadmaps have been moved to the `future/` directory and will be revisited after the completion of the Design/UX phase and Repository Reorganization roadmap.

For more information about future roadmaps, see the [Future Roadmaps README](future/README.md).

### Containerized Flask/React Architecture

This roadmap outlines a comprehensive plan for implementing a containerized Flask/React architecture for the Science Data Kit. This approach will provide a more containerization-friendly alternative to the current Streamlit implementation, enabling better scalability, deployment flexibility, and enhanced user interface capabilities. The roadmap includes support for both Docker and Singularity containerization, making it suitable for various environments including HPC clusters.

**Latest Version**: [Containerized Flask/React Architecture Roadmap](future/roadmap_ContainerizedFlaskReact_00.md)

**Status**: Planning - The Containerized Flask/React Architecture roadmap has been defined but not started yet. The roadmap is divided into five phases:

1. **Phase 1: Flask API Foundation** - Create Flask application structure, implement core API endpoints, set up authentication and session management, and implement comprehensive API testing.
2. **Phase 2: React Frontend Development** - Set up React application structure, implement core UI components, create API integration layer, and develop responsive design.
3. **Phase 3: Containerization** - Create optimized Dockerfiles for Flask backend and React frontend, implement Docker Compose configuration, and set up development and production environments.
4. **Phase 4: Integration and Deployment** - Integrate with existing SDK core functionality, implement comprehensive end-to-end testing, create deployment documentation, and provide migration guides from Streamlit.
5. **Phase 5: Singularity Implementation** - Create Singularity definition files, implement conversion process from Docker to Singularity, set up writable directories for Singularity containers, and create deployment scripts for HPC environments.

### Cloud Extensions

The Science Data Kit is expanding its cloud integration capabilities with the following extension roadmaps:

#### Google Drive/Workspace Extension

This roadmap outlines a comprehensive plan for implementing the Google Drive/Workspace extension for the Science Data Kit. The extension will enable integration with Google's cloud services, including Google Drive for file access and synchronization, Google Sheets for spreadsheet parsing, and Google Docs for metadata extraction.

**Latest Version**: [Google Drive/Workspace Extension Roadmap](future/roadmap_GoogleExtension_00.md)

**Status**: Planning - The Google Drive/Workspace extension roadmap has been defined but not started yet. The roadmap is divided into four phases:

1. **Phase 1: Foundation** - Authentication and connection setup, basic file/folder operations, core integration with entity schemas, and Neo4j knowledge graph integration.
2. **Phase 2: Advanced Features** - Real-time sync capabilities, spreadsheet/document parsing, collaboration metadata extraction, and error handling/retry logic.
3. **Phase 3: UI Integration** - Streamlit page components for cloud connection management, progress monitoring for sync operations, and cloud data visualization.
4. **Phase 4: Enterprise Features** - Batch processing for large datasets, scheduling and automated sync, advanced security and permissions handling, and performance optimization.

#### Enhanced Microsoft Graph Extension

This roadmap outlines a comprehensive plan for enhancing the Microsoft Graph extension for the Science Data Kit. The extension enables integration with Microsoft 365 services including SharePoint, OneDrive, Teams, and Excel through the Microsoft Graph API.

**Latest Version**: [Microsoft Graph Extension Roadmap](future/roadmap_MSGraphExtension_00.md)

**Status**: In Progress - The Microsoft Graph extension is partially implemented, with basic functionality for connecting to Microsoft Graph API and accessing some Microsoft 365 services. The roadmap is divided into four phases:

1. **Phase 1: Foundation** - Enhanced authentication and connection setup, SharePoint integration, core integration with entity schemas, and Neo4j knowledge graph integration.
2. **Phase 2: Advanced Features** - OneDrive file management, Teams conversation analysis, Excel file processing, and error handling/retry logic.
3. **Phase 3: UI Integration** - Streamlit page components for cloud connection management, progress monitoring for operations, and cloud data visualization.
4. **Phase 4: Enterprise Features** - Batch processing for large datasets, scheduling and automated operations, advanced security and permissions handling, and performance optimization.

### Conversational Pipeline Builder

This roadmap outlines a plan for implementing a conversational interface for scientific pipeline creation that integrates with the existing SciDK platform. Users would interact through natural language to build, modify, and visualize scientific data analysis pipelines, with the system leveraging the knowledge graph and component architecture to translate conversations into working pipelines.

**Latest Version**: [Conversational Pipeline Builder Roadmap](future/roadmap_CPB_00.md)

**Status**: Planning - The Conversational Pipeline Builder roadmap has been defined but not started yet. It is being added to the system for future consideration. The roadmap is divided into four phases:

1. **Phase 1: Foundation** - Basic conversational interface and component integration.
2. **Phase 2: Visual Representation** - Visual pipeline editing and cross-UI integration.
3. **Phase 3: Advanced Natural Language** - Sophisticated domain understanding and complex pipeline support.
4. **Phase 4: Ecosystem Integration** - Full integration with SciDK ecosystem and external tools.

### Knowledge Graph Documentation System

This roadmap outlines the plan for implementing a Knowledge Graph Documentation System that transforms the Science Data Kit into an AI-navigable scientific software platform. The system enables documentation to live naturally in the codebase while providing structured markup and linking for automatic knowledge graph generation. AI agents can query this graph to understand codebase structure and patterns, with the graph automatically rebuilding from source documentation when files change.

**Latest Version**: [Knowledge Graph Documentation System Roadmap](future/roadmap_kg_00.md)

**Status**: Planning - The Knowledge Graph Documentation System roadmap has been defined and is divided into six phases:

1. **Phase 1: Foundation** - Establishing the core infrastructure for the knowledge graph system without disrupting existing workflows. See [Phase 1 Roadmap](future/roadmap_kgPhase1_00.md) for details.
2. **Phase 2: Core Integration** - Integrating the knowledge graph system with existing documentation systems and tools. See [Phase 2 Roadmap](future/roadmap_kgPhase2_00.md) for details.
3. **Phase 3: AI Navigation** - Enabling AI agents to navigate and understand the codebase through the knowledge graph. See [Phase 3 Roadmap](future/roadmap_kgPhase3_00.md) for details.
4. **Phase 4: User Interfaces** - Creating tools for human interaction with the knowledge graph. See [Phase 4 Roadmap](future/roadmap_kgPhase4_00.md) for details.
5. **Phase 5: Advanced Features** - Adding advanced capabilities to the knowledge graph system. See [Phase 5 Roadmap](future/roadmap_kgPhase5_00.md) for details.
6. **Phase 6: Ecosystem** - Platform maturation and broader adoption. See [Phase 6 Roadmap](future/roadmap_kgPhase6_00.md) for details.

**Supporting Documentation**:
- [Knowledge Graph Vision](future/knowledge_graph_vision.md) - Detailed vision document explaining the "AI-native software architecture" concept
- [Knowledge Graph Technical Specification](future/knowledge_graph_technical_spec.md) - Technical specification covering documentation markup standards, schema design, and integration requirements
- [Knowledge Graph Examples](future/knowledge_graph_examples.md) - Concrete examples showing before/after documentation examples, sample AI queries, and tagging examples

### GitHub Integration

This roadmap outlines a comprehensive plan for integrating GitHub issues and automation into the Science Data Kit development workflow. This integration will improve tracking, visibility, and collaboration for development progress, debugging cycles, and roadmap task management.

**Latest Version**: [GitHub Integration Roadmap](future/roadmap_GitHubIntegration_00.md)

**Status**: Initial Implementation - The GitHub Integration roadmap has been defined and partially implemented with the following components:

1. **GitHub Actions Workflow** - A GitHub Actions workflow has been created for automated issue management
2. **CLI Helper Scripts** - Helper scripts have been created for common issue management tasks
3. **Roadmap-to-Issues Integration** - A Python script has been created to sync roadmap tasks with GitHub issues
4. **Debugging Workflow** - A debugging workflow script has been created to integrate debugging cycles with GitHub issues

The roadmap is divided into four phases:

1. **Phase 1: GitHub Actions Setup** - Setting up GitHub Actions for automated issue management
2. **Phase 2: CLI Integration** - Creating CLI scripts for common issue management tasks
3. **Phase 3: Roadmap-to-Issues Integration** - Developing a system to sync roadmap tasks with GitHub issues
4. **Phase 4: Documentation and Training** - Creating documentation and training materials for GitHub integration

### Strategic Enhancements

This roadmap outlines a comprehensive plan for strategic enhancements to the Science Data Kit platform, focusing on key areas for platform maturation, community adoption, and long-term sustainability. These enhancements build upon the existing Knowledge Graph and Repository Reorganization roadmaps while addressing higher-level platform capabilities that will accelerate adoption in the scientific community.

**Latest Version**: [Strategic Enhancements Roadmap](future/roadmap_StrategicEnhancements_00.md)

**Status**: Planning - The Strategic Enhancements roadmap has been defined and is divided into three phases:

1. **Phase 1: Foundation Enhancements** - Establishing core capabilities for documentation automation, workshop feedback integration, and domain branch templates.
2. **Phase 2: Community and Performance** - Implementing performance monitoring, AI assistant training, and community contribution frameworks.
3. **Phase 3: Platform Expansion** - Completing domain branch templates and adding cross-platform deployment and scientific workflow integration.

## Testing and Quality Status

### Design/UX Phase
**Implementation Status**: In Progress - Phase 1: Core Component Validation
**Testing Status**: Active - Comprehensive testing framework implemented and executed
**Next Testing Steps**: Test navigation components and responsive design
**Recommended Testing**: Use prompts #22 for workshop feature testing, #19 for quality assessment, #23 for performance validation
**Quality Gates**: Core Component Validation before Integration Testing, Integration Testing before User Experience Optimization

### Streamlit to Flask Migration
**Implementation Status**: In Progress - Phase 2: Flask Implementation Completion
**Testing Status**: Active - Testing plugin connection management implementation
**Next Testing Steps**: Test plugin connection management functionality and API endpoints
**Recommended Testing**: Use prompts #19 for quality assessment, #21 for code analysis, #23 for performance validation
**Quality Gates**: Feature Parity Assessment before Flask Implementation Completion, User Experience Optimization before Streamlit Deprecation

### Dropbox Extension
**Implementation Status**: In Progress - Phase 3: UI Integration
**Testing Status**: Active - Testing UI components
**Next Testing Steps**: Test Dropbox connection management and file browser components
**Recommended Testing**: Use prompts #19 for quality assessment, #21 for code analysis, #24 for real data testing
**Quality Gates**: UI Integration before Enterprise Features

### Future Roadmaps

#### Containerized Flask/React Architecture
**Implementation Status**: Planning - Moved to future roadmaps
**Testing Status**: On hold until return to active development
**Next Testing Steps**: Not applicable at this stage
**Recommended Testing**: Use prompts #19 for quality assessment, #21 for code analysis when reactivated
**Quality Gates**: Streamlit to Flask Migration completion before starting

#### Conversational Pipeline Builder
**Implementation Status**: Planning - Moved to future roadmaps
**Testing Status**: On hold until return to active development
**Next Testing Steps**: Not applicable at this stage
**Recommended Testing**: Will be determined when reactivated
**Quality Gates**: Design/UX Phase completion before starting

#### Knowledge Graph Documentation System  
**Implementation Status**: Planning - Moved to future roadmaps
**Testing Status**: On hold until return to active development
**Recommended Testing**: Use prompts #21, #19, #24 for foundation validation when reactivated
**Quality Gates**: Design/UX Phase completion before reactivation

#### GitHub Integration
**Implementation Status**: Initial Implementation - Partially implemented in future roadmaps
**Testing Status**: On hold until return to active development
**Next Testing Steps**: Test GitHub Actions workflow and CLI scripts
**Recommended Testing**: Use prompts #19, #21 for code quality assessment
**Quality Gates**: Design/UX Phase completion before full implementation

#### Strategic Enhancements
**Implementation Status**: Planning - Moved to future roadmaps
**Testing Status**: On hold until return to active development
**Next Testing Steps**: Use prompt #21 from prompts.md once reactivated
**Recommended Testing**: Use prompts #19, #22, #24 for high-priority enhancements when reactivated
**Quality Gates**: Knowledge Graph Documentation System foundation before reactivation

### Testing Workflow Integration
Use the testing prompts in `docs/roadmaps/prompts.md` (#17-24) at these natural checkpoints:
- **After completing 3-5 implementation tasks** in any roadmap
- **Before transitioning between roadmap phases**
- **When preparing for workshops or user feedback**
- **When implementing core architectural components**

For guidance on selecting appropriate testing prompts, start with prompt #21 (Pre-Review Code Analysis) to assess current state and get recommendations for additional validation.

## Archived Roadmaps

### Plugin Architecture

This roadmap outlined a comprehensive plan for refactoring the Science Data Kit's connection system to create a consistent, extensible plugin architecture. The goal was to establish clear boundaries between core functionality, protocols, and provider-specific implementations while reducing redundancy and improving maintainability.

**Latest Version**: [Plugin Architecture Roadmap](archive/roadmap_PluginArchitecture_09.md)

**Status**: Completed - The Plugin Architecture implementation has been completed with all phases successfully implemented:

1. **Phase 1: Core Protocol System** - Established the foundation for all connections by creating base protocol classes, implementing capability mixins, and migrating existing code.
2. **Phase 2: Plugin Standardization** - Refactored existing providers into plugins with standardized interfaces and configuration.
3. **Phase 3: Connection Manager** - Implemented a unified connection management system with plugin registry and auto-discovery.
4. **Phase 4: UI Integration** - Created dynamic UI components based on available plugins and their capabilities.

### Framework-Agnostic Architecture

This roadmap outlined a comprehensive plan for evolving the current render function pattern into a framework-agnostic architecture. This would have allowed the app to support multiple frontends (Streamlit, Flask, React) without duplicating business logic.

**Latest Version**: [Framework-Agnostic Architecture Roadmap](archive/roadmap_FrameworkAgnosticArchitecture_17.md)

**Status**: Archived (Deprioritized) - The Framework-Agnostic Architecture roadmap was deprioritized in favor of the more focused Streamlit to Flask Migration roadmap. The roadmap was divided into five phases:

1. **Phase 1: Core Extraction** - Extract page logic from render functions into framework-independent core classes, define base page data models, and maintain backward compatibility with current Streamlit UI.
2. **Phase 2: Streamlit Adapter Layer** - Convert current render functions to thin Streamlit adapters, move all Streamlit-specific code to adapter layer, and ensure all pages work through new architecture.
3. **Phase 3: Flask API Development** - Create Flask application structure, implement REST API endpoints for each page, add authentication/session management, and create simple Jinja2 templates for testing.
4. **Phase 4: Enhanced UI Components** - Implement HTMX for dynamic updates, add Alpine.js for client-side interactivity, focus on file browser and connection management, and create rich preview capabilities.
5. **Phase 5: React Exploration** - Evaluate need for full SPA, prototype key components, and consider hybrid approach.

### Repository Reorganization

This roadmap outlined the plan for reorganizing the Science Data Kit repository structure, with a particular focus on improving the organization of roadmap files and documentation. The reorganization prepared the repository for the implementation of the Knowledge Graph Documentation System by creating a more logical and maintainable structure for project documentation.

**Latest Version**: [Repository Reorganization Roadmap](archive/roadmap_RepoReorg_04.md)

**Status**: Completed - The Repository Reorganization roadmap has been fully implemented:

1. **Phase 1: Documentation Reorganization** - Completed. New directory structure has been created, roadmap files have been moved to their new locations, redirect notices have been added to original files, and documentation integration has been completed.
2. **Phase 2: Repository Structure Improvements** - Completed. The tools directory has been created and development scripts have been moved to it. The config directory has been created and configuration files have been moved to it. The docker directory has been created and Docker-related files have been moved to it. Docker documentation has been updated and test organization has been improved.

### Previous Development Phases

The Science Data Kit has completed six major development phases, resulting in a comprehensive platform with extensive capabilities for scientific data analysis. All completed roadmaps have been archived and can be accessed through the [Complete Roadmap Index](archive/index_complete.md).

Any remaining tasks from these roadmaps have been added to the [Later Roadmap](active/roadmap_later.md) file for future consideration.

## Roadmap Management

The detailed processes for updating roadmaps and archiving completed roadmaps are documented in [Roadmap Memo](active/roadmap_memo.md).

## Conclusion

The Science Data Kit project has successfully achieved its goal of becoming a comprehensive tool for scientific data analysis and visualization. Through the systematic implementation of twelve major roadmaps across six development phases, the SDK has evolved into a robust platform with extensive capabilities.

### Roadmap Reorganization and Prioritization

The project has undergone a strategic reorganization to focus on fundamental frontend/backend integration work and user experience optimization. This reorganization includes:

1. **Active Roadmaps**: Focusing on core platform stability and user experience
   - The **Repository Reorganization** roadmap, which has made significant progress with most tasks now completed
   - The new **Design/UX Phase** roadmap, which focuses on frontend component validation, user experience optimization, backend validation through the user interface, and workshop preparation
   - The **Streamlit to Flask Migration** roadmap, which focuses on transitioning from Streamlit to Flask as the primary UI framework

2. **Future Roadmaps**: Advanced features temporarily deprioritized
   - The **Conversational Pipeline Builder** roadmap, which outlines a future vision for a natural language interface (planning phase only)
   - The **Knowledge Graph Documentation System** roadmap, which represents a fundamental shift toward "AI-native software architecture"
   - The **Strategic Enhancements** roadmap, which focuses on platform maturation, community adoption, and long-term sustainability

This reorganization ensures that the Science Data Kit establishes a solid foundation of frontend-backend integration and user experience optimization before implementing advanced features. By focusing on these fundamental aspects first, the project will create a more stable, user-friendly platform that can better support the advanced features planned for future development.

### Current Focus: Streamlit to Flask Migration and Design/UX Phase

The Streamlit to Flask Migration and Design/UX Phase represent critical steps in the evolution of the Science Data Kit, shifting focus from backend architecture to user-facing components and interactions. These phases will:

1. Systematically validate all frontend components and their integration with backend systems
2. Optimize user experience through interface consistency, navigation flow, and error handling improvements
3. Validate backend functionality through comprehensive frontend testing
4. Prepare for workshops by refining documentation, training materials, and demo scenarios
5. Complete the transition from Streamlit to Flask as the primary UI framework

By completing these phases, the Science Data Kit will provide a cohesive, intuitive, and reliable experience for scientific users, establishing a solid foundation for future enhancements.

Together, these roadmaps will guide the transformation of the Science Data Kit into a user-friendly, well-tested scientific software platform with a well-organized repository structure and a clear path to advanced capabilities for long-term growth and sustainability.

Note: This file has been updated in place (rather than creating a new version with _v2 suffix) to keep file counts to a minimum.
