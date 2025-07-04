# Session Management Guide

## Overview

The Science Data Kit provides robust session management capabilities, allowing you to save and restore your work environment, including server connections, data sources, and pipelines. This guide explains how to use these features effectively.

## Table of Contents

1. [Introduction](#introduction)
2. [Session Configuration](#session-configuration)
3. [Resource Management](#resource-management)
4. [Saving and Loading Sessions](#saving-and-loading-sessions)
5. [Automatic Session Recovery](#automatic-session-recovery)
6. [Resource Access Control](#resource-access-control)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Introduction

Session management is a core feature of the Science Data Kit that allows you to maintain the state of your work environment across different sessions. This includes:

- Saving and loading session configurations
- Managing resources (connections, data sources, pipelines, etc.)
- Tracking dependencies between resources
- Automatically recovering sessions after crashes
- Controlling access to resources

## Session Configuration

The session configuration is the central component of the session management system. It stores metadata about the session and references to all resources.

### SessionConfig Class

The `SessionConfig` class is defined in `science_data_kit/core/session/config.py` and has the following structure:

```python
class SessionConfig:
    def __init__(self, name=None, description=None, version="1.0"):
        self.name = name or f"session_{int(time.time())}"
        self.description = description or "Science Data Kit session"
        self.version = version
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.resources = {}
        self.connections = {}
        self.metadata = {}
```

### Creating a Session Configuration

You can create a session configuration as follows:

```python
from science_data_kit.core.session.config import SessionConfig

# Create a session configuration
session_config = SessionConfig(
    name="my_session",
    description="My Science Data Kit session",
    version="1.0"
)

# Add metadata
session_config.metadata["author"] = "John Doe"
session_config.metadata["project"] = "My Research Project"
```

## Resource Management

Resources are managed through the `ResourceRegistry` class, which provides methods for registering, tracking, and accessing resources.

### Resource Class

The `Resource` class is the base class for all resources in the Science Data Kit. It has the following structure:

```python
class Resource:
    def __init__(self, name, resource_type, description=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = resource_type
        self.description = description or f"{resource_type} resource"
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.status = "created"
        self.dependencies = []
        self.metadata = {}
        self.permissions = []
```

### ResourceRegistry Class

The `ResourceRegistry` class is defined in `science_data_kit/core/session/registry.py` and provides methods for managing resources:

```python
class ResourceRegistry:
    def __init__(self):
        self.resources = {}
        
    def register_resource(self, resource):
        """Register a resource in the registry."""
        self.resources[resource.id] = resource
        return resource.id
        
    def get_resource(self, resource_id):
        """Get a resource by ID."""
        return self.resources.get(resource_id)
        
    def list_resources(self, resource_type=None):
        """List all resources, optionally filtered by type."""
        if resource_type:
            return [r for r in self.resources.values() if r.type == resource_type]
        return list(self.resources.values())
        
    def unregister_resource(self, resource_id):
        """Remove a resource from the registry."""
        if resource_id in self.resources:
            del self.resources[resource_id]
            return True
        return False
```

### Using the Resource Registry

Here's how to use the resource registry:

```python
from science_data_kit.core.session.registry import ResourceRegistry
from science_data_kit.core.session.resource import Resource

# Create a resource registry
registry = ResourceRegistry()

# Create and register a resource
db_resource = Resource(
    name="my_database",
    resource_type="database",
    description="My Neo4j database connection"
)
resource_id = registry.register_resource(db_resource)

# Get a resource by ID
resource = registry.get_resource(resource_id)
print(f"Resource name: {resource.name}")

# List all resources
all_resources = registry.list_resources()
print(f"Total resources: {len(all_resources)}")

# List resources by type
db_resources = registry.list_resources(resource_type="database")
print(f"Database resources: {len(db_resources)}")

# Unregister a resource
registry.unregister_resource(resource_id)
```

### Resource Dependencies

Resources can have dependencies on other resources. This is useful for tracking relationships between resources and ensuring that dependent resources are loaded in the correct order.

```python
# Create resources
db_resource = Resource(
    name="my_database",
    resource_type="database",
    description="My Neo4j database connection"
)
pipeline_resource = Resource(
    name="my_pipeline",
    resource_type="pipeline",
    description="My data transformation pipeline"
)

# Register resources
db_id = registry.register_resource(db_resource)
pipeline_id = registry.register_resource(pipeline_resource)

# Add dependency
pipeline_resource.dependencies.append(db_id)

# Check dependencies
print(f"Pipeline depends on: {pipeline_resource.dependencies}")
```

## Saving and Loading Sessions

The Science Data Kit provides functions for saving and loading session configurations.

### Saving a Session

You can save a session configuration to a file as follows:

```python
from science_data_kit.core.session.session import save_session

# Create a session configuration
session_config = SessionConfig(
    name="my_session",
    description="My Science Data Kit session"
)

# Add resources to the session
session_config.resources = {r.id: r for r in registry.list_resources()}

# Save the session
save_session(session_config, "my_session.yaml")  # or "my_session.json"
```

### Loading a Session

You can load a session configuration from a file as follows:

```python
from science_data_kit.core.session.session import load_session

# Load the session
session_config = load_session("my_session.yaml")  # or "my_session.json"

# Access session metadata
print(f"Session name: {session_config.name}")
print(f"Session description: {session_config.description}")

# Access session resources
for resource_id, resource in session_config.resources.items():
    print(f"Resource: {resource.name} ({resource.type})")
```

## Automatic Session Recovery

The Science Data Kit includes functionality for automatically recovering sessions after crashes or unexpected shutdowns.

### Signal Handlers

Signal handlers are set up to catch signals like SIGINT (Ctrl+C) and SIGTERM (termination) and save the session before exiting:

```python
from science_data_kit.core.session.recovery import setup_signal_handlers

# Set up signal handlers
setup_signal_handlers(session_config, "autosave.yaml")
```

### Exit Handlers

Exit handlers are registered to save the session when the Python interpreter exits:

```python
from science_data_kit.core.session.recovery import setup_exit_handler

# Set up exit handler
setup_exit_handler(session_config, "autosave.yaml")
```

### Autosave Functionality

The autosave functionality periodically saves the session to a file:

```python
from science_data_kit.core.session.recovery import start_autosave

# Start autosave (every 5 minutes)
stop_autosave = start_autosave(session_config, "autosave.yaml", interval=300)

# Later, stop autosave
stop_autosave()
```

## Resource Access Control

The Science Data Kit includes functionality for controlling access to resources.

### ResourcePermission Class

The `ResourcePermission` class defines permissions for resources:

```python
class ResourcePermission:
    def __init__(self, user_id, permission_type):
        self.user_id = user_id
        self.permission_type = permission_type  # "read", "write", "admin"
        self.granted_at = datetime.now().isoformat()
```

### Managing Permissions

You can manage permissions for resources as follows:

```python
from science_data_kit.core.session.resource import ResourcePermission

# Create a resource
resource = Resource(
    name="my_database",
    resource_type="database",
    description="My Neo4j database connection"
)

# Add permissions
resource.permissions.append(ResourcePermission("user1", "read"))
resource.permissions.append(ResourcePermission("user2", "write"))
resource.permissions.append(ResourcePermission("admin", "admin"))

# Check permissions
def has_permission(resource, user_id, permission_type):
    for perm in resource.permissions:
        if perm.user_id == user_id and perm.permission_type == permission_type:
            return True
    return False

print(f"User1 can read: {has_permission(resource, 'user1', 'read')}")
print(f"User2 can write: {has_permission(resource, 'user2', 'write')}")
print(f"User1 can write: {has_permission(resource, 'user1', 'write')}")
```

## Best Practices

Here are some best practices for using session management in the Science Data Kit:

1. **Use Descriptive Names**: Give your sessions and resources descriptive names to make them easier to identify.
2. **Track Dependencies**: Explicitly track dependencies between resources to ensure they are loaded in the correct order.
3. **Use Autosave**: Enable autosave to prevent data loss in case of crashes or unexpected shutdowns.
4. **Manage Permissions**: Use the permission system to control access to sensitive resources.
5. **Clean Up Resources**: Unregister resources when they are no longer needed to free up memory.
6. **Version Your Sessions**: Use the version field to track changes to your session configurations.
7. **Add Metadata**: Use the metadata field to add additional information about your sessions and resources.

## Troubleshooting

Here are some common issues and their solutions:

### Session Loading Issues

- **Issue**: Unable to load a session file.
  - **Solution**: Check that the file exists and is in the correct format (YAML or JSON). Ensure that the file has not been corrupted.

### Resource Dependency Issues

- **Issue**: Resources are not loaded in the correct order.
  - **Solution**: Check that dependencies are correctly defined. Resources with dependencies should be loaded after their dependencies.

### Permission Issues

- **Issue**: Unable to access a resource due to permission issues.
  - **Solution**: Check that the user has the necessary permissions for the resource. If not, grant the appropriate permissions.

### Recovery Issues

- **Issue**: Session is not automatically recovered after a crash.
  - **Solution**: Check that signal handlers and exit handlers are correctly set up. Ensure that the autosave file is being created and is not corrupted.

If you encounter other issues, please refer to the API documentation or contact support.