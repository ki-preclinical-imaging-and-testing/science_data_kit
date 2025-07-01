"""
Unit tests for the Google Sheets provider.
"""

import unittest
import pandas as pd
import io
from unittest.mock import patch, MagicMock
from google.oauth2.credentials import Credentials

from science_data_kit.core.providers.storage.google_sheets_provider import GoogleSheetsProvider


class TestGoogleSheetsProvider(unittest.TestCase):
    """Test cases for the GoogleSheetsProvider class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "credentials_file": "test_credentials.json",
            "token_file": "test_token.json"
        }
        
        # Create patchers for the Google API clients
        self.credentials_patcher = patch('science_data_kit.core.providers.storage.google_sheets_provider.Credentials')
        self.flow_patcher = patch('science_data_kit.core.providers.storage.google_sheets_provider.InstalledAppFlow')
        self.request_patcher = patch('science_data_kit.core.providers.storage.google_sheets_provider.Request')
        self.build_patcher = patch('science_data_kit.core.providers.storage.google_sheets_provider.build')
        
        # Start the patchers
        self.mock_credentials = self.credentials_patcher.start()
        self.mock_flow = self.flow_patcher.start()
        self.mock_request = self.request_patcher.start()
        self.mock_build = self.build_patcher.start()
        
        # Create mock services
        self.mock_sheets_service = MagicMock()
        self.mock_drive_service = MagicMock()
        
        # Configure the build mock to return different services based on the service name
        def mock_build_side_effect(service_name, version, credentials):
            if service_name == 'sheets':
                return self.mock_sheets_service
            elif service_name == 'drive':
                return self.mock_drive_service
            return MagicMock()
        
        self.mock_build.side_effect = mock_build_side_effect
        
        # Create mock credentials
        self.mock_creds = MagicMock(spec=Credentials)
        self.mock_creds.valid = True
        
        # Configure the _get_credentials method to return mock credentials
        with patch.object(GoogleSheetsProvider, '_get_credentials', return_value=self.mock_creds):
            # Create the provider
            self.provider = GoogleSheetsProvider(self.config)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.credentials_patcher.stop()
        self.flow_patcher.stop()
        self.request_patcher.stop()
        self.build_patcher.stop()
    
    async def test_initialize_success(self):
        """Test successful initialization of the provider."""
        # Configure the _get_credentials method to return mock credentials
        with patch.object(GoogleSheetsProvider, '_get_credentials', return_value=self.mock_creds):
            # Call the method
            result = await self.provider.initialize()
            
            # Verify the result
            self.assertTrue(result)
            self.assertTrue(self.provider.is_initialized)
            self.mock_build.assert_called_with('sheets', 'v4', credentials=self.mock_creds)
    
    async def test_initialize_missing_credentials_file(self):
        """Test initialization with missing credentials file."""
        # Create a provider with empty config
        provider = GoogleSheetsProvider({})
        
        # Call the method
        result = await provider.initialize()
        
        # Verify the result
        self.assertFalse(result)
        self.assertFalse(provider.is_initialized)
        self.mock_build.assert_not_called()
    
    async def test_initialize_credentials_error(self):
        """Test initialization with credentials error."""
        # Configure the _get_credentials method to return None
        with patch.object(GoogleSheetsProvider, '_get_credentials', return_value=None):
            # Create a new provider
            provider = GoogleSheetsProvider(self.config)
            
            # Call the method
            result = await provider.initialize()
            
            # Verify the result
            self.assertFalse(result)
            self.assertFalse(provider.is_initialized)
            self.mock_build.assert_not_called()
    
    async def test_health_check_success(self):
        """Test successful health check."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.service = self.mock_sheets_service
        self.provider.credentials = self.mock_creds
        
        # Set up the mock
        mock_files = self.mock_drive_service.files.return_value
        mock_list = mock_files.list.return_value
        mock_list.execute.return_value = {"files": []}
        
        # Call the method
        result = await self.provider.health_check()
        
        # Verify the result
        self.assertTrue(result)
        self.mock_build.assert_called_with('drive', 'v3', credentials=self.mock_creds)
        mock_files.list.assert_called_once()
    
    async def test_health_check_not_initialized(self):
        """Test health check when provider is not initialized."""
        # Set up the provider as not initialized
        self.provider.is_initialized = False
        
        # Call the method
        result = await self.provider.health_check()
        
        # Verify the result
        self.assertFalse(result)
    
    async def test_health_check_error(self):
        """Test health check with error."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.service = self.mock_sheets_service
        self.provider.credentials = self.mock_creds
        
        # Set up the mock to raise an exception
        mock_files = self.mock_drive_service.files.return_value
        mock_list = mock_files.list.return_value
        mock_list.execute.side_effect = Exception("Test error")
        
        # Call the method
        result = await self.provider.health_check()
        
        # Verify the result
        self.assertFalse(result)
        self.mock_build.assert_called_with('drive', 'v3', credentials=self.mock_creds)
        mock_files.list.assert_called_once()
    
    def test_get_capabilities(self):
        """Test getting provider capabilities."""
        # Call the method
        capabilities = self.provider.get_capabilities()
        
        # Verify the result
        self.assertIsInstance(capabilities, dict)
        self.assertIn("data_types", capabilities)
        self.assertIn("real_time", capabilities)
        self.assertIn("formats", capabilities)
        self.assertIn("max_size", capabilities)
        
        self.assertIn("sheets", capabilities["formats"])
        self.assertIn("spreadsheet", capabilities["data_types"])
        self.assertFalse(capabilities["real_time"])
    
    async def test_list_spreadsheets_success(self):
        """Test listing spreadsheets successfully."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.service = self.mock_sheets_service
        self.provider.credentials = self.mock_creds
        
        # Set up the mock response
        mock_files = self.mock_drive_service.files.return_value
        mock_list = mock_files.list.return_value
        mock_list.execute.return_value = {
            "files": [
                {
                    "id": "spreadsheet1",
                    "name": "Test Spreadsheet",
                    "createdTime": "2023-01-01T00:00:00",
                    "modifiedTime": "2023-01-02T00:00:00"
                }
            ]
        }
        
        # Call the method
        result = await self.provider.list_spreadsheets()
        
        # Verify the result
        self.assertEqual(len(result), 1)
        
        # Verify spreadsheet entry
        spreadsheet = result[0]
        self.assertEqual(spreadsheet["id"], "spreadsheet1")
        self.assertEqual(spreadsheet["name"], "Test Spreadsheet")
        self.assertEqual(spreadsheet["created"], "2023-01-01T00:00:00")
        self.assertEqual(spreadsheet["modified"], "2023-01-02T00:00:00")
        self.assertEqual(spreadsheet["type"], "spreadsheet")
        
        # Verify the mock was called correctly
        self.mock_build.assert_called_with('drive', 'v3', credentials=self.mock_creds)
        mock_files.list.assert_called_once_with(
            q="mimeType='application/vnd.google-apps.spreadsheet'",
            fields="files(id, name, createdTime, modifiedTime)"
        )
    
    async def test_list_spreadsheets_not_initialized(self):
        """Test listing spreadsheets when provider is not initialized."""
        # Set up the provider as not initialized
        self.provider.is_initialized = False
        
        # Call the method and verify it raises an exception
        with self.assertRaises(Exception):
            await self.provider.list_spreadsheets()
    
    async def test_list_sheets_success(self):
        """Test listing sheets successfully."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.service = self.mock_sheets_service
        self.provider.credentials = self.mock_creds
        
        # Set up the mock response
        mock_spreadsheets = self.mock_sheets_service.spreadsheets.return_value
        mock_get = mock_spreadsheets.get.return_value
        mock_get.execute.return_value = {
            "sheets": [
                {
                    "properties": {
                        "sheetId": "sheet1",
                        "title": "Sheet1",
                        "index": 0,
                        "gridProperties": {
                            "rowCount": 100,
                            "columnCount": 26
                        }
                    }
                }
            ]
        }
        
        # Call the method
        result = await self.provider.list_sheets("spreadsheet1")
        
        # Verify the result
        self.assertEqual(len(result), 1)
        
        # Verify sheet entry
        sheet = result[0]
        self.assertEqual(sheet["id"], "sheet1")
        self.assertEqual(sheet["name"], "Sheet1")
        self.assertEqual(sheet["index"], 0)
        self.assertEqual(sheet["rows"], 100)
        self.assertEqual(sheet["columns"], 26)
        
        # Verify the mock was called correctly
        mock_spreadsheets.get.assert_called_once_with(spreadsheetId="spreadsheet1")
    
    async def test_list_sheets_not_initialized(self):
        """Test listing sheets when provider is not initialized."""
        # Set up the provider as not initialized
        self.provider.is_initialized = False
        
        # Call the method and verify it raises an exception
        with self.assertRaises(Exception):
            await self.provider.list_sheets("spreadsheet1")
    
    async def test_get_sheet_data_success(self):
        """Test getting sheet data successfully."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.service = self.mock_sheets_service
        self.provider.credentials = self.mock_creds
        
        # Set up the mock response
        mock_spreadsheets = self.mock_sheets_service.spreadsheets.return_value
        mock_values = mock_spreadsheets.values.return_value
        mock_get = mock_values.get.return_value
        mock_get.execute.return_value = {
            "values": [
                ["Header1", "Header2"],
                ["Value1", "Value2"]
            ]
        }
        
        # Call the method
        result = await self.provider.get_sheet_data("spreadsheet1", "Sheet1")
        
        # Verify the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, (1, 2))
        self.assertEqual(list(result.columns), ["Header1", "Header2"])
        
        # Verify the mock was called correctly
        mock_values.get.assert_called_once_with(spreadsheetId="spreadsheet1", range="Sheet1")
    
    async def test_get_sheet_data_empty(self):
        """Test getting empty sheet data."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.service = self.mock_sheets_service
        self.provider.credentials = self.mock_creds
        
        # Set up the mock response
        mock_spreadsheets = self.mock_sheets_service.spreadsheets.return_value
        mock_values = mock_spreadsheets.values.return_value
        mock_get = mock_values.get.return_value
        mock_get.execute.return_value = {
            "values": []
        }
        
        # Call the method
        result = await self.provider.get_sheet_data("spreadsheet1", "Sheet1")
        
        # Verify the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
        
        # Verify the mock was called correctly
        mock_values.get.assert_called_once_with(spreadsheetId="spreadsheet1", range="Sheet1")
    
    async def test_get_sheet_data_not_initialized(self):
        """Test getting sheet data when provider is not initialized."""
        # Set up the provider as not initialized
        self.provider.is_initialized = False
        
        # Call the method and verify it raises an exception
        with self.assertRaises(Exception):
            await self.provider.get_sheet_data("spreadsheet1", "Sheet1")
    
    async def test_get_spreadsheet_info_success(self):
        """Test getting spreadsheet info successfully."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.service = self.mock_sheets_service
        self.provider.credentials = self.mock_creds
        
        # Set up the mock response for spreadsheets.get
        mock_spreadsheets = self.mock_sheets_service.spreadsheets.return_value
        mock_get = mock_spreadsheets.get.return_value
        mock_get.execute.return_value = {
            "sheets": [
                {"properties": {}},
                {"properties": {}}
            ]
        }
        
        # Set up the mock response for files.get
        mock_files = self.mock_drive_service.files.return_value
        mock_files_get = mock_files.get.return_value
        mock_files_get.execute.return_value = {
            "name": "Test Spreadsheet",
            "createdTime": "2023-01-01T00:00:00",
            "modifiedTime": "2023-01-02T00:00:00",
            "owners": [
                {"displayName": "Test User"}
            ]
        }
        
        # Call the method
        result = await self.provider.get_spreadsheet_info("spreadsheet1")
        
        # Verify the result
        self.assertEqual(result["id"], "spreadsheet1")
        self.assertEqual(result["name"], "Test Spreadsheet")
        self.assertEqual(result["created"], "2023-01-01T00:00:00")
        self.assertEqual(result["modified"], "2023-01-02T00:00:00")
        self.assertEqual(result["owner"], "Test User")
        self.assertEqual(result["sheets"], 2)
        self.assertEqual(result["type"], "spreadsheet")
        
        # Verify the mocks were called correctly
        mock_spreadsheets.get.assert_called_once_with(spreadsheetId="spreadsheet1")
        mock_files.get.assert_called_once_with(
            fileId="spreadsheet1",
            fields="name,createdTime,modifiedTime,owners"
        )
    
    async def test_get_spreadsheet_info_not_initialized(self):
        """Test getting spreadsheet info when provider is not initialized."""
        # Set up the provider as not initialized
        self.provider.is_initialized = False
        
        # Call the method and verify it raises an exception
        with self.assertRaises(Exception):
            await self.provider.get_spreadsheet_info("spreadsheet1")


if __name__ == '__main__':
    unittest.main()