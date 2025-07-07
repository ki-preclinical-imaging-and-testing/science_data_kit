# Science Data Kit (SDK) Repository Reorganization Roadmap - Version 03

## Overview
This roadmap outlines the current state of the Science Data Kit repository reorganization, with a particular focus on the organization of roadmap files and documentation. This document is an update to roadmap_RepoReorg_02.md, reflecting the progress made in implementing the repository structure improvements.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2024-08-10 | Initial version of Repository Reorganization roadmap |
| 01 | 2024-07-06 | Update reflecting the current state of reorganization |
| 02 | 2024-07-07 | Update reflecting completion of documentation integration and tools directory |
| 03 | 2024-07-07 | Update reflecting completion of config and docker directories |

## Background
The Science Data Kit repository has evolved over time, with roadmap files and documentation stored in various locations. As the project moves toward implementing the Knowledge Graph Documentation System, there was a need to reorganize the repository structure to improve discoverability, maintainability, and integration with documentation systems.

This reorganization represents the final roadmap created using the current approach before transitioning to the new organization system that will be used for the Knowledge Graph Documentation System.

## Goals
1. Create a more logical and maintainable structure for project documentation
2. Improve discoverability of roadmap files and other documentation
3. Prepare the repository for the implementation of the Knowledge Graph Documentation System
4. Ensure backward compatibility with existing references to documentation
5. Streamline the roadmap index to focus on active development

## Current Status
The repository reorganization has made significant progress, with most tasks now completed:

1. New directory structure has been created:
   - `docs/roadmaps/` directory has been created as the central location for all roadmap files
   - Subdirectories for active, archive, and templates have been created
   - New index.md and organization.md files have been created in the docs/roadmaps/ directory

2. Roadmap files have been moved to their new locations:
   - All active roadmaps have been moved to `docs/roadmaps/active/`
   - Archived roadmaps have been moved to `docs/roadmaps/archive/`
   - Roadmap templates have been moved to `docs/roadmaps/templates/`

3. Redirect notices have been added to all original roadmap files in the project directory:
   - Each file contains a standardized redirect notice at the top
   - The notice includes the new location, creation date, and removal date
   - Original files will be kept for a 1-month transition period (until August 6, 2024)

4. Documentation integration has been completed:
   - Sphinx configuration has been updated to include roadmaps and tools directory
   - Build scripts have been updated to work from the tools directory
   - Comprehensive index has been moved to archive
   - myst_parser package has been installed for Markdown support

5. Repository structure improvements have been implemented:
   - Tools directory has been created for development-related scripts
   - Development scripts have been moved to the tools directory
   - Config directory has been created for configuration files
   - Configuration files have been moved to the config directory
   - Docker directory has been created for Docker-related files
   - Docker files have been moved to the docker directory

## Roadmap Components

### 1. Documentation Reorganization

#### 1.1 Roadmap Files Structure
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create `docs/roadmaps/` directory | High | Completed | Central location for all roadmap files |
| Create `docs/roadmaps/active/` subdirectory | High | Completed | For currently active roadmaps |
| Create `docs/roadmaps/archive/` subdirectory | High | Completed | For completed roadmaps |
| Create `docs/roadmaps/templates/` subdirectory | Medium | Completed | For roadmap templates |
| Move active roadmaps to `docs/roadmaps/active/` | High | Completed | Including Knowledge Graph roadmap files |
| Move archived roadmaps to `docs/roadmaps/archive/` | High | Completed | From `project/archive/` |
| Move roadmap templates to `docs/roadmaps/templates/` | Medium | Completed | From `project/templates/` |

#### 1.2 Roadmap Index Updates
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create streamlined `docs/roadmaps/index.md` | High | Completed | Focus on active roadmaps |
| Move comprehensive index to `docs/roadmaps/archive/index_complete.md` | Medium | Completed | Preserve historical context |
| Update references to roadmap files | High | In Progress | In documentation and code |
| Add redirects from old locations | Medium | Completed | To maintain backward compatibility |

#### 1.3 Documentation Integration
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update Sphinx configuration | Medium | Completed | Updated to include roadmaps and tools directory |
| Create documentation for roadmap organization | Medium | Completed | Created organization.md |
| Update `roadmap_memo.md` | Medium | Completed | Document new organization approach |
| Update build scripts | Medium | Completed | Updated build_docs.py to work from tools directory |
| Install myst_parser package | Medium | Completed | For Markdown support in documentation |

### 2. Repository Structure Improvements

#### 2.1 Root Directory Cleanup
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create `tools/` directory | Medium | Completed | For development-related scripts |
| Move development scripts to `tools/` | Medium | Completed | Moved run_black.py, run_mypy.py, run_coverage.py, build_docs.py |
| Create `config/` directory | Low | Completed | For configuration files |
| Move configuration files to `config/` | Low | Completed | Moved db_config.yaml, db_config.template.yaml, README_CONFIG.md |

#### 2.2 Docker Organization
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create `docker/` directory | Low | Completed | For Docker-related files |
| Move Docker files to `docker/` directory | Low | Completed | Moved Dockerfile, Dockerfile.workshop, docker-compose.yml, etc. |
| Update Docker documentation | Low | To Do | Reflect new organization |

#### 2.3 Test Organization
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Review test directory structure | Low | To Do | Ensure it mirrors package structure |
| Update test documentation | Low | To Do | Reflect any changes |

