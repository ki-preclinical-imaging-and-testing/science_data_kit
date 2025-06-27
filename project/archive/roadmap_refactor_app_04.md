# Science Data Kit (SDK) Application Refactoring Roadmap - Phase 1 Progress Update

## Overview

This document builds upon the progress outlined in `roadmap_refactor_app_03.md` and provides an update on the refactoring of the Streamlit application components of the Science Data Kit (SDK). This update focuses on the progress made in moving core functionality to the `science_data_kit` package structure and identifies the next steps in the refactoring process.

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

### 2. UI Component Refactoring

#### 2.1 UI Framework

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create UI base module | High | To Do | Create science_data_kit.ui.__init__.py with common imports |
| Create UI config module | High | To Do | Create science_data_kit.ui.config.py for UI configuration |
| Create UI state management | High | To Do | Create science_data_kit.ui.state.py for session state management |

#### 2.2 UI Components

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Refactor sidebar.py | High | To Do | Move to science_data_kit.ui.components.sidebar |
| Create database sidebar component | Medium | To Do | Extract from sidebar.py to science_data_kit.ui.components.database_sidebar |
| Create jupyter sidebar component | Medium | To Do | Extract from sidebar.py to science_data_kit.ui.components.jupyter_sidebar |
| Create neo4j connector component | Medium | To Do | Extract from sidebar.py to science_data_kit.ui.components.neo4j_connector |
| Create neodash sidebar component | Medium | To Do | Extract from sidebar.py to science_data_kit.ui.components.neodash_sidebar |
| Create schema widget component | Medium | To Do | Extract from sidebar.py to science_data_kit.ui.components.schema_widget |
| Create settings sidebar component | Medium | To Do | Extract from sidebar.py to science_data_kit.ui.components.settings_sidebar |
| Refactor menu.py | Medium | To Do | Move to science_data_kit.ui.components.menu |

## Current Issues and Challenges

During the refactoring process, we've encountered several issues that need to be addressed:

1. **Module Import Issues**: The app was failing with a `ModuleNotFoundError: No module named 'science_data_kit.core.db.db_manager'` error. This has been fixed by creating the missing module and moving the code from the original location.

2. **Node Class Definition Conflicts**: After fixing the import issue, we're now seeing a `NodeClassAlreadyDefined` error related to the `Folder` class. This suggests there might be conflicts in how node classes are defined across different modules.

3. **Dependency Management**: We need to ensure that all dependencies are properly managed and that the app can find all the required modules.

## Next Steps

### 1. Resolve Node Class Definition Conflicts

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Investigate NodeClassAlreadyDefined error | High | To Do | Identify where the Folder class is being defined multiple times |
| Refactor registry_utils.py | High | To Do | Ensure node classes are defined only once |
| Update import statements | High | To Do | Make sure imports are consistent across the codebase |

### 2. Continue UI Framework Implementation

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create UI base module | High | To Do | Create science_data_kit.ui.__init__.py with common imports |
| Create UI config module | High | To Do | Create science_data_kit.ui.config.py for UI configuration |
| Create UI state management | High | To Do | Create science_data_kit.ui.state.py for session state management |

### 3. Implement UI Components

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Refactor sidebar.py | High | To Do | Move to science_data_kit.ui.components.sidebar |
| Create database sidebar component | Medium | To Do | Extract from sidebar.py to science_data_kit.ui.components.database_sidebar |
| Create jupyter sidebar component | Medium | To Do | Extract from sidebar.py to science_data_kit.ui.components.jupyter_sidebar |

## Implementation Plan

### Phase 1: Resolve Current Issues (Week 1)

1. Fix Node Class Definition Conflicts
   - Investigate where the Folder class is being defined multiple times
   - Refactor registry_utils.py to ensure node classes are defined only once
   - Update import statements to ensure consistency

2. Complete Core Functionality Refactoring
   - Refactor visualizations.py to science_data_kit.core.utils.visualization_utils
   - Refactor file_utils.py to science_data_kit.core.utils.file_utils
   - Refactor isa_compatibility.py to science_data_kit.core.utils.isa_utils

### Phase 2: UI Framework Implementation (Week 2)

1. Create UI Base Modules
   - science_data_kit.ui.__init__.py
   - science_data_kit.ui.config.py
   - science_data_kit.ui.state.py

2. Create UI Adapter Modules
   - science_data_kit.ui.adapters.__init__.py
   - science_data_kit.ui.adapters.page_adapter.py
   - science_data_kit.ui.adapters.component_adapter.py

### Phase 3: UI Components Implementation (Week 3)

1. Refactor Sidebar Components
   - science_data_kit.ui.components.database_sidebar.py
   - science_data_kit.ui.components.jupyter_sidebar.py
   - science_data_kit.ui.components.neo4j_connector.py
   - science_data_kit.ui.components.neodash_sidebar.py
   - science_data_kit.ui.components.schema_widget.py
   - science_data_kit.ui.components.settings_sidebar.py

2. Refactor Menu and App
   - science_data_kit.ui.app.py
   - science_data_kit.ui.components.menu.py

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

The refactoring of the Science Data Kit application is progressing, with the core functionality being moved to the new package structure. We've successfully addressed the immediate issue with the missing db_manager module, but we've encountered new challenges with node class definitions that need to be resolved. The next steps will focus on resolving these issues and continuing with the UI framework and component implementation.