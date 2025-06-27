"""
Microsoft Graph API Connection Manager for Science Data Kit

This module provides a connection manager for Microsoft Graph API, allowing
the Science Data Kit to interact with Microsoft 365 services.
"""

import os
import json
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from datetime import datetime, timedelta

from science_data_kit.core.db.api_manager_base import (
    APIManagerBase, ConnectionError, AuthenticationError, QueryError, ConfigurationError
)

try:
    from msgraph.core import GraphClient
    from azure.identity import ClientSecretCredential, DeviceCodeCredential, InteractiveBrowserCredential
    MSGRAPH_AVAILABLE = True
except ImportError:
    MSGRAPH_AVAILABLE = False


class MSGraphConnectionManager(APIManagerBase):
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

        Raises:
            ImportError: If the Microsoft Graph SDK is not installed.
        """
        if not MSGRAPH_AVAILABLE:
            raise ImportError(
                "Microsoft Graph SDK is not installed. "
                "Please install it with 'pip install msgraph-sdk-python azure-identity'."
            )

        # Initialize the base class
        super().__init__(config_file, enable_cache, cache_ttl)

        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_method = auth_method
        self.client = None

        # Load configuration from file if provided
        if config_file:
            self._load_config_values(config_file)

    def _load_config_values(self, config_file: str) -> None:
        """
        Load configuration values from a file.

        Args:
            config_file: Path to the configuration file.

        Raises:
            ConfigurationError: If there is an error loading the configuration.
        """
        try:
            config = self._load_config(config_file)

            self.tenant_id = config.get('tenant_id', self.tenant_id)
            self.client_id = config.get('client_id', self.client_id)
            self.client_secret = config.get('client_secret', self.client_secret)
            self.auth_method = config.get('auth_method', self.auth_method)

            # Load cache settings if provided
            if 'enable_cache' in config:
                self.enable_cache = config.get('enable_cache')
            if 'cache_ttl' in config:
                self.cache_ttl = config.get('cache_ttl')
        except ConfigurationError as e:
            raise ConfigurationError(f"Error loading Microsoft Graph API configuration: {str(e)}")

    def connect(self) -> bool:
        """
        Connect to Microsoft Graph API.

        Returns:
            True if connection is successful, False otherwise.

        Raises:
            AuthenticationError: If there is an error with the authentication credentials.
            ConnectionError: If there is an error connecting to the API.
        """
        try:
            # Create the appropriate credential based on the authentication method
            if self.auth_method == "client_credentials":
                if not all([self.tenant_id, self.client_id, self.client_secret]):
                    raise AuthenticationError("tenant_id, client_id, and client_secret are required for client_credentials auth")

                credential = ClientSecretCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )

            elif self.auth_method == "device_code":
                if not all([self.tenant_id, self.client_id]):
                    raise AuthenticationError("tenant_id and client_id are required for device_code auth")

                credential = DeviceCodeCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id
                )

            elif self.auth_method == "interactive":
                if not all([self.tenant_id, self.client_id]):
                    raise AuthenticationError("tenant_id and client_id are required for interactive auth")

                credential = InteractiveBrowserCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id
                )

            else:
                raise AuthenticationError(f"Unsupported authentication method: {self.auth_method}")

            # Create the Graph client
            self.client = GraphClient(credential=credential)

            # Test the connection
            response = self.client.get('/me')
            if response.status_code == 200:
                self.connected = True
                return True
            else:
                self.connected = False
                raise ConnectionError(f"Error connecting to Microsoft Graph API: {response.status_code} - {response.text}")

        except AuthenticationError:
            self.connected = False
            raise
        except Exception as e:
            self.connected = False
            raise ConnectionError(f"Error connecting to Microsoft Graph API: {str(e)}")

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

        Raises:
            ConnectionError: If not connected to Microsoft Graph API.
            QueryError: If there is an error executing the query.
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

        try:
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
                raise QueryError(f"Error executing query: {response.status_code} - {response.text}")
        except Exception as e:
            if isinstance(e, QueryError):
                raise
            raise QueryError(f"Error executing query: {str(e)}")

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

        Raises:
            ConnectionError: If not connected to Microsoft Graph API.
            QueryError: If there is an error executing the query.
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

        Raises:
            ConnectionError: If not connected to Microsoft Graph API.
            QueryError: If there is an error executing the query.
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

        Raises:
            ConnectionError: If not connected to Microsoft Graph API.
            QueryError: If there is an error executing the query.
        """
        return self.query_to_dataframe('/groups', query_parameters, use_cache)

    def get_me(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get information about the current user.

        Args:
            use_cache: Whether to use the cache for this query (default: True).

        Returns:
            A dictionary containing information about the current user.

        Raises:
            ConnectionError: If not connected to Microsoft Graph API.
            QueryError: If there is an error executing the query.
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

        Raises:
            ConnectionError: If not connected to Microsoft Graph API.
            QueryError: If there is an error executing the query.
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

        Raises:
            ConnectionError: If not connected to Microsoft Graph API.
            QueryError: If there is an error executing the query.
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

        Raises:
            ConnectionError: If not connected to Microsoft Graph API.
            QueryError: If there is an error executing the query.
        """
        return self.query_to_dataframe('/me/drive/root/children', query_parameters, use_cache)
