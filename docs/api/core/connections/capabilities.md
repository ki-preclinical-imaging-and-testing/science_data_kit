# Capability Mixins

## Overview

Capability mixins define specific functionalities that can be added to connection protocols. They allow for a modular approach to defining connection capabilities, where protocols can include only the capabilities they support.

## Available Capabilities

### Browsable

The `Browsable` mixin is for connections that support directory/content listing and navigation.

```python
from science_data_kit.core.connections.protocols import ConnectionProtocol
from science_data_kit.core.connections.capabilities import Browsable

class MyBrowsableConnection(ConnectionProtocol, Browsable):
    # Implement ConnectionProtocol methods
    
    # Implement Browsable methods
    def list_contents(self, path="/"):
        """List contents at the given path."""
        # Implementation
        return [
            {"name": "file1.txt", "type": "file", "size": 1024},
            {"name": "folder1", "type": "directory"}
        ]
    
    def get_metadata(self, path):
        """Get metadata for a specific item."""
        # Implementation
        return {"name": "file1.txt", "type": "file", "size": 1024, "modified": "2025-07-26T12:00:00Z"}
```

#### Methods

- `list_contents(path)`: Lists the contents at the given path.
- `get_metadata(path)`: Gets metadata for a specific item.

### Queryable

The `Queryable` mixin is for connections that support query execution, such as databases or APIs with query capabilities.

```python
from science_data_kit.core.connections.protocols import ConnectionProtocol
from science_data_kit.core.connections.capabilities import Queryable

class MyQueryableConnection(ConnectionProtocol, Queryable):
    # Implement ConnectionProtocol methods
    
    # Implement Queryable methods
    def execute_query(self, query, params=None):
        """Execute a query."""
        # Implementation
        return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    
    def get_query_schema(self):
        """Get the schema for queries."""
        # Implementation
        return {
            "tables": ["users", "posts"],
            "fields": {
                "users": ["id", "name", "email"],
                "posts": ["id", "title", "content", "user_id"]
            }
        }
    
    def get_query_result_as_dataframe(self, query, params=None):
        """Get query results as a pandas DataFrame."""
        # Implementation
        import pandas as pd
        return pd.DataFrame([{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}])
```

#### Methods

- `execute_query(query, params)`: Executes a query with optional parameters.
- `get_query_schema()`: Gets the schema for queries.
- `get_query_result_as_dataframe(query, params)`: Gets query results as a pandas DataFrame.

### Searchable

The `Searchable` mixin is for connections that support search functionality.

```python
from science_data_kit.core.connections.protocols import ConnectionProtocol
from science_data_kit.core.connections.capabilities import Searchable

class MySearchableConnection(ConnectionProtocol, Searchable):
    # Implement ConnectionProtocol methods
    
    # Implement Searchable methods
    def search(self, query, path="/"):
        """Search for items matching the query."""
        # Implementation
        return [
            {"name": "file1.txt", "type": "file", "path": "/file1.txt"},
            {"name": "file2.txt", "type": "file", "path": "/folder1/file2.txt"}
        ]
    
    def get_search_capabilities(self):
        """Get the search capabilities."""
        # Implementation
        return {
            "supports_wildcards": True,
            "supports_regex": False,
            "max_results": 100
        }
```

#### Methods

- `search(query, path)`: Searches for items matching the query.
- `get_search_capabilities()`: Gets the search capabilities.

### Streamable

The `Streamable` mixin is for connections that support streaming data.

```python
from science_data_kit.core.connections.protocols import ConnectionProtocol
from science_data_kit.core.connections.capabilities import Streamable

class MyStreamableConnection(ConnectionProtocol, Streamable):
    # Implement ConnectionProtocol methods
    
    # Implement Streamable methods
    def open_stream(self, path, mode="r"):
        """Open a stream to the specified path."""
        # Implementation
        return open(path, mode)
    
    def close_stream(self, stream):
        """Close a stream."""
        # Implementation
        stream.close()
    
    def read_stream(self, stream, size=None):
        """Read from a stream."""
        # Implementation
        return stream.read(size)
    
    def write_stream(self, stream, data):
        """Write to a stream."""
        # Implementation
        stream.write(data)
```

#### Methods

