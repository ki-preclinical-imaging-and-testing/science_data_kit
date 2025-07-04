"""
Dependency Injection Decorators for Science Data Kit

This module provides decorators for easy integration with the dependency injection system,
including decorators for registering components and injecting dependencies.
"""

import inspect
import functools
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, get_type_hints

from .container import container

# Type variables for generic typing
T = TypeVar('T')
F = TypeVar('F', bound=Callable)


def injectable(cls: Type[T]) -> Type[T]:
    """
    Decorator for classes that can be injected.
    
    This decorator registers the class with the container as a transient instance.
    
    Args:
        cls: The class to register.
        
    Returns:
        The same class, now registered with the container.
    """
    # Register the class with itself as the interface
    container.register(cls, cls)
    return cls


def singleton(cls: Type[T]) -> Type[T]:
    """
    Decorator for singleton classes.
    
    This decorator registers the class with the container as a singleton instance.
    
    Args:
        cls: The class to register.
        
    Returns:
        The same class, now registered with the container as a singleton.
    """
    # Register the class with itself as the interface, as a singleton
    container.register(cls, cls, singleton=True)
    return cls


def provides(interface: Type[T]) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for classes that provide an interface.
    
    This decorator registers the class with the container as an implementation of the specified interface.
    
    Args:
        interface: The interface that the class provides.
        
    Returns:
        A decorator function that registers the class with the container.
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Register the class as an implementation of the interface
        container.register(interface, cls)
        return cls
    return decorator


def singleton_provides(interface: Type[T]) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for singleton classes that provide an interface.
    
    This decorator registers the class with the container as a singleton implementation of the specified interface.
    
    Args:
        interface: The interface that the class provides.
        
    Returns:
        A decorator function that registers the class with the container as a singleton.
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Register the class as a singleton implementation of the interface
        container.register(interface, cls, singleton=True)
        return cls
    return decorator


def inject(func: F) -> F:
    """
    Decorator for methods that need dependencies injected.
    
    This decorator resolves dependencies for method parameters from the container.
    
    Args:
        func: The method to inject dependencies into.
        
    Returns:
        A wrapped method that has dependencies injected.
    """
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a new kwargs dict with injected dependencies
        new_kwargs = kwargs.copy()
        
        # Get parameters that aren't already provided
        provided_params = set(kwargs.keys())
        if args:
            # Skip 'self' or 'cls' parameter for methods
            is_method = inspect.ismethod(func) or (len(args) > 0 and isinstance(args[0], type))
            offset = 1 if is_method else 0
            provided_params.update(list(signature.parameters.keys())[offset:offset+len(args)])
        
        # Inject dependencies for parameters with type hints
        for param_name, param in signature.parameters.items():
            if param_name in provided_params:
                continue
            
            if param_name in type_hints:
                param_type = type_hints[param_name]
                try:
                    # Resolve the dependency from the container
                    new_kwargs[param_name] = container.resolve(param_type)
                except KeyError:
                    # If the parameter has a default value, use it
                    if param.default is not param.empty:
                        new_kwargs[param_name] = param.default
                    # Otherwise, let the function handle the missing parameter
            elif param.default is not param.empty:
                # If no type hint but has default, use the default
                new_kwargs[param_name] = param.default
        
        # Call the original function with injected dependencies
        return func(*args, **new_kwargs)
    
    return wrapper