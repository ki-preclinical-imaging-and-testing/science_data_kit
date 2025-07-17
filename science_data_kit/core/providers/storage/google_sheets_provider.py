"""
Google Sheets Provider for Science Data Kit

This module provides a Google Sheets provider for accessing spreadsheet data
from Google Sheets.

This is a compatibility layer that uses the new GoogleSheetsPlugin under the hood
while maintaining the old interface for backward compatibility.
"""

import io
import os
import pandas as pd
import warnings
from typing import Dict, List, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from ...providers.registry import BaseProvider
from science_data_kit.core.connections.manager import manager
from science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin import GoogleSheetsPlugin


class GoogleSheetsProvider(BaseProvider):
    """
    Google Sheets provider for spreadsheet data access

    This is a compatibility layer that uses the new GoogleSheetsPlugin under the hood
    while maintaining the old interface for backward compatibility.
    """

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Google Sheets provider.

        Args:
            config: Configuration dictionary containing Google Sheets credentials
        """
        super().__init__(config)
        self.service = None
        self.credentials = None
        self._plugin = None

        # Emit deprecation warning
        warnings.warn(
            "GoogleSheetsProvider is deprecated and will be removed in a future version. "
            "Please use the new plugin architecture instead. "
            "See docs/guides/plugin_migration_guide.md for migration instructions.",
            DeprecationWarning,
            stacklevel=2
        )

    async def initialize(self) -> bool:
        """
        Initialize Google Sheets API connection using OAuth2.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Get credentials from config
            credentials_file = self.config.get("credentials_file")
            token_file = self.config.get("token_file", "token.json")

            if not credentials_file:
                print("Google Sheets credentials file not found in configuration")
                return False

            # Initialize the plugin
            try:
                # Try to get the plugin from the manager
                self._plugin = manager.get_plugin_instance("google_sheets")
            except Exception:
                # If the plugin is not registered, create a new instance
                self._plugin = GoogleSheetsPlugin()

            # Convert old config format to new format
            plugin_config = {
                "credentials_file": credentials_file,
                "token_file": token_file
            }

            # Connect to the plugin
            self._plugin.connect(plugin_config)

            # For backward compatibility, also initialize the service and credentials
            # Load or create credentials
            self.credentials = self._get_credentials(credentials_file, token_file)
            if not self.credentials:
                return False

            # Create Google Sheets service
            self.service = build('sheets', 'v4', credentials=self.credentials)

            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Error initializing Google Sheets provider: {str(e)}")
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
            credentials = Credentials.from_authorized_user_info(
                info=eval(open(token_file, 'r').read()),
                scopes=self.SCOPES
            )

        # If credentials don't exist or are invalid, get new ones
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, self.SCOPES)
                credentials = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(str(credentials.to_json()))

        return credentials

    async def health_check(self) -> bool:
        """
        Verify Google Sheets connection is working.

        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized or not self._plugin:
            return False

        try:
            # Use the plugin's test_connection method
            return self._plugin.test_connection()
        except Exception as e:
            print(f"Google Sheets health check failed: {str(e)}")
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return provider capabilities.

        Returns:
            Dictionary of provider capabilities
        """
        return {
            "data_types": ["spreadsheet"],
            "real_time": False,
            "formats": ["sheets"],
            "max_size": "5,000,000 cells"  # Google Sheets cell limit
        }

    async def list_spreadsheets(self) -> List[Dict[str, Any]]:
        """
        List available Google Sheets spreadsheets.

        Returns:
            List of spreadsheet metadata dictionaries
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Google Sheets provider not initialized")

        try:
            # Use the plugin's list_spreadsheets method
            return self._plugin.list_spreadsheets()

        except Exception as e:
            print(f"Error listing Google Sheets spreadsheets: {str(e)}")
            raise

    async def list_sheets(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """
        List sheets in a Google Sheets spreadsheet.

        Args:
            spreadsheet_id: ID of the spreadsheet

        Returns:
            List of sheet metadata dictionaries
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Google Sheets provider not initialized")

        try:
            # Use the plugin's list_sheets method
            return self._plugin.list_sheets(spreadsheet_id)

        except Exception as e:
            print(f"Error listing sheets in spreadsheet: {str(e)}")
            raise

    async def get_sheet_data(self, spreadsheet_id: str, sheet_name: str) -> pd.DataFrame:
        """
        Get data from a sheet in a Google Sheets spreadsheet.

        Args:
            spreadsheet_id: ID of the spreadsheet
            sheet_name: Name of the sheet

        Returns:
            Pandas DataFrame containing the sheet data
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Google Sheets provider not initialized")

        try:
            # Use the plugin's get_sheet_data method
            return self._plugin.get_sheet_data(spreadsheet_id, sheet_name)

        except Exception as e:
            print(f"Error getting sheet data: {str(e)}")
            raise

    async def get_spreadsheet_info(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Get spreadsheet metadata.

        Args:
            spreadsheet_id: ID of the spreadsheet

        Returns:
            Dictionary containing spreadsheet metadata
        """
        if not self.is_initialized or not self._plugin:
            raise Exception("Google Sheets provider not initialized")

        try:
            # Use the plugin's get_spreadsheet_info method
            return self._plugin.get_spreadsheet_info(spreadsheet_id)

        except Exception as e:
            print(f"Error getting spreadsheet info: {str(e)}")
            raise
