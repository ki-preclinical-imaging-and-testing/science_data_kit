# Science Data Kit (SDK) Roadmap Index

## Overview
This document serves as a master index for all roadmaps in the Science Data Kit project. It provides links to all active roadmaps and a high-level overview of the project's direction.

## Active Roadmaps

### Repository Reorganization

This roadmap outlines the plan for reorganizing the Science Data Kit repository structure, with a particular focus on improving the organization of roadmap files and documentation. The reorganization will prepare the repository for the implementation of the Knowledge Graph Documentation System by creating a more logical and maintainable structure for project documentation.

**Latest Version**: [Repository Reorganization Roadmap](active/roadmap_RepoReorg_02.md)

**Status**: Implementation in Progress - The Repository Reorganization roadmap has made significant progress, with all high-priority tasks now completed:

1. **Phase 1: Documentation Reorganization** - Completed. New directory structure has been created, roadmap files have been moved to their new locations, redirect notices have been added to original files, and documentation integration has been completed.
2. **Phase 2: Repository Structure Improvements** - In Progress. The tools directory has been created and development scripts have been moved to it. Remaining tasks include creating a config directory, organizing Docker files, and improving test organization.

### Knowledge Graph Documentation System

This roadmap outlines the plan for implementing a Knowledge Graph Documentation System that transforms the Science Data Kit into an AI-navigable scientific software platform. The system enables documentation to live naturally in the codebase while providing structured markup and linking for automatic knowledge graph generation. AI agents can query this graph to understand codebase structure and patterns, with the graph automatically rebuilding from source documentation when files change.

**Latest Version**: [Knowledge Graph Documentation System Roadmap](active/roadmap_kg_00.md)

**Status**: Planning - The Knowledge Graph Documentation System roadmap has been defined and is divided into six phases:

1. **Phase 1: Foundation** - Establishing the core infrastructure for the knowledge graph system without disrupting existing workflows. See [Phase 1 Roadmap](active/roadmap_kgPhase1_00.md) for details.
2. **Phase 2: Core Integration** - Integrating the knowledge graph system with existing documentation systems and tools. See [Phase 2 Roadmap](active/roadmap_kgPhase2_00.md) for details.
3. **Phase 3: AI Navigation** - Enabling AI agents to navigate and understand the codebase through the knowledge graph. See [Phase 3 Roadmap](active/roadmap_kgPhase3_00.md) for details.
4. **Phase 4: User Interfaces** - Creating tools for human interaction with the knowledge graph. See [Phase 4 Roadmap](active/roadmap_kgPhase4_00.md) for details.
5. **Phase 5: Advanced Features** - Adding advanced capabilities to the knowledge graph system. See [Phase 5 Roadmap](active/roadmap_kgPhase5_00.md) for details.
6. **Phase 6: Ecosystem** - Platform maturation and broader adoption. See [Phase 6 Roadmap](active/roadmap_kgPhase6_00.md) for details.

**Supporting Documentation**:
- [Knowledge Graph Vision](active/knowledge_graph_vision.md) - Detailed vision document explaining the "AI-native software architecture" concept
- [Knowledge Graph Technical Specification](active/knowledge_graph_technical_spec.md) - Technical specification covering documentation markup standards, schema design, and integration requirements
- [Knowledge Graph Examples](active/knowledge_graph_examples.md) - Concrete examples showing before/after documentation examples, sample AI queries, and tagging examples

### Strategic Enhancements

This roadmap outlines a comprehensive plan for strategic enhancements to the Science Data Kit platform, focusing on key areas for platform maturation, community adoption, and long-term sustainability. These enhancements build upon the existing Knowledge Graph and Repository Reorganization roadmaps while addressing higher-level platform capabilities that will accelerate adoption in the scientific community.

**Latest Version**: [Strategic Enhancements Roadmap](active/roadmap_StrategicEnhancements_00.md)

**Status**: Planning - The Strategic Enhancements roadmap has been defined and is divided into three phases:

1. **Phase 1: Foundation Enhancements** - Establishing core capabilities for documentation automation, workshop feedback integration, and domain branch templates.
2. **Phase 2: Community and Performance** - Implementing performance monitoring, AI assistant training, and community contribution frameworks.
3. **Phase 3: Platform Expansion** - Completing domain branch templates and adding cross-platform deployment and scientific workflow integration.

### Conversational Pipeline Builder

This roadmap outlines a plan for implementing a conversational interface for scientific pipeline creation that integrates with the existing SciDK platform. Users would interact through natural language to build, modify, and visualize scientific data analysis pipelines, with the system leveraging the knowledge graph and component architecture to translate conversations into working pipelines.

