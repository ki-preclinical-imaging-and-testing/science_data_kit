# Science Data Kit (SDK) Plugin Architecture Roadmap - Version 00

## Overview
This roadmap outlines a comprehensive plan for refactoring the Science Data Kit's connection system to create a consistent, extensible plugin architecture. The goal is to establish clear boundaries between core functionality, protocols, and provider-specific implementations while reducing redundancy and improving maintainability.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2025-07-25 | Initial version of Plugin Architecture roadmap |

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
The Plugin Architecture roadmap has been defined but not started yet. The roadmap is divided into four phases:

1. **Phase 1: Core Protocol System** - Establish the foundation for all connections by creating base protocol classes, implementing capability mixins, and migrating existing code.
2. **Phase 2: Plugin Standardization** - Refactor existing providers into plugins with standardized interfaces and configuration.
3. **Phase 3: Connection Manager** - Implement a unified connection management system with plugin registry and auto-discovery.
4. **Phase 4: UI Integration** - Create dynamic UI components based on available plugins and their capabilities.

## Implementation Details

### Architecture Overview

```
science_data_kit/
├── core/
│   ├── connections/
│   │   ├── __init__.py
│   │   ├── manager.py              # Central connection manager
│   │   ├── registry.py             # Plugin registry
│   │   ├── config.py               # Configuration schemas
│   │   ├── protocols/              # Base protocol classes
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # BaseProtocol class
│   │   │   ├── filesystem.py      # FilesystemProtocol
│   │   │   ├── database.py        # DatabaseProtocol
│   │   │   ├── api.py            # APIProtocol
│   │   │   └── object_storage.py  # ObjectStorageProtocol
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
│   └── parsers/                   # File format parsers
│       ├── __init__.py
│       ├── base.py
│       ├── pdf.py
│       ├── excel.py
│       └── csv.py

plugins/                           # All external connections
├── __init__.py
├── cloud_storage/
│   ├── __init__.py
│   ├── dropbox/
│   │   ├── __init__.py
│   │   ├── plugin.py          # Main plugin class
│   │   ├── config.yaml        # Plugin metadata
│   │   └── requirements.txt   # Dependencies
│   ├── google_drive/
│   │   └── ... (same structure)
│   └── microsoft365/          # Renamed from msgraph
│       ├── __init__.py
│       ├── plugin.py
│       ├── config.yaml
│       ├── onedrive.py       # OneDrive-specific features
│       ├── sharepoint.py     # SharePoint features
│       └── outlook.py        # Email/calendar features
├── databases/
│   ├── neo4j/
│   ├── postgresql/
│   └── mongodb/
└── local/
    └── filesystem/
```

### Phase 1: Core Protocol System (2 weeks)

**Objective**: Establish the foundation for all connections

**Tasks**:
- Create base protocol classes in `core/connections/protocols/`
- Implement capability mixins in `core/connections/capabilities/`
- Define authentication strategies in `core/connections/auth/`
- Move `core/providers/abstract_providers.py` → `core/connections/protocols/`
- Extract interfaces from existing providers
- Create capability detection system
- Implement unit tests for core protocol classes
- Document protocol and capability interfaces

**Example Base Protocol Class**:
```python
# core/connections/protocols/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class ConnectionProtocol(ABC):
    """Base protocol all connections must implement"""
    
    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> None:
        """Establish connection with the service"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Clean up connection"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Verify connection is working"""
        pass
    
    @property
    @abstractmethod
    def connection_type(self) -> str:
        """Return the type of connection (filesystem, api, database)"""
        pass
```

**Example Capability Mixin**:
```python
# core/connections/capabilities/browsable.py
from typing import List, Dict, Any

class Browsable:
    """Mixin for connections that support directory listing"""
    
    def list_contents(self, path: str = "/") -> List[Dict[str, Any]]:
        """List contents at the given path"""
        raise NotImplementedError
    
    def get_metadata(self, path: str) -> Dict[str, Any]:
        """Get metadata for a specific item"""
        raise NotImplementedError
```

### Phase 2: Plugin Standardization (2 weeks)

**Objective**: Refactor existing providers into plugins

**Tasks**:
- Create `plugins/` directory structure
- Define plugin configuration schema
- Implement standardized plugin interfaces
- Refactor existing providers into plugins
- Migrate `science_data_kit_extensions/dropbox/` → `plugins/cloud_storage/dropbox/`
- Migrate `science_data_kit_extensions/msgraph/` → `plugins/cloud_storage/microsoft365/`
- Split `core/providers/storage/` between protocols and plugins
- Implement comprehensive tests for each plugin
- Create plugin documentation template
- Document migration process for existing code

**Example Plugin Configuration**:
```yaml
# plugins/cloud_storage/dropbox/config.yaml
plugin:
  name: "Dropbox"
  version: "1.0.0"
  description: "Dropbox cloud storage integration"
  author: "SDK Team"
  
connection:
  protocol: "api"
  capabilities:
    - browsable
    - searchable
    - versionable
  data_types:
    - files
    - folders
    
authentication:
  type: "oauth2"
  scopes:
    - "files.read"
    - "files.write"
    
dependencies:
  - "dropbox>=11.36.0"
```

**Example Plugin Interface**:
```python
# plugins/cloud_storage/dropbox/plugin.py
from science_data_kit.core.connections import ConnectionProtocol
from science_data_kit.core.connections.capabilities import Browsable, Searchable

class DropboxPlugin(ConnectionProtocol, Browsable, Searchable):
    """Dropbox cloud storage plugin"""
    
    def __init__(self):
        self.client = None
        
    def connect(self, config):
        # Implementation
        pass
```

### Phase 3: Connection Manager (2 weeks)

