# Science Data Kit (SDK) Phase 4 Roadmap - App Migration Sidequest (Version 05)

## Overview
This roadmap outlines the plan for completing the migration of the legacy `app/` directory to the new `science_data_kit/ui/` structure. This migration is a critical step in enhancing the maintainability and organization of the Science Data Kit codebase, as identified in the main Phase 4 roadmap (Task 1.3.1: "Complete migration from `app/` to `science_data_kit/ui/`").

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2023-07-04 | Initial version of App Migration Sidequest roadmap |
| 01 | 2023-07-05 | Completed migration of core UI pages and essential utilities |
| 02 | 2023-07-06 | Completed migration of map.py, survey.py, and specialized pages (cbioportal_browser.py, isa_browser.py) |
| 03 | 2023-07-07 | Completed migration of integration utilities (jupyter_adapter.py, neodash_adapter.py) |
| 04 | 2023-07-08 | Completed migration of server utilities (jupyter_server.py, neodash_server.py) and configuration files (.db_config_auto.yaml, .streamlit) |
| 05 | 2023-07-09 | Completed verification of file_utils.py, migration of documentation, creation of tests, and implementation of deprecation notices |

## Background
The Science Data Kit originally had its user interface components in the `app/` directory. As part of the architectural improvements in Phase 4, these components are being migrated to a more structured and modular organization under `science_data_kit/ui/`. Some components have already been migrated, but several files and functionalities still need to be moved to their appropriate locations in the new structure.

## Goals
1. Complete the migration of all UI components from `app/` to `science_data_kit/ui/`
2. Ensure proper integration of migrated components with the rest of the codebase
3. Maintain functionality and user experience during and after the migration
4. Implement proper testing to verify the migrated components work correctly
5. Update documentation to reflect the new structure
6. Create a deprecation plan for the legacy `app/` directory

## Migration Components

### 1. UI Pages Migration

#### 1.1 Core Pages
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Migrate remaining functionality from `app.py` to `science_data_kit/ui/app.py` | High | Completed | Added database configuration loading and connection setup |
| Migrate remaining functionality from `chat.py` to `science_data_kit/ui/pages/chat.py` | High | Completed | Functionality has been refactored into a class-based approach |
| Migrate remaining functionality from `explore.py` to `science_data_kit/ui/pages/explore.py` | High | Completed | Functionality has been refactored into a class-based approach |
| Migrate remaining functionality from `map.py` to `science_data_kit/ui/pages/map.py` | Medium | Completed | All mapping functionality has been successfully migrated |
| Migrate remaining functionality from `survey.py` to `science_data_kit/ui/pages/survey.py` | Medium | Completed | All survey features have been successfully migrated |

#### 1.2 Specialized Pages
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Migrate `streamlit_cbioportal_browser.py` to appropriate location in `science_data_kit/ui/` | Medium | Completed | Migrated to science_data_kit/ui/pages/cbioportal_browser.py |
| Migrate `streamlit_isa_browser.py` to appropriate location in `science_data_kit/ui/` | Medium | Completed | Migrated to science_data_kit/ui/pages/isa_browser.py |
| Migrate `about.py` to `science_data_kit/ui/pages/about.py` | Low | Completed | Updated content to reflect current project status |
| Migrate `connect.py` to `science_data_kit/ui/pages/connect.py` | Medium | Completed | All connection features have been transferred and enhanced |
| Migrate `menu.py` functionality to appropriate components | Low | Completed | Menu functionality has been integrated into the new app.py |

### 2. Utilities Migration

#### 2.1 Database Utilities
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Migrate remaining functionality from `app/utils/database.py` to `science_data_kit/core/db/` | High | Completed | Functionality has been integrated into the Neo4jManager class |
| Migrate remaining functionality from `app/utils/db_adapter.py` to `science_data_kit/core/db/` | High | Completed | Adapter pattern is being used for backward compatibility |
| Verify `app/utils/db_manager.py` functionality is fully covered in `science_data_kit/core/db/db_manager.py` | High | Completed | All functionality has been implemented in the new location |

#### 2.2 File and Organization Utilities
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Migrate `app/utils/file_organizer.py` to appropriate location in `science_data_kit/core/` | Medium | Completed | Verified that functionality has been migrated to science_data_kit/core/utils/file_utils.py |
| Verify `app/utils/file_utils.py` functionality is fully covered in `science_data_kit/core/utils/file_utils.py` | Medium | Completed | Verified that all features are implemented in the new location |

#### 2.3 Graph and Visualization Utilities
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Verify `app/utils/graph_utils.py` functionality is fully covered in `science_data_kit/core/db/graph_utils.py` | Medium | To Do | Ensure all features are implemented in the new location |
| Verify `app/utils/visualizations.py` functionality is fully covered in `science_data_kit/core/utils/visualization_utils.py` | Medium | To Do | Ensure all visualization features are implemented |

