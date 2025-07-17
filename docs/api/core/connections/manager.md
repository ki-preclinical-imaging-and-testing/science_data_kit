# Connection Manager API

The Connection Manager provides a central interface for managing connections in the Science Data Kit. It handles connection creation, configuration, lifecycle management, and connection pooling.

## Overview

The Connection Manager is designed to:

1. Provide a unified interface for creating and managing connections
2. Handle connection lifecycle (initialization, connection, disconnection)
3. Support connection pooling for efficient resource utilization
4. Enable discovery of connections by capability

## Basic Usage

### Creating a Connection

```python
from science_data_kit.core.connections.manager import manager

# Create a connection
connection = manager.create_connection(
    name="my_connection",
    plugin_type="api",  # or use PluginCategory.API
    plugin_name="microsoft365",
    config={
        "client_id": "your-client-id",
        "tenant_id": "your-tenant-id",
        "client_secret": "your-client-secret",
        "auth_method": "client_credentials",
        "scopes": ["https://graph.microsoft.com/.default"],
    }
)
```

### Connecting and Disconnecting

```python
# Connect to the service
manager.connect("my_connection")

# Disconnect from the service
manager.disconnect("my_connection")
```

### Getting a Connection

```python
# Get a connection by name
connection = manager.get_connection("my_connection")

# Get the configuration for a connection
config = manager.get_connection_config("my_connection")
```

### Removing a Connection

```python
# Remove a connection
manager.remove_connection("my_connection")
```

### Listing Connections

```python
# List all connections
connections = manager.list_connections()
for conn_info in connections:
    print(f"Name: {conn_info['name']}")
    print(f"Type: {conn_info['type']}")
    print(f"Connected: {conn_info['connected']}")
    print(f"Capabilities: {conn_info['capabilities']}")
```

### Finding Connections by Capability

```python
# Find connections with a specific capability
search_connections = manager.get_connection_by_capability("search")
```

### Disconnecting All Connections

```python
# Disconnect all connections
manager.disconnect_all()
```

## Connection Pooling

Connection pooling allows for efficient reuse of connections, reducing the overhead of creating new connections.

### Configuring a Connection Pool

```python
from science_data_kit.core.connections.manager import manager, ConnectionPoolConfig

# Configure a connection pool
pool_config = ConnectionPoolConfig(
    max_pool_size=10,
    min_idle=1,
    max_idle=5,
    idle_timeout=300.0,  # 5 minutes
    max_lifetime=3600.0,  # 1 hour
    connection_timeout=30.0,
    validation_interval=60.0,  # 1 minute
)

manager.configure_pool("cloud_storage", "dropbox", pool_config)
```

### Getting a Connection from a Pool

```python
# Get a connection from the pool
connection = manager.get_pooled_connection(
    "cloud_storage",
    "dropbox",
    {
        "app_key": "your-app-key",
        "app_secret": "your-app-secret",
        "refresh_token": "your-refresh-token",
        "root_path": "",
    }
)

# Use the connection
# ...

# Return the connection to the pool
manager.return_pooled_connection("cloud_storage", "dropbox", connection)
```

### Getting Pool Statistics

```python
# Get pool statistics
stats = manager.get_pool_stats("cloud_storage", "dropbox")
print(f"Idle connections: {stats['idle_connections']}")
print(f"Active connections: {stats['active_connections']}")
print(f"Max pool size: {stats['max_pool_size']}")
```

### Closing a Connection Pool

```python
# Close a connection pool
manager.close_pool("cloud_storage", "dropbox")
```

## Best Practices

1. **Use Connection Pooling**: For frequently used connections, configure and use connection pooling to improve performance.

2. **Properly Close Connections**: Always disconnect connections when they are no longer needed to free up resources.

3. **Handle Exceptions**: Wrap connection operations in try-except blocks to handle potential errors.

4. **Use Capabilities**: Use the capability system to find connections that support specific features.

5. **Validate Configurations**: Ensure that connection configurations are valid before creating connections.

6. **Monitor Pool Statistics**: Regularly check pool statistics to ensure efficient resource utilization.

## API Reference

### ConnectionManager

The main class for managing connections.

#### Methods

