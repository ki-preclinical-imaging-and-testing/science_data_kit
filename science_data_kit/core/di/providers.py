"""
Dependency Injection Providers for Science Data Kit

This module implements different provider types for the dependency injection system,
including singleton providers, transient providers, and factory providers.
"""

from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar, Union
import inspect

from .interfaces import Provider

# Type variables for generic typing
T = TypeVar('T')


class SingletonProvider(Provider[T]):
    """
    Provider that creates a single instance of a component and reuses it.
    
    This provider is useful for components that should be shared across the application,
    such as database connections, configuration managers, etc.
    """
    
    def __init__(self, factory: Callable[..., T]):
        """
        Initialize the singleton provider.
        
        Args:
            factory: A callable that creates an instance of the component.
        """
        self._factory = factory
        self._instance = None
    
    def get(self) -> T:
        """
        Get the singleton instance of the component.
        
        If the instance doesn't exist yet, it will be created using the factory.
        
        Returns:
            The singleton instance of the component.
        """
        if self._instance is None:
            self._instance = self._factory()
        return self._instance


class TransientProvider(Provider[T]):
    """
    Provider that creates a new instance of a component each time it's requested.
    
    This provider is useful for components that should not be shared, such as
    request-specific objects, data transfer objects, etc.
    """
    
    def __init__(self, factory: Callable[..., T]):
        """
        Initialize the transient provider.
        
        Args:
            factory: A callable that creates an instance of the component.
        """
        self._factory = factory
    
    def get(self) -> T:
        """
        Get a new instance of the component.
        
        Returns:
            A new instance of the component.
        """
        return self._factory()


class InstanceProvider(Provider[T]):
    """
    Provider that returns a pre-created instance of a component.
    
    This provider is useful for integrating existing instances into the
    dependency injection system.
    """
    
    def __init__(self, instance: T):
        """
        Initialize the instance provider.
        
        Args:
            instance: The instance to provide.
        """
        self._instance = instance
    
    def get(self) -> T:
        """
        Get the pre-created instance of the component.
        
        Returns:
            The pre-created instance of the component.
        """
        return self._instance


class FactoryProvider(Provider[T]):
    """
    Provider that uses a factory function to create instances of a component.
    
    This provider is useful for components that require complex initialization
    or have dependencies that are not managed by the container.
    """
    
    def __init__(self, factory: Callable[..., T], *args, **kwargs):
        """
        Initialize the factory provider.
        
        Args:
            factory: A callable that creates an instance of the component.
            *args: Positional arguments to pass to the factory.
            **kwargs: Keyword arguments to pass to the factory.
        """
        self._factory = factory
        self._args = args
        self._kwargs = kwargs
    
    def get(self) -> T:
        """
        Get a new instance of the component using the factory.
        
        Returns:
            A new instance of the component.
        """
        return self._factory(*self._args, **self._kwargs)