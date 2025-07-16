"""
Flask Web Application for Science Data Kit

This package contains the Flask web application for the Science Data Kit.
It provides a web interface and REST API for the core functionality.
"""

from science_data_kit.web.app import create_app

__all__ = ['create_app']