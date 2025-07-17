# Science Data Kit (SDK) Plugin Architecture Roadmap - Version 02

## Overview
This roadmap outlines a comprehensive plan for refactoring the Science Data Kit's connection system to create a consistent, extensible plugin architecture. The goal is to establish clear boundaries between core functionality, protocols, and provider-specific implementations while reducing redundancy and improving maintainability.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2025-07-25 | Initial version of Plugin Architecture roadmap |
| 01 | 2025-07-26 | Implemented Phase 1 core components, updated status and next steps |
| 02 | 2025-07-27 | Implemented unit tests for core protocols, created documentation, started Phase 2 with plugins directory structure |

## Background
The Science Data Kit currently has mixed provider implementations with inconsistent connection management. Some providers use SDKs (Dropbox), others use APIs (msgraph), and there's redundancy in the codebase. The current architecture lacks clear separation between protocols, capabilities, and implementations, making it difficult to add new data sources and maintain existing ones.

## Goals
1. Create a consistent, extensible plugin architecture for data connections
2. Establish clear boundaries between core functionality, protocols, and provider-specific implementations
3. Reduce redundancy and improve maintainability
4. Standardize plugin structure and configuration
5. Maintain backward compatibility where possible
6. Enable easy addition of new data sources

## Current Status
The Plugin Architecture implementation has made significant progress with the completion of Phase 1 core components and the start of Phase 2. The following components have been implemented:

1. **Core Protocol System (Completed)**
   - Created base protocol classes in `core/connections/protocols/`
   - Implemented capability mixins in `core/connections/capabilities/`
   - Defined authentication strategies in `core/connections/auth/`
   - Moved `core/providers/abstract_providers.py` → `core/connections/protocols/` (as compatibility layer)
   - Created plugin registry and connection manager
   - Implemented unit tests for core protocol classes
   - Created documentation for protocol and capability interfaces

2. **Plugin Standardization (In Progress)**
   - Created `plugins/` directory structure
   - Created plugin package hierarchy for cloud storage, databases, and local plugins
   - Next steps: Implement standardized plugin interfaces and refactor existing providers

## Implementation Details

### Architecture Overview

```
science_data_kit/
├── core/
│   ├── connections/
│   │   ├── __init__.py
│   │   ├── manager.py              # Central connection manager
│   │   ├── registry.py             # Plugin registry
│   │   ├── protocols/              # Base protocol classes
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # ConnectionProtocol class
│   │   │   ├── filesystem.py      # FilesystemProtocol
│   │   │   ├── database.py        # DatabaseProtocol
│   │   │   ├── api.py            # APIProtocol
│   │   │   ├── object_storage.py  # ObjectStorageProtocol
│   │   │   └── abstract_providers.py  # Compatibility layer
│   │   ├── capabilities/          # Capability mixins
│   │   │   ├── __init__.py
│   │   │   ├── browsable.py
│   │   │   ├── queryable.py
│   │   │   ├── searchable.py
│   │   │   ├── streamable.py
│   │   │   └── versionable.py
│   │   └── auth/                  # Authentication strategies
│   │       ├── __init__.py
│   │       ├── oauth2.py
│   │       ├── api_key.py
│   │       └── credentials.py
│   └── tests/
│       └── core/
│           └── connections/
│               └── protocols/
│                   ├── test_base.py
│                   └── test_api.py

plugins/                           # All external connections
├── __init__.py
├── cloud_storage/
│   ├── __init__.py
│   ├── dropbox/
│   │   ├── __init__.py
│   ├── google_drive/
│   │   ├── __init__.py
│   └── microsoft365/
│       ├── __init__.py
├── databases/
│   ├── __init__.py
│   ├── neo4j/
│   │   ├── __init__.py
│   ├── postgresql/
│   │   ├── __init__.py
│   └── mongodb/
│       ├── __init__.py
└── local/
    ├── __init__.py
    └── filesystem/
        ├── __init__.py
```

### Phase 1: Core Protocol System (Completed)

**Objective**: Establish the foundation for all connections

**Tasks**:
- ✅ Create base protocol classes in `core/connections/protocols/`
- ✅ Implement capability mixins in `core/connections/capabilities/`
- ✅ Define authentication strategies in `core/connections/auth/`
- ✅ Move `core/providers/abstract_providers.py` → `core/connections/protocols/` (as compatibility layer)
- ✅ Create plugin registry in `core/connections/registry.py`
- ✅ Implement connection manager in `core/connections/manager.py`
- ✅ Implement unit tests for core protocol classes
- ✅ Document protocol and capability interfaces

