# Science Data Kit API Documentation

This directory contains API documentation for the Science Data Kit project.

## Overview

The Science Data Kit provides several APIs for interacting with the system programmatically:

1. **Core API** - The fundamental API for interacting with the Science Data Kit core functionality
2. **Plugin API** - The API for developing plugins to extend the Science Data Kit
3. **Web API** - The RESTful API for interacting with the Science Data Kit via HTTP

## Directory Structure

- **[core/](core/)** - Documentation for the Core API
  - **[database/](core/database/)** - Database interaction APIs
  - **[plugins/](core/plugins/)** - Plugin development APIs
  - **[models/](core/models/)** - Data model APIs

## Core API

The Core API provides direct access to the Science Data Kit's functionality through Python. This API is used by the UI components and can also be used directly by scripts and other applications.

Key components include:

- **Database Utilities** - For connecting to and querying Neo4j and other databases
- **File System Utilities** - For scanning and analyzing files
- **Data Models** - For representing entities and relationships
- **Visualization Utilities** - For creating interactive visualizations
- **Ontology Module** - For working with ontologies and semantic data models

## Plugin API

The Plugin API allows developers to extend the Science Data Kit with new functionality, such as:

- **Data Source Connectors** - For connecting to new types of data sources
- **Visualization Components** - For creating new types of visualizations
- **Analysis Tools** - For performing specialized data analysis
- **Integration Modules** - For integrating with other systems

## Web API

The Web API provides RESTful access to the Science Data Kit's functionality over HTTP. This API is used by the web UI and can also be used by other applications.

Key endpoints include:

- **/api/database** - For database operations
- **/api/files** - For file system operations
- **/api/ontology** - For ontology operations
- **/api/chat** - For GraphRAG interactions

## Usage Examples

Code examples for using the APIs can be found in the respective documentation sections.

## API Standards

All APIs follow these standards:

1. **Consistent Naming** - Clear and consistent naming conventions
2. **Error Handling** - Comprehensive error handling with informative messages
3. **Documentation** - Complete documentation with examples
4. **Versioning** - Semantic versioning for API changes
5. **Testing** - Comprehensive test coverage

## Contributing to API Documentation

When contributing to API documentation:

1. Follow the documentation standards outlined in [docs/code_standards.md](../code_standards.md)
2. Include code examples for common use cases
3. Document all parameters, return values, and exceptions
4. Update the documentation when the API changes