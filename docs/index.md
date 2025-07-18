# Science Data Kit Documentation Index

This index provides a comprehensive overview of all documentation for the Science Data Kit project.

## Science Data Kit Overview

The Science Data Kit (SDK) is an open-source data harmonization platform designed to connect, integrate, and analyze research data across multiple sources and modalities. Built specifically for research facilities facing complex data integration challenges, SDK uses knowledge graph technology and AI-powered tools to bridge the gap between highly standardized data (like genomics) and complex, heterogeneous data (like preclinical imaging).

### Core Value Proposition

SDK provides a unified layer that:
1. **Connects** to existing data sources without disruption
2. **Harmonizes** data using AI and knowledge graphs
3. **Enables** cross-modal queries and discovery
4. **Empowers** researchers with AI-assisted tools

### Architecture

SDK follows a layered architecture:
- **User Interface Layer**: Web GUI, API, Command Line, Jupyter
- **AI Assistant Layer**: Plugin Generation, Data Harmonization, GraphRAG
- **Knowledge Graph Layer**: Neo4j, Semantic Relationships, Ontologies
- **Connection Layer**: Plugins for Each Data Source/Instrument
- **Data Sources**: File Systems, Cloud Storage, Databases, Instruments

## Development Roadmaps and Planning

- [Roadmaps Index](roadmaps/index.md) - Master index for all development roadmaps
  - [Active Roadmaps](roadmaps/active/) - Current development priorities
  - [Future Roadmaps](roadmaps/future/) - Planned future development
  - [Archived Roadmaps](roadmaps/archive/) - Completed roadmaps
- [Executive Roadmap](roadmaps/executive.md) - High-level strategic roadmap

## User Documentation

- [User Guide](guides/user_guide.md) - Comprehensive guide for users
- [Tutorials](tutorials/) - Step-by-step tutorials for common tasks
- [Troubleshooting](troubleshooting/) - Solutions for common issues
- [FAQ](common_errors_faq.md) - Frequently asked questions

## Developer Documentation

- [Architecture](architecture/) - System architecture documentation
- [API Documentation](api/) - API reference
- [Framework Adapters](framework_adapters.md) - Documentation on framework adapter pattern
- [Design Decisions](design_decisions.md) - Explanation of key design decisions
- [Testing Strategy](TESTING_STRATEGY.md) - Overview of testing approach
- [Code Standards](code_standards.md) - Coding standards and guidelines
- [Module Standards](module_standards.md) - Module organization standards

## Feature-Specific Documentation

- [Ontology Features](ONTOLOGY_FEATURES.md) - Documentation for ontology features
- [SQL Database Integration](sql_database_integration.md) - SQL database integration guide
- [RESTful API Integration](restful_api_integration.md) - RESTful API integration guide

## Project Management

- [Deprecation Plan](deprecation_plan.md) - Plan for deprecating features
- [Research Use Cases](research_use_cases.md) - Research use cases for the Science Data Kit
- [Next Steps](next_steps.md) - Next steps for the project

## Workshop Materials

- [Workshop](workshop/) - Materials for workshops and training sessions

## Implementation Strategy

The project is currently in Phase 2 (Enhancement), with completed work on:
- Core infrastructure with Neo4j
- Basic file system connectivity
- Cloud storage integration
- ISA framework support

Current focus areas include:
- Plugin architecture standardization
- AI-powered plugin development
- GraphRAG implementation
- Improved user interface

## Technical Specifications

- **Backend**: Python 3.9+
- **Graph Database**: Neo4j 4.4+
- **Web Framework**: Flask (migrating from Streamlit)
- **Frontend**: Streamlit (current), React (planned)
- **AI/ML**: OpenAI API, local LLM support via Ollama
- **Container**: Docker, Kubernetes-ready