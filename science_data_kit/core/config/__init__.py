"""
Configuration Module for Science Data Kit

This package provides configuration management for the Science Data Kit,
including provider configuration, application settings, and environment variables.
"""

from .providers import load_provider_config

__all__ = ['load_provider_config']