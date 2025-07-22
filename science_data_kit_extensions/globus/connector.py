"""
Globus connector for Science Data Kit.

This module provides a connector for Globus, handling authentication and
connection management for Globus endpoints.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

# Globus SDK imports
# Note: These would need to be installed via pip install globus-sdk
try:
    import globus_sdk
    from globus_sdk import (
        NativeAppAuthClient, 
        TransferClient,
        RefreshTokenAuthorizer,
        AuthClient,
        SearchClient,
        GroupsClient
    )
    from globus_sdk.exc import AuthAPIError, TransferAPIError
    GLOBUS_SDK_AVAILABLE = True
except ImportError:
    GLOBUS_SDK_AVAILABLE = False
    logging.warning("Globus SDK not available. Install with 'pip install globus-sdk'")


class GlobusConnector:
    """
    Connector for Globus services.
    
    This class handles authentication and connection to Globus services,
    including Transfer, Search, and Groups APIs.
    """
    
    def __init__(
        self, 
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        config_file: Optional[str] = None
    ):
        """
        Initialize the Globus connector.
        
        Args:
            client_id: Globus client ID
            client_secret: Globus client secret
            refresh_token: Refresh token for authentication
            config_file: Path to a JSON configuration file
        """
        self.logger = logging.getLogger(__name__)
        
        if not GLOBUS_SDK_AVAILABLE:
            self.logger.error("Globus SDK not available. Install with 'pip install globus-sdk'")
            raise ImportError("Globus SDK not available")
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        
        self.auth_client = None
        self.transfer_client = None
        self.search_client = None
        self.groups_client = None
        
        # Load config from file if provided
        if config_file:
            self._load_config(config_file)
    
    def _load_config(self, config_file: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_file: Path to a JSON configuration file
        """
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                self.logger.error(f"Config file not found: {config_file}")
                return
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            self.client_id = config.get('client_id', self.client_id)
            self.client_secret = config.get('client_secret', self.client_secret)
            self.refresh_token = config.get('refresh_token', self.refresh_token)
            
            self.logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
    
    def connect(self) -> bool:
        """
        Connect to Globus services using the provided credentials.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        if not self.client_id:
            self.logger.error("Client ID is required for connection")
            return False
        
        try:
            # Initialize the Native App authentication client
            self.auth_client = NativeAppAuthClient(self.client_id)
            
            # If we have a refresh token, use it to create an authorizer
            if self.refresh_token:
                authorizer = RefreshTokenAuthorizer(
                    self.refresh_token,
                    self.auth_client
                )
                
                # Initialize clients with the authorizer
                self.transfer_client = TransferClient(authorizer=authorizer)
                self.search_client = SearchClient(authorizer=authorizer)
                self.groups_client = GroupsClient(authorizer=authorizer)
                
                # Test the connection
                self.transfer_client.get_endpoint_list(limit=1)
                self.logger.info("Successfully connected to Globus services")
                return True
            else:
                self.logger.warning("No refresh token available, authentication required")
                return False
        except Exception as e:
            self.logger.error(f"Error connecting to Globus: {str(e)}")
            return False
    
    def authenticate(self) -> Dict[str, Any]:
        """
        Start the authentication flow for Globus.
        
        Returns:
            Dict containing auth URL and other info needed for authentication
        """
        if not self.client_id:
            self.logger.error("Client ID is required for authentication")
            return {"error": "Client ID is required"}
        
        try:
            self.auth_client = NativeAppAuthClient(self.client_id)
            self.auth_client.oauth2_start_flow(
                requested_scopes=[
                    "openid",
                    "profile",
                    "email",
                    "urn:globus:auth:scope:transfer.api.globus.org:all",
                    "urn:globus:auth:scope:search.api.globus.org:all",
                    "urn:globus:auth:scope:groups.api.globus.org:all"
                ],
                refresh_tokens=True
            )
            
            authorize_url = self.auth_client.oauth2_get_authorize_url()
            return {
                "auth_url": authorize_url,
                "message": "Please visit this URL to authenticate with Globus"
            }
        except Exception as e:
            self.logger.error(f"Error starting authentication flow: {str(e)}")
            return {"error": str(e)}
    
    def complete_authentication(self, auth_code: str) -> Dict[str, Any]:
        """
        Complete the authentication flow with the provided code.
        
        Args:
            auth_code: The authorization code from Globus
            
        Returns:
            Dict with tokens and connection status
        """
        if not self.auth_client:
            self.logger.error("Authentication client not initialized")
            return {"error": "Authentication client not initialized"}
        
        try:
            # Exchange code for tokens
            token_response = self.auth_client.oauth2_exchange_code_for_tokens(auth_code)
            
            # Extract tokens for each service
            transfer_data = token_response.by_resource_server['transfer.api.globus.org']
            self.refresh_token = transfer_data['refresh_token']
            
            # Create authorizer with the tokens
            authorizer = RefreshTokenAuthorizer(
                self.refresh_token,
                self.auth_client
            )
            
            # Initialize clients with the authorizer
            self.transfer_client = TransferClient(authorizer=authorizer)
            self.search_client = SearchClient(authorizer=authorizer)
            self.groups_client = GroupsClient(authorizer=authorizer)
            
            self.logger.info("Authentication completed successfully")
            return {
                "status": "success",
                "refresh_token": self.refresh_token,
                "message": "Authentication completed successfully"
            }
        except Exception as e:
            self.logger.error(f"Error completing authentication: {str(e)}")
            return {"error": str(e)}
    
    def is_connected(self) -> bool:
        """
        Check if the connector is connected to Globus services.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.transfer_client:
            return False
        
        try:
            # Test the connection by making a simple API call
            self.transfer_client.get_endpoint_list(limit=1)
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from Globus services.
        """
        self.transfer_client = None
        self.search_client = None
        self.groups_client = None
        self.logger.info("Disconnected from Globus services")
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user.
        
        Returns:
            Dict with user information
        """
        if not self.auth_client or not self.transfer_client:
            self.logger.error("Not connected to Globus")
            return {"error": "Not connected to Globus"}
        
        try:
            # Get user info from Auth API
            auth_user_info = self.auth_client.oauth2_userinfo()
            
            # Get transfer-specific info
            transfer_info = self.transfer_client.get_task_list(limit=1)
            
            return {
                "user_info": auth_user_info.data,
                "connected": True,
                "transfer_endpoint_count": len(self.transfer_client.get_endpoint_list(limit=100).data)
            }
        except Exception as e:
            self.logger.error(f"Error getting account info: {str(e)}")
            return {"error": str(e)}