**Objective**: Unified connection management

**Tasks**:
- Implement connection manager in `core/connections/manager.py`
- Create plugin registry in `core/connections/registry.py`
- Implement auto-discovery system for plugins
- Add configuration validation
- Create connection lifecycle management
- Implement connection pooling
- Add comprehensive tests for connection manager
- Document connection manager API
- Create migration guide for existing connection code

**Example Connection Manager**:
```python
# core/connections/manager.py
class ConnectionManager:
    """Central manager for all connections"""
    
    def __init__(self):
        self._registry = {}
        self._active_connections = {}
    
    def register_plugin(self, plugin_class):
        """Register a new plugin"""
        pass
    
    def create_connection(self, name: str, plugin_type: str, config: dict):
        """Create and store a new connection"""
        pass
    
    def get_connection(self, name: str):
        """Retrieve an active connection"""
        pass
```

### Phase 4: UI Integration (2 weeks)

**Objective**: Dynamic UI based on available plugins

**Tasks**:
- Create connection UI generator
- Implement dynamic forms based on plugin configuration
- Add capability-based feature display
- Create connection status indicators
- Implement plugin management UI
- Add comprehensive UI tests
- Document UI integration patterns
- Create user guide for connection management

**Focus Areas**:
- Connection configuration UI that adapts to plugin requirements
- File browser that shows only relevant actions based on capabilities
- Search interface for connections with the Searchable capability
- Query builder for connections with the Queryable capability

### Technical Implementation Details

#### Plugin System Architecture

The plugin system follows a composition-based design:

```
Connection = Protocol + Capabilities + DataTypes + Authentication
```

Each plugin declares its protocol (API, filesystem, database), capabilities (browsable, searchable, etc.), supported data types (files, folders, tables, etc.), and authentication method (OAuth2, API key, credentials).

#### Microsoft Graph vs OneDrive Strategy

Microsoft Graph will remain the primary Microsoft integration because:
- It provides unified access to OneDrive, SharePoint, Outlook, Teams, and more
- Single authentication flow for all Microsoft 365 services
- More comprehensive than OneDrive SDK alone
- Already implemented in the codebase

The implementation will be renamed from "msgraph" to "microsoft365" to clarify that it includes OneDrive capabilities.

#### Complete Dropbox Plugin Example

```python
# plugins/cloud_storage/dropbox/plugin.py
from typing import List, Dict, Any
import dropbox
from dropbox.exceptions import AuthError

from science_data_kit.core.connections.protocols import APIProtocol
from science_data_kit.core.connections.capabilities import (
    Browsable, Searchable, Versionable
)
from science_data_kit.core.connections.auth import OAuth2Mixin

class DropboxPlugin(APIProtocol, OAuth2Mixin, Browsable, Searchable, Versionable):
    """
    Dropbox cloud storage plugin.
    
    Provides file storage, sharing, and collaboration features.
    """
    
    connection_type = "api"
    
    def __init__(self):
        self.client = None
        self._config = {}
    
    def connect(self, config: Dict[str, Any]) -> None:
        """Establish connection to Dropbox"""
        self._config = config
        
        # OAuth2Mixin handles token refresh
        access_token = self.get_valid_token(config)
        
        self.client = dropbox.Dropbox(
            oauth2_access_token=access_token,
            app_key=config.get('app_key'),
            app_secret=config.get('app_secret')
        )
    
    def disconnect(self) -> None:
        """Clean up Dropbox connection"""
        if self.client:
            self.client.close()
            self.client = None
    
    def test_connection(self) -> bool:
        """Verify Dropbox connection is working"""
        try:
            self.client.users_get_current_account()
            return True
        except AuthError:
            return False
    
    # Browsable implementation
    def list_contents(self, path: str = "") -> List[Dict[str, Any]]:
        """List folder contents"""
        try:
            result = self.client.files_list_folder(path)
            return [self._entry_to_dict(entry) for entry in result.entries]
        except Exception as e:
            raise ConnectionError(f"Failed to list contents: {e}")
    
    def get_metadata(self, path: str) -> Dict[str, Any]:
        """Get file/folder metadata"""
        try:
            metadata = self.client.files_get_metadata(path)
            return self._entry_to_dict(metadata)
        except Exception as e:
            raise ConnectionError(f"Failed to get metadata: {e}")
    
    # Searchable implementation
    def search(self, query: str, path: str = "") -> List[Dict[str, Any]]:
        """Search for files and folders"""
        try:
            result = self.client.files_search_v2(query, path)
            return [self._match_to_dict(match) for match in result.matches]
        except Exception as e:
            raise ConnectionError(f"Search failed: {e}")
    
    # Versionable implementation
    def get_revisions(self, path: str) -> List[Dict[str, Any]]:
        """Get file revision history"""
        try:
            revisions = self.client.files_list_revisions(path)
            return [self._revision_to_dict(rev) for rev in revisions.entries]
        except Exception as e:
            raise ConnectionError(f"Failed to get revisions: {e}")
    
    # Helper methods
    def _entry_to_dict(self, entry) -> Dict[str, Any]:
        """Convert Dropbox entry to standard format"""
        return {
            'name': entry.name,
            'path': entry.path_display,
            'type': 'folder' if isinstance(entry, dropbox.files.FolderMetadata) else 'file',
            'size': getattr(entry, 'size', None),
            'modified': getattr(entry, 'client_modified', None),
        }
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

- **Phase 1**: 1 senior developer, 2 weeks
- **Phase 2**: 1 senior developer, 2 weeks
- **Phase 3**: 1 senior developer, 2 weeks
- **Phase 4**: 1 senior developer + 1 UI developer, 2 weeks

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