**Implementation Details**:

The core protocol system has been implemented with the following components:

1. **ConnectionProtocol**: Base abstract class that all connection protocols must implement, defining methods for connecting, disconnecting, and testing connections.

2. **Specific Protocol Classes**:
   - **FilesystemProtocol**: For filesystem-like connections
   - **DatabaseProtocol**: For database connections
   - **APIProtocol**: For API-based connections
   - **ObjectStorageProtocol**: For object storage services like S3

3. **Capability Mixins**:
   - **Browsable**: For connections that support directory/content listing
   - **Queryable**: For connections that support query execution
   - **Searchable**: For connections that support search functionality
   - **Streamable**: For connections that support streaming data
   - **Versionable**: For connections that support versioning of resources

4. **Authentication Strategies**:
   - **OAuth2Mixin**: For connections that use OAuth2 authentication
   - **APIKeyMixin**: For connections that use API key authentication
   - **CredentialsMixin**: For connections that use username/password credentials

5. **Plugin Registry**: Manages the registration and retrieval of connection plugins.

6. **Connection Manager**: Provides a high-level interface for managing connections, including creation, configuration, and lifecycle management.

7. **Unit Tests**: Comprehensive tests for the base protocol class and API protocol class, with mock implementations for testing.

8. **Documentation**: Detailed documentation for protocol classes and capability mixins, including usage examples and best practices.

### Phase 2: Plugin Standardization (In Progress)

**Objective**: Refactor existing providers into plugins

**Tasks**:
- ✅ Create `plugins/` directory structure
- ✅ Create plugin package hierarchy for cloud storage, databases, and local plugins
- ⬜ Define plugin configuration schema
- ⬜ Implement standardized plugin interfaces
- ⬜ Refactor existing providers into plugins
- ⬜ Migrate `science_data_kit_extensions/dropbox/` → `plugins/cloud_storage/dropbox/`
- ⬜ Migrate `science_data_kit_extensions/msgraph/` → `plugins/cloud_storage/microsoft365/`
- ⬜ Split `core/providers/storage/` between protocols and plugins
- ⬜ Implement comprehensive tests for each plugin
- ⬜ Create plugin documentation template
- ⬜ Document migration process for existing code

**Implementation Details**:

The plugin directory structure has been created with the following organization:

1. **Top-level Plugins Directory**: Contains all plugin packages.

2. **Plugin Categories**:
   - **cloud_storage**: For cloud storage plugins like Dropbox, Google Drive, and Microsoft 365.
   - **databases**: For database plugins like Neo4j, PostgreSQL, and MongoDB.
   - **local**: For local data source plugins like the filesystem.

3. **Specific Plugin Directories**: Each plugin has its own directory with an `__init__.py` file.

The next steps in Phase 2 include defining a standardized plugin configuration schema, implementing plugin interfaces, and refactoring existing providers into the new plugin structure.

### Phase 3: Connection Manager (Planned)

**Objective**: Unified connection management

**Tasks**:
- ✅ Implement connection manager in `core/connections/manager.py`
- ✅ Create plugin registry in `core/connections/registry.py`
- ✅ Implement auto-discovery system for plugins
- ⬜ Add configuration validation
- ⬜ Create connection lifecycle management
- ⬜ Implement connection pooling
- ⬜ Add comprehensive tests for connection manager
- ⬜ Document connection manager API
- ⬜ Create migration guide for existing connection code

### Phase 4: UI Integration (Planned)

**Objective**: Dynamic UI based on available plugins

**Tasks**:
- ⬜ Create connection UI generator
- ⬜ Implement dynamic forms based on plugin configuration
- ⬜ Add capability-based feature display
- ⬜ Create connection status indicators
- ⬜ Implement plugin management UI
- ⬜ Add comprehensive UI tests
- ⬜ Document UI integration patterns
- ⬜ Create user guide for connection management

### Technical Implementation Details

#### Plugin System Architecture

The plugin system follows a composition-based design:

```
Connection = Protocol + Capabilities + DataTypes + Authentication
```

Each plugin declares its protocol (API, filesystem, database), capabilities (browsable, searchable, etc.), supported data types (files, folders, tables, etc.), and authentication method (OAuth2, API key, credentials).

#### Plugin Registration and Discovery

Plugins are registered with the PluginRegistry, which maintains a mapping of plugin types to plugin classes and instances. The registry also provides methods for discovering plugins from packages, allowing for automatic registration of plugins.

