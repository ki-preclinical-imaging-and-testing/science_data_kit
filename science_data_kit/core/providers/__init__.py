"""
Provider Registry for Science Data Kit

This package provides a registry for data source providers, allowing the Science Data Kit
to interact with various data sources like Dropbox, Google Sheets, and Microsoft Graph.
"""

from .registry import ProviderRegistry, ProviderType, BaseProvider, registry
from .storage import DropboxProvider, GoogleSheetsProvider

# Register providers
registry.register_provider(ProviderType.STORAGE, "dropbox", DropboxProvider)
registry.register_provider(ProviderType.SPREADSHEET, "google_sheets", GoogleSheetsProvider)

__all__ = ['ProviderRegistry', 'ProviderType', 'BaseProvider', 'registry',
           'DropboxProvider', 'GoogleSheetsProvider']
