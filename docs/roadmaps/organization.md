# Roadmap Organization

## Overview

This document explains the organization of roadmaps in the Science Data Kit project. The roadmaps are organized into a logical structure to improve discoverability, maintainability, and integration with documentation systems.

## Directory Structure

The roadmaps are organized into the following directory structure:

```
docs/roadmaps/
├── active/            # Currently active roadmaps
│   ├── roadmap_RepoReorg_00.md
│   ├── roadmap_kg_00.md
│   ├── roadmap_kgPhase1_00.md
│   ├── roadmap_kgPhase2_00.md
│   ├── roadmap_kgPhase3_00.md
│   ├── roadmap_kgPhase4_00.md
│   ├── roadmap_kgPhase5_00.md
│   ├── roadmap_kgPhase6_00.md
│   ├── knowledge_graph_vision.md
│   ├── knowledge_graph_technical_spec.md
│   └── knowledge_graph_examples.md
├── archive/           # Completed roadmaps
│   ├── index_complete.md  # Comprehensive index of all roadmaps
│   ├── roadmap_CodebaseOrganization_00.md
│   ├── roadmap_CodebaseOrganization_01.md
│   └── ...
├── templates/         # Roadmap templates
│   └── roadmap_template.md
└── index.md           # Main roadmap index
```

## Roadmap Naming Conventions

Roadmaps follow a specific naming convention to indicate their purpose and version:

1. **Component-specific roadmaps**: `roadmap_{component}_{mm}.md`
   - `{component}` is a descriptive name for the roadmap set (e.g., `MSGraphAPI`, `CodebaseOrganization`)
   - `{mm}` is a sequential number (e.g., `00`, `01`, `02`, ...) that indicates the version or progression of the roadmap

2. **Phase-specific roadmaps**: `roadmap_{component}Phase{n}_{mm}.md`
   - `{component}` is the descriptive name for the roadmap set (e.g., `kg` for Knowledge Graph)
   - `{n}` is the phase number within the component roadmap (e.g., `1`, `2`, `3`, ...)
   - `{mm}` is a sequential number (e.g., `00`, `01`, `02`, ...) that indicates the version or progression of the phase roadmap

## Roadmap Lifecycle

Roadmaps follow a specific lifecycle:

1. **Creation**: New roadmaps are created in the `active` directory using the appropriate template from the `templates` directory.
2. **Updates**: As work progresses, roadmaps are updated to reflect the current status of tasks and any changes to the plan.
3. **Archiving**: When a roadmap is completed, it is moved to the `archive` directory, and any remaining tasks are added to the appropriate roadmap or to the `roadmap_later.md` file for future consideration.

## Roadmap Index

The main roadmap index (`index.md`) provides an overview of all active roadmaps and a link to the comprehensive index of all roadmaps (`archive/index_complete.md`). The comprehensive index includes both active and archived roadmaps, providing a complete history of the project's development.

## Integration with Documentation

The roadmaps are integrated with the Sphinx documentation system, allowing them to be included in the generated HTML documentation. This integration ensures that the roadmaps are easily accessible to all project stakeholders.

## Conclusion

This organization approach improves the discoverability, maintainability, and integration of roadmaps with documentation systems. It provides a clear structure for roadmap files, making it easier for project stakeholders to find and understand the project's direction and progress.