## Implementation Details

### Documentation Integration
The documentation integration has been completed with the following changes:

1. **Sphinx Configuration Update**:
   - Updated conf.py to remove references to the removed app directory
   - Added tools directory to autoapi_dirs to include development scripts in the documentation
   - Kept myst_parser extension for parsing Markdown files

2. **Build Scripts Update**:
   - Moved build_docs.py to the tools directory
   - Updated the script to determine its location and adjust paths accordingly
   - Added logic to handle running the script from different directories
   - Created symbolic links in the root directory for backward compatibility

3. **Tools Directory Creation**:
   - Created tools directory for development-related scripts
   - Moved run_black.py, run_mypy.py, run_coverage.py, and build_docs.py to tools directory
   - Created symbolic links in the root directory for backward compatibility
   - Tested scripts to ensure they work correctly from their new location

4. **myst_parser Installation**:
   - Installed myst_parser package for Markdown support in documentation
   - Tested documentation build with myst_parser package installed
   - Identified issue with autoapi extension that needs further investigation

### Repository Structure Improvements

1. **Config Directory Creation**:
   - Created config directory for configuration files
   - Moved db_config.yaml and db_config.template.yaml to config directory
   - Moved README_CONFIG.md to config directory
   - Kept .pre-commit-config.yaml in the root directory as it's required there for pre-commit hooks

2. **Docker Directory Creation**:
   - Created docker directory for Docker-related files
   - Moved Dockerfile and Dockerfile.workshop to docker directory
   - Moved docker-compose.yml, docker-compose-full.yml, and docker-compose-workshop.yml to docker directory
   - Moved docker-entrypoint.sh and docker-entrypoint-workshop.sh to docker directory

## Remaining Tasks

1. **Complete Documentation Integration**:
   - Resolve issue with autoapi extension in documentation build
   - The current error is: "No such file or directory: '/home/patch/PycharmProjects/science_data_kit/docs/source/autoapi/index.rst'"
   - Further investigation is needed to understand why the autoapi directory is not being properly recognized

2. **Repository Structure Improvements**:
   - Implement all tasks in section 2.3
   - Update Docker documentation to reflect the new organization
   - These tasks are lower priority and can be completed in a future phase

3. **Finalize Transition**:
   - Continue monitoring access to old file locations during the transition period
   - After the transition period (August 6, 2024), remove the original files from the project/ directory

## Knowledge Graph Integration Considerations

The reorganization supports the upcoming Knowledge Graph Documentation System in several ways:

1. **Centralized Documentation**: By moving all roadmaps to the `docs/` directory, they will be more easily indexed by the Knowledge Graph system.

2. **Logical Structure**: The new organization creates a more logical structure that will be easier for the Knowledge Graph to represent and navigate.

3. **Reduced Duplication**: Streamlining the roadmap index reduces duplication and makes it easier to maintain a single source of truth.

4. **Improved Discoverability**: The new structure improves discoverability for both humans and AI agents.

5. **Self-Preserving Transition**: The approach of copying roadmaps before moving them and maintaining redirects ensures that the Knowledge Graph system can properly index the roadmaps even during the transition period.

## Success Metrics

1. **Organization Clarity**: All roadmap files and documentation have a clear, logical location in the repository. ✓

2. **Build Integration**: Documentation builds successfully include roadmap files. (In Progress)

3. **Backward Compatibility**: Existing references to documentation continue to work through redirects or updates. ✓

4. **Reduced Clutter**: Root directory contains fewer files, with specialized files moved to appropriate subdirectories. ✓

5. **Knowledge Graph Readiness**: Repository structure is ready for Knowledge Graph Documentation System implementation. ✓

6. **Self-Preservation Success**: The roadmap itself remains accessible throughout the reorganization process, and the transition to the new location is completed without loss of information or accessibility. ✓

7. **Transition Effectiveness**: Redirects successfully guide users to new file locations, with minimal disruption during the transition period. ✓

8. **Reference Integrity**: All references to roadmap files (both internal and external) are successfully updated to point to the new locations. (In Progress)

## Next Steps

1. **Resolve Documentation Build Issues**:
   - Investigate the issue with the autoapi extension in the documentation build
   - Consider alternative approaches if the issue cannot be resolved easily
   - Document the solution for future reference

2. **Complete Remaining Repository Structure Improvements**:
   - Update Docker documentation to reflect the new organization
   - Review and update the test directory structure if needed
   - Update test documentation to reflect any changes

3. **Prepare for Knowledge Graph Documentation System**:
   - Ensure all roadmap files are properly formatted for the Knowledge Graph system
   - Document the new organization structure for the Knowledge Graph team
   - Identify any remaining issues that need to be addressed before implementing the Knowledge Graph system

## Conclusion

The repository reorganization has made significant progress, with most tasks now completed. The new structure provides a more logical and maintainable organization for project documentation and code, improving discoverability and preparing the repository for the implementation of the Knowledge Graph Documentation System.

The remaining tasks focus on resolving documentation build issues and completing the lower-priority repository structure improvements. The transition period will continue until August 6, 2024, after which the original files will be removed from the project directory.

This reorganization represents an important milestone in the evolution of the Science Data Kit, setting the stage for the next phase of development with the Knowledge Graph Documentation System.