- `open_stream(path, mode)`: Opens a stream to the specified path.
- `close_stream(stream)`: Closes a stream.
- `read_stream(stream, size)`: Reads from a stream.
- `write_stream(stream, data)`: Writes to a stream.

### Versionable

The `Versionable` mixin is for connections that support versioning of resources.

```python
from science_data_kit.core.connections.protocols import ConnectionProtocol
from science_data_kit.core.connections.capabilities import Versionable

class MyVersionableConnection(ConnectionProtocol, Versionable):
    # Implement ConnectionProtocol methods
    
    # Implement Versionable methods
    def get_versions(self, path):
        """Get all versions of a resource."""
        # Implementation
        return [
            {"version": "v1", "modified": "2025-07-25T12:00:00Z"},
            {"version": "v2", "modified": "2025-07-26T12:00:00Z"}
        ]
    
    def get_version(self, path, version):
        """Get a specific version of a resource."""
        # Implementation
        return {"content": b"Version content", "metadata": {"version": version}}
    
    def create_version(self, path, content=None):
        """Create a new version of a resource."""
        # Implementation
        return {"version": "v3", "modified": "2025-07-27T12:00:00Z"}
```

#### Methods

- `get_versions(path)`: Gets all versions of a resource.
- `get_version(path, version)`: Gets a specific version of a resource.
- `create_version(path, content)`: Creates a new version of a resource.

## Combining Capabilities

One of the strengths of the capability mixin approach is the ability to combine multiple capabilities in a single connection protocol. This allows for creating rich, feature-full connections that can support a variety of operations.

```python
from science_data_kit.core.connections.protocols import FilesystemProtocol
from science_data_kit.core.connections.capabilities import Browsable, Searchable, Versionable

class MyAdvancedFilesystem(FilesystemProtocol, Browsable, Searchable, Versionable):
    """A filesystem protocol with browsing, searching, and versioning capabilities."""
    
    # Implement FilesystemProtocol methods
    
    # Implement Browsable methods
    def list_contents(self, path="/"):
        # Implementation
        pass
    
    def get_metadata(self, path):
        # Implementation
        pass
    
    # Implement Searchable methods
    def search(self, query, path="/"):
        # Implementation
        pass
    
    def get_search_capabilities(self):
        # Implementation
        pass
    
    # Implement Versionable methods
    def get_versions(self, path):
        # Implementation
        pass
    
    def get_version(self, path, version):
        # Implementation
        pass
    
    def create_version(self, path, content=None):
        # Implementation
        pass
```

## Implementing Custom Capabilities

You can also create your own capability mixins to define custom functionality for your connections.

```python
class Compressible:
    """Mixin for connections that support compression."""
    
    def compress(self, path, compression_type="zip"):
        """Compress a file or directory."""
        raise NotImplementedError
    
    def decompress(self, path, target_path=None):
        """Decompress a file."""
        raise NotImplementedError
    
    def get_compression_types(self):
        """Get supported compression types."""
        raise NotImplementedError

class MyCompressibleConnection(ConnectionProtocol, Compressible):
    # Implement ConnectionProtocol methods
    
    # Implement Compressible methods
    def compress(self, path, compression_type="zip"):
        # Implementation
        pass
    
    def decompress(self, path, target_path=None):
        # Implementation
        pass
    
    def get_compression_types(self):
        # Implementation
        return ["zip", "gzip", "tar"]
```

## Best Practices

1. **Implement all methods**: When including a capability mixin, make sure to implement all its methods.
2. **Update capabilities dictionary**: Override the `get_capabilities` method to include the capabilities provided by the mixins.
3. **Handle unsupported operations**: If a capability method is not fully supported in certain contexts, raise an appropriate exception with a clear message.
4. **Document capabilities**: Clearly document which capabilities are supported and any limitations or special behaviors.
5. **Test capabilities**: Create tests for each capability to ensure they work as expected.

## Capability Detection

The connection manager can detect and filter connections based on their capabilities:

```python
from science_data_kit.core.connections.manager import manager

# Get all connections with the Browsable capability
browsable_connections = manager.get_connections_by_capability("browsable")

# Get all connections with both Browsable and Searchable capabilities
browsable_searchable_connections = manager.get_connections_by_capabilities(["browsable", "searchable"])
```

This allows for dynamic discovery and usage of connections based on the capabilities they support, making the system more flexible and extensible.