# Science Data Kit (SDK) Application Refactoring Roadmap - Phase 1 Progress Update

## Overview

This document builds upon the progress outlined in `roadmap_refactor_app_04.md` and provides an update on the refactoring of the Streamlit application components of the Science Data Kit (SDK). This update focuses on the progress made in implementing the UI framework and components, as well as addressing the NodeClassAlreadyDefined error.

## Progress Update

### 1. Core Functionality Refactoring

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Add deprecation notice to database.py | High | Completed | Points to science_data_kit.core.db.db_manager |
| Add deprecation notice to db_manager.py | High | Completed | Points to science_data_kit.core.db.db_manager |
| Add deprecation notice to graph_utils.py | High | Completed | Points to science_data_kit.core.db.graph_utils |
| Add deprecation notice to models.py | High | Completed | Points to science_data_kit.core.models.app_models |
| Create science_data_kit.core.db.db_manager | High | Completed | Moved code from app/utils/db_manager.py |
| Refactor visualizations.py | Medium | To Do | Move to science_data_kit.core.utils.visualization_utils |
| Refactor file_utils.py | Medium | To Do | Merge with science_data_kit.core.utils.file_utils |
| Refactor isa_compatibility.py | Medium | To Do | Move to science_data_kit.core.utils.isa_utils |

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

1. **NodeClassAlreadyDefined Error**: We identified that the Folder class is being defined in multiple places:
   - app/utils/registry.py
   - science_data_kit/core/utils/registry_utils.py
   - science_data_kit/core/models/app_models.py
   
   This is causing a conflict when the app tries to register the class multiple times. The solution will involve consolidating these definitions and ensuring that the class is only registered once.

2. **Module Import Structure**: The current import structure needs to be updated to reflect the new package organization. This includes updating imports in existing files to use the new module paths.

3. **Backward Compatibility**: We need to ensure that the refactored code maintains backward compatibility with existing code that uses the old module structure.

## Next Steps

### 1. Resolve Node Class Definition Conflicts

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Consolidate Folder class definition | High | To Do | Move to a single location in science_data_kit.core.models |
| Update imports in app/survey.py | High | To Do | Update to use the new Folder class location |
| Add compatibility layer | Medium | To Do | Ensure backward compatibility for existing code |

### 2. Continue UI Pages Implementation

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update science_data_kit.ui.pages.__init__.py | High | To Do | Add package documentation |
| Create science_data_kit.ui.pages.base_page.py | High | To Do | Create base class for pages |
| Create science_data_kit.ui.pages.connect.py | Medium | To Do | Implement connect page |
| Create science_data_kit.ui.pages.survey.py | Medium | To Do | Implement survey page |
| Create science_data_kit.ui.pages.map.py | Medium | To Do | Implement map page |
| Create science_data_kit.ui.pages.explore.py | Medium | To Do | Implement explore page |

### 3. Update Entry Point

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create science_data_kit.ui.app.py | High | To Do | Create main app entry point |
| Update run_app.py | High | To Do | Update to use the new app entry point |
| Create backward compatibility layer | Medium | To Do | Ensure existing code continues to work |

## Implementation Plan

### Phase 1: Resolve Node Class Definition Conflicts (Week 1)

1. Consolidate Folder class definition
   - Move the Folder class definition to science_data_kit.core.models.file_models.py
   - Update registry_utils.py to import from file_models.py
   - Update app_models.py to import from file_models.py

2. Update imports in app/survey.py
   - Update imports to use the new Folder class location
   - Test the app to ensure it works correctly

3. Add compatibility layer
   - Add imports in app/utils/registry.py to import from the new location
   - Ensure backward compatibility for existing code

### Phase 2: UI Pages Implementation (Week 2)

1. Create base page class
   - Implement science_data_kit.ui.pages.base_page.py
   - Define common page functionality

2. Implement core pages
   - Implement connect.py, survey.py, map.py, and explore.py
   - Test each page to ensure it works correctly

### Phase 3: Update Entry Point (Week 3)

1. Create main app entry point
   - Implement science_data_kit.ui.app.py
   - Define app initialization and page routing

2. Update run_app.py
   - Update to use the new app entry point
   - Test the app to ensure it works correctly

3. Create backward compatibility layer
   - Ensure existing code continues to work with the new structure

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

The refactoring of the Science Data Kit application is progressing well. We've successfully implemented the UI framework base modules, adapter modules, and sidebar components. We've also identified the cause of the NodeClassAlreadyDefined error and have a plan to resolve it. The next steps will focus on resolving the node class definition conflicts, implementing the UI pages, and updating the entry point.