- `create_connection(name, plugin_type, plugin_name, config)`: Create and register a new connection.
- `get_connection(name)`: Get a connection by name.
- `get_connection_config(name)`: Get the configuration for a connection.
- `connect(name)`: Establish a connection.
- `disconnect(name)`: Disconnect a connection.
- `remove_connection(name)`: Remove a connection from the manager.
- `list_connections()`: List all connections.
- `get_connection_by_capability(capability)`: Get connections that have a specific capability.
- `disconnect_all()`: Disconnect all connections.

### ConnectionPoolConfig

Configuration for connection pooling.

#### Parameters

- `max_pool_size`: Maximum number of connections in the pool.
- `min_idle`: Minimum number of idle connections to maintain.
- `max_idle`: Maximum number of idle connections to keep.
- `idle_timeout`: Time in seconds after which idle connections are closed.
- `max_lifetime`: Maximum lifetime of a connection in seconds.
- `connection_timeout`: Timeout in seconds for connection acquisition.
- `validation_interval`: Interval in seconds for validating connections.

### Connection Pooling Methods

- `configure_pool(plugin_type, plugin_name, pool_config)`: Configure a connection pool.
- `get_pooled_connection(plugin_type, plugin_name, config)`: Get a connection from a pool.
- `return_pooled_connection(plugin_type, plugin_name, connection)`: Return a connection to a pool.
- `get_pool_stats(plugin_type, plugin_name)`: Get statistics about a connection pool.
- `close_pool(plugin_type, plugin_name)`: Close a connection pool.

## Example: Complete Connection Lifecycle

```python
from science_data_kit.core.connections.manager import manager, ConnectionPoolConfig

# Configure a connection pool
pool_config = ConnectionPoolConfig(
    max_pool_size=5,
    min_idle=1,
    max_idle=3,
    idle_timeout=60.0,
    max_lifetime=300.0,
    connection_timeout=10.0,
    validation_interval=30.0,
)

manager.configure_pool("cloud_storage", "microsoft365", pool_config)

# Configuration for the connection
config = {
    "client_id": "your-client-id",
    "tenant_id": "your-tenant-id",
    "client_secret": "your-client-secret",
    "auth_method": "client_credentials",
    "scopes": ["https://graph.microsoft.com/.default"],
}

try:
    # Get a connection from the pool
    connection = manager.get_pooled_connection("cloud_storage", "microsoft365", config)
    
    # Use the connection
    users = connection.request("GET", "/users")
    
    # Return the connection to the pool
    manager.return_pooled_connection("cloud_storage", "microsoft365", connection)
    
    # Get pool statistics
    stats = manager.get_pool_stats("cloud_storage", "microsoft365")
    print(f"Pool stats: {stats}")
    
finally:
    # Close the pool when done
    manager.close_pool("cloud_storage", "microsoft365")
```

## Migration Guide

If you're migrating from the old connection system to the new connection manager, follow these steps:

1. **Update Imports**: Change imports from specific providers to the connection manager.

   ```python
   # Old
   from science_data_kit.core.providers.storage.dropbox_provider import DropboxProvider
   
   # New
   from science_data_kit.core.connections.manager import manager
   ```

2. **Update Connection Creation**: Use the connection manager to create connections.

   ```python
   # Old
   provider = DropboxProvider(app_key="key", app_secret="secret", refresh_token="token")
   
   # New
   connection = manager.create_connection(
       name="dropbox",
       plugin_type="cloud_storage",
       plugin_name="dropbox",
       config={
           "app_key": "key",
           "app_secret": "secret",
           "refresh_token": "token",
       }
   )
   ```

3. **Update Connection Usage**: Use the connection manager to get and manage connections.

   ```python
   # Old
   provider.connect()
   files = provider.list_files("/")
   provider.disconnect()
   
   # New
   manager.connect("dropbox")
   connection = manager.get_connection("dropbox")
   files = connection.list_directory("/")
   manager.disconnect("dropbox")
   ```

4. **Consider Connection Pooling**: For frequently used connections, use connection pooling.

   ```python
   # Configure a pool
   pool_config = ConnectionPoolConfig(max_pool_size=5)
   manager.configure_pool("cloud_storage", "dropbox", pool_config)
   
   # Get a connection from the pool
   connection = manager.get_pooled_connection(
       "cloud_storage",
       "dropbox",
       config={
           "app_key": "key",
           "app_secret": "secret",
           "refresh_token": "token",
       }
   )
   
   # Use the connection
   files = connection.list_directory("/")
   
   # Return the connection to the pool
   manager.return_pooled_connection("cloud_storage", "dropbox", connection)
   ```