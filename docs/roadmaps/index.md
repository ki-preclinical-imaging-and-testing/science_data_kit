# Science Data Kit (SDK) Roadmap Index

## Overview
This document serves as a master index for all roadmaps in the Science Data Kit project. It provides links to all active roadmaps and a high-level overview of the project's direction.

## Active Roadmaps

### Repository Reorganization

This roadmap outlines the plan for reorganizing the Science Data Kit repository structure, with a particular focus on improving the organization of roadmap files and documentation. The reorganization will prepare the repository for the implementation of the Knowledge Graph Documentation System by creating a more logical and maintainable structure for project documentation.

**Latest Version**: [Repository Reorganization Roadmap](active/roadmap_RepoReorg_00.md)

**Status**: Planning - The Repository Reorganization roadmap has been defined and is divided into two phases:

1. **Phase 1: Documentation Reorganization** - Creating a new directory structure for roadmap files and documentation, moving files to appropriate locations, and updating references.
2. **Phase 2: Repository Structure Improvements** - Cleaning up the root directory, organizing Docker files, and improving test organization.

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

## Archived Roadmaps

The Science Data Kit has completed six major development phases, resulting in a comprehensive platform with extensive capabilities for scientific data analysis. All completed roadmaps have been archived and can be accessed through the [Complete Roadmap Index](archive/index_complete.md).

Any remaining tasks from these roadmaps have been added to the [Later Roadmap](active/roadmap_later.md) file for future consideration.

## Roadmap Management

The detailed processes for updating roadmaps and archiving completed roadmaps are documented in [Roadmap Memo](active/roadmap_memo.md).

## Conclusion

The Science Data Kit project has successfully achieved its goal of becoming a comprehensive tool for scientific data analysis and visualization. Through the systematic implementation of twelve major roadmaps across six development phases, the SDK has evolved into a robust platform with extensive capabilities.

The project is now entering a new phase with two active roadmaps:

1. The **Repository Reorganization** roadmap, which will improve the organization of roadmap files and documentation, preparing the repository for the Knowledge Graph Documentation System.

2. The **Knowledge Graph Documentation System** roadmap, which represents a fundamental shift toward "AI-native software architecture" where the codebase actively communicates its structure and patterns to both human developers and AI agents.

These roadmaps will guide the transformation of the Science Data Kit into an AI-navigable scientific software platform with a well-organized repository structure.