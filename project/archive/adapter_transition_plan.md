# Adapter Functions in Science Data Kit: Transition Plan

## Purpose and Usage

The adapter functions in the Science Data Kit serve as a **compatibility layer** between the old codebase and the new refactored architecture. They were added as part of a significant refactoring effort to improve code organization, maintainability, and standards compliance.

These adapters allow the application to continue functioning while the underlying code is being modernized. They essentially "translate" between old function calls and the new class-based implementations.

## Types of Adapter Functions

There are three main types of adapter functions:

### 1. Database Adapters (`db_adapter.py`)
- Bridge old `database.py` functions with the new `Neo4jManager` class
- Provide backward compatibility for database operations
- Example: `fetch_available_labels()` in the adapter calls `db_manager.fetch_labels()` in the new implementation

### 2. Server Adapters
- `jupyter_adapter.py`: Connects old Jupyter server functions with the new `JupyterManager` class
- `neodash_adapter.py`: Connects old NeoDash server functions with the new `NeoDashManager` class

### 3. ISA Compatibility Layer
- Provides alternative implementations of isatools classes for environments where isatools cannot be installed (e.g., Python 3.12+)
- Moved from `app/utils/isa_compatibility.py` to `science_data_kit/core/utils/isa_compatibility.py`

## When to Remove Them

The adapter functions are intended to be **temporary**. According to the project roadmap (roadmap_07.md), there are specific plans to:

1. Complete the adapter layer integration by updating all imports to use the new adapters
2. Eventually remove the duplicate ISA compatibility layer
3. Refactor all application code to use the new core modules directly

You should consider removing these adapters when:

1. All application code has been updated to use the new refactored modules directly
2. You no longer need to support users on older versions of the application
3. The refactoring process is complete and thoroughly tested

## Recommendation

Since you mentioned not having many users on the old version, you could consider accelerating the timeline for removing these adapters. However, I would recommend:

1. **Short-term (1-3 months)**: Keep the adapters to ensure stability while completing the refactoring
2. **Medium-term (3-6 months)**: Deprecate the adapters with warnings to any remaining users of the old API
3. **Long-term (6+ months)**: Remove the adapters completely once you're confident all code is using the new architecture

The adapters are indeed helpful in the short term as they allow for a gradual transition, but they do add complexity to the codebase that will eventually become unnecessary technical debt.