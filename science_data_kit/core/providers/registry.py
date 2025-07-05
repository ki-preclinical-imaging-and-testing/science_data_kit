"""
Provider Registry for Science Data Kit

This module provides a registry for data source providers, allowing the Science Data Kit
to interact with various data sources like Dropbox, Google Sheets, and Microsoft Graph.
"""

import enum
from abc import ABC, abstractmethod
from typing import Dict, Any, Type, Optional, List, Callable


class ProviderType(enum.Enum):
    """Enumeration of provider types supported by the Science Data Kit."""

    STORAGE = "storage"  # Providers for file storage (Dropbox, Google Drive, etc.)
    SPREADSHEET = "spreadsheet"  # Providers for spreadsheet data (Google Sheets, Excel, etc.)
    DATABASE = "database"  # Providers for database connections
    API = "api"  # Providers for API connections (MS Graph, etc.)
    MESSAGING = "messaging"  # Providers for messaging systems (Kafka, RabbitMQ, etc.)

    def __str__(self) -> str:
        """Return the string representation of the provider type."""
        return self.value


class BaseProvider(ABC):
    """
    Base class for all data source providers.

    This abstract class defines the interface that all providers must implement.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the provider with configuration.

        Args:
            config: Configuration dictionary for the provider
        """
        self.config = config
        self.is_initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the provider with the provided configuration.

        Returns:
            True if initialization was successful, False otherwise
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy and can be used.

        Returns:
            True if the provider is healthy, False otherwise
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the provider.

        Returns:
            Dictionary of provider capabilities
        """
        pass


class ProviderRegistry:
    """
    Registry for data source providers.

    This class manages the registration and retrieval of providers.
    """

    def __init__(self):
        """Initialize the provider registry."""
        self._providers: Dict[ProviderType, Dict[str, Type[BaseProvider]]] = {
            provider_type: {} for provider_type in ProviderType
        }
        self._instances: Dict[ProviderType, Dict[str, BaseProvider]] = {
            provider_type: {} for provider_type in ProviderType
        }

    def register_provider(self, provider_type: ProviderType, name: str, 
                         provider_class: Type[BaseProvider]) -> None:
        """
        Register a provider class with the registry.

        Args:
            provider_type: Type of the provider
            name: Name of the provider
            provider_class: Provider class to register
        """
        if not issubclass(provider_class, BaseProvider):
            raise TypeError(f"Provider class must be a subclass of BaseProvider")

        self._providers[provider_type][name] = provider_class

    def get_provider_class(self, provider_type: ProviderType, name: str) -> Optional[Type[BaseProvider]]:
        """
        Get a provider class from the registry.

        Args:
            provider_type: Type of the provider
            name: Name of the provider

        Returns:
            Provider class if found, None otherwise
        """
        return self._providers[provider_type].get(name)

    def get_provider_names(self, provider_type: ProviderType) -> List[str]:
        """
        Get a list of registered provider names for a given type.

        Args:
            provider_type: Type of the provider

        Returns:
            List of provider names
        """
        return list(self._providers[provider_type].keys())

    def create_provider(self, provider_type: ProviderType, name: str, 
                       config: Dict[str, Any]) -> Optional[BaseProvider]:
        """
        Create a provider instance.

        Args:
            provider_type: Type of the provider
            name: Name of the provider
            config: Configuration for the provider

        Returns:
            Provider instance if created successfully, None otherwise
        """
        provider_class = self.get_provider_class(provider_type, name)
        if provider_class is None:
            return None

        provider = provider_class(config)
        self._instances[provider_type][name] = provider
        return provider

    def get_provider(self, provider_type: ProviderType, name: str) -> Optional[BaseProvider]:
        """
        Get a provider instance from the registry.

        Args:
            provider_type: Type of the provider
            name: Name of the provider

        Returns:
            Provider instance if found, None otherwise
        """
        return self._instances[provider_type].get(name)

    def get_all_providers(self, provider_type: Optional[ProviderType] = None) -> Dict[str, BaseProvider]:
        """
        Get all provider instances of a given type.

        Args:
            provider_type: Type of the provider, or None for all types

        Returns:
            Dictionary of provider instances
        """
        if provider_type is None:
            # Flatten all provider instances into a single dictionary
            result = {}
            for provider_type in ProviderType:
                result.update(self._instances[provider_type])
            return result

        return self._instances[provider_type]


# Create a singleton instance of the provider registry
registry = ProviderRegistry()
