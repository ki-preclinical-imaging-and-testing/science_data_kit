# Science Data Kit (SDK) Deprecation Plan

## Overview

This document outlines the plan for deprecating legacy components in the Science Data Kit (SDK) project. It identifies components to be deprecated, provides a timeline for deprecation, and offers migration paths for users transitioning to newer components.

## Legacy Components to Deprecate

The following components are considered legacy and are scheduled for deprecation:

### 1. `app/` Directory

The `app/` directory contains the legacy Streamlit application code that is being phased out in favor of the new `science_data_kit/ui/` directory. The following files and directories within `app/` are scheduled for deprecation:

#### Core Application Files
- `app/app.py` - Main entry point for the legacy application
- `app/menu.py` - Navigation menu for the legacy app
- `app/connect.py` - Connect page showing driver connectors
- `app/explore.py` - Explore page for data exploration
- `app/chat.py` - Chat functionality
- `app/map.py` - Map visualization functionality
- `app/about.py` - About page
- `app/survey.py` - Survey functionality
- `app/streamlit_cbioportal_browser.py` - cBioPortal browser integration
- `app/streamlit_isa_browser.py` - ISA browser integration

#### Utility Modules
- `app/utils/database.py` - Database utilities
- `app/utils/db_adapter.py` - Database adapter
- `app/utils/db_manager.py` - Database manager
- `app/utils/file_organizer.py` - File organization utilities
- `app/utils/file_utils.py` - File utilities
- `app/utils/graph_utils.py` - Graph utilities
- `app/utils/isa_compatibility.py` - ISA compatibility utilities
- `app/utils/jupyter_adapter.py` - Jupyter adapter
- `app/utils/jupyter_server.py` - Jupyter server utilities
- `app/utils/models.py` - Data models
- `app/utils/neodash_adapter.py` - NeoDash adapter
- `app/utils/neodash_server.py` - NeoDash server utilities
- `app/utils/registry.py` - Registry functionality
- `app/utils/sidebar.py` - Sidebar components
- `app/utils/visualizations.py` - Visualization utilities

#### Configuration Files
- `app/.streamlit/config.toml` - Streamlit configuration
- `app/.db_config_auto.yaml` - Automatically generated database configuration

## Deprecation Timeline

The deprecation of legacy components will follow this timeline:

1. **Phase 1: Announcement and Documentation (Current - 2023-12-31)**
   - Publish this deprecation plan
   - Add deprecation warnings to legacy components
   - Create migration guides for users

2. **Phase 2: Transition Period (2024-01-01 - 2024-06-30)**
   - Maintain both legacy and new components
   - Encourage users to migrate to new components
   - Provide support for migration issues

3. **Phase 3: Deprecation (2024-07-01 - 2024-12-31)**
   - Legacy components will be marked as deprecated
   - Warning messages will appear when using deprecated components
   - Limited support for legacy components

4. **Phase 4: Removal (2025-01-01)**
   - Legacy components will be removed from the codebase
   - Only new components will be supported

## Migration Paths

### For Users

Users of the Science Data Kit should follow these steps to migrate from legacy components to new components:

1. **Update Import Statements**
   - Replace imports from `app.utils.*` with imports from `science_data_kit.ui.*` or `science_data_kit.core.*`
   - Example:
     ```python
     # Old import
     from app.utils.database import connect_to_neo4j
     
     # New import
     from science_data_kit.core.db.neo4j_connector import connect_to_neo4j
     ```

2. **Update Configuration Files**
   - Move configuration from `app/.streamlit/config.toml` to `science_data_kit/ui/.streamlit/config.toml`
   - Move database configuration from `app/.db_config_auto.yaml` to `.db_config_auto.yaml` in the project root

3. **Update Application Entry Points**
   - Replace calls to `streamlit run app/app.py` with `streamlit run science_data_kit/ui/app.py`

4. **Update Custom Scripts**
   - Review and update any custom scripts that import from the `app` directory
   - Test thoroughly after migration

### For Developers

Developers contributing to the Science Data Kit should follow these guidelines:

1. **No New Features in Legacy Components**
   - Do not add new features to components in the `app/` directory
   - Implement all new features in the `science_data_kit/ui/` directory

2. **Bug Fixes in Legacy Components**
   - Critical bug fixes may be applied to legacy components during the transition period
   - Ensure all bug fixes are also applied to the corresponding new components

3. **Documentation Updates**
   - Update documentation to reference new components instead of legacy components
   - Add migration notes to relevant documentation

## Compatibility Layer

To ease the transition, a compatibility layer will be provided:

1. **Adapter Modules**
   - Adapter modules will be created to redirect calls from legacy components to new components
   - These adapters will issue deprecation warnings

2. **Import Aliases**
   - Import aliases will be set up to allow imports from legacy paths to resolve to new paths
   - These aliases will issue deprecation warnings

## Monitoring and Support

During the transition period, the following support will be provided:

1. **Migration Support**
   - A dedicated channel for migration support will be established
   - Regular office hours for migration assistance will be scheduled

2. **Usage Monitoring**
   - Usage of legacy components will be monitored to track migration progress
   - Targeted outreach will be conducted for users still using legacy components

3. **Feedback Collection**
   - Feedback on the migration process will be collected
   - Improvements to migration guides will be made based on feedback

## Conclusion

This deprecation plan provides a structured approach to phasing out legacy components in the Science Data Kit. By following this plan, we aim to ensure a smooth transition for users while maintaining the stability and reliability of the SDK.

The deprecation of legacy components is a necessary step in the evolution of the Science Data Kit, allowing us to focus development efforts on the new, more maintainable architecture.