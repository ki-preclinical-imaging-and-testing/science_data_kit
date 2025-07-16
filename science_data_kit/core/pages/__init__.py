"""
Core Pages Package for Science Data Kit

This package provides framework-independent page classes for the Science Data Kit application.
These classes define the business logic for pages without any UI-specific code.
"""

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.pages.dashboard import DashboardPage

__all__ = ['BasePage', 'DashboardPage']