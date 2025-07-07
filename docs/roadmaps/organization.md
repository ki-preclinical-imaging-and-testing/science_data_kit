# Roadmap Organization

## Overview

This document explains the organization of roadmaps in the Science Data Kit project. The roadmaps are organized into a logical structure to improve discoverability, maintainability, and integration with documentation systems.

## Directory Structure

The roadmaps are organized into the following directory structure:

```
docs/roadmaps/
├── active/            # Currently active roadmaps (current priorities)
│   ├── roadmap_DesignUX_00.md
│   ├── roadmap_DesignUX_01.md
│   ├── roadmap_CPB_00.md
│   ├── roadmap_memo.md
│   ├── roadmap_later.md
│   └── testing_status_template.md
├── future/            # Future roadmaps (planned but not currently active)
│   ├── README.md      # Overview of future roadmaps
│   ├── roadmap_kg_00.md
│   ├── roadmap_kgPhase1_00.md
│   ├── roadmap_kgPhase2_00.md
│   ├── roadmap_kgPhase3_00.md
│   ├── roadmap_kgPhase4_00.md
│   ├── roadmap_kgPhase5_00.md
│   ├── roadmap_kgPhase6_00.md
│   ├── roadmap_StrategicEnhancements_00.md
│   ├── knowledge_graph_vision.md
│   ├── knowledge_graph_technical_spec.md
│   └── knowledge_graph_examples.md
├── archive/           # Completed roadmaps
│   ├── index_complete.md  # Comprehensive index of all roadmaps
│   ├── roadmap_RepoReorg_00.md
│   ├── roadmap_RepoReorg_01.md
│   ├── roadmap_RepoReorg_02.md
│   ├── roadmap_RepoReorg_03.md
│   ├── roadmap_RepoReorg_04.md
│   ├── roadmap_CodebaseOrganization_00.md
│   ├── roadmap_CodebaseOrganization_01.md
│   └── ...
├── templates/         # Roadmap templates
│   ├── roadmap_template.md
│   └── testing_status_template.md
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
3. **Prioritization**: Roadmaps may be moved between the `active` and `future` directories based on current project priorities:
   - **Active Roadmaps**: Represent current development priorities that are actively being worked on
   - **Future Roadmaps**: Represent important strategic directions that have been temporarily deprioritized to focus on more fundamental work
4. **Archiving**: When a roadmap is completed, it is moved to the `archive` directory, and any remaining tasks are added to the appropriate roadmap or to the `roadmap_later.md` file for future consideration.

### Active vs. Future Roadmaps

The distinction between active and future roadmaps helps maintain focus on current priorities while preserving the planning work done for advanced features:

- **Active Roadmaps** (`active/` directory):
  - Currently being implemented or in active planning for immediate implementation
  - Represent the current focus of development efforts
  - Typically address fundamental platform capabilities and immediate priorities
  - Regularly updated with progress and status changes

- **Future Roadmaps** (`future/` directory):
  - Planned for future implementation but not currently active
  - Represent important strategic directions for the project
  - Typically address advanced features that build upon fundamental platform capabilities
  - Include timeline estimates for when they might return to active development
  - Preserved in their current state until they are reactivated

The `future/` directory includes a README.md file that provides an overview of all future roadmaps, their current status, and estimated timelines for when they might return to active development.

## Testing Integration

### When to Use Testing Prompts
Testing should be integrated into the roadmap lifecycle at strategic points:

- **During Active Development**: After completing 3-5 implementation tasks in a roadmap
- **Phase Transitions**: Before moving from one phase to another within a roadmap
- **Pre-Workshop**: When preparing features for user testing or feedback collection
- **Architecture Validation**: When implementing core architectural components or patterns
- **Quality Gates**: Before considering major components "complete"

### Testing Prompt Workflow
1. **Assessment**: Use prompt #21 (Pre-Review Code Analysis) to analyze current state
2. **Selection**: Based on assessment, select appropriate validation prompts (#17-24)
3. **Execution**: Run selected testing workflows
4. **Documentation**: Update roadmap files with testing results and findings
5. **Integration**: Address any issues before continuing development

### Testing Status Tracking
Testing status should be tracked in both individual roadmaps and the main index:

- **Individual Roadmaps**: Include testing results in "Current Status" sections
- **Main Index**: Update "Testing and Quality Status" section with progress
- **Documentation**: Record testing outcomes and any identified issues
- **Testing Status Reports**: Create dedicated testing status reports using the `templates/testing_status_template.md` template for comprehensive testing documentation

### Testing Prompt Reference
Quick reference for common testing scenarios:

- **Code Quality Review**: Prompt #19 - Comprehensive quality assessment
- **Manual Testing Prep**: Prompt #17 - Create testing checklists for human validation
- **Workshop Preparation**: Prompt #22 - Prepare features for user testing
- **Performance Validation**: Prompt #23 - Test scalability and performance
- **Real Data Testing**: Prompt #24 - Validate with scientific datasets
- **Pre-Review Analysis**: Prompt #21 - Prepare for human code review

## Roadmap Index

The main roadmap index (`index.md`) provides an overview of all active roadmaps and a link to the comprehensive index of all roadmaps (`archive/index_complete.md`). The comprehensive index includes both active and archived roadmaps, providing a complete history of the project's development.

## Integration with Documentation

The roadmaps are integrated with the Sphinx documentation system, allowing them to be included in the generated HTML documentation. This integration ensures that the roadmaps are easily accessible to all project stakeholders.

## Conclusion

This organization approach improves the discoverability, maintainability, and integration of roadmaps with documentation systems. It provides a clear structure for roadmap files, making it easier for project stakeholders to find and understand the project's direction and progress.