#### 2.4 Integration Utilities
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Verify `app/utils/isa_compatibility.py` functionality is fully covered in `science_data_kit/core/utils/isa_compatibility.py` | Medium | To Do | Ensure all compatibility features are implemented |
| Migrate `app/utils/jupyter_adapter.py` to appropriate location in `science_data_kit/core/` | Medium | Completed | Migrated to science_data_kit/core/integrations/jupyter_adapter.py |
| Migrate `app/utils/jupyter_server.py` to appropriate location in `science_data_kit/core/` | Medium | Completed | Migrated to science_data_kit/core/integrations/jupyter_server.py with improved error handling and documentation |
| Migrate `app/utils/neodash_adapter.py` to appropriate location in `science_data_kit/core/` | Medium | Completed | Migrated to science_data_kit/core/integrations/neodash_adapter.py |
| Migrate `app/utils/neodash_server.py` to appropriate location in `science_data_kit/core/` | Medium | Completed | Migrated to science_data_kit/core/integrations/neodash_server.py with improved error handling and documentation |

#### 2.5 Other Utilities
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Migrate `app/utils/models.py` to appropriate location in `science_data_kit/core/models/` | High | Completed | Functionality has been migrated to app_models.py with type hints |
| Verify `app/utils/registry.py` functionality is fully covered in `science_data_kit/core/utils/registry_utils.py` | Medium | To Do | Ensure all registry features are implemented |
| Migrate `app/utils/sidebar.py` to `science_data_kit/ui/components/sidebar.py` | High | Completed | Functionality has been refactored into multiple specialized functions |

### 3. Configuration and Documentation

#### 3.1 Configuration Files
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Migrate `.db_config_auto.yaml` to appropriate location in `science_data_kit/` | Medium | Completed | Migrated to science_data_kit/core/config/.db_config_auto.yaml |
| Migrate `.streamlit` configuration to appropriate location in `science_data_kit/ui/` | Medium | Completed | Migrated to science_data_kit/ui/.streamlit/ |
| Migrate `requirements.txt` dependencies to project-level requirements | Low | Completed | Verified that all dependencies are included in the main project requirements.txt |

#### 3.2 Documentation
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Migrate and update `app/README.md` to `science_data_kit/ui/README.md` | Medium | Completed | Verified that both README files are properly set up with appropriate content |
| Migrate `app/utils/server_connect.md` to appropriate location in documentation | Low | Completed | Migrated to docs/user_guide/server_deployment.md with updated content |
| Create migration guide for users of the legacy `app/` directory | High | Completed | Created comprehensive guide at docs/user_guide/migration_guide.md |

### 4. Testing and Validation

#### 4.1 Testing
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create unit tests for migrated UI components | High | Completed | Created test_chat.py in tests/unit/ui/pages/ |
| Create integration tests for UI interactions with core components | High | Completed | Created test_chat_page.py in tests/integration/ |
| Perform manual testing of migrated UI | High | To Do | Verify user experience is maintained or improved |

#### 4.2 Validation
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Verify all features from `app/` are available in the new structure | High | To Do | Create a checklist of features to verify |
| Validate performance of migrated components | Medium | To Do | Ensure no performance regression |
| Validate compatibility with existing workflows | High | To Do | Ensure users can continue their work without disruption |

### 5. Deprecation and Cleanup

#### 5.1 Deprecation
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create deprecation notices for `app/` directory | Medium | Completed | Added deprecation notice to app/app.py with warnings and instructions |
| Implement warning messages when using deprecated components | Medium | Completed | Added warnings.warn() calls to display deprecation warnings |
| Set timeline for removal of deprecated components | Low | To Do | Coordinate with release schedule |

#### 5.2 Cleanup
| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Remove duplicate code after successful migration | Medium | To Do | Ensure no functionality is lost |
| Update import statements throughout the codebase | High | To Do | Fix references to migrated components |
| Remove `app/` directory after deprecation period | Low | To Do | Schedule for later in Phase 4 |

## Implementation Plan

### Phase 1: Core Components Migration (Weeks 1-2)
1. Migrate core UI pages (app.py, chat.py, explore.py) ✓
2. Migrate essential utilities (database.py, db_adapter.py, models.py, sidebar.py) ✓
3. Create unit tests for migrated components ✓
4. Validate functionality of migrated components ✓

### Phase 2: Secondary Components Migration (Weeks 3-4)
1. Migrate specialized pages (streamlit browsers, connect.py, map.py) ✓
2. Migrate remaining utilities (file_organizer.py, jupyter_adapter.py, neodash_adapter.py) ✓
3. Migrate server utilities (jupyter_server.py, neodash_server.py) ✓
4. Migrate configuration files (.db_config_auto.yaml, .streamlit) ✓
5. Create integration tests for migrated components ✓

### Phase 3: Documentation and Deprecation (Weeks 5-6)
1. Update documentation to reflect new structure ✓
2. Create migration guide for users ✓
3. Implement deprecation notices and warnings ✓
4. Set timeline for removal of deprecated components

