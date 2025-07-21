"""
Cloud Storage authentication for Science Data Kit connections.

This module provides a unified authentication management interface for cloud storage providers.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union, Tuple
from abc import ABC, abstractmethod

from .oauth2 import OAuth2Mixin
from .api_key import APIKeyMixin
from .credentials import CredentialsMixin

logger = logging.getLogger(__name__)

class CloudStorageAuthProvider(ABC):
    """Base class for cloud storage authentication providers."""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider."""
        pass
    
    @abstractmethod
    def authenticate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate with the cloud storage provider.
        
        Args:
            config: Configuration dictionary for authentication
            
        Returns:
            Dictionary containing authentication result
        """
        pass
    
    @abstractmethod
    def is_authenticated(self, config: Dict[str, Any]) -> bool:
        """
        Check if the connection is authenticated.
        
        Args:
            config: Configuration dictionary containing authentication information
            
        Returns:
            True if authenticated, False otherwise
        """
        pass
    
    @abstractmethod
    def get_auth_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get authentication headers.
        
        Args:
            config: Configuration dictionary containing authentication information
            
        Returns:
            Dictionary of authentication headers
        """
        pass
    
    @abstractmethod
    def get_connection_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about the connection.
        
        Args:
            config: Configuration dictionary containing authentication information
            
        Returns:
            Dictionary containing connection information
        """
        pass


class DropboxAuthProvider(CloudStorageAuthProvider, OAuth2Mixin):
    """Authentication provider for Dropbox."""
    
    @property
    def provider_name(self) -> str:
        """Return the name of the provider."""
        return "dropbox"
    
    def get_auth_url(self) -> str:
        """
        Get the authorization URL for OAuth2 authentication.
        
        Returns:
            Authorization URL as a string
        """
        from science_data_kit_extensions.dropbox.connector import DropboxConnector
        
        # Get app key and app secret from environment variables
        app_key = os.environ.get("DROPBOX_APP_KEY")
        app_secret = os.environ.get("DROPBOX_APP_SECRET")
        
        if not app_key or not app_secret:
            raise ValueError(
                "Dropbox API credentials not provided. "
                "Please set DROPBOX_APP_KEY and DROPBOX_APP_SECRET environment variables."
            )
        
        # Create a temporary connector to get the auth URL
        connector = DropboxConnector(app_key=app_key, app_secret=app_secret)
        return connector.authenticate()
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange an authorization code for an access token.
        
        Args:
            code: Authorization code from the OAuth2 flow
            
        Returns:
            Dictionary containing token information
        """
        from science_data_kit_extensions.dropbox.connector import DropboxConnector
        
        # Get app key and app secret from environment variables
        app_key = os.environ.get("DROPBOX_APP_KEY")
        app_secret = os.environ.get("DROPBOX_APP_SECRET")
        
        if not app_key or not app_secret:
            raise ValueError(
                "Dropbox API credentials not provided. "
                "Please set DROPBOX_APP_KEY and DROPBOX_APP_SECRET environment variables."
            )
        
        # Create a temporary connector to exchange the code for a token
        connector = DropboxConnector(app_key=app_key, app_secret=app_secret)
        if connector.complete_authentication(code):
            return {
                "access_token": None,  # Dropbox connector doesn't expose the access token
                "refresh_token": connector.refresh_token,
                "expires_in": None,  # Dropbox connector doesn't expose the expiration time
                "token_type": "bearer"
            }
        else:
            raise ValueError("Failed to exchange code for token")
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Refresh token from a previous authentication
            
        Returns:
            Dictionary containing new token information
        """
        from science_data_kit_extensions.dropbox.connector import DropboxConnector
        
        # Get app key and app secret from environment variables
        app_key = os.environ.get("DROPBOX_APP_KEY")
        app_secret = os.environ.get("DROPBOX_APP_SECRET")
        
        if not app_key or not app_secret:
            raise ValueError(
                "Dropbox API credentials not provided. "
                "Please set DROPBOX_APP_KEY and DROPBOX_APP_SECRET environment variables."
            )
        
        # Create a connector with the refresh token
        connector = DropboxConnector(
            app_key=app_key,
            app_secret=app_secret,
            refresh_token=refresh_token
        )
        
        # Connect to test if the refresh token is valid
        if connector.connect():
            return {
                "access_token": None,  # Dropbox connector doesn't expose the access token
                "refresh_token": connector.refresh_token,
                "expires_in": None,  # Dropbox connector doesn't expose the expiration time
                "token_type": "bearer"
            }
        else:
            raise ValueError("Failed to refresh token")
    
    def authenticate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate with Dropbox.
        
        Args:
            config: Configuration dictionary for authentication
            
        Returns:
            Dictionary containing authentication result
        """
        from science_data_kit_extensions.dropbox.connector import DropboxConnector
        
        app_key = config.get("app_key") or os.environ.get("DROPBOX_APP_KEY")
        app_secret = config.get("app_secret") or os.environ.get("DROPBOX_APP_SECRET")
        refresh_token = config.get("refresh_token") or os.environ.get("DROPBOX_REFRESH_TOKEN")
        
        if not app_key or not app_secret:
            raise ValueError(
                "Dropbox API credentials not provided. "
                "Please provide app_key and app_secret in config or set "
                "DROPBOX_APP_KEY and DROPBOX_APP_SECRET environment variables."
            )
        
        # Create a connector with the provided credentials
        connector = DropboxConnector(
            app_key=app_key,
            app_secret=app_secret,
            refresh_token=refresh_token
        )
        
        # Connect to test if the credentials are valid
        if connector.connect():
            return {
                "authenticated": True,
                "refresh_token": connector.refresh_token,
                "account_info": connector.get_account_info()
            }
        else:
            return {
                "authenticated": False,
                "error": "Failed to authenticate with Dropbox"
            }
    
    def is_authenticated(self, config: Dict[str, Any]) -> bool:
        """
        Check if the connection is authenticated.
        
        Args:
            config: Configuration dictionary containing authentication information
            
        Returns:
            True if authenticated, False otherwise
        """
        try:
            # Try to get a valid token
            token_info = config.get("token_info", {})
            if "refresh_token" in token_info:
                self.refresh_token(token_info["refresh_token"])
                return True
            return False
        except Exception:
            return False
    
    def get_auth_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get authentication headers.
        
        Args:
            config: Configuration dictionary containing authentication information
            
        Returns:
            Dictionary of authentication headers
        """
        # Dropbox uses the access token directly in the API client, not in headers
        return {}
    
    def get_connection_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about the connection.
        
        Args:
            config: Configuration dictionary containing authentication information
            
        Returns:
            Dictionary containing connection information
        """
        from science_data_kit_extensions.dropbox.connector import DropboxConnector
        
        app_key = config.get("app_key") or os.environ.get("DROPBOX_APP_KEY")
        app_secret = config.get("app_secret") or os.environ.get("DROPBOX_APP_SECRET")
        refresh_token = config.get("refresh_token")
        
        if not refresh_token:
            token_info = config.get("token_info", {})
            refresh_token = token_info.get("refresh_token")
        
        if not app_key or not app_secret or not refresh_token:
            return {
                "connected": False,
                "error": "Missing credentials"
            }
        
        # Create a connector with the provided credentials
        connector = DropboxConnector(
            app_key=app_key,
            app_secret=app_secret,
            refresh_token=refresh_token
        )
        
        # Connect to test if the credentials are valid
        if connector.connect():
            return {
                "connected": True,
                "account_info": connector.get_account_info()
            }
        else:
            return {
                "connected": False,
                "error": "Failed to connect to Dropbox"
            }


