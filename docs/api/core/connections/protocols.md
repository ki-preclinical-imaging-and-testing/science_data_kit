# Protocol Classes

## Overview

Protocol classes define the interface for different types of connections in the Science Data Kit. They provide a consistent way to interact with various data sources, regardless of the underlying implementation details.

## Base Protocol

The `ConnectionProtocol` class is the base class for all connection protocols. It defines the basic methods and properties that all connections must implement.

```python
from science_data_kit.core.connections.protocols import ConnectionProtocol

class MyConnectionProtocol(ConnectionProtocol):
    def connect(self, config):
        # Implementation
        pass
    
    def disconnect(self):
        # Implementation
        pass
    
    def test_connection(self):
        # Implementation
        return True
    
    @property
    def connection_type(self):
        return "my_connection_type"
```

### Methods

- `connect(config)`: Establishes a connection with the service using the provided configuration.
- `disconnect()`: Cleans up the connection.
- `test_connection()`: Verifies that the connection is working.
- `get_capabilities()`: Returns a dictionary of capabilities supported by the connection.
- `get_metadata()`: Returns metadata about the connection.

### Properties

- `connection_type`: Returns the type of connection (e.g., "filesystem", "api", "database").
- `is_connected`: Returns whether the connection is currently established.

## Specific Protocol Classes

### APIProtocol

The `APIProtocol` class is used for connections to API-based data sources. It extends the base `ConnectionProtocol` with methods specific to API interactions.

```python
from science_data_kit.core.connections.protocols import APIProtocol

class MyAPIProtocol(APIProtocol):
    # Implement required methods
    
    def list_resources(self, resource_type):
        # Implementation
        return []
    
    def get_resource(self, resource_type, resource_id):
        # Implementation
        return {}
    
    def execute_request(self, endpoint, method="GET", params=None, data=None, headers=None):
        # Implementation
        return {}
    
    def get_data_as_dataframe(self, resource_type, query_params=None):
        # Implementation
        import pandas as pd
        return pd.DataFrame()
```

#### Methods

- `list_resources(resource_type)`: Lists resources of a specific type.
- `get_resource(resource_type, resource_id)`: Gets a specific resource.
- `execute_request(endpoint, method, params, data, headers)`: Executes a request to the API.
- `get_data_as_dataframe(resource_type, query_params)`: Gets data from the API as a pandas DataFrame.

### DatabaseProtocol

The `DatabaseProtocol` class is used for connections to database systems. It extends the base `ConnectionProtocol` with methods specific to database interactions.

```python
from science_data_kit.core.connections.protocols import DatabaseProtocol

class MyDatabaseProtocol(DatabaseProtocol):
    # Implement required methods
    
    def execute_query(self, query, params=None):
        # Implementation
        return []
    
    def get_tables(self):
        # Implementation
        return []
    
    def get_table_schema(self, table_name):
        # Implementation
        return {}
    
    def get_data_as_dataframe(self, query_or_table, params=None):
        # Implementation
        import pandas as pd
        return pd.DataFrame()
```

#### Methods

- `execute_query(query, params)`: Executes a query on the database.
- `get_tables()`: Gets a list of tables in the database.
- `get_table_schema(table_name)`: Gets the schema for a specific table.
- `get_data_as_dataframe(query_or_table, params)`: Gets data from the database as a pandas DataFrame.

### FilesystemProtocol

The `FilesystemProtocol` class is used for connections to filesystem-like data sources. It extends the base `ConnectionProtocol` with methods specific to file operations.

```python
from science_data_kit.core.connections.protocols import FilesystemProtocol

class MyFilesystemProtocol(FilesystemProtocol):
    # Implement required methods
    
    def list_directory(self, path):
        # Implementation
        return []
    
    def get_file_metadata(self, path):
        # Implementation
        return {}
    
    def read_file(self, path):
        # Implementation
        return b""
    
    def write_file(self, path, content):
        # Implementation
        pass
    
    def delete_file(self, path):
        # Implementation
        pass
```

#### Methods

- `list_directory(path)`: Lists the contents of a directory.
- `get_file_metadata(path)`: Gets metadata for a specific file.
- `read_file(path)`: Reads the contents of a file.
- `write_file(path, content)`: Writes content to a file.
- `delete_file(path)`: Deletes a file.

### ObjectStorageProtocol

The `ObjectStorageProtocol` class is used for connections to object storage services like S3. It extends the base `ConnectionProtocol` with methods specific to object storage operations.

```python
from science_data_kit.core.connections.protocols import ObjectStorageProtocol

class MyObjectStorageProtocol(ObjectStorageProtocol):
    # Implement required methods
    
    def list_buckets(self):
        # Implementation
        return []
    
    def list_objects(self, bucket, prefix=None):
        # Implementation
        return []
    
    def get_object(self, bucket, key):
        # Implementation
        return b""
    
    def put_object(self, bucket, key, content):
        # Implementation
        pass
    
    def delete_object(self, bucket, key):
        # Implementation
        pass
```

#### Methods

- `list_buckets()`: Lists all buckets.
- `list_objects(bucket, prefix)`: Lists objects in a bucket.
- `get_object(bucket, key)`: Gets an object from a bucket.
- `put_object(bucket, key, content)`: Puts an object in a bucket.
- `delete_object(bucket, key)`: Deletes an object from a bucket.

## Creating Custom Protocols

To create a custom protocol, you can either extend one of the existing protocol classes or implement the base `ConnectionProtocol` directly. The choice depends on the type of data source you're connecting to and the operations you need to support.

```python
from science_data_kit.core.connections.protocols import ConnectionProtocol
from science_data_kit.core.connections.capabilities import Browsable, Searchable

class MyCustomProtocol(ConnectionProtocol, Browsable, Searchable):
    """My custom protocol for a specific data source."""
    
    def connect(self, config):
        # Implementation
        pass
    
    def disconnect(self):
        # Implementation
        pass
    
    def test_connection(self):
        # Implementation
        return True
    
    @property
    def connection_type(self):
        return "custom"
    
    # Implement Browsable methods
    def list_contents(self, path="/"):
        # Implementation
        return []
    
    def get_metadata(self, path):
        # Implementation
        return {}
    
    # Implement Searchable methods
    def search(self, query, path="/"):
        # Implementation
        return []
```

## Best Practices

1. **Implement all abstract methods**: Make sure to implement all abstract methods from the base protocol class and any capability mixins you include.
2. **Handle connection state**: Keep track of the connection state and raise appropriate exceptions when methods are called on a disconnected protocol.
3. **Validate configuration**: Validate the configuration in the `connect` method and raise informative exceptions if required parameters are missing or invalid.
4. **Document capabilities**: Override the `get_capabilities` method to accurately reflect the capabilities of your protocol implementation.
5. **Error handling**: Implement robust error handling and provide informative error messages.
6. **Testing**: Create comprehensive tests for your protocol implementation, including tests for error conditions and edge cases.