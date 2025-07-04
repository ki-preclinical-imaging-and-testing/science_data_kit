"""
Dependency Injection Interfaces for Science Data Kit

This module defines the interfaces for the dependency injection system,
including the container, providers, and component registration.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar, Union

# Type variables for generic typing
T = TypeVar('T')
R = TypeVar('R')


class Provider(Generic[T], ABC):
    """
    Abstract base class for dependency providers.
    
    Providers are responsible for creating and managing instances of components.
    Different provider implementations can handle different component lifetimes
    (e.g., singleton, transient, scoped).
    """
    
    @abstractmethod
    def get(self) -> T:
        """
        Get an instance of the component.
        
        Returns:
            An instance of the component.
        """
        pass


class Container(ABC):
    """
    Abstract base class for the dependency injection container.
    
    The container is responsible for registering and resolving dependencies.
    """
    
    @abstractmethod
    def register(self, interface: Type[T], implementation: Union[Type[T], Callable[..., T]], 
                singleton: bool = False) -> None:
        """
        Register a component with the container.
        
        Args:
            interface: The interface or abstract class that the implementation fulfills.
            implementation: The concrete implementation class or a factory function.
            singleton: If True, the component will be created once and reused.
        """
        pass
    
    @abstractmethod
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register an existing instance with the container.
        
        Args:
            interface: The interface or abstract class that the instance fulfills.
            instance: The instance to register.
        """
        pass
    
    @abstractmethod
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a dependency from the container.
        
        Args:
            interface: The interface or abstract class to resolve.
            
        Returns:
            An instance of the requested type.
            
        Raises:
            KeyError: If the requested interface is not registered.
        """
        pass


class Injector(ABC):
    """
    Abstract base class for dependency injectors.
    
    Injectors are responsible for injecting dependencies into components.
    """
    
    @abstractmethod
    def inject(self, target: Any) -> Any:
        """
        Inject dependencies into a target object.
        
        Args:
            target: The object to inject dependencies into.
            
        Returns:
            The target object with dependencies injected.
        """
        pass