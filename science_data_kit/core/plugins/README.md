# Science Data Kit Plugin System

The Science Data Kit Plugin System provides a framework for extending the functionality of the Science Data Kit through plugins. Plugins can add new features, modify existing behavior, or integrate with external systems.

## Table of Contents

- [Architecture](#architecture)
- [Creating Plugins](#creating-plugins)
- [Using the Plugin Manager](#using-the-plugin-manager)
- [Plugin Discovery](#plugin-discovery)
- [Example Plugins](#example-plugins)
- [Best Practices](#best-practices)

## Architecture

The plugin system consists of the following components:

- **Plugin**: An abstract base class that defines the interface for all plugins.
- **PluginManager**: A class that handles loading, registering, activating, and deactivating plugins.
- **Plugin Discovery**: Mechanisms for discovering and loading plugins from various sources.

### Directory Structure

```
science_data_kit/core/plugins/
├── __init__.py           # Package initialization
├── base.py               # Plugin and PluginManager classes
├── discovery.py          # Plugin discovery mechanisms
├── examples/             # Example plugins
│   ├── __init__.py
│   ├── hello_world.py    # A simple Hello World plugin
│   ├── data_processor.py # A data processing plugin
│   ├── visualization.py  # A visualization plugin
│   └── test_plugins.py   # Test script for the example plugins
└── README.md             # This documentation
```

## Creating Plugins

To create a plugin, you need to:

1. Create a new class that inherits from `Plugin`.
2. Implement the required abstract methods: `name`, `version`, `description`, and `initialize`.
3. Optionally override the `dependencies` property and `shutdown` method.

Here's a simple example:

```python
from science_data_kit.core.plugins.base import Plugin

class MyPlugin(Plugin):
    @property
    def name(self) -> str:
        """Return the name of the plugin."""
        return "my_plugin"
    
    @property
    def version(self) -> str:
        """Return the version of the plugin."""
        return "1.0.0"
    
    @property
    def description(self) -> str:
        """Return a description of the plugin."""
        return "A simple plugin for the Science Data Kit."
    
    @property
    def dependencies(self) -> List[str]:
        """Return a list of plugin names that this plugin depends on."""
        return []  # No dependencies
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        print("MyPlugin initialized!")
    
    def shutdown(self) -> None:
        """Shut down the plugin."""
        print("MyPlugin shut down!")
    
    # Custom methods for your plugin
    def do_something(self) -> str:
        return "MyPlugin did something!"
```

### Plugin Properties

- **name**: A unique identifier for the plugin. This should be a string that is unique among all plugins.
- **version**: The version of the plugin. This should follow semantic versioning (e.g., "1.0.0").
- **description**: A human-readable description of the plugin.
- **dependencies**: A list of plugin names that this plugin depends on. The plugin manager will ensure that dependencies are activated before the plugin.

### Plugin Methods

- **initialize**: Called when the plugin is activated. This method should perform any setup required for the plugin to function.
- **shutdown**: Called when the plugin is deactivated. This method should perform any cleanup required when the plugin is no longer needed.

## Using the Plugin Manager

The `PluginManager` class handles loading, registering, activating, and deactivating plugins. Here's how to use it:

```python
from science_data_kit.core.plugins.base import PluginManager
from my_plugin import MyPlugin

# Create a plugin manager
manager = PluginManager()

# Create and register a plugin
plugin = MyPlugin()
manager.register_plugin(plugin)

# Activate the plugin
success = manager.activate_plugin(plugin.name)
if success:
    print(f"Plugin {plugin.name} activated successfully!")
else:
    print(f"Failed to activate plugin {plugin.name}.")

# Use the plugin
plugin.do_something()

# Deactivate the plugin
success = manager.deactivate_plugin(plugin.name)
if success:
    print(f"Plugin {plugin.name} deactivated successfully!")
else:
    print(f"Failed to deactivate plugin {plugin.name}.")
```

### Plugin Manager Methods

- **register_plugin**: Register a plugin with the manager.
- **activate_plugin**: Activate a registered plugin and its dependencies.
- **deactivate_plugin**: Deactivate an active plugin.
- **get_plugin**: Get a registered plugin by name.
- **get_all_plugins**: Get all registered plugins.
- **get_active_plugins**: Get all active plugins.
- **get_plugin_state**: Get the state of a plugin.
- **get_plugin_error**: Get the error message for a plugin in the ERROR state.
- **activate_all_plugins**: Activate all registered plugins.
- **deactivate_all_plugins**: Deactivate all active plugins.

## Plugin Discovery

The plugin system provides mechanisms for discovering and loading plugins from various sources:

- **Directories**: Search for Python modules and packages in specified directories.
- **Modules**: Import specified modules and search for plugins.
- **Entry Points**: Search for plugins registered as entry points.

Here's how to use the plugin discovery mechanisms:

```python
from science_data_kit.core.plugins.base import PluginManager
from science_data_kit.core.plugins.discovery import discover_plugins

# Create a plugin manager
manager = PluginManager()

# Discover plugins from various sources
results = discover_plugins(
    manager,
    plugin_dirs=["/path/to/plugins"],
    plugin_modules=["my_package.plugins"],
    plugin_entry_points=["my_package.plugins"]
)

# Activate all discovered plugins
activation_results = manager.activate_all_plugins()
```

## Example Plugins

The plugin system includes several example plugins that demonstrate how to create and use plugins:

- **HelloWorldPlugin**: A simple plugin that demonstrates the basic structure of a plugin.
- **DataProcessorPlugin**: A plugin that performs data processing operations on pandas DataFrames.
- **VisualizationPlugin**: A plugin that creates visualizations of data using matplotlib and seaborn.

You can find these examples in the `examples` directory.

## Best Practices

Here are some best practices for creating and using plugins:

- **Keep plugins focused**: Each plugin should have a clear, focused purpose.
- **Handle errors gracefully**: Plugins should handle errors gracefully and provide clear error messages.
- **Document your plugins**: Provide clear documentation for your plugins, including their purpose, usage, and any dependencies.
- **Test your plugins**: Write tests for your plugins to ensure they work correctly.
- **Version your plugins**: Use semantic versioning for your plugins to indicate compatibility.
- **Consider dependencies**: Be mindful of dependencies between plugins and ensure they are properly declared.
- **Clean up resources**: Ensure that plugins clean up any resources they use when they are deactivated.
- **Use logging**: Use the logging module to provide information about plugin activities.