```python
# Example plugin registration
from science_data_kit.core.connections.registry import register_plugin, PluginCategory
from science_data_kit.core.connections.protocols import FilesystemProtocol
from science_data_kit.core.connections.capabilities import Browsable, Searchable

class MyFileSystemPlugin(FilesystemProtocol, Browsable, Searchable):
    """My custom filesystem plugin."""
    
    # Implementation details...

# Register the plugin
register_plugin(PluginCategory.FILESYSTEM, "MyFileSystem", MyFileSystemPlugin)
```

#### Connection Management

The ConnectionManager provides a high-level interface for managing connections, including creation, configuration, and lifecycle management. It uses the PluginRegistry to create and manage plugin instances.

```python
# Example connection management
from science_data_kit.core.connections.manager import manager

# Create a connection
connection = manager.create_connection(
    "my_connection",
    "filesystem",
    "MyFileSystem",
    {"param": "value"}
)

# Connect
manager.connect("my_connection")

# Use the connection
files = connection.list_directory("/")

# Disconnect
manager.disconnect("my_connection")
```

### Success Metrics

The success of the plugin architecture will be measured by:

1. **Reduced code duplication**
   - 80% reduction in duplicated authentication code
   - 70% reduction in duplicated file operation code
   - 90% standardization of error handling

2. **Improved extensibility**
   - New plugin implementation time reduced by 50%
   - Plugin configuration time reduced by 70%
   - Zero changes required to core code when adding new plugins

3. **Enhanced user experience**
   - Consistent UI for all connection types
   - Dynamic UI based on plugin capabilities
   - Improved error messages and recovery options

4. **Backward compatibility**
   - All existing functionality preserved
   - Minimal changes required for existing client code
   - Clear migration path for custom extensions

### Risk Mitigation

1. **Breaking changes to existing code**
   - Mitigation: Create compatibility layer in `core/providers/` that maps old imports to new plugins
   - Mitigation: Support old configuration format with deprecation warnings
   - Mitigation: Provide migration script for existing configurations

2. **Performance degradation**
   - Mitigation: Benchmark existing providers before refactoring
   - Mitigation: Implement performance tests for new plugin system
   - Mitigation: Optimize critical paths based on profiling results

3. **Increased complexity**
   - Mitigation: Comprehensive documentation of plugin architecture
   - Mitigation: Example implementations for common use cases
   - Mitigation: Clear guidelines for plugin development

### Resource Requirements

- **Phase 1**: 1 senior developer, 2 weeks (Completed)
- **Phase 2**: 1 senior developer, 2 weeks (In Progress)
- **Phase 3**: 1 senior developer, 2 weeks (Planned)
- **Phase 4**: 1 senior developer + 1 UI developer, 2 weeks (Planned)

### Testing Strategy

1. **Unit Tests**
   - Test each protocol implementation
   - Test capability mixins in isolation
   - Test plugin loading mechanism

2. **Integration Tests**
   - Test full connection lifecycle
   - Test capability detection
   - Test UI generation

3. **Plugin Tests**
   - Each plugin must include:
     - Connection tests
     - Capability tests
     - Error handling tests

### Migration Strategy

1. **Breaking Changes**
   - Import paths will change:
     - `from science_data_kit.core.providers.storage.dropbox_provider import DropboxProvider`
     - Becomes: `from science_data_kit.plugins.cloud_storage.dropbox import DropboxPlugin`
   - Configuration format changes:
     - Current: Provider-specific configurations
     - New: Standardized plugin configuration schema

2. **Backwards Compatibility**
   - Create compatibility layer in `core/providers/` that maps old imports to new plugins
   - Support old configuration format with deprecation warnings
   - Provide migration script for existing configurations

## Next Steps

1. **Complete Phase 2: Plugin Standardization**
   - Define plugin configuration schema
   - Implement standardized plugin interfaces
   - Create a template plugin implementation
   - Refactor existing providers into plugins, starting with Dropbox

2. **Enhance Testing**
   - Create tests for remaining protocol classes (DatabaseProtocol, FilesystemProtocol, ObjectStorageProtocol)
   - Implement tests for capability mixins
   - Add integration tests for the plugin registry and connection manager

3. **Improve Documentation**
   - Create a plugin development guide
   - Document the migration process for existing providers
   - Update user documentation with new connection management features

## Approval

- [ ] Architecture review completed
- [ ] Resource allocation approved
- [ ] Timeline approved
- [ ] Success metrics approved

## Reviewers

- [ ] Lead Developer
- [ ] UX Designer
- [ ] Product Manager
- [ ] QA Lead