# Science Data Kit (SDK) Ontology Integration Roadmap - Version 01

## Overview

This roadmap outlines the plan for refactoring the Science Data Kit to focus on ontology integration with Neo4j as the core technology. The goal is to remove isatools dependencies and implement a more streamlined approach to ontology management using Neo4j's neosemantics (n10s) plugin.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 01 | 2025-05-02 | Updated status of completed tasks and outlined next steps |
| 00 | 2025-05-01 | Initial roadmap for ontology integration |

## Completed Tasks

### 1. Remove isatools Dependencies

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Remove isatools from setup.py extras_require | High | Completed | Removed 'isatools' and 'isatools_full' sections from setup.py |
| Update pyproject.toml to remove Python 3.9 compatibility | High | Completed | Updated target-version to focus on Python 3.12+ |
| Remove isatools-related installation scripts | High | Completed | Removed install_isatools.py, install_isatools.sh, install_isatools_py312.py |
| Remove isatools imports from codebase | High | Completed | Removed isatools imports from db_manager.py and graph_utils.py |
| Refactor isa_compatibility.py | High | Completed | Updated to use the new ontology module and added deprecation notices |
| Refactor isa_utils.py | High | Completed | Updated to use the new ontology module and added deprecation notices |
| Update db_manager.py and graph_utils.py | High | Completed | Updated to use the new ontology module |

### 2. Add Python Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Add rdflib as a dependency | High | Completed | Added to requirements.txt |
| Create helper functions for ontology queries | Medium | Completed | Implemented in science_data_kit/core/ontology/queries.py |
| Build ontology browser/search capability | Medium | Completed | Implemented in science_data_kit/core/ontology/browser.py |
| Create example notebooks for ontology integration | Low | Completed | Added tutorial in tutorials/ontology_integration_tutorial.py |

## Current Status

The Science Data Kit has been refactored to remove isatools dependencies and implement a more streamlined approach to ontology management. The following components have been implemented:

1. Core ontology models in `science_data_kit/core/ontology/models.py`
   - OntologySource and OntologyAnnotation classes

2. Ontology importer in `science_data_kit/core/ontology/importer.py`
   - OntologyImporter class with placeholder methods for importing ontologies from files and URLs

3. Ontology queries in `science_data_kit/core/ontology/queries.py`
   - Helper functions for common ontology queries in Neo4j

4. Ontology browser in `science_data_kit/core/ontology/browser.py`
   - OntologyBrowser class for visualizing ontologies

5. Compatibility layer in `science_data_kit/core/utils/isa_compatibility.py` and `science_data_kit/core/utils/isa_utils.py`
   - Updated to use the new ontology module and added deprecation notices

6. Neo4j integration in `science_data_kit/core/db/db_manager.py` and `science_data_kit/core/db/graph_utils.py`
   - Updated to use the new ontology module

7. Example tutorial in `tutorials/ontology_integration_tutorial.py`
   - Demonstrates how to use the new ontology integration features

The current implementation has the following limitations:
- The OntologyImporter class has placeholder methods for importing ontologies from files and URLs
- The neosemantics (n10s) plugin integration is not yet implemented
- Comprehensive testing and documentation are still needed

## Next Steps

### 1. Implement Neo4j Ontology Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Research Neo4j's neosemantics (n10s) plugin | High | To Do | Understand capabilities and integration points |
| Implement OWL/RDF file import | High | To Do | Support OWL, Turtle (.ttl), RDF/XML, JSON-LD formats |
| Add URL support for ontology import | Medium | To Do | Support importing from BioPortal and other repositories |
| Implement ontology class to Neo4j label mapping | Medium | To Do | Map OWL classes to Neo4j node labels |
| Preserve class hierarchies as relationships | Medium | To Do | Implement subclass relationships |
| Add conflict detection for multiple ontologies | Medium | To Do | Detect and handle conflicts when importing multiple ontologies |

### 2. Update Documentation and Tests

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update README.md | Medium | To Do | Remove isatools references, add ontology integration information |
| Create ontology integration documentation | Medium | To Do | Add to docs/ directory |
| Update API documentation | Medium | To Do | Update docs/api_docs/ |
| Create tests for ontology integration | Medium | To Do | Add to tests/ directory |
| Update existing tests | Medium | To Do | Remove isatools dependencies from tests |

## Implementation Plan

### Phase 1: Neo4j Ontology Integration (Weeks 1-2)

1. Research and Planning
   - Research Neo4j's neosemantics (n10s) plugin
   - Plan the implementation of OWL/RDF file import
   - Identify integration points with existing codebase

2. Implement OntologyImporter
   - Implement OWL/RDF file import functionality
   - Add URL support for ontology import
   - Implement ontology class to Neo4j label mapping
   - Preserve class hierarchies as relationships
   - Add conflict detection for multiple ontologies

### Phase 2: Documentation and Testing (Weeks 3-4)

1. Update Documentation
   - Update README.md
   - Create ontology integration documentation
   - Update API documentation

2. Create and Update Tests
   - Create tests for ontology integration
   - Update existing tests to remove isatools dependencies

## Conclusion

Significant progress has been made in refactoring the Science Data Kit to focus on ontology integration with Neo4j as the core technology. The isatools dependencies have been removed, and a new ontology module has been implemented with core models, importer, queries, and browser capabilities.

The next steps involve implementing the Neo4j neosemantics (n10s) plugin integration to enable importing ontologies from various formats and sources, as well as updating documentation and tests to ensure the new functionality is well-documented and tested.

The end result will be a simplified codebase that focuses on Python 3.12+ and Neo4j, with enhanced ontology capabilities that make ontology integration feel natural for scientists who just want their domain knowledge properly represented in their data analysis workflows.