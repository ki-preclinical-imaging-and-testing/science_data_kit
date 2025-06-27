# Science Data Kit API Documentation

This directory contains API documentation for the Science Data Kit modules. The documentation is organized by module and provides information about the classes, methods, and functions available in each module.

## Core Modules

### Database Modules

- [db_manager.py](core/db/db_manager.md) - Database manager for Neo4j connections
- [graph_utils.py](core/db/graph_utils.md) - Utilities for working with Neo4j graphs
- [api_manager_base.py](core/db/api_manager_base.md) - Base classes for API managers
- [msgraph_manager.py](core/db/msgraph_manager.md) - Microsoft Graph API manager
- [msgraph_adapter.py](core/db/msgraph_adapter.md) - Microsoft Graph API adapter

### Model Modules

- [file_models.py](core/models/file_models.md) - Models for file and folder objects
- [app_models.py](core/models/app_models.md) - Models for application objects
- [msgraph_schemas.py](core/models/msgraph_schemas.md) - Microsoft Graph API entity schemas

### Utility Modules

- [isa_compatibility.py](core/utils/isa_compatibility.md) - Compatibility layer for isatools
- [isa_utils.py](core/utils/isa_utils.md) - Utilities for working with ISA data models
- [file_utils.py](core/utils/file_utils.md) - Utilities for file operations
- [visualization_utils.py](core/utils/visualization_utils.md) - Utilities for data visualization
- [msgraph_utils.py](core/utils/msgraph_utils.md) - Utilities for Microsoft Graph API

## UI Modules

### Base Modules

- [config.py](ui/config.py.md) - Configuration settings for UI components
- [state.py](ui/state.py.md) - State management utilities

### Adapter Modules

- [page_adapter.py](ui/adapters/page_adapter.md) - Adapter for dynamic page loading
- [component_adapter.py](ui/adapters/component_adapter.md) - Adapter for UI components

### Component Modules

- [sidebar.py](ui/components/sidebar.md) - Sidebar component
- [schema_widget.py](ui/components/schema_widget.md) - Schema visualization and editing widget

### Page Modules

- [base_page.py](ui/pages/base_page.md) - Base class for pages
- [connect.py](ui/pages/connect.md) - Connect page
- [survey.py](ui/pages/survey.md) - Survey page
- [map.py](ui/pages/map.md) - Map page
- [explore.py](ui/pages/explore.md) - Explore page

## How to Use This Documentation

Each documentation file provides:

1. An overview of the module
2. A list of classes and functions
3. Detailed documentation for each class and function, including:
   - Parameters
   - Return values
   - Examples
   - Notes and warnings

## Contributing to API Documentation

When contributing to API documentation, please follow these guidelines:

1. Use Markdown format for documentation files
2. Include examples for complex functions
3. Document all parameters and return values
4. Include type hints in code examples
5. Add notes and warnings where appropriate
