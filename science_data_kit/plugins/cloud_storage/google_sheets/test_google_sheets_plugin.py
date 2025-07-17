"""
Tests for the Google Sheets plugin.

This module contains tests for the Google Sheets plugin implementation.
"""

import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import os
from typing import Dict, Any

from science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin import GoogleSheetsPlugin


class TestGoogleSheetsPlugin(unittest.TestCase):
    """Test cases for the Google Sheets plugin."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = GoogleSheetsPlugin()
        
        # Mock configuration
        self.config = {
            "credentials_file": "/path/to/credentials.json",
            "token_file": "/path/to/token.json"
        }
        
        # Create a patch for os.path.exists to make validate_config pass
        self.path_exists_patcher = patch('os.path.exists')
        self.mock_path_exists = self.path_exists_patcher.start()
        self.mock_path_exists.return_value = True
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.path_exists_patcher.stop()
    
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.Credentials')
    def test_initialize(self, mock_credentials):
        """Test plugin initialization."""
        # Mock credentials
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        # Mock _get_credentials method
        self.plugin._get_credentials = MagicMock(return_value=mock_creds)
        
        # Test initialization
        result = self.plugin.initialize(self.config)
        
        # Assertions
        self.assertTrue(result)
        self.assertTrue(self.plugin.is_initialized)
        self.plugin._get_credentials.assert_called_once_with(
            self.config["credentials_file"], 
            self.config["token_file"]
        )
    
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.build')
    def test_connect(self, mock_build, mock_credentials):
        """Test plugin connection."""
        # Mock credentials and services
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        # Mock _get_credentials method
        self.plugin._get_credentials = MagicMock(return_value=mock_creds)
        
        # Mock service
        mock_sheets_service = MagicMock()
        mock_drive_service = MagicMock()
        mock_files = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = {"files": []}
        mock_files.list.return_value = mock_list
        mock_drive_service.files.return_value = mock_files
        
        # Mock build to return different services
        mock_build.side_effect = [mock_sheets_service, mock_drive_service]
        
        # Initialize and connect
        self.plugin.initialize(self.config)
        self.plugin.connect(self.config)
        
        # Assertions
        self.assertTrue(self.plugin.is_connected)
        self.assertEqual(mock_build.call_count, 2)
        mock_build.assert_any_call('sheets', 'v4', credentials=mock_creds)
        mock_build.assert_any_call('drive', 'v3', credentials=mock_creds)
        mock_files.list.assert_called_once()
    
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.build')
    def test_list_spreadsheets(self, mock_build, mock_credentials):
        """Test listing spreadsheets."""
        # Mock credentials and services
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        # Mock _get_credentials method
        self.plugin._get_credentials = MagicMock(return_value=mock_creds)
        
        # Mock service response
        mock_files_result = {
            "files": [
                {
                    "id": "spreadsheet1",
                    "name": "Spreadsheet 1",
                    "createdTime": "2023-01-01T00:00:00Z",
                    "modifiedTime": "2023-01-02T00:00:00Z"
                },
                {
                    "id": "spreadsheet2",
                    "name": "Spreadsheet 2",
                    "createdTime": "2023-01-03T00:00:00Z",
                    "modifiedTime": "2023-01-04T00:00:00Z"
                }
            ]
        }
        
        # Mock services
        mock_sheets_service = MagicMock()
        mock_drive_service = MagicMock()
        mock_files = MagicMock()
        
        # Mock list method for connection test
        mock_list_connection = MagicMock()
        mock_list_connection.execute.return_value = {"files": []}
        
        # Mock list method for list_spreadsheets
        mock_list_spreadsheets = MagicMock()
        mock_list_spreadsheets.execute.return_value = mock_files_result
        
        # Set up the mock chain
        mock_files.list.side_effect = [mock_list_connection, mock_list_spreadsheets]
        mock_drive_service.files.return_value = mock_files
        
        # Mock build to return different services
        mock_build.side_effect = [mock_sheets_service, mock_drive_service]
        
        # Initialize and connect
        self.plugin.initialize(self.config)
        self.plugin.connect(self.config)
        
        # Test list_spreadsheets
        result = self.plugin.list_spreadsheets()
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "spreadsheet1")
        self.assertEqual(result[0]["name"], "Spreadsheet 1")
        self.assertEqual(result[0]["type"], "spreadsheet")
        self.assertEqual(result[1]["id"], "spreadsheet2")
        self.assertEqual(result[1]["name"], "Spreadsheet 2")
        self.assertEqual(result[1]["type"], "spreadsheet")
        
        # Verify the correct query was used
        mock_files.list.assert_any_call(
            q="mimeType='application/vnd.google-apps.spreadsheet'",
            fields="files(id, name, createdTime, modifiedTime)"
        )
    
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.build')
    def test_list_sheets(self, mock_build, mock_credentials):
        """Test listing sheets in a spreadsheet."""
        # Mock credentials and services
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        # Mock _get_credentials method
        self.plugin._get_credentials = MagicMock(return_value=mock_creds)
        
        # Mock spreadsheet response
        mock_spreadsheet_result = {
            "sheets": [
                {
                    "properties": {
                        "sheetId": "sheet1",
                        "title": "Sheet 1",
                        "index": 0,
                        "gridProperties": {
                            "rowCount": 100,
                            "columnCount": 26
                        }
                    }
                },
                {
                    "properties": {
                        "sheetId": "sheet2",
                        "title": "Sheet 2",
                        "index": 1,
                        "gridProperties": {
                            "rowCount": 50,
                            "columnCount": 10
                        }
                    }
                }
            ]
        }
        
        # Mock services
        mock_sheets_service = MagicMock()
        mock_drive_service = MagicMock()
        
        # Mock sheets methods
        mock_spreadsheets = MagicMock()
        mock_get = MagicMock()
        mock_get.execute.return_value = mock_spreadsheet_result
        mock_spreadsheets.get.return_value = mock_get
        mock_sheets_service.spreadsheets.return_value = mock_spreadsheets
        
        # Mock drive methods for connection test
        mock_files = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = {"files": []}
        mock_files.list.return_value = mock_list
        mock_drive_service.files.return_value = mock_files
        
        # Mock build to return different services
        mock_build.side_effect = [mock_sheets_service, mock_drive_service]
        
        # Initialize and connect
        self.plugin.initialize(self.config)
        self.plugin.connect(self.config)
        
        # Test list_sheets
        result = self.plugin.list_sheets("spreadsheet1")
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "sheet1")
        self.assertEqual(result[0]["name"], "Sheet 1")
        self.assertEqual(result[0]["rows"], 100)
        self.assertEqual(result[0]["columns"], 26)
        self.assertEqual(result[1]["id"], "sheet2")
        self.assertEqual(result[1]["name"], "Sheet 2")
        self.assertEqual(result[1]["rows"], 50)
        self.assertEqual(result[1]["columns"], 10)
        
        # Verify the correct spreadsheet ID was used
        mock_spreadsheets.get.assert_called_once_with(spreadsheetId="spreadsheet1")
    
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.build')
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.pd.DataFrame')
    def test_get_sheet_data(self, mock_dataframe, mock_build, mock_credentials):
        """Test getting sheet data."""
        # Mock credentials and services
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        # Mock _get_credentials method
        self.plugin._get_credentials = MagicMock(return_value=mock_creds)
        
        # Mock sheet data response
        mock_sheet_data = {
            "values": [
                ["Header1", "Header2", "Header3"],
                ["Value1", "Value2", "Value3"],
                ["Value4", "Value5", "Value6"]
            ]
        }
        
        # Mock DataFrame
        mock_df = MagicMock()
        mock_df.iloc.__getitem__.return_value = ["Header1", "Header2", "Header3"]
        mock_df.drop.return_value = "processed_dataframe"
        mock_dataframe.return_value = mock_df
        
        # Mock services
        mock_sheets_service = MagicMock()
        mock_drive_service = MagicMock()
        
        # Mock sheets methods
        mock_spreadsheets = MagicMock()
        mock_values = MagicMock()
        mock_get = MagicMock()
        mock_get.execute.return_value = mock_sheet_data
        mock_values.get.return_value = mock_get
        mock_spreadsheets.values.return_value = mock_values
        mock_sheets_service.spreadsheets.return_value = mock_spreadsheets
        
        # Mock drive methods for connection test
        mock_files = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = {"files": []}
        mock_files.list.return_value = mock_list
        mock_drive_service.files.return_value = mock_files
        
        # Mock build to return different services
        mock_build.side_effect = [mock_sheets_service, mock_drive_service]
        
        # Initialize and connect
        self.plugin.initialize(self.config)
        self.plugin.connect(self.config)
        
        # Test get_sheet_data
        result = self.plugin.get_sheet_data("spreadsheet1", "Sheet1")
        
        # Assertions
        self.assertEqual(result, "processed_dataframe")
        mock_values.get.assert_called_once_with(
            spreadsheetId="spreadsheet1",
            range="Sheet1"
        )
        mock_dataframe.assert_called_once_with(mock_sheet_data["values"])
        mock_df.drop.assert_called_once_with(0)
    
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_sheets.google_sheets_plugin.build')
    def test_request(self, mock_build, mock_credentials):
        """Test making API requests."""
        # Mock credentials and services
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        # Mock _get_credentials method
        self.plugin._get_credentials = MagicMock(return_value=mock_creds)
        
        # Mock services
        mock_sheets_service = MagicMock()
        mock_drive_service = MagicMock()
        
        # Mock sheets methods
        mock_spreadsheets = MagicMock()
        mock_values = MagicMock()
        mock_get_values = MagicMock()
        mock_get_values.execute.return_value = {"values": []}
        mock_values.get.return_value = mock_get_values
        mock_spreadsheets.values.return_value = mock_values
        
        mock_get_spreadsheet = MagicMock()
        mock_get_spreadsheet.execute.return_value = {"sheets": []}
        mock_spreadsheets.get.return_value = mock_get_spreadsheet
        
        mock_sheets_service.spreadsheets.return_value = mock_spreadsheets
        
        # Mock drive methods
        mock_files = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = {"files": []}
        mock_files.list.return_value = mock_list
        
        mock_get_file = MagicMock()
        mock_get_file.execute.return_value = {"name": "test"}
        mock_files.get.return_value = mock_get_file
        
        mock_drive_service.files.return_value = mock_files
        
        # Mock build to return different services
        mock_build.side_effect = [mock_sheets_service, mock_drive_service]
        
        # Initialize and connect
        self.plugin.initialize(self.config)
        self.plugin.connect(self.config)
        
        # Test request for spreadsheet values
        result1 = self.plugin.request("GET", "/spreadsheets/spreadsheet1/values/Sheet1")
        
        # Test request for spreadsheet metadata
        result2 = self.plugin.request("GET", "/spreadsheets/spreadsheet1/get")
        
        # Test request for files list
        result3 = self.plugin.request("GET", "/files/list")
        
        # Test request for file metadata
        result4 = self.plugin.request("GET", "/files/file1")
        
        # Assertions
        mock_values.get.assert_called_once_with(
            spreadsheetId="spreadsheet1",
            range="Sheet1"
        )
        mock_spreadsheets.get.assert_called_once_with(
            spreadsheetId="spreadsheet1"
        )
        mock_files.list.assert_called()
        mock_files.get.assert_called_once_with(
            fileId="file1"
        )
    
    def test_capabilities(self):
        """Test plugin capabilities."""
        capabilities = self.plugin.capabilities
        self.assertIn("api", capabilities)
        self.assertIn("spreadsheet", capabilities)
        self.assertIn("readable", capabilities)


if __name__ == '__main__':
    unittest.main()