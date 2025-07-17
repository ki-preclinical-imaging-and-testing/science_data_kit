"""
Core connections package for Science Data Kit.

This package provides a unified interface for connecting to various data sources,
including cloud storage, databases, APIs, and messaging systems.
"""

from .manager import ConnectionManager
from .registry import PluginRegistry

__all__ = ["ConnectionManager", "PluginRegistry"]