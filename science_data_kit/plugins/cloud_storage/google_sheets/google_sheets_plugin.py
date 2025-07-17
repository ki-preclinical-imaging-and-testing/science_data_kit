"""
Google Sheets Plugin for Science Data Kit.

This module provides a plugin for accessing spreadsheet data from Google Sheets.
It implements the APIPluginInterface and provides methods for
spreadsheet operations using the Google Sheets API.
"""

import os
import logging
import pandas as pd
from typing import Any, Dict, List, Optional, Set, Union
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

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
class GoogleSheetsPlugin(APIPluginInterface):
    """
    Plugin for accessing spreadsheet data from Google Sheets.
    
    This plugin provides access to spreadsheet data from Google Sheets,
    with authentication and connection management.
    """
    
    # Define the scopes needed for Google Sheets access
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self):
        """Initialize the plugin."""
        self._name = "google_sheets"
        self._version = "1.0.0"
        self._description = "Plugin for accessing spreadsheet data from Google Sheets"
        self._is_initialized = False
        self._is_connected = False
        self._config = {}
        self._service = None
        self._drive_service = None
        self._credentials = None
        
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
                    name="credentials_file",
                    field_type=ConfigFieldType.FILE_PATH,
                    description="Path to the credentials file",
                    required=True,
                ),
                ConfigField(
                    name="token_file",
                    field_type=ConfigFieldType.FILE_PATH,
                    description="Path to the token file",
                    required=False,
                    default="token.json",
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
            
        # Additional validation: credentials_file must exist
        credentials_file = config.get("credentials_file")
        if not credentials_file or not os.path.exists(credentials_file):
            logger.error(f"Credentials file does not exist: {credentials_file}")
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
            logger.error("Invalid configuration for Google Sheets plugin")
            return False
            
        self._config = config
        
        try:
            # Get credentials from config
            credentials_file = config.get("credentials_file")
            token_file = config.get("token_file", "token.json")
            
            # Load or create credentials
            self._credentials = self._get_credentials(credentials_file, token_file)
            if not self._credentials:
                logger.error("Failed to obtain valid Google Sheets credentials")
                return False
                
            self._is_initialized = True
            logger.info("Google Sheets plugin initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Google Sheets plugin: {e}")
            self._is_initialized = False
            return False
        
    def _get_credentials(self, credentials_file: str, token_file: str) -> Optional[Credentials]:
        """
        Get OAuth2 credentials for Google Sheets API.
        
        Args:
            credentials_file: Path to the credentials file
            token_file: Path to the token file
            
        Returns:
            Credentials object if successful, None otherwise
        """
        credentials = None
        
        # Check if token file exists
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r') as token:
                    credentials = Credentials.from_authorized_user_info(
                        info=eval(token.read()),
                        scopes=self.SCOPES
                    )
            except Exception as e:
                logger.error(f"Error loading token file: {e}")
                return None
        
        # If credentials don't exist or are invalid, get new ones
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    return None
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, self.SCOPES)
                    credentials = flow.run_local_server(port=0)
                except Exception as e:
                    logger.error(f"Error running OAuth flow: {e}")
                    return None
            
            # Save the credentials for the next run
            try:
                with open(token_file, 'w') as token:
                    token.write(str(credentials.to_json()))
            except Exception as e:
                logger.error(f"Error saving token file: {e}")
                # Continue even if we couldn't save the token
        
        return credentials
        
    def shutdown(self) -> bool:
        """
        Shut down the plugin and release any resources.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        if self._is_connected:
            self.disconnect()
            
        self._service = None
        self._drive_service = None
        self._credentials = None
        self._is_initialized = False
        logger.info("Google Sheets plugin shut down")
        return True
        
    @property
    def is_initialized(self) -> bool:
        """Check if the plugin is initialized."""
        return self._is_initialized
        
    @property
    def capabilities(self) -> Set[str]:
        """Get the plugin capabilities."""
        capabilities = {"api", "spreadsheet", "readable"}
        return capabilities
        
    def connect(self, config: Dict[str, Any]) -> None:
        """
        Establish connection with Google Sheets.
        
        Args:
            config: Configuration dictionary for the connection
        """
        if not self._is_initialized:
            if not self.initialize(config):
                raise RuntimeError("Failed to initialize Google Sheets plugin")
                
        try:
            # Create Google Sheets service
            self._service = build('sheets', 'v4', credentials=self._credentials)
            
            # Create Drive service for listing spreadsheets
            self._drive_service = build('drive', 'v3', credentials=self._credentials)
            
            # Test connection by listing spreadsheets (limit to 1)
            self._drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=1
            ).execute()
            
            self._is_connected = True
            logger.info("Connected to Google Sheets API")
        except Exception as e:
            logger.error(f"Error connecting to Google Sheets: {e}")
            self._is_connected = False
            raise RuntimeError(f"Failed to connect to Google Sheets: {e}")
        
    def disconnect(self) -> None:
        """Clean up connection."""
        self._service = None
        self._drive_service = None
        self._is_connected = False
        logger.info("Disconnected from Google Sheets API")
        
    def test_connection(self) -> bool:
        """
        Verify connection is working.
        
        Returns:
            True if connection is working, False otherwise
        """
        if not self._is_connected or not self._service or not self._drive_service:
            return False
            
        try:
            # Try to list spreadsheets to verify connection (limit to 1)
            self._drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=1
            ).execute()
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
        return self._is_connected and self._service is not None and self._drive_service is not None
        
    def request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        """
        Make an API request.
        
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
            raise RuntimeError("Not connected to Google Sheets")
            
        # This is a simplified implementation that doesn't actually make HTTP requests directly
        # Instead, it uses the Google API client library which handles the HTTP requests internally
        
        # Parse the endpoint to determine what API call to make
        parts = endpoint.strip('/').split('/')
        
        if len(parts) < 1:
            raise ValueError(f"Invalid endpoint: {endpoint}")
            
        service_name = parts[0]
        
        if service_name == 'spreadsheets':
            if len(parts) < 3:
                raise ValueError(f"Invalid spreadsheets endpoint: {endpoint}")
                
            spreadsheet_id = parts[1]
            action = parts[2]
            
            if action == 'values' and method.upper() == 'GET':
                # Handle GET /spreadsheets/{spreadsheet_id}/values/{range}
                if len(parts) < 4:
                    raise ValueError(f"Invalid values endpoint: {endpoint}")
                    
                range_name = parts[3]
                return self._service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    **(params or {})
                ).execute()
            elif action == 'get' and method.upper() == 'GET':
                # Handle GET /spreadsheets/{spreadsheet_id}/get
                return self._service.spreadsheets().get(
                    spreadsheetId=spreadsheet_id,
                    **(params or {})
                ).execute()
        elif service_name == 'files' and method.upper() == 'GET':
            # Handle GET /files/list
            if len(parts) > 1 and parts[1] == 'list':
                return self._drive_service.files().list(
                    **(params or {})
                ).execute()
            # Handle GET /files/{file_id}
            elif len(parts) > 1:
                file_id = parts[1]
                return self._drive_service.files().get(
                    fileId=file_id,
                    **(params or {})
                ).execute()
                
        raise ValueError(f"Unsupported endpoint or method: {method} {endpoint}")
        
    def get_endpoints(self) -> List[str]:
        """
        Get a list of available endpoints.
        
        Returns:
            List of endpoint names
        """
        return [
            "/spreadsheets/{spreadsheet_id}/values/{range}",
            "/spreadsheets/{spreadsheet_id}/get",
            "/files/list",
            "/files/{file_id}"
        ]
        
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get the current rate limit status.
        
        Returns:
            Rate limit information
        """
        # Google Sheets API doesn't provide a direct way to get rate limit status
        # This is a placeholder implementation
        return {
            "quota": {
                "limit": "Unknown",
                "remaining": "Unknown",
                "reset": "Unknown"
            }
        }
        
    # Additional methods specific to Google Sheets
    
    def list_spreadsheets(self) -> List[Dict[str, Any]]:
        """
        List available Google Sheets spreadsheets.
        
        Returns:
            List of spreadsheet metadata dictionaries
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Google Sheets")
            
        try:
            # Use Drive API to list spreadsheets
            results = self._drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                fields="files(id, name, createdTime, modifiedTime)"
            ).execute()
            
            spreadsheets = []
            for item in results.get('files', []):
                spreadsheets.append({
                    "id": item['id'],
                    "name": item['name'],
                    "created": item.get('createdTime'),
                    "modified": item.get('modifiedTime'),
                    "type": "spreadsheet"
                })
            
            return spreadsheets
        except Exception as e:
            logger.error(f"Error listing Google Sheets spreadsheets: {e}")
            raise
        
    def list_sheets(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """
        List sheets in a Google Sheets spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            
        Returns:
            List of sheet metadata dictionaries
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Google Sheets")
            
        try:
            # Get spreadsheet metadata
            spreadsheet = self._service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets = []
            for sheet in spreadsheet.get('sheets', []):
                properties = sheet.get('properties', {})
                sheets.append({
                    "id": properties.get('sheetId'),
                    "name": properties.get('title'),
                    "index": properties.get('index'),
                    "rows": properties.get('gridProperties', {}).get('rowCount'),
                    "columns": properties.get('gridProperties', {}).get('columnCount')
                })
            
            return sheets
        except Exception as e:
            logger.error(f"Error listing sheets in spreadsheet: {e}")
            raise
        
    def get_sheet_data(self, spreadsheet_id: str, sheet_name: str) -> pd.DataFrame:
        """
        Get data from a sheet in a Google Sheets spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            sheet_name: Name of the sheet
            
        Returns:
            Pandas DataFrame containing the sheet data
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Google Sheets")
            
        try:
            # Get sheet data
            result = self._service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=sheet_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(values)
            
            # Use first row as header
            df.columns = df.iloc[0]
            df = df.drop(0)
            
            return df
        except Exception as e:
            logger.error(f"Error getting sheet data: {e}")
            raise
        
    def get_spreadsheet_info(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Get spreadsheet metadata.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            
        Returns:
            Dictionary containing spreadsheet metadata
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Google Sheets")
            
        try:
            # Get spreadsheet metadata
            spreadsheet = self._service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            # Get Drive file metadata for additional info
            file_metadata = self._drive_service.files().get(
                fileId=spreadsheet_id,
                fields="name,createdTime,modifiedTime,owners"
            ).execute()
            
            return {
                "id": spreadsheet_id,
                "name": file_metadata.get('name'),
                "created": file_metadata.get('createdTime'),
                "modified": file_metadata.get('modifiedTime'),
                "owner": file_metadata.get('owners', [{}])[0].get('displayName', 'Unknown'),
                "sheets": len(spreadsheet.get('sheets', [])),
                "type": "spreadsheet"
            }
        except Exception as e:
            logger.error(f"Error getting spreadsheet info: {e}")
            raise