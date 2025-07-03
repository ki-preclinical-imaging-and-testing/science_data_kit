"""
Resource Registry for Science Data Kit

This module provides functionality for managing resources in a session,
including registering, tracking, and accessing resources.
"""

import logging
from typing import Dict, Any, Optional, List, Type, TypeVar, Generic, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

# Type variable for resource types
T = TypeVar('T')


class ResourcePermission:
    """
    Class representing a permission for a resource.

    Attributes:
        user_id: The ID of the user.
        can_read: Whether the user can read the resource.
        can_write: Whether the user can write to the resource.
        can_execute: Whether the user can execute the resource.
        can_share: Whether the user can share the resource with others.
    """

    def __init__(self, user_id: str, can_read: bool = True, can_write: bool = False, 
                 can_execute: bool = False, can_share: bool = False):
        """
        Initialize a resource permission.

        Args:
            user_id: The ID of the user.
            can_read: Whether the user can read the resource.
            can_write: Whether the user can write to the resource.
            can_execute: Whether the user can execute the resource.
            can_share: Whether the user can share the resource with others.
        """
        self.user_id = user_id
        self.can_read = can_read
        self.can_write = can_write
        self.can_execute = can_execute
        self.can_share = can_share

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the permission to a dictionary.

        Returns:
            A dictionary representation of the permission.
        """
        return {
            "user_id": self.user_id,
            "can_read": self.can_read,
            "can_write": self.can_write,
            "can_execute": self.can_execute,
            "can_share": self.can_share
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourcePermission':
        """
        Create a permission from a dictionary.

        Args:
            data: A dictionary containing the permission data.

        Returns:
            A new ResourcePermission instance.
        """
        return cls(
            user_id=data.get("user_id", ""),
            can_read=data.get("can_read", True),
            can_write=data.get("can_write", False),
            can_execute=data.get("can_execute", False),
            can_share=data.get("can_share", False)
        )


class Resource(ABC):
    """
    Abstract base class for all resources.

    This class defines the interface that all resources must implement.
    Resources are objects that can be registered in the resource registry
    and managed by the session.

    Attributes:
        resource_id: The unique identifier for the resource.
        resource_type: The type of the resource.
        metadata: Additional metadata for the resource.
        owner: The ID of the resource owner.
        permissions: A dictionary of user permissions, keyed by user ID.
    """

    def __init__(self, resource_id: str, resource_type: str, **kwargs):
        """
        Initialize a resource.

        Args:
            resource_id: The unique identifier for the resource.
            resource_type: The type of the resource.
            **kwargs: Additional keyword arguments for resource configuration.
        """
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.metadata = kwargs.get('metadata', {})
        self.created = datetime.now().isoformat()
        self.last_accessed = self.created
        self.status = "initialized"
        self._dependencies = set()
        self._dependents = set()

        # Access control
        self.owner = kwargs.get('owner', '')
        self.permissions: Dict[str, ResourcePermission] = {}

        # Add owner permission if owner is specified
        if self.owner:
            self.add_permission(ResourcePermission(
                user_id=self.owner,
                can_read=True,
                can_write=True,
                can_execute=True,
                can_share=True
            ))

    @abstractmethod
    def to_config(self) -> Dict[str, Any]:
        """
        Convert the resource to a configuration dictionary.

        Returns:
            A dictionary representation of the resource configuration.
        """
        config = {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "metadata": self.metadata,
            "created": self.created,
            "last_accessed": self.last_accessed,
            "status": self.status,
            "owner": self.owner,
            "permissions": self.get_permissions_dict()
        }
        return config

    @classmethod
    @abstractmethod
    def from_config(cls, config: Dict[str, Any]) -> 'Resource':
        """
        Create a resource from a configuration dictionary.

        Args:
            config: A dictionary containing the resource configuration.

        Returns:
            A new resource instance.
        """
        pass

    def add_dependency(self, resource_id: str) -> None:
        """
        Add a dependency to this resource.

        Args:
            resource_id: The ID of the resource that this resource depends on.
        """
        self._dependencies.add(resource_id)

    def remove_dependency(self, resource_id: str) -> None:
        """
        Remove a dependency from this resource.

        Args:
            resource_id: The ID of the resource to remove as a dependency.
        """
        if resource_id in self._dependencies:
            self._dependencies.remove(resource_id)

    def add_dependent(self, resource_id: str) -> None:
        """
        Add a dependent to this resource.

        Args:
            resource_id: The ID of the resource that depends on this resource.
        """
        self._dependents.add(resource_id)

    def remove_dependent(self, resource_id: str) -> None:
        """
        Remove a dependent from this resource.

        Args:
            resource_id: The ID of the resource to remove as a dependent.
        """
        if resource_id in self._dependents:
            self._dependents.remove(resource_id)

    @property
    def dependencies(self) -> List[str]:
        """
        Get the dependencies of this resource.

        Returns:
            A list of resource IDs that this resource depends on.
        """
        return list(self._dependencies)

    @property
    def dependents(self) -> List[str]:
        """
        Get the dependents of this resource.

        Returns:
            A list of resource IDs that depend on this resource.
        """
        return list(self._dependents)

    def update_last_accessed(self) -> None:
        """Update the last_accessed timestamp to the current time."""
        self.last_accessed = datetime.now().isoformat()

    def update_status(self, status: str) -> None:
        """
        Update the status of the resource.

        Args:
            status: The new status of the resource.
        """
        self.status = status

    def add_permission(self, permission: ResourcePermission) -> None:
        """
        Add a permission to the resource.

        Args:
            permission: The permission to add.
        """
        self.permissions[permission.user_id] = permission

    def remove_permission(self, user_id: str) -> None:
        """
        Remove a permission from the resource.

        Args:
            user_id: The ID of the user whose permission to remove.

        Raises:
            KeyError: If the user does not have a permission for this resource.
        """
        if user_id not in self.permissions:
            raise KeyError(f"User '{user_id}' does not have a permission for resource '{self.resource_id}'")

        del self.permissions[user_id]

    def get_permission(self, user_id: str) -> Optional[ResourcePermission]:
        """
        Get a user's permission for the resource.

        Args:
            user_id: The ID of the user.

        Returns:
            The user's permission, or None if the user does not have a permission.
        """
        return self.permissions.get(user_id)

    def check_permission(self, user_id: str, permission_type: str) -> bool:
        """
        Check if a user has a specific permission for the resource.

        Args:
            user_id: The ID of the user.
            permission_type: The type of permission to check ('read', 'write', 'execute', 'share').

        Returns:
            True if the user has the permission, False otherwise.

        Raises:
            ValueError: If the permission_type is not valid.
        """
        # Owner has all permissions
        if user_id == self.owner:
            return True

        # Check if the user has a permission
        permission = self.get_permission(user_id)
        if permission is None:
            return False

        # Check the specific permission
        if permission_type == 'read':
            return permission.can_read
        elif permission_type == 'write':
            return permission.can_write
        elif permission_type == 'execute':
            return permission.can_execute
        elif permission_type == 'share':
            return permission.can_share
        else:
            raise ValueError(f"Invalid permission type: {permission_type}")

    def get_permissions_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a dictionary of all permissions for the resource.

        Returns:
            A dictionary of permissions, keyed by user ID.
        """
        return {
            user_id: permission.to_dict()
            for user_id, permission in self.permissions.items()
        }

    def set_permissions_from_dict(self, permissions_dict: Dict[str, Dict[str, Any]]) -> None:
        """
        Set permissions from a dictionary.

        Args:
            permissions_dict: A dictionary of permissions, keyed by user ID.
        """
        self.permissions = {
            user_id: ResourcePermission.from_dict(permission_data)
            for user_id, permission_data in permissions_dict.items()
        }


