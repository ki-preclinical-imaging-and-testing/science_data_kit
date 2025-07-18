# Science Data Kit - Documentation

This directory contains documentation files for the Science Data Kit project, including development roadmaps, implementation guides, and reference materials.

## Documentation Structure

### Current Documentation

#### [roadmaps/](roadmaps/index.md)
The primary location for project roadmaps and development planning. This directory contains:
- **Active Roadmaps**: Current development priorities
- **Future Roadmaps**: Planned but not currently active roadmaps
- **Archived Roadmaps**: Completed roadmaps
- **Templates**: For creating new roadmap documents

The [roadmaps/index.md](roadmaps/index.md) file serves as the master index for all roadmaps and should be the starting point for understanding the project's direction.

#### Topic-Specific Documentation
- [architecture/](architecture/) - System architecture documentation
- [guides/](guides/) - User and developer guides
- [api/](api/) - API documentation
- [tutorials/](tutorials/) - Step-by-step tutorials
- [troubleshooting/](troubleshooting/) - Common issues and solutions
- [workshop/](workshop/) - Workshop materials

### Legacy Documentation (Deprecated)

The following files are maintained for historical reference but are no longer actively updated:

- [tasks.md](tasks.md) - Historical task list (superseded by roadmaps)
- [roadmap.md](roadmap.md) - Old roadmap structure (superseded by roadmaps/index.md)
- [high_priority_tasks.md](high_priority_tasks.md) - Old high-priority tasks (superseded by active roadmaps)

Please refer to the [roadmaps/index.md](roadmaps/index.md) for current development priorities and plans.

## Contributing to Documentation

When contributing to documentation:

1. **For roadmaps**: Follow the guidelines in [roadmaps/organization.md](roadmaps/organization.md)
2. **For other documentation**: Place files in the appropriate topic-specific directory
3. **For new documentation types**: Create a new directory with a README.md explaining its purpose

## Documentation Standards

All documentation should follow the standards outlined in [code_standards.md](code_standards.md) and [module_standards.md](module_standards.md).

## Science Data Kit Overview

The Science Data Kit (SDK) is an open-source data harmonization platform designed to connect, integrate, and analyze research data across multiple sources and modalities. Built specifically for research facilities facing complex data integration challenges, SDK uses knowledge graph technology and AI-powered tools to bridge the gap between highly standardized data (like genomics) and complex, heterogeneous data (like preclinical imaging).

### Core Value Proposition

SDK provides a unified layer that:
1. **Connects** to existing data sources without disruption
2. **Harmonizes** data using AI and knowledge graphs
3. **Enables** cross-modal queries and discovery
4. **Empowers** researchers with AI-assisted tools

For a comprehensive overview of the project, including architecture, features, and implementation strategy, please refer to the [index.md](index.md) file.
