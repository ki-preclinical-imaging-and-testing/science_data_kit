"""
Provider Registry for Science Data Kit

This package provides a registry for data source providers, allowing the Science Data Kit
to interact with various data sources like Dropbox, Google Sheets, and Microsoft Graph.
"""

from .registry import ProviderRegistry, ProviderType, BaseProvider, registry
from .abstract_providers import StorageProvider, DatabaseProvider, APIProvider
from .storage import DropboxProvider, GoogleSheetsProvider
from .api import MSGraphProvider

# Register providers
registry.register_provider(ProviderType.STORAGE, "dropbox", DropboxProvider)
registry.register_provider(ProviderType.SPREADSHEET, "google_sheets", GoogleSheetsProvider)
registry.register_provider(ProviderType.API, "msgraph", MSGraphProvider)

__all__ = ['ProviderRegistry', 'ProviderType', 'BaseProvider', 'registry',
           'StorageProvider', 'DatabaseProvider', 'APIProvider',
           'DropboxProvider', 'GoogleSheetsProvider', 'MSGraphProvider']