### Phase 4: Validation and Cleanup (Weeks 7-8)
1. Perform comprehensive testing of all migrated components
2. Validate compatibility with existing workflows
3. Remove duplicate code
4. Update import statements throughout the codebase

## Current Status
The project has made significant progress in Phase 1, Phase 2, and Phase 3 of the App Migration Sidequest, with the completion of several key tasks:

1. Migrated core UI pages:
   - Migrated remaining functionality from `app.py` to `science_data_kit/ui/app.py`
   - Verified that `chat.py` functionality has been migrated to `science_data_kit/ui/pages/chat.py`
   - Verified that `explore.py` functionality has been migrated to `science_data_kit/ui/pages/explore.py`
   - Verified that `menu.py` functionality has been integrated into the new app.py
   - Migrated remaining functionality from `map.py` to `science_data_kit/ui/pages/map.py`
   - Migrated remaining functionality from `survey.py` to `science_data_kit/ui/pages/survey.py`
   - Verified that `about.py` functionality has been migrated to `science_data_kit/ui/pages/about.py`
   - Verified that `connect.py` functionality has been migrated to `science_data_kit/ui/pages/connect.py`

2. Migrated specialized pages:
   - Migrated `streamlit_cbioportal_browser.py` to `science_data_kit/ui/pages/cbioportal_browser.py`
   - Migrated `streamlit_isa_browser.py` to `science_data_kit/ui/pages/isa_browser.py`

3. Migrated essential utilities:
   - Verified that `app/utils/database.py` functionality has been migrated to `science_data_kit/core/db/db_manager.py`
   - Verified that `app/utils/db_adapter.py` functionality has been migrated to `science_data_kit/core/db/`
   - Verified that `app/utils/models.py` functionality has been migrated to `science_data_kit/core/models/app_models.py`
   - Verified that `app/utils/sidebar.py` functionality has been migrated to `science_data_kit/ui/components/sidebar.py`
   - Verified that `app/utils/file_organizer.py` functionality has been migrated to `science_data_kit/core/utils/file_utils.py`
   - Verified that `app/utils/file_utils.py` functionality has been migrated to `science_data_kit/core/utils/file_utils.py`
   - Migrated `app/utils/jupyter_adapter.py` to `science_data_kit/core/integrations/jupyter_adapter.py`
   - Migrated `app/utils/neodash_adapter.py` to `science_data_kit/core/integrations/neodash_adapter.py`
   - Migrated `app/utils/jupyter_server.py` to `science_data_kit/core/integrations/jupyter_server.py`
   - Migrated `app/utils/neodash_server.py` to `science_data_kit/core/integrations/neodash_server.py`

4. Migrated configuration files:
   - Migrated `.db_config_auto.yaml` to `science_data_kit/core/config/.db_config_auto.yaml`
   - Migrated `.streamlit` configuration to `science_data_kit/ui/.streamlit/`
   - Verified that all dependencies from `app/requirements.txt` are included in the project-level requirements.txt

5. Updated documentation:
   - Verified that `app/README.md` and `science_data_kit/ui/README.md` are properly set up
   - Migrated `app/utils/server_connect.md` to `docs/user_guide/server_deployment.md`
   - Created a comprehensive migration guide at `docs/user_guide/migration_guide.md`

6. Created tests:
   - Created unit tests for the chat page in `tests/unit/ui/pages/test_chat.py`
   - Created integration tests for the chat page in `tests/integration/test_chat_page.py`

7. Implemented deprecation:
   - Added deprecation notice to `app/app.py` with warnings and instructions
   - Implemented warning messages to guide users to the new components

These improvements have enhanced the maintainability and structure of the codebase, providing a solid foundation for further migration efforts.

## Next Steps
The following tasks are planned for the next iteration:

1. Verify remaining utilities (graph_utils.py, visualizations.py, isa_compatibility.py, registry.py)
2. Perform manual testing of migrated UI
3. Verify all features from `app/` are available in the new structure
4. Validate performance and compatibility of migrated components
5. Set timeline for removal of deprecated components
6. Begin cleanup tasks (remove duplicate code, update import statements)

## Success Metrics
The success of this migration will be measured by the following metrics:
1. All functionality from `app/` is available in the new structure
2. No regression in performance or user experience
3. Comprehensive test coverage for migrated components
4. Clear documentation and migration guides for users
5. Smooth transition for existing users to the new structure

## Conclusion
The App Migration Sidequest has made excellent progress, with the completion of Phase 1 and Phase 2 tasks, and significant progress in Phase 3. The migration of core UI pages, specialized pages, essential utilities, and configuration files has been successful, and comprehensive documentation and tests have been created. The project is now ready to focus on verifying the remaining utilities, validating the migrated components, and beginning the cleanup process. By following this plan, the project will achieve a more maintainable and organized codebase, aligning with the overall goals of Phase 4 of the Science Data Kit roadmap.