**Latest Version**: [Conversational Pipeline Builder Roadmap](active/roadmap_CPB_00.md)

**Status**: Planning - The Conversational Pipeline Builder roadmap has been defined but not started yet. It is being added to the system for future consideration. The roadmap is divided into four phases:

1. **Phase 1: Foundation** - Basic conversational interface and component integration.
2. **Phase 2: Visual Representation** - Visual pipeline editing and cross-UI integration.
3. **Phase 3: Advanced Natural Language** - Sophisticated domain understanding and complex pipeline support.
4. **Phase 4: Ecosystem Integration** - Full integration with SciDK ecosystem and external tools.

## Testing and Quality Status

### Repository Reorganization
**Implementation Status**: In Progress - Phase 1 completed, Phase 2 started
**Testing Status**: Phase 1 ready for final validation, Phase 2 in progress
**Next Testing Steps**: Use prompt #21 from prompts.md to validate Phase 1 implementation and tools directory
**Quality Gates**: Phase 1 final validation, tools directory validation before continuing Phase 2

### Knowledge Graph Documentation System  
**Implementation Status**: Planning - Foundation phase components ready for validation
**Testing Status**: Ready for validation preparation
**Recommended Testing**: Use prompts #21, #19, #24 for foundation validation
**Workshop Readiness**: Use prompt #22 for user testing preparation
**Quality Gates**: Phase 1 validation before Phase 2, Workshop preparation before user testing

### Strategic Enhancements
**Implementation Status**: Planning - Initial definition phase
**Testing Status**: Not yet applicable - planning phase
**Next Testing Steps**: Use prompt #21 from prompts.md once implementation begins
**Recommended Testing**: Use prompts #19, #22, #24 for high-priority enhancements
**Quality Gates**: Foundation Enhancements validation before Community and Performance phase

### Conversational Pipeline Builder
**Implementation Status**: Planning - Not started yet
**Testing Status**: Not yet applicable - planning phase
**Next Testing Steps**: Not applicable at this stage
**Recommended Testing**: Will be determined when implementation begins
**Quality Gates**: Knowledge Graph Documentation System Phase 1-2 completion before starting

### Testing Workflow Integration
Use the testing prompts in `docs/roadmaps/prompts.md` (#17-24) at these natural checkpoints:
- **After completing 3-5 implementation tasks** in any roadmap
- **Before transitioning between roadmap phases**
- **When preparing for workshops or user feedback**
- **When implementing core architectural components**

For guidance on selecting appropriate testing prompts, start with prompt #21 (Pre-Review Code Analysis) to assess current state and get recommendations for additional validation.

## Archived Roadmaps

The Science Data Kit has completed six major development phases, resulting in a comprehensive platform with extensive capabilities for scientific data analysis. All completed roadmaps have been archived and can be accessed through the [Complete Roadmap Index](archive/index_complete.md).

Any remaining tasks from these roadmaps have been added to the [Later Roadmap](active/roadmap_later.md) file for future consideration.

## Roadmap Management

The detailed processes for updating roadmaps and archiving completed roadmaps are documented in [Roadmap Memo](active/roadmap_memo.md).

## Conclusion

The Science Data Kit project has successfully achieved its goal of becoming a comprehensive tool for scientific data analysis and visualization. Through the systematic implementation of twelve major roadmaps across six development phases, the SDK has evolved into a robust platform with extensive capabilities.

The project is now entering a new phase with four active roadmaps:

1. The **Repository Reorganization** roadmap, which has made significant progress with all high-priority tasks now completed. Phase 1 (Documentation Reorganization) is complete, with the new directory structure in place, roadmap files moved to their appropriate locations, and documentation integration completed. Phase 2 (Repository Structure Improvements) is now in progress, with the tools directory created and development scripts moved. This reorganization is preparing the repository for the Knowledge Graph Documentation System.

2. The **Knowledge Graph Documentation System** roadmap, which represents a fundamental shift toward "AI-native software architecture" where the codebase actively communicates its structure and patterns to both human developers and AI agents.

3. The **Strategic Enhancements** roadmap, which focuses on platform maturation, community adoption, and long-term sustainability through documentation automation, workshop feedback integration, domain customization, and other strategic capabilities.

4. The **Conversational Pipeline Builder** roadmap, which outlines a future vision for a natural language interface that enables researchers to create sophisticated data analysis pipelines through conversation. This roadmap has been defined but not started yet, and is planned to begin after the completion of Knowledge Graph Documentation System Phase 1-2.

Together, these roadmaps will guide the transformation of the Science Data Kit into an AI-navigable, community-adoptable scientific software platform with a well-organized repository structure and strategic capabilities for long-term growth and sustainability.
