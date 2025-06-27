# Science Data Kit (SDK) Application Refactoring Roadmap - Phase 1 Progress Update

## Overview

This document builds upon the progress outlined in `roadmap_refactor_app_05.md` and provides an update on the refactoring of the Streamlit application components of the Science Data Kit (SDK). This update focuses on the resolution of the NodeClassAlreadyDefined error and the continued implementation of the UI framework and components.

## Progress Update

### 1. Node Class Definition Conflicts Resolution

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Consolidate Folder class definition | High | Completed | Created science_data_kit/core/models/file_models.py as single source of truth |
| Update imports in registry_utils.py | High | Completed | Now imports Folder and File from file_models.py |
| Update imports in app_models.py | High | Completed | Now imports Folder and File from file_models.py |
| Update imports in app/utils/registry.py | High | Completed | Now imports Folder and File from file_models.py |
| Add safety checks for duplicate registration | Medium | Completed | Improved register_model function to use get_registered_model |

### 2. UI Framework Implementation

#### 2.1 UI Base Modules

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update science_data_kit.ui.__init__.py | High | Completed | Added common imports and version information |
| Create science_data_kit.ui.config.py | High | Completed | Added configuration settings for UI components |
| Create science_data_kit.ui.state.py | High | Completed | Added state management utilities |

#### 2.2 UI Adapter Modules

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create science_data_kit.ui.adapters.__init__.py | High | Completed | Added package documentation |
| Create science_data_kit.ui.adapters.page_adapter.py | High | Completed | Added page adapter for dynamic page loading |
| Create science_data_kit.ui.adapters.component_adapter.py | High | Completed | Added component and database adapters |

#### 2.3 UI Components

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update science_data_kit.ui.components.__init__.py | High | Completed | Added package documentation |
| Create science_data_kit.ui.components.sidebar.py | High | Completed | Added sidebar component with various sections |
| Create database sidebar component | Medium | Completed | Implemented in sidebar.py |
| Create jupyter sidebar component | Medium | Completed | Implemented in sidebar.py |
| Create neo4j connector component | Medium | Completed | Implemented in sidebar.py |
| Create neodash sidebar component | Medium | Completed | Implemented in sidebar.py |
| Create settings sidebar component | Medium | Completed | Implemented in sidebar.py |
| Create schema widget component | Medium | To Do | Will be implemented as a separate component |

## Current Issues and Challenges

During the refactoring process, we've identified and addressed several issues:

1. **NodeClassAlreadyDefined Error**: We identified that the Folder class was being defined in multiple places:
   - app/utils/registry.py
   - science_data_kit/core/utils/registry_utils.py
   - science_data_kit/core/models/app_models.py
   
   This was causing a conflict when the app tried to register the class multiple times. We've resolved this by:
   - Creating a single source of truth in science_data_kit/core/models/file_models.py
   - Updating all modules to import from this file instead of defining the classes themselves
   - Adding safety checks to prevent duplicate registration

2. **Module Import Structure**: We've updated the import structure to reflect the new package organization. This includes updating imports in existing files to use the new module paths.

3. **Backward Compatibility**: We've ensured that the refactored code maintains backward compatibility with existing code that uses the old module structure.

## Next Steps

### 1. Continue UI Pages Implementation

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update science_data_kit.ui.pages.__init__.py | High | To Do | Add package documentation |
| Create science_data_kit.ui.pages.base_page.py | High | To Do | Create base class for pages |
| Create science_data_kit.ui.pages.connect.py | Medium | To Do | Implement connect page |
| Create science_data_kit.ui.pages.survey.py | Medium | To Do | Implement survey page |
| Create science_data_kit.ui.pages.map.py | Medium | To Do | Implement map page |
| Create science_data_kit.ui.pages.explore.py | Medium | To Do | Implement explore page |

### 2. Update Entry Point

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create science_data_kit.ui.app.py | High | To Do | Create main app entry point |
| Update run_app.py | High | To Do | Update to use the new app entry point |
| Create backward compatibility layer | Medium | To Do | Ensure existing code continues to work |

### 3. Complete Core Functionality Refactoring

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Refactor visualizations.py | Medium | To Do | Move to science_data_kit.core.utils.visualization_utils |
| Refactor file_utils.py | Medium | To Do | Merge with science_data_kit.core.utils.file_utils |
| Refactor isa_compatibility.py | Medium | To Do | Move to science_data_kit.core.utils.isa_utils |

## Implementation Plan

### Phase 1: UI Pages Implementation (Week 1)

1. Create base page class
   - Implement science_data_kit.ui.pages.base_page.py
   - Define common page functionality

2. Implement core pages
   - Implement connect.py, survey.py, map.py, and explore.py
   - Test each page to ensure it works correctly

### Phase 2: Update Entry Point (Week 2)

1. Create main app entry point
   - Implement science_data_kit.ui.app.py
   - Define app initialization and page routing

2. Update run_app.py
   - Update to use the new app entry point
   - Test the app to ensure it works correctly

3. Create backward compatibility layer
   - Ensure existing code continues to work with the new structure

### Phase 3: Complete Core Functionality Refactoring (Week 3)

1. Refactor remaining core functionality
   - Move visualizations.py to science_data_kit.core.utils.visualization_utils
   - Merge file_utils.py with science_data_kit.core.utils.file_utils
   - Move isa_compatibility.py to science_data_kit.core.utils.isa_utils

## Testing Strategy

For each refactored module:

1. Create unit tests to verify functionality
   - Test UI components in isolation
   - Test page rendering
   - Test state management

2. Create integration tests
   - Test component interactions
   - Test page navigation
   - Test data flow between components

3. Ensure backward compatibility
   - Test with existing entry points
   - Verify that all features still work

## Conclusion

The refactoring of the Science Data Kit application is progressing well. We've successfully resolved the NodeClassAlreadyDefined error by consolidating the Folder and File class definitions to a single source of truth. We've also made significant progress in implementing the UI framework and components. The next steps will focus on implementing the UI pages, updating the entry point, and completing the core functionality refactoring.