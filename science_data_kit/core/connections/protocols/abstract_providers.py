"""
Abstract Provider Classes for Science Data Kit

This module provides abstract base classes for different types of providers,
defining the interfaces that specific provider implementations must follow.

This is a compatibility layer that re-exports the classes from the original
abstract_providers.py file to maintain backward compatibility while moving
to the new plugin architecture.
"""

import warnings
from typing import Dict, List, Optional, Any, Union, Tuple, Callable

import pandas as pd

from science_data_kit.core.providers.abstract_providers import (
    StorageProvider,
    DatabaseProvider,
    APIProvider,
    MessagingProvider,
)

# Emit deprecation warning
warnings.warn(
    "The abstract_providers module has been moved to science_data_kit.core.connections.protocols. "
    "Please update your imports to use the new location.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    "StorageProvider",
    "DatabaseProvider",
    "APIProvider",
    "MessagingProvider",
]