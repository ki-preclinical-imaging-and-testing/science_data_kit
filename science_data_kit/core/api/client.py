"""
Python Client Library for Science Data Kit API

This module provides a Python client library for interacting with the Science Data Kit API,
making it easy to integrate the SDK's functionality into external Python applications.
"""

import requests
import json
from typing import Any, Dict, List, Optional, Union, Tuple
import logging
from enum import Enum
from datetime import datetime
import time
from .cache import APICache

logger = logging.getLogger(__name__)


class APIClientError(Exception):
    """Exception raised for errors in the API client."""

    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response: Optional[Dict[str, Any]] = None):
        """
        Initialize the API client error.

        Args:
            message: The error message.
            status_code: The HTTP status code.
            response: The response from the API.
        """
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class APIClient:
    """Client for interacting with the Science Data Kit API."""

    def __init__(self, base_url: str, timeout: int = 30, enable_cache: bool = True,
                 cache_max_size: int = 100, cache_default_ttl: Optional[int] = 300):
        """
        Initialize the API client.

        Args:
            base_url: The base URL of the API.
            timeout: The timeout for API requests in seconds.
            enable_cache: Whether to enable caching of API responses.
            cache_max_size: The maximum number of entries in the cache.
            cache_default_ttl: The default time-to-live for cache entries in seconds,
                              or None for no expiration.
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.token = None
        self.session = requests.Session()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize cache
        self.cache = APICache(max_size=cache_max_size, default_ttl=cache_default_ttl)
        self.enable_cache = enable_cache

        # Define cacheable endpoints (method, path, ttl)
        self.cacheable_endpoints = [
            ("GET", "/api/session", 60),
            ("GET", "/api/database", 60),
            ("GET", "/api/database/query", 300)
        ]

    def _make_url(self, path: str) -> str:
        """
        Make a full URL from a path.

        Args:
            path: The path to append to the base URL.

        Returns:
            The full URL.
        """
        path = path.lstrip('/')
        return f"{self.base_url}/{path}"

    def _get_headers(self) -> Dict[str, str]:
        """
        Get the headers for API requests.

        Returns:
            The headers.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle an API response.

        Args:
            response: The response from the API.

        Returns:
            The parsed response data.

        Raises:
            APIClientError: If the response indicates an error.
        """
        try:
            data = response.json()
        except ValueError:
            raise APIClientError(
                message=f"Invalid JSON response: {response.text}",
                status_code=response.status_code
            )

        if not response.ok:
            error_message = "Unknown error"
            if "error" in data and "message" in data["error"]:
                error_message = data["error"]["message"]

            raise APIClientError(
                message=error_message,
                status_code=response.status_code,
                response=data
            )

        return data

    def _is_cacheable(self, method: str, path: str) -> Tuple[bool, Optional[int]]:
        """
        Check if a request is cacheable.

        Args:
            method: The HTTP method.
            path: The request path.

        Returns:
            A tuple (cacheable, ttl) where cacheable is True if the request is cacheable,
            and ttl is the time-to-live for the cache entry (or None to use the default).
        """
        if not self.enable_cache:
            return False, None

        # Only cache GET requests by default
        if method != "GET" and not any(method == m for m, p, _ in self.cacheable_endpoints if p == path):
            return False, None

        # Check if the endpoint is in the list of cacheable endpoints
        for m, p, ttl in self.cacheable_endpoints:
            if method == m and path == p:
                return True, ttl

        # Default to cacheable for GET requests
        return method == "GET", None

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, 
                data: Optional[Dict[str, Any]] = None, skip_cache: bool = False) -> Dict[str, Any]:
        """
        Make an API request.

        Args:
            method: The HTTP method (GET, POST, PUT, DELETE, etc.).
            path: The request path.
            params: The query parameters.
            data: The request body.
            skip_cache: Whether to skip the cache for this request.

        Returns:
            The parsed response data.

        Raises:
            APIClientError: If the request fails.
        """
        url = self._make_url(path)
        headers = self._get_headers()

        # Check if the request is cacheable
        cacheable, ttl = self._is_cacheable(method, path)

        # Check the cache if the request is cacheable and we're not skipping the cache
        if cacheable and not skip_cache:
            cache_hit, cached_data = self.cache.get(method, path, params, data)
            if cache_hit:
                self.logger.debug(f"Cache hit for {method} {path}")
                return cached_data

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=self.timeout
            )

            response_data = self._handle_response(response)

            # Cache the response if the request is cacheable
            if cacheable and not skip_cache:
                self.cache.set(method, path, response_data, ttl, params, data)

            return response_data
        except requests.RequestException as e:
            raise APIClientError(f"Request failed: {str(e)}")

    def enable_caching(self, enable: bool = True) -> None:
        """
        Enable or disable caching.

        Args:
            enable: Whether to enable caching.
        """
        self.enable_cache = enable
        self.logger.debug(f"Caching {'enabled' if enable else 'disabled'}")

    def clear_cache(self) -> int:
        """
        Clear the cache.

        Returns:
            The number of entries cleared.
        """
        count = self.cache.clear()
        self.logger.debug(f"Cleared {count} cache entries")
        return count

    def invalidate_cache(self, method: Optional[str] = None, path: Optional[str] = None) -> int:
        """
        Invalidate cache entries matching the given criteria.

        Args:
            method: The HTTP method to match, or None to match any method.
            path: The request path to match, or None to match any path.

        Returns:
            The number of entries invalidated.
        """
        count = self.cache.invalidate(method, path)
        self.logger.debug(f"Invalidated {count} cache entries")
        return count

    def login(self, user_id: str) -> Dict[str, Any]:
        """
        Log in to the API.

        Args:
            user_id: The user ID to log in with.

        Returns:
            The login response data.
        """
        response = self._request(
            method="POST",
            path="/api/session/login",
            data={"user_id": user_id}
        )

        if "token" in response:
            self.token = response["token"]

        return response

    def logout(self) -> Dict[str, Any]:
        """
        Log out from the API.

        Returns:
            The logout response data.
        """
        if not self.token:
            return {"message": "Not logged in"}

        response = self._request(
            method="DELETE",
            path="/api/session/logout"
        )

        self.token = None

        return response

    def get_session(self) -> Dict[str, Any]:
        """
        Get session information.

        Returns:
            The session information.
        """
        return self._request(
            method="GET",
            path="/api/session"
        )

    def create_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new session.

        Args:
            data: The session data.

        Returns:
            The created session data.
        """
        return self._request(
            method="POST",
            path="/api/session",
            data=data
        )

    def update_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a session.

        Args:
            data: The updated session data.

        Returns:
            The updated session data.
        """
        return self._request(
            method="PUT",
            path="/api/session",
            data=data
        )

    def delete_session(self) -> Dict[str, Any]:
        """
        Delete a session.

        Returns:
            The response data.
        """
        return self._request(
            method="DELETE",
            path="/api/session"
        )

    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information.

        Returns:
            The database information.
        """
        return self._request(
            method="GET",
            path="/api/database"
        )

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a database query.

        Args:
            query: The query to execute.
            params: The query parameters.

        Returns:
            The query results.
        """
        data = {"query": query}
        if params:
            data["params"] = params

        return self._request(
            method="POST",
            path="/api/database/query",
            data=data
        )

    def create_database(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new database.

        Args:
            data: The database data.

        Returns:
            The created database data.
        """
        return self._request(
            method="POST",
            path="/api/database",
            data=data
        )

    def update_database(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a database.

        Args:
            data: The updated database data.

        Returns:
            The updated database data.
        """
        return self._request(
            method="PUT",
            path="/api/database",
            data=data
        )

    def delete_database(self) -> Dict[str, Any]:
        """
        Delete a database.

        Returns:
            The response data.
        """
        return self._request(
            method="DELETE",
            path="/api/database"
        )


class SDKClient:
    """
    High-level client for the Science Data Kit API.

    This class provides a more user-friendly interface for common SDK operations.
    """

    def __init__(self, base_url: str, user_id: Optional[str] = None, enable_cache: bool = True,
                 cache_max_size: int = 100, cache_default_ttl: Optional[int] = 300):
        """
        Initialize the SDK client.

        Args:
            base_url: The base URL of the API.
            user_id: The user ID to log in with. If provided, the client will automatically log in.
            enable_cache: Whether to enable caching of API responses.
            cache_max_size: The maximum number of entries in the cache.
            cache_default_ttl: The default time-to-live for cache entries in seconds,
                              or None for no expiration.
        """
        self.api_client = APIClient(base_url, enable_cache=enable_cache,
                                   cache_max_size=cache_max_size, cache_default_ttl=cache_default_ttl)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        if user_id:
            self.login(user_id)

    def login(self, user_id: str) -> Dict[str, Any]:
        """
        Log in to the SDK.

        Args:
            user_id: The user ID to log in with.

        Returns:
            The login response data.
        """
        return self.api_client.login(user_id)

    def logout(self) -> Dict[str, Any]:
        """
        Log out from the SDK.

        Returns:
            The logout response data.
        """
        return self.api_client.logout()

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get information about the current user.

        Returns:
            The user information.
        """
        return self.api_client.get_session()

    def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a database query and return the results.

        Args:
            query: The query to execute.
            params: The query parameters.

        Returns:
            The query results.
        """
        response = self.api_client.execute_query(query, params)
        return response.get("results", [])

    def create_session_with_database(self, session_name: str, database_name: str) -> Dict[str, Any]:
        """
        Create a new session with a database.

        Args:
            session_name: The name of the session.
            database_name: The name of the database.

        Returns:
            The created session data.
        """
        # Create the database
        database_response = self.api_client.create_database({
            "name": database_name
        })

        # Create the session with the database
        session_response = self.api_client.create_session({
            "name": session_name,
            "database_id": database_response.get("database_id")
        })

        return session_response

    def enable_caching(self, enable: bool = True) -> None:
        """
        Enable or disable caching.

        Args:
            enable: Whether to enable caching.
        """
        self.api_client.enable_caching(enable)

    def clear_cache(self) -> int:
        """
        Clear the cache.

        Returns:
            The number of entries cleared.
        """
        return self.api_client.clear_cache()

    def invalidate_cache(self, method: Optional[str] = None, path: Optional[str] = None) -> int:
        """
        Invalidate cache entries matching the given criteria.

        Args:
            method: The HTTP method to match, or None to match any method.
            path: The request path to match, or None to match any path.

        Returns:
            The number of entries invalidated.
        """
        return self.api_client.invalidate_cache(method, path)

    def query_with_cache(self, query: str, params: Optional[Dict[str, Any]] = None, 
                        skip_cache: bool = False) -> List[Dict[str, Any]]:
        """
        Execute a database query and return the results, with optional cache control.

        Args:
            query: The query to execute.
            params: The query parameters.
            skip_cache: Whether to skip the cache for this request.

        Returns:
            The query results.
        """
        response = self.api_client._request(
            method="POST",
            path="/api/database/query",
            data={"query": query, "params": params or {}},
            skip_cache=skip_cache
        )
        return response.get("results", [])
