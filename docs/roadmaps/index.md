# Science Data Kit (SDK) Roadmap Index

## Overview
This document serves as a master index for all roadmaps in the Science Data Kit project. It provides links to all active roadmaps and a high-level overview of the project's direction.

## Active Roadmaps

### Design/UX Phase

This roadmap outlines a comprehensive plan for the Design/UX phase of the Science Data Kit, focusing on frontend component validation, user experience optimization, backend validation through the user interface, and workshop preparation integration. This phase is critical for ensuring that the backend architecture established in previous phases is effectively integrated with frontend components and that the overall user experience is thoroughly tested, refined, and validated.

**Latest Version**: [Design/UX Phase Roadmap](active/roadmap_DesignUX_04.md)

**Status**: In Progress - The Design/UX phase roadmap has made significant progress in Phase 1: Core Component Validation with eleven high-priority tasks completed:

1. Component Inventory
2. Testing Checklists
3. AI-Generated Test Scenarios
4. Testing Workflow
5. Streamlit Page Tests
6. Data Visualization Tests
7. Input Form Tests
8. Database Connectivity Tests
9. Test Suite Execution
10. Critical Visualization Component Fixes
11. Database Connectivity Fixes

The roadmap is divided into four phases:

1. **Phase 1: Core Component Validation** - Systematically testing all frontend components and their integration with backend systems.
2. **Phase 2: Integration Testing** - Validating user workflows, cross-component integration, and performance.
3. **Phase 3: User Experience Optimization** - Improving interface consistency, navigation flow, error handling, accessibility, and mobile responsiveness.
4. **Phase 4: Workshop Readiness** - Preparing documentation, training materials, feedback collection mechanisms, and demo scenarios.


## Future Roadmaps

The following roadmaps represent important strategic directions for the Science Data Kit but have been temporarily deprioritized to focus on fundamental frontend/backend integration work and user experience optimization. These roadmaps have been moved to the `future/` directory and will be revisited after the completion of the Design/UX phase and Repository Reorganization roadmap.

For more information about future roadmaps, see the [Future Roadmaps README](future/README.md).

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

### Future Roadmaps

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

2. **Future Roadmaps**: Advanced features temporarily deprioritized
   - The **Conversational Pipeline Builder** roadmap, which outlines a future vision for a natural language interface (planning phase only)
   - The **Knowledge Graph Documentation System** roadmap, which represents a fundamental shift toward "AI-native software architecture"
   - The **Strategic Enhancements** roadmap, which focuses on platform maturation, community adoption, and long-term sustainability

This reorganization ensures that the Science Data Kit establishes a solid foundation of frontend-backend integration and user experience optimization before implementing advanced features. By focusing on these fundamental aspects first, the project will create a more stable, user-friendly platform that can better support the advanced features planned for future development.

### Current Focus: Design/UX Phase

The Design/UX phase represents a critical step in the evolution of the Science Data Kit, shifting focus from backend architecture to user-facing components and interactions. This phase will:

1. Systematically validate all frontend components and their integration with backend systems
2. Optimize user experience through interface consistency, navigation flow, and error handling improvements
3. Validate backend functionality through comprehensive frontend testing
4. Prepare for workshops by refining documentation, training materials, and demo scenarios

By completing this phase, the Science Data Kit will provide a cohesive, intuitive, and reliable experience for scientific users, establishing a solid foundation for future enhancements.

Together, these roadmaps will guide the transformation of the Science Data Kit into a user-friendly, well-tested scientific software platform with a well-organized repository structure and a clear path to advanced capabilities for long-term growth and sustainability.
