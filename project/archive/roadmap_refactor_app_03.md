# Science Data Kit (SDK) Application Refactoring Roadmap - Phase 1 Streamlit App Focus

## Overview

This document builds upon the progress outlined in `roadmap_refactor_app_02.md` and provides a more detailed plan for refactoring the Streamlit application components of the Science Data Kit (SDK). After reviewing the structure of the Streamlit app, this roadmap focuses on creating a more modular, maintainable UI architecture while ensuring backward compatibility.

## Current Application Structure

The current Streamlit application has the following structure:

1. **Entry Point**:
   - `run_app.py`: Main entry point that launches the Streamlit app using `streamlit run app/app.py`

2. **Main Application**:
   - `app/app.py`: Sets up the page configuration, initializes session state variables, loads database configuration, and sets up connections to Neo4j

3. **Navigation**:
   - `app/menu.py`: Defines the navigation menu using Streamlit's navigation component

4. **Pages**:
   - File-based pages: `connect.py`, `survey.py`, `map.py`, `explore.py`, `streamlit_isa_browser.py`
   - Function-based pages: `about.py` (contains `about()` function), `chat.py` (contains `chat()` function)

5. **Utility Components**:
   - `app/utils/sidebar.py`: Contains sidebar components for database, Jupyter, Neo4j, NeoDash, and settings
   - Other utility modules in `app/utils/` directory

6. **Adapters**:
   - `app/utils/db_adapter.py`: Adapter for database operations
   - `app/utils/jupyter_adapter.py`: Adapter for Jupyter notebook integration
   - `app/utils/neodash_adapter.py`: Adapter for NeoDash dashboard integration

## Refactoring Goals

1. Move all application code to the `science_data_kit` package structure
2. Create a more modular UI architecture with clear separation of concerns
3. Ensure backward compatibility through adapter layers
4. Improve code organization, readability, and maintainability
5. Enable easier testing and extension of the application

## Refactoring Tasks

### 1. Core Functionality Refactoring

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Add deprecation notice to database.py | High | Completed | Points to science_data_kit.core.db.db_manager |
| Add deprecation notice to db_manager.py | High | Completed | Points to science_data_kit.core.db.db_manager |
| Add deprecation notice to graph_utils.py | High | Completed | Points to science_data_kit.core.db.graph_utils |
| Add deprecation notice to models.py | High | Completed | Points to science_data_kit.core.models.app_models |
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

#### 2.3 UI Pages

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create base page class | High | To Do | Create science_data_kit.ui.pages.base_page.py |
| Refactor app.py | High | To Do | Move to science_data_kit.ui.app |
| Refactor about.py | Medium | To Do | Move to science_data_kit.ui.pages.about |
| Refactor chat.py | Medium | To Do | Move to science_data_kit.ui.pages.chat |
| Refactor connect.py | Medium | To Do | Move to science_data_kit.ui.pages.connect |
| Refactor explore.py | Medium | To Do | Move to science_data_kit.ui.pages.explore |
| Refactor map.py | Medium | To Do | Move to science_data_kit.ui.pages.map |
| Refactor streamlit_cbioportal_browser.py | Medium | To Do | Move to science_data_kit.ui.pages.cbioportal_browser |
| Refactor streamlit_isa_browser.py | Medium | To Do | Move to science_data_kit.ui.pages.isa_browser |
| Refactor survey.py | Medium | To Do | Move to science_data_kit.ui.pages.survey |

### 3. Adapter Layer

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create UI adapter module | High | To Do | Create science_data_kit.ui.adapters.__init__.py |
| Create page adapter | High | To Do | Create science_data_kit.ui.adapters.page_adapter.py |
| Create component adapter | High | To Do | Create science_data_kit.ui.adapters.component_adapter.py |
| Create layout adapter | Medium | To Do | Create science_data_kit.ui.adapters.layout_adapter.py |

### 4. Entry Point Updates

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Update run_app.py | High | To Do | Update to use science_data_kit.ui.app |
| Create backward compatibility script | Medium | To Do | Create app/app.py that imports from science_data_kit.ui.app |

### 5. Modular UI Architecture

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create component registry | Medium | To Do | For dynamic component loading |
| Implement layout manager | Medium | To Do | For consistent UI layout |
| Create theme manager | Low | To Do | For customizable UI appearance |
| Create UI event system | Low | To Do | For component communication |

## Implementation Plan

### Phase 1: UI Framework and Base Components (Week 1)

1. Create UI base module and configuration
   - science_data_kit.ui.__init__.py
   - science_data_kit.ui.config.py
   - science_data_kit.ui.state.py

2. Create base page class
   - science_data_kit.ui.pages.base_page.py

3. Create UI adapter modules
   - science_data_kit.ui.adapters.__init__.py
   - science_data_kit.ui.adapters.page_adapter.py
   - science_data_kit.ui.adapters.component_adapter.py

### Phase 2: High-Priority UI Components (Week 2)

1. Refactor sidebar.py into modular components
   - science_data_kit.ui.components.database_sidebar.py
   - science_data_kit.ui.components.jupyter_sidebar.py
   - science_data_kit.ui.components.neo4j_connector.py
   - science_data_kit.ui.components.neodash_sidebar.py
   - science_data_kit.ui.components.schema_widget.py
   - science_data_kit.ui.components.settings_sidebar.py

2. Refactor app.py and menu.py
   - science_data_kit.ui.app.py
   - science_data_kit.ui.components.menu.py

3. Update run_app.py to use the new module structure

### Phase 3: UI Pages (Week 3)

1. Refactor file-based pages
   - science_data_kit.ui.pages.connect.py
   - science_data_kit.ui.pages.survey.py
   - science_data_kit.ui.pages.map.py
   - science_data_kit.ui.pages.explore.py
   - science_data_kit.ui.pages.cbioportal_browser.py
   - science_data_kit.ui.pages.isa_browser.py

2. Refactor function-based pages
   - science_data_kit.ui.pages.about.py
   - science_data_kit.ui.pages.chat.py

### Phase 4: Advanced UI Architecture (Week 4)

1. Implement component registry
   - science_data_kit.ui.registry.py

2. Create layout manager
   - science_data_kit.ui.layout.py

3. Implement theme manager
   - science_data_kit.ui.theme.py

4. Create UI event system
   - science_data_kit.ui.events.py

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

## Migration Strategy

To ensure a smooth transition to the new architecture:

1. **Parallel Development**:
   - Keep the existing app structure working while developing the new structure
   - Use adapter layers to bridge between old and new code

2. **Incremental Refactoring**:
   - Refactor one component at a time
   - Test thoroughly after each refactoring step
   - Update documentation as components are refactored

3. **Backward Compatibility**:
   - Create compatibility scripts that import from the new structure
   - Update import statements in existing code to use the new structure

## Success Criteria

The application refactoring will be considered complete when:

1. All UI components have been moved to the appropriate modules in the science_data_kit package
2. The application can be launched using the new entry point
3. All features work as expected with the new architecture
4. Unit and integration tests pass for all refactored modules
5. Documentation has been updated to reflect the new architecture

## Conclusion

This roadmap provides a detailed plan for refactoring the Streamlit application components of the Science Data Kit. By creating a more modular UI architecture with clear separation of concerns, the application will be easier to maintain, test, and extend. The use of adapter layers will ensure backward compatibility, allowing for a smooth transition to the new architecture.

The next steps are to implement the UI framework and base components, followed by refactoring the high-priority UI components. This will establish the foundation for the new architecture and enable incremental refactoring of the remaining components.