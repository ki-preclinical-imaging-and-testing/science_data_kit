"""
Interfaces Module for Science Data Kit

This module provides interfaces for core components of the Science Data Kit,
including database managers, API managers, and container managers.

These interfaces define the contracts that implementations must fulfill,
enabling dependency injection and improving testability.
"""

# Database interfaces
from .database import (
    DatabaseInterface,
    GraphDatabaseInterface,
    Neo4jDatabaseInterface,
)

# API interfaces
from .api import (
    APIInterface,
    MSGraphAPIInterface,
)

# Container interfaces
from .container import (
    ContainerInterface,
    JupyterContainerInterface,
    NeoDashContainerInterface,
)

__all__ = [
    # Database interfaces
    'DatabaseInterface',
    'GraphDatabaseInterface',
    'Neo4jDatabaseInterface',
    
    # API interfaces
    'APIInterface',
    'MSGraphAPIInterface',
    
    # Container interfaces
    'ContainerInterface',
    'JupyterContainerInterface',
    'NeoDashContainerInterface',
]