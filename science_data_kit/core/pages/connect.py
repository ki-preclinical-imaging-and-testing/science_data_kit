"""
Connect Page Module for Science Data Kit Core

This module provides the framework-independent implementation of the connect page.
It defines the core functionality for managing connections to various data sources.
"""

from typing import List, Dict, Any, Optional, Tuple
import os
import uuid
import json
import time
import secrets
from urllib.parse import urlencode

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import ConnectPageData

class ConnectPage(BasePage):
    """
    Core implementation of the connect page.

    This class provides the framework-independent functionality for managing
    connections to various data sources. It returns a ConnectPageData object
    that can be rendered by any UI framework.
    """

    def __init__(self, db_connection=None):
        """
        Initialize the connect page.

        Args:
            db_connection: Optional database connection to use for data retrieval.
        """
        super().__init__(db_connection)
        self.active_connections = {}
        self.connection_status = {}
        self.connection_errors = {}
        self.oauth_auth_urls = {}
        self.oauth_states = {}
        self.oauth_tokens = {}

    def get_page_data(self) -> ConnectPageData:
        """
        Return data needed to render the connect page.

        Returns:
            A ConnectPageData object containing the data needed to render the page.
        """
        return ConnectPageData(
            title="Connect to Data Sources",
            available_connections=self._get_available_connections(),
            active_connections=self._get_active_connections(),
            connection_status=self.connection_status,
            connection_errors=self.connection_errors,
            oauth_auth_urls=self.oauth_auth_urls,
            oauth_states=self.oauth_states
        )

    def _get_available_connections(self) -> List[Dict[str, Any]]:
        """
        Get the list of available connection types.

        Returns:
            A list of dictionaries containing connection type information.
        """
        return [
            {
                "id": "database",
                "name": "Database",
                "description": "Connect to SQL databases like PostgreSQL, MySQL, SQLite",
                "icon": "database",
                "enabled": True,
                "auth_type": "basic",
                "config_fields": [
                    {"name": "uri", "type": "string", "label": "URI", "required": True},
                    {"name": "username", "type": "string", "label": "Username", "required": True},
                    {"name": "password", "type": "password", "label": "Password", "required": True},
                    {"name": "database", "type": "string", "label": "Database", "required": True}
                ]
            },
            {
                "id": "neo4j",
                "name": "Neo4j",
                "description": "Connect to Neo4j graph databases",
                "icon": "graph",
                "enabled": True,
                "auth_type": "basic",
                "config_fields": [
                    {"name": "uri", "type": "string", "label": "URI", "required": True},
                    {"name": "username", "type": "string", "label": "Username", "required": True},
                    {"name": "password", "type": "password", "label": "Password", "required": True}
                ]
            },
            {
                "id": "msgraph",
                "name": "Microsoft Graph API",
                "description": "Connect to Microsoft 365 services",
                "icon": "cloud",
                "enabled": True,
                "auth_type": "oauth",
                "oauth_config": {
                    "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                    "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                    "scope": "Files.Read Files.ReadWrite Files.Read.All Files.ReadWrite.All",
                    "redirect_uri": "/api/connect/oauth/callback"
                },
                "config_fields": [
                    {"name": "client_id", "type": "string", "label": "Client ID", "required": True},
                    {"name": "tenant_id", "type": "string", "label": "Tenant ID", "required": True},
                    {"name": "client_secret", "type": "password", "label": "Client Secret", "required": True}
                ]
            },
            {
                "id": "google_drive",
                "name": "Google Drive",
                "description": "Connect to Google Drive for file access",
                "icon": "cloud",
                "enabled": True,
                "auth_type": "oauth",
                "oauth_config": {
                    "auth_url": "https://accounts.google.com/o/oauth2/auth",
                    "token_url": "https://oauth2.googleapis.com/token",
                    "scope": "https://www.googleapis.com/auth/drive.readonly",
                    "redirect_uri": "/api/connect/oauth/callback"
                },
                "config_fields": [
                    {"name": "client_id", "type": "string", "label": "Client ID", "required": True},
                    {"name": "client_secret", "type": "password", "label": "Client Secret", "required": True}
                ]
            },
            {
                "id": "github",
                "name": "GitHub",
                "description": "Connect to GitHub repositories",
                "icon": "code",
                "enabled": True,
                "auth_type": "oauth",
                "oauth_config": {
                    "auth_url": "https://github.com/login/oauth/authorize",
                    "token_url": "https://github.com/login/oauth/access_token",
                    "scope": "repo",
                    "redirect_uri": "/api/connect/oauth/callback"
                },
                "config_fields": [
                    {"name": "client_id", "type": "string", "label": "Client ID", "required": True},
                    {"name": "client_secret", "type": "password", "label": "Client Secret", "required": True}
                ]
            },
            {
                "id": "dropbox",
                "name": "Dropbox",
                "description": "Connect to Dropbox for file access",
                "icon": "file",
                "enabled": True,
                "auth_type": "oauth",
                "oauth_config": {
                    "auth_url": "https://www.dropbox.com/oauth2/authorize",
                    "token_url": "https://api.dropboxapi.com/oauth2/token",
                    "scope": "",
                    "redirect_uri": "/api/connect/oauth/callback"
                },
                "config_fields": [
                    {"name": "client_id", "type": "string", "label": "App Key", "required": True},
                    {"name": "client_secret", "type": "password", "label": "App Secret", "required": True}
                ]
            },
            {
                "id": "local_fs",
                "name": "Local Filesystem",
                "description": "Access files on the local filesystem",
                "icon": "folder",
                "enabled": True,
                "auth_type": "none",
                "config_fields": [
                    {"name": "path", "type": "string", "label": "Path", "required": True}
                ]
            }
        ]

    def _get_active_connections(self) -> List[Dict[str, Any]]:
        """
        Get the list of active connections.

        Returns:
            A list of dictionaries containing active connection information.
        """
        active_connections = []
        for conn_id, conn_info in self.active_connections.items():
            active_connections.append({
                "id": conn_id,
                "name": conn_info.get("name", "Unnamed Connection"),
                "type": conn_info.get("type", "Unknown"),
                "status": self.connection_status.get(conn_id, False),
                "config": {
                    k: v for k, v in conn_info.get("config", {}).items()
                    if k != "password" and k != "client_secret" and k != "api_secret"
                }
            })
        return active_connections

    def connect(self, connection_type: str, config: Dict[str, Any], name: str = None) -> bool:
        """
        Connect to a data source.

        Args:
            connection_type: The type of connection to establish.
            config: The configuration parameters for the connection.
            name: Optional name for the connection.

        Returns:
            True if the connection was successful, False otherwise.
        """
        conn_id = f"{connection_type}_{len(self.active_connections)}"
        conn_name = name or f"{connection_type.capitalize()} Connection {len(self.active_connections) + 1}"

        # Store connection info
        self.active_connections[conn_id] = {
            "type": connection_type,
            "name": conn_name,
            "config": config
        }

        # Attempt to connect
        try:
            # This would be replaced with actual connection logic
            if connection_type == "database":
                # Simulate database connection
                self.connection_status[conn_id] = True
            elif connection_type == "neo4j":
                # Simulate Neo4j connection
                self.connection_status[conn_id] = True
            elif connection_type == "msgraph":
                # Simulate Microsoft Graph API connection
                self.connection_status[conn_id] = True
            elif connection_type == "dropbox":
                # Simulate Dropbox connection
                self.connection_status[conn_id] = True
            elif connection_type == "local_fs":
                # Check if path exists
                path = config.get("path", "")
                if os.path.exists(path):
                    self.connection_status[conn_id] = True
                else:
                    self.connection_status[conn_id] = False
                    self.connection_errors[conn_id] = f"Path does not exist: {path}"
            else:
                self.connection_status[conn_id] = False
                self.connection_errors[conn_id] = f"Unknown connection type: {connection_type}"
                return False

            return self.connection_status[conn_id]

        except Exception as e:
            self.connection_status[conn_id] = False
            self.connection_errors[conn_id] = str(e)
            return False

    def disconnect(self, connection_id: str) -> bool:
        """
        Disconnect from a data source.

        Args:
            connection_id: The ID of the connection to disconnect.

        Returns:
            True if the disconnection was successful, False otherwise.
        """
        if connection_id in self.active_connections:
            # This would be replaced with actual disconnection logic
            try:
                # Remove connection info
                self.active_connections.pop(connection_id)
                self.connection_status.pop(connection_id, None)
                self.connection_errors.pop(connection_id, None)
                return True
            except Exception as e:
                self.connection_errors[connection_id] = str(e)
                return False
        else:
            return False

    def test_connection(self, connection_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a connection without saving it.

        Args:
            connection_type: The type of connection to test.
            config: The configuration parameters for the connection.

        Returns:
            A dictionary with the test results.
        """
        # This would be replaced with actual connection testing logic
        try:
            if connection_type == "database":
                # Simulate database connection test
                return {"success": True, "message": "Database connection successful"}
            elif connection_type == "neo4j":
                # Simulate Neo4j connection test
                return {"success": True, "message": "Neo4j connection successful"}
            elif connection_type == "msgraph":
                # Simulate Microsoft Graph API connection test
                return {"success": True, "message": "Microsoft Graph API connection successful"}
            elif connection_type == "google_drive":
                # Simulate Google Drive connection test
                return {"success": True, "message": "Google Drive connection successful"}
            elif connection_type == "github":
                # Simulate GitHub connection test
                return {"success": True, "message": "GitHub connection successful"}
            elif connection_type == "dropbox":
                # Simulate Dropbox connection test
                return {"success": True, "message": "Dropbox connection successful"}
            elif connection_type == "local_fs":
                # Check if path exists
                path = config.get("path", "")
                if os.path.exists(path):
                    return {"success": True, "message": f"Path exists: {path}"}
                else:
                    return {"success": False, "message": f"Path does not exist: {path}"}
            else:
                return {"success": False, "message": f"Unknown connection type: {connection_type}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def initiate_oauth(self, connection_type: str, config: Dict[str, Any], base_url: str) -> Tuple[bool, str, Optional[str]]:
        """
        Initiate OAuth authorization flow.

        Args:
            connection_type: The type of connection to establish.
            config: The configuration parameters for the connection.
            base_url: The base URL of the application for constructing the redirect URI.

        Returns:
            A tuple containing:
            - Boolean indicating success
            - Message describing the result
            - Authorization URL (if successful)
        """
        # Find the connection type in available connections
        connection_info = None
        for conn in self._get_available_connections():
            if conn["id"] == connection_type:
                connection_info = conn
                break

        if not connection_info:
            return False, f"Unknown connection type: {connection_type}", None

        if connection_info.get("auth_type") != "oauth":
            return False, f"Connection type {connection_type} does not support OAuth", None

        oauth_config = connection_info.get("oauth_config", {})
        if not oauth_config:
            return False, f"OAuth configuration missing for {connection_type}", None

        # Generate a unique state parameter to prevent CSRF
        state = secrets.token_urlsafe(32)
        conn_id = f"{connection_type}_{len(self.active_connections)}"

        # Store the state for later verification
        self.oauth_states[conn_id] = state

        # Store connection info
        self.active_connections[conn_id] = {
            "type": connection_type,
            "name": f"{connection_info['name']} Connection",
            "config": config,
            "status": "authorizing"
        }

        # Construct the authorization URL
        auth_url = oauth_config["auth_url"]
        redirect_uri = f"{base_url}{oauth_config['redirect_uri']}"

        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state
        }

        if oauth_config.get("scope"):
            params["scope"] = oauth_config["scope"]

        # Add any additional parameters based on connection type
        if connection_type == "msgraph":
            params["tenant"] = config.get("tenant_id", "common")

        auth_url = f"{auth_url}?{urlencode(params)}"

        # Store the authorization URL
        self.oauth_auth_urls[conn_id] = auth_url

        return True, "Authorization URL generated", auth_url

    def handle_oauth_callback(self, code: str, state: str, base_url: str) -> Tuple[bool, str, Optional[str]]:
        """
        Handle OAuth callback and exchange authorization code for tokens.

        Args:
            code: The authorization code returned by the OAuth provider.
            state: The state parameter returned by the OAuth provider.
            base_url: The base URL of the application for constructing the redirect URI.

        Returns:
            A tuple containing:
            - Boolean indicating success
            - Message describing the result
            - Connection ID (if successful)
        """
        # Find the connection with matching state
        conn_id = None
        for cid, stored_state in self.oauth_states.items():
            if stored_state == state:
                conn_id = cid
                break

        if not conn_id:
            return False, "Invalid state parameter", None

        # Get connection info
        conn_info = self.active_connections.get(conn_id)
        if not conn_info:
            return False, "Connection not found", None

        # Find the connection type in available connections
        connection_type = conn_info["type"]
        connection_config = None
        for conn in self._get_available_connections():
            if conn["id"] == connection_type:
                connection_config = conn
                break

        if not connection_config:
            return False, f"Unknown connection type: {connection_type}", None

        oauth_config = connection_config.get("oauth_config", {})
        if not oauth_config:
            return False, f"OAuth configuration missing for {connection_type}", None

        # Exchange code for tokens (in a real implementation, this would make an HTTP request)
        # For this example, we'll simulate a successful token exchange
        tokens = {
            "access_token": f"simulated_access_token_{uuid.uuid4()}",
            "refresh_token": f"simulated_refresh_token_{uuid.uuid4()}",
            "expires_at": int(time.time()) + 3600  # Token expires in 1 hour
        }

        # Store the tokens
        self.oauth_tokens[conn_id] = tokens

        # Update connection status
        self.connection_status[conn_id] = True

        # Clean up
        self.oauth_states.pop(conn_id, None)
        self.oauth_auth_urls.pop(conn_id, None)

        return True, "OAuth authorization successful", conn_id

    def refresh_oauth_token(self, connection_id: str) -> bool:
        """
        Refresh an expired OAuth token.

        Args:
            connection_id: The ID of the connection to refresh.

        Returns:
            True if the token was refreshed successfully, False otherwise.
        """
        # Get connection info
        conn_info = self.active_connections.get(connection_id)
        if not conn_info:
            self.connection_errors[connection_id] = "Connection not found"
            return False

        # Get tokens
        tokens = self.oauth_tokens.get(connection_id)
        if not tokens:
            self.connection_errors[connection_id] = "No tokens found for connection"
            return False

        # Check if token is expired
        if tokens.get("expires_at", 0) > time.time():
            # Token is still valid
            return True

        # In a real implementation, this would make an HTTP request to refresh the token
        # For this example, we'll simulate a successful token refresh
        new_tokens = {
            "access_token": f"simulated_access_token_{uuid.uuid4()}",
            "refresh_token": tokens.get("refresh_token"),  # Keep the same refresh token
            "expires_at": int(time.time()) + 3600  # Token expires in 1 hour
        }

        # Store the new tokens
        self.oauth_tokens[connection_id] = new_tokens

        return True