class ResourceRegistry:
    """
    Registry for managing resources.

    This class provides functionality for registering, tracking, and accessing
    resources in a session.

    Attributes:
        resources: A dictionary of registered resources, keyed by resource ID.
    """

    def __init__(self):
        """Initialize an empty resource registry."""
        self.resources: Dict[str, Resource] = {}
        self._resource_factories: Dict[str, Callable[[Dict[str, Any]], Resource]] = {}

    def register_resource(self, resource: Resource) -> None:
        """
        Register a resource in the registry.

        Args:
            resource: The resource to register.

        Raises:
            ValueError: If a resource with the same ID is already registered.
        """
        if resource.resource_id in self.resources:
            raise ValueError(f"Resource with ID '{resource.resource_id}' is already registered")

        self.resources[resource.resource_id] = resource
        logger.info(f"Registered resource: {resource.resource_id} ({resource.resource_type})")

    def unregister_resource(self, resource_id: str) -> None:
        """
        Unregister a resource from the registry.

        Args:
            resource_id: The ID of the resource to unregister.

        Raises:
            KeyError: If the resource is not registered.
        """
        if resource_id not in self.resources:
            raise KeyError(f"Resource '{resource_id}' is not registered")

        # Get the resource
        resource = self.resources[resource_id]

        # Remove dependencies and dependents
        for dep_id in resource.dependencies:
            if dep_id in self.resources:
                self.resources[dep_id].remove_dependent(resource_id)

        for dep_id in resource.dependents:
            if dep_id in self.resources:
                self.resources[dep_id].remove_dependency(resource_id)

        # Remove the resource
        del self.resources[resource_id]
        logger.info(f"Unregistered resource: {resource_id}")

    def get_resource(self, resource_id: str) -> Resource:
        """
        Get a resource from the registry.

        Args:
            resource_id: The ID of the resource to get.

        Returns:
            The requested resource.

        Raises:
            KeyError: If the resource is not registered.
        """
        if resource_id not in self.resources:
            raise KeyError(f"Resource '{resource_id}' is not registered")

        resource = self.resources[resource_id]
        resource.update_last_accessed()
        return resource

    def register_resource_factory(self, resource_type: str, factory: Callable[[Dict[str, Any]], Resource]) -> None:
        """
        Register a factory function for creating resources of a specific type.

        Args:
            resource_type: The type of resource the factory creates.
            factory: A function that creates a resource from a configuration dictionary.
        """
        self._resource_factories[resource_type] = factory
        logger.info(f"Registered resource factory for type: {resource_type}")

    def create_resource(self, resource_type: str, resource_id: str, config: Dict[str, Any]) -> Resource:
        """
        Create a resource using a registered factory function.

        Args:
            resource_type: The type of resource to create.
            resource_id: The ID for the new resource.
            config: The configuration for the new resource.

        Returns:
            The created resource.

        Raises:
            ValueError: If no factory is registered for the resource type.
        """
        if resource_type not in self._resource_factories:
            raise ValueError(f"No factory registered for resource type: {resource_type}")

        # Add resource_id to the config
        config['resource_id'] = resource_id

        # Create the resource
        resource = self._resource_factories[resource_type](config)

        # Register the resource
        self.register_resource(resource)

        return resource

    def add_dependency(self, dependent_id: str, dependency_id: str) -> None:
        """
        Add a dependency relationship between two resources.

        Args:
            dependent_id: The ID of the dependent resource.
            dependency_id: The ID of the dependency resource.

        Raises:
            KeyError: If either resource is not registered.
        """
        if dependent_id not in self.resources:
            raise KeyError(f"Dependent resource '{dependent_id}' is not registered")
        if dependency_id not in self.resources:
            raise KeyError(f"Dependency resource '{dependency_id}' is not registered")

        # Add the dependency
        self.resources[dependent_id].add_dependency(dependency_id)
        self.resources[dependency_id].add_dependent(dependent_id)

    def remove_dependency(self, dependent_id: str, dependency_id: str) -> None:
        """
        Remove a dependency relationship between two resources.

        Args:
            dependent_id: The ID of the dependent resource.
            dependency_id: The ID of the dependency resource.

        Raises:
            KeyError: If either resource is not registered.
        """
        if dependent_id not in self.resources:
            raise KeyError(f"Dependent resource '{dependent_id}' is not registered")
        if dependency_id not in self.resources:
            raise KeyError(f"Dependency resource '{dependency_id}' is not registered")

        # Remove the dependency
        self.resources[dependent_id].remove_dependency(dependency_id)
        self.resources[dependency_id].remove_dependent(dependent_id)

    def get_dependencies(self, resource_id: str) -> List[Resource]:
        """
        Get all dependencies of a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            A list of resources that the specified resource depends on.

        Raises:
            KeyError: If the resource is not registered.
        """
        if resource_id not in self.resources:
            raise KeyError(f"Resource '{resource_id}' is not registered")

        resource = self.resources[resource_id]
        return [self.resources[dep_id] for dep_id in resource.dependencies if dep_id in self.resources]

    def get_dependents(self, resource_id: str) -> List[Resource]:
        """
        Get all dependents of a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            A list of resources that depend on the specified resource.

        Raises:
            KeyError: If the resource is not registered.
        """
        if resource_id not in self.resources:
            raise KeyError(f"Resource '{resource_id}' is not registered")

        resource = self.resources[resource_id]
        return [self.resources[dep_id] for dep_id in resource.dependents if dep_id in self.resources]

    def to_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Convert the registry to a configuration dictionary.

        Returns:
            A dictionary representation of the registry.
        """
        return {
            resource_id: resource.to_config()
            for resource_id, resource in self.resources.items()
        }

    def from_config(self, config: Dict[str, Dict[str, Any]]) -> None:
        """
        Populate the registry from a configuration dictionary.

        Args:
            config: A dictionary containing resource configurations.

        Raises:
            ValueError: If a resource type is not registered.
        """
        for resource_id, resource_config in config.items():
            resource_type = resource_config.get('resource_type')
            if not resource_type:
                logger.warning(f"Resource '{resource_id}' has no type, skipping")
                continue

            if resource_type not in self._resource_factories:
                logger.warning(f"No factory registered for resource type: {resource_type}, skipping")
                continue

            try:
                # Create and register the resource
                self.create_resource(resource_type, resource_id, resource_config)
            except Exception as e:
                logger.error(f"Error creating resource '{resource_id}': {e}")
