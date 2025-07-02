"""
Examples for Session Management in Science Data Kit

This module provides examples of how to use the session management functionality.
"""

import os
from typing import Dict, Any
from pathlib import Path

from .config import SessionConfig, load_session_config, save_session_config
from .registry import Resource, ResourceRegistry
from .session import Session, create_session, load_session, list_sessions


class ExampleResource(Resource):
    """
    Example resource class for demonstration purposes.
    
    This class implements the Resource interface and provides a simple
    example of how to create a custom resource type.
    """
    
    def __init__(self, resource_id: str, name: str, value: Any, **kwargs):
        """
        Initialize an example resource.
        
        Args:
            resource_id: The unique identifier for the resource.
            name: The name of the resource.
            value: The value of the resource.
            **kwargs: Additional keyword arguments for resource configuration.
        """
        super().__init__(resource_id=resource_id, resource_type="example", **kwargs)
        self.name = name
        self.value = value
    
    def to_config(self) -> Dict[str, Any]:
        """
        Convert the resource to a configuration dictionary.
        
        Returns:
            A dictionary representation of the resource configuration.
        """
        config = super().to_config()
        config.update({
            "name": self.name,
            "value": self.value
        })
        return config
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'ExampleResource':
        """
        Create a resource from a configuration dictionary.
        
        Args:
            config: A dictionary containing the resource configuration.
            
        Returns:
            A new resource instance.
        """
        return cls(
            resource_id=config["resource_id"],
            name=config.get("name", ""),
            value=config.get("value"),
            metadata=config.get("metadata", {})
        )


def example_resource_factory(config: Dict[str, Any]) -> Resource:
    """
    Factory function for creating ExampleResource instances.
    
    Args:
        config: A dictionary containing the resource configuration.
        
    Returns:
        A new ExampleResource instance.
    """
    return ExampleResource.from_config(config)


def example_create_and_save_session():
    """
    Example of creating and saving a session.
    
    This function creates a new session, adds some resources to it,
    and saves it to a file.
    """
    # Create a new session
    session = create_session(name="Example Session", description="An example session for demonstration purposes")
    
    # Register the example resource factory
    session.registry.register_resource_factory("example", example_resource_factory)
    
    # Create some resources
    resource1 = ExampleResource(resource_id="resource1", name="Resource 1", value="Hello, world!")
    resource2 = ExampleResource(resource_id="resource2", name="Resource 2", value=42)
    
    # Add the resources to the session
    session.add_resource(resource1)
    session.add_resource(resource2)
    
    # Add a dependency between the resources
    session.add_dependency("resource2", "resource1")
    
    # Save the session
    session.save()
    
    print(f"Session saved to {session.session_file}")
    
    return session


def example_load_session(session_file: Path):
    """
    Example of loading a session.
    
    This function loads a session from a file and prints information about it.
    
    Args:
        session_file: The path to the session file.
    """
    # Register the example resource factory (this would typically be done at application startup)
    registry = ResourceRegistry()
    registry.register_resource_factory("example", example_resource_factory)
    
    # Load the session
    session = load_session(session_file)
    
    # Print session information
    print(f"Loaded session: {session.config.name}")
    print(f"Description: {session.config.description}")
    print(f"Created: {session.config.created}")
    print(f"Last modified: {session.config.last_modified}")
    print(f"Resources: {len(session.registry.resources)}")
    
    # Print resource information
    for resource_id, resource in session.registry.resources.items():
        print(f"Resource: {resource_id}")
        print(f"  Type: {resource.resource_type}")
        print(f"  Name: {resource.name}")
        print(f"  Value: {resource.value}")
        print(f"  Dependencies: {resource.dependencies}")
        print(f"  Dependents: {resource.dependents}")
    
    return session


def run_examples():
    """Run all examples."""
    # Create and save a session
    session = example_create_and_save_session()
    
    # Load the session
    example_load_session(session.session_file)
    
    # List available sessions
    sessions = list_sessions()
    print(f"Available sessions: {len(sessions)}")
    for session_info in sessions:
        print(f"  {session_info['name']} - {session_info['description']}")


if __name__ == "__main__":
    run_examples()