"""
Dropbox Connect Page Module for Science Data Kit Core

This module provides the Dropbox Connect page for the Science Data Kit application.
It defines the framework-independent core functionality for the Dropbox Connect page.
"""

from typing import Dict, Any, Optional
import json
import os

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import DropboxConnectPageData
from science_data_kit_extensions.dropbox.connector import DropboxConnector

class DropboxConnectPage(BasePage):
    """
    Dropbox Connect page for managing connections to Dropbox.

    This class provides the core business logic for the Dropbox Connect page,
    independent of any UI framework.
    """

    def __init__(self, db_connection=None):
        """Initialize the Dropbox Connect page."""
        super().__init__(db_connection)
        self.connection_status = {"dropbox": False}
        self.connection_errors = {}
        self.account_info = None
        self.app_key = None
        self.app_secret = None
        self.refresh_token = None
        self.config_file = None
        self.auth_url = None
        self.connector = None

    def get_page_data(self) -> DropboxConnectPageData:
        """
        Return data needed to render the Dropbox Connect page.

        Returns:
            An instance of DropboxConnectPageData containing the data needed
            to render the Dropbox Connect page.
        """
        return DropboxConnectPageData(
            title="Connect to Dropbox",
            requires_auth=True,
            connection_status=self.connection_status,
            connection_errors=self.connection_errors,
            account_info=self.account_info,
            app_key=self.app_key,
            app_secret=self.app_secret,
            refresh_token=self.refresh_token,
            config_file=self.config_file,
            auth_url=self.auth_url
        )

    def connect(self, app_key: str, app_secret: str, refresh_token: Optional[str] = None, 
                save_config: bool = False, config_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Connect to Dropbox API.

        Args:
            app_key: The app key for the Dropbox application.
            app_secret: The app secret for the Dropbox application.
            refresh_token: The refresh token for the Dropbox application (optional).
            save_config: Whether to save the configuration to a file.
            config_file: The path to the configuration file (optional).

        Returns:
            A dictionary with connection status and error message if any.
        """
        result = {
            "success": False,
            "error": None,
            "auth_url": None
        }

        try:
            # Store configuration
            self.app_key = app_key
            self.app_secret = app_secret
            self.refresh_token = refresh_token
            self.config_file = config_file if save_config else None

            # Create connector
            self.connector = DropboxConnector(
                app_key=app_key,
                app_secret=app_secret,
                refresh_token=refresh_token
            )

            # Save configuration if requested
            if save_config and config_file:
                config = {
                    "app_key": app_key,
                    "app_secret": app_secret,
                    "refresh_token": refresh_token if refresh_token else None
                }

                try:
                    with open(config_file, 'w') as f:
                        json.dump(config, f, indent=4)
                    result["config_saved"] = True
                except Exception as e:
                    result["config_saved"] = False
                    result["config_error"] = str(e)

            # Check if connected
            if self.connector.is_connected():
                self.connection_status["dropbox"] = True
                
                # Get account info
                try:
                    self.account_info = self.connector.get_account_info()
                except Exception as e:
                    self.connection_errors["account_info"] = str(e)
                
                result["success"] = True
                return result
            else:
                # If not connected and no refresh token, start OAuth flow
                if not refresh_token:
                    auth_url = self.connector.authenticate()
                    self.auth_url = auth_url
                    result["auth_url"] = auth_url
                    return result
                else:
                    error_msg = "Failed to connect to Dropbox API with the provided refresh token."
                    result["error"] = error_msg
                    self.connection_errors["dropbox"] = error_msg
                    return result
        except Exception as e:
            error_msg = str(e)
            result["error"] = f"Failed to connect to Dropbox API: {error_msg}"
            self.connection_errors["dropbox"] = error_msg
            return result

    def complete_authentication(self, auth_code: str) -> Dict[str, Any]:
        """
        Complete the OAuth authentication flow.

        Args:
            auth_code: The authorization code from the OAuth flow.

        Returns:
            A dictionary with connection status and error message if any.
        """
        result = {
            "success": False,
            "error": None
        }

        try:
            if not self.connector:
                error_msg = "No connector available. Please start the authentication flow again."
                result["error"] = error_msg
                self.connection_errors["dropbox"] = error_msg
                return result

            # Complete authentication
            if self.connector.complete_authentication(auth_code):
                self.connection_status["dropbox"] = True
                self.refresh_token = self.connector.refresh_token
                
                # Get account info
                try:
                    self.account_info = self.connector.get_account_info()
                except Exception as e:
                    self.connection_errors["account_info"] = str(e)
                
                # Update saved configuration with new refresh token
                if self.config_file:
                    config = {
                        "app_key": self.app_key,
                        "app_secret": self.app_secret,
                        "refresh_token": self.connector.refresh_token
                    }

                    try:
                        with open(self.config_file, 'w') as f:
                            json.dump(config, f, indent=4)
                        result["config_saved"] = True
                    except Exception as e:
                        result["config_saved"] = False
                        result["config_error"] = str(e)
                
                result["success"] = True
                return result
            else:
                error_msg = "Failed to complete authentication. Please check the authorization code."
                result["error"] = error_msg
                self.connection_errors["dropbox"] = error_msg
                return result
        except Exception as e:
            error_msg = str(e)
            result["error"] = f"Failed to complete authentication: {error_msg}"
            self.connection_errors["dropbox"] = error_msg
            return result

    def disconnect(self) -> Dict[str, Any]:
        """
        Disconnect from Dropbox API.

        Returns:
            A dictionary with disconnection status and error message if any.
        """
        result = {
            "success": False,
            "error": None
        }

        try:
            # Reset connection state
            self.connector = None
            self.connection_status["dropbox"] = False
            self.account_info = None
            
            result["success"] = True
            return result
        except Exception as e:
            error_msg = str(e)
            result["error"] = f"Failed to disconnect from Dropbox API: {error_msg}"
            self.connection_errors["dropbox"] = error_msg
            return result

    def load_config_from_file(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from a file.

        Args:
            config_file: The path to the configuration file.

        Returns:
            A dictionary with the loaded configuration.
        """
        result = {
            "success": False,
            "error": None,
            "config": {}
        }

        try:
            if not os.path.exists(config_file):
                error_msg = f"Configuration file not found: {config_file}"
                result["error"] = error_msg
                return result

            with open(config_file, 'r') as f:
                config = json.load(f)

            if not isinstance(config, dict):
                error_msg = "Invalid configuration format"
                result["error"] = error_msg
                return result

            # Extract configuration
            app_key = config.get("app_key")
            app_secret = config.get("app_secret")
            refresh_token = config.get("refresh_token")

            if not app_key or not app_secret:
                error_msg = "Missing required configuration: app_key and app_secret"
                result["error"] = error_msg
                return result

            result["success"] = True
            result["config"] = {
                "app_key": app_key,
                "app_secret": app_secret,
                "refresh_token": refresh_token
            }
            return result
        except Exception as e:
            error_msg = str(e)
            result["error"] = f"Failed to load configuration: {error_msg}"
            return result