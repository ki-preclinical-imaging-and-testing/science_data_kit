"""
Flask Adapters for Science Data Kit

This package contains adapter classes that translate core page data into Flask templates and API responses.
"""

from science_data_kit.web.adapters.flask_adapter import render_page_html, render_page_api

__all__ = ['render_page_html', 'render_page_api']