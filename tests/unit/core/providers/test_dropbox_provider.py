"""
Unit tests for the Dropbox provider.
"""

import unittest
import pandas as pd
import io
from unittest.mock import patch, MagicMock
from dropbox.exceptions import AuthError, ApiError
from dropbox.files import FileMetadata, FolderMetadata

from science_data_kit.core.providers.storage.dropbox_provider import DropboxProvider


class TestDropboxProvider(unittest.TestCase):
    """Test cases for the DropboxProvider class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "access_token": "test_access_token"
        }
        
        # Create a patcher for the Dropbox client
        self.dropbox_patcher = patch('science_data_kit.core.providers.storage.dropbox_provider.Dropbox')
        self.mock_dropbox = self.dropbox_patcher.start()
        
        # Create a mock Dropbox client
        self.mock_client = MagicMock()
        self.mock_dropbox.return_value = self.mock_client
        
        # Create the provider
        self.provider = DropboxProvider(self.config)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.dropbox_patcher.stop()
    
    async def test_initialize_success(self):
        """Test successful initialization of the provider."""
        # Set up the mock
        self.mock_client.users_get_current_account.return_value = {"account_id": "test_account"}
        
        # Call the method
        result = await self.provider.initialize()
        
        # Verify the result
        self.assertTrue(result)
        self.assertTrue(self.provider.is_initialized)
        self.mock_dropbox.assert_called_once_with("test_access_token")
        self.mock_client.users_get_current_account.assert_called_once()
    
    async def test_initialize_missing_token(self):
        """Test initialization with missing access token."""
        # Create a provider with empty config
        provider = DropboxProvider({})
        
        # Call the method
        result = await provider.initialize()
        
        # Verify the result
        self.assertFalse(result)
        self.assertFalse(provider.is_initialized)
        self.mock_dropbox.assert_not_called()
    
    async def test_initialize_auth_error(self):
        """Test initialization with authentication error."""
        # Set up the mock to raise an AuthError
        self.mock_client.users_get_current_account.side_effect = AuthError("Auth error")
        
        # Call the method
        result = await self.provider.initialize()
        
        # Verify the result
        self.assertFalse(result)
        self.assertFalse(self.provider.is_initialized)
        self.mock_dropbox.assert_called_once_with("test_access_token")
        self.mock_client.users_get_current_account.assert_called_once()
    
    async def test_health_check_success(self):
        """Test successful health check."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.client = self.mock_client
        
        # Set up the mock
        self.mock_client.users_get_current_account.return_value = {"account_id": "test_account"}
        
        # Call the method
        result = await self.provider.health_check()
        
        # Verify the result
        self.assertTrue(result)
        self.mock_client.users_get_current_account.assert_called_once()
    
    async def test_health_check_not_initialized(self):
        """Test health check when provider is not initialized."""
        # Set up the provider as not initialized
        self.provider.is_initialized = False
        
        # Call the method
        result = await self.provider.health_check()
        
        # Verify the result
        self.assertFalse(result)
        self.mock_client.users_get_current_account.assert_not_called()
    
    async def test_health_check_error(self):
        """Test health check with error."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.client = self.mock_client
        
        # Set up the mock to raise an exception
        self.mock_client.users_get_current_account.side_effect = Exception("Test error")
        
        # Call the method
        result = await self.provider.health_check()
        
        # Verify the result
        self.assertFalse(result)
        self.mock_client.users_get_current_account.assert_called_once()
    
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
        
        self.assertIn("csv", capabilities["formats"])
        self.assertIn("xlsx", capabilities["formats"])
        self.assertIn("xls", capabilities["formats"])
        
        self.assertFalse(capabilities["real_time"])
    
    async def test_list_files_success(self):
        """Test listing files successfully."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.client = self.mock_client
        
        # Create mock file and folder metadata
        file_metadata = MagicMock(spec=FileMetadata)
        file_metadata.id = "file1"
        file_metadata.name = "test.csv"
        file_metadata.path_display = "/test.csv"
        file_metadata.size = 1024
        file_metadata.server_modified.isoformat.return_value = "2023-01-01T00:00:00"
        
        folder_metadata = MagicMock(spec=FolderMetadata)
        folder_metadata.id = "folder1"
        folder_metadata.name = "test_folder"
        folder_metadata.path_display = "/test_folder"
        
        # Set up the mock response
        mock_result = MagicMock()
        mock_result.entries = [file_metadata, folder_metadata]
        mock_result.has_more = False
        
        self.mock_client.files_list_folder.return_value = mock_result
        
        # Call the method
        result = await self.provider.list_files("/test")
        
        # Verify the result
        self.assertEqual(len(result), 2)
        
        # Verify file entry
        file_entry = result[0]
        self.assertEqual(file_entry["id"], "file1")
        self.assertEqual(file_entry["name"], "test.csv")
        self.assertEqual(file_entry["path"], "/test.csv")
        self.assertEqual(file_entry["size"], 1024)
        self.assertEqual(file_entry["type"], "csv")
        
        # Verify folder entry
        folder_entry = result[1]
        self.assertEqual(folder_entry["id"], "folder1")
        self.assertEqual(folder_entry["name"], "test_folder")
        self.assertEqual(folder_entry["path"], "/test_folder")
        self.assertEqual(folder_entry["type"], "folder")
        
        # Verify the mock was called correctly
        self.mock_client.files_list_folder.assert_called_once_with("/test")
    
    async def test_list_files_not_initialized(self):
        """Test listing files when provider is not initialized."""
        # Set up the provider as not initialized
        self.provider.is_initialized = False
        
        # Call the method and verify it raises an exception
        with self.assertRaises(Exception):
            await self.provider.list_files("/test")
    
    async def test_download_file_data_csv(self):
        """Test downloading CSV file data."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.client = self.mock_client
        
        # Create mock response
        mock_metadata = MagicMock()
        mock_response = MagicMock()
        mock_response.content = b"col1,col2\nvalue1,value2"
        
        self.mock_client.files_download.return_value = (mock_metadata, mock_response)
        
        # Mock pandas.read_csv
        csv_df = pd.DataFrame({"col1": ["value1"], "col2": ["value2"]})
        with patch('pandas.read_csv', return_value=csv_df) as mock_read_csv:
            # Call the method
            result = await self.provider.download_file_data("/test.csv")
            
            # Verify the result
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(result.shape, (1, 2))
            
            # Verify the mocks were called correctly
            self.mock_client.files_download.assert_called_once_with("/test.csv")
            mock_read_csv.assert_called_once()
    
    async def test_download_file_data_excel(self):
        """Test downloading Excel file data."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.client = self.mock_client
        
        # Create mock response
        mock_metadata = MagicMock()
        mock_response = MagicMock()
        mock_response.content = b"excel file content"
        
        self.mock_client.files_download.return_value = (mock_metadata, mock_response)
        
        # Mock pandas.read_excel
        excel_df = pd.DataFrame({"col1": ["value1"], "col2": ["value2"]})
        with patch('pandas.read_excel', return_value=excel_df) as mock_read_excel:
            # Call the method
            result = await self.provider.download_file_data("/test.xlsx")
            
            # Verify the result
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(result.shape, (1, 2))
            
            # Verify the mocks were called correctly
            self.mock_client.files_download.assert_called_once_with("/test.xlsx")
            mock_read_excel.assert_called_once()
    
    async def test_download_file_data_unsupported_format(self):
        """Test downloading file with unsupported format."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.client = self.mock_client
        
        # Create mock response
        mock_metadata = MagicMock()
        mock_response = MagicMock()
        mock_response.content = b"file content"
        
        self.mock_client.files_download.return_value = (mock_metadata, mock_response)
        
        # Call the method and verify it raises an exception
        with self.assertRaises(ValueError):
            await self.provider.download_file_data("/test.txt")
    
    async def test_get_file_info_success(self):
        """Test getting file info successfully."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.client = self.mock_client
        
        # Create mock file metadata
        file_metadata = MagicMock(spec=FileMetadata)
        file_metadata.id = "file1"
        file_metadata.name = "test.csv"
        file_metadata.path_display = "/test.csv"
        file_metadata.size = 1024
        file_metadata.server_modified.isoformat.return_value = "2023-01-01T00:00:00"
        
        self.mock_client.files_get_metadata.return_value = file_metadata
        
        # Call the method
        result = await self.provider.get_file_info("/test.csv")
        
        # Verify the result
        self.assertEqual(result["id"], "file1")
        self.assertEqual(result["name"], "test.csv")
        self.assertEqual(result["path"], "/test.csv")
        self.assertEqual(result["size"], 1024)
        self.assertEqual(result["type"], "csv")
        
        # Verify the mock was called correctly
        self.mock_client.files_get_metadata.assert_called_once_with("/test.csv")
    
    async def test_get_file_info_not_file(self):
        """Test getting info for a path that is not a file."""
        # Set up the provider as initialized
        self.provider.is_initialized = True
        self.provider.client = self.mock_client
        
        # Create mock folder metadata
        folder_metadata = MagicMock(spec=FolderMetadata)
        
        self.mock_client.files_get_metadata.return_value = folder_metadata
        
        # Call the method and verify it raises an exception
        with self.assertRaises(ValueError):
            await self.provider.get_file_info("/test_folder")


if __name__ == '__main__':
    unittest.main()