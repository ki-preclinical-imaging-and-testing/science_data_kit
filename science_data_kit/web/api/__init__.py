"""
REST API for Science Data Kit

This package contains the REST API endpoints for the Science Data Kit.
It provides a programmatic interface to the core functionality.
"""

from science_data_kit.web.api.routes import register_api_routes

__all__ = ['register_api_routes']