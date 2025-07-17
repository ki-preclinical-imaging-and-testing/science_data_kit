# Migration Guide: From Providers to Plugins

## Overview

This guide explains how to migrate your code from the old provider-based system to the new plugin architecture in Science Data Kit. The plugin architecture provides a more consistent, extensible, and maintainable way to connect to various data sources.

## Key Changes

1. **Import Paths**: Provider imports have changed to plugin imports
2. **Configuration**: Configuration format has been standardized
3. **Connection Management**: Connection lifecycle is now more explicit
4. **Method Names**: Some method names have changed for consistency

## General Migration Pattern

### Old Provider Pattern

```python
from science_data_kit.core.providers.storage.some_provider import SomeProvider

# Create provider instance
provider = SomeProvider(config={
    "param1": "value1",
    "param2": "value2"
})

# Initialize provider
await provider.initialize()

# Use provider
result = await provider.some_method()
```

### New Plugin Pattern

```python
from science_data_kit.core.connections.manager import manager

# Get plugin instance
plugin = manager.get_plugin_instance("some_plugin")

# Connect to service
plugin.connect({
    "param1": "value1",
    "param2": "value2"
})

# Use plugin
result = plugin.some_method()
```

## Provider-Specific Migration Examples

### Local Storage Provider

#### Old Code

```python
from science_data_kit.core.providers.storage.local_storage_provider import LocalStorageProvider

# Create provider instance
provider = LocalStorageProvider(config={
    "base_path": "/path/to/data"
})

# Initialize provider
await provider.initialize()

# List files
files = await provider.list_files("/some/directory")

# Read file
content = await provider.read_file("/some/file.txt")
```

#### New Code

```python
from science_data_kit.core.connections.manager import manager

# Get plugin instance
plugin = manager.get_plugin_instance("local_storage")

# Connect to service
plugin.connect({
    "root_directory": "/path/to/data",
    "read_only": False
})

# List files
files = plugin.list_directory("/some/directory")

# Read file
content = plugin.read_file("/some/file.txt")
```

### Dropbox Provider

#### Old Code

```python
from science_data_kit.core.providers.storage.dropbox_provider import DropboxProvider

# Create provider instance
provider = DropboxProvider(config={
    "app_key": "your_app_key",
    "app_secret": "your_app_secret",
    "refresh_token": "your_refresh_token"
})

# Initialize provider
await provider.initialize()

# List files
files = await provider.list_files("/some/directory")

# Read file
content = await provider.read_file("/some/file.txt")
```

#### New Code

```python
from science_data_kit.core.connections.manager import manager

# Get plugin instance
plugin = manager.get_plugin_instance("dropbox")

# Connect to service
plugin.connect({
    "app_key": "your_app_key",
    "app_secret": "your_app_secret",
    "refresh_token": "your_refresh_token",
    "root_path": ""
})

# List files
files = plugin.list_directory("/some/directory")

# Read file
content = plugin.read_file("/some/file.txt")
```

### Google Drive Provider

#### Old Code

```python
from science_data_kit.core.providers.storage.google_drive_provider import GoogleDriveProvider

# Create provider instance
provider = GoogleDriveProvider(config={
    "token_path": "/path/to/token.json",
    "credentials_path": "/path/to/credentials.json"
})

# Initialize provider
await provider.initialize()

# List files
files = await provider.list_files("folder_id")

# Download file data
data = await provider.download_file_data("file_id")
```

#### New Code

```python
from science_data_kit.core.connections.manager import manager

# Get plugin instance
plugin = manager.get_plugin_instance("google_drive")

# Connect to service
plugin.connect({
    "token_path": "/path/to/token.json",
    "credentials_path": "/path/to/credentials.json",
    "root_folder_id": "root"
})

# List files
files = plugin.list_directory("folder_id")

# Read file
content = plugin.read_file("file_id")
```

### Google Sheets Provider

#### Old Code

```python
from science_data_kit.core.providers.storage.google_sheets_provider import GoogleSheetsProvider

# Create provider instance
provider = GoogleSheetsProvider(config={
    "credentials_file": "/path/to/credentials.json",
    "token_file": "/path/to/token.json"
})

# Initialize provider
await provider.initialize()

# List spreadsheets
spreadsheets = await provider.list_spreadsheets()

# List sheets in a spreadsheet
sheets = await provider.list_sheets("spreadsheet_id")

# Get sheet data
data = await provider.get_sheet_data("spreadsheet_id", "sheet_name")
```

#### New Code

```python
from science_data_kit.core.connections.manager import manager

# Get plugin instance
plugin = manager.get_plugin_instance("google_sheets")

# Connect to service
plugin.connect({
    "credentials_file": "/path/to/credentials.json",
    "token_file": "/path/to/token.json"
})

# List spreadsheets
spreadsheets = plugin.list_spreadsheets()

# List sheets in a spreadsheet
sheets = plugin.list_sheets("spreadsheet_id")

# Get sheet data
data = plugin.get_sheet_data("spreadsheet_id", "sheet_name")
```

## Using the Connection Manager

The new plugin architecture includes a connection manager that provides a centralized way to manage connections to various data sources. Here's how to use it:

```python
from science_data_kit.core.connections.manager import manager

# Get a plugin instance by name
plugin = manager.get_plugin_instance("plugin_name")

# Configure a connection pool
manager.configure_pool("cloud_storage", "dropbox", {
    "max_pool_size": 10,
    "min_idle": 1,
    "max_idle": 5,
    "idle_timeout": 300.0,  # 5 minutes
    "max_lifetime": 3600.0,  # 1 hour
})

# Get a pooled connection
connection = manager.get_pooled_connection("cloud_storage", "dropbox", config)

# Use the connection
# ...

# Return the connection to the pool
manager.return_pooled_connection("cloud_storage", "dropbox", connection)

# Get pool statistics
stats = manager.get_pool_stats("cloud_storage", "dropbox")
```

## Compatibility Layer

For backward compatibility, the old provider imports will continue to work for a transitional period. These imports will use the new plugin architecture under the hood, but will maintain the old interface. However, it's recommended to migrate to the new plugin architecture as soon as possible.

## Plugin Discovery

The plugin architecture includes an auto-discovery system that automatically finds and registers plugins. You can also manually register plugins:

```python
from science_data_kit.core.connections.registry import registry
from my_package.my_plugin import MyPlugin

# Register a plugin
registry.register_plugin(MyPlugin)

# Discover plugins in a package
registry.discover_plugins("my_package")
```

## Troubleshooting

### Plugin Not Found

If you get an error like `Plugin 'plugin_name' not found`, make sure the plugin is properly installed and registered. You can check the available plugins with:

```python
from science_data_kit.core.connections.registry import registry

# Get all registered plugins
plugins = registry.get_all_plugins()
print(plugins)
```

### Connection Errors

If you encounter connection errors, check the following:

1. Make sure your configuration is correct
2. Verify that you have the necessary permissions
3. Check if the service is available
4. Look for more detailed error messages in the logs

## Further Reading

- [Plugin Architecture Overview](../architecture/plugin_architecture.md)
- [Creating Custom Plugins](../development/creating_plugins.md)
- [Connection Manager API Reference](../api/core/connections/manager.md)