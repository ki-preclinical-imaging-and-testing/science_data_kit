"""
Dependency Injection Module for Science Data Kit

This module provides a dependency injection system for the Science Data Kit,
allowing for loose coupling between components and easier testing.

The module includes:
- A dependency injection container for registering and resolving dependencies
- Providers for different component lifetimes (singleton, transient, etc.)
- Decorators for easy integration with existing code
"""

# Import public interfaces
from .interfaces import Container, Provider, Injector

# Import container implementation
from .container import DIContainer, container

# Import provider implementations
from .providers import (
    SingletonProvider,
    TransientProvider,
    InstanceProvider,
    FactoryProvider,
)

# Import decorators
from .decorators import (
    injectable,
    singleton,
    provides,
    singleton_provides,
    inject,
)

__all__ = [
    # Interfaces
    'Container',
    'Provider',
    'Injector',
    
    # Container
    'DIContainer',
    'container',
    
    # Providers
    'SingletonProvider',
    'TransientProvider',
    'InstanceProvider',
    'FactoryProvider',
    
    # Decorators
    'injectable',
    'singleton',
    'provides',
    'singleton_provides',
    'inject',
]