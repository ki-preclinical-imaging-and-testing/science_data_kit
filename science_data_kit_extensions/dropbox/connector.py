"""
Science Data Kit - Dropbox Extension
Connector Module

This module provides the DropboxConnector class, which is the main entry point
for interacting with Dropbox API.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect, Dropbox
from dropbox.exceptions import AuthError, ApiError

logger = logging.getLogger(__name__)

class DropboxConnector:
    """
    Main connector class for Dropbox integration.
    
    This class handles authentication, connection management, and provides
    methods for interacting with Dropbox API.
    """
    
    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        config_file: Optional[str] = None
    ):
        """
        Initialize the Dropbox connector.
        
        Args:
            app_key: Dropbox API app key
            app_secret: Dropbox API app secret
            refresh_token: OAuth2 refresh token for authentication
            config_file: Path to a configuration file containing credentials
        """
        self.app_key = app_key or os.environ.get("DROPBOX_APP_KEY")
        self.app_secret = app_secret or os.environ.get("DROPBOX_APP_SECRET")
        self.refresh_token = refresh_token or os.environ.get("DROPBOX_REFRESH_TOKEN")
        
        # Load configuration from file if provided
        if config_file:
            self._load_config(config_file)
            
        # Validate credentials
        if not self.app_key or not self.app_secret:
            raise ValueError(
                "Dropbox API credentials not provided. "
                "Please provide app_key and app_secret or set DROPBOX_APP_KEY "
                "and DROPBOX_APP_SECRET environment variables."
            )
            
        self.client = None
        self.connected = False
        
        # Connect if refresh token is available
        if self.refresh_token:
            self.connect()
    
    def _load_config(self, config_file: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_file: Path to the configuration file
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        # Determine file type and load accordingly
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            try:
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
            except ImportError:
                raise ImportError("PyYAML is required for YAML config files. Install with 'pip install pyyaml'.")
        elif config_path.suffix.lower() == '.json':
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        # Update credentials from config
        self.app_key = config.get('app_key', self.app_key)
        self.app_secret = config.get('app_secret', self.app_secret)
        self.refresh_token = config.get('refresh_token', self.refresh_token)
    
    def connect(self) -> bool:
        """
        Connect to Dropbox API using the provided credentials.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            if self.refresh_token:
                self.client = Dropbox(
                    oauth2_refresh_token=self.refresh_token,
                    app_key=self.app_key,
                    app_secret=self.app_secret
                )
                # Test the connection
                self.client.check_user()
                self.connected = True
                logger.info("Successfully connected to Dropbox API using refresh token")
                return True
            else:
                logger.warning("No refresh token available, authentication required")
                return False
        except AuthError as e:
            logger.error(f"Authentication error: {e}")
            self.connected = False
            return False
        except ApiError as e:
            logger.error(f"API error during connection: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            self.connected = False
            return False
    
    def authenticate(self) -> str:
        """
        Start the OAuth2 authentication flow.
        
        Returns:
            str: URL for the user to visit to authorize the application
        """
        auth_flow = DropboxOAuth2FlowNoRedirect(
            self.app_key,
            self.app_secret,
            token_access_type="offline"
        )
        auth_url = auth_flow.start()
        return auth_url
    
    def complete_authentication(self, auth_code: str) -> bool:
        """
        Complete the OAuth2 authentication flow with the provided code.
        
        Args:
            auth_code: Authorization code from Dropbox
            
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        try:
            auth_flow = DropboxOAuth2FlowNoRedirect(
                self.app_key,
                self.app_secret,
                token_access_type="offline"
            )
            oauth_result = auth_flow.finish(auth_code)
            
            # Store the refresh token
            self.refresh_token = oauth_result.refresh_token
            
            # Connect with the new token
            return self.connect()
        except Exception as e:
            logger.error(f"Error completing authentication: {e}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if the connector is connected to Dropbox API.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.client or not self.connected:
            return False
            
        try:
            # Test the connection by making a simple API call
            self.client.check_user()
            return True
        except Exception:
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from Dropbox API.
        """
        self.client = None
        self.connected = False
        logger.info("Disconnected from Dropbox API")
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get information about the connected Dropbox account.
        
        Returns:
            Dict[str, Any]: Account information
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Dropbox API")
            
        try:
            account_info = self.client.users_get_current_account()
            return {
                'account_id': account_info.account_id,
                'name': f"{account_info.name.given_name} {account_info.name.surname}",
                'email': account_info.email,
                'country': account_info.country,
                'team': account_info.team.name if account_info.team else None,
                'team_member_id': account_info.team_member_id if account_info.team_member_id else None
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise