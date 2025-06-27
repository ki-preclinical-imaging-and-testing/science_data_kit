# Science Data Kit (SDK) Application Refactoring Roadmap - Phase 1

## Overview

This document outlines a focused subset of tasks for completing the application refactoring of the Science Data Kit (SDK) as specified in the "Next Steps" section of `roadmap_10.md`. The goal is to continue refactoring app code into the new package structure, refactor remaining utility functions to use the new core modules, and create a more modular UI architecture.

## Current Status

Based on a review of the codebase, significant progress has been made in refactoring the application:

- Core functionality has been moved to the `science_data_kit/core/` directory, organized into `db/`, `models/`, and `utils/` subdirectories
- UI components have been organized into `science_data_kit/ui/components/` and `science_data_kit/ui/pages/` subdirectories
- Adapter layers have been created for backward compatibility (db_adapter.py, jupyter_adapter.py, neodash_adapter.py)
- Deprecation notices have been added to legacy modules (registry.py, file_organizer.py)

However, several files still need to be refactored to complete the application restructuring.

## Refactoring Tasks

### 1. Core Functionality Refactoring

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Add deprecation notice to database.py | High | To Do | Point to science_data_kit.core.db.db_manager |
| Add deprecation notice to db_manager.py | High | To Do | Point to science_data_kit.core.db.db_manager |
| Add deprecation notice to graph_utils.py | High | To Do | Point to science_data_kit.core.db.graph_utils |
| Add deprecation notice to models.py | High | To Do | Point to science_data_kit.core.models.app_models |
| Refactor visualizations.py | Medium | To Do | Move to science_data_kit.core.utils.visualization_utils |
| Refactor file_utils.py | Medium | To Do | Merge with science_data_kit.core.utils.file_utils |
| Refactor isa_compatibility.py | Medium | To Do | Move to science_data_kit.core.utils.isa_utils |

### 2. UI Component Refactoring

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Refactor sidebar.py | High | To Do | Move to science_data_kit.ui.components.sidebar |
| Refactor about.py | Medium | To Do | Move to science_data_kit.ui.pages.about |
| Refactor app.py | High | To Do | Move to science_data_kit.ui.app |
| Refactor chat.py | Medium | To Do | Move to science_data_kit.ui.pages.chat |
| Refactor connect.py | Medium | To Do | Move to science_data_kit.ui.pages.connect |
| Refactor explore.py | Medium | To Do | Move to science_data_kit.ui.pages.explore |
| Refactor map.py | Medium | To Do | Move to science_data_kit.ui.pages.map |
| Refactor menu.py | Low | To Do | Move to science_data_kit.ui.components.menu |
| Refactor streamlit_cbioportal_browser.py | Medium | To Do | Move to science_data_kit.ui.pages.cbioportal_browser |
| Refactor streamlit_isa_browser.py | Medium | To Do | Move to science_data_kit.ui.pages.isa_browser |
| Refactor survey.py | Medium | To Do | Move to science_data_kit.ui.pages.survey |

### 3. Import Updates

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update imports in refactored UI components | High | To Do | Use the new module paths |
| Create UI adapter layer | Medium | To Do | For backward compatibility with existing code |
| Update app entry points | High | To Do | Ensure the application can still be launched |

### 4. Modular UI Architecture

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create base page class | Medium | To Do | For common page functionality |
| Create component registry | Medium | To Do | For dynamic component loading |
| Implement layout manager | Medium | To Do | For consistent UI layout |
| Create theme manager | Low | To Do | For customizable UI appearance |

## Implementation Plan

### Phase 1: Core Functionality (Week 1)

1. Add deprecation notices to remaining core modules
   - database.py
   - db_manager.py
   - graph_utils.py
   - models.py

2. Refactor remaining utility functions
   - visualizations.py
   - file_utils.py
   - isa_compatibility.py

### Phase 2: UI Components (Week 2)

1. Refactor high-priority UI components
   - sidebar.py
   - app.py

2. Create UI adapter layer for backward compatibility

3. Update app entry points to use the new module paths

### Phase 3: Remaining UI Components (Week 3)

1. Refactor medium-priority UI components
   - about.py
   - chat.py
   - connect.py
   - explore.py
   - map.py
   - streamlit_cbioportal_browser.py
   - streamlit_isa_browser.py
   - survey.py

2. Refactor low-priority UI components
   - menu.py

### Phase 4: Modular UI Architecture (Week 4)

1. Create base page class for common page functionality

2. Implement component registry for dynamic component loading

3. Create layout manager for consistent UI layout

4. Implement theme manager for customizable UI appearance

## Testing Strategy

For each refactored module:

1. Create unit tests to verify functionality
2. Ensure backward compatibility through adapter layers
3. Test the application end-to-end to verify that all features still work

## Success Criteria

The application refactoring will be considered complete when:

1. All core functionality has been moved to the appropriate modules in the science_data_kit package
2. All UI components have been moved to the appropriate modules in the science_data_kit package
3. Deprecation notices have been added to all legacy modules
4. The application can be launched and all features work as expected
5. Unit tests pass for all refactored modules

## Next Steps After Completion

1. Enhance code standards compliance
   - Apply Black and isort formatting to all Python files
   - Add type hints to all modules
   - Add docstrings to all functions and classes

2. Expand testing infrastructure
   - Create additional unit tests
   - Add integration tests
   - Implement continuous integration

3. Improve documentation
   - Update documentation to reflect the new architecture
   - Create tutorials and examples
   - Document the adapter pattern and its benefits