class MSGraphAuthProvider(CloudStorageAuthProvider, OAuth2Mixin):
    """Authentication provider for Microsoft Graph."""
    
    @property
    def provider_name(self) -> str:
        """Return the name of the provider."""
        return "msgraph"
    
    def get_auth_url(self) -> str:
        """
        Get the authorization URL for OAuth2 authentication.
        
        Returns:
            Authorization URL as a string
        """
        from azure.identity import DeviceCodeCredential
        
        # Get client ID and tenant ID from environment variables
        client_id = os.environ.get("MSGRAPH_CLIENT_ID")
        tenant_id = os.environ.get("MSGRAPH_TENANT_ID")
        
        if not client_id or not tenant_id:
            raise ValueError(
                "Microsoft Graph API credentials not provided. "
                "Please set MSGRAPH_CLIENT_ID and MSGRAPH_TENANT_ID environment variables."
            )
        
        # Create a device code credential
        credential = DeviceCodeCredential(
            client_id=client_id,
            tenant_id=tenant_id,
            callback=lambda code: print(f"Please use the following code to authenticate: {code.user_code}")
        )
        
        # Start the device code flow
        # This will print the user code and return the verification URL
        return "https://microsoft.com/devicelogin"
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange an authorization code for an access token.
        
        Args:
            code: Authorization code from the OAuth2 flow
            
        Returns:
            Dictionary containing token information
        """
        # Device code flow doesn't use this method
        raise NotImplementedError("Device code flow doesn't use exchange_code_for_token")
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Refresh token from a previous authentication
            
        Returns:
            Dictionary containing new token information
        """
        # Azure Identity handles token refresh automatically
        return {
            "access_token": None,
            "refresh_token": refresh_token,
            "expires_in": None,
            "token_type": "bearer"
        }
    
    def authenticate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate with Microsoft Graph.
        
        Args:
            config: Configuration dictionary for authentication
            
        Returns:
            Dictionary containing authentication result
        """
        from azure.identity import ClientSecretCredential, DeviceCodeCredential, InteractiveBrowserCredential
        from msgraph.core import GraphClient
        
        client_id = config.get("client_id") or os.environ.get("MSGRAPH_CLIENT_ID")
        tenant_id = config.get("tenant_id") or os.environ.get("MSGRAPH_TENANT_ID")
        client_secret = config.get("client_secret") or os.environ.get("MSGRAPH_CLIENT_SECRET")
        auth_method = config.get("auth_method", "client_credentials")
        scopes = config.get("scopes", ["https://graph.microsoft.com/.default"])
        
        if not client_id or not tenant_id:
            raise ValueError(
                "Microsoft Graph API credentials not provided. "
                "Please provide client_id and tenant_id in config or set "
                "MSGRAPH_CLIENT_ID and MSGRAPH_TENANT_ID environment variables."
            )
        
        # Create the appropriate credential based on the auth method
        credential = None
        
        if auth_method == "client_credentials":
            if not client_secret:
                raise ValueError(
                    "Client secret not provided for client_credentials auth method. "
                    "Please provide client_secret in config or set MSGRAPH_CLIENT_SECRET environment variable."
                )
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
        elif auth_method == "device_code":
            credential = DeviceCodeCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                callback=lambda code: print(f"Please use the following code to authenticate: {code.user_code}")
            )
        elif auth_method == "interactive":
            credential = InteractiveBrowserCredential(
                tenant_id=tenant_id,
                client_id=client_id
            )
        else:
            raise ValueError(f"Unsupported auth_method: {auth_method}")
        
        # Create the Graph client
        client = GraphClient(credential=credential, scopes=scopes)
        
        # Test the connection
        try:
            response = client.get("/me")
            if response.status_code == 200:
                return {
                    "authenticated": True,
                    "user_info": response.json()
                }
            else:
                return {
                    "authenticated": False,
                    "error": f"Failed to authenticate with Microsoft Graph: {response.status_code} {response.text}"
                }
        except Exception as e:
            return {
                "authenticated": False,
                "error": f"Failed to authenticate with Microsoft Graph: {str(e)}"
            }
    
    def is_authenticated(self, config: Dict[str, Any]) -> bool:
        """
        Check if the connection is authenticated.
        
        Args:
            config: Configuration dictionary containing authentication information
            
        Returns:
            True if authenticated, False otherwise
        """
        try:
            # Try to authenticate
            result = self.authenticate(config)
            return result.get("authenticated", False)
        except Exception:
            return False
    
    def get_auth_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get authentication headers.
        
        Args:
            config: Configuration dictionary containing authentication information
            
        Returns:
            Dictionary of authentication headers
        """
        # Microsoft Graph uses the credential directly in the API client, not in headers
        return {}
    
    def get_connection_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about the connection.
        
        Args:
            config: Configuration dictionary containing authentication information
            
        Returns:
            Dictionary containing connection information
        """
        try:
            # Try to authenticate
            result = self.authenticate(config)
            if result.get("authenticated", False):
                return {
                    "connected": True,
                    "user_info": result.get("user_info", {})
                }
            else:
                return {
                    "connected": False,
                    "error": result.get("error", "Unknown error")
                }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }


class CloudStorageAuthManager:
    """
    Unified authentication management interface for cloud storage providers.
    
    This class provides a unified interface for authenticating with different cloud storage providers.
    """
    
    def __init__(self):
        """Initialize the cloud storage authentication manager."""
        self._providers = {}
        self._register_default_providers()
    
    def _register_default_providers(self):
        """Register the default authentication providers."""
        self.register_provider(DropboxAuthProvider())
        self.register_provider(MSGraphAuthProvider())
    
    def register_provider(self, provider: CloudStorageAuthProvider):
        """
        Register an authentication provider.
        
        Args:
            provider: Authentication provider to register
        """
        self._providers[provider.provider_name] = provider
    
    def get_provider(self, provider_name: str) -> CloudStorageAuthProvider:
        """
        Get an authentication provider by name.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Authentication provider
        """
        if provider_name not in self._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return self._providers[provider_name]
    
    def list_providers(self) -> List[str]:
        """
        List all registered authentication providers.
        
        Returns:
            List of provider names
        """
        return list(self._providers.keys())
    
    def authenticate(self, provider_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate with a cloud storage provider.
        
        Args:
            provider_name: Name of the provider
            config: Configuration dictionary for authentication
            
        Returns:
            Dictionary containing authentication result
        """
        provider = self.get_provider(provider_name)
        return provider.authenticate(config)
    
    def is_authenticated(self, provider_name: str, config: Dict[str, Any]) -> bool:
        """
        Check if a connection is authenticated.
        
        Args:
            provider_name: Name of the provider
            config: Configuration dictionary containing authentication information
            
        Returns:
            True if authenticated, False otherwise
        """
        provider = self.get_provider(provider_name)
        return provider.is_authenticated(config)
    
    def get_auth_headers(self, provider_name: str, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get authentication headers for a provider.
        
        Args:
            provider_name: Name of the provider
            config: Configuration dictionary containing authentication information
            
        Returns:
            Dictionary of authentication headers
        """
        provider = self.get_provider(provider_name)
        return provider.get_auth_headers(config)
    
    def get_connection_info(self, provider_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about a connection.
        
        Args:
            provider_name: Name of the provider
            config: Configuration dictionary containing authentication information
            
        Returns:
            Dictionary containing connection information
        """
        provider = self.get_provider(provider_name)
        return provider.get_connection_info(config)
    
    def get_auth_url(self, provider_name: str) -> str:
        """
        Get the authorization URL for OAuth2 authentication.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Authorization URL as a string
        """
        provider = self.get_provider(provider_name)
        if isinstance(provider, OAuth2Mixin):
            return provider.get_auth_url()
        else:
            raise ValueError(f"Provider {provider_name} does not support OAuth2 authentication")
    
    def exchange_code_for_token(self, provider_name: str, code: str) -> Dict[str, Any]:
        """
        Exchange an authorization code for an access token.
        
        Args:
            provider_name: Name of the provider
            code: Authorization code from the OAuth2 flow
            
        Returns:
            Dictionary containing token information
        """
        provider = self.get_provider(provider_name)
        if isinstance(provider, OAuth2Mixin):
            return provider.exchange_code_for_token(code)
        else:
            raise ValueError(f"Provider {provider_name} does not support OAuth2 authentication")
    
    def refresh_token(self, provider_name: str, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            provider_name: Name of the provider
            refresh_token: Refresh token from a previous authentication
            
        Returns:
            Dictionary containing new token information
        """
        provider = self.get_provider(provider_name)
        if isinstance(provider, OAuth2Mixin):
            return provider.refresh_token(refresh_token)
        else:
            raise ValueError(f"Provider {provider_name} does not support OAuth2 authentication")


# Create a singleton instance
auth_manager = CloudStorageAuthManager()