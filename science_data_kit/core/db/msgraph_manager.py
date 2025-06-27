"""
Microsoft Graph API Connection Manager for Science Data Kit

This module provides a connection manager for Microsoft Graph API, allowing
the Science Data Kit to interact with Microsoft 365 services.
"""

import os
import json
import pandas as pd
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from datetime import datetime, timedelta

try:
    from msgraph.core import GraphClient
    from azure.identity import ClientSecretCredential, DeviceCodeCredential, InteractiveBrowserCredential
    MSGRAPH_AVAILABLE = True
except ImportError:
    MSGRAPH_AVAILABLE = False


class MSGraphConnectionManager:
    """
    Connection manager for Microsoft Graph API.

    This class provides methods for authenticating with Microsoft Graph API
    and executing queries against it.
    """

    def __init__(self, tenant_id: str = None, client_id: str = None, client_secret: str = None,
                 auth_method: str = "device_code", config_file: str = None, 
                 enable_cache: bool = True, cache_ttl: int = 300):
        """
        Initialize the Microsoft Graph API connection manager.

        Args:
            tenant_id: The tenant ID for the Microsoft 365 account.
            client_id: The client ID for the application.
            client_secret: The client secret for the application.
            auth_method: The authentication method to use. Options are:
                - "client_credentials": For daemon or service applications
                - "device_code": For command-line tools or IoT devices
                - "interactive": For web applications
            config_file: Path to a configuration file containing authentication details.
            enable_cache: Whether to enable caching of API responses.
            cache_ttl: Time-to-live for cached responses in seconds (default: 5 minutes).
        """
        if not MSGRAPH_AVAILABLE:
            raise ImportError(
                "Microsoft Graph SDK is not installed. "
                "Please install it with 'pip install msgraph-sdk-python azure-identity'."
            )

        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_method = auth_method
        self.client = None
        self.connected = False

        # Cache settings
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        self.cache = {}  # Dictionary to store cached responses

        # Load configuration from file if provided
        if config_file:
            self._load_config(config_file)

    def _load_config(self, config_file: str) -> None:
        """
        Load configuration from a file.

        Args:
            config_file: Path to the configuration file.
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        with open(config_path, 'r') as f:
            config = json.load(f)

        self.tenant_id = config.get('tenant_id', self.tenant_id)
        self.client_id = config.get('client_id', self.client_id)
        self.client_secret = config.get('client_secret', self.client_secret)
        self.auth_method = config.get('auth_method', self.auth_method)

        # Load cache settings if provided
        if 'enable_cache' in config:
            self.enable_cache = config.get('enable_cache')
        if 'cache_ttl' in config:
            self.cache_ttl = config.get('cache_ttl')

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

    def connect(self) -> bool:
        """
        Connect to Microsoft Graph API.

        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            # Create the appropriate credential based on the authentication method
            if self.auth_method == "client_credentials":
                if not all([self.tenant_id, self.client_id, self.client_secret]):
                    raise ValueError("tenant_id, client_id, and client_secret are required for client_credentials auth")

                credential = ClientSecretCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )

            elif self.auth_method == "device_code":
                if not all([self.tenant_id, self.client_id]):
                    raise ValueError("tenant_id and client_id are required for device_code auth")

                credential = DeviceCodeCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id
                )

            elif self.auth_method == "interactive":
                if not all([self.tenant_id, self.client_id]):
                    raise ValueError("tenant_id and client_id are required for interactive auth")

                credential = InteractiveBrowserCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id
                )

            else:
                raise ValueError(f"Unsupported authentication method: {self.auth_method}")

            # Create the Graph client
            self.client = GraphClient(credential=credential)

            # Test the connection
            response = self.client.get('/me')
            if response.status_code == 200:
                self.connected = True
                return True
            else:
                self.connected = False
                return False

        except Exception as e:
            self.connected = False
            print(f"Error connecting to Microsoft Graph API: {str(e)}")
            return False

    def execute_query(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None, 
                  use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute a query against Microsoft Graph API.

        Args:
            resource_path: The resource path to query (e.g., '/me', '/users').
            query_parameters: Optional query parameters.
            use_cache: Whether to use the cache for this query (default: True).

        Returns:
            The response from Microsoft Graph API as a dictionary.
        """
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to Microsoft Graph API. Call connect() first.")

        # Generate the full resource path with query parameters
        full_resource_path = resource_path
        if query_parameters:
            # Convert query parameters to URL parameters
            params = '&'.join([f'${k}={v}' for k, v in query_parameters.items()])
            if '?' in resource_path:
                full_resource_path = f"{resource_path}&{params}"
            else:
                full_resource_path = f"{resource_path}?{params}"

        # Check if the response is in the cache
        if use_cache and self.enable_cache:
            cache_key = self._get_cache_key(resource_path, query_parameters)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                return cached_response

        # Execute the query
        response = self.client.get(full_resource_path)

        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()

            # Store the response in the cache
            if use_cache and self.enable_cache:
                cache_key = self._get_cache_key(resource_path, query_parameters)
                self._store_in_cache(cache_key, response_data)

            return response_data
        else:
            raise Exception(f"Error executing query: {response.status_code} - {response.text}")

    def query_to_dataframe(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None,
                       use_cache: bool = True) -> pd.DataFrame:
        """
        Execute a query and return results as a pandas DataFrame.

        Args:
            resource_path: The resource path to query (e.g., '/me', '/users').
            query_parameters: Optional query parameters.
            use_cache: Whether to use the cache for this query (default: True).

        Returns:
            A pandas DataFrame containing the query results.
        """
        response = self.execute_query(resource_path, query_parameters, use_cache)

        # Check if the response contains a 'value' field (collection)
        if 'value' in response:
            return pd.DataFrame(response['value'])
        else:
            # Single entity response
            return pd.DataFrame([response])

    def get_users(self, query_parameters: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> pd.DataFrame:
        """
        Get users from Microsoft Graph API.

        Args:
            query_parameters: Optional query parameters.
            use_cache: Whether to use the cache for this query (default: True).

        Returns:
            A pandas DataFrame containing user information.
        """
        return self.query_to_dataframe('/users', query_parameters, use_cache)

    def get_groups(self, query_parameters: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> pd.DataFrame:
        """
        Get groups from Microsoft Graph API.

        Args:
            query_parameters: Optional query parameters.
            use_cache: Whether to use the cache for this query (default: True).

        Returns:
            A pandas DataFrame containing group information.
        """
        return self.query_to_dataframe('/groups', query_parameters, use_cache)

    def get_me(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get information about the current user.

        Args:
            use_cache: Whether to use the cache for this query (default: True).

        Returns:
            A dictionary containing information about the current user.
        """
        return self.execute_query('/me', use_cache=use_cache)

    def get_my_messages(self, query_parameters: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> pd.DataFrame:
        """
        Get messages for the current user.

        Args:
            query_parameters: Optional query parameters.
            use_cache: Whether to use the cache for this query (default: True).

        Returns:
            A pandas DataFrame containing message information.
        """
        return self.query_to_dataframe('/me/messages', query_parameters, use_cache)

    def get_my_events(self, query_parameters: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> pd.DataFrame:
        """
        Get calendar events for the current user.

        Args:
            query_parameters: Optional query parameters.
            use_cache: Whether to use the cache for this query (default: True).

        Returns:
            A pandas DataFrame containing event information.
        """
        return self.query_to_dataframe('/me/events', query_parameters, use_cache)

    def get_my_files(self, query_parameters: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> pd.DataFrame:
        """
        Get files for the current user.

        Args:
            query_parameters: Optional query parameters.
            use_cache: Whether to use the cache for this query (default: True).

        Returns:
            A pandas DataFrame containing file information.
        """
        return self.query_to_dataframe('/me/drive/root/children', query_parameters, use_cache)
