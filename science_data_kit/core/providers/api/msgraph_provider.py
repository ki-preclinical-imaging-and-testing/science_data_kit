"""
Microsoft Graph Provider for Science Data Kit

This module provides a provider for Microsoft Graph API, allowing
the Science Data Kit to interact with Microsoft 365 services.
"""

import os
import asyncio
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple

from ...db.msgraph_manager import MSGraphConnectionManager
from ..registry import BaseProvider, ProviderType

class MSGraphProvider(BaseProvider):
    """
    Provider for Microsoft Graph API.

    This class adapts the MSGraphConnectionManager to the BaseProvider interface,
    allowing it to be used with the provider registry.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Microsoft Graph API provider.

        Args:
            config: Configuration dictionary for the provider
        """
        super().__init__(config)
        
        # Extract configuration values
        tenant_id = config.get('tenant_id')
        client_id = config.get('client_id')
        client_secret = config.get('client_secret')
        auth_method = config.get('auth_method', 'device_code')
        config_file = config.get('config_file')
        enable_cache = config.get('enable_cache', True)
        cache_ttl = config.get('cache_ttl', 300)
        
        # Create the connection manager
        self.manager = MSGraphConnectionManager(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            auth_method=auth_method,
            config_file=config_file,
            enable_cache=enable_cache,
            cache_ttl=cache_ttl
        )
        
    async def initialize(self) -> bool:
        """
        Initialize the provider with the provided configuration.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Connect to Microsoft Graph API
            success = self.manager.connect()
            self.is_initialized = success
            return success
        except Exception as e:
            print(f"Error initializing Microsoft Graph provider: {str(e)}")
            self.is_initialized = False
            return False
    
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy and can be used.
        
        Returns:
            True if the provider is healthy, False otherwise
        """
        if not self.is_initialized:
            return False
        
        try:
            # Test the connection by getting the current user
            self.manager.get_me()
            return True
        except Exception:
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the provider.
        
        Returns:
            Dictionary of provider capabilities
        """
        return {
            "type": ProviderType.API.value,
            "name": "msgraph",
            "features": [
                "users",
                "groups",
                "messages",
                "events",
                "files"
            ],
            "auth_methods": [
                "client_credentials",
                "device_code",
                "interactive"
            ]
        }
    
    async def list_files(self) -> List[Dict[str, Any]]:
        """
        List files available in OneDrive.
        
        Returns:
            List of file metadata dictionaries
        """
        try:
            df = self.manager.get_my_files()
            
            # Convert DataFrame to list of dictionaries
            files = []
            for _, row in df.iterrows():
                file_type = "folder" if row.get("folder") else "file"
                
                # Determine file type based on name extension
                if file_type == "file":
                    name = row.get("name", "")
                    if name.lower().endswith(".csv"):
                        file_type = "csv"
                    elif name.lower().endswith((".xlsx", ".xls")):
                        file_type = "xlsx"
                    elif name.lower().endswith((".docx", ".doc")):
                        file_type = "docx"
                    elif name.lower().endswith(".txt"):
                        file_type = "txt"
                    elif name.lower().endswith(".pdf"):
                        file_type = "pdf"
                
                files.append({
                    "id": row.get("id", ""),
                    "name": row.get("name", ""),
                    "path": row.get("webUrl", ""),
                    "type": file_type,
                    "size": row.get("size", 0),
                    "modified": row.get("lastModifiedDateTime", "")
                })
            
            return files
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []
    
    async def download_file_data(self, file_id: str) -> Optional[pd.DataFrame]:
        """
        Download and parse file data.
        
        Args:
            file_id: ID of the file to download
            
        Returns:
            Pandas DataFrame containing the file data
        """
        try:
            # Get file content
            response = self.manager.execute_query(f"/me/drive/items/{file_id}/content")
            
            # Parse the content based on file type
            # Note: This is a simplified implementation
            # In a real implementation, you would need to handle different file types
            return pd.DataFrame(response)
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return None
    
    async def list_spreadsheets(self) -> List[Dict[str, Any]]:
        """
        List available Excel spreadsheets.
        
        Returns:
            List of spreadsheet metadata dictionaries
        """
        try:
            # Get all files
            files = await self.list_files()
            
            # Filter for Excel files
            spreadsheets = [
                {
                    "id": file["id"],
                    "name": file["name"],
                    "url": file["path"]
                }
                for file in files
                if file["type"] in ["xlsx", "xls"]
            ]
            
            return spreadsheets
        except Exception as e:
            print(f"Error listing spreadsheets: {str(e)}")
            return []
    
    async def list_sheets(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """
        List sheets in an Excel spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            
        Returns:
            List of sheet metadata dictionaries
        """
        try:
            # Get workbook information
            response = self.manager.execute_query(f"/me/drive/items/{spreadsheet_id}/workbook/worksheets")
            
            sheets = []
            for sheet in response.get("value", []):
                sheets.append({
                    "id": sheet.get("id", ""),
                    "name": sheet.get("name", ""),
                    "rows": sheet.get("rowCount", 0),
                    "columns": sheet.get("columnCount", 0)
                })
            
            return sheets
        except Exception as e:
            print(f"Error listing sheets: {str(e)}")
            return []
    
    async def get_sheet_data(self, spreadsheet_id: str, sheet_name: str) -> Optional[pd.DataFrame]:
        """
        Get data from a sheet in an Excel spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            sheet_name: Name of the sheet
            
        Returns:
            Pandas DataFrame containing the sheet data
        """
        try:
            # Get sheet data
            response = self.manager.execute_query(
                f"/me/drive/items/{spreadsheet_id}/workbook/worksheets/{sheet_name}/usedRange"
            )
            
            # Convert to DataFrame
            values = response.get("values", [])
            if not values:
                return pd.DataFrame()
            
            # Use first row as header
            headers = values[0]
            data = values[1:]
            
            return pd.DataFrame(data, columns=headers)
        except Exception as e:
            print(f"Error getting sheet data: {str(e)}")
            return None