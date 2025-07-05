"""
Provider Registry for Science Data Kit

This package provides a registry for data source providers, allowing the Science Data Kit
to interact with various data sources like Dropbox, Google Sheets, and Microsoft Graph.
"""

from .registry import ProviderRegistry, ProviderType, BaseProvider, registry
from .abstract_providers import StorageProvider, DatabaseProvider, APIProvider
from .storage import DropboxProvider, GoogleSheetsProvider
from .api import MSGraphProvider
from .database.mongodb_provider import MongoDBProvider
from .database.sparql_provider import SPARQLProvider
from .database.elasticsearch_provider import ElasticsearchProvider

# Register providers
registry.register_provider(ProviderType.STORAGE, "dropbox", DropboxProvider)
registry.register_provider(ProviderType.SPREADSHEET, "google_sheets", GoogleSheetsProvider)
registry.register_provider(ProviderType.API, "msgraph", MSGraphProvider)
registry.register_provider(ProviderType.DATABASE, "mongodb", MongoDBProvider)
registry.register_provider(ProviderType.DATABASE, "sparql", SPARQLProvider)
registry.register_provider(ProviderType.DATABASE, "elasticsearch", ElasticsearchProvider)

__all__ = ['ProviderRegistry', 'ProviderType', 'BaseProvider', 'registry',
           'StorageProvider', 'DatabaseProvider', 'APIProvider',
           'DropboxProvider', 'GoogleSheetsProvider', 'MSGraphProvider',
           'MongoDBProvider', 'SPARQLProvider', 'ElasticsearchProvider']
