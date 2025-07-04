"""
Dependency Injection Container for Science Data Kit

This module implements the dependency injection container, which is responsible
for registering and resolving dependencies.
"""

import inspect
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, get_type_hints

from .interfaces import Container, Provider
from .providers import SingletonProvider, TransientProvider, InstanceProvider, FactoryProvider

# Type variables for generic typing
T = TypeVar('T')


class DIContainer(Container):
    """
    Implementation of the dependency injection container.
    
    This container manages the registration and resolution of dependencies,
    supporting different provider types and automatic dependency resolution.
    """
    
    def __init__(self):
        """Initialize the container with an empty registry."""
        self._registry: Dict[Type, Provider] = {}
    
    def register(self, interface: Type[T], implementation: Union[Type[T], Callable[..., T]], 
                singleton: bool = False) -> None:
        """
        Register a component with the container.
        
        Args:
            interface: The interface or abstract class that the implementation fulfills.
            implementation: The concrete implementation class or a factory function.
            singleton: If True, the component will be created once and reused.
        """
        if singleton:
            provider = SingletonProvider(self._create_factory(implementation))
        else:
            provider = TransientProvider(self._create_factory(implementation))
        
        self._registry[interface] = provider
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register an existing instance with the container.
        
        Args:
            interface: The interface or abstract class that the instance fulfills.
            instance: The instance to register.
        """
        self._registry[interface] = InstanceProvider(instance)
    
    def register_factory(self, interface: Type[T], factory: Callable[..., T], 
                        *args, **kwargs) -> None:
        """
        Register a factory function with the container.
        
        Args:
            interface: The interface or abstract class that the factory creates.
            factory: A callable that creates an instance of the component.
            *args: Positional arguments to pass to the factory.
            **kwargs: Keyword arguments to pass to the factory.
        """
        self._registry[interface] = FactoryProvider(factory, *args, **kwargs)
    
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
        if interface not in self._registry:
            raise KeyError(f"No registration found for {interface.__name__}")
        
        return self._registry[interface].get()
    
    def _create_factory(self, implementation: Union[Type[T], Callable[..., T]]) -> Callable[[], T]:
        """
        Create a factory function for the given implementation.
        
        If the implementation is a class, the factory will create an instance of the class,
        resolving constructor dependencies from the container. If the implementation is a
        callable, it will be used directly as the factory.
        
        Args:
            implementation: The class or callable to create a factory for.
            
        Returns:
            A factory function that creates instances of the implementation.
        """
        if inspect.isclass(implementation):
            def factory():
                # Get constructor parameters
                init_signature = inspect.signature(implementation.__init__)
                parameters = init_signature.parameters
                
                # Skip 'self' parameter
                parameters = list(parameters.values())[1:]
                
                # Resolve dependencies for constructor parameters
                args = []
                for param in parameters:
                    # Get parameter type hint
                    type_hints = get_type_hints(implementation.__init__)
                    if param.name in type_hints:
                        param_type = type_hints[param.name]
                        # Try to resolve the dependency
                        try:
                            arg = self.resolve(param_type)
                            args.append(arg)
                        except KeyError:
                            # If the parameter has a default value, use it
                            if param.default is not param.empty:
                                args.append(param.default)
                            else:
                                raise KeyError(f"Cannot resolve dependency {param.name} of type {param_type.__name__}")
                    else:
                        # If no type hint, use default value if available
                        if param.default is not param.empty:
                            args.append(param.default)
                        else:
                            raise KeyError(f"Cannot resolve dependency {param.name} without type hint")
                
                # Create instance with resolved dependencies
                return implementation(*args)
            
            return factory
        else:
            # If implementation is already a callable, use it directly
            return implementation


# Global container instance for easy access
container = DIContainer()