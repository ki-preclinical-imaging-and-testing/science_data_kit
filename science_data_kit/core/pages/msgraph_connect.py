"""
Microsoft Graph Connection Page for Science Data Kit

This module defines the MSGraphConnectPage class, which provides functionality for
connecting to the Microsoft Graph API.
"""

from typing import Dict, Any, Optional, List
import os
import json

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import MSGraphConnectPageData
from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter
from science_data_kit.core.utils.msgraph_utils import create_msgraph_config

class MSGraphConnectPage(BasePage):
    """
    Microsoft Graph connection page for the Science Data Kit.
    
    This page provides functionality for connecting to the Microsoft Graph API,
    managing connection status, and retrieving user information.
    """
    
    def __init__(self):
        """
        Initialize the MSGraphConnectPage.
        """
        super().__init__()
        self.page_data = MSGraphConnectPageData(title="Connect to Microsoft Graph API")
        self.connection_manager = None
        self.adapter = None
        
        # Check if Microsoft Graph SDK is available
        try:
            from msgraph.core import GraphClient
            from azure.identity import ClientSecretCredential, DeviceCodeCredential, InteractiveBrowserCredential
            self.page_data.msgraph_available = True
        except ImportError:
            self.page_data.msgraph_available = False
            self.page_data.connection_errors["msgraph"] = "Microsoft Graph SDK is not installed. Please install it with 'pip install msgraph-sdk-python azure-identity'."
    
    def get_page_data(self) -> MSGraphConnectPageData:
        """
        Get the page data for the Microsoft Graph connection page.
        
        Returns:
            MSGraphConnectPageData: The page data for the Microsoft Graph connection page.
        """
        return self.page_data
    
    def connect(self, tenant_id: str, client_id: str, client_secret: Optional[str] = None, 
                auth_method: str = "device_code", config_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Connect to the Microsoft Graph API.
        
        Args:
            tenant_id: The tenant ID for the Microsoft 365 account.
            client_id: The client ID for the application.
            client_secret: The client secret for the application (only for client_credentials).
            auth_method: The authentication method to use (device_code, client_credentials, or interactive).
            config_file: Optional path to save the configuration to.
            
        Returns:
            Dict[str, Any]: A dictionary with the connection result.
        """
        try:
            if not self.page_data.msgraph_available:
                return {
                    "success": False,
                    "message": "Microsoft Graph SDK is not installed. Please install it with 'pip install msgraph-sdk-python azure-identity'."
                }
            
            # Save configuration if requested
            if config_file:
                config = create_msgraph_config(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret if auth_method == "client_credentials" else None,
                    auth_method=auth_method,
                    output_file=config_file
                )
            
            # Create connection manager
            self.connection_manager = MSGraphConnectionManager(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret if auth_method == "client_credentials" else None,
                auth_method=auth_method,
                config_file=config_file
            )
            
            # Connect to Microsoft Graph API
            if self.connection_manager.connect():
                # Store configuration in page data
                self.page_data.tenant_id = tenant_id
                self.page_data.client_id = client_id
                if auth_method == "client_credentials":
                    self.page_data.client_secret = client_secret
                self.page_data.auth_method = auth_method
                self.page_data.config_file = config_file
                
                # Update connection status
                self.page_data.connection_status["msgraph"] = True
                self.page_data.connection_errors = {}
                
                # Create adapter
                self.adapter = MSGraphAdapter(connection_manager=self.connection_manager)
                
                # Get user information
                try:
                    self.page_data.user_info = self.connection_manager.get_me()
                except Exception as e:
                    self.page_data.user_info = None
                    self.page_data.connection_errors["user_info"] = str(e)
                
                return {
                    "success": True,
                    "message": "Connected to Microsoft Graph API successfully",
                    "user_info": self.page_data.user_info
                }
            else:
                self.page_data.connection_status["msgraph"] = False
                self.page_data.connection_errors["msgraph"] = "Failed to connect to Microsoft Graph API"
                return {
                    "success": False,
                    "message": "Failed to connect to Microsoft Graph API"
                }
        except Exception as e:
            self.page_data.connection_status["msgraph"] = False
            self.page_data.connection_errors["msgraph"] = str(e)
            return {
                "success": False,
                "message": f"Error connecting to Microsoft Graph API: {str(e)}"
            }
    
    def disconnect(self) -> Dict[str, Any]:
        """
        Disconnect from the Microsoft Graph API.
        
        Returns:
            Dict[str, Any]: A dictionary with the disconnection result.
        """
        try:
            # Reset connection manager and adapter
            self.connection_manager = None
            self.adapter = None
            
            # Update connection status
            self.page_data.connection_status["msgraph"] = False
            self.page_data.connection_errors = {}
            self.page_data.user_info = None
            
            return {
                "success": True,
                "message": "Disconnected from Microsoft Graph API successfully"
            }
        except Exception as e:
            self.page_data.connection_errors["msgraph"] = str(e)
            return {
                "success": False,
                "message": f"Error disconnecting from Microsoft Graph API: {str(e)}"
            }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get the current connection status.
        
        Returns:
            Dict[str, Any]: A dictionary with the connection status.
        """
        if self.connection_manager and self.connection_manager.connected:
            return {
                "connected": True,
                "user_info": self.page_data.user_info
            }
        else:
            return {
                "connected": False,
                "errors": self.page_data.connection_errors
            }
    
    def load_config_from_file(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_file: The path to the configuration file.
            
        Returns:
            Dict[str, Any]: A dictionary with the loaded configuration.
        """
        try:
            if not os.path.exists(config_file):
                return {
                    "success": False,
                    "message": f"Configuration file not found: {config_file}"
                }
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Update page data with loaded configuration
            self.page_data.tenant_id = config.get("tenant_id")
            self.page_data.client_id = config.get("client_id")
            self.page_data.client_secret = config.get("client_secret")
            self.page_data.auth_method = config.get("auth_method", "device_code")
            self.page_data.config_file = config_file
            
            return {
                "success": True,
                "message": f"Configuration loaded from {config_file}",
                "config": config
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error loading configuration: {str(e)}"
            }
    
    def save_config_to_file(self, config_file: str) -> Dict[str, Any]:
        """
        Save configuration to a file.
        
        Args:
            config_file: The path to save the configuration to.
            
        Returns:
            Dict[str, Any]: A dictionary with the save result.
        """
        try:
            config = {
                "tenant_id": self.page_data.tenant_id,
                "client_id": self.page_data.client_id,
                "client_secret": self.page_data.client_secret if self.page_data.auth_method == "client_credentials" else None,
                "auth_method": self.page_data.auth_method
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            self.page_data.config_file = config_file
            
            return {
                "success": True,
                "message": f"Configuration saved to {config_file}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error saving configuration: {str(e)}"
            }