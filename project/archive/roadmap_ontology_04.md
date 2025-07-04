# Science Data Kit (SDK) Ontology Integration Roadmap - Version 04

## Overview

This roadmap outlines the plan for refactoring the Science Data Kit to focus on ontology integration with Neo4j as the core technology. The goal is to remove isatools dependencies and implement a more streamlined approach to ontology management using Neo4j's neosemantics (n10s) plugin.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 04 | 2025-05-05 | Completed test files for ontology integration |
| 03 | 2025-05-04 | Updated documentation for ontology integration |
| 02 | 2025-05-03 | Implemented Neo4j's neosemantics (n10s) plugin integration |
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

### 2. Implement Neo4j Ontology Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Research Neo4j's neosemantics (n10s) plugin | High | Completed | Researched capabilities and integration points |
| Implement OWL/RDF file import | High | Completed | Added support for OWL, Turtle (.ttl), RDF/XML, JSON-LD formats in importer.py |
| Add URL support for ontology import | Medium | Completed | Implemented URL-based ontology import in importer.py |
| Implement ontology class to Neo4j label mapping | Medium | Completed | Added mapping of OWL classes to Neo4j nodes |
| Preserve class hierarchies as relationships | Medium | Completed | Implemented subclass relationships |
| Add conflict detection for multiple ontologies | Medium | Completed | Added error handling for ontology conflicts |

### 3. Add Python Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Add rdflib as a dependency | High | Completed | Added to requirements.txt |
| Create helper functions for ontology queries | Medium | Completed | Implemented in science_data_kit/core/ontology/queries.py |
| Build ontology browser/search capability | Medium | Completed | Implemented in science_data_kit/core/ontology/browser.py |
| Create example notebooks for ontology integration | Low | Completed | Added tutorial in tutorials/ontology_integration_tutorial.py |

### 4. Update Documentation and Tests

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update README.md | Medium | Completed | Removed isatools references, updated ontology section |
| Create ontology integration documentation | Medium | Completed | Updated docs/ONTOLOGY_FEATURES.md with comprehensive documentation |
| Create tests for ontology integration | Medium | Completed | Added tests for OntologyImporter, OntologyBrowser, and ontology queries |

## Current Status

The Science Data Kit has been refactored to remove isatools dependencies and implement a more streamlined approach to ontology management. The following components have been implemented:

1. Core ontology models in `science_data_kit/core/ontology/models.py`
   - OntologySource and OntologyAnnotation classes

2. Ontology importer in `science_data_kit/core/ontology/importer.py`
   - OntologyImporter class with comprehensive support for importing ontologies using Neo4j's neosemantics (n10s) plugin
   - Support for various RDF formats (OWL, Turtle, RDF/XML, JSON-LD)
   - Fallback implementation using rdflib when the neosemantics plugin is not available
   - Robust error handling and logging

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

8. Documentation in `docs/ONTOLOGY_FEATURES.md`
   - Comprehensive documentation for the ontology integration features
   - Examples for using the OntologyImporter and OntologyBrowser classes
   - Best practices for working with ontologies in Neo4j

9. Tests in `tests/unit/core/ontology/`
   - Comprehensive tests for the OntologyImporter class
   - Comprehensive tests for the OntologyBrowser class
   - Comprehensive tests for the ontology queries module

The current implementation has the following limitations:
- Integration with the Neo4j browser for visualizing ontologies could be improved
- API documentation needs to be updated

## Next Steps

### 1. Update Documentation and Tests

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update API documentation | Medium | To Do | Update docs/api_docs/ |
| Update existing tests | Medium | To Do | Remove isatools dependencies from tests |

### 2. Enhance Ontology Visualization

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Improve ontology browser visualization | Medium | To Do | Enhance the visualization capabilities of the OntologyBrowser class |
| Add support for exporting ontology visualizations | Low | To Do | Add methods to export visualizations to HTML, SVG, or PNG |
| Create interactive ontology explorer | Low | To Do | Build a Streamlit-based interactive ontology explorer |

## Implementation Plan

### Phase 1: Documentation (Weeks 1-2)

1. Update API Documentation
   - Update docs/api_docs/ with comprehensive API documentation
   - Add examples for using the ontology integration features

2. Update Existing Tests
   - Update existing tests to remove isatools dependencies
   - Ensure all tests pass with the new ontology module

### Phase 2: Visualization Enhancements (Weeks 3-4)

1. Improve Ontology Browser
   - Enhance visualization capabilities
   - Add support for exporting visualizations

2. Create Interactive Explorer
   - Build a Streamlit-based interactive ontology explorer
   - Integrate with the Neo4j browser

## Conclusion

Significant progress has been made in refactoring the Science Data Kit to focus on ontology integration with Neo4j as the core technology. The isatools dependencies have been removed, and a new ontology module has been implemented with comprehensive support for importing ontologies using Neo4j's neosemantics (n10s) plugin.

The implementation now supports various RDF formats (OWL, Turtle, RDF/XML, JSON-LD) and provides robust error handling and logging. A fallback implementation using rdflib is available when the neosemantics plugin is not installed.

The documentation has been updated to reflect the new ontology integration features, with comprehensive examples and best practices for working with ontologies in Neo4j.

Comprehensive tests have been created for the ontology integration features, including tests for the OntologyImporter class, OntologyBrowser class, and ontology queries module.

The next steps involve updating the API documentation, removing isatools dependencies from existing tests, and enhancing the ontology visualization capabilities to provide a better user experience.

The end result will be a simplified codebase that focuses on Python 3.12+ and Neo4j, with enhanced ontology capabilities that make ontology integration feel natural for scientists who just want their domain knowledge properly represented in their data analysis workflows.