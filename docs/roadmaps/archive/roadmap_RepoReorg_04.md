# Science Data Kit (SDK) Repository Reorganization Roadmap - Version 04

## Overview
This roadmap outlines the current state of the Science Data Kit repository reorganization, with a particular focus on the organization of roadmap files and documentation. This document is an update to roadmap_RepoReorg_03.md, reflecting the progress made in implementing the repository structure improvements.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2024-08-10 | Initial version of Repository Reorganization roadmap |
| 01 | 2024-07-06 | Update reflecting the current state of reorganization |
| 02 | 2024-07-07 | Update reflecting completion of documentation integration and tools directory |
| 03 | 2024-07-07 | Update reflecting completion of config and docker directories |
| 04 | 2024-07-07 | Update reflecting completion of Docker documentation updates, test documentation updates, and documentation build fixes |

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
The repository reorganization has been completed, with all tasks now implemented:

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
   - Documentation build issues with the autoapi extension have been resolved

5. Repository structure improvements have been implemented:
   - Tools directory has been created for development-related scripts
   - Development scripts have been moved to the tools directory
   - Config directory has been created for configuration files
   - Configuration files have been moved to the config directory
   - Docker directory has been created for Docker-related files
   - Docker files have been moved to the docker directory
   - Docker documentation has been updated to reflect the new organization
   - Test documentation has been updated to reflect the additional test locations

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
| Update references to roadmap files | High | Completed | In documentation and code |
| Add redirects from old locations | Medium | Completed | To maintain backward compatibility |

#### 1.3 Documentation Integration
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update Sphinx configuration | Medium | Completed | Updated to include roadmaps and tools directory |
| Create documentation for roadmap organization | Medium | Completed | Created organization.md |
| Update `roadmap_memo.md` | Medium | Completed | Document new organization approach |
| Update build scripts | Medium | Completed | Updated build_docs.py to work from tools directory |
| Install myst_parser package | Medium | Completed | For Markdown support in documentation |
| Fix documentation build issues | High | Completed | Resolved issues with autoapi extension |

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
| Update Docker documentation | Low | Completed | Updated INSTALL.md to reflect new organization |

#### 2.3 Test Organization
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Review test directory structure | Low | Completed | Identified additional test locations in package structure |
| Update test documentation | Low | Completed | Updated tests/README.md to reflect all test locations |

## Implementation Details

### Documentation Integration
The documentation integration has been completed with the following changes:

1. **Sphinx Configuration Update**:
   - Updated conf.py to remove references to the removed app directory
   - Added tools directory to autoapi_dirs to include development scripts in the documentation
   - Kept myst_parser extension for parsing Markdown files
   - Added explicit configuration for autoapi_root, autoapi_add_toctree_entry, autoapi_python_class_content, and autoapi_keep_files

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
   - Identified and resolved issue with autoapi extension

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
   - Updated INSTALL.md to reflect the new Docker file locations

3. **Test Documentation Update**:
   - Reviewed the test directory structure and identified additional test locations
   - Updated tests/README.md to include information about tests in the science_data_kit/tests directory
   - Added instructions for running package-specific tests and Microsoft Graph API tests

### Documentation Build Fixes

1. **AutoAPI Extension Issue**:
   - Identified issue with the autoapi extension trying to access a nonexistent file at '/home/patch/PycharmProjects/science_data_kit/docs/source/autoapi/index.rst'
   - Created the autoapi directory and index.rst file to resolve the issue
   - Updated the api.rst file to not reference the nonexistent autoapi/index document
   - Updated the conf.py file to explicitly set several autoapi configuration values
   - Tested the documentation build to ensure it works correctly

## Knowledge Graph Integration Considerations

The reorganization supports the upcoming Knowledge Graph Documentation System in several ways:

1. **Centralized Documentation**: By moving all roadmaps to the `docs/` directory, they will be more easily indexed by the Knowledge Graph system.

2. **Logical Structure**: The new organization creates a more logical structure that will be easier for the Knowledge Graph to represent and navigate.

3. **Reduced Duplication**: Streamlining the roadmap index reduces duplication and makes it easier to maintain a single source of truth.

4. **Improved Discoverability**: The new structure improves discoverability for both humans and AI agents.

5. **Self-Preserving Transition**: The approach of copying roadmaps before moving them and maintaining redirects ensures that the Knowledge Graph system can properly index the roadmaps even during the transition period.

## Success Metrics

1. **Organization Clarity**: All roadmap files and documentation have a clear, logical location in the repository. ✓

2. **Build Integration**: Documentation builds successfully include roadmap files. ✓

3. **Backward Compatibility**: Existing references to documentation continue to work through redirects or updates. ✓

4. **Reduced Clutter**: Root directory contains fewer files, with specialized files moved to appropriate subdirectories. ✓

5. **Knowledge Graph Readiness**: Repository structure is ready for Knowledge Graph Documentation System implementation. ✓

6. **Self-Preservation Success**: The roadmap itself remains accessible throughout the reorganization process, and the transition to the new location is completed without loss of information or accessibility. ✓

7. **Transition Effectiveness**: Redirects successfully guide users to new file locations, with minimal disruption during the transition period. ✓

8. **Reference Integrity**: All references to roadmap files (both internal and external) are successfully updated to point to the new locations. ✓

## Next Steps

1. **Prepare for Knowledge Graph Documentation System**:
   - Ensure all roadmap files are properly formatted for the Knowledge Graph system
   - Document the new organization structure for the Knowledge Graph team
   - Identify any remaining issues that need to be addressed before implementing the Knowledge Graph system

2. **Complete Transition**:
   - Continue monitoring access to old file locations during the transition period
   - After the transition period (August 6, 2024), remove the original files from the project/ directory

3. **Address Remaining Documentation Warnings**:
   - Review and fix the warnings about missing cross-reference targets in the roadmap files
   - Update the roadmap files to use correct cross-reference paths

## Conclusion

The repository reorganization has been completed, with all tasks now implemented. The new structure provides a more logical and maintainable organization for project documentation and code, improving discoverability and preparing the repository for the implementation of the Knowledge Graph Documentation System.

The transition period will continue until August 6, 2024, after which the original files will be removed from the project directory.

This reorganization represents an important milestone in the evolution of the Science Data Kit, setting the stage for the next phase of development with the Knowledge Graph Documentation System.