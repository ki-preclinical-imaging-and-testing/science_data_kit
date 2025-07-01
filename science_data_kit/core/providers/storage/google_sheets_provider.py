"""
Google Sheets Provider for Science Data Kit

This module provides a Google Sheets provider for accessing spreadsheet data
from Google Sheets.
"""

import io
import os
import pandas as pd
from typing import Dict, List, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from ...providers.registry import BaseProvider


class GoogleSheetsProvider(BaseProvider):
    """Google Sheets provider for spreadsheet data access"""
    
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
        if not self.is_initialized or not self.service:
            return False
        
        try:
            # Try to list spreadsheets to verify connection
            drive_service = build('drive', 'v3', credentials=self.credentials)
            drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                fields="files(id, name)"
            ).execute()
            return True
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
        if not self.is_initialized or not self.service:
            raise Exception("Google Sheets provider not initialized")
        
        try:
            # Use Drive API to list spreadsheets
            drive_service = build('drive', 'v3', credentials=self.credentials)
            results = drive_service.files().list(
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
        if not self.is_initialized or not self.service:
            raise Exception("Google Sheets provider not initialized")
        
        try:
            # Get spreadsheet metadata
            spreadsheet = self.service.spreadsheets().get(
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
        if not self.is_initialized or not self.service:
            raise Exception("Google Sheets provider not initialized")
        
        try:
            # Get sheet data
            result = self.service.spreadsheets().values().get(
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
        if not self.is_initialized or not self.service:
            raise Exception("Google Sheets provider not initialized")
        
        try:
            # Get spreadsheet metadata
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            # Get Drive file metadata for additional info
            drive_service = build('drive', 'v3', credentials=self.credentials)
            file_metadata = drive_service.files().get(
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
            print(f"Error getting spreadsheet info: {str(e)}")
            raise