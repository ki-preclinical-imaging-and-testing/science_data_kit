"""
Microsoft 365 Plugin for Science Data Kit.

This module provides a plugin for accessing Microsoft 365 services through the Microsoft Graph API.
It implements the APIPluginInterface and provides methods for authentication and API requests.
"""

import os
import logging
from typing import Any, Dict, List, Optional, Set

from azure.identity import ClientSecretCredential, DeviceCodeCredential, InteractiveBrowserCredential
from msgraph.core import GraphClient

from science_data_kit.core.plugins.config import (
    ConfigField,
    ConfigFieldType,
    PluginConfigSchema,
    create_default_config,
)
from science_data_kit.core.plugins.interfaces import APIPluginInterface
from science_data_kit.core.integrations.plugin_architecture import register_plugin

logger = logging.getLogger(__name__)


@register_plugin
class Microsoft365Plugin(APIPluginInterface):
    """
    Plugin for accessing Microsoft 365 services through the Microsoft Graph API.
    
    This plugin provides access to Microsoft 365 services including Microsoft Teams, SharePoint,
    OneDrive, Outlook, and user/group information.
    """
    
    def __init__(self):
        """Initialize the plugin."""
        self._name = "microsoft365"
        self._version = "1.0.0"
        self._description = "Plugin for accessing Microsoft 365 services through the Microsoft Graph API"
        self._is_initialized = False
        self._is_connected = False
        self._config = {}
        self._client = None
        self._auth_method = None
        
    @property
    def name(self) -> str:
        """Get the plugin name."""
        return self._name
        
    @property
    def version(self) -> str:
        """Get the plugin version."""
        return self._version
        
    @property
    def description(self) -> str:
        """Get the plugin description."""
        return self._description
        
    @property
    def config_schema(self) -> PluginConfigSchema:
        """Get the plugin configuration schema."""
        return PluginConfigSchema(
            fields=[
                ConfigField(
                    name="client_id",
                    field_type=ConfigFieldType.STRING,
                    description="Microsoft Graph API client ID",
                    required=True,
                ),
                ConfigField(
                    name="tenant_id",
                    field_type=ConfigFieldType.STRING,
                    description="Microsoft Graph API tenant ID",
                    required=True,
                ),
                ConfigField(
                    name="client_secret",
                    field_type=ConfigFieldType.STRING,
                    description="Microsoft Graph API client secret",
                    required=False,
                ),
                ConfigField(
                    name="auth_method",
                    field_type=ConfigFieldType.STRING,
                    description="Authentication method (client_credentials, device_code, interactive)",
                    required=False,
                    default="client_credentials",
                ),
                ConfigField(
                    name="scopes",
                    field_type=ConfigFieldType.LIST,
                    description="List of permission scopes",
                    required=False,
                    default=["https://graph.microsoft.com/.default"],
                ),
            ],
            version="1.0",
        )
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate a configuration against this plugin's schema.
        
        Args:
            config: The configuration to validate
            
        Returns:
            True if the configuration is valid, False otherwise
        """
        # Basic schema validation
        if not self.config_schema.validate_config(config):
            return False
            
        # Additional validation for auth_method
        auth_method = config.get("auth_method", "client_credentials")
        if auth_method not in ["client_credentials", "device_code", "interactive"]:
            logger.error(f"Invalid auth_method: {auth_method}")
            return False
            
        # If auth_method is client_credentials, client_secret is required
        if auth_method == "client_credentials" and not config.get("client_secret"):
            logger.error("client_secret is required for client_credentials auth_method")
            return False
            
        return True
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with the given configuration.
        
        Args:
            config: The configuration to use
            
        Returns:
            True if initialization was successful, False otherwise
        """
        if not self.validate_config(config):
            logger.error("Invalid configuration for Microsoft 365 plugin")
            return False
            
        self._config = config
        self._auth_method = config.get("auth_method", "client_credentials")
        
        try:
            # Initialize authentication based on the selected method
            if self._auth_method == "client_credentials":
                if not config.get("client_secret"):
                    logger.error("client_secret is required for client_credentials auth_method")
                    return False
                    
            self._is_initialized = True
            logger.info("Microsoft 365 plugin initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Microsoft 365 plugin: {e}")
            self._is_initialized = False
            return False
        
    def shutdown(self) -> bool:
        """
        Shut down the plugin and release any resources.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        if self._is_connected:
            self.disconnect()
            
        self._client = None
        self._is_initialized = False
        logger.info("Microsoft 365 plugin shut down")
        return True
        
    @property
    def is_initialized(self) -> bool:
        """Check if the plugin is initialized."""
        return self._is_initialized
        
    @property
    def capabilities(self) -> Set[str]:
        """Get the plugin capabilities."""
        capabilities = {"api", "teams", "sharepoint", "onedrive", "outlook", "users", "groups"}
        return capabilities
        
    def connect(self, config: Dict[str, Any]) -> None:
        """
        Establish connection with Microsoft Graph API.
        
        Args:
            config: Configuration dictionary for the connection
        """
        if not self._is_initialized:
            if not self.initialize(config):
                raise RuntimeError("Failed to initialize Microsoft 365 plugin")
                
        try:
            # Create the appropriate credential based on the auth method
            credential = None
            scopes = config.get("scopes", ["https://graph.microsoft.com/.default"])
            
            if self._auth_method == "client_credentials":
                credential = ClientSecretCredential(
                    tenant_id=config["tenant_id"],
                    client_id=config["client_id"],
                    client_secret=config["client_secret"]
                )
            elif self._auth_method == "device_code":
                credential = DeviceCodeCredential(
                    tenant_id=config["tenant_id"],
                    client_id=config["client_id"]
                )
            elif self._auth_method == "interactive":
                credential = InteractiveBrowserCredential(
                    tenant_id=config["tenant_id"],
                    client_id=config["client_id"]
                )
            else:
                raise ValueError(f"Unsupported auth_method: {self._auth_method}")
                
            # Create the Graph client
            self._client = GraphClient(credential=credential, scopes=scopes)
            
            # Test the connection
            self.request("GET", "/me")
            
            self._is_connected = True
            logger.info("Connected to Microsoft Graph API")
        except Exception as e:
            logger.error(f"Error connecting to Microsoft Graph API: {e}")
            self._is_connected = False
            raise RuntimeError(f"Failed to connect to Microsoft Graph API: {e}")
        
    def disconnect(self) -> None:
        """Clean up connection."""
        self._client = None
        self._is_connected = False
        logger.info("Disconnected from Microsoft Graph API")
        
    def test_connection(self) -> bool:
        """
        Verify connection is working.
        
        Returns:
            True if connection is working, False otherwise
        """
        if not self._is_connected or not self._client:
            return False
            
        try:
            # Make a simple request to test the connection
            self.request("GET", "/me")
            return True
        except Exception:
            return False
        
    @property
    def is_connected(self) -> bool:
        """
        Check if the connection is currently established.
        
        Returns:
            True if connected, False otherwise
        """
        return self._is_connected and self._client is not None
        
    def request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        """
        Make an API request to the Microsoft Graph API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body
            headers: Request headers
            
        Returns:
            API response
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Microsoft Graph API")
            
        try:
            # Ensure endpoint starts with /
            if not endpoint.startswith("/"):
                endpoint = f"/{endpoint}"
                
            # Make the request
            response = self._client.request(
                method=method,
                url=endpoint,
                params=params,
                json=data,
                headers=headers
            )
            
            # Check for errors
            if response.status_code >= 400:
                error_info = response.json() if response.content else {"error": "Unknown error"}
                raise RuntimeError(f"API request failed: {response.status_code} - {error_info}")
                
            # Return the response data
            return response.json() if response.content else None
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            raise
        
    def get_endpoints(self) -> List[str]:
        """
        Get a list of available endpoints.
        
        Returns:
            List of endpoint names
        """
        # Microsoft Graph API has many endpoints, so we'll return a list of common ones
        return [
            "/me",
            "/users",
            "/groups",
            "/teams",
            "/sites",
            "/drives",
            "/me/drive",
            "/me/messages",
            "/me/events",
            "/me/contacts"
        ]
        
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get the current rate limit status.
        
        Returns:
            Rate limit information
        """
        # Microsoft Graph API doesn't provide a standard way to check rate limits
        # We'll return a placeholder for now
        return {
            "requests_remaining": "unknown",
            "requests_limit": "unknown",
            "reset_time": "unknown"
        }
        
    # Helper methods for common Microsoft Graph API operations
    
    def get_me(self) -> Dict[str, Any]:
        """
        Get information about the current user.
        
        Returns:
            User information
        """
        return self.request("GET", "/me")
        
    def get_users(self) -> List[Dict[str, Any]]:
        """
        Get a list of users.
        
        Returns:
            List of users
        """
        response = self.request("GET", "/users")
        return response.get("value", [])
        
    def get_groups(self) -> List[Dict[str, Any]]:
        """
        Get a list of groups.
        
        Returns:
            List of groups
        """
        response = self.request("GET", "/groups")
        return response.get("value", [])
        
    def get_teams(self) -> List[Dict[str, Any]]:
        """
        Get a list of teams.
        
        Returns:
            List of teams
        """
        response = self.request("GET", "/teams")
        return response.get("value", [])
        
    def get_channels(self, team_id: str) -> List[Dict[str, Any]]:
        """
        Get a list of channels in a team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of channels
        """
        response = self.request("GET", f"/teams/{team_id}/channels")
        return response.get("value", [])
        
    def get_messages(self, team_id: str, channel_id: str) -> List[Dict[str, Any]]:
        """
        Get a list of messages in a channel.
        
        Args:
            team_id: Team ID
            channel_id: Channel ID
            
        Returns:
            List of messages
        """
        response = self.request("GET", f"/teams/{team_id}/channels/{channel_id}/messages")
        return response.get("value", [])
        
    def get_sharepoint_sites(self) -> List[Dict[str, Any]]:
        """
        Get a list of SharePoint sites.
        
        Returns:
            List of sites
        """
        response = self.request("GET", "/sites")
        return response.get("value", [])
        
    def get_onedrive_files(self, drive_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a list of files in OneDrive.
        
        Args:
            drive_id: Drive ID (optional, defaults to current user's drive)
            
        Returns:
            List of files
        """
        endpoint = f"/drives/{drive_id}/root/children" if drive_id else "/me/drive/root/children"
        response = self.request("GET", endpoint)
        return response.get("value", [])