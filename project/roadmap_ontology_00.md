# Science Data Kit (SDK) Ontology Integration Roadmap - Version 00

## Overview

This roadmap outlines the plan for refactoring the Science Data Kit to focus on ontology integration with Neo4j as the core technology. The goal is to remove isatools dependencies and implement a more streamlined approach to ontology management using Neo4j's neosemantics (n10s) plugin.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 00 | 2025-05-01 | Initial roadmap for ontology integration |

## Completed Tasks

No tasks have been completed yet. This is the initial roadmap.

## Current Status

The Science Data Kit currently uses isatools for ontology management, with a compatibility layer for environments where isatools cannot be installed (e.g., Python 3.12+). The codebase includes:

1. A compatibility layer in `science_data_kit/core/utils/isa_compatibility.py`
2. Utility functions in `science_data_kit/core/utils/isa_utils.py`
3. Neo4j integration in `science_data_kit/core/db/db_manager.py` and `science_data_kit/core/db/graph_utils.py`
4. isatools-specific installation scripts and dependencies

The current implementation has limitations:
- Dependency on isatools, which is not compatible with Python 3.12+
- Complex compatibility layer to handle environments without isatools
- Limited ontology integration capabilities

## Next Steps

### 1. Remove isatools Dependencies

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Remove isatools from setup.py extras_require | High | To Do | Remove 'isatools' and 'isatools_full' sections |
| Update pyproject.toml to remove Python 3.9 compatibility | High | To Do | Focus on Python 3.12+ |
| Remove isatools-related installation scripts | High | To Do | Remove install_isatools.py, install_isatools.sh, install_isatools_py312.py |
| Remove isatools imports from codebase | High | To Do | Search for and remove all isatools imports |
| Refactor isa_compatibility.py | High | To Do | Keep OntologySource and OntologyAnnotation classes but remove isatools dependencies |
| Refactor isa_utils.py | High | To Do | Remove isatools-specific functionality |
| Update db_manager.py and graph_utils.py | High | To Do | Remove isatools dependencies |

### 2. Implement Neo4j Ontology Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Research Neo4j's neosemantics (n10s) plugin | High | To Do | Understand capabilities and integration points |
| Create OntologyImporter class | High | To Do | Implement in science_data_kit/core/ontology/importer.py |
| Implement OWL/RDF file import | High | To Do | Support OWL, Turtle (.ttl), RDF/XML, JSON-LD formats |
| Add URL support for ontology import | Medium | To Do | Support importing from BioPortal and other repositories |
| Implement ontology class to Neo4j label mapping | Medium | To Do | Map OWL classes to Neo4j node labels |
| Preserve class hierarchies as relationships | Medium | To Do | Implement subclass relationships |
| Add conflict detection for multiple ontologies | Medium | To Do | Detect and handle conflicts when importing multiple ontologies |

### 3. Add Python Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Add rdflib as a dependency | High | To Do | Add to requirements.txt and setup.py |
| Create helper functions for ontology queries | Medium | To Do | Implement in science_data_kit/core/ontology/queries.py |
| Build ontology browser/search capability | Medium | To Do | Implement in science_data_kit/core/ontology/browser.py |
| Create example notebooks for ontology integration | Low | To Do | Add to tutorials/ directory |

### 4. Update Documentation and Tests

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update README.md | Medium | To Do | Remove isatools references, add ontology integration information |
| Create ontology integration documentation | Medium | To Do | Add to docs/ directory |
| Update API documentation | Medium | To Do | Update docs/api_docs/ |
| Create tests for ontology integration | Medium | To Do | Add to tests/ directory |
| Update existing tests | Medium | To Do | Remove isatools dependencies from tests |

## Implementation Plan

### Phase 1: Cleanup and Preparation (Weeks 1-2)

1. Remove isatools Dependencies
   - Remove isatools from setup.py extras_require
   - Update pyproject.toml to remove Python 3.9 compatibility
   - Remove isatools-related installation scripts
   - Remove isatools imports from codebase
   - Refactor isa_compatibility.py to keep OntologySource and OntologyAnnotation classes
   - Refactor isa_utils.py to remove isatools-specific functionality
   - Update db_manager.py and graph_utils.py to remove isatools dependencies

2. Research and Planning
   - Research Neo4j's neosemantics (n10s) plugin
   - Plan the OntologyImporter class architecture
   - Identify integration points with existing codebase

### Phase 2: Core Implementation (Weeks 3-4)

1. Implement OntologyImporter
   - Create OntologyImporter class in science_data_kit/core/ontology/importer.py
   - Implement OWL/RDF file import functionality
   - Add URL support for ontology import
   - Implement ontology class to Neo4j label mapping
   - Preserve class hierarchies as relationships
   - Add conflict detection for multiple ontologies

2. Add Python Integration
   - Add rdflib as a dependency
   - Create helper functions for ontology queries
   - Build ontology browser/search capability

### Phase 3: Documentation and Testing (Weeks 5-6)

1. Update Documentation
   - Update README.md
   - Create ontology integration documentation
   - Update API documentation

2. Create and Update Tests
   - Create tests for ontology integration
   - Update existing tests to remove isatools dependencies

3. Create Examples
   - Create example notebooks for ontology integration
   - Add to tutorials/ directory

## Conclusion

This roadmap outlines the plan for refactoring the Science Data Kit to focus on ontology integration with Neo4j as the core technology. By removing isatools dependencies and implementing a more streamlined approach to ontology management using Neo4j's neosemantics plugin, we will create a cleaner, more maintainable solution that makes ontology integration feel natural for scientists.

The implementation will be done in three phases: cleanup and preparation, core implementation, and documentation and testing. The end result will be a simplified codebase that focuses on Python 3.12+ and Neo4j, with enhanced ontology capabilities.