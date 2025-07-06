# Science Data Kit (SDK) Repository Reorganization Roadmap - Version 00

## Overview
This roadmap outlines the plan for reorganizing the Science Data Kit repository structure, with a particular focus on improving the organization of roadmap files and documentation. The reorganization will prepare the repository for the implementation of the Knowledge Graph Documentation System by creating a more logical and maintainable structure for project documentation.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2024-08-10 | Initial version of Repository Reorganization roadmap |

## Background
The Science Data Kit repository has evolved over time, with roadmap files and documentation stored in various locations. As the project moves toward implementing the Knowledge Graph Documentation System, there is a need to reorganize the repository structure to improve discoverability, maintainability, and integration with documentation systems.

This reorganization represents the final roadmap created using the current approach before transitioning to the new organization system that will be used for the Knowledge Graph Documentation System.

## Goals
1. Create a more logical and maintainable structure for project documentation
2. Improve discoverability of roadmap files and other documentation
3. Prepare the repository for the implementation of the Knowledge Graph Documentation System
4. Ensure backward compatibility with existing references to documentation
5. Streamline the roadmap index to focus on active development

## Current Status
The current repository structure has several areas that could be improved:

1. Roadmap files are stored in the `project/` directory at the repository root
2. Archived roadmaps are stored in `project/archive/`
3. The `roadmap_index.md` file contains both active and archived roadmaps
4. Documentation is spread across multiple directories
5. The root directory contains many scripts and configuration files

## Roadmap Components

### 1. Documentation Reorganization

#### 1.1 Roadmap Files Structure
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create `docs/roadmaps/` directory | High | To Do | Central location for all roadmap files |
| Create `docs/roadmaps/active/` subdirectory | High | To Do | For currently active roadmaps |
| Create `docs/roadmaps/archive/` subdirectory | High | To Do | For completed roadmaps |
| Create `docs/roadmaps/templates/` subdirectory | Medium | To Do | For roadmap templates |
| Move active roadmaps to `docs/roadmaps/active/` | High | To Do | Including Knowledge Graph roadmap files |
| Move archived roadmaps to `docs/roadmaps/archive/` | High | To Do | From `project/archive/` |
| Move roadmap templates to `docs/roadmaps/templates/` | Medium | To Do | From `project/templates/` |

#### 1.2 Roadmap Index Updates
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create streamlined `docs/roadmaps/index.md` | High | To Do | Focus on active roadmaps |
| Move comprehensive index to `docs/roadmaps/archive/index_complete.md` | Medium | To Do | Preserve historical context |
| Update references to roadmap files | High | To Do | In documentation and code |
| Add redirects from old locations | Medium | To Do | To maintain backward compatibility |

#### 1.3 Documentation Integration
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update Sphinx configuration | Medium | To Do | To include roadmaps in documentation build |
| Create documentation for roadmap organization | Medium | To Do | Explain new structure and conventions |
| Update `roadmap_memo.md` | Medium | To Do | Document new organization approach |
| Update build scripts | Medium | To Do | Ensure documentation builds correctly |

### 2. Repository Structure Improvements

#### 2.1 Root Directory Cleanup
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create `tools/` directory | Medium | To Do | For development-related scripts |
| Move development scripts to `tools/` | Medium | To Do | Scripts like `run_black.py`, `run_mypy.py`, etc. |
| Create `config/` directory | Low | To Do | For configuration files |
| Move configuration files to `config/` | Low | To Do | Where appropriate |

#### 2.2 Docker Organization
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create `docker/` directory | Low | To Do | For Docker-related files |
| Move Docker files to `docker/` directory | Low | To Do | Dockerfile, docker-compose.yml, etc. |
| Update Docker documentation | Low | To Do | Reflect new organization |

#### 2.3 Test Organization
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Review test directory structure | Low | To Do | Ensure it mirrors package structure |
| Update test documentation | Low | To Do | Reflect any changes |

## Implementation Plan

### Phase 1: Documentation Reorganization (Weeks 1-2)

1. Create New Directory Structure
   - Create `docs/roadmaps/` directory
   - Create subdirectories for active, archive, and templates
   - Set up appropriate permissions and .gitignore rules

2. Move Roadmap Files
   - Create a copy of this roadmap (roadmap_RepoReorg_00.md) in `docs/roadmaps/active/` to ensure it's not lost during the reorganization
   - Move other active roadmaps to `docs/roadmaps/active/`
   - Move archived roadmaps to `docs/roadmaps/archive/`
   - Move roadmap templates to `docs/roadmaps/templates/`
   - Verify all files are moved correctly
   - Keep the original roadmap_RepoReorg_00.md in place until the reorganization is complete

3. Update Roadmap Index
   - Create streamlined `docs/roadmaps/index.md`
   - Move comprehensive index to `docs/roadmaps/archive/index_complete.md`
   - Update references to roadmap files
   - Add redirects from old locations
   - Create a mapping document that tracks old file locations to new locations
   - Update any external documentation that references the roadmap files

4. Documentation Integration
   - Update Sphinx configuration
   - Create documentation for roadmap organization
   - Update `roadmap_memo.md`
   - Update build scripts
   - Test documentation build

5. Finalize Transition
   - Verify all roadmap files are correctly moved and accessible in their new locations
   - Update any remaining references to the old locations
   - Add a note to the original roadmap_RepoReorg_00.md indicating it has been moved, with a clear link to the new location
   - Create a standardized redirect format for all moved files that includes:
     * A prominent notice at the top of the file
     * The exact path to the new location
     * The date when the redirect was created
     * The expected date when the original file will be removed
   - Keep the original files in place for a transition period (e.g., 1 month) with these clear redirects
   - Set up monitoring to track access to old file locations during the transition period
   - After the transition period, remove the original files from the project/ directory only after confirming no active references remain

### Phase 2: Repository Structure Improvements (Weeks 3-4)

1. Root Directory Cleanup
   - Create `tools/` directory
   - Move development scripts to `tools/`
   - Create `config/` directory
   - Move configuration files to `config/`
   - Update references to moved files

2. Docker and Test Organization
   - Create `docker/` directory
   - Move Docker files to `docker/` directory
   - Review and update test directory structure
   - Update documentation to reflect changes
   - Test all affected components

## Knowledge Graph Integration Considerations

The reorganization will support the upcoming Knowledge Graph Documentation System in several ways:

1. **Centralized Documentation**: By moving all roadmaps to the `docs/` directory, they will be more easily indexed by the Knowledge Graph system.

2. **Logical Structure**: The new organization creates a more logical structure that will be easier for the Knowledge Graph to represent and navigate.

3. **Reduced Duplication**: Streamlining the roadmap index reduces duplication and makes it easier to maintain a single source of truth.

4. **Improved Discoverability**: The new structure improves discoverability for both humans and AI agents.

5. **Self-Preserving Transition**: The approach of copying roadmaps before moving them and maintaining redirects ensures that the Knowledge Graph system can properly index the roadmaps even during the transition period.

## Success Metrics

1. **Organization Clarity**: All roadmap files and documentation have a clear, logical location in the repository.

2. **Build Integration**: Documentation builds successfully include roadmap files.

3. **Backward Compatibility**: Existing references to documentation continue to work through redirects or updates.

4. **Reduced Clutter**: Root directory contains fewer files, with specialized files moved to appropriate subdirectories.

5. **Knowledge Graph Readiness**: Repository structure is ready for Knowledge Graph Documentation System implementation.

6. **Self-Preservation Success**: The roadmap itself remains accessible throughout the reorganization process, and the transition to the new location is completed without loss of information or accessibility.

7. **Transition Effectiveness**: Redirects successfully guide users to new file locations, with minimal disruption during the transition period.

8. **Reference Integrity**: All references to roadmap files (both internal and external) are successfully updated to point to the new locations.

## Conclusion

This repository reorganization represents an important step in preparing the Science Data Kit for the implementation of the Knowledge Graph Documentation System. By creating a more logical and maintainable structure for project documentation, we will improve discoverability, maintainability, and integration with documentation systems.

The self-preserving approach to this reorganization ensures that the roadmap itself remains accessible throughout the process, avoiding the paradox of a plan that deletes itself before completion. The comprehensive transition strategy with standardized redirects, monitoring, and verification steps will ensure continuity of access for all users and systems that rely on these documents. This careful approach demonstrates the thoughtful planning that will be essential for the Knowledge Graph Documentation System implementation and sets a standard for future organizational changes.

The reorganization will be the final roadmap created using the current approach before transitioning to the new organization system that will be used for the Knowledge Graph Documentation System. Upon completion, the repository will be well-structured for the next phase of development.
