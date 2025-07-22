"""
Globus plugin for Science Data Kit.

This plugin provides integration with Globus for large-scale data transfer
and management, particularly for research facilities and institutes dealing with
multi-institutional collaborations and high-performance computing environments.
"""

from .globus_plugin import GlobusPlugin

__all__ = ['GlobusPlugin']