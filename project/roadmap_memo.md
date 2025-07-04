# Science Data Kit (SDK) Project Directory Guidelines

This document provides guidelines for working with the Science Data Kit project directory, particularly focusing on roadmap files and their organization.

## Directory Structure

The project directory is organized as follows:

- **project/**: Main directory for project planning and roadmap files
  - **archive/**: Contains completed roadmap sets that are no longer actively being worked on
  - **templates/**: Contains templates for creating new roadmap files
  - **roadmap_phase?_??.md**: Active roadmap files that are currently being worked on, organized by phase
  - **roadmap_index.md**: Master index of all roadmaps, providing an overview of the project's direction
  - **roadmap_later.md**: Collection of tasks from completed roadmaps that are planned for future implementation
  - **roadmap_memo.md**: This file, providing guidelines for working with the project directory

## Roadmap Organization

Roadmaps in the Science Data Kit project are organized in phases, with each phase representing a major development cycle. Within each phase, roadmap files are versioned sequentially. Roadmap files follow a naming convention:

```
roadmap_phase{n}_{mm}.md
```

Where:
- `{n}` is the phase number (e.g., `1`, `2`, `3`, ...)
- `{mm}` is a sequential number (e.g., `00`, `01`, `02`, ...) that indicates the version or progression of the roadmap within that phase

For example:
- `roadmap_phase1_00.md`, `roadmap_phase1_01.md`, `roadmap_phase1_02.md`, ...
- `roadmap_phase2_00.md`, `roadmap_phase2_01.md`, ...

For component-specific roadmaps that are not tied to a specific phase, the naming convention is:

```
roadmap_{component}_{mm}.md
```

Where:
- `{component}` is a descriptive name for the roadmap set (e.g., `MSGraphAPI`, `CodebaseOrganization`, `refactor_app`)
- `{mm}` is a sequential number (e.g., `00`, `01`, `02`, ...) that indicates the version or progression of the roadmap

For example:
- `roadmap_MSGraphAPI_00.md`, `roadmap_MSGraphAPI_01.md`, `roadmap_MSGraphAPI_02.md`, ...
- `roadmap_CodebaseOrganization_00.md`, `roadmap_CodebaseOrganization_01.md`, ...
- `roadmap_refactor_app_01.md`, `roadmap_refactor_app_02.md`, ...

## Working with Roadmaps

### Creating a New Roadmap

1. Identify the phase or component you want to create or extend
2. If creating a new phase, start with `roadmap_phase{n}_00.md`
3. If extending an existing phase, use the next sequential number in the series
4. If creating a new component-specific roadmap, choose a descriptive name for the `{component}` part of the filename
5. Use the template in `project/templates/roadmap_template.md` as a starting point
6. Update the roadmap_index.md file to include the new roadmap

### Updating an Existing Roadmap

1. Create a new version by incrementing the version number
2. Copy content from the previous version
3. Update status of tasks and add new tasks as needed
4. Add implementation details for completed tasks
5. Update the "Current Status" and "Next Steps" sections
6. Reference the new roadmap in the roadmap_index.md file

### Archiving Completed Roadmaps

When a roadmap phase or component is completed (all planned tasks have been implemented), the roadmap files should be moved to the archive directory:

1. Move all files in the completed roadmap set to the `project/archive/` directory
2. Extract any remaining tasks (marked as "To Do" or in the "Next Steps" section) and add them to the `roadmap_later.md` file
3. Update the roadmap_index.md file to reflect that the roadmap set has been completed and archived

## Roadmap Content Guidelines

Each roadmap file should include the following sections:

1. **Overview**: A brief description of the roadmap's purpose and scope
2. **Background** (if applicable): Context and information about previous phases or related work
3. **Goals**: Clear objectives for the current phase or component
4. **Roadmap Components**: Detailed breakdown of tasks, organized by category
5. **Implementation Plan**: Timeline and phases for implementing the roadmap
6. **Current Status**: A summary of the current state of the project with respect to the roadmap
7. **Next Steps**: A list of tasks planned for the next phase of implementation
8. **Success Metrics**: Measurable criteria for determining the success of the roadmap
9. **Conclusion**: A summary of the progress made and the path forward

## Roadmap Index

The roadmap_index.md file serves as a master index for all roadmaps in the Science Data Kit project. It provides links to all phase and component-specific roadmaps and a high-level overview of the project's direction.

The roadmap_index.md file should be updated whenever:
- A new roadmap phase or component is created
- A new version of an existing roadmap is created
- A roadmap phase or component is completed and archived

The roadmap_index.md file should include:
- An overview of the project
- A list of active roadmaps with links, status, and next steps
- A list of archived roadmaps with links and status
- A description of the project direction
- A conclusion summarizing the current state and future plans

## Later Phase Tasks

The roadmap_later.md file collects remaining tasks from completed roadmaps that have been moved to the archive. These tasks represent potential future enhancements to the Science Data Kit.

When archiving a completed roadmap set, any remaining tasks (marked as "To Do" or in the "Next Steps" section) should be added to the roadmap_later.md file, organized by the roadmap phase or component they came from.

## Phase Transitions

When transitioning from one phase to another:

1. Complete all high-priority tasks from the current phase
2. Archive all roadmap files from the completed phase
3. Create a new roadmap file for the next phase (e.g., `roadmap_phase{n+1}_00.md`)
4. Update the roadmap_index.md file to reflect the phase transition
5. Add any remaining tasks from the completed phase to the roadmap_later.md file
