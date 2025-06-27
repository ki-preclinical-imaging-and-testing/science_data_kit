"""
Base API Manager for Science Data Kit

This module provides a base class for API connection managers, defining
common patterns and standardizing error handling across different API integrations.
"""

import json
import time
from typing import Dict, Any, Optional
from pathlib import Path
from abc import ABC, abstractmethod


class APIError(Exception):
    """Base exception for API-related errors."""
    pass


class ConnectionError(APIError):
    """Exception raised when there is an error connecting to the API."""
    pass


class AuthenticationError(APIError):
    """Exception raised when there is an authentication error."""
    pass


class QueryError(APIError):
    """Exception raised when there is an error executing a query."""
    pass


class ConfigurationError(APIError):
    """Exception raised when there is an error in the configuration."""
    pass


class CacheableMixin:
    """
    Mixin that provides caching functionality for API responses.
    """
    
    def __init__(self, enable_cache: bool = True, cache_ttl: int = 300):
        """
        Initialize the caching functionality.
        
        Args:
            enable_cache: Whether to enable caching of API responses.
            cache_ttl: Time-to-live for cached responses in seconds (default: 5 minutes).
        """
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        self.cache = {}  # Dictionary to store cached responses
    
    def _get_cache_key(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a cache key for a query.
        
        Args:
            resource_path: The resource path to query.
            query_parameters: Optional query parameters.
            
        Returns:
            A string that can be used as a cache key.
        """
        if query_parameters:
            # Sort the parameters to ensure consistent cache keys
            sorted_params = sorted(query_parameters.items())
            return f"{resource_path}:{json.dumps(sorted_params)}"
        else:
            return resource_path
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if a cached response is still valid.
        
        Args:
            cache_key: The cache key to check.
            
        Returns:
            True if the cached response is valid, False otherwise.
        """
        if not self.enable_cache or cache_key not in self.cache:
            return False
        
        timestamp, _ = self.cache[cache_key]
        current_time = time.time()
        
        # Check if the cached response has expired
        return current_time - timestamp < self.cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a response from the cache.
        
        Args:
            cache_key: The cache key to retrieve.
            
        Returns:
            The cached response, or None if the cache is invalid.
        """
        if self._is_cache_valid(cache_key):
            _, response = self.cache[cache_key]
            return response
        return None
    
    def _store_in_cache(self, cache_key: str, response: Dict[str, Any]) -> None:
        """
        Store a response in the cache.
        
        Args:
            cache_key: The cache key to store.
            response: The response to cache.
        """
        if self.enable_cache:
            self.cache[cache_key] = (time.time(), response)
    
    def clear_cache(self) -> None:
        """
        Clear the cache.
        """
        self.cache = {}


class ConfigurableMixin:
    """
    Mixin that provides configuration loading functionality.
    """
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_file: Path to the configuration file.
            
        Returns:
            The configuration as a dictionary.
            
        Raises:
            ConfigurationError: If there is an error loading the configuration.
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {str(e)}")
        except IOError as e:
            raise ConfigurationError(f"Error reading configuration file: {str(e)}")


class APIManagerBase(ABC, CacheableMixin, ConfigurableMixin):
    """
    Base class for API connection managers.
    
    This class defines the common interface and functionality for all API connection managers.
    """
    
    def __init__(self, config_file: str = None, enable_cache: bool = True, cache_ttl: int = 300):
        """
        Initialize the API connection manager.
        
        Args:
            config_file: Path to a configuration file containing authentication details.
            enable_cache: Whether to enable caching of API responses.
            cache_ttl: Time-to-live for cached responses in seconds (default: 5 minutes).
        """
        CacheableMixin.__init__(self, enable_cache, cache_ttl)
        self.connected = False
        
        # Load configuration from file if provided
        if config_file:
            self.config = self._load_config(config_file)
        else:
            self.config = {}
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the API.
        
        Returns:
            True if connection is successful, False otherwise.
            
        Raises:
            ConnectionError: If there is an error connecting to the API.
            AuthenticationError: If there is an authentication error.
        """
        pass
    
    @abstractmethod
    def execute_query(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None, 
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute a query against the API.
        
        Args:
            resource_path: The resource path to query.
            query_parameters: Optional query parameters.
            use_cache: Whether to use the cache for this query.
            
        Returns:
            The response from the API as a dictionary.
            
        Raises:
            ConnectionError: If not connected to the API.
            QueryError: If there is an error executing the query.
        """
        pass
    
    def build_query(self, resource_path: str, **kwargs) -> Dict[str, Any]:
        """
        Build a query with parameters.
        
        Args:
            resource_path: The resource path to query.
            **kwargs: Query parameters.
            
        Returns:
            A dictionary containing the query parameters.
        """
        query_params = {}
        
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, list):
                    query_params[key] = ','.join(value)
                else:
                    query_params[key] = str(value)